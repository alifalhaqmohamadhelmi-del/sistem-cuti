from django.urls import path
from . import views

urlpatterns = [
    path('apply/', views.apply_leave, name='apply_leave'),
    path('pending/', views.pending_applications, name='pending_applications'),
    path('approve/<int:application_id>/', views.approve_leave, name='approve_leave'),
    path('reject/<int:application_id>/', views.reject_leave, name='reject_leave'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('status/', views.view_status, name='view_status'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),  # kalau ada fungsi login dalam sini
    path('profile/', views.profile_view, name='profile'),
    path('supervisor/', views.supervisor_applications, name='supervisor_applications'),
    path('supervisor/review/<int:application_id>/', views.supervisor_review, name='supervisor_review'),
    path('profile/update/', views.update_profile, name='update_profile')
    
]