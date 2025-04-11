from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
import pandas as pd
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from cart.forms import CartAddProductForm
from .forms import RatingForm
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Product, Interaction, Rating, Category
from cart.cart import Cart
import pandas as pd
from .models import Rating
from surprise import Dataset, Reader, SVDpp
from surprise.model_selection import train_test_split
from django.shortcuts import render
from .recommendation import load_data, train_algorithm, get_top_n_recommendations
import logging

logger = logging.getLogger(__name__)

# Create your views here.

def IndexView(request):
    cart = Cart(request)
    return render(request,'shop/index.html', {'cart': cart})

#def category_list(request):
#    categories = Category.objects.all()
 #   logger.info(f"Categories: {list(categories)}")
  #  return render(request, 'root/_header.html', {'categories': categories})

def books_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    books = Product.objects.filter(categories=category)
    return render(request, 'shop/books_by_category.html', {'category': category, 'books': books})

# ListView - Display a list of objects
class ProductListView(ListView):
    model = Product
    template_name = 'shop/index.html'
    context_object_name = 'products'
    paginate_by = 30

    def get_queryset(self):
        return Product.objects.all()
    

class ProductSearchListView(ListView):
    model = Product
    template_name = 'shop/search_results.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(isbn__icontains=query)
            )
        return Product.objects.none()  # Return an empty queryset if no query



# DetailView - Display details of a single object
class ProductDetailView(DetailView):
    model = Product
    cart_product_form = CartAddProductForm()
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_object(self):
        isbn = self.kwargs.get("isbn")
        return Product.objects.get(isbn=isbn)

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Check if the current user has liked this product
        #user_has_liked = Interaction.objects.filter(user=self.request.user, product=product, liked=True).exists()
        # Check if the user is authenticated before querying for interactions
        if self.request.user.is_authenticated:
            user_has_liked = Interaction.objects.filter(
                user=self.request.user,
                product=product,
                liked=True
            ).exists()
        else:
            user_has_liked = False

        # Add additional context data here
        cart_product_form = CartAddProductForm()
        context['cart_product_form'] = cart_product_form
        
        related_products = Product.objects.filter(categories__in=product.categories.all()).exclude(id=product.id).distinct()[:5]
        context['related_products'] = related_products  # Exclude the current product and select some other products
        context['rating_form'] = RatingForm()
        context['ratings'] = Rating.objects.filter(product=self.object)
        context['user_has_liked'] = user_has_liked
        context['categories'] = self.object.categories.all()  # Load categories

        # Fetch the current book

        # If the user is authenticated, generate recommendations
        if self.request.user.is_authenticated:
            user_id = self.request.user.id

            # load data and train the algorithm
            data, df = self.load_data()

            algo = self.train_algorithm(data)

            # Get top N recommendations for the user
            recommendations = self.get_top_n_recommendations(algo, user_id, df, n=10)
            
            # Retrieve the recommended books
            recommended_books = Product.objects.filter(isbn__in=recommendations)
        else:
            # For unauthenticated users, no recommendations, show related books only
            recommended_books = Product.objects.none()

        # Add the recommended books to the context
        context['recommended_books'] = recommended_books

        return context
    
    def load_data(self):
        # Load data from the Rating model
        ratings = Rating.objects.all().values('user_id', 'product_id', 'rating')
        df = pd.DataFrame(list(ratings))
        
        # Define the rating scale and load data into a Surprise dataset
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(df[['user_id', 'product_id', 'rating']], reader)
        return data, df
    

    def train_algorithm(self, data):
    # Use the SVD++ algorithm
        algo = SVDpp()
        
        # Train the algorithm on the entire dataset
        trainset = data.build_full_trainset()
        algo.fit(trainset)
        
        return algo

    def get_top_n_recommendations(self, algo, user_id, df, n=10):
        # Get a list of all book_ids
        all_books = df['product_id'].unique()
        
        # Get the books the user has already rated
        rated_books = df[df['user_id'] == user_id]['product_id']

        if rated_books.empty:
            return JsonResponse({"message": "No Books Recommended!. <br> Click and like a book to get recommendation"})
        
        # Remove already rated books from the list of all books
        books_to_predict = [book for book in all_books if book not in rated_books.values]

        
        # Predict ratings for each book the user hasn't rated yet
        predictions = [algo.predict(user_id, book_id) for book_id in books_to_predict]
        
        # Sort the predictions by the estimated rating
        predictions.sort(key=lambda x: x.est, reverse=True)
        
        # Return the top N book_ids
        top_n_books = [pred.iid for pred in predictions[:n]]
        return top_n_books


    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = RatingForm(request.POST)
            product = self.get_object()
            if form.is_valid():
                rating = form.save(commit=False)
                rating.user = request.user
                rating.product = product
                rating.save()
                messages.success(request, "Your review has been submitted.")
            else:
                messages.error(request, "There was an error with your review.")
            return redirect('shop:product_detail',  isbn=product.isbn)
        else:
            messages.error(request, "You need to be logged in to leave a review.")
            return redirect('user:login')

#Get Interaction
def register_interaction(request, isbn):
    product = get_object_or_404(Product, isbn=isbn)
    user = request.user
    #print(user)

    interaction, created = Interaction.objects.get_or_create(user=user, product=product)
    rating_value = 0.0
    if 'like' in request.POST:
        interaction.liked = True
        rating_value = interaction.calculate_interaction_value()
    elif 'add_to_cart'in request.POST:
        interaction.added_to_cart = True
        rating_value = interaction.calculate_interaction_value()
    elif 'click' in request.POST:
        interaction.clicks += 1
        if 'time_spent' in request.POST:
            interaction.time_spent += float(request.POST['time_spent'])
            rating_value = interaction.calculate_interaction_value()

    interaction.save()

    # Update or create the rating
    rating, created = Rating.objects.get_or_create(user=user, product=product)
    rating.update_rating(rating_value)

    return JsonResponse({
        'status': 'success',
        'rating':rating.rating
    })
    
            

def recommend_books_view(request, user_id):
    # Load data and train the algorithm
    data, df = load_data()
    algo = train_algorithm(data)
    
    # Get top 10 recommendations for the user
    recommendations = get_top_n_recommendations(algo, user_id, df, n=30)
    
    # Retrieve the book objects for the recommended book_ids
    recommended_books = Product.objects.filter(isbn__in=recommendations)
    
    # Render the template with the recommended books
    return render(request, 'shop/recommendations.html', {'recommended_books': recommended_books})

