from django.http import JsonResponse
import pandas as pd
from .models import Rating
from surprise import Dataset, Reader, SVDpp
from surprise.model_selection import train_test_split


def load_data():
    # Load data from the Rating model
    ratings = Rating.objects.all().values('user_id', 'product_id', 'rating')
    df = pd.DataFrame(list(ratings))
    
    # Define the rating scale and load data into a Surprise dataset
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['user_id', 'product_id', 'rating']], reader)
    return data, df

def train_algorithm(data):
    # Use the SVD++ algorithm
    algo = SVDpp()
    
    # Train the algorithm on the entire dataset
    trainset = data.build_full_trainset()
    algo.fit(trainset)
    
    return algo

def get_top_n_recommendations(algo, user_id, df, n=30):
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

