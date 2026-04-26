from django.contrib import admin
from .models import EmployeeProfile, LeaveType, LeaveApplication

admin.site.register(EmployeeProfile)
admin.site.register(LeaveType)
admin.site.register(LeaveApplication)
