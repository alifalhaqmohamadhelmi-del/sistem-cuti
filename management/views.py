from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import LeaveApplication, LeaveType, EmployeeProfile
from datetime import date, timedelta, datetime
from .forms import RegisterForm

# ==========================
# FUNGSI KIRA HARI BEKERJA
# ==========================

def kira_hari_bekerja(start_date, end_date):
    jumlah = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            jumlah += 1
        current += timedelta(days=1)
    return jumlah

# ==========================
# 1. PENGURUSAN AKAUN & PROFIL
# ==========================

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Akaun {user.username} berjaya didaftarkan!")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile_view(request):
    profile, created = EmployeeProfile.objects.get_or_create(
        user=request.user,
        defaults={'total_leave_quota': 48}
    )

    if request.method == 'POST':
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            messages.success(request, 'Gambar profil berjaya dikemaskini!')
            return redirect('profile')

    return render(request, 'profile.html', {'profile': profile})

@login_required
def dashboard(request):
    from datetime import date
    import json

    profile, created = EmployeeProfile.objects.get_or_create(
        user=request.user,
        defaults={'total_leave_quota': 48}  # ← tukar 24 kepada 48
    )

    # Kalau profile dah wujud tapi quota masih 24, update kepada 48
    if profile.total_leave_quota == 24:
        profile.total_leave_quota = 48
        profile.save()

    tahun_ini = date.today().year

    pending_count = LeaveApplication.objects.filter(
        employee=request.user,
        status='Pending'
    ).count()

    # Semua cuti approved tahun ini
    approved_leaves = LeaveApplication.objects.filter(
        employee=request.user,
        status='Approved',
        start_date__year=tahun_ini
    )
    approved_count = approved_leaves.count()

    # Jumlah hari cuti yang dah diluluskan
    jumlah_hari_approved = sum(leave.jumlah_hari for leave in approved_leaves)

    # Baki cuti = quota - jumlah hari approved
    baki_cuti = profile.total_leave_quota - jumlah_hari_approved

    # Cuti ditolak
    rejected_count = LeaveApplication.objects.filter(
        employee=request.user,
        status='Rejected'
    ).count()

    # Cuti sakit MC
    mc_leaves = LeaveApplication.objects.filter(
        employee=request.user,
        status='Approved',
        leave_type__name__icontains='sakit'
    )
    mc_hari = sum(leave.jumlah_hari for leave in mc_leaves)

    # Data kalendar
    all_approved = LeaveApplication.objects.filter(
        employee=request.user,
        status='Approved'
    )
    all_approved_dates = []
    for leave in all_approved:
        all_approved_dates.append({
            'title': leave.leave_type.name,
            'start': str(leave.start_date),
            'end': str(leave.end_date),
        })

    context = {
        'baki_cuti': baki_cuti,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'mc_hari': mc_hari,
        'approved_dates': json.dumps(all_approved_dates),
        'quota': profile.total_leave_quota,
    }
    return render(request, 'dashboard.html', context)

@login_required
def update_profile(request):
    return render(request, 'update_profile.html')

# ==========================
# 2. FUNGSI UNTUK STAFF/EMPLOYEE
# ==========================

@login_required
def apply_leave(request):
    leave_types = LeaveType.objects.all()

    if request.method == 'POST':
        leave_type_id = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        mc_file = request.FILES.get('medical_certificate')

        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        jumlah_hari = kira_hari_bekerja(start, end)

        leave_type = get_object_or_404(LeaveType, id=leave_type_id)

        LeaveApplication.objects.create(
            employee=request.user,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            jumlah_hari=jumlah_hari,
            medical_certificate=mc_file,
            status='Pending'
        )
        messages.success(request, f"Permohonan cuti berjaya dihantar! Jumlah hari bekerja: {jumlah_hari} hari")
        return redirect('view_status')

    return render(request, 'apply_leave.html', {'leave_types': leave_types})

@login_required
def view_status(request):
    my_leaves = LeaveApplication.objects.filter(employee=request.user).order_by('-start_date')
    return render(request, 'view_status.html', {'my_leaves': my_leaves})

# ==========================
# 3. FUNGSI UNTUK HR / ADMIN (APPROVE/REJECT)
# ==========================

def is_hr(user):
    return user.is_staff

@login_required
@user_passes_test(is_hr, login_url='login')
def pending_applications(request):
    applications = LeaveApplication.objects.filter(status='Pending').order_by('start_date')
    return render(request, 'pending_applications.html', {'applications': applications})

@staff_member_required
def approve_leave(request, application_id):
    application = get_object_or_404(LeaveApplication, id=application_id)
    application.status = 'Approved'
    application.hr_comment = request.POST.get('hr_comment', 'Permohonan diluluskan.')
    application.save()
    messages.success(request, f"Permohonan {application.employee.username} telah diluluskan!")
    return redirect('pending_applications')

@staff_member_required
def reject_leave(request, application_id):
    application = get_object_or_404(LeaveApplication, id=application_id)
    application.status = 'Rejected'
    application.hr_comment = request.POST.get('hr_comment', '')
    application.save()
    messages.warning(request, f"Permohonan {application.employee.username} telah ditolak.")
    return redirect('pending_applications')

# ==========================
# 4. LOGIN / LOGOUT / REGISTER
# ==========================

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            error = 'Username atau password salah.'
    return render(request, 'login.html', {'error': error})

def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# Helper semak supervisor
def is_supervisor(user):
    return user.groups.filter(name='Supervisor').exists()

@login_required
@user_passes_test(is_supervisor, login_url='login')
def supervisor_applications(request):
    # Supervisor tengok semua permohonan yang masih Pending
    applications = LeaveApplication.objects.filter(
        status='Pending'
    ).order_by('start_date')
    return render(request, 'supervisor_applications.html', {'applications': applications})

@login_required
@user_passes_test(is_supervisor, login_url='login')
def supervisor_review(request, application_id):
    application = get_object_or_404(LeaveApplication, id=application_id)
    if request.method == 'POST':
        supervisor_status = request.POST.get('supervisor_status')
        supervisor_comment = request.POST.get('supervisor_comment', '')
        application.supervisor_status = supervisor_status
        application.supervisor_comment = supervisor_comment
        application.save()
        messages.success(request, f"Ulasan untuk permohonan {application.employee.username} berjaya dihantar!")
        return redirect('supervisor_applications')
    return render(request, 'supervisor_applications.html', {'applications': LeaveApplication.objects.filter(status='Pending')})