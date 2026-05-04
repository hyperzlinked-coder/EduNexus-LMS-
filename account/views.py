from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.models import Group
from django.views.decorators.cache import never_cache
from django.conf import settings
from .forms import SchoolLoginForm, StudentForm, TeacherForm
from .models import Student, Teacher, AdminProfile
from django.contrib.auth.models import User, Group
from django.utils.crypto import get_random_string
from .forms import UserRegistrationForm 
from django.core.exceptions import PermissionDenied
User = get_user_model()
from django.utils.crypto import get_random_string
from django.db import transaction

@never_cache
def login_view(request):
    MAX_ATTEMPTS = getattr(settings, 'MAX_ATTEMPTS', 5)

    # 1. Check kung naka-login na para hindi na bumalik sa login page
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('account:admin_dashboard')
        elif request.user.groups.filter(name='Teacher').exists():
            return redirect('account:teacher_dashboard')
        else:
            return redirect('account:student_dashboard')# Palitan ito ng tamang redirect base sa role

    # 2. Check lockout status
    if request.session.get('login_attempts', 0) >= MAX_ATTEMPTS:
        messages.error(request, "Account is locked due to too many failed attempts. Check your email to reset.")
        return render(request, 'account/login.html', {'form': SchoolLoginForm()})

    if request.method == 'GET':
        return render(request, 'account/login.html', {'form': SchoolLoginForm()})

    # 3. Processing POST
    form = SchoolLoginForm(request, data=request.POST)
    
    if form.is_valid():
        user = form.get_user()
        
        # Security: Dito na-aauthenticate ang user gamit ang backend
        if user is not None and user.is_active:
            login(request, user)
            request.session['login_attempts'] = 0  # Reset counter pag success
            
            # Role-based Redirection
            if user.is_superuser:
                return redirect('account:admin_dashboard')
            elif user.groups.filter(name='Teacher').exists():
                return redirect('account:teacher_dashboard')
            else:
                return redirect('account:student_dashboard')
        else:
            messages.error(request, "Account is disabled. Please contact your admin.")
    
    else:
        # Increment login attempts
        attempts = request.session.get('login_attempts', 0) + 1
        request.session['login_attempts'] = attempts
        remaining = MAX_ATTEMPTS - attempts

        if attempts >= MAX_ATTEMPTS:
            # Trigger Password Reset
            username = request.POST.get('username')
            target_user = User.objects.filter(username__iexact=username).first()
            if target_user and target_user.email:
                reset_form = PasswordResetForm({'email': target_user.email})
                if reset_form.is_valid():
                    reset_form.save(request=request, email_template_name='templates/registration/password_reset_email.html')
            messages.error(request, "Account locked. A reset link has been sent to your email.")
        else:
            messages.error(request, f"Invalid login. {remaining} attempts left.")

    return render(request, 'account/login.html', {'form': form})

# =========================
# LOGOUT
# =========================
@never_cache
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('account:login')


# =========================
# DASHBOARDS
# =========================
@login_required
@never_cache
def admin_dashboard_view(request):
    if not request.user.is_superuser:
        return redirect('account:teacher_dashboard')
    return render(request, 'account/admin_dashboard.html')


@login_required
@never_cache
def teacher_dashboard_view(request):
    # Only allow access if user is in 'Teacher' group
    if request.user.is_superuser or request.user.groups.filter(name='Teacher').exists():
        return render(request, 'account/teacher_dashboard.html')
    
    # If they aren't a teacher, send them to their own dashboard or home
    return redirect('account:student_dashboard')

@login_required 
@never_cache
def student_dashboard_view(request):
    return render(request, 'account/student_dashboard.html')


# =========================
# USER PROFILE
# ========================

@login_required
@never_cache
def admin_profile_view(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, "includes/admin_profile.html", {'profile': profile})

@login_required
def update_profile_info(request):
    if request.method == 'POST':

        # Change password
        if 'change_password' in request.POST:
            form = PasswordChangeForm(request.user, request.POST)

            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully!')
            else:
                for error in form.errors.values():
                    messages.error(request, error)

            return redirect('account:admin_profile')

        # Update basic info
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        # Update profile (if exists)
        profile = getattr(user, 'profile', None)
        if profile:
            profile.address = request.POST.get('address', profile.address)
            profile.phone_number = request.POST.get('phone', profile.phone_number)
            profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('account:admin_profile')

    return redirect('account:admin_profile')


# =========================
# STUDENT CRUD
# =========================
@login_required
@never_cache
def student_list(request):
    students = Student.objects.select_related('user').all()
    return render(request, 'includes/student_list.html', {'students': students})


