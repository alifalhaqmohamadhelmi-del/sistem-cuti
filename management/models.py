from django.db import models
from django.contrib.auth.models import User

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    total_leave_quota = models.IntegerField(default=48)

    def __str__(self):
        return self.user.username

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    total_leave_quota = models.IntegerField(default=48)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.username


class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    annual_quota = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class LeaveApplication(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_applications')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    jumlah_hari = models.IntegerField(default=0)
    medical_certificate = models.FileField(upload_to='mc_files/', null=True, blank=True)
    hr_comment = models.TextField(null=True, blank=True)
    supervisor_comment = models.TextField(null=True, blank=True)  # ← tambah ni
    supervisor_status = models.CharField(                          # ← tambah ni
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Setuju', 'Setuju'),
            ('Tidak Setuju', 'Tidak Setuju'),
        ],
        default='Pending'
    )
    status_choices = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type.name}"