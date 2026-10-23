from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.contrib.auth import get_user_model


class AcademicYear(models.Model):
    class Status(models.TextChoices):
        PLANNED = 'planned', 'Planned'
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'

    label = models.CharField(max_length=32)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=8,
        choices=Status.choices,
        default=Status.PLANNED,
    )

    class Meta:
        ordering = ('start_date',)
        constraints = [
            models.CheckConstraint(
                condition=Q(start_date__lte=F('end_date')),
                name='academics_year_date_order',
            ),
        ]

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({'end_date': 'End date must be on or after start date.'})

    def __str__(self):
        return self.label


class Term(models.Model):
    class Status(models.TextChoices):
        PLANNED = 'planned', 'Planned'
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'

    year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name='terms',
    )
    order = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=8,
        choices=Status.choices,
        default=Status.PLANNED,
    )

    class Meta:
        ordering = ('year__start_date', 'order')
        constraints = [
            models.UniqueConstraint(
                fields=('year', 'order'),
                name='academics_term_year_order_uniq',
            ),
            models.CheckConstraint(
                condition=Q(start_date__lte=F('end_date')),
                name='academics_term_date_order',
            ),
            models.CheckConstraint(
                condition=Q(order__gte=1, order__lte=4),
                name='academics_term_order_quarter_range',
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}

        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors['end_date'] = 'End date must be on or after start date.'

        if self.year_id and self.start_date and self.end_date:
            year = self.year
            if self.start_date < year.start_date:
                errors['start_date'] = 'Term must start on or after its academic year starts.'
            if self.end_date > year.end_date:
                errors['end_date'] = 'Term must end on or before its academic year ends.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.year.label} — Term {self.order}'


class SchoolClass(models.Model):
    year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name='school_classes',
    )
    grade_level = models.PositiveSmallIntegerField()
    section = models.CharField(max_length=8)

    class Meta:
        ordering = ('year__start_date', 'grade_level', 'section')
        constraints = [
            models.UniqueConstraint(
                fields=('year', 'grade_level', 'section'),
                name='academics_class_year_grade_sec_uniq',
            ),
            models.CheckConstraint(
                condition=Q(grade_level__gte=1, grade_level__lte=11),
                name='academics_class_grade_range',
            ),
        ]

    def __str__(self):
        return f'{self.grade_level}-{self.section}'


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=120)

    class Meta:
        ordering = ('title', 'code')

    def __str__(self):
        return self.title


class CourseOffering(models.Model):
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name='course_offerings',
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name='course_offerings',
    )
    archived_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('school_class__grade_level', 'school_class__section', 'subject__title')
        constraints = [
            models.UniqueConstraint(
                fields=('school_class', 'subject'),
                name='academics_offering_class_subject_uniq',
            ),
        ]

    def __str__(self):
        return f'{self.school_class} — {self.subject.title}'


class TeachingAssignment(models.Model):
    course = models.ForeignKey(
        CourseOffering,
        on_delete=models.PROTECT,
        related_name='teaching_assignments',
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='teaching_assignments',
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    can_grade = models.BooleanField(default=False)

    class Meta:
        ordering = ('course_id', 'start_date')
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__isnull=True) | Q(end_date__gte=F('start_date')),
                name='academics_assignment_date_order',
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}

        if self.start_date and self.end_date and self.end_date < self.start_date:
            errors['end_date'] = 'End date must be on or after start date.'

        if self.teacher_id:
            user_model = get_user_model()
            teacher = self.teacher
            if teacher.role != user_model.Role.TEACHER:
                errors['teacher'] = 'Only a teacher account can receive a teaching assignment.'
            if self._state.adding and not teacher.is_active:
                errors['teacher'] = 'An inactive teacher cannot receive a new assignment.'

            if not self._state.adding:
                previous_teacher_id = type(self).objects.filter(pk=self.pk).values_list(
                    'teacher_id', flat=True
                ).first()
                if previous_teacher_id is not None and previous_teacher_id != self.teacher_id:
                    errors['teacher'] = 'Change teachers by closing this assignment and creating another.'

        if self.course_id and self._state.adding and self.course.archived_at is not None:
            errors['course'] = 'An archived course cannot receive a new teaching assignment.'

        if self.course_id and self.start_date:
            overlapping = type(self).objects.filter(
                course_id=self.course_id,
                start_date__lte=self.end_date or date.max,
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=self.start_date)
            )
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)
            if overlapping.exists():
                errors['start_date'] = 'Teaching assignment dates cannot overlap for the same course.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.teacher} — {self.course}'


