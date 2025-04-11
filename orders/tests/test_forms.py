from django.test import TestCase
from orders.forms import OrderCreateForm

class OrderCreateFormTest(TestCase):
    
    def test_form_valid_data(self):
        """Test that the form is valid with proper data."""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'address': '123 Main St',
            'postal_code': '12345',
            'city': 'Anytown'
        }
        form = OrderCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_missing_required_fields(self):
        """Test that the form is invalid when required fields are missing."""
        form_data = {
            'first_name': '',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'address': '123 Main St',
            'postal_code': '12345',
            'city': 'Anytown'
        }
        form = OrderCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
    
    def test_form_invalid_email(self):
        """Test that the form is invalid with an incorrect email format."""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalid-email',
            'address': '123 Main St',
            'postal_code': '12345',
            'city': 'Anytown'
        }
        form = OrderCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_missing_all_fields(self):
        """Test that the form is invalid if no data is provided."""
        form_data = {}
        form = OrderCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 6)  # since all fields are required
