# Script de Verificación del Entorno para Despliegue con ngrok
# Verifica que todo esté listo antes de exponer el sistema

Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        Verificación del Entorno - Sistema Carrocería Alvarado     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$errores = 0
$advertencias = 0
$exitos = 0

# ========== VERIFICAR ESTRUCTURA DE CARPETAS ==========
Write-Host "📁 Verificando estructura de carpetas..." -ForegroundColor Yellow

$carpetasRequeridas = @("frontend", "backend", "docs")
foreach ($carpeta in $carpetasRequeridas) {
    if (Test-Path $carpeta) {
        Write-Host "   ✓ $carpeta" -ForegroundColor Green
        $exitos++
    }
    else {
        Write-Host "   ✗ $carpeta - NO ENCONTRADA" -ForegroundColor Red
        $errores++
    }
}

# ========== VERIFICAR ARCHIVOS CRÍTICOS ==========
Write-Host "`n📄 Verificando archivos críticos..." -ForegroundColor Yellow

$archivosRequeridos = @(
    "backend\app.py",
    "frontend\index.html",
    "frontend\listar_ordenes_trabajo.html",
    "configurar_ngrok_completo.ps1"
)

foreach ($archivo in $archivosRequeridos) {
    if (Test-Path $archivo) {
        Write-Host "   ✓ $archivo" -ForegroundColor Green
        $exitos++
    }
    else {
        Write-Host "   ✗ $archivo - NO ENCONTRADO" -ForegroundColor Red
        $errores++
    }
}

# ========== VERIFICAR SERVIDORES CORRIENDO ==========
Write-Host "`n🖥️  Verificando servidores locales..." -ForegroundColor Yellow

# Verificar puerto 5000 (Backend)
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✓ Backend (puerto 5000) - CORRIENDO" -ForegroundColor Green
    $exitos++
}
catch {
    Write-Host "   ✗ Backend (puerto 5000) - NO RESPONDE" -ForegroundColor Red
    Write-Host "     Ejecuta: cd backend && python app.py" -ForegroundColor Gray
    $errores++
}

# Verificar puerto 8000 (Frontend)
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✓ Frontend (puerto 8000) - CORRIENDO" -ForegroundColor Green
    $exitos++
}
catch {
    Write-Host "   ✗ Frontend (puerto 8000) - NO RESPONDE" -ForegroundColor Red
    Write-Host "     Ejecuta: cd frontend && python -m http.server 8000" -ForegroundColor Gray
    $errores++
}

# ========== VERIFICAR NGROK ==========
Write-Host "`n🌐 Verificando ngrok..." -ForegroundColor Yellow

# Verificar si ngrok está instalado
$ngrokPath = "C:\ngrok\ngrok.exe"
if (Test-Path $ngrokPath) {
    Write-Host "   ✓ ngrok instalado en $ngrokPath" -ForegroundColor Green
    $exitos++
    
    # Verificar versión
    try {
        $version = & $ngrokPath version 2>&1
        Write-Host "     Versión: $version" -ForegroundColor Gray
    }
    catch {
        Write-Host "     ⚠ No se pudo obtener la versión" -ForegroundColor Yellow
    }
}
else {
    Write-Host "   ✗ ngrok NO encontrado en $ngrokPath" -ForegroundColor Red
    Write-Host "     Descarga desde: https://ngrok.com/download" -ForegroundColor Gray
    $errores++
}

# Verificar si ngrok está configurado con authtoken
$ngrokConfigPath = "$env:USERPROFILE\.ngrok2\ngrok.yml"
if (Test-Path $ngrokConfigPath) {
    $configContent = Get-Content $ngrokConfigPath -Raw
    if ($configContent -match "authtoken:") {
        Write-Host "   ✓ ngrok configurado con authtoken" -ForegroundColor Green
        $exitos++
    }
    else {
        Write-Host "   ⚠ ngrok instalado pero sin authtoken" -ForegroundColor Yellow
        Write-Host "     Ejecuta: ngrok config add-authtoken TU_TOKEN" -ForegroundColor Gray
        $advertencias++
    }
}
else {
    Write-Host "   ⚠ Archivo de configuración de ngrok no encontrado" -ForegroundColor Yellow
    Write-Host "     Ejecuta: ngrok config add-authtoken TU_TOKEN" -ForegroundColor Gray
    $advertencias++
}

# Verificar si ngrok está corriendo
$ngrokRunning = Get-Process -Name "ngrok" -ErrorAction SilentlyContinue
if ($ngrokRunning) {
    Write-Host "   ✓ ngrok está corriendo ($($ngrokRunning.Count) instancia(s))" -ForegroundColor Green
    $exitos++
    
    # Verificar interfaz web de ngrok
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:4040/api/tunnels" -Method GET -TimeoutSec 2 -ErrorAction Stop
        $tunnels = $response.Content | ConvertFrom-Json
        
        if ($tunnels.tunnels.Count -gt 0) {
            Write-Host "`n   📊 Túneles activos:" -ForegroundColor Cyan
            foreach ($tunnel in $tunnels.tunnels) {
                Write-Host "      • $($tunnel.public_url) -> $($tunnel.config.addr)" -ForegroundColor White
            }
        }
    }
    catch {
        Write-Host "   ⚠ No se pudo acceder a la interfaz de ngrok" -ForegroundColor Yellow
    }
}
else {
    Write-Host "   ⚠ ngrok NO está corriendo" -ForegroundColor Yellow
    Write-Host "     Para iniciar: ngrok http 5000 --host-header='localhost:5000'" -ForegroundColor Gray
    $advertencias++
}

