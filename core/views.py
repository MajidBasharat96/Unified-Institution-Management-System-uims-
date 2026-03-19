from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from hospital.models import Patient, Doctor, Appointment
from college.models import Student, Teacher, FeeRecord
from django.utils import timezone


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    # Hospital stats
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    today_appointments = Appointment.objects.filter(
        appointment_date=timezone.now().date()
    ).count()

    # College stats
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    pending_fees = FeeRecord.objects.filter(status='pending').count()

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'today_appointments': today_appointments,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'pending_fees': pending_fees,
        'recent_patients': Patient.objects.order_by('-created_at')[:5],
        'recent_students': Student.objects.order_by('-created_at')[:5],
        'recent_appointments': Appointment.objects.order_by('-created_at')[:5],
    }
    return render(request, 'core/dashboard.html', context)
