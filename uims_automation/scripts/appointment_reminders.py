"""
UIMS Appointment Reminder Script
- Finds all appointments scheduled for tomorrow
- Sends email reminders to patients
- Sends daily appointment summary to admin
- Run daily at 7:00 AM via Task Scheduler
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
        msg['From'] = f"UIMS Hospital <{config['EMAIL_USER']}>"
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
    with open(os.path.join(log_dir, 'appointment_reminders.log'), 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'config.env')
    config = load_config(config_path)
    log_dir = config.get('LOG_DIR', os.path.join(config['UIMS_PATH'], 'automation', 'logs'))
    os.makedirs(log_dir, exist_ok=True)

    setup_django(config['UIMS_PATH'])
    from hospital.models import Appointment

    today = date.today()
    tomorrow = today + timedelta(days=1)

    log(log_dir, "=" * 50)
    log(log_dir, f"Appointment Reminder Run — {today}")

    # Appointments scheduled for tomorrow
    appointments = Appointment.objects.filter(
        appointment_date=tomorrow,
        status='scheduled'
    ).select_related('patient', 'doctor')

    sent = 0
    failed = 0

    for appt in appointments:
        patient = appt.patient
        doctor = appt.doctor
        time_str = appt.appointment_time.strftime('%I:%M %p')

        if not patient.email:
            log(log_dir, f"  Skipped {patient.patient_id} — no email")
            continue

        subject = f"🏥 Appointment Reminder — Tomorrow at {time_str}"
        body = f"""
        <div style="font-family:'Segoe UI',sans-serif;max-width:520px;margin:auto;border:1px solid #e4e4e0;border-radius:10px;overflow:hidden;">
          <div style="background:#0f766e;padding:20px 24px;">
            <h2 style="color:#fff;margin:0;font-size:18px;">🏥 UIMS — Appointment Reminder</h2>
          </div>
          <div style="padding:24px;">
            <p>Dear <strong>{patient.first_name} {patient.last_name}</strong>,</p>
            <p>This is a reminder that you have a medical appointment <strong>tomorrow</strong>.</p>
            <table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;">
              <tr style="background:#f0fdfa;"><td style="padding:10px 14px;color:#6b6b65;">Patient ID</td><td style="padding:10px 14px;"><strong>{patient.patient_id}</strong></td></tr>
              <tr><td style="padding:10px 14px;color:#6b6b65;">Doctor</td><td style="padding:10px 14px;"><strong>Dr. {doctor.first_name} {doctor.last_name}</strong></td></tr>
              <tr style="background:#f0fdfa;"><td style="padding:10px 14px;color:#6b6b65;">Specialization</td><td style="padding:10px 14px;">{doctor.get_specialization_display()}</td></tr>
              <tr><td style="padding:10px 14px;color:#6b6b65;">Date</td><td style="padding:10px 14px;"><strong>{tomorrow.strftime('%A, %d %B %Y')}</strong></td></tr>
              <tr style="background:#f0fdfa;"><td style="padding:10px 14px;color:#0f766e;font-weight:600;">Time</td><td style="padding:10px 14px;color:#0f766e;font-weight:600;font-size:16px;">{time_str}</td></tr>
              {f'<tr><td style="padding:10px 14px;color:#6b6b65;">Reason</td><td style="padding:10px 14px;">{appt.reason}</td></tr>' if appt.reason else ''}
            </table>
            <div style="background:#f0fdfa;border:1px solid #99f6e4;border-radius:6px;padding:12px 14px;font-size:13px;color:#0f766e;">
              <strong>Please arrive 10 minutes early.</strong> If you need to cancel or reschedule, please contact the hospital.
            </div>
            <p style="color:#6b6b65;font-size:12px;margin-top:20px;border-top:1px solid #e4e4e0;padding-top:12px;">This is an automated message from UIMS Hospital Management. Please do not reply.</p>
          </div>
        </div>
        """

        ok = send_email(config, patient.email, subject, body)
        if ok:
            sent += 1
            log(log_dir, f"  Reminder sent → {patient.email} (Dr. {doctor.last_name}, {time_str})")
        else:
            failed += 1

    # Today's appointment count for admin
    today_appts = Appointment.objects.filter(
        appointment_date=today, status='scheduled'
    ).count()

    # Admin summary
    admin_subject = f"📅 UIMS Appointment Summary — {today.strftime('%d %b %Y')}"
    admin_body = f"""
    <div style="font-family:'Segoe UI',sans-serif;max-width:520px;margin:auto;">
      <h2 style="color:#0f766e;">UIMS Daily Appointment Report</h2>
      <p style="color:#6b6b65;">{today.strftime('%A, %d %B %Y')}</p>
      <table style="width:100%;border-collapse:collapse;font-size:14px;margin:16px 0;">
        <tr style="background:#f0fdfa;"><td style="padding:10px 14px;color:#6b6b65;">Today's Appointments</td><td style="padding:10px 14px;"><strong style="color:#0f766e;">{today_appts}</strong></td></tr>
        <tr><td style="padding:10px 14px;color:#6b6b65;">Tomorrow's Appointments</td><td style="padding:10px 14px;"><strong>{appointments.count()}</strong></td></tr>
        <tr style="background:#f0fdfa;"><td style="padding:10px 14px;color:#6b6b65;">Reminders Sent</td><td style="padding:10px 14px;"><strong style="color:#1d4ed8;">{sent}</strong></td></tr>
        <tr><td style="padding:10px 14px;color:#6b6b65;">Failed Deliveries</td><td style="padding:10px 14px;">{failed}</td></tr>
      </table>
      {'<p style="color:#6b6b65;">No appointments scheduled for tomorrow.</p>' if appointments.count() == 0 else ''}
    </div>
    """
    send_email(config, config['ADMIN_EMAIL'], admin_subject, admin_body)
    log(log_dir, f"Done. Sent: {sent}, Failed: {failed}, Tomorrow: {appointments.count()} appointments")


if __name__ == '__main__':
    main()
