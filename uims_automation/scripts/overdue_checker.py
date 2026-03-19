"""
UIMS Overdue Fee Checker
- Automatically marks past-due fees as 'overdue'
- Sends a warning email to admin listing all overdue accounts
- Run daily at 9:00 AM via Task Scheduler
"""
import os
import sys
import django
import smtplib
from datetime import datetime, date
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
    with open(os.path.join(log_dir, 'overdue_checker.log'), 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'config.env')
    config = load_config(config_path)
    log_dir = config.get('LOG_DIR', os.path.join(config['UIMS_PATH'], 'automation', 'logs'))
    os.makedirs(log_dir, exist_ok=True)

    setup_django(config['UIMS_PATH'])
    from college.models import FeeRecord

    today = date.today()
    log(log_dir, "=" * 50)
    log(log_dir, f"Overdue Fee Check — {today}")

    # Mark overdue
    newly_overdue = FeeRecord.objects.filter(
        due_date__lt=today,
        status__in=['pending', 'partial']
    )
    count = newly_overdue.count()
    newly_overdue.update(status='overdue')
    log(log_dir, f"Marked {count} new record(s) as overdue.")

    # All overdue records
    all_overdue = FeeRecord.objects.filter(
        status='overdue'
    ).select_related('student').order_by('due_date')

    if not all_overdue.exists():
        log(log_dir, "No overdue fees. All clear!")
        return

    total_overdue_amount = sum(f.amount - f.paid_amount for f in all_overdue)
    days_overdue_map = {f.id: (today - f.due_date).days for f in all_overdue}

    # Build table rows for email
    table_rows = ''
    for f in all_overdue[:50]:
        days = days_overdue_map[f.id]
        balance = f.amount - f.paid_amount
        severity = '#dc2626' if days > 30 else '#b45309' if days > 7 else '#6b6b65'
        table_rows += f"""
        <tr>
          <td style="padding:7px 10px;">{f.student.roll_number}</td>
          <td style="padding:7px 10px;">{f.student.first_name} {f.student.last_name}</td>
          <td style="padding:7px 10px;">{f.get_fee_type_display()}</td>
          <td style="padding:7px 10px;color:#dc2626;font-weight:600;">PKR {balance:,.0f}</td>
          <td style="padding:7px 10px;">{f.due_date.strftime('%d %b %Y')}</td>
          <td style="padding:7px 10px;color:{severity};font-weight:600;">{days} days</td>
        </tr>
        """

    more_note = f'<p style="color:#6b6b65;font-size:12px;">Showing top 50 of {all_overdue.count()} overdue records.</p>' if all_overdue.count() > 50 else ''

    subject = f"⚠ UIMS Overdue Fees Alert — {all_overdue.count()} records — PKR {total_overdue_amount:,.0f}"
    body = f"""
    <div style="font-family:'Segoe UI',sans-serif;max-width:700px;margin:auto;">
      <div style="background:#dc2626;padding:20px 24px;border-radius:10px 10px 0 0;">
        <h2 style="color:#fff;margin:0;">⚠ Overdue Fee Report</h2>
        <p style="color:rgba(255,255,255,0.85);margin:4px 0 0;font-size:14px;">{today.strftime('%A, %d %B %Y')}</p>
      </div>
      <div style="border:1px solid #fecaca;border-top:none;padding:20px;border-radius:0 0 10px 10px;">
        <div style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;">
          <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:12px 20px;min-width:140px;">
            <div style="font-size:11px;color:#9e9e98;text-transform:uppercase;letter-spacing:0.05em;">Overdue Records</div>
            <div style="font-size:26px;font-weight:700;color:#dc2626;">{all_overdue.count()}</div>
          </div>
          <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:12px 20px;min-width:140px;">
            <div style="font-size:11px;color:#9e9e98;text-transform:uppercase;letter-spacing:0.05em;">Total Overdue</div>
            <div style="font-size:26px;font-weight:700;color:#dc2626;">PKR {total_overdue_amount:,.0f}</div>
          </div>
          <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:12px 20px;min-width:140px;">
            <div style="font-size:11px;color:#9e9e98;text-transform:uppercase;letter-spacing:0.05em;">Newly Overdue</div>
            <div style="font-size:26px;font-weight:700;color:#b45309;">{count}</div>
          </div>
        </div>

        <table style="width:100%;border-collapse:collapse;font-size:13px;">
          <thead>
            <tr style="background:#fef2f2;border-bottom:1px solid #fecaca;">
              <th style="padding:8px 10px;text-align:left;color:#dc2626;">Roll No</th>
              <th style="padding:8px 10px;text-align:left;color:#dc2626;">Student</th>
              <th style="padding:8px 10px;text-align:left;color:#dc2626;">Fee Type</th>
              <th style="padding:8px 10px;text-align:left;color:#dc2626;">Balance</th>
              <th style="padding:8px 10px;text-align:left;color:#dc2626;">Due Date</th>
              <th style="padding:8px 10px;text-align:left;color:#dc2626;">Days Overdue</th>
            </tr>
          </thead>
          <tbody>{table_rows}</tbody>
        </table>
        {more_note}
        <p style="color:#9e9e98;font-size:12px;margin-top:20px;border-top:1px solid #fecaca;padding-top:12px;">
          Generated by UIMS at {datetime.now().strftime('%H:%M')}. Please follow up with students listed above.
        </p>
      </div>
    </div>
    """

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"UIMS Alerts <{config['EMAIL_USER']}>"
        msg['To'] = config['ADMIN_EMAIL']
        msg.attach(MIMEText(body, 'html'))
        with smtplib.SMTP(config['EMAIL_HOST'], int(config['EMAIL_PORT'])) as server:
            server.starttls()
            server.login(config['EMAIL_USER'], config['EMAIL_PASS'])
            server.send_message(msg)
        log(log_dir, f"Overdue report sent to {config['ADMIN_EMAIL']}")
    except Exception as e:
        log(log_dir, f"Failed to send overdue report: {e}")

    log(log_dir, f"Done. Total overdue: {all_overdue.count()}, Amount: PKR {total_overdue_amount:,.0f}")


if __name__ == '__main__':
    main()