# ========== VERIFICAR DEPENDENCIAS DE PYTHON ==========
Write-Host "`n🐍 Verificando dependencias de Python..." -ForegroundColor Yellow

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✓ Python instalado: $pythonVersion" -ForegroundColor Green
    $exitos++
}
catch {
    Write-Host "   ✗ Python NO encontrado" -ForegroundColor Red
    $errores++
}

# Verificar requirements.txt
if (Test-Path "requirements.txt") {
    Write-Host "   ✓ requirements.txt encontrado" -ForegroundColor Green
    $exitos++
    
    # Verificar Flask
    try {
        $flaskVersion = python -c "import flask; print(flask.__version__)" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "     ✓ Flask instalado (v$flaskVersion)" -ForegroundColor Green
        }
        else {
            Write-Host "     ✗ Flask NO instalado" -ForegroundColor Red
            Write-Host "       Ejecuta: pip install -r requirements.txt" -ForegroundColor Gray
            $errores++
        }
    }
    catch {
        Write-Host "     ⚠ No se pudo verificar Flask" -ForegroundColor Yellow
        $advertencias++
    }
}
else {
    Write-Host "   ⚠ requirements.txt NO encontrado" -ForegroundColor Yellow
    $advertencias++
}

# ========== VERIFICAR CORS EN BACKEND ==========
Write-Host "`n🔒 Verificando configuración de CORS..." -ForegroundColor Yellow

if (Test-Path "backend\app.py") {
    $appContent = Get-Content "backend\app.py" -Raw
    
    if ($appContent -match "from flask_cors import CORS") {
        Write-Host "   ✓ flask_cors importado" -ForegroundColor Green
        $exitos++
    }
    else {
        Write-Host "   ✗ flask_cors NO importado" -ForegroundColor Red
        Write-Host "     Añade: from flask_cors import CORS" -ForegroundColor Gray
        $errores++
    }
    
    if ($appContent -match "CORS\(app") {
        Write-Host "   ✓ CORS configurado en app" -ForegroundColor Green
        $exitos++
    }
    else {
        Write-Host "   ✗ CORS NO configurado" -ForegroundColor Red
        Write-Host "     Añade: CORS(app, resources={r'/*': {'origins': '*'}})" -ForegroundColor Gray
        $errores++
    }
}

# ========== VERIFICAR CONFIGURACIÓN DE URLs ==========
Write-Host "`n⚙️  Verificando configuración de URLs..." -ForegroundColor Yellow

if (Test-Path "frontend\js\config.js") {
    Write-Host "   ✓ config.js encontrado" -ForegroundColor Green
    $exitos++
    
    $configContent = Get-Content "frontend\js\config.js" -Raw
    if ($configContent -match "http://127\.0\.0\.1:5000") {
        Write-Host "   ℹ  Configurado para desarrollo local" -ForegroundColor Cyan
    }
    elseif ($configContent -match "https://.*\.ngrok.*\.app") {
        Write-Host "   ℹ  Configurado para ngrok" -ForegroundColor Cyan
        if ($configContent -match "const API_BASE_URL = '(https://.*\.ngrok.*\.app)'") {
            Write-Host "     URL: $($matches[1])" -ForegroundColor Gray
        }
    }
}
else {
    Write-Host "   ⚠ config.js NO encontrado" -ForegroundColor Yellow
    $advertencias++
}

# ========== RESUMEN FINAL ==========
Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor White
Write-Host "║                        RESUMEN DE VERIFICACIÓN                     ║" -ForegroundColor White
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor White

Write-Host "`n📊 Resultados:" -ForegroundColor Cyan
Write-Host "   ✓ Verificaciones exitosas: $exitos" -ForegroundColor Green
Write-Host "   ⚠ Advertencias: $advertencias" -ForegroundColor Yellow
Write-Host "   ✗ Errores: $errores" -ForegroundColor Red

Write-Host "`n🎯 Estado general:" -ForegroundColor Cyan
if ($errores -eq 0 -and $advertencias -eq 0) {
    Write-Host "   ✅ PERFECTO - Todo listo para desplegar con ngrok!" -ForegroundColor Green
    Write-Host "`n📋 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "   1. Ejecuta ngrok en dos terminales (puertos 5000 y 8000)" -ForegroundColor White
    Write-Host "   2. Ejecuta: .\configurar_ngrok_completo.ps1 -BackendUrl 'TU_URL'" -ForegroundColor White
    Write-Host "   3. Comparte la URL del frontend con tus usuarios" -ForegroundColor White
}
elseif ($errores -eq 0) {
    Write-Host "   ⚠️  CASI LISTO - Hay algunas advertencias" -ForegroundColor Yellow
    Write-Host "   Puedes continuar, pero revisa las advertencias arriba." -ForegroundColor Yellow
}
else {
    Write-Host "   ❌ NO LISTO - Hay errores que deben corregirse" -ForegroundColor Red
    Write-Host "   Revisa y corrige los errores antes de continuar." -ForegroundColor Red
}

Write-Host "`n📚 Documentación:" -ForegroundColor Cyan
Write-Host "   • Guía completa: docs\DESPLIEGUE_NGROK.md" -ForegroundColor White
Write-Host "   • Guía rápida: docs\GUIA_RAPIDA_NGROK.md" -ForegroundColor White
Write-Host "   • Resumen: README_NGROK.md" -ForegroundColor White

Write-Host ""
