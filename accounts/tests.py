from django.test import TestCase

from .models import User


class UserPasswordHashTests(TestCase):
    def test_create_user_hashes_password(self):
        raw_password = 'synthetic-test-password'
        user = User.objects.create_user(
            username='synthetic-pupil',
            password=raw_password,
            role=User.Role.PUPIL,
        )

        self.assertNotEqual(user.password, raw_password)
        self.assertTrue(user.check_password(raw_password))
