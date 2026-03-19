from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['name']


class Teacher(models.Model):
    DESIGNATION_CHOICES = [
        ('professor', 'Professor'),
        ('assoc_professor', 'Associate Professor'),
        ('asst_professor', 'Assistant Professor'),
        ('lecturer', 'Lecturer'),
        ('lab_instructor', 'Lab Instructor'),
    ]
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=30, choices=DESIGNATION_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='teachers')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    qualification = models.CharField(max_length=200)
    joining_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last = Teacher.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.employee_id = f"EMP-{num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"

    class Meta:
        ordering = ['first_name', 'last_name']


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='courses')
    credit_hours = models.PositiveIntegerField(default=3)
    semester = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']


class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
    ]

    roll_number = models.CharField(max_length=20, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='students')
    semester = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    enrollment_date = models.DateField(auto_now_add=True)
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.roll_number:
            last = Student.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.roll_number = f"STU-{num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.roll_number} - {self.first_name} {self.last_name}"

    class Meta:
        ordering = ['-created_at']


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    remarks = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.course} - {self.date} - {self.status}"

    class Meta:
        unique_together = ['student', 'course', 'date']
        ordering = ['-date']


class Grade(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+'), ('A', 'A'), ('A-', 'A-'),
        ('B+', 'B+'), ('B', 'B'), ('B-', 'B-'),
        ('C+', 'C+'), ('C', 'C'), ('F', 'Fail'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    mid_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    assignment_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.course} - {self.grade}"

    class Meta:
        unique_together = ['student', 'course']


class FeeRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('overdue', 'Overdue'),
        ('waived', 'Waived'),
    ]
    FEE_TYPE_CHOICES = [
        ('tuition', 'Tuition Fee'),
        ('exam', 'Exam Fee'),
        ('library', 'Library Fee'),
        ('lab', 'Lab Fee'),
        ('transport', 'Transport Fee'),
        ('hostel', 'Hostel Fee'),
        ('other', 'Other'),
    ]
    receipt_number = models.CharField(max_length=20, unique=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    semester = models.PositiveIntegerField(default=1)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            last = FeeRecord.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.receipt_number = f"REC-{num:04d}"
        super().save(*args, **kwargs)

    @property
    def balance(self):
        return self.amount - self.paid_amount

    def __str__(self):
        return f"{self.receipt_number} - {self.student} - {self.get_fee_type_display()}"

    class Meta:
        ordering = ['-created_at']
