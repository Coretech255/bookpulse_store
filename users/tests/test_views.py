from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from user.models import CustomUser
from django.contrib.messages import get_messages
from user.forms import CustomUserCreationForm, UpdateUserForm
from django.contrib.auth import authenticate, login


UserModel = get_user_model()

class RegisterViewTest(TestCase):
    def setUp(self):
        # Data for a new user registration
        self.valid_user_data = {
            #'username': 'newuser',
            'first_name': 'Ikechukwu',
            'last_name': 'Wise',
            'email': 'newuser@example.com',
            'password1': 'complexPassword123',
            'password2': 'complexPassword123'
        }

        # Invalid user data (email already in use)
        self.existing_user_data = {
            #'username': 'existinguser',
            'email': 'existinguser@example.com',
            'password1': 'Password123',
            'password2': 'Password123'
        }
        # Create an existing user to check duplicate email case
        self.existing_user = CustomUser.objects.create_user(
            #username='existinguser', 
            email='existinguser@example.com', 
            password='Password123'
        )

    def test_register_view_authenticated_user_redirects(self):
        # Simulate an authenticated user
        self.client.login(username='existinguser@example.com', password='Password123')
        response = self.client.get(reverse('user:register'))
        # Assert that the authenticated user is redirected to the shop:index page
        self.assertRedirects(response, reverse('shop:index'))

    def test_register_view_valid_form(self):
        # Test valid user registration
        response = self.client.post(reverse('user:register'), data=self.valid_user_data)
        print(response,'response')
        # Check if user was created
        user = CustomUser.objects.filter(email='newuser@example.com').exists()

        self.assertTrue(user)
        # Check if user is redirected to the login page
        self.assertRedirects(response, reverse('user:login'))
        # Check if a success message was displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Account created successfully. You can now log in.')

    def test_register_view_email_already_in_use(self):
        # Try to register with an email that is already in use
        response = self.client.post(reverse('user:register'), data=self.existing_user_data)
        # Check if the user was not created
        users_with_same_email = CustomUser.objects.filter(email='existinguser@example.com').count()
        self.assertEqual(users_with_same_email, 1)  # The user should already exist from setUp
        # Check if an error message is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'email: This email address is already in use.')

    def test_register_view_invalid_form(self):
        # Test invalid form (e.g., passwords don't match)
        invalid_form_data = self.valid_user_data.copy()
        print(invalid_form_data)
        invalid_form_data['password1'] = 'differentPassword'
        response = self.client.post(reverse('user:register'), data=invalid_form_data)
        # Ensure user is not created
        user = CustomUser.objects.filter(email='newuser@example.com').exists()
        self.assertFalse(user)
        # Check if form error message is displayed
        form = response.context.get('form')
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)  # Ensure that the error for password mismatch is present


class LoginViewTest(TestCase):

    def setUp(self):
        # Create a test user for login
        self.user = CustomUser.objects.create_user(
            #username='testuser',
            first_name = 'Ikechukwu',
            last_name = 'Wise', 
            email='testuser@example.com', 
            password='Password123'
        )
        # Login credentials
        self.valid_login_data = {
            'email': 'testuser@example.com',
            'password': 'Password123'
        }
        self.invalid_login_data = {
            'email': 'testuser@example.com',
            'password': 'WrongPassword'
        }

    def test_login_view_authenticated_user_redirects(self):
        # Simulate an authenticated user
        self.client.login(username='testuser@example.com', password='Password123')
        response = self.client.get(reverse('user:login'))
        # Assert that the authenticated user is redirected to the shop:index page
        self.assertRedirects(response, reverse('shop:index'))

    def test_login_view_valid_login(self):
        # Test valid login credentials
        response = self.client.post(reverse('user:login'), data=self.valid_login_data)
        # Check if user is redirected to the shop:index page after login
        self.assertRedirects(response, reverse('shop:index'))
        # Check if the user is authenticated
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)

    def test_login_view_invalid_login(self):
        # Test invalid login credentials
        response = self.client.post(reverse('user:login'), data=self.invalid_login_data)
        # Check if the error message is displayed
        self.assertContains(response, 'Invalid email or password')
        # Ensure the user is not authenticated
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

    def test_login_view_get_request_renders_login_form(self):
        # Test that a GET request renders the login form
        response = self.client.get(reverse('user:login'))
        # Check if the login form is rendered
        self.assertTemplateUsed(response, 'login_form.html')


class ProfileViewTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            #username='testuser', 
            first_name = 'Ikechukwu',
            last_name = 'Wise', 
            email='testuser@example.com', 
            password='Password123'
        )
        # Data to update the profile with
        self.valid_user_data = {
            'first_name': 'Ezechimere',
            'last_name': 'Ikechukwu',
            #'email': 'updateduser@example.com'
        }
        # Login the test user
        self.client.login(username='testuser@example.com', password='Password123')

    def test_profile_view_requires_login(self):
        # Log out the user to test login requirement
        self.client.logout()
        response = self.client.get('/user/auth/profile/')
        # Check the actual URL for redirection
        login_url = reverse('user:login')
        profile_url = reverse('user:profile')
        redirect_url = f"{login_url}?next={profile_url}"
            # Print the URLs for debugging
        print(f"Resolved login URL: {login_url}")
        print(f"Resolved profile URL: {profile_url}")
        print(f"Expected redirect URL: {redirect_url}")
        #self.assertRedirects(response, redirect_url)
        self.assertEquals(response.status_code, 302)

class LogoutViewTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            #username='testuser', 
            email='testuser@example.com', 
            password='Password123'
        )
        # Login the test user
        self.client.login(username='testuser@example.com', password='Password123')

    def test_logout_view_logged_in_user(self):
        # Simulate a GET request to the logout view
        response = self.client.get(reverse('user:logout'))
        
        # Check if the user is logged out
        user = self.client.session.get('_auth_user_id')
        self.assertIsNone(user)
        
        # Check if the user is redirected to the shop:index page
        self.assertRedirects(response, reverse('shop:index'))

    def test_logout_view_logged_out_user(self):
        # Log out the user first
        self.client.logout()
        
        # Simulate a GET request to the logout view
        response = self.client.get(reverse('user:logout'))
        
        # Check if the user is redirected to the shop:index page
        self.assertRedirects(response, reverse('shop:index'))





