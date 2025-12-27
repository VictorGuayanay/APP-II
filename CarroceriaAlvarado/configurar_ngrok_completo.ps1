# Script Avanzado de Configuración para ngrok
# Actualiza automáticamente TODOS los archivos HTML con la URL de ngrok

param(
    [Parameter(Mandatory = $false, HelpMessage = "URL de ngrok del backend (ejemplo: https://abc123.ngrok-free.app)")]
    [string]$BackendUrl,
    
    [Parameter(Mandatory = $false)]
    [switch]$Revertir,
    
    [Parameter(Mandatory = $false)]
    [switch]$VerificarSolamente
)

$frontendDir = "frontend"
$localUrl = "http://127.0.0.1:5000"
$archivosModificados = 0
$errores = 0

# Lista de archivos HTML que contienen URLs del backend
$archivosHTML = @(
    "listar_ordenes_trabajo.html",
    "orden_trabajo.html",
    "editar_orden.html",
    "detalle_orden.html",
    "ver_inventario.html",
    "anadir_material.html",
    "entradas_salidas_inventario.html",
    "ver_empleados.html",
    "ingresar_empleado.html",
    "ingresar_cliente.html",
    "ver_proveedores.html",
    "ingresar_proveedor.html",
    "consultar_comprobantes.html",
    "reportes.html",
    "vision_general.html",
    "gestion_categorias.html",
    "registrer.html",
    "index.html"
)

function Verificar-URLs {
    Write-Host "`n🔍 Verificando URLs en archivos HTML..." -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Gray
    
    foreach ($archivo in $archivosHTML) {
        $rutaCompleta = Join-Path $frontendDir $archivo
        
        if (Test-Path $rutaCompleta) {
            $contenido = Get-Content $rutaCompleta -Raw
            $ocurrencias = ([regex]::Matches($contenido, "http://127\.0\.0\.1:5000")).Count
            
            if ($ocurrencias -gt 0) {
                Write-Host "✓ $archivo" -ForegroundColor Yellow -NoNewline
                Write-Host " - $ocurrencias ocurrencia(s)" -ForegroundColor Gray
            }
            else {
                Write-Host "○ $archivo" -ForegroundColor Green -NoNewline
                Write-Host " - Sin URLs locales" -ForegroundColor Gray
            }
        }
        else {
            Write-Host "✗ $archivo" -ForegroundColor Red -NoNewline
            Write-Host " - Archivo no encontrado" -ForegroundColor Gray
        }
    }
    
    Write-Host ("=" * 70) -ForegroundColor Gray
}

function Actualizar-URLs {
    param([string]$urlNueva)
    
    Write-Host "`n🔧 Actualizando URLs en archivos HTML..." -ForegroundColor Cyan
    Write-Host "   URL anterior: $localUrl" -ForegroundColor Gray
    Write-Host "   URL nueva: $urlNueva" -ForegroundColor Gray
    Write-Host ("=" * 70) -ForegroundColor Gray
    
    foreach ($archivo in $archivosHTML) {
        $rutaCompleta = Join-Path $frontendDir $archivo
        
        if (Test-Path $rutaCompleta) {
            try {
                $contenido = Get-Content $rutaCompleta -Raw -Encoding UTF8
                $ocurrenciasAntes = ([regex]::Matches($contenido, [regex]::Escape($localUrl))).Count
                
                if ($ocurrenciasAntes -gt 0) {
                    # Reemplazar todas las ocurrencias
                    $contenidoNuevo = $contenido -replace [regex]::Escape($localUrl), $urlNueva
                    Set-Content $rutaCompleta -Value $contenidoNuevo -Encoding UTF8 -NoNewline
                    
                    $ocurrenciasDespues = ([regex]::Matches($contenidoNuevo, [regex]::Escape($urlNueva))).Count
                    
                    Write-Host "✓ $archivo" -ForegroundColor Green -NoNewline
                    Write-Host " - $ocurrenciasAntes URL(s) actualizadas" -ForegroundColor Gray
                    $script:archivosModificados++
                }
                else {
                    Write-Host "○ $archivo" -ForegroundColor Gray -NoNewline
                    Write-Host " - Sin cambios necesarios" -ForegroundColor DarkGray
                }
            }
            catch {
                Write-Host "✗ $archivo" -ForegroundColor Red -NoNewline
                Write-Host " - Error: $($_.Exception.Message)" -ForegroundColor Red
                $script:errores++
            }
        }
        else {
            Write-Host "⊘ $archivo" -ForegroundColor DarkGray -NoNewline
            Write-Host " - Archivo no encontrado (omitido)" -ForegroundColor DarkGray
        }
    }
    
    Write-Host ("=" * 70) -ForegroundColor Gray
}

