from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SchoolLoginForm, StudentForm 
from .models import Student
from django.views.decorators.cache import never_cache

# --- LOGIN/LOGOUT ---
@never_cache
def login_view(request):
    if request.method == 'POST':
        form = SchoolLoginForm(request, data=request.POST)
        if form.is_valid():
            username_provided = form.cleaned_data.get('username')
            password_provided = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username_provided, password=password_provided)
            
            if user is not None:
                # CRITICAL: Check if the casing matches exactly
                if user.username == username_provided:
                    login(request, user)
                    
                    # Your existing redirect logic
                    if user.is_superuser:
                        return redirect('account:admin_dashboard')
                    elif user.groups.filter(name='Teacher').exists() or user.is_staff:
                        return redirect('account:teacher_dashboard')
                    else:
                        return redirect('account:student_dashboard')
                else:
                    # If casing is wrong (e.g., 'admin' vs 'Admin')
                    messages.error(request, "Invalid username or password (check your capitalization).")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = SchoolLoginForm()
    return render(request, 'account/login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('account:login')

# --- DASHBOARDS ---
@login_required
def admin_dashboard_view(request):
    return render(request, 'account/admin_dashboard.html')

@login_required
def teacher_dashboard_view(request):
    return render(request, 'account/teacher_dashboard.html')

@login_required
def student_dashboard_view(request):
    return render(request, 'account/student_dashboard.html')

# --- STUDENT CRUD ---

@login_required
def student_list(request):
    students = Student.objects.all()
    # CHANGE: Removed 'account/' prefix because 'includes' is directly in 'templates'
    return render(request, 'includes/list.html', {'students': students})

@login_required
def student_create(request):
    if request.method == "POST":
        # Pass request.FILES to handle the student photo upload
        form = StudentForm(request.POST, request.FILES) 
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student {student} added successfully!")
            return redirect("account:student_list")
    else:
        form = StudentForm()
    
    return render(request, 'includes/form.html', {
        'form': form, 
        'title': 'Add Student'
    })
    
@login_required
def student_profile(request, pk):
    student = get_object_or_404(Student, pk=pk)
    # CHANGE: Removed 'account/' prefix
    return render(request, "includes/profile.html", {'student': student})

@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"Student {student} updated successfully!")
            return redirect("account:student_list")
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'includes/form.html', {
        'form': form, 
        'title': 'Edit Student'
    })
    
    # account/views.py
@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully!")
        return redirect("account:student_list")
    
    # If someone tries to access via GET, redirect them back
    return redirect("account:student_list")

# account/views.py
def ajax_update_student_profile_picture(request):
    # Your logic here
    pass