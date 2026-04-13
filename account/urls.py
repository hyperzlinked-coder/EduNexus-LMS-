from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    
    # Idagdag mo itong line na ito para sa logout:
    path('logout/', views.logout_user, name='logout'), 
    
    path('dashboard/student/', views.student_dashboard_view, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    
]
