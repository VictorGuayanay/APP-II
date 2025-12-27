# Script Simple para Actualizar URLs de ngrok
param(
    [Parameter(Mandatory = $true)]
    [string]$BackendUrl,
    
    [Parameter(Mandatory = $false)]
    [switch]$Revertir
)

$frontendDir = "frontend"
$localUrl = "http://127.0.0.1:5000"

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

if ($Revertir) {
    Write-Host "Revirtiendo a URL local..." -ForegroundColor Yellow
    $urlNueva = $localUrl
}
else {
    $urlNueva = $BackendUrl.TrimEnd('/')
}

$archivosModificados = 0

foreach ($archivo in $archivosHTML) {
    $rutaCompleta = Join-Path $frontendDir $archivo
    
    if (Test-Path $rutaCompleta) {
        try {
            $contenido = Get-Content $rutaCompleta -Raw -Encoding UTF8
            
            if ($Revertir) {
                $contenidoNuevo = $contenido -replace 'https://[^"'']+\.ngrok[^"'']*\.app', $localUrl
            }
            else {
                $contenidoNuevo = $contenido -replace [regex]::Escape($localUrl), $urlNueva
            }
            
            if ($contenido -ne $contenidoNuevo) {
                Set-Content $rutaCompleta -Value $contenidoNuevo -Encoding UTF8 -NoNewline
                Write-Host "Actualizado: $archivo" -ForegroundColor Green
                $archivosModificados++
            }
        }
        catch {
            Write-Host "Error en: $archivo" -ForegroundColor Red
        }
    }
}

Write-Host "`nArchivos modificados: $archivosModificados" -ForegroundColor Cyan

if (-not $Revertir) {
    Write-Host "`nURL configurada: $urlNueva" -ForegroundColor Green
    Write-Host "Comparte con usuarios: La URL del frontend de ngrok" -ForegroundColor Yellow
}
