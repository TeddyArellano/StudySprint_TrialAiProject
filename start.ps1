# Study Sprint Agent - Iniciador PowerShell

Write-Host "========================================"  -ForegroundColor Cyan
Write-Host "Study Sprint Agent - Iniciando Sistema" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Obtener el directorio del script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "[1/2] Iniciando Backend (FastAPI)..." -ForegroundColor Yellow
Set-Location "$scriptPath\backend"
Start-Process python -ArgumentList "main.py" -WindowStyle Normal
Start-Sleep -Seconds 3

Write-Host "[2/2] Iniciando Frontend (React)..." -ForegroundColor Yellow
Set-Location "$scriptPath\frontend"
Start-Process cmd -ArgumentList "/c npm start" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Sistema iniciado correctamente" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
