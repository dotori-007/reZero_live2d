@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] setup.ps1 execution failed with code %ERRORLEVEL%
)
pause
