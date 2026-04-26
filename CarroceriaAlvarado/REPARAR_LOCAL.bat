@echo off
echo ======================================================
echo   REPARADOR DE ENTORNO LOCAL - CARROCERIA ALVARADO
echo ======================================================
echo.

:: 1. Verificar si existe el entorno virtual
if not exist "venv" (
    echo [!] No se encontro la carpeta 'venv'. Creando entorno virtual...
    python -m venv venv
)

:: 2. Activar entorno virtual e instalar requerimientos
echo [1/3] Activando entorno virtual y actualizando pip...
call venv\Scripts\activate
python -m pip install --upgrade pip

echo [2/3] Instalando librerias desde backend\requirements.txt...
:: Intentar encontrar el archivo en la raiz o en backend
if exist "requirements.txt" (
    pip install -r requirements.txt
) else if exist "backend\requirements.txt" (
    pip install -r backend\requirements.txt
) else (
    echo [ERROR] No se encontro el archivo requirements.txt en ninguna carpeta.
)

:: 3. Limpiar archivos de despliegue remanentes
echo [3/3] Limpiando archivos de despliegue...
if exist "Dockerfile" del Dockerfile
if exist "fly.toml" del fly.toml
if exist ".dockerignore" del .dockerignore
if exist "backend\Procfile" del backend\Procfile
if exist "backend\runtime.txt" del backend\runtime.txt

echo.
echo ======================================================
echo   ¡LISTO! Ahora puedes ejecutar el sistema:
echo   1. Abre una terminal y ejecuta: .\venv\Scripts\activate
echo   2. Luego: cd backend
echo   3. Finalmente: python app.py
echo ======================================================
pause