@login_required
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # --- Username Generation ---
                    fname = form.cleaned_data['first_name'].lower().replace(" ", "")
                    lname = form.cleaned_data['last_name'].lower().replace(" ", "")
                    base_username = f"std_{fname}{lname}" # Nilagyan ko ng prefix para hindi mag-clash sa Admin
                    username = base_username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1
                    
                    password = get_random_string(12)
                    email = f"{username}@gmail.com"

                    # 1. Create the User
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name']
                    )

                    # 2. Assign to Group
                    group, _ = Group.objects.get_or_create(name='Student')
                    user.groups.add(group)

                    # 3. Handle the Student record
                    # Gagamit tayo ng commit=False para mas malinis
                    student = form.save(commit=False)
                    student.user = user
                    student.email = email
                    
                    if 'photo' in request.FILES:
                        student.photo = request.FILES['photo']
                    
                    student.save() 

                    messages.success(request, f"Student Created! User: {username} | Pass: {password}")
                    return redirect("account:student_list")

            except Exception as e:
                messages.error(request, f"System Error: {e}")
        else:
            # Dito papasok kung may kulang na field (Validation Error)
            messages.warning(request, "Please fill up all required fields.")
            # HINDI natin gagawing 'form = StudentForm()' para hindi mabura ang input
    else:
        form = StudentForm()
    
    # Napaka-importante: 'form' dito ay contains the POST data if invalid
    return render(request, 'includes/student_form.html', {'form': form, 'title': 'Save Student'})


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
            messages.success(request, f"Student {student} updated!")
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
        # I-check kung may linked user account
        if student.user:
            student.user.delete() # Ito ang mag-de-delete ng user sa auth_user table
        
        student.delete()
        messages.success(request, "Student and their account were deleted successfully!")

    return redirect("account:student_list")

def register_user_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST) # Dito dapat i-initialize ang form
        if form.is_valid():
            user = form.save() 
            
            # Kunin ang role mula sa dropdown sa HTML (dapat ay 'student' o 'teacher')
            role = request.POST.get('role') 
            
            if role == 'student':
                group = Group.objects.get(name='Student')
                user.groups.add(group)
            elif role == 'teacher':
                group = Group.objects.get(name='Teacher')
                user.groups.add(group)
                
            user.save()
            return redirect('dashboard') # Siguraduhing tama ang URL name
    else:
        form = UserRegistrationForm()
        
    return render(request, 'account/register.html', {'form': form})

# account/views.py

def register_teacher_view(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        teacher_form = TeacherForm(request.POST, request.FILES)
        
        if user_form.is_valid() and teacher_form.is_valid():
            # 1. Gawa ng User
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            # 2. Add sa 'Teacher' group
            group = Group.objects.get(name='Teacher')
            user.groups.add(group)
            
            # 3. Gawa ng Teacher Profile
            teacher = teacher_form.save(commit=False)
            teacher.user = user
            teacher.save()
            
            messages.success(request, "Teacher account created successfully!")
            return redirect('dashboard')


# account/views.py

@login_required
def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, 'includes/teacher_list.html', {'teachers': teachers})

@login_required
def teacher_create(request):
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save(commit=False)
            
            # Generate credentials
            fname = teacher.first_name.lower().replace(" ", "")
            lname = teacher.last_name.lower().replace(" ", "")
            username = f"tchr_{fname}{lname}"
            email = f"{username}@gmail.com"
            
            if User.objects.filter(username=username).exists():
                messages.error(request, f"The username '{username}' has already exist.")
                return render(request, 'includes/teacher_form.html', {'form': form, 'title': 'Add Teacher'})
            
            # 1. Create User
            password = get_random_string(12)
            user = User.objects.create_user(
                username=username, 
                password=password, 
                email=email,
                first_name=teacher.first_name, 
                last_name=teacher.last_name
            )

            # 2. ASSIGN TO TEACHER GROUP
            group, created = Group.objects.get_or_create(name='Teacher')
            user.groups.add(group)
            
            teacher.user = user
            teacher.email = email
            teacher.save()
            
            messages.success(request, f"Teacher Created! User: {username} | Pass: {password}")
            return redirect("account:teacher_list")
    else:
        form = TeacherForm()
    return render(request, 'includes/teacher_form.html', {'form': form, 'title': 'Add Teacher'})

@login_required
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher updated successfully!")
            return redirect('account:teacher_list')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'includes/teacher_form.html', {'form': form, 'title': 'Edit Teacher'})

@login_required
@never_cache
def teacher_profile(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, "includes/teacher_profile.html", {'teacher': teacher})

@login_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    
    if request.method == "POST":
        if teacher.user:
                teacher.user.delete()
        
        teacher.delete()
        messages.success(request, "Teacher and their account were deleted successfully!")
        
    return redirect('account:teacher_list')
   

@login_required
def admin_dashboard_view(request):
    # ... your existing counts ...
    recent_students = Student.objects.order_by('-id')[:5] # Fetches the last 5 added
    
    context = {
        'student_count': Student.objects.count(),
        'teacher_count': Teacher.objects.count(),
        'recent_students': recent_students,
    }
    return render(request, 'account/admin_dashboard.html', context)

#Security

