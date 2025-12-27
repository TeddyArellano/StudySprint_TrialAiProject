@echo off
echo ========================================
echo Study Sprint Agent - Iniciando Sistema
echo ========================================
echo.

echo [1/2] Iniciando Backend (FastAPI)...
cd /d "%~dp0backend"
start "Study Sprint Backend" cmd /c "python main.py"
timeout /t 3 >nul

echo [2/2] Iniciando Frontend (React)...
cd /d "%~dp0frontend"
start "Study Sprint Frontend" cmd /c "npm start"

echo.
echo ========================================
echo Sistema iniciado correctamente
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
