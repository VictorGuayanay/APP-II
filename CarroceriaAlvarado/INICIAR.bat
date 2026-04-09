@echo off
REM =========================================================
REM Script para ejecutar Backend + Frontend de Carrocer√≠a Alvarado
REM =========================================================
REM Este script abre dos ventanas PowerShell:
REM  - Terminal 1: Backend (Puerto 5001)
REM  - Terminal 2: Frontend (Puerto 8000)
REM =========================================================

echo.
echo ✓ Iniciando Carrocer√≠a Alvarado...
echo.

REM Obtener la ruta del directorio actual
set RUTA_BASE=%~dp0

echo [1/3] Iniciando Backend en puerto 5001...
start "Backend - Puerto 5001" powershell -NoExit -Command "cd '%RUTA_BASE%backend'; python app.py"

timeout /t 3 /nobreak

echo [2/3] Iniciando Frontend en puerto 8000...
start "Frontend - Puerto 8000" powershell -NoExit -Command "cd '%RUTA_BASE%frontend'; python -m http.server 8000"

timeout /t 2 /nobreak

echo [3/3] Abriendo navegador...
start http://127.0.0.1:8000

echo.
echo =========================================================
echo ✓ Carrocer√≠a Alvarado iniciado!
echo.
echo URLs:
echo  - Frontend:  http://127.0.0.1:8000
echo  - Backend:   http://127.0.0.1:5001
echo.
echo Usuario de prueba:
echo  - Username: admin
echo  - Password: 123456
echo  - Rol: Administrador
echo.
echo Nota: Ejecuta primero el script SQL: scripts/fix_usuarios_table.sql
echo =========================================================
pause
