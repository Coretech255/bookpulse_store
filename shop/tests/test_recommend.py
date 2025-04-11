from django.contrib.auth import get_user_model
from django.test import TestCase
from shop.models import Rating, Product
from user.models import CustomUser
from shop.recommendation import load_data, train_algorithm, get_top_n_recommendations

User = get_user_model()

class RecommendationsTestCase(TestCase):
    def setUp(self):
                # Create test users
        user1 = CustomUser.objects.create(email='user1@example.com', password='password123')
        user2 = CustomUser.objects.create(email='user2@example.com', password='password123')

        Product.objects.create(
            isbn=101, 
            title='Product 101',
            author="Author Name",
            description="An example book description",
            price=19.99,
            publication_date=2023    
        )

        Product.objects.create(isbn=102, title='Product 102',            
            author="Author Name",
            description="An example book ",
            price=19.99,
            publication_date=2023   
        )

        Product.objects.create(isbn=103, title='Product 103',            
            author="Author Name",
            description="An example book bio",
            price=19.99,
            publication_date=2023   
        )

        # Create test data
        Rating.objects.create(user=user1, product_id=101, rating=4)
        Rating.objects.create(user=user1, product_id=102, rating=5)
        Rating.objects.create(user=user2, product_id=101, rating=3)
        Rating.objects.create(user=user2, product_id=103, rating=4)
        
        # Load and train the algorithm
        self.data, self.df = load_data()
        self.algo = train_algorithm(self.data)
    
    def test_get_top_n_recommendations(self):
        # Test recommendations for user_id=1
        top_n_books = get_top_n_recommendations(self.algo, 1, self.df, n=2)
        
        # Check that the recommendations are returned as a list
        self.assertIsInstance(top_n_books, list)
        
        # Check that the list contains the correct number of recommendations
        self.assertEqual(len(top_n_books), 1)
        
        # Optionally, check that the recommendations do not include already rated books
        rated_books = self.df[self.df['user_id'] == 1]['product_id'].tolist()
        self.assertNotIn(rated_books[0], top_n_books)

