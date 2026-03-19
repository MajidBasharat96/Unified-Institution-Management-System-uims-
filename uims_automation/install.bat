@echo off
:: ============================================================
::  UIMS Automation Installer
::  Run this ONCE as Administrator to set everything up
:: ============================================================
title UIMS Automation Installer
color 0A

echo.
echo  =====================================================
echo   UIMS - Unified Institution Management System
echo   Automation Installer for Windows
echo  =====================================================
echo.

:: Check for Admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo  [ERROR] Please run this script as Administrator!
    echo  Right-click install.bat and select "Run as administrator"
    pause
    exit /b 1
)

:: ── Step 1: Ask for project path ──────────────────────────
echo  [1/6] Configuring paths...
set /p UIMS_PATH="Enter full path to your UIMS project (e.g. C:\Users\Waqar JSA\Desktop\uims): "
if not exist "%UIMS_PATH%\manage.py" (
    echo  [ERROR] manage.py not found at %UIMS_PATH%
    echo  Please check the path and try again.
    pause
    exit /b 1
)

set /p VENV_PATH="Enter full path to your venv folder (e.g. %UIMS_PATH%\venv): "
if not exist "%VENV_PATH%\Scripts\python.exe" (
    echo  [ERROR] Python not found at %VENV_PATH%\Scripts\python.exe
    pause
    exit /b 1
)

:: ── Step 2: Email config ──────────────────────────────────
echo.
echo  [2/6] Email notification setup...
set /p EMAIL_HOST="SMTP Host (e.g. smtp.gmail.com): "
set /p EMAIL_PORT="SMTP Port (587 for Gmail): "
set /p EMAIL_USER="Your email address: "
set /p EMAIL_PASS="Your email password / app password: "
set /p ADMIN_EMAIL="Admin email to receive reports: "

:: Save config file
set CONFIG_FILE=%UIMS_PATH%\automation\config.env
mkdir "%UIMS_PATH%\automation" 2>nul
(
echo UIMS_PATH=%UIMS_PATH%
echo VENV_PYTHON=%VENV_PATH%\Scripts\python.exe
echo EMAIL_HOST=%EMAIL_HOST%
echo EMAIL_PORT=%EMAIL_PORT%
echo EMAIL_USER=%EMAIL_USER%
echo EMAIL_PASS=%EMAIL_PASS%
echo ADMIN_EMAIL=%ADMIN_EMAIL%
echo LOG_DIR=%UIMS_PATH%\automation\logs
) > "%CONFIG_FILE%"
echo  Config saved to %CONFIG_FILE%

:: Create log directory
mkdir "%UIMS_PATH%\automation\logs" 2>nul

:: ── Step 3: Copy scripts ──────────────────────────────────
echo.
echo  [3/6] Copying automation scripts...
set SCRIPT_DIR=%~dp0scripts
copy "%SCRIPT_DIR%\*.py" "%UIMS_PATH%\automation\" >nul
echo  Scripts copied.

:: ── Step 4: Install UIMS as Windows Service ───────────────
echo.
echo  [4/6] Installing UIMS as a Windows Service...

:: Create the service wrapper batch file
(
echo @echo off
echo cd /d "%UIMS_PATH%"
echo "%VENV_PATH%\Scripts\python.exe" -m gunicorn uims_project.wsgi:application --bind 0.0.0.0:8000 --workers 2 --log-file "%UIMS_PATH%\automation\logs\gunicorn.log" --access-logfile "%UIMS_PATH%\automation\logs\access.log"
) > "%UIMS_PATH%\automation\start_server.bat"

