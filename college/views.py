from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Student, Teacher, Course, Department, Attendance, Grade, FeeRecord


# ─── STUDENTS ───────────────────────────────────────────────────────────────

@login_required
def student_list(request):
    q = request.GET.get('q', '')
    students = Student.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q) |
        Q(roll_number__icontains=q) | Q(email__icontains=q)
    ) if q else Student.objects.all()
    return render(request, 'college/student_list.html', {'students': students, 'query': q})


@login_required
def student_create(request):
    if request.method == 'POST':
        s = Student(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            gender=request.POST['gender'],
            date_of_birth=request.POST['date_of_birth'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            address=request.POST['address'],
            department_id=request.POST['department'],
            semester=request.POST.get('semester', 1),
            guardian_name=request.POST.get('guardian_name', ''),
            guardian_phone=request.POST.get('guardian_phone', ''),
        )
        s.save()
        messages.success(request, f'Student {s.roll_number} enrolled successfully.')
        return redirect('student_list')
    return render(request, 'college/student_form.html', {
        'title': 'Enroll Student',
        'departments': Department.objects.all(),
    })


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'college/student_detail.html', {
        'student': student,
        'grades': student.grades.select_related('course').all(),
        'fees': student.fees.all()[:10],
        'attendances': student.attendances.select_related('course').all()[:20],
    })


@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.first_name = request.POST['first_name']
        student.last_name = request.POST['last_name']
        student.gender = request.POST['gender']
        student.date_of_birth = request.POST['date_of_birth']
        student.email = request.POST['email']
        student.phone = request.POST['phone']
        student.address = request.POST['address']
        student.department_id = request.POST['department']
        student.semester = request.POST.get('semester', student.semester)
        student.status = request.POST.get('status', student.status)
        student.guardian_name = request.POST.get('guardian_name', '')
        student.guardian_phone = request.POST.get('guardian_phone', '')
        student.save()
        messages.success(request, 'Student updated successfully.')
        return redirect('student_detail', pk=pk)
    return render(request, 'college/student_form.html', {
        'title': 'Edit Student', 'student': student,
        'departments': Department.objects.all(),
    })


# ─── TEACHERS ───────────────────────────────────────────────────────────────

@login_required
def teacher_list(request):
    q = request.GET.get('q', '')
    teachers = Teacher.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q) |
        Q(employee_id__icontains=q)
    ) if q else Teacher.objects.all()
    return render(request, 'college/teacher_list.html', {'teachers': teachers, 'query': q})


@login_required
def teacher_create(request):
    if request.method == 'POST':
        t = Teacher(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            designation=request.POST['designation'],
            department_id=request.POST['department'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            qualification=request.POST['qualification'],
            joining_date=request.POST['joining_date'],
        )
        t.save()
        messages.success(request, f'{t.employee_id} added successfully.')
        return redirect('teacher_list')
    return render(request, 'college/teacher_form.html', {
        'title': 'Add Teacher',
        'departments': Department.objects.all(),
        'designations': Teacher.DESIGNATION_CHOICES,
    })


# ─── COURSES ────────────────────────────────────────────────────────────────

@login_required
def course_list(request):
    courses = Course.objects.select_related('department', 'teacher').all()
    return render(request, 'college/course_list.html', {'courses': courses})


@login_required
def course_create(request):
    if request.method == 'POST':
        c = Course(
            code=request.POST['code'],
            name=request.POST['name'],
            department_id=request.POST['department'],
            teacher_id=request.POST.get('teacher') or None,
            credit_hours=request.POST.get('credit_hours', 3),
            semester=request.POST.get('semester', 1),
            description=request.POST.get('description', ''),
        )
        c.save()
        messages.success(request, f'Course {c.code} created.')
        return redirect('course_list')
    return render(request, 'college/course_form.html', {
        'title': 'Add Course',
        'departments': Department.objects.all(),
        'teachers': Teacher.objects.filter(is_active=True),
    })


# ─── ATTENDANCE ─────────────────────────────────────────────────────────────

@login_required
def attendance_list(request):
    attendances = Attendance.objects.select_related('student', 'course').all()[:100]
    return render(request, 'college/attendance_list.html', {'attendances': attendances})


@login_required
def attendance_mark(request):
    if request.method == 'POST':
        student_id = request.POST['student']
        course_id = request.POST['course']
        date = request.POST['date']
        status = request.POST['status']
        obj, created = Attendance.objects.update_or_create(
            student_id=student_id, course_id=course_id, date=date,
            defaults={'status': status, 'remarks': request.POST.get('remarks', '')}
        )
        messages.success(request, 'Attendance marked successfully.')
        return redirect('attendance_list')
    return render(request, 'college/attendance_form.html', {
        'title': 'Mark Attendance',
        'students': Student.objects.filter(status='active'),
        'courses': Course.objects.filter(is_active=True),
    })


# ─── GRADES ─────────────────────────────────────────────────────────────────

@login_required
def grade_list(request):
    grades = Grade.objects.select_related('student', 'course').all()
    return render(request, 'college/grade_list.html', {'grades': grades})


@login_required
def grade_create(request):
    if request.method == 'POST':
        mid = float(request.POST.get('mid_marks', 0))
        final = float(request.POST.get('final_marks', 0))
        assign = float(request.POST.get('assignment_marks', 0))
        total = mid + final + assign
        grade_letter = (
            'A+' if total >= 90 else 'A' if total >= 85 else 'A-' if total >= 80 else
            'B+' if total >= 75 else 'B' if total >= 70 else 'B-' if total >= 65 else
            'C+' if total >= 60 else 'C' if total >= 50 else 'F'
        )
        obj, _ = Grade.objects.update_or_create(
            student_id=request.POST['student'],
            course_id=request.POST['course'],
            defaults={
                'mid_marks': mid, 'final_marks': final,
                'assignment_marks': assign, 'total_marks': total,
                'grade': grade_letter,
            }
        )
        messages.success(request, f'Grade saved: {grade_letter}')
        return redirect('grade_list')
    return render(request, 'college/grade_form.html', {
        'title': 'Enter Grade',
        'students': Student.objects.filter(status='active'),
        'courses': Course.objects.filter(is_active=True),
    })


# ─── FEES ───────────────────────────────────────────────────────────────────

@login_required
def fee_list(request):
    fees = FeeRecord.objects.select_related('student').all()
    return render(request, 'college/fee_list.html', {'fees': fees})


@login_required
def fee_create(request):
    if request.method == 'POST':
        paid = float(request.POST.get('paid_amount', 0))
        total = float(request.POST['amount'])
        status = 'paid' if paid >= total else ('partial' if paid > 0 else 'pending')
        fee = FeeRecord(
            student_id=request.POST['student'],
            fee_type=request.POST['fee_type'],
            amount=total,
            paid_amount=paid,
            due_date=request.POST['due_date'],
            payment_date=request.POST.get('payment_date') or None,
            semester=request.POST.get('semester', 1),
            status=status,
            remarks=request.POST.get('remarks', ''),
        )
        fee.save()
        messages.success(request, f'Fee record {fee.receipt_number} created.')
        return redirect('fee_list')
    return render(request, 'college/fee_form.html', {
        'title': 'Add Fee Record',
        'students': Student.objects.filter(status='active'),
        'fee_types': FeeRecord.FEE_TYPE_CHOICES,
    })
