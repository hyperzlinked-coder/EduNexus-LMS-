import os
import uuid
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. FUNCTION AT THE TOP (Fixed: instance vs instance.user logic)
def get_upload_path(instance, filename):
    # Check what kind of object 'instance' is directly
    if hasattr(instance, 'admin_profile') or isinstance(instance, AdminProfile):
        return f'admin_photos/{filename}'
    elif hasattr(instance, 'teacher_profile') or isinstance(instance, Teacher):
        return f'teacher_photos/{filename}'
    elif hasattr(instance, 'student_profile') or isinstance(instance, Student):
        return f'student_photos/{filename}'
    return f'misc_photos/{filename}'

# --- 1. STUDENT MODEL ---
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    
    # REMOVED DUPLICATE PHOTO FIELD. Using one field with the dynamic path.
    photo = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'))
    ACADEMIC_LEVEL_CHOICES = (
        ('G-7', 'Grade 7'), ('G-8', 'Grade 8'), ('G-9', 'Grade 9'),
        ('G-10', 'Grade 10'), ('G-11', 'Grade 11'), ('G-12', 'Grade 12'),
    )
    ENROLLMENT_STATUS_CHOICES = (
        ('active', 'Active'), ('dismissed', 'Dismissed'),
        ('graduated', 'Graduated'), ('transferred', 'Transferred'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField('First Name', max_length=50)
    last_name = models.CharField('Last Name', max_length=50)
    birth_date = models.DateField('Birth Date', null=True, blank=True) # Added null=True to fix migration hang
    gender = models.CharField('Gender', max_length=10, choices=GENDER_CHOICES, default='M')
    current_academic_level = models.CharField('Current Academic Level', max_length=10, choices=ACADEMIC_LEVEL_CHOICES)
    enrollment_status = models.CharField('Enrollment Status', max_length=20, choices=ENROLLMENT_STATUS_CHOICES)
    email = models.EmailField(max_length=254, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_first_login = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def get_age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return "N/A"
    
# --- 2. ADMIN PROFILE ---
class AdminProfile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    
    photo = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    
    must_change_password = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# --- 3. TEACHER & SCHEDULING MODELS ---
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.code

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    
    # DYNAMIC PHOTO FIELD
    photo = models.ImageField(upload_to=get_upload_path, blank=True, null=True)
    
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'))
    GRADE_LEVEL_CHOICES = [('7', 'Grade 7'), ('8', 'Grade 8'), ('9', 'Grade 9'), ('10', 'Grade 10'), ('11', 'Grade 11'), ('12', 'Grade 12')]
    
    # Use your Prefixed Choices for the Dependent Dropdown logic
    SUBJECT_CHOICES = [
    ('JHS-English', 'English (JHS)'), 
    ('JHS-Math', 'Mathematics (JHS)'),
    ('JHS-Science', 'Science (JHS)'), 
    ('JHS-Filipino', 'Filipino (JHS)'),
    ('JHS-ESP', 'Edukasyon sa Pagpapakatao'), 
    ('JHS-MAPEH', 'Music, Art, PE, Health'),
    
    ('SHS-OralComm', 'Oral Communication'), 
    ('SHS-GenMath', 'General Mathematics'),
    ('SHS-EarthLife', 'Earth & Life Science'), 
    ('SHS-ICT', 'ICT / Empowerment Tech'),
]

    DEPT_CHOICES = [
        ('JHS', 'Junior High Department'), 
        ('SHS', 'Senior High Department')
    ]

    # CLEANED UP DUPLICATES
    
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    gender = models.CharField('Gender', max_length=10, choices=GENDER_CHOICES, default='M')
    birth_date = models.DateField(null=True, blank=True)
    teacher_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.CharField(max_length=50, choices=DEPT_CHOICES, default='JHS')
    preferred_subject = models.CharField(max_length=100, choices=SUBJECT_CHOICES, default='JHS-Math')
    assigned_grade = models.CharField(max_length=2, choices=GRADE_LEVEL_CHOICES, blank=True, null=True)
    
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    subjects = models.ManyToManyField(Subject, related_name='teachers', blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

class TeacherAvailability(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField() # 0=Mon, 6=Sun
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('teacher', 'day_of_week', 'start_time')

# --- 4. SIGNALS ---
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            AdminProfile.objects.get_or_create(user=instance)
        elif instance.groups.filter(name='Teacher').exists():
            Teacher.objects.get_or_create(user=instance)
        else:
            Student.objects.get_or_create(user=instance)
            
