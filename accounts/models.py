from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        PUPIL = 'pupil', 'Pupil'
        TEACHER = 'teacher', 'Teacher'

    role = models.CharField(
        max_length=7,
        choices=Role.choices,
        default=Role.PUPIL,
    )
    must_change_password = models.BooleanField(default=False)
    preferred_language = models.CharField(
        max_length=2,
        choices=(('uz', 'O‘zbekcha'), ('ru', 'Русский'), ('en', 'English')),
        default='uz',
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=('pupil', 'teacher')),
                name='accounts_user_role_valid',
            ),
        ]
