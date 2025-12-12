# Script para ejecutar el SQL de agregar costo_hora a Empleados
# Ejecuta el script SQL en SQL Server

$serverInstance = "DESKTOP-OJ81G31\SQLEXPRESS"
$database = "CarroceriaAlvaradoDB"
$sqlFile = "add_costo_hora_to_empleados.sql"

Write-Host "Ejecutando script SQL: $sqlFile" -ForegroundColor Cyan
Write-Host "Servidor: $serverInstance" -ForegroundColor Cyan
Write-Host "Base de datos: $database" -ForegroundColor Cyan
Write-Host ""

try {
    # Ejecutar el script SQL usando sqlcmd
    sqlcmd -S $serverInstance -d $database -i $sqlFile -E
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Script ejecutado exitosamente!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "✗ Error al ejecutar el script (código: $LASTEXITCODE)" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "✗ Error: $_" -ForegroundColor Red
}
