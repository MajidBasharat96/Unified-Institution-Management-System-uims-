"""
UIMS Daily Admin Report Script
- Compiles a full daily summary of hospital + college activity
- Emails the admin every evening at 9:00 PM
- Run via Task Scheduler
"""
import os
import sys
import django
import smtplib
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def load_config(config_path):
    config = {}
    with open(config_path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, val = line.split('=', 1)
                config[key.strip()] = val.strip()
    return config


def setup_django(uims_path):
    sys.path.insert(0, uims_path)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uims_project.settings')
    django.setup()


def log(log_dir, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {message}"
    print(line)
    with open(os.path.join(log_dir, 'daily_report.log'), 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def stat_row(label, value, color='#1a1a18', bg='#ffffff'):
    return f'<tr style="background:{bg};"><td style="padding:9px 14px;color:#6b6b65;font-size:13px;">{label}</td><td style="padding:9px 14px;font-weight:600;color:{color};">{value}</td></tr>'


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'config.env')
    config = load_config(config_path)
    log_dir = config.get('LOG_DIR', os.path.join(config['UIMS_PATH'], 'automation', 'logs'))
    os.makedirs(log_dir, exist_ok=True)

    setup_django(config['UIMS_PATH'])

    from hospital.models import Patient, Doctor, Appointment, Medicine, Bill
    from college.models import Student, Teacher, FeeRecord, Attendance, Grade

    today = date.today()
    yesterday = today - timedelta(days=1)

    log(log_dir, f"Generating daily report for {today}")

    # ── Hospital stats ────────────────────────────────────
    new_patients_today = Patient.objects.filter(created_at__date=today).count()
    appts_today = Appointment.objects.filter(appointment_date=today)
    appts_completed = appts_today.filter(status='completed').count()
    appts_scheduled = appts_today.filter(status='scheduled').count()
    appts_cancelled = appts_today.filter(status='cancelled').count()
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()

    bills_today = Bill.objects.filter(bill_date=today)
    revenue_today = sum(b.paid_amount for b in bills_today)
    pending_bills = Bill.objects.filter(status='pending').count()

    low_stock = Medicine.objects.filter(stock_quantity__lte=10)

    # ── College stats ─────────────────────────────────────
    new_students_today = Student.objects.filter(created_at__date=today).count()
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    active_students = Student.objects.filter(status='active').count()

    attendance_today = Attendance.objects.filter(date=today)
    present_today = attendance_today.filter(status='present').count()
    absent_today = attendance_today.filter(status='absent').count()

    fees_collected_today = sum(
        f.paid_amount for f in FeeRecord.objects.filter(payment_date=today)
    )
    pending_fees = FeeRecord.objects.filter(status='pending').count()
    overdue_fees = FeeRecord.objects.filter(status='overdue').count()
    overdue_amount = sum(
        f.amount - f.paid_amount for f in FeeRecord.objects.filter(status='overdue')
    )

    # ── Build email ───────────────────────────────────────
    date_label = today.strftime('%A, %d %B %Y')

    hospital_rows = (
        stat_row("Total Patients", total_patients, bg='#f5f5f3') +
        stat_row("New Patients Today", new_patients_today, '#1d4ed8') +
        stat_row("Today's Appointments", appts_today.count(), bg='#f5f5f3') +
        stat_row("  — Completed", appts_completed, '#15803d') +
        stat_row("  — Scheduled", appts_scheduled, bg='#f5f5f3') +
        stat_row("  — Cancelled", appts_cancelled, '#dc2626') +
        stat_row("Revenue Today", f"PKR {revenue_today:,.0f}", '#15803d', '#f0fdf4') +
        stat_row("Pending Bills", pending_bills, '#b45309', '#fffbeb') +
        stat_row("Low Stock Medicines", low_stock.count(), '#dc2626' if low_stock.count() > 0 else '#15803d', '#fef2f2' if low_stock.count() > 0 else '#f0fdf4') +
        stat_row("Total Doctors", total_doctors, bg='#f5f5f3')
    )

    college_rows = (
        stat_row("Total Students", total_students, bg='#f5f5f3') +
        stat_row("Active Students", active_students, '#0f766e') +
        stat_row("New Enrollments Today", new_students_today, '#1d4ed8', '#eff6ff') +
        stat_row("Total Faculty", total_teachers, bg='#f5f5f3') +
        stat_row("Present Today", present_today, '#15803d', '#f0fdf4') +
        stat_row("Absent Today", absent_today, '#dc2626', '#fef2f2') +
        stat_row("Fees Collected Today", f"PKR {fees_collected_today:,.0f}", '#15803d', '#f0fdf4') +
        stat_row("Pending Fees", pending_fees, '#b45309', '#fffbeb') +
        stat_row("Overdue Fees", overdue_fees, '#dc2626', '#fef2f2') +
        stat_row("Total Overdue Amount", f"PKR {overdue_amount:,.0f}", '#dc2626')
    )

    low_stock_html = ''
    if low_stock.exists():
        rows = ''.join(
            f'<tr><td style="padding:6px 12px;">{m.name}</td><td style="padding:6px 12px;color:#dc2626;font-weight:600;">{m.stock_quantity} left</td></tr>'
            for m in low_stock[:10]
        )
        low_stock_html = f"""
        <h3 style="color:#dc2626;margin:24px 0 8px;">⚠ Low Stock Medicines</h3>
        <table style="width:100%;border-collapse:collapse;font-size:13px;border:1px solid #fecaca;border-radius:6px;overflow:hidden;">
          <thead><tr style="background:#fef2f2;"><th style="padding:8px 12px;text-align:left;color:#dc2626;">Medicine</th><th style="padding:8px 12px;text-align:left;color:#dc2626;">Stock</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
        """

    body = f"""
    <div style="font-family:'Segoe UI',sans-serif;max-width:600px;margin:auto;color:#1a1a18;">
      <div style="background:linear-gradient(135deg,#1d4ed8,#0f766e);padding:24px;border-radius:10px 10px 0 0;">
        <h1 style="color:#fff;margin:0;font-size:20px;">⊕ UIMS — Daily Report</h1>
        <p style="color:rgba(255,255,255,0.8);margin:4px 0 0;font-size:14px;">{date_label}</p>
      </div>
      <div style="border:1px solid #e4e4e0;border-top:none;border-radius:0 0 10px 10px;padding:24px;">

        <h2 style="color:#1d4ed8;font-size:16px;margin:0 0 10px;">🏥 Hospital Summary</h2>
        <table style="width:100%;border-collapse:collapse;font-size:14px;margin-bottom:24px;">
          {hospital_rows}
        </table>

        <h2 style="color:#0f766e;font-size:16px;margin:0 0 10px;">🎓 College Summary</h2>
        <table style="width:100%;border-collapse:collapse;font-size:14px;">
          {college_rows}
        </table>

        {low_stock_html}

        <p style="color:#9e9e98;font-size:12px;margin-top:24px;border-top:1px solid #e4e4e0;padding-top:12px;">
          Generated automatically by UIMS at {datetime.now().strftime('%H:%M')} on {date_label}.
        </p>
      </div>
    </div>
    """

    subject = f"📊 UIMS Daily Report — {today.strftime('%d %b %Y')}"

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"UIMS Reports <{config['EMAIL_USER']}>"
        msg['To'] = config['ADMIN_EMAIL']
        msg.attach(MIMEText(body, 'html'))
        with smtplib.SMTP(config['EMAIL_HOST'], int(config['EMAIL_PORT'])) as server:
            server.starttls()
            server.login(config['EMAIL_USER'], config['EMAIL_PASS'])
            server.send_message(msg)
        log(log_dir, f"Daily report emailed to {config['ADMIN_EMAIL']}")
    except Exception as e:
        log(log_dir, f"Failed to send daily report: {e}")


if __name__ == '__main__':
    main()