class ClassMembership(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ENDED = 'ended', 'Ended'

    pupil = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='class_memberships',
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name='memberships',
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ('pupil_id', 'start_date')
        constraints = [
            models.UniqueConstraint(
                fields=('pupil',),
                condition=Q(status='active'),
                name='academics_one_active_class_membership',
            ),
            models.CheckConstraint(
                condition=Q(start_date__lte=F('end_date')) | Q(end_date__isnull=True),
                name='academics_membership_date_order',
            ),
            models.CheckConstraint(
                condition=(
                    Q(status='active', end_date__isnull=True)
                    | Q(status='ended', end_date__isnull=False)
                ),
                name='academics_membership_status_dates',
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}

        if self.pupil_id and self.pupil.role != get_user_model().Role.PUPIL:
            errors['pupil'] = 'Only a pupil account can have a class membership.'

        if self.pupil_id and self.start_date:
            overlapping = type(self).objects.filter(
                pupil_id=self.pupil_id,
                start_date__lte=self.end_date or date.max,
            ).filter(Q(end_date__isnull=True) | Q(end_date__gte=self.start_date))
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)
            if overlapping.exists():
                errors['start_date'] = 'Class membership dates cannot overlap for a pupil.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.pupil} — {self.school_class}'


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ENDED = 'ended', 'Ended'

    pupil = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='course_enrollments',
    )
    course = models.ForeignKey(
        CourseOffering,
        on_delete=models.PROTECT,
        related_name='enrollments',
    )
    membership = models.ForeignKey(
        ClassMembership,
        on_delete=models.PROTECT,
        related_name='enrollments',
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ('pupil_id', 'course_id', 'start_date')
        constraints = [
            models.UniqueConstraint(
                fields=('pupil', 'course'),
                condition=Q(status='active'),
                name='academics_one_active_pupil_course',
            ),
            models.CheckConstraint(
                condition=Q(start_date__lte=F('end_date')) | Q(end_date__isnull=True),
                name='academics_enrollment_date_order',
            ),
            models.CheckConstraint(
                condition=(
                    Q(status='active', end_date__isnull=True)
                    | Q(status='ended', end_date__isnull=False)
                ),
                name='academics_enrollment_status_dates',
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}

        if self.pupil_id and self.pupil.role != get_user_model().Role.PUPIL:
            errors['pupil'] = 'Only a pupil account can be enrolled in a course.'

        if self.membership_id and self.course_id and self.pupil_id:
            membership = self.membership
            course = self.course
            if membership.pupil_id != self.pupil_id:
                errors['membership'] = 'Enrollment pupil must match the class membership pupil.'
            if membership.school_class_id != course.school_class_id:
                errors['course'] = 'Course must belong to the membership class.'
            if self._state.adding and membership.status != ClassMembership.Status.ACTIVE:
                errors['membership'] = 'A new enrollment requires an active class membership.'
            if self._state.adding and course.archived_at is not None:
                errors['course'] = 'An archived course cannot receive a new enrollment.'

        if self.pupil_id and self.course_id and self.start_date:
            overlapping = type(self).objects.filter(
                pupil_id=self.pupil_id,
                course_id=self.course_id,
                start_date__lte=self.end_date or date.max,
            ).filter(Q(end_date__isnull=True) | Q(end_date__gte=self.start_date))
            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)
            if overlapping.exists():
                errors['start_date'] = 'Enrollment dates cannot overlap for a pupil and course.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.pupil} — {self.course}'
