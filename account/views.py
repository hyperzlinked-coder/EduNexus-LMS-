from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import SchoolLoginForm

def login_view(request):
    if request.method == 'POST':
        form = SchoolLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # --- THE TRAFFIC COP LOGIC ---
            
            # 1. Is the user an admin?
            if user.is_superuser:
                return redirect('admin_dashboard')
                
            # 2. Is the user a teacher?
            elif user.groups.filter(name='Teacher').exists():
                return redirect('teacher_dashboard')
                
            # 3. Default fallback: Student
            else:
                return redirect('student_dashboard') 
                
    else:
        form = SchoolLoginForm()
        
    return render(request, 'account/login.html', {'form': form})

# --- THE 3 DASHBOARD VIEWS ---

def student_dashboard_view(request):
    return render(request, 'account/student_dashboard.html')

def teacher_dashboard_view(request):
    return render(request, 'account/teacher_dashboard.html')

def admin_dashboard_view(request):
    return render(request, 'account/admin_dashboard.html')

def logout_user(request):
    logout(request)
    return redirect('login')