from django.urls import path
from . import views, ajax_views


app_name = 'account'

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('dashboard/student/', views.student_dashboard_view, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # Student CRUD
    path('student_list/', views.student_list, name="student_list"),
    path('student_form/', views.student_create, name="student_create"), # Matches the function above
    path('student/<uuid:pk>/profile/', views.student_profile, name='student_profile'),
    path('student/<uuid:pk>/edit/', views.student_edit, name='student_edit'),
    path('student<uuid:pk>/delete/', views.student_delete, name='student_delete'),
    
    # Teacher CRUD
    path('teacher_list/', views.teacher_list, name='teacher_list'),
    path('teacher_form/', views.teacher_create, name='teacher_create'),
    path('teacher/edit/<uuid:pk>/', views.teacher_edit, name='teacher_edit'), # Use uuid:pk if using UUIDs
    path('teacher/delete/<uuid:pk>/', views.teacher_delete, name='teacher_delete'),
    path('teacher/<uuid:pk>/profile/', views.teacher_profile, name='teacher_profile'),
    
     # User Profile
    path('admin-profile/', views.admin_profile_view, name='admin_profile'),
    path('my-profile/update/', views.update_profile_info, name='update_profile_info'),
    
    # Ajax
    path("ajax/update-student-picture/", ajax_views.ajax_update_student_profile_picture, name="ajax_update_student_profile_picture"),
    path('ajax/update-admin-photo/', ajax_views.ajax_update_admin_profile_picture, name='ajax_update_admin_profile_picture'),
    path('ajax/update-teacher-photo/', ajax_views.ajax_update_teacher_profile_picture, name='ajax_update_teacher_profile_picture'),
]


