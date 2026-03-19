# UIMS — Unified Institution Management System
### Django + PostgreSQL | Hospital & College Management

---

## What's Included

### 🏥 Hospital Modules
- **Patient Management** — Registration, records, medical history, blood group
- **Doctor & Staff** — Profiles, specialization, schedules, consultation fees
- **Appointments & OPD** — Scheduling, status tracking, doctor-patient linking
- **Pharmacy** — Medicine inventory, stock levels, expiry tracking, low-stock alerts
- **Billing** — Bill creation, payment tracking, balance management

### 🎓 College Modules
- **Student Enrollment** — Registration, roll numbers, department assignment
- **Faculty & Courses** — Teacher profiles, course management, timetabling
- **Attendance** — Per-student, per-course attendance with status tracking
- **Grades** — Marks entry, automatic grade calculation (A+ to F)
- **Fees & Finance** — Fee records, payment tracking, receipt generation

---

## Installation Guide

### Step 1 — Requirements
- Python 3.10 or higher
- pip (Python package manager)
- PostgreSQL (optional for production; SQLite used by default)

### Step 2 — Set Up Virtual Environment
```bash
# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run Setup Script
```bash
python setup.py
```
This will:
- Run all database migrations
- Create an admin user (admin / admin123)
- Add sample departments

### Step 5 — Start the Server
```bash
python manage.py runserver 0.0.0.0:8000
```

### Step 6 — Open in Browser
```
http://localhost:8000/
```

Login with:
- **Username:** admin
- **Password:** admin123

---

## Switching to PostgreSQL (Production)

1. Create a PostgreSQL database:
```sql
CREATE DATABASE uims_db;
CREATE USER uims_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE uims_db TO uims_user;
```

2. Edit `uims_project/settings.py` and update the DATABASES section:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'uims_db',
        'USER': 'uims_user',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

3. Run migrations again:
```bash
python manage.py migrate
```

---

## Deploying on a Server (Production)

### Using Gunicorn + Nginx

1. Install Gunicorn (already in requirements.txt):
```bash
gunicorn uims_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

2. Set `DEBUG = False` in settings.py and add your server IP/domain to `ALLOWED_HOSTS`:
```python
DEBUG = False
ALLOWED_HOSTS = ['your-server-ip', 'yourdomain.com']
```

3. Collect static files:
```bash
python manage.py collectstatic
```

4. Configure Nginx to proxy to Gunicorn (port 8000).

---

## Project Structure

```
uims/
├── manage.py                  # Django management
├── requirements.txt           # Python dependencies
├── setup.py                   # Quick setup script
├── uims.db                    # SQLite DB (auto-created)
│
├── uims_project/              # Project settings
│   ├── settings.py
│   └── urls.py
│
├── core/                      # Auth, dashboard, user roles
│   ├── models.py              # UserProfile
│   ├── views.py               # Login, dashboard
│   └── urls.py
│
├── hospital/                  # Hospital management app
│   ├── models.py              # Patient, Doctor, Appointment, Medicine, Bill
│   ├── views.py               # All hospital views
│   └── urls.py
│
├── college/                   # College management app
│   ├── models.py              # Student, Teacher, Course, Attendance, Grade, Fee
│   ├── views.py               # All college views
│   └── urls.py
│
└── templates/                 # HTML templates
    ├── base.html              # Shared sidebar layout
    ├── core/
    │   ├── login.html
    │   └── dashboard.html
    ├── hospital/
    │   ├── patient_list/form/detail
    │   ├── doctor_list/form
    │   ├── appointment_list/form
    │   ├── medicine_list/form
    │   └── bill_list/form/detail
    └── college/
        ├── student_list/form/detail
        ├── teacher_list/form
        ├── course_list/form
        ├── attendance_list/form
        ├── grade_list/form
        └── fee_list/form
```

---

## Default Login
| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | System Admin |

> ⚠️ Change the password immediately after first login in production.
