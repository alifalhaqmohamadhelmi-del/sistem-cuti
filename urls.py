from django.contrib import admin
from django.urls import path, include
from management.views import dashboard, view_status, apply_leave

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('management.urls')),
    path('', include('accounts.urls')),
    path('', dashboard, name='dashboard'),
    path('status/', view_status, name='view_status'),
    path('apply/', apply_leave, name='apply_leave'),
]
