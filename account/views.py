from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.conf import settings
from .forms import SchoolLoginForm, StudentForm
from .models import Student
from django.contrib.auth.models import User, Group
from django.utils.crypto import get_random_string

@never_cache
def login_view(request):
    MAX_ATTEMPTS = getattr(settings, 'MAX_ATTEMPTS', 5)

    if request.method == 'POST':
        # I-check muna ang lock status bago i-process ang form
        if request.session.get('login_attempts', 0) >= MAX_ATTEMPTS:
            messages.error(request, "Account locked. Please check your email for a reset link.")
            return render(request, 'account/login.html', {'form': SchoolLoginForm()})

        form = SchoolLoginForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            
            # CRITICAL CHECK: Active status
            if user.is_active:
                login(request, user)
                request.session['login_attempts'] = 0 # Reset attempts on success
                
                # Redirect logic
                if user.is_superuser:
                    return redirect('account:admin_dashboard')
                elif user.groups.filter(name='Teacher').exists():
                    return redirect('account:teacher_dashboard')
                else:
                    return redirect('account:student_dashboard')
            else:
                messages.error(request, "Your account is inactive. Please contact the administrator.")
        else:
            # Increment attempts on failure
            request.session['login_attempts'] = request.session.get('login_attempts', 0) + 1
            remaining = MAX_ATTEMPTS - request.session['login_attempts']
            
            if request.session['login_attempts'] >= MAX_ATTEMPTS:
                username = request.POST.get('username')
                target_user = User.objects.filter(username__iexact=username).first()
                if target_user and target_user.email:
                    # PasswordResetForm usage (siguraduhing tama ang data)
                    form_data = {'email': target_user.email}
                    reset_form = PasswordResetForm(form_data)
                    if reset_form.is_valid():
                        reset_form.save(request=request, use_https=request.is_secure())
                messages.error(request, "Max attempts reached. Reset link sent to your email.")
            else:
                messages.error(request, f"Invalid login. {remaining} attempts left.")
                
    else:
        form = SchoolLoginForm()
    
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
# =========================
@login_required
@never_cache
def user_profile_view(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, "includes/user_profile.html", {'profile': profile})


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

            return redirect('account:my_profile')

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
        return redirect('account:my_profile')

    return redirect('account:my_profile')


# =========================
# STUDENT CRUD
# =========================
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
            # 1. Kunin ang basic student info
            student = form.save(commit=False)
            
            # 2. I-generate ang username at email (Automatic)
            username = f"{student.first_name.lower()}{student.last_name.lower()}".replace(" ", "")
            email = f"{username}@gmail.com" 
            
            # 3. Check kung may existing user na para iwas IntegrityError
            if User.objects.filter(username=username).exists():
                messages.error(request, f"Ang username na '{username}' ay taken na. Mag-add ng middle initial kung kailangan.")
                return render(request, 'includes/form.html', {'form': form, 'title': 'Add Student'})
            
            # 4. Gumawa ng User account
            password = get_random_string(12)
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=student.first_name,
                last_name=student.last_name
            )
            
            # 5. I-link ang User sa Student at i-save
            student.user = user
            student.email = email # Siguraduhing may email field ka sa Student model
            student.save()
            
            messages.success(request, f"Success! Username: {username}, Password: {password}")
            return redirect("account:student_list")
            
    else:
        form = StudentForm()

    return render(request, 'includes/form.html', {'form': form, 'title': 'Add Student'})


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