from django import forms
from django.test import TestCase
from cart.forms import CartAddProductForm

class CartAddProductFormTest(TestCase):

    def test_form_initialization(self):
        # Test initialization with default values
        form = CartAddProductForm()
        
        # Check if the form contains the correct fields
        self.assertIn('quantity', form.fields)
        self.assertIn('override', form.fields)

        # Check if 'quantity' field has the correct choices
        self.assertEqual(form.fields['quantity'].choices, [(1, '1'), (2, '2'), (3, '3'), (4, '4')])
        
        # Check if 'override' field is a hidden input
        self.assertIsInstance(form.fields['override'].widget, forms.HiddenInput)

    def test_form_valid_data(self):
        # Test form with valid data
        form_data = {'quantity': 3, 'override': True}
        form = CartAddProductForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['quantity'], 3)
        self.assertTrue(form.cleaned_data['override'])

    def test_form_invalid_data(self):
        # Test form with invalid data
        form_data = {'quantity': 'invalid', 'override': True}
        form = CartAddProductForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