:: Use NSSM (Non-Sucking Service Manager) if available, otherwise use Task Scheduler
where nssm >nul 2>&1
if %errorLevel% == 0 (
    nssm install UIMS_Server "%UIMS_PATH%\automation\start_server.bat"
    nssm set UIMS_Server DisplayName "UIMS - Institution Management Server"
    nssm set UIMS_Server Description "Runs the UIMS Django web server on port 8000"
    nssm set UIMS_Server Start SERVICE_AUTO_START
    nssm set UIMS_Server AppStdout "%UIMS_PATH%\automation\logs\service.log"
    nssm set UIMS_Server AppStderr "%UIMS_PATH%\automation\logs\service_error.log"
    nssm start UIMS_Server
    echo  UIMS Server installed as Windows Service (via NSSM^).
) else (
    echo  NSSM not found. Creating startup Task Scheduler entry instead...
    schtasks /create /tn "UIMS_AutoStart" /tr "\"%UIMS_PATH%\automation\start_server.bat\"" /sc onstart /ru SYSTEM /rl HIGHEST /f
    echo  UIMS will auto-start on Windows boot via Task Scheduler.
)

:: ── Step 5: Schedule automated tasks ─────────────────────
echo.
echo  [5/6] Scheduling automated tasks...

set PYTHON="%VENV_PATH%\Scripts\python.exe"
set AUTO_DIR=%UIMS_PATH%\automation

:: Daily backup at 2:00 AM
schtasks /create /tn "UIMS_DailyBackup" ^
  /tr "%PYTHON% \"%AUTO_DIR%\backup.py\" \"%CONFIG_FILE%\"" ^
  /sc daily /st 02:00 /ru SYSTEM /rl HIGHEST /f
echo  [OK] Daily backup scheduled at 2:00 AM

:: Fee due reminders — every day at 8:00 AM
schtasks /create /tn "UIMS_FeeReminders" ^
  /tr "%PYTHON% \"%AUTO_DIR%\fee_reminders.py\" \"%CONFIG_FILE%\"" ^
  /sc daily /st 08:00 /ru SYSTEM /rl HIGHEST /f
echo  [OK] Fee reminders scheduled at 8:00 AM

:: Appointment reminders — every day at 7:00 AM
schtasks /create /tn "UIMS_AppointmentReminders" ^
  /tr "%PYTHON% \"%AUTO_DIR%\appointment_reminders.py\" \"%CONFIG_FILE%\"" ^
  /sc daily /st 07:00 /ru SYSTEM /rl HIGHEST /f
echo  [OK] Appointment reminders scheduled at 7:00 AM

:: Daily report to admin — every day at 9:00 PM
schtasks /create /tn "UIMS_DailyReport" ^
  /tr "%PYTHON% \"%AUTO_DIR%\daily_report.py\" \"%CONFIG_FILE%\"" ^
  /sc daily /st 21:00 /ru SYSTEM /rl HIGHEST /f
echo  [OK] Daily admin report scheduled at 9:00 PM

:: Overdue fee checker — every day at 9:00 AM
schtasks /create /tn "UIMS_OverdueFees" ^
  /tr "%PYTHON% \"%AUTO_DIR%\overdue_checker.py\" \"%CONFIG_FILE%\"" ^
  /sc daily /st 09:00 /ru SYSTEM /rl HIGHEST /f
echo  [OK] Overdue fee checker scheduled at 9:00 AM

:: ── Step 6: Done ─────────────────────────────────────────
echo.
echo  [6/6] All done!
echo.
echo  =====================================================
echo   Automation Setup Complete
echo  =====================================================
echo.
echo   Service:    UIMS runs automatically on Windows boot
echo   Backup:     Daily at 2:00 AM
echo   Fees:       Reminders sent daily at 8:00 AM
echo   Appts:      Reminders sent daily at 7:00 AM
echo   Report:     Daily summary emailed at 9:00 PM
echo   Overdue:    Fee overdue check daily at 9:00 AM
echo.
echo   Logs saved to: %UIMS_PATH%\automation\logs\
echo   Config at:     %CONFIG_FILE%
echo.
echo   To manage tasks: Open Task Scheduler (taskschd.msc)
echo   To view service: Open Services (services.msc)
echo.
pause
