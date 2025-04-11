from django.test import TestCase, Client
from django.urls import reverse
from shop.models import Product, Rating
from user.models import CustomUser
from shop.views import recommend_books_view
from unittest.mock import patch

class ProductSearchListViewTestCase(TestCase):
    def setUp(self):
        # Create test products
        Product.objects.create(
            title='Book A', 
            author='Author A', 
            isbn='123456', 
            description="An example book description",
            price=19.99,
            publication_date=2023
        )
        Product.objects.create(
            title='Book B', 
            author='Author B', 
            isbn='234567',
            description="An example book description",
            price=19.99,
            publication_date=2023
        )
        Product.objects.create(
            title='Another Book', 
            author='Author C', 
            isbn='345678',            
            description="An example book description",
            price=19.99,
            publication_date=2023
        )
    
    def test_search_with_query(self):
        # Send a GET request with a search query
        response = self.client.get(reverse('shop:product-search') + '?q=Book')
        
        # Check that the response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Check that the correct products are in the context
        self.assertContains(response, 'Book A')
        self.assertContains(response, 'Book B')
        #self.assertNotContains(response, 'Another')
        
        # Check that the template used is correct
        self.assertTemplateUsed(response, 'shop/search_results.html')
    
    def test_search_without_query(self):
        # Send a GET request without a search query
        response = self.client.get(reverse('shop:product-search'))
        
        # Check that the response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Check that no products are in the context
        self.assertContains(response, 'No products found')
        
        # Check that the template used is correct
        self.assertTemplateUsed(response, 'shop/search_results.html')



class RecommendBooksViewTestCase(TestCase):
    def setUp(self):
        # Create test users
        user1 = CustomUser.objects.create(email='user1@gmail.com', password='password123')
        
        # Create test products
        self.product1 = Product.objects.create(
            isbn='123456', 
            title='Book A',
            author="Author A",
            description="An example book description",
            price=19.99,
            publication_date=2023    
        )
        self.product2 = Product.objects.create(
            isbn='234567', 
            title='Book B', 
            author='Author B',
            description="An example book description",
            price=19.99,
            publication_date=2023 
        )
        self.product3 = Product.objects.create(
            isbn='345678', 
            title='Another Book', 
            author='Author C',
            description="An example book description",
            price=19.99,
            publication_date=2023 
        )
        
        # Create test ratings
        Rating.objects.create(user_id=user1.id, product_id=self.product1.isbn, rating=4)
        Rating.objects.create(user_id=user1.id, product_id=self.product2.isbn, rating=5)
        
        # Create a test client
        self.client = Client()
    
    @patch('shop.views.get_top_n_recommendations')
    def test_recommend_books_view(self, mock_get_top_n_recommendations):
        # Mock the recommendation function
        mock_get_top_n_recommendations.return_value = [self.product2.isbn, self.product1.isbn]
        
        # Simulate a request to the view
        response = self.client.get(reverse('shop:recommendations', kwargs={'user_id': 1}))
        
        # Check that the response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Check that the correct template is used
        self.assertTemplateUsed(response, 'shop/recommendations.html')
        
        # Check that the recommended books are included in the response context
        self.assertIn(self.product1, response.context['recommended_books'])
        self.assertIn(self.product2, response.context['recommended_books'])
        self.assertNotIn(self.product3, response.context['recommended_books'])
