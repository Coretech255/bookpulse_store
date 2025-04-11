from django.test import TestCase
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from shop.models import Product
from cart.cart import Cart
from cart.views import cart_add
from cart.forms import CartAddProductForm
from django.contrib.auth import get_user_model

class CartViewTest(TestCase):
    
    def setUp(self):
        # Create a product for testing
        self.product = Product.objects.create(
            title='Test Product', 
            price=100,
            author="Author", 
            isbn="1234567890", 
            publication_date="1999"
            )
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            #username='testuser@example.com', 
            email="testuser@example.com",
            password='password'
        )
    
    def test_cart_add(self):
        #Test adding a product to the cart.
        # Create a POST request to add the product to the cart
        data = {'quantity': 1, 'override': False}
        request = self.factory.post(reverse('cart:cart_add', args=[self.product.id]), data)
        
        # Add session to request (since cart relies on session)
        middleware = SessionMiddleware(get_response=lambda x: x)
        middleware.process_request(request)
        request.session.save()
        
        # Call the cart_add view
        response = cart_add(request, self.product.id)
        
        # Check if the product was added to the cart
        cart = Cart(request)
        cart_items = list(cart)
        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0]['quantity'], 1)

        # Check redirection to cart detail page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('cart:cart_detail'))
        
    def test_cart_remove(self):
        #Test removing a product from the cart.
        # Add a product to the cart
        session = self.client.session
        cart = Cart(self.client) 
        cart.add(product=self.product, quantity=1)
        cart.save()  # Save the session after modification
        
        # Create a POST request to remove the product from the cart
        response = self.client.post(reverse('cart:cart_remove', args=[self.product.id]))
        
        # Check if the product has been removed from the cart
    # Reload the session after modifying the cart
        session = self.client.session
        cart = Cart(self.client)
        self.assertEqual(len(cart), 0)  # Ensure the cart is now empty
        
        # Assert redirection after removal
        self.assertRedirects(response, reverse('cart:cart_detail'))



class CartDetailViewTest(TestCase):

    def setUp(self):
        # Create a sample product to add to the cart
        self.product = Product.objects.create(
            title='Test Product', 
            price=100,
            author="Author", 
            isbn="1234567890", 
            publication_date="1999"
        )

        # Initialize session and cart
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {'quantity': 1, 'price': str(self.product.price)}
        }
        session.save()

    def test_cart_detail_view(self):
        # Send a GET request to the cart detail page
        response = self.client.get(reverse('cart:cart_detail'))

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used
        self.assertTemplateUsed(response, 'cart/detail.html')

        # Verify that the cart is passed to the context
        cart = response.context['cart']

        # Verify the cart items and their properties
        self.assertTrue(isinstance(cart, Cart))  # Ensure it's a Cart instance

        # Verify that the cart contains the product added in setUp
        found = False
        for item in cart:
            if item['product'].id == self.product.id:  # Assuming 'product' is part of the item dictionary
                self.assertEqual(item['quantity'], 1)
                found = True
                # Check that the update_quantity_form is in the context for each item
                self.assertIn('update_quantity_form', item)
        
        self.assertTrue(found)