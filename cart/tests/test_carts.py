from django.test import TestCase, RequestFactory
from decimal import Decimal
from django.conf import settings
from shop.models import Product
from cart.cart import Cart

class CartTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.session = self.client.session
        
        # Create sample products
        self.product1 = Product.objects.create(
            title="Test Product 1", 
            price=Decimal('10.00'),
            author="Author Name",
            description="An example book description",
            isbn="1234567890123",
            publication_date=2023
        )
        self.product2 = Product.objects.create(
            title="Test Product 2", 
            price=Decimal('20.00'),
            author="Author Name",
            description="An example book description",
            isbn="123456789034",
            publication_date=2023
        )
        
        self.cart = Cart(self.request)

    def test_add_product(self):
        # Add product to cart
        self.cart.add(self.product1, quantity=2)
        self.cart.add(self.product2)

        # Verify cart length
        self.assertEqual(len(self.cart), 3)  # Total 2 of product1 + 1 of product2

        # Check total price
        total_price = self.cart.get_total_price()
        self.assertEqual(total_price, Decimal('40.00'))  # (2*10) + 20

    def test_remove_product(self):
        # Add product then remove it
        self.cart.add(self.product1)
        self.cart.remove(self.product1)

        # Cart should be empty
        self.assertEqual(len(self.cart), 0)

    def test_cart_total_price(self):
        # Add products
        self.cart.add(self.product1, quantity=2)
        self.cart.add(self.product2, quantity=1)

        # Check total price
        total_price = self.cart.get_total_price()
        self.assertEqual(total_price, Decimal('40.00'))

    def test_clear_cart(self):
        # Add product and then clear cart
        self.cart.add(self.product1)
        cleared_cart = self.cart.clear()
        # Cart should be empty after clearing
        self.assertEqual(cleared_cart, None)

