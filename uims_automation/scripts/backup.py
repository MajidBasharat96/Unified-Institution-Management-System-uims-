"""
UIMS Daily Backup Script
- Backs up SQLite database (or dumps PostgreSQL)
- Keeps last 30 days of backups
- Emails admin if backup fails
- Run via Task Scheduler at 2:00 AM
"""
import os
import sys
import shutil
import smtplib
import sqlite3
from datetime import datetime, timedelta
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


def send_email(config, subject, body, is_html=False):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config['EMAIL_USER']
        msg['To'] = config['ADMIN_EMAIL']
        part = MIMEText(body, 'html' if is_html else 'plain')
        msg.attach(part)
        with smtplib.SMTP(config['EMAIL_HOST'], int(config['EMAIL_PORT'])) as server:
            server.starttls()
            server.login(config['EMAIL_USER'], config['EMAIL_PASS'])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False


def log(log_dir, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_file = os.path.join(log_dir, 'backup.log')
    line = f"[{timestamp}] {message}"
    print(line)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def backup_sqlite(config, log_dir):
    uims_path = config['UIMS_PATH']
    db_path = os.path.join(uims_path, 'uims.db')

    if not os.path.exists(db_path):
        log(log_dir, "ERROR: uims.db not found!")
        return False, "Database file not found"

    # Create backup directory
    backup_dir = os.path.join(uims_path, 'automation', 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    # Timestamped backup filename
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_file = os.path.join(backup_dir, f'uims_backup_{timestamp}.db')

    # Use SQLite's backup API for a safe consistent copy
    try:
        source = sqlite3.connect(db_path)
        dest = sqlite3.connect(backup_file)
        source.backup(dest)
        source.close()
        dest.close()
        size_mb = os.path.getsize(backup_file) / (1024 * 1024)
        log(log_dir, f"Backup created: {backup_file} ({size_mb:.2f} MB)")
        return True, backup_file
    except Exception as e:
        log(log_dir, f"Backup ERROR: {e}")
        return False, str(e)


def cleanup_old_backups(config, log_dir, keep_days=30):
    backup_dir = os.path.join(config['UIMS_PATH'], 'automation', 'backups')
    if not os.path.exists(backup_dir):
        return
    cutoff = datetime.now() - timedelta(days=keep_days)
    removed = 0
    for fname in os.listdir(backup_dir):
        fpath = os.path.join(backup_dir, fname)
        if os.path.isfile(fpath):
            modified = datetime.fromtimestamp(os.path.getmtime(fpath))
            if modified < cutoff:
                os.remove(fpath)
                removed += 1
    if removed:
        log(log_dir, f"Cleaned up {removed} old backup(s) older than {keep_days} days.")


def count_backups(config):
    backup_dir = os.path.join(config['UIMS_PATH'], 'automation', 'backups')
    if not os.path.exists(backup_dir):
        return 0
    return len([f for f in os.listdir(backup_dir) if f.endswith('.db')])


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), 'config.env')
    config = load_config(config_path)
    log_dir = config.get('LOG_DIR', os.path.join(config['UIMS_PATH'], 'automation', 'logs'))
    os.makedirs(log_dir, exist_ok=True)

    log(log_dir, "=" * 50)
    log(log_dir, "UIMS Daily Backup Started")

    success, result = backup_sqlite(config, log_dir)
    cleanup_old_backups(config, log_dir)
    total_backups = count_backups(config)

    if success:
        log(log_dir, f"Backup completed successfully. Total backups: {total_backups}")
        subject = "✅ UIMS Backup Successful"
        body = f"""
        <h2 style="color:#15803d;">UIMS Daily Backup — Success</h2>
        <p>The nightly database backup completed successfully.</p>
        <table style="border-collapse:collapse;font-family:sans-serif;">
          <tr><td style="padding:6px 12px;color:#6b6b65;">Date</td><td style="padding:6px 12px;"><strong>{datetime.now().strftime('%Y-%m-%d %H:%M')}</strong></td></tr>
          <tr><td style="padding:6px 12px;color:#6b6b65;">Backup File</td><td style="padding:6px 12px;">{os.path.basename(result)}</td></tr>
          <tr><td style="padding:6px 12px;color:#6b6b65;">Total Backups Stored</td><td style="padding:6px 12px;">{total_backups} (last 30 days)</td></tr>
        </table>
        """
    else:
        log(log_dir, f"Backup FAILED: {result}")
        subject = "❌ UIMS Backup FAILED"
        body = f"""
        <h2 style="color:#dc2626;">UIMS Daily Backup — FAILED</h2>
        <p>The nightly backup encountered an error. Please check your server.</p>
        <p><strong>Error:</strong> {result}</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        """

    send_email(config, subject, body, is_html=True)
    log(log_dir, "Backup script finished.")


if __name__ == '__main__':
    main()
