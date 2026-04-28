from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import SchoolLoginForm, StudentForm 
from .models import Student
from django.views.decorators.cache import never_cache
from django.http import JsonResponse

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
                if user.username == username_provided:
                    login(request, user)
                    
                    if user.is_superuser:
                        return redirect('account:admin_dashboard')
                    elif user.groups.filter(name='Teacher').exists() or user.is_staff:
                        return redirect('account:teacher_dashboard')
                    else:
                        return redirect('account:student_dashboard')
                else:
                    messages.error(request, "Invalid username or password (check your capitalization).")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = SchoolLoginForm()
    return render(request, 'account/login.html', {'form': form})

@never_cache
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('account:login')

# --- DASHBOARDS ---

@login_required
@never_cache
def admin_dashboard_view(request):
    return render(request, 'account/admin_dashboard.html')

@login_required
@never_cache
def teacher_dashboard_view(request):
    return render(request, 'account/teacher_dashboard.html')

@login_required
@never_cache
def student_dashboard_view(request):
    return render(request, 'account/student_dashboard.html')

# --- USER SELF-PROFILE ---

@login_required
@never_cache
def user_profile_view(request):
    """
    This view finds the Student record associated with the logged-in user 
    and displays it on the profile page.
    """
    # Assuming your Student model has a 'user' field (OneToOneField)
    # If it doesn't, we just pass the user object itself.
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = request.user 

    return render(request, "includes/user_profile.html", {'student': student})

# --- STUDENT CRUD (For Admin/Teacher use) ---

@login_required
@never_cache
def student_list(request):
    students = Student.objects.all()
    return render(request, 'includes/list.html', {'students': students})

@login_required
def student_create(request):
    if request.method == "POST":
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
@never_cache
def student_profile(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "includes/student_profile.html", {'student': student})

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
    
@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully!")
        return redirect("account:student_list")
    
    return redirect("account:student_list")

@login_required
@require_POST
def ajax_update_student_profile_picture(request):
    try:
        student_id = request.POST.get('student_id')
        photo = request.FILES.get('photo')
        
        if not photo:
            return JsonResponse({'status': 'error', 'message': 'No image provided'}, status=400)

        # Update the specific student record
        student = get_object_or_404(Student, id=student_id)
        student.photo = photo
        student.save()
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Profile picture updated!',
            'url': student.photo.url
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)