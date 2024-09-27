from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from django.contrib.auth.decorators import login_required


# Signup view
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({"message": "Username already exists"}, status=400)

        # Hash the password before storing it for security
        user = User.objects.create(username=username, password=make_password(password))
        user.save()

        return JsonResponse({"message": "User created successfully"}, status=201)

    # If it's a GET request, render the signup form
    return render(request, 'signup.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')  
        else:
            return JsonResponse({"message": "Invalid credentials"}, status=400)

    return render(request, 'login.html')

# Dashboard view
@login_required  # Ensures only logged-in users can access the dashboard
def dashboard(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user  
    signup_date = user.date_joined  
    return render(request, 'profile.html', {'user': user, 'signup_date': signup_date})