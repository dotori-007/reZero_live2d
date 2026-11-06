@echo off
cd /d "%~dp0"

REM 1. Check known Python path
if exist "C:\2026591001\Python_3.10.11_64\pythonw.exe" (
    start "" "C:\2026591001\Python_3.10.11_64\pythonw.exe" "app.py"
    exit
)

REM 2. Check local venv
if exist "venv\Scripts\pythonw.exe" (
    start "" "venv\Scripts\pythonw.exe" "app.py"
    exit
)

REM 3. Check system PATH pythonw
where pythonw >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" pythonw "app.py"
    exit
)

start "" python "app.py"
exit
