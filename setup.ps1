# Re:Zero Live2D Companion Setup Script
$ErrorActionPreference = "Continue"

$companionDir = $PSScriptRoot
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "         Re:Zero Live2D Companion Auto Setup" -ForegroundColor Green
Write-Host "=============================================================================="
Write-Host "Path: $companionDir"
Write-Host ""

# 1. Python Check & Selection
Write-Host "[1/3] Checking Python environment..." -ForegroundColor Cyan
$pythonCmd = "python"
$knownPy = "C:\2026591001\Python_3.10.11_64\python.exe"
if (Test-Path $knownPy) {
    $pythonCmd = $knownPy
} else {
    $pyPaths = & where.exe python 2>&1
    foreach ($p in $pyPaths) {
        if ($p -and ($p -notmatch "WindowsApps") -and (Test-Path $p.Trim())) {
            $pythonCmd = $p.Trim()
            break
        }
    }
}

try {
    $pyVer = & $pythonCmd --version 2>&1
    Write-Host "[OK] Detected: $pyVer (using: $pythonCmd)" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not found!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. Pip Dependencies
Write-Host "[2/3] Installing dependencies from requirements.txt..." -ForegroundColor Cyan
& $pythonCmd -m pip install -r "$companionDir\requirements.txt"
Write-Host "[OK] Dependencies ready." -ForegroundColor Green
Write-Host ""

# 3. Windows Task Scheduler
Write-Host "[3/3] Registering Windows Task Scheduler (ReZeroMascot)..." -ForegroundColor Cyan
try {
    $vbsPath = Join-Path $companionDir "start_rezero.vbs"
    $action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument "`"$vbsPath`""
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Days 3)
    Register-ScheduledTask -TaskName "ReZeroMascot" -Action $action -Settings $settings -Force | Out-Null
    Write-Host "[OK] Task Scheduler registered successfully! (ReZeroMascot)" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Task registration failed: $_" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "  Setup completed successfully!" -ForegroundColor Green
Write-Host "  Launch command: schtasks /run /tn `"ReZeroMascot`"" -ForegroundColor Cyan
Write-Host "  Or double click start_rezero.vbs in File Explorer." -ForegroundColor Cyan
Write-Host "=============================================================================="
Write-Host ""
