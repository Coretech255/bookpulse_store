from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

class CustomUserManagerTests(TestCase):

    def setUp(self):
        self.UserModel = get_user_model()

    def test_create_user_with_email_successful(self):
        user = self.UserModel.objects.create_user(
            email='testuser@example.com',
            password='testpassword'
        )
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('testpassword'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            self.UserModel.objects.create_user(email='', password='testpassword')

    def test_create_superuser(self):
        superuser = self.UserModel.objects.create_superuser(
            email='superuser@example.com',
            password='superpassword'
        )
        self.assertEqual(superuser.email, 'superuser@example.com')
        self.assertTrue(superuser.check_password('superpassword'))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_superuser_without_is_staff(self):
        with self.assertRaises(ValueError):
            self.UserModel.objects.create_superuser(
                email='wrongsuperuser@example.com',
                password='wrongpassword',
                is_staff=False
            )

    def test_create_superuser_without_is_superuser(self):
        with self.assertRaises(ValueError):
            self.UserModel.objects.create_superuser(
                email='wrongsuperuser@example.com',
                password='wrongpassword',
                is_superuser=False
            )
    
    def test_user_str(self):
        user = self.UserModel.objects.create_user(
            email='strtestuser@example.com',
            password='strpassword'
        )
        self.assertEqual(str(user), 'strtestuser@example.com')