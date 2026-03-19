from django.contrib import admin
from .models import Patient, Doctor, Appointment, Medicine, Bill, BillItem

admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(Medicine)
admin.site.register(Bill)
admin.site.register(BillItem)
