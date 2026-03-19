@echo off
:: ============================================================
::  UIMS Automation Uninstaller
::  Removes all scheduled tasks and Windows service
:: ============================================================
title UIMS Uninstaller
color 0C

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Run as Administrator!
    pause
    exit /b 1
)

echo.
echo  Removing UIMS scheduled tasks...
schtasks /delete /tn "UIMS_AutoStart"        /f 2>nul && echo  [OK] UIMS_AutoStart removed
schtasks /delete /tn "UIMS_DailyBackup"      /f 2>nul && echo  [OK] UIMS_DailyBackup removed
schtasks /delete /tn "UIMS_FeeReminders"     /f 2>nul && echo  [OK] UIMS_FeeReminders removed
schtasks /delete /tn "UIMS_AppointmentReminders" /f 2>nul && echo  [OK] UIMS_AppointmentReminders removed
schtasks /delete /tn "UIMS_DailyReport"      /f 2>nul && echo  [OK] UIMS_DailyReport removed
schtasks /delete /tn "UIMS_OverdueFees"      /f 2>nul && echo  [OK] UIMS_OverdueFees removed

echo.
echo  Removing UIMS Windows Service (if installed)...
where nssm >nul 2>&1
if %errorLevel% == 0 (
    nssm stop UIMS_Server 2>nul
    nssm remove UIMS_Server confirm 2>nul
    echo  [OK] UIMS_Server service removed
)

echo.
echo  All UIMS automation tasks removed.
echo  Your database and project files are untouched.
echo.
pause
