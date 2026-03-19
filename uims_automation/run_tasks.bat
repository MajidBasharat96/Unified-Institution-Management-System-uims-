@echo off
:: ============================================================
::  UIMS Manual Task Runner
::  Use this to test or manually trigger any automation task
:: ============================================================
title UIMS Manual Task Runner
color 0B

:MENU
cls
echo.
echo  =====================================================
echo   UIMS Automation — Manual Task Runner
echo  =====================================================
echo.
echo   [1] Run Daily Backup NOW
echo   [2] Send Fee Reminders NOW
echo   [3] Send Appointment Reminders NOW
echo   [4] Run Overdue Fee Checker NOW
echo   [5] Send Daily Admin Report NOW
echo   [6] Run ALL tasks
echo   [7] View Logs
echo   [8] Exit
echo.
set /p CHOICE="  Enter choice (1-8): "

set CONFIG=%~dp0config.env
if not exist "%CONFIG%" (
    echo.
    echo  [ERROR] config.env not found. Please run install.bat first.
    pause
    goto MENU
)

for /f "tokens=1,2 delims==" %%a in (%CONFIG%) do set %%a=%%b
set PYTHON=%VENV_PYTHON%
set AUTO=%~dp0

if "%CHOICE%"=="1" goto BACKUP
if "%CHOICE%"=="2" goto FEES
if "%CHOICE%"=="3" goto APPTS
if "%CHOICE%"=="4" goto OVERDUE
if "%CHOICE%"=="5" goto REPORT
if "%CHOICE%"=="6" goto ALL
if "%CHOICE%"=="7" goto LOGS
if "%CHOICE%"=="8" exit /b 0
goto MENU

:BACKUP
echo.
echo  Running backup...
"%PYTHON%" "%AUTO%backup.py" "%CONFIG%"
echo.
echo  Done. Press any key to return to menu.
pause >nul
goto MENU

:FEES
echo.
echo  Sending fee reminders...
"%PYTHON%" "%AUTO%fee_reminders.py" "%CONFIG%"
echo.
pause >nul
goto MENU

:APPTS
echo.
echo  Sending appointment reminders...
"%PYTHON%" "%AUTO%appointment_reminders.py" "%CONFIG%"
echo.
pause >nul
goto MENU

:OVERDUE
echo.
echo  Running overdue checker...
"%PYTHON%" "%AUTO%overdue_checker.py" "%CONFIG%"
echo.
pause >nul
goto MENU

:REPORT
echo.
echo  Generating daily report...
"%PYTHON%" "%AUTO%daily_report.py" "%CONFIG%"
echo.
pause >nul
goto MENU

:ALL
echo.
echo  Running ALL tasks in sequence...
echo.
echo  [1/5] Backup...
"%PYTHON%" "%AUTO%backup.py" "%CONFIG%"
echo  [2/5] Overdue checker...
"%PYTHON%" "%AUTO%overdue_checker.py" "%CONFIG%"
echo  [3/5] Fee reminders...
"%PYTHON%" "%AUTO%fee_reminders.py" "%CONFIG%"
echo  [4/5] Appointment reminders...
"%PYTHON%" "%AUTO%appointment_reminders.py" "%CONFIG%"
echo  [5/5] Daily report...
"%PYTHON%" "%AUTO%daily_report.py" "%CONFIG%"
echo.
echo  All tasks complete!
pause >nul
goto MENU

:LOGS
cls
echo.
echo  =====================================================
echo   Log Files
echo  =====================================================
echo.
set LOGDIR=%LOG_DIR%
if not exist "%LOGDIR%" (
    echo  No logs found yet.
    pause >nul
    goto MENU
)
echo  Log directory: %LOGDIR%
echo.
dir "%LOGDIR%\*.log" /b
echo.
set /p LOGNAME="  Enter log filename to view (or press Enter to go back): "
if "%LOGNAME%"=="" goto MENU
if exist "%LOGDIR%\%LOGNAME%" (
    type "%LOGDIR%\%LOGNAME%" | more
) else (
    echo  File not found.
)
pause >nul
goto MENU
