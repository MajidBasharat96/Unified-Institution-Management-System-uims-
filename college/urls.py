from django.urls import path
from . import views

urlpatterns = [
    # Students
    path('students/', views.student_list, name='student_list'),
    path('students/new/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),

    # Teachers
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/new/', views.teacher_create, name='teacher_create'),

    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/new/', views.course_create, name='course_create'),

    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/mark/', views.attendance_mark, name='attendance_mark'),

    # Grades
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/new/', views.grade_create, name='grade_create'),

    # Fees
    path('fees/', views.fee_list, name='fee_list'),
    path('fees/new/', views.fee_create, name='fee_create'),
]
