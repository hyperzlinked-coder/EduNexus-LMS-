from django.shortcuts import redirect
from django.urls import reverse

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'student'):
            if request.user.student.is_first_login:
                # Allow them to access the profile page and logout only
                allowed_url = reverse('admin_profile')
                logout_url = reverse('logout')
                
                if request.path != allowed_url and request.path != logout_url:
                    return redirect('admin_profile')

        return self.get_response(request)