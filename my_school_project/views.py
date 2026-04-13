from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SchoolLoginForm

def login_view(request):
    # 1. If the user clicks the LOGIN button (POST request)
    if request.method == 'POST':
        form = SchoolLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Send them directly to the dashboard upon successful login!
            return redirect('dashboard') 
    
    # 2. If the user is just loading the page for the first time (GET request)
    else:
        form = SchoolLoginForm()
        
    # Render the login page and pass the form fields to it
    return render(request, 'account/login.html', {'form': form})

def dashboard_view(request):
    return render(request, 'account/login.html')