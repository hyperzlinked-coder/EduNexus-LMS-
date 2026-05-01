from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# my_school_project/urls.py
urlpatterns = [
    path('', include('account.urls', namespace='account')), 
    
    path('admin/', admin.site.urls),
    # Use 'account' as the namespace
    path('accounts/', include('django.contrib.auth.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 