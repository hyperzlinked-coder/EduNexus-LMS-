from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# I-unregister ang default User para mapalitan natin
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Ipakita ang group sa listahan
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_groups')
    
    # Ito ang maglalagay ng "By groups" sa sidebar (tamang-tama sa request mo!)
    list_filter = ('groups', 'is_staff', 'is_superuser')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'