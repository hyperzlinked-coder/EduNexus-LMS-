from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# --- 1. STUDENT MODEL ---
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    
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
    birth_date = models.DateField('Birth Date')
    gender = models.CharField('Gender', max_length=10, choices=GENDER_CHOICES, default='M')
    current_academic_level = models.CharField('Current Academic Level', max_length=10, choices=ACADEMIC_LEVEL_CHOICES)
    enrollment_status = models.CharField('Enrollment Status', max_length=20, choices=ENROLLMENT_STATUS_CHOICES)
    email = models.EmailField(max_length=254, blank=True, null=True)
    photo = models.ImageField('Photo', upload_to='students/photos', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# --- 2. USER PROFILE ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    must_change_password = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

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
    teacher_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    subjects = models.ManyToManyField(Subject, related_name='teachers')
    photo = models.ImageField(upload_to='teachers/photos/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.teacher_id})"

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
        UserProfile.objects.create(user=instance)
    instance.profile.save()