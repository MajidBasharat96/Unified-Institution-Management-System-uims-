# UIMS Automation Package
### Windows Server / Local PC — Full Automation Suite

---

## What This Package Does

| Task | Schedule | Description |
|------|----------|-------------|
| **Auto Start** | On Windows boot | UIMS server starts automatically, restarts if it crashes |
| **Daily Backup** | Every night at 2:00 AM | Database backup saved, old ones cleaned up after 30 days |
| **Appointment Reminders** | Every day at 7:00 AM | Emails patients about tomorrow's appointments |
| **Fee Reminders** | Every day at 8:00 AM | Emails students about fees due in next 3 days |
| **Overdue Checker** | Every day at 9:00 AM | Marks overdue fees, emails admin a list |
| **Daily Report** | Every day at 9:00 PM | Full hospital + college summary emailed to admin |

---

## Installation (One-Time Setup)

### Step 1 — Prerequisites
Make sure UIMS is working correctly:
```
python manage.py runserver
```
Access it at `http://localhost:8000` before installing automation.

### Step 2 — Gmail Setup (Recommended)
For email notifications to work with Gmail:
1. Go to your Google Account → Security
2. Enable **2-Step Verification**
3. Go to **App Passwords** → Generate a new app password
4. Use that 16-character password (not your Gmail password) during setup

> For other providers: Outlook = `smtp-mail.outlook.com:587`, Yahoo = `smtp.mail.yahoo.com:587`

### Step 3 — Run the Installer
1. Right-click `install.bat` → **Run as administrator**
2. Enter your UIMS project path (e.g. `C:\Users\Waqar JSA\Desktop\uims`)
3. Enter your venv path (e.g. `C:\Users\Waqar JSA\Desktop\uims\venv`)
4. Enter your SMTP email settings
5. That's it — everything is configured automatically

---

## File Structure

```
automation/               ← Created inside your UIMS folder
├── config.env            ← Your settings (email, paths)
├── backup.py             ← Database backup script
├── fee_reminders.py      ← Fee due email reminders
├── appointment_reminders.py  ← Appointment email reminders
├── daily_report.py       ← Evening admin summary email
├── overdue_checker.py    ← Marks + reports overdue fees
├── start_server.bat      ← Auto-start server script
├── backups/              ← Database backups stored here
│   └── uims_backup_2026-03-19_02-00-00.db
└── logs/                 ← All task logs stored here
    ├── backup.log
    ├── fee_reminders.log
    ├── appointment_reminders.log
    ├── daily_report.log
    ├── overdue_checker.log
    └── server.log
```

---

## Manual Testing

Use `run_tasks.bat` to test any task immediately without waiting for the schedule:

```
Double-click run_tasks.bat
```

Menu options:
- Run backup now
- Send fee reminders now
- Send appointment reminders now
- Run overdue checker now
- Send daily report now
- Run ALL tasks
- View log files

---

## Managing Scheduled Tasks

Open **Task Scheduler** (`taskschd.msc` in Start menu) to:
- See all UIMS tasks
- Manually run or disable any task
- Change the schedule times

Tasks installed:
- `UIMS_AutoStart` — Server boot startup
- `UIMS_DailyBackup` — 2:00 AM daily
- `UIMS_AppointmentReminders` — 7:00 AM daily
- `UIMS_FeeReminders` — 8:00 AM daily
- `UIMS_OverdueFees` — 9:00 AM daily
- `UIMS_DailyReport` — 9:00 PM daily

---

## Uninstalling

Run `uninstall.bat` as Administrator to remove all tasks.
Your database and project files will not be touched.

---

## Troubleshooting

**Email not sending?**
- Check `logs/daily_report.log` for error details
- Make sure you used an App Password (not your main Gmail password)
- Check firewall is not blocking outbound port 587

**Server not auto-starting?**
- Open Task Scheduler → find `UIMS_AutoStart` → Run manually to test
- Check `logs/server.log` for startup errors

**Backup not running?**
- Check `logs/backup.log`
- Make sure the path in `config.env` is correct

**Edit config:** Open `automation\config.env` in Notepad to change email settings or paths.
