from django.test import TestCase
from user.forms import CustomUserCreationForm, UpdateUserForm
from user.models import CustomUser

class CustomUserCreationFormTest(TestCase):

    def setUp(self):
        # Create an existing user for testing email uniqueness
        self.existing_user = CustomUser.objects.create_user(
            email='existinguser@example.com',
            first_name='Existing',
            last_name='User',
            phone_number='1234567890',
            date_of_birth='1990-01-01',
            password='TestPassword123'
        )

    def test_form_valid_data(self):
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '0987654321',
            'date_of_birth': '1995-05-05',
            'password1': 'ValidPassword123',
            'password2': 'ValidPassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('ValidPassword123'))

    def test_form_invalid_email_already_in_use(self):
        form_data = {
            'email': 'existinguser@example.com',  # Email already exists
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '0987654321',
            'date_of_birth': '1995-05-05',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], 'This email address is already in use.')

    def test_form_invalid_password_mismatch(self):
        form_data = {
            'email': 'newuser2@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '0987654321',
            'date_of_birth': '1995-05-05',
            'password1': 'Password123',
            'password2': 'Password321',  # Mismatching passwords
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)



class UpdateUserFormTest(TestCase):

    def setUp(self):
        # Create two users, one for updating and one to test email uniqueness
        self.user = CustomUser.objects.create_user(
            email='user@example.com',
            first_name='Original',
            last_name='User',
            phone_number='1234567890',
            date_of_birth='1990-01-01',
            password='TestPassword123'
        )
        self.existing_user = CustomUser.objects.create_user(
            email='existinguser@example.com',
            first_name='Existing',
            last_name='User',
            phone_number='0987654321',
            date_of_birth='1995-05-05',
            password='TestPassword123'
        )

    def test_form_valid_data(self):
        form_data = {
            'email': 'updateduser@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'phone_number': '9876543210',
            'date_of_birth': '1995-05-05'
        }
        form = UpdateUserForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        
        # Check that the user's data was updated correctly
        self.assertEqual(updated_user.email, 'updateduser@example.com')
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'User')
        self.assertEqual(updated_user.phone_number, '9876543210')
        self.assertEqual(updated_user.date_of_birth.strftime('%Y-%m-%d'), '1995-05-05')

    def test_form_invalid_email_already_in_use(self):
        form_data = {
            'email': 'existinguser@example.com',  # Email already in use by another user
            'first_name': 'Updated',
            'last_name': 'User',
            'phone_number': '9876543210',
            'date_of_birth': '1995-05-05'
        }
        form = UpdateUserForm(data=form_data, instance=self.user)
        
        # The form should be invalid because the email is already used by another user
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], 'Custom user with this Email already exists.')

    def test_form_no_changes(self):
        # Simulate submitting the form without changing any data
        form_data = {
            'email': 'user@example.com',
            'first_name': 'Original',
            'last_name': 'User',
            'phone_number': '1234567890',
            'date_of_birth': '1990-01-01'
        }
        form = UpdateUserForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        
        # Check that the data remains the same
        self.assertEqual(updated_user.email, 'user@example.com')
        self.assertEqual(updated_user.first_name, 'Original')
        self.assertEqual(updated_user.last_name, 'User')
        self.assertEqual(updated_user.phone_number, '1234567890')
        self.assertEqual(updated_user.date_of_birth.strftime('%Y-%m-%d'), '1990-01-01')