# ========== MAIN ==========

Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Script de Configuración de URLs para ngrok - Carrocería       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Verificar que estamos en el directorio correcto
if (-not (Test-Path $frontendDir)) {
    Write-Host "❌ Error: No se encontró la carpeta '$frontendDir'" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar este script desde la raíz del proyecto." -ForegroundColor Yellow
    exit 1
}

# MODO: Solo Verificar
if ($VerificarSolamente) {
    Verificar-URLs
    Write-Host "`n✅ Verificación completada.`n" -ForegroundColor Green
    exit 0
}

# MODO: Revertir a Local
if ($Revertir) {
    Write-Host "🔄 Revirtiendo configuración a desarrollo local..." -ForegroundColor Yellow
    Actualizar-URLs -urlNueva $localUrl
    
    if ($archivosModificados -gt 0) {
        Write-Host "`n✅ Configuración revertida exitosamente!" -ForegroundColor Green
        Write-Host "   📁 Archivos modificados: $archivosModificados" -ForegroundColor White
        if ($errores -gt 0) {
            Write-Host "   ⚠️  Errores encontrados: $errores" -ForegroundColor Yellow
        }
        Write-Host "   🌐 URL actual: $localUrl`n" -ForegroundColor White
    }
    else {
        Write-Host "`n⚠️  No se encontraron URLs de ngrok para revertir.`n" -ForegroundColor Yellow
    }
    exit 0
}

# MODO: Actualizar a ngrok
if (-not $BackendUrl) {
    Write-Host "❌ Error: Debes proporcionar la URL del backend de ngrok`n" -ForegroundColor Red
    Write-Host "Uso:" -ForegroundColor Yellow
    Write-Host "  .\configurar_ngrok_completo.ps1 -BackendUrl 'https://abc123.ngrok-free.app'" -ForegroundColor White
    Write-Host "  .\configurar_ngrok_completo.ps1 -Revertir" -ForegroundColor White
    Write-Host "  .\configurar_ngrok_completo.ps1 -VerificarSolamente`n" -ForegroundColor White
    exit 1
}

# Validar formato de URL
if (-not $BackendUrl.StartsWith("https://")) {
    Write-Host "❌ Error: La URL debe comenzar con https://" -ForegroundColor Red
    Write-Host "   Ejemplo: https://abc123.ngrok-free.app`n" -ForegroundColor Yellow
    exit 1
}

# Remover trailing slash si existe
$BackendUrl = $BackendUrl.TrimEnd('/')

# Confirmar con el usuario
Write-Host "⚠️  Estás a punto de actualizar TODOS los archivos HTML" -ForegroundColor Yellow
Write-Host "   URL nueva: $BackendUrl" -ForegroundColor White
Write-Host "`n¿Deseas continuar? (S/N): " -ForegroundColor Cyan -NoNewline
$confirmacion = Read-Host

if ($confirmacion -ne 'S' -and $confirmacion -ne 's') {
    Write-Host "`n❌ Operación cancelada por el usuario.`n" -ForegroundColor Red
    exit 0
}

# Realizar la actualización
Actualizar-URLs -urlNueva $BackendUrl

# Resumen final
Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    ACTUALIZACIÓN COMPLETADA                        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📊 Resumen:" -ForegroundColor Cyan
Write-Host "   ✓ Archivos modificados: $archivosModificados" -ForegroundColor Green
if ($errores -gt 0) {
    Write-Host "   ✗ Errores encontrados: $errores" -ForegroundColor Red
}
Write-Host "   🌐 URL configurada: $BackendUrl" -ForegroundColor White

Write-Host "`n📋 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Verifica que ngrok esté corriendo en el backend (puerto 5000)" -ForegroundColor White
Write-Host "   2. Verifica que ngrok esté corriendo en el frontend (puerto 8000)" -ForegroundColor White
Write-Host "   3. Comparte la URL del frontend con tus usuarios de prueba" -ForegroundColor White

Write-Host "`n🔄 Para revertir los cambios:" -ForegroundColor Yellow
Write-Host "   .\configurar_ngrok_completo.ps1 -Revertir" -ForegroundColor Gray

Write-Host "`n🔍 Para verificar las URLs actuales:" -ForegroundColor Yellow
Write-Host "   .\configurar_ngrok_completo.ps1 -VerificarSolamente" -ForegroundColor Gray

Write-Host "`n✅ ¡Todo listo para las pruebas!`n" -ForegroundColor Green
