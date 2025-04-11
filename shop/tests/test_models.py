from django.test import TestCase
from shop.models import Category, Product, Interaction, Rating
from user.models import CustomUser

class CategoryModelTest(TestCase):

    def test_category_creation(self):
        category = Category.objects.create(name="Fiction", description="Fictional books category")
        self.assertEqual(str(category), "Fiction")


class ProductModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Fiction", description="Fictional books category")
        self.product = Product.objects.create(
            title="Example Book",
            author="Author Name",
            description="An example book description",
            price=19.99,
            isbn="1234567890123",
            publication_date=2023
        )
        self.product.categories.add(self.category)

    def test_product_creation(self):
        self.assertEqual(str(self.product), "Example Book")
        self.assertEqual(self.product.isbn, "1234567890123")

    def test_product_categories(self):
        self.assertIn(self.category, self.product.categories.all())

    def test_product_ordering(self):
        product2 = Product.objects.create(
            title="Another Book",
            price=14.99,
            isbn="9876543210987",
            publication_date=2022
        )
        products = Product.objects.all()
        self.assertEqual(products[0], product2)  # product2 was created last, so it should come first


class InteractionModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(email="user@example.com", password="testpassword")
        self.product = Product.objects.create(
            title="Example Book",
            price=19.99,
            isbn="1234567890123",
            publication_date=2023
        )
        self.interaction = Interaction.objects.create(
            user=self.user,
            product=self.product,
            liked=True,
            clicks=3,
            time_spent=120.0,
            added_to_cart=False
        )

    def test_interaction_creation(self):
        self.assertEqual(str(self.interaction), "user@example.com - Example Book - Interaction")
    
    def test_calculate_interaction_value_liked(self):
        self.assertEqual(self.interaction.calculate_interaction_value(), 7.0)
    
    def test_calculate_interaction_value_cart(self):
        self.interaction.liked = False
        self.interaction.added_to_cart = True
        self.interaction.save()
        self.assertEqual(self.interaction.calculate_interaction_value(), 10.0)

    def test_calculate_interaction_value_clicks_time(self):
        self.interaction.liked = False
        self.interaction.added_to_cart = False
        self.interaction.save()
        self.assertEqual(self.interaction.calculate_interaction_value(), 5.0)


class RatingModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(email="user@example.com", password="testpassword")
        self.product = Product.objects.create(
            title="Example Book",
            price=19.99,
            isbn="1234567890123",
            publication_date=2023
        )
        self.rating = Rating.objects.create(
            user=self.user,
            product=self.product,
            rating=8.0,
            review="Great book!"
        )

    def test_rating_creation(self):
        expected_str = f"{self.user.first_name} {self.user.last_name} - Example Book - 8.0"
        self.assertEqual(str(self.rating), expected_str)

    def test_update_rating(self):
        self.rating.update_rating(9.5)
        self.assertEqual(self.rating.rating, 9.5)

    def test_update_rating_over_max(self):
        self.rating.update_rating(12.0)
        self.assertEqual(self.rating.rating, 10.0)  # Rating should be capped at 10.0

    def test_rating_creation_with_no_user(self):
        # Test case where user is not set
        rating_without_user = Rating.objects.create(
            user=None,
            product=self.product,
            rating=7.5,
            review="Good book!"
        )
        expected_str = "Anonymous - Example Book - 7.5"
        self.assertEqual(str(rating_without_user), expected_str)
