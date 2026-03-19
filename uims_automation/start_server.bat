@echo off
:: ============================================================
::  UIMS Server Launcher with Auto-Restart
::  Place this in startup or run via Task Scheduler
:: ============================================================
title UIMS Server

set CONFIG=%~1
if "%CONFIG%"=="" set CONFIG=%~dp0config.env

:: Load config
for /f "tokens=1,2 delims==" %%a in (%CONFIG%) do set %%a=%%b

set PYTHON=%VENV_PYTHON%
set LOG=%LOG_DIR%\server.log
set ERR=%LOG_DIR%\server_error.log

echo [%date% %time%] Starting UIMS Server... >> "%LOG%"

:RESTART_LOOP
echo [%date% %time%] Launching Django server on port 8000... >> "%LOG%"

cd /d "%UIMS_PATH%"

:: Run collectstatic silently before starting
"%PYTHON%" manage.py collectstatic --noinput >> "%LOG%" 2>&1

:: Start gunicorn (falls back to runserver if gunicorn not installed)
"%PYTHON%" -m gunicorn uims_project.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 >> "%LOG%" 2>&1
if %errorLevel% neq 0 (
    echo [%date% %time%] gunicorn failed, trying runserver... >> "%LOG%"
    "%PYTHON%" manage.py runserver 0.0.0.0:8000 >> "%LOG%" 2>&1
)

echo [%date% %time%] Server stopped. Restarting in 10 seconds... >> "%LOG%"
timeout /t 10 /nobreak >nul
goto RESTART_LOOP
