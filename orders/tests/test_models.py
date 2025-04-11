from django.test import TestCase
from orders.models import Order, OrderItem
from shop.models import Product
from decimal import Decimal

class OrderModelTest(TestCase):

    def setUp(self):
        # Create a sample product
        self.product = Product.objects.create(
            title='Sample Product',
            price=Decimal('19.99'),
            author="Author", 
            isbn="1234567890", 
            publication_date="1999"
        )

        # Create a sample order
        self.order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            address='123 Main St',
            postal_code='12345',
            city='Anytown',
            paid=True,
        )
        
        # Add items to the order
        self.order.items.create(product=self.product, price=self.product.price, quantity=2)

    def test_order_creation(self):
        # Test if the order was created successfully
        self.assertEqual(self.order.first_name, 'John')
        self.assertEqual(self.order.last_name, 'Doe')
        self.assertEqual(self.order.email, 'john.doe@example.com')
        self.assertEqual(self.order.address, '123 Main St')
        self.assertEqual(self.order.postal_code, '12345')
        self.assertEqual(self.order.city, 'Anytown')
        self.assertTrue(self.order.paid)

    def test_get_total_cost(self):
        # Test if the total cost is calculated correctly
        expected_total = Decimal('39.98')  # Price * Quantity
        self.assertEqual(self.order.get_total_cost(), expected_total)

    def test_order_str(self):
        # Test the string representation of the order
        self.assertEqual(str(self.order), 'Order John')


class OrderItemModelTest(TestCase):

    def setUp(self):
        # Create a sample product
        self.product = Product.objects.create(
            title='Sample Product',
            price=Decimal('19.99'),
            author="Author", 
            isbn="1234567890", 
            publication_date="1999"
        )

        # Create a sample order
        self.order = Order.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            address='123 Main St',
            postal_code='12345',
            city='Anytown',
            paid=True,
        )

        # Create a sample order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=self.product.price,
            quantity=2
        )

    def test_order_item_creation(self):
        # Test if the order item was created successfully
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.price, Decimal('19.99'))
        self.assertEqual(self.order_item.quantity, 2)

    def test_get_cost(self):
        # Test if the cost is calculated correctly
        expected_cost = Decimal('39.98')  # Price * Quantity
        self.assertEqual(self.order_item.get_cost(), expected_cost)

    def test_order_item_str(self):
        # Test the string representation of the order item
        self.assertEqual(str(self.order_item), str(self.order_item.id))
