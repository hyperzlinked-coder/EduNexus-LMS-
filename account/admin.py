from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import AdminProfile  # Import your model

# 1. Create the Inline class
class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    verbose_name_plural = 'Student Profile Information'
    fk_name = 'user'

# I-unregister ang default User
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 2. Add the inline here
    inlines = (AdminProfileInline, )
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_groups')
    list_filter = ('groups', 'is_staff', 'is_superuser')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'