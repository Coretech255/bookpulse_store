from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    #path('register_form/', views.RegistrationFormView, name='registration_form'),
    path('register/', views.registerView, name='register'),
    path('profile/', views.ProfileView, name='profile'),
    path('login/', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name='logout')
]