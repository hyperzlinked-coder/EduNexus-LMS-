from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SchoolLoginForm

# --- 1. MGA SECURITY CHECK FUNCTIONS ---
def is_admin(user):
    return user.is_authenticated and user.is_superuser

def is_teacher(user):
    # Sinisiguro nito na papasok ang user kung nasa 'Teacher' group o may Staff status
    return user.is_authenticated and (user.groups.filter(name='Teacher').exists() or user.is_staff)

def is_student(user):
    # Student kung login siya pero hindi admin at hindi teacher group
    return user.is_authenticated and not user.is_superuser and not user.groups.filter(name='Teacher').exists()

# --- 2. LOGIN VIEW ---
def login_view(request):
   
    if request.method == 'POST':
        form = SchoolLoginForm(request, data=request.POST)
        if form.is_valid():
            username_input = form.cleaned_data.get('username')
            password_input = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username_input, password=password_input)
            
            if user is not None:
                # --- CASE SENSITIVE CHECK ---
                # Kinukumpara ang tinype (username_input) sa totoong nasa DB (user.username)
                if user.username != username_input:
                    messages.error(request, 'Invalid username or password (Case sensitive).')
                else:
                    login(request, user)
                    print(f"--- LOGIN SUCCESS: {user.username} ---")
                    
                    if is_admin(user):
                        return redirect('admin_dashboard')
                    elif is_teacher(user):
                        return redirect('teacher_dashboard')
                    else:
                        return redirect('student_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            # Lalabas lang ito kung may mali sa fields o blanko
            messages.error(request, 'Invalid form submission. Please try again.')
    else:
        # Bago pa lang binuksan ang page (GET), kaya walang error message at malinis ang form
        form = SchoolLoginForm()

    return render(request, 'account/login.html', {'form': form})

# --- 3. PROTECTED DASHBOARD VIEWS ---
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
    # Ang student view ay madalas walang special check maliban sa login_required
    return render(request, 'account/student_dashboard.html')

# --- 4. LOGOUT VIEW ---
def logout_user(request):
    logout(request)
    return redirect('login')