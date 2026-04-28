from django.db import models
from django.conf import settings
import uuid

# Create your models here.
class Student(models.Model):

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )

    ACADEMIC_LEVEL_CHOICES = (
        ('G-7', 'Grade 7'),
        ('G-8', 'Grade 8'),
        ('G-9', 'Grade 9'),
        ('G-10', 'Grade 10'),
        ('G-11', 'Grade 11'),
        ('G-12', 'Grade 12'),
    )

    ENROLLMENT_STATUS_CHOICES = (
        ('active', 'Active'),
        ('dismissed', 'Dismissed'),
        ('graduated', 'Graduated'),
        ('transferred', 'Transferred'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField('First Name', max_length=50)
    last_name = models.CharField('Last Name', max_length=50)
    birth_date = models.DateField('Birth Date')
    gender = models.CharField('Gender', max_length=10, choices=GENDER_CHOICES, default='M')
    current_academic_level = models.CharField('Current Academic Level', max_length=10, choices=ACADEMIC_LEVEL_CHOICES)
    enrollment_status = models.CharField('Enrollment Status', max_length=20, choices=ENROLLMENT_STATUS_CHOICES)
    photo = models.ImageField('Photo', upload_to='students/photos', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} "
    
    
    def get_age(self):
        from datetime import date
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return age
    
    # account/models.py


from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    # This links the profile to a User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Basic Info Fields
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# --- AUTOMATION: Create a profile whenever a new User is created ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()