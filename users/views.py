from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, UpdateUserForm  # Assuming you have a custom user creation form
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth.decorators import login_required


def registerView(request):
    if request.user.is_authenticated:
        return redirect('shop:index')
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Check if email is already in use
            email = form.cleaned_data['email']
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email is already in use.')
                return redirect('registration_form')

            # Check if password meets complexity requirements
            password = form.cleaned_data['password1']
            if not is_password_complex(password):
                messages.error(request, 'Password must be at least 8 characters long and contain both letters and numbers.')
                return redirect('registration_form')
            
            # Save user if all validation passes
            user = form.save()
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('user:login')  # Redirect to login page after successful registration
        else:
            # Display error messages if form is invalid
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            # You can also pass the invalid form back to the template for display
            return render(request, 'registration_form.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration_form.html', {'form': form})


def is_password_complex(password):
    # Check if password meets complexity requirements (e.g., at least 8 characters long and contains both letters and numbers)
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True


def LoginView(request):
    if request.user.is_authenticated:
        return redirect('shop:index')
    elif request.method == 'POST':
        email = request.POST.get('email')  # Assuming email is used as username
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page or home page
            return redirect('shop:index')  # Redirect to home page after successful login
        else:
            return render(request, 'login_form.html', 
                          {'error_message': 'Invalid email or password'})
    else:
        return render(request, 'login_form.html')


@login_required
def ProfileView(request):
    if request.method =='POST':
        user_form = UpdateUserForm(request.POST,instance=request.user)
        if user_form.is_valid():
            user_form.save()
        messages.success(request, 'Your profile is updated successfully')
        return redirect('user:profile')
    else:
        return render(request, 'profile.html')


def LogoutView(request):
    logout(request)
    return redirect('shop:index')