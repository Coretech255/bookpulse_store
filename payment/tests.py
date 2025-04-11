from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.conf import settings
from orders.models import Order, OrderItem
from shop.models import Product
from decimal import Decimal

class PaymentProcessViewTest(TestCase):

    def setUp(self):
        # Create a product and order for testing
        self.product = Product.objects.create(title='Test Product', price=Decimal('10.00'), author="Author", 
                                              isbn="1234567890", publication_date="1999")
        self.order = Order.objects.create(id=1)
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product, price=Decimal('10.00'), quantity=2)
        #self.client.session['order_id'] = self.order.id
            # Set the session with the valid order ID
        session = self.client.session
        session['order_id'] = self.order.id
        session.save()

    @patch('stripe.checkout.Session.create')
    def test_payment_process_view_success(self, mock_stripe_session_create):
        # Mock the Stripe session creation
        mock_stripe_session_create.return_value = {'url': 'https://stripe.com/payment'}

        response = self.client.post(reverse('payment:process'))

        # Ensure the request was successful
        self.assertEqual(response.status_code, 302)

        # Check if the Stripe session is created correctly
        self.assertTrue(mock_stripe_session_create.called)
        
        # Check that the correct data was passed to the Stripe API
        session_data = mock_stripe_session_create.call_args[1]
        self.assertEqual(session_data['mode'], 'payment')
        self.assertEqual(session_data['client_reference_id'], self.order.id)
        self.assertEqual(session_data['line_items'][0]['quantity'], self.order_item.quantity)

        # Ensure the user is redirected to the Stripe payment page
        self.assertRedirects(response, 'https://stripe.com/payment', status_code=302, fetch_redirect_response=False)

    @patch('stripe.checkout.Session.create')
    def test_payment_process_view_order_not_found(self, mock_stripe_session_create):
        # Remove the order from the session to simulate an order not found scenario
        # Safely remove 'order_id' from the session (won't raise KeyError if it's missing)
        session = self.client.session
        session.pop('order_id', None)
        session.save()

        response = self.client.post(reverse('payment:process'))

        # Assert that the view responds with a 404 if the order is not found
        self.assertEqual(response.status_code, 404)

    @patch('stripe.checkout.Session.create')
    def test_payment_process_view_get_request(self, mock_stripe_session_create):
        response = self.client.get(reverse('payment:process'))
        # Ensure the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Ensure no Stripe session is created when accessed via GET
        self.assertFalse(mock_stripe_session_create.called)
        
        # Ensure the GET request renders the payment process template
        self.assertTemplateUsed(response, 'payment/process.html')

