#!/usr/bin/env python
"""
UIMS Quick Setup Script
Run this after installing requirements to get the system ready.
Usage: python setup.py
"""
import os
import sys
import subprocess

def run(cmd):
    print(f"  → {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    ERROR: {result.stderr}")
    else:
        if result.stdout.strip():
            print(f"    {result.stdout.strip()}")
    return result.returncode == 0

def main():
    print("\n" + "="*55)
    print("  UIMS — Unified Institution Management System")
    print("  Setup Script")
    print("="*55 + "\n")

    print("[1/4] Running database migrations...")
    run("python manage.py makemigrations core hospital college")
    run("python manage.py migrate")

    print("\n[2/4] Creating superuser (admin / admin123)...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uims_project.settings')
    import django
    django.setup()

    from django.contrib.auth.models import User
    from core.models import UserProfile

    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser(
            username='admin',
            email='admin@uims.local',
            password='admin123',
            first_name='System',
            last_name='Admin'
        )
        UserProfile.objects.create(user=user, role='admin')
        print("  → Admin user created: admin / admin123")
    else:
        print("  → Admin user already exists.")

    print("\n[3/4] Creating sample departments...")
    from college.models import Department
    departments = [
        ('CS', 'Computer Science'),
        ('EE', 'Electrical Engineering'),
        ('BBA', 'Business Administration'),
        ('MED', 'Medical Technology'),
    ]
    for code, name in departments:
        Department.objects.get_or_create(code=code, defaults={'name': name})
        print(f"  → {code}: {name}")

    print("\n[4/4] Setup complete!\n")
    print("="*55)
    print("  Start the server with:")
    print("    python manage.py runserver 0.0.0.0:8000")
    print()
    print("  Then open in your browser:")
    print("    http://localhost:8000/")
    print()
    print("  Login credentials:")
    print("    Username: admin")
    print("    Password: admin123")
    print("="*55 + "\n")

if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
