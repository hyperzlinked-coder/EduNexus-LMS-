# account/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from .models import Profile

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                # I-exempt ang password change page para hindi mag-loop
                if profile.must_change_password and request.path != reverse('password_change'):
                    return redirect('password_change')
            except Profile.DoesNotExist:
                pass
        return self.get_response(request)