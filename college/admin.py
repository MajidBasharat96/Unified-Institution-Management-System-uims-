from django.contrib import admin
from .models import Student, Teacher, Course, Department, Attendance, Grade, FeeRecord

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Department)
admin.site.register(Attendance)
admin.site.register(Grade)
admin.site.register(FeeRecord)
