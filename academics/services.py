from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from academics.models import CourseOffering, TeachingAssignment


@transaction.atomic
def assign_teacher_to_course(*, course, teacher, start_date, can_grade=False, end_date=None):
    """Create an assignment, closing any open course assignment the day before it starts."""
    course = CourseOffering.objects.select_for_update().get(pk=course.pk)
    user_model = get_user_model()

    if teacher.role != user_model.Role.TEACHER:
        raise ValidationError({'teacher': 'Only a teacher account can receive a teaching assignment.'})
    if not teacher.is_active:
        raise ValidationError({'teacher': 'An inactive teacher cannot receive a new assignment.'})
    if course.archived_at is not None:
        raise ValidationError({'course': 'An archived course cannot receive a new teaching assignment.'})

    open_assignments = TeachingAssignment.objects.select_for_update().filter(
        course=course,
        end_date__isnull=True,
    )
    for previous in open_assignments:
        if start_date <= previous.start_date:
            raise ValidationError({
                'start_date': 'A replacement assignment must start after the current assignment.'
            })
        previous.end_date = start_date - timedelta(days=1)
        previous.full_clean()
        previous.save(update_fields=('end_date',))

    assignment = TeachingAssignment(
        course=course,
        teacher=teacher,
        start_date=start_date,
        end_date=end_date,
        can_grade=can_grade,
    )
    assignment.full_clean()
    assignment.save()
    return assignment


@transaction.atomic
def close_teaching_assignment(*, assignment, end_date: date):
    """Close an existing assignment without deleting its history."""
    current = TeachingAssignment.objects.select_for_update().get(pk=assignment.pk)
    if current.end_date is not None:
        raise ValidationError({'end_date': 'This teaching assignment is already closed.'})

    current.end_date = end_date
    current.full_clean()
    current.save(update_fields=('end_date',))
    return current
