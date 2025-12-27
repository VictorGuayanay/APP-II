# Script para agregar header ngrok-skip-browser-warning a todas las peticiones AJAX
# Esto evita que ngrok muestre la página de advertencia en peticiones AJAX

Write-Host "Agregando header 'ngrok-skip-browser-warning' a archivos HTML..." -ForegroundColor Cyan

$archivosHTML = Get-ChildItem -Path "frontend" -Filter *.html -Recurse

$contador = 0

foreach ($archivo in $archivosHTML) {
    $contenido = Get-Content $archivo.FullName -Raw -Encoding UTF8
    $contenidoOriginal = $contenido
    
    # Patrón 1: headers: { 'Authorization':
    $contenido = $contenido -replace "headers:\s*\{\s*'Authorization':", "headers: { 'ngrok-skip-browser-warning': 'true', 'Authorization':"
    
    # Patrón 2: headers: { "Authorization":
    $contenido = $contenido -replace 'headers:\s*\{\s*"Authorization":', 'headers: { "ngrok-skip-browser-warning": "true", "Authorization":'
    
    if ($contenido -ne $contenidoOriginal) {
        Set-Content $archivo.FullName $contenido -NoNewline -Encoding UTF8
        $contador++
        Write-Host "  ✓ Actualizado: $($archivo.Name)" -ForegroundColor Green
    }
}

Write-Host "`n✅ Proceso completado. $contador archivos actualizados." -ForegroundColor Green
Write-Host "`n📝 Ahora reinicia el frontend:" -ForegroundColor Yellow
Write-Host "   1. Ctrl+C en la terminal del frontend" -ForegroundColor White
Write-Host "   2. python -m http.server 8000" -ForegroundColor White
Write-Host "   3. Recarga la aplicación en el navegador" -ForegroundColor White
