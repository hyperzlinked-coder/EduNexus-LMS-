from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import SchoolLoginForm

# --- 1. MGA SECURITY CHECK FUNCTIONS ---

def is_admin(user):
    return user.is_authenticated and user.is_superuser

def is_teacher(user):
    # Idinagdag natin ang check para sa 'is_staff' para mas madaling i-test
    return user.is_authenticated and (user.groups.filter(name='Teacher').exists() or user.is_staff)

def is_student(user):
    # Student kung hindi admin at hindi teacher
    return user.is_authenticated and not user.is_superuser and not user.groups.filter(name='Teacher').exists()

# --- 2. LOGIN VIEW ---
def login_view(request):
    if request.user.is_authenticated:
        if is_admin(request.user): return redirect('admin_dashboard')
        if is_teacher(request.user): return redirect('teacher_dashboard')
        return redirect('student_dashboard')

    form = SchoolLoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                print(f"DEBUG: User {username} logged in. Superuser: {user.is_superuser}")
                
                if user.is_superuser:
                    return redirect('admin_dashboard')
                elif user.groups.filter(name='Teacher').exists():
                    return redirect('teacher_dashboard')
                else:
                    return redirect('student_dashboard')
            else:
                messages.error(request, 'Invalid username or password')
    return render(request, 'account/login.html', {'form': form})

# --- 3. PROTECTED DASHBOARD VIEWS ---
# Pansamantala nating alisin ang @user_passes_test sa student para makita kung makakapasok ka

from django.contrib import messages

@login_required(login_url='login')
def admin_dashboard_view(request):
    if not is_admin(request.user):
        messages.error(request, "Access Denied: You do not have Admin privileges.")
        return redirect('login')
    return render(request, 'account/admin_dashboard.html')

@login_required(login_url='login')
def teacher_dashboard_view(request):
    if not is_teacher(request.user):
        messages.error(request, "Access Denied: This area is for Instructors only.")
        return redirect('login')
    return render(request, 'account/teacher_dashboard.html')

@login_required(login_url='login')
def student_dashboard_view(request):
    # Dito, dahil student ang default, check lang natin kung authenticated
    return render(request, 'account/student_dashboard.html')

# Dapat 'logout_user' ang pangalan para tumugma sa urls.py mo
def logout_user(request):
    logout(request)
    return redirect('login')