from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Patient, Doctor, Appointment, Medicine, Bill, BillItem


# ─── PATIENTS ───────────────────────────────────────────────────────────────

@login_required
def patient_list(request):
    q = request.GET.get('q', '')
    patients = Patient.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q) |
        Q(patient_id__icontains=q) | Q(phone__icontains=q)
    ) if q else Patient.objects.all()
    return render(request, 'hospital/patient_list.html', {'patients': patients, 'query': q})


@login_required
def patient_create(request):
    if request.method == 'POST':
        p = Patient(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            gender=request.POST['gender'],
            date_of_birth=request.POST['date_of_birth'],
            blood_group=request.POST.get('blood_group', ''),
            phone=request.POST['phone'],
            email=request.POST.get('email', ''),
            address=request.POST['address'],
            emergency_contact=request.POST.get('emergency_contact', ''),
            emergency_phone=request.POST.get('emergency_phone', ''),
            medical_history=request.POST.get('medical_history', ''),
        )
        p.save()
        messages.success(request, f'Patient {p.patient_id} registered successfully.')
        return redirect('patient_list')
    return render(request, 'hospital/patient_form.html', {'title': 'Register Patient'})


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    appointments = patient.appointments.all()[:10]
    bills = patient.bills.all()[:10]
    return render(request, 'hospital/patient_detail.html', {
        'patient': patient, 'appointments': appointments, 'bills': bills
    })


@login_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.first_name = request.POST['first_name']
        patient.last_name = request.POST['last_name']
        patient.gender = request.POST['gender']
        patient.date_of_birth = request.POST['date_of_birth']
        patient.blood_group = request.POST.get('blood_group', '')
        patient.phone = request.POST['phone']
        patient.email = request.POST.get('email', '')
        patient.address = request.POST['address']
        patient.emergency_contact = request.POST.get('emergency_contact', '')
        patient.emergency_phone = request.POST.get('emergency_phone', '')
        patient.medical_history = request.POST.get('medical_history', '')
        patient.save()
        messages.success(request, 'Patient updated successfully.')
        return redirect('patient_detail', pk=pk)
    return render(request, 'hospital/patient_form.html', {'title': 'Edit Patient', 'patient': patient})


# ─── DOCTORS ────────────────────────────────────────────────────────────────

@login_required
def doctor_list(request):
    q = request.GET.get('q', '')
    doctors = Doctor.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q) |
        Q(specialization__icontains=q)
    ) if q else Doctor.objects.all()
    return render(request, 'hospital/doctor_list.html', {'doctors': doctors, 'query': q})


@login_required
def doctor_create(request):
    if request.method == 'POST':
        d = Doctor(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            specialization=request.POST['specialization'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            qualification=request.POST['qualification'],
            experience_years=request.POST.get('experience_years', 0),
            consultation_fee=request.POST.get('consultation_fee', 0),
        )
        d.save()
        messages.success(request, f'Dr. {d.last_name} added successfully.')
        return redirect('doctor_list')
    return render(request, 'hospital/doctor_form.html', {
        'title': 'Add Doctor',
        'specializations': Doctor.SPECIALIZATION_CHOICES
    })


@login_required
def doctor_edit(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.first_name = request.POST['first_name']
        doctor.last_name = request.POST['last_name']
        doctor.specialization = request.POST['specialization']
        doctor.email = request.POST['email']
        doctor.phone = request.POST['phone']
        doctor.qualification = request.POST['qualification']
        doctor.experience_years = request.POST.get('experience_years', 0)
        doctor.consultation_fee = request.POST.get('consultation_fee', 0)
        doctor.is_available = 'is_available' in request.POST
        doctor.save()
        messages.success(request, 'Doctor updated successfully.')
        return redirect('doctor_list')
    return render(request, 'hospital/doctor_form.html', {
        'title': 'Edit Doctor', 'doctor': doctor,
        'specializations': Doctor.SPECIALIZATION_CHOICES
    })


# ─── APPOINTMENTS ───────────────────────────────────────────────────────────

@login_required
def appointment_list(request):
    appointments = Appointment.objects.select_related('patient', 'doctor').all()
    return render(request, 'hospital/appointment_list.html', {'appointments': appointments})


@login_required
def appointment_create(request):
    if request.method == 'POST':
        a = Appointment(
            patient_id=request.POST['patient'],
            doctor_id=request.POST['doctor'],
            appointment_date=request.POST['appointment_date'],
            appointment_time=request.POST['appointment_time'],
            reason=request.POST.get('reason', ''),
            notes=request.POST.get('notes', ''),
        )
        a.save()
        messages.success(request, 'Appointment scheduled successfully.')
        return redirect('appointment_list')
    return render(request, 'hospital/appointment_form.html', {
        'title': 'New Appointment',
        'patients': Patient.objects.all(),
        'doctors': Doctor.objects.filter(is_available=True),
    })


@login_required
def appointment_update_status(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appt.status = request.POST['status']
        appt.notes = request.POST.get('notes', appt.notes)
        appt.save()
        messages.success(request, 'Appointment status updated.')
    return redirect('appointment_list')


# ─── PHARMACY ───────────────────────────────────────────────────────────────

@login_required
def medicine_list(request):
    q = request.GET.get('q', '')
    medicines = Medicine.objects.filter(
        Q(name__icontains=q) | Q(generic_name__icontains=q)
    ) if q else Medicine.objects.all()
    low_stock = medicines.filter(stock_quantity__lte=10)
    return render(request, 'hospital/medicine_list.html', {
        'medicines': medicines, 'query': q, 'low_stock_count': low_stock.count()
    })


@login_required
def medicine_create(request):
    if request.method == 'POST':
        m = Medicine(
            name=request.POST['name'],
            generic_name=request.POST.get('generic_name', ''),
            category=request.POST['category'],
            manufacturer=request.POST.get('manufacturer', ''),
            unit_price=request.POST['unit_price'],
            stock_quantity=request.POST['stock_quantity'],
            expiry_date=request.POST.get('expiry_date') or None,
            reorder_level=request.POST.get('reorder_level', 10),
        )
        m.save()
        messages.success(request, f'{m.name} added to pharmacy.')
        return redirect('medicine_list')
    return render(request, 'hospital/medicine_form.html', {
        'title': 'Add Medicine',
        'categories': Medicine.CATEGORY_CHOICES,
    })


# ─── BILLING ────────────────────────────────────────────────────────────────

@login_required
def bill_list(request):
    bills = Bill.objects.select_related('patient').all()
    return render(request, 'hospital/bill_list.html', {'bills': bills})


@login_required
def bill_create(request):
    if request.method == 'POST':
        bill = Bill(
            patient_id=request.POST['patient'],
            total_amount=request.POST['total_amount'],
            paid_amount=request.POST.get('paid_amount', 0),
            notes=request.POST.get('notes', ''),
        )
        paid = float(request.POST.get('paid_amount', 0))
        total = float(request.POST['total_amount'])
        bill.status = 'paid' if paid >= total else ('partial' if paid > 0 else 'pending')
        bill.save()
        messages.success(request, f'Bill {bill.bill_number} created.')
        return redirect('bill_list')
    return render(request, 'hospital/bill_form.html', {
        'title': 'Create Bill',
        'patients': Patient.objects.all(),
    })


@login_required
def bill_detail(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    return render(request, 'hospital/bill_detail.html', {'bill': bill})
