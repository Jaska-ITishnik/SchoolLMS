from datetime import date
from unittest.mock import patch

from accounts.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.utils import timezone

from academics.models import (
    AcademicYear,
    CourseOffering,
    ClassMembership,
    Enrollment,
    SchoolClass,
    Subject,
    TeachingAssignment,
    Term,
)
from academics.services import assign_teacher_to_course, close_teaching_assignment
from academics.membership_services import assign_pupil_to_class


class AcademicYearTests(TestCase):
    def test_reversed_dates_are_rejected_by_model_validation(self):
        year = AcademicYear(
            label='2025–2026',
            start_date=date(2026, 8, 1),
            end_date=date(2025, 6, 30),
        )

        with self.assertRaises(ValidationError) as error:
            year.full_clean()

        self.assertIn('end_date', error.exception.message_dict)

    def test_reversed_dates_are_rejected_by_database_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AcademicYear.objects.create(
                    label='Invalid year',
                    start_date=date(2026, 8, 1),
                    end_date=date(2025, 6, 30),
                )


class TermTests(TestCase):
    def setUp(self):
        self.year = AcademicYear.objects.create(
            label='2025–2026',
            start_date=date(2025, 8, 1),
            end_date=date(2026, 6, 30),
        )

    def test_duplicate_order_in_same_year_is_rejected_by_database(self):
        Term.objects.create(
            year=self.year,
            order=1,
            start_date=date(2025, 8, 1),
            end_date=date(2025, 10, 31),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Term.objects.create(
                    year=self.year,
                    order=1,
                    start_date=date(2025, 11, 1),
                    end_date=date(2026, 1, 31),
                )

    def test_term_outside_academic_year_is_rejected_by_validation(self):
        term = Term(
            year=self.year,
            order=1,
            start_date=date(2025, 7, 31),
            end_date=date(2025, 10, 31),
        )

        with self.assertRaises(ValidationError) as error:
            term.full_clean()

        self.assertIn('start_date', error.exception.message_dict)

    def test_reversed_term_dates_are_rejected_by_database_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Term.objects.create(
                    year=self.year,
                    order=1,
                    start_date=date(2025, 10, 31),
                    end_date=date(2025, 8, 1),
                )


class CourseOfferingTests(TestCase):
    def setUp(self):
        self.year = AcademicYear.objects.create(
            label='2025–2026',
            start_date=date(2025, 8, 1),
            end_date=date(2026, 6, 30),
        )
        self.subject = Subject.objects.create(code='MATH', title='Matematika')
        self.class_7a = SchoolClass.objects.create(
            year=self.year,
            grade_level=7,
            section='A',
        )
        self.class_7b = SchoolClass.objects.create(
            year=self.year,
            grade_level=7,
            section='B',
        )

    def test_subject_can_be_offered_to_multiple_classes(self):
        CourseOffering.objects.create(school_class=self.class_7a, subject=self.subject)
        CourseOffering.objects.create(school_class=self.class_7b, subject=self.subject)

        self.assertEqual(self.subject.course_offerings.count(), 2)

    def test_duplicate_subject_offering_in_one_class_is_rejected(self):
        CourseOffering.objects.create(school_class=self.class_7a, subject=self.subject)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CourseOffering.objects.create(
                    school_class=self.class_7a,
                    subject=self.subject,
                )

    def test_same_grade_and_section_cannot_repeat_in_year(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SchoolClass.objects.create(
                    year=self.year,
                    grade_level=7,
                    section='A',
                )

    def test_grade_level_outside_school_range_is_rejected(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SchoolClass.objects.create(
                    year=self.year,
                    grade_level=12,
                    section='A',
                )

    def test_class_and_subject_are_protected_while_offering_exists(self):
        CourseOffering.objects.create(school_class=self.class_7a, subject=self.subject)

        with self.assertRaises(ProtectedError):
            self.subject.delete()


class TeachingAssignmentTests(TestCase):
    def setUp(self):
        self.year = AcademicYear.objects.create(
            label='2025–2026',
            start_date=date(2025, 8, 1),
            end_date=date(2026, 6, 30),
        )
        school_class = SchoolClass.objects.create(
            year=self.year,
            grade_level=7,
            section='A',
        )
        subject = Subject.objects.create(code='MATH', title='Matematika')
        self.course = CourseOffering.objects.create(
            school_class=school_class,
            subject=subject,
        )
        self.teacher = User.objects.create_user(
            username='teacher-one',
            password='safe-test-password',
            role=User.Role.TEACHER,
        )

    def test_pupil_cannot_receive_teacher_assignment(self):
        pupil = User.objects.create_user(
            username='pupil-one',
            password='safe-test-password',
            role=User.Role.PUPIL,
        )

        with self.assertRaises(ValidationError):
            assign_teacher_to_course(
                course=self.course,
                teacher=pupil,
                start_date=date(2025, 9, 1),
            )

        self.assertEqual(TeachingAssignment.objects.count(), 0)

    def test_teacher_replacement_closes_old_assignment_and_keeps_history(self):
        previous = assign_teacher_to_course(
            course=self.course,
            teacher=self.teacher,
            start_date=date(2025, 9, 1),
            can_grade=True,
        )
        next_teacher = User.objects.create_user(
            username='teacher-two',
            password='safe-test-password',
            role=User.Role.TEACHER,
        )

        replacement = assign_teacher_to_course(
            course=self.course,
            teacher=next_teacher,
            start_date=date(2025, 10, 1),
        )

        previous.refresh_from_db()
        self.assertEqual(previous.end_date, date(2025, 9, 30))
        self.assertTrue(previous.can_grade)
        self.assertTrue(TeachingAssignment.objects.filter(pk=previous.pk).exists())
        self.assertIsNone(replacement.end_date)

    def test_inactive_teacher_and_archived_course_cannot_receive_assignment(self):
        self.teacher.is_active = False
        self.teacher.save(update_fields=('is_active',))

        with self.assertRaises(ValidationError):
            assign_teacher_to_course(
                course=self.course,
                teacher=self.teacher,
                start_date=date(2025, 9, 1),
            )

        self.teacher.is_active = True
        self.teacher.save(update_fields=('is_active',))
        self.course.archived_at = timezone.now()
        self.course.save(update_fields=('archived_at',))

        with self.assertRaises(ValidationError):
            assign_teacher_to_course(
                course=self.course,
                teacher=self.teacher,
                start_date=date(2025, 9, 1),
            )

    def test_date_order_is_validated_and_existing_assignment_can_be_closed(self):
        invalid = TeachingAssignment(
            course=self.course,
            teacher=self.teacher,
            start_date=date(2025, 10, 1),
            end_date=date(2025, 9, 30),
        )
        with self.assertRaises(ValidationError):
            invalid.full_clean()

        assignment = assign_teacher_to_course(
            course=self.course,
            teacher=self.teacher,
            start_date=date(2025, 9, 1),
        )
        closed = close_teaching_assignment(
            assignment=assignment,
            end_date=date(2025, 9, 30),
        )
        self.assertEqual(closed.end_date, date(2025, 9, 30))

    def test_reversed_assignment_dates_are_rejected_by_database_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TeachingAssignment.objects.create(
                    course=self.course,
                    teacher=self.teacher,
                    start_date=date(2025, 10, 1),
                    end_date=date(2025, 9, 30),
                )


class ClassMembershipTests(TestCase):
    def setUp(self):
        year = AcademicYear.objects.create(
            label='2025–2026',
            start_date=date(2025, 8, 1),
            end_date=date(2026, 6, 30),
        )
        self.class_7a = SchoolClass.objects.create(
            year=year,
            grade_level=7,
            section='A',
        )
        self.class_7b = SchoolClass.objects.create(
            year=year,
            grade_level=7,
            section='B',
        )
        math = Subject.objects.create(code='MATH', title='Matematika')
        english = Subject.objects.create(code='ENG', title='Ingliz tili')
        self.math_7a = CourseOffering.objects.create(school_class=self.class_7a, subject=math)
        self.english_7a = CourseOffering.objects.create(school_class=self.class_7a, subject=english)
        self.math_7b = CourseOffering.objects.create(school_class=self.class_7b, subject=math)
        self.pupil = User.objects.create_user(
            username='membership-pupil',
            password='safe-test-password',
            role=User.Role.PUPIL,
        )

    def test_teacher_cannot_be_added_as_class_pupil(self):
        teacher = User.objects.create_user(
            username='membership-teacher',
            password='safe-test-password',
            role=User.Role.TEACHER,
        )

        with self.assertRaises(ValidationError):
            assign_pupil_to_class(
                pupil=teacher,
                school_class=self.class_7a,
                start_date=date(2025, 9, 1),
            )

        self.assertEqual(ClassMembership.objects.count(), 0)

    def test_assignment_creates_membership_and_all_active_class_enrollments(self):
        archived_subject = Subject.objects.create(code='ART', title='Tasviriy san’at')
        CourseOffering.objects.create(
            school_class=self.class_7a,
            subject=archived_subject,
            archived_at=timezone.now(),
        )

        membership = assign_pupil_to_class(
            pupil=self.pupil,
            school_class=self.class_7a,
            start_date=date(2025, 9, 1),
        )

        self.assertEqual(membership.status, ClassMembership.Status.ACTIVE)
        self.assertSetEqual(
            set(membership.enrollments.values_list('course_id', flat=True)),
            {self.math_7a.pk, self.english_7a.pk},
        )

    def test_class_change_closes_old_history_and_enrolls_new_class_courses(self):
        old_membership = assign_pupil_to_class(
            pupil=self.pupil,
            school_class=self.class_7a,
            start_date=date(2025, 9, 1),
        )
        old_enrollments = list(old_membership.enrollments.all())

        new_membership = assign_pupil_to_class(
            pupil=self.pupil,
            school_class=self.class_7b,
            start_date=date(2025, 10, 1),
        )

        old_membership.refresh_from_db()
        self.assertEqual(old_membership.status, ClassMembership.Status.ENDED)
        self.assertEqual(old_membership.end_date, date(2025, 9, 30))
        for enrollment in old_enrollments:
            enrollment.refresh_from_db()
            self.assertEqual(enrollment.status, Enrollment.Status.ENDED)
            self.assertEqual(enrollment.end_date, date(2025, 9, 30))
            self.assertTrue(Enrollment.objects.filter(pk=enrollment.pk).exists())
        self.assertEqual(list(new_membership.enrollments.values_list('course_id', flat=True)), [self.math_7b.pk])

    def test_database_rejects_two_active_class_memberships(self):
        assign_pupil_to_class(
            pupil=self.pupil,
            school_class=self.class_7a,
            start_date=date(2025, 9, 1),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ClassMembership.objects.create(
                    pupil=self.pupil,
                    school_class=self.class_7b,
                    start_date=date(2025, 10, 1),
                )

    def test_database_rejects_duplicate_active_pupil_course_enrollment(self):
        membership = assign_pupil_to_class(
            pupil=self.pupil,
            school_class=self.class_7a,
            start_date=date(2025, 9, 1),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Enrollment.objects.create(
                    pupil=self.pupil,
                    course=self.math_7a,
                    membership=membership,
                    start_date=date(2025, 9, 1),
                )

    def test_backdated_class_change_is_rejected(self):
        membership = assign_pupil_to_class(
            pupil=self.pupil,
            school_class=self.class_7a,
            start_date=date(2025, 9, 1),
        )

        with self.assertRaises(ValidationError):
            assign_pupil_to_class(
                pupil=self.pupil,
                school_class=self.class_7b,
                start_date=date(2025, 8, 31),
            )

        membership.refresh_from_db()
        self.assertEqual(membership.status, ClassMembership.Status.ACTIVE)

    def test_failed_course_enrollment_rolls_back_class_change(self):
        old_membership = assign_pupil_to_class(
            pupil=self.pupil,
            school_class=self.class_7a,
            start_date=date(2025, 9, 1),
        )
        original_full_clean = Enrollment.full_clean

        def reject_new_enrollment(instance, *args, **kwargs):
            if instance.pk is None:
                raise ValidationError({'course': 'Synthetic enrollment failure.'})
            return original_full_clean(instance, *args, **kwargs)

        with patch.object(Enrollment, 'full_clean', reject_new_enrollment):
            with self.assertRaises(ValidationError):
                assign_pupil_to_class(
                    pupil=self.pupil,
                    school_class=self.class_7b,
                    start_date=date(2025, 10, 1),
                )

        old_membership.refresh_from_db()
        self.assertEqual(old_membership.status, ClassMembership.Status.ACTIVE)
        self.assertEqual(
            Enrollment.objects.filter(pupil=self.pupil, status=Enrollment.Status.ACTIVE).count(),
            2,
        )
        self.assertFalse(ClassMembership.objects.filter(pupil=self.pupil, school_class=self.class_7b).exists())
