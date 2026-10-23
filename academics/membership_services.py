from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max

from academics.models import ClassMembership, Enrollment, SchoolClass


@transaction.atomic
def assign_pupil_to_class(*, pupil, school_class, start_date: date):
    """Assign a pupil to one class and enroll them in its current courses atomically."""
    user_model = get_user_model()
    pupil = user_model.objects.select_for_update().get(pk=pupil.pk)
    school_class = SchoolClass.objects.select_for_update().get(pk=school_class.pk)

    if pupil.role != user_model.Role.PUPIL:
        raise ValidationError({'pupil': 'Only a pupil account can join a class.'})

    latest_membership_start = ClassMembership.objects.filter(pupil=pupil).aggregate(
        latest=Max('start_date')
    )['latest']
    if latest_membership_start is not None and start_date <= latest_membership_start:
        raise ValidationError({
            'start_date': 'Backdated class changes are not supported; use a date after existing history.'
        })

    active_membership = ClassMembership.objects.select_for_update().filter(
        pupil=pupil,
        status=ClassMembership.Status.ACTIVE,
    ).first()
    if active_membership is not None and active_membership.school_class_id == school_class.pk:
        raise ValidationError({'school_class': 'Pupil is already active in this class.'})

    previous_enrollments = list(
        Enrollment.objects.select_for_update().filter(
            pupil=pupil,
            status=Enrollment.Status.ACTIVE,
        )
    )
    for enrollment in previous_enrollments:
        if start_date <= enrollment.start_date:
            raise ValidationError({
                'start_date': 'Class change must start after each active enrollment began.'
            })

    transfer_end_date = start_date - timedelta(days=1)
    for enrollment in previous_enrollments:
        enrollment.end_date = transfer_end_date
        enrollment.status = Enrollment.Status.ENDED
        enrollment.full_clean()
        enrollment.save(update_fields=('end_date', 'status'))

    if active_membership is not None:
        active_membership.end_date = transfer_end_date
        active_membership.status = ClassMembership.Status.ENDED
        active_membership.full_clean()
        active_membership.save(update_fields=('end_date', 'status'))

    membership = ClassMembership(
        pupil=pupil,
        school_class=school_class,
        start_date=start_date,
    )
    membership.full_clean()
    membership.save()

    current_courses = school_class.course_offerings.filter(archived_at__isnull=True)
    for course in current_courses:
        enrollment = Enrollment(
            pupil=pupil,
            course=course,
            membership=membership,
            start_date=start_date,
        )
        enrollment.full_clean()
        enrollment.save()

    return membership
