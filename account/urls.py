from django.urls import path
from . import views, ajax_views


app_name = 'account'

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('dashboard/student/', views.student_dashboard_view, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('student/dashboard/', views.student_dashboard_view, name='student_dashboard'),
    
    # Student CRUD
    path("list/", views.student_list, name="student_list"),
    path("form/", views.student_create, name="student_create"), # Matches the function above
    path('<uuid:pk>/profile/', views.student_profile, name='student_profile'),
    path('<uuid:pk>/edit/', views.student_edit, name='student_edit'),
    path('<uuid:pk>/delete/', views.student_delete, name='student_delete'),
    
    # User Profile
    path('my-profile/', views.user_profile_view, name='my_profile'),
    path('my-profile/update/', views.update_profile_info, name='update_profile_info'),
    
    # Ajax
    path("ajax/update-profile-picture/", ajax_views.ajax_update_student_profile_picture, name="ajax_update_student_profile_picture"),
    path('ajax/update-user-photo/', ajax_views.ajax_update_user_profile_picture, name='ajax_update_user_profile_picture'),
]

