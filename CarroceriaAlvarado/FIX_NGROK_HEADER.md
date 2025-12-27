# 🔧 Solución: Bypass de Advertencia de ngrok

## Problema
ngrok muestra página de advertencia en peticiones AJAX, bloqueando el acceso a los datos.

## ✅ Solución Rápida: Agregar Header

Agrega este header a todas las peticiones AJAX:

```javascript
headers: {
    'ngrok-skip-browser-warning': 'true',
    'Authorization': 'Bearer ' + token
}
```

### Ejemplo en ver_inventario.html:

```javascript
$.ajax({
    url: 'https://553682876eea.ngrok-free.app/materiales',
    method: 'GET',
    headers: {
        'ngrok-skip-browser-warning': 'true',  // ← AGREGAR ESTO
        'Authorization': 'Bearer ' + token
    },
    success: function(materiales) {
        // ...
    }
});
```

## 🔄 Aplicar a Todos los Archivos

Ejecuta este script PowerShell para agregar el header automáticamente:

```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado

# Buscar y reemplazar en todos los HTML
$files = Get-ChildItem -Path frontend -Filter *.html -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    
    # Reemplazar headers con Authorization por headers con ngrok-skip
    $content = $content -replace "headers: \{\s*'Authorization':", "headers: { 'ngrok-skip-browser-warning': 'true', 'Authorization':"
    
    Set-Content $file.FullName $content -NoNewline
}

Write-Host "Headers actualizados en archivos HTML"
```

## ⚠️ Nota

Este header solo funciona con ngrok. Si cambias a otro servicio de túnel, deberás removerlo.

---

**Ejecuta el script PowerShell para aplicar el fix automáticamente. 🚀**
