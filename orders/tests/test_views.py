from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from orders.models import OrderItem, Order
from orders.forms import OrderCreateForm
from user.models import CustomUser
from cart.cart import Cart
from shop.models import Product
from decimal import Decimal

class OrderCreateViewTest(TestCase):

    def setUp(self):
        # Create a sample user
        self.user = CustomUser.objects.create_user(
            #username='testuser@example.com', 
            email='testuser@example.com', 
            password='testpassword'
        )

        # Create a sample product
        self.product = Product.objects.create(
            title='Sample Product',
            price=Decimal('19.99'),
            author="Author", 
            isbn="1234567890", 
            publication_date="1999"
        )

        # Create a cart and add an item
        self.client = Client()
        self.client.login(username='testuser@example.com', password='testpassword')
        #self.client.cookies.load({'cart': {'product_id': self.product.id, 'quantity': 2, 'price': str(self.product.price)}})
        # Set up a cart in the session
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {
                'quantity': 2,
                'price': str(self.product.price),
            }
        }
        session.save()

    def test_order_create_valid_form(self):
        # Mock the cart to return the product
        cart = Cart(self.client)
        cart.__iter__ = lambda: [{'product': self.product, 'price': self.product.price, 'quantity': 2}]
        
        response = self.client.post(reverse('orders:order_create'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@example.com',
            'address': '123 Main St',
            'postal_code': '12345',
            'city': 'Anytown',
        })
        
        # Check if the order is created
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertTrue(Order.objects.exists())
        self.assertEqual(OrderItem.objects.count(), 1)
        
        order = Order.objects.first()
        order_item = OrderItem.objects.first()
        
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, self.product.price)

        # Check if the cart is cleared (assuming cart.clear() is implemented correctly)
        self.assertEqual(Cart(self.client).get_total_price(), Decimal('0.00'))

    def test_order_create_invalid_form(self):
        response = self.client.post(reverse('orders:order_create'), {
            'first_name': '',  # Invalid form data
            'last_name': '',
            'email': 'invalid-email',
            'address': '',
            'postal_code': '',
            'city': '',
        })
        

        # Check if the form is rendered again with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order.html')
        self.assertContains(response, 'This field is required.')

    def test_order_create_no_cart(self):
        # Simulate an empty cart
        #self.client.cookies.load({'cart': {}})
        session = self.client.session
        session['cart'] = {}
        session.save()
        
        response = self.client.post(reverse('orders:order_create'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'address': '123 Main St',
            'postal_code': '12345',
            'city': 'Anytown',
        })
        
        # Check if no order is created
        self.assertEqual(Order.objects.count(), 0)
        self.assertRedirects(response, reverse('cart:cart_detail'))

    def tearDown(self):
        self.client.logout()
