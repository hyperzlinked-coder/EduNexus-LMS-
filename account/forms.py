from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User # Idinagdag para sa registration
from .models import Student, Teacher

class SchoolLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password'
    }))

# Idinagdag para sa User Registration (para magawa ang account + groups)
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'birth_date', 'gender', 
            'current_academic_level', 'enrollment_status', 'photo', 'email'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@gmail.com'}),
            'gender': forms.RadioSelect(), # Let the template handle the flex styling
            'current_academic_level': forms.Select(attrs={'class': 'form-control'}), # Changed from form-select
            'enrollment_status': forms.Select(attrs={'class': 'form-control'}),     # Changed from form-select
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not email.endswith('@gmail.com'):
            raise forms.ValidationError("Ang system ay tumatanggap lamang ng @gmail.com accounts.")
        return email

# forms.py
class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'first_name', 'last_name', 'email', 'preferred_subject',
            'department', 'phone_number', 'photo' , 'gender', 'birth_date',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'teacher@gmail.com'}),
            'gender': forms.RadioSelect(), # Let the template handle the flex styling
            
            'department': forms.Select(attrs={'class': 'form-select'}),
            'preferred_subject': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'id': 'phone',  # Critical: we use this ID for the JavaScript
                'placeholder': '912 345 6789'
            }),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not email.endswith('@gmail.com'):
            raise forms.ValidationError("Ang system ay tumatanggap lamang ng @gmail.com accounts.")
        return email