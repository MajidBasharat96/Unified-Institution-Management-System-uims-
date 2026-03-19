"""
UIMS Fee Reminder Script
- Finds students with fees due in the next 3 days
- Marks overdue fees automatically
- Sends email reminders to students
- Sends summary to admin
- Run daily at 8:00 AM via Task Scheduler
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


def send_email(config, to_email, subject, body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"UIMS Notifications <{config['EMAIL_USER']}>"
        msg['To'] = to_email
        msg.attach(MIMEText(body, 'html'))
        with smtplib.SMTP(config['EMAIL_HOST'], int(config['EMAIL_PORT'])) as server:
            server.starttls()
            server.login(config['EMAIL_USER'], config['EMAIL_PASS'])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"  Email to {to_email} failed: {e}")
        return False


def log(log_dir, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {message}"
    print(line)
    with open(os.path.join(log_dir, 'fee_reminders.log'), 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'config.env')
    config = load_config(config_path)
    log_dir = config.get('LOG_DIR', os.path.join(config['UIMS_PATH'], 'automation', 'logs'))
    os.makedirs(log_dir, exist_ok=True)

    setup_django(config['UIMS_PATH'])
    from college.models import FeeRecord

    today = date.today()
    reminder_window = today + timedelta(days=3)

    log(log_dir, "=" * 50)
    log(log_dir, f"Fee Reminder Run — {today}")

    # ── Mark overdue fees automatically ──────────────────
    overdue = FeeRecord.objects.filter(
        due_date__lt=today,
        status__in=['pending', 'partial']
    )
    overdue_count = overdue.count()
    overdue.update(status='overdue')
    if overdue_count:
        log(log_dir, f"Marked {overdue_count} fee record(s) as overdue.")

    # ── Find fees due in next 3 days ──────────────────────
    upcoming = FeeRecord.objects.filter(
        due_date__gte=today,
        due_date__lte=reminder_window,
        status__in=['pending', 'partial']
    ).select_related('student')

    sent = 0
    failed = 0

    for fee in upcoming:
        student = fee.student
        days_left = (fee.due_date - today).days
        due_label = "today" if days_left == 0 else f"in {days_left} day(s)"
        balance = fee.amount - fee.paid_amount

        subject = f"📢 Fee Payment Reminder — {fee.get_fee_type_display()} due {due_label}"
        body = f"""
        <div style="font-family:'Segoe UI',sans-serif;max-width:520px;margin:auto;border:1px solid #e4e4e0;border-radius:10px;overflow:hidden;">
          <div style="background:#1d4ed8;padding:20px 24px;">
            <h2 style="color:#fff;margin:0;font-size:18px;">⊕ UIMS — Fee Reminder</h2>
          </div>
          <div style="padding:24px;">
            <p>Dear <strong>{student.first_name} {student.last_name}</strong>,</p>
            <p>This is a reminder that your fee payment is due <strong>{due_label}</strong>.</p>
            <table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;">
              <tr style="background:#f5f5f3;"><td style="padding:8px 12px;color:#6b6b65;">Roll Number</td><td style="padding:8px 12px;"><strong>{student.roll_number}</strong></td></tr>
              <tr><td style="padding:8px 12px;color:#6b6b65;">Fee Type</td><td style="padding:8px 12px;">{fee.get_fee_type_display()}</td></tr>
              <tr style="background:#f5f5f3;"><td style="padding:8px 12px;color:#6b6b65;">Total Amount</td><td style="padding:8px 12px;">PKR {fee.amount}</td></tr>
              <tr><td style="padding:8px 12px;color:#6b6b65;">Paid</td><td style="padding:8px 12px;color:#15803d;">PKR {fee.paid_amount}</td></tr>
              <tr style="background:#fef2f2;"><td style="padding:8px 12px;color:#dc2626;font-weight:600;">Balance Due</td><td style="padding:8px 12px;color:#dc2626;font-weight:600;">PKR {balance}</td></tr>
              <tr><td style="padding:8px 12px;color:#6b6b65;">Due Date</td><td style="padding:8px 12px;"><strong>{fee.due_date.strftime('%d %B %Y')}</strong></td></tr>
            </table>
            <p style="color:#6b6b65;font-size:13px;">Please visit the college accounts office or log in to the UIMS portal to complete your payment.</p>
            <p style="color:#6b6b65;font-size:12px;margin-top:20px;border-top:1px solid #e4e4e0;padding-top:12px;">This is an automated message from UIMS. Please do not reply to this email.</p>
          </div>
        </div>
        """

        if student.email:
            ok = send_email(config, student.email, subject, body)
            if ok:
                sent += 1
                log(log_dir, f"  Reminder sent → {student.email} ({fee.get_fee_type_display()}, PKR {balance} due {due_label})")
            else:
                failed += 1
        else:
            log(log_dir, f"  Skipped {student.roll_number} — no email address")

    # ── Admin summary ──────────────────────────────────────
    overdue_total = FeeRecord.objects.filter(status='overdue')
    total_overdue_amount = sum(f.amount - f.paid_amount for f in overdue_total)

    admin_subject = f"📊 UIMS Fee Reminders — {today.strftime('%d %b %Y')}"
    admin_body = f"""
    <div style="font-family:'Segoe UI',sans-serif;max-width:520px;margin:auto;">
      <h2 style="color:#1d4ed8;">UIMS Daily Fee Reminder Report</h2>
      <p style="color:#6b6b65;">{today.strftime('%A, %d %B %Y')}</p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;margin:16px 0;">
        <tr style="background:#f5f5f3;"><td style="padding:10px 14px;color:#6b6b65;">Reminders Sent</td><td style="padding:10px 14px;"><strong style="color:#1d4ed8;">{sent}</strong></td></tr>
        <tr><td style="padding:10px 14px;color:#6b6b65;">Failed Deliveries</td><td style="padding:10px 14px;">{failed}</td></tr>
        <tr style="background:#f5f5f3;"><td style="padding:10px 14px;color:#6b6b65;">Newly Marked Overdue</td><td style="padding:10px 14px;"><strong style="color:#dc2626;">{overdue_count}</strong></td></tr>
        <tr><td style="padding:10px 14px;color:#6b6b65;">Total Overdue Records</td><td style="padding:10px 14px;">{overdue_total.count()}</td></tr>
        <tr style="background:#fef2f2;"><td style="padding:10px 14px;color:#dc2626;font-weight:600;">Total Overdue Amount</td><td style="padding:10px 14px;color:#dc2626;font-weight:600;">PKR {total_overdue_amount:,.0f}</td></tr>
      </table>
    </div>
    """
    send_email(config, config['ADMIN_EMAIL'], admin_subject, admin_body)
    log(log_dir, f"Done. Sent: {sent}, Failed: {failed}, Overdue marked: {overdue_count}")


if __name__ == '__main__':
    main()
