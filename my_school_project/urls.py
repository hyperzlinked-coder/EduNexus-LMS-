from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # This sends all basic URLs straight to your account app
    path('', include('account.urls')), 
]