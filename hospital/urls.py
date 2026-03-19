from django.urls import path
from . import views

urlpatterns = [
    # Patients
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/new/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_edit, name='patient_edit'),

    # Doctors
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/new/', views.doctor_create, name='doctor_create'),
    path('doctors/<int:pk>/edit/', views.doctor_edit, name='doctor_edit'),

    # Appointments
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/new/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/status/', views.appointment_update_status, name='appointment_status'),

    # Pharmacy
    path('pharmacy/', views.medicine_list, name='medicine_list'),
    path('pharmacy/new/', views.medicine_create, name='medicine_create'),

    # Billing
    path('billing/', views.bill_list, name='bill_list'),
    path('billing/new/', views.bill_create, name='bill_create'),
    path('billing/<int:pk>/', views.bill_detail, name='bill_detail'),
]
