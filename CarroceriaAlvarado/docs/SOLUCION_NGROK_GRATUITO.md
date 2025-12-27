# 🔧 Solución: Exponer Múltiples Puertos con ngrok Gratuito

## ❌ El Problema

La versión gratuita de ngrok **solo permite 1 agente simultáneo**, por lo que no puedes ejecutar:
- `ngrok http 5000` en una terminal
- `ngrok http 8000` en otra terminal

**Error:** `ERR_NGROK_108 - Your account is limited to 1 simultaneous ngrok agent sessions`

---

## ✅ La Solución

Usar **UN SOLO agente de ngrok** que exponga **AMBOS puertos** usando un archivo de configuración.

---

## 🚀 Pasos para Implementar

### Paso 1: Actualizar el Archivo de Configuración

Ya se ha creado el archivo `ngrok.yml` en la raíz del proyecto. Ahora necesitas:

1. **Abre el archivo:** `ngrok.yml`
2. **Reemplaza** `TU_TOKEN_AQUI` con tu authtoken real de ngrok
3. **Guarda** el archivo

**Ejemplo:**
```yaml
version: "2"
authtoken: 2abc123def456ghi789jkl  # Tu token real aquí

tunnels:
  backend:
    proto: http
    addr: 5000
    host_header: "localhost:5000"
  
  frontend:
    proto: http
    addr: 8000
    host_header: "localhost:8000"
```

---

### Paso 2: Ejecutar ngrok con el Archivo de Configuración

**Cierra** cualquier instancia de ngrok que tengas corriendo, luego:

```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
ngrok start --all --config ngrok.yml
```

O si ngrok está en `C:\ngrok\`:

```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
C:\ngrok\ngrok.exe start --all --config ngrok.yml
```

---

### Paso 3: Copiar las URLs

Verás algo como esto:

```
ngrok

Session Status                online
Account                       tu_email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040

Forwarding                    https://abc123-backend.ngrok-free.app -> http://localhost:5000
Forwarding                    https://xyz789-frontend.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

📝 **Copia ambas URLs:**
- **Backend:** `https://abc123-backend.ngrok-free.app`
- **Frontend:** `https://xyz789-frontend.ngrok-free.app`

---

### Paso 4: Actualizar la Configuración del Sistema

```powershell
.\configurar_ngrok_completo.ps1 -BackendUrl "https://abc123-backend.ngrok-free.app"
```

> ⚠️ Usa la URL del **backend** (puerto 5000)

---

### Paso 5: Compartir con Usuarios

Comparte la URL del **frontend** (puerto 8000) con tus usuarios:

```
https://xyz789-frontend.ngrok-free.app
```

---

## 📊 Comparación de Métodos

### ❌ Método Anterior (No funciona con cuenta gratuita)
```powershell
# Terminal 1
ngrok http 5000 --host-header="localhost:5000"

# Terminal 2 (ERROR!)
ngrok http 8000 --host-header="localhost:8000"
```

### ✅ Método Nuevo (Funciona con cuenta gratuita)
```powershell
# Una sola terminal
ngrok start --all --config ngrok.yml
```

---

## 🎯 Ventajas del Nuevo Método

1. ✅ **Funciona con cuenta gratuita** - Solo usa 1 agente
2. ✅ **Más simple** - Solo una terminal en lugar de dos
3. ✅ **Más organizado** - Configuración en un archivo
4. ✅ **Reutilizable** - Guarda tu configuración

---

## 🔍 Verificar que Funciona

### Opción 1: Interfaz Web de ngrok
Abre en tu navegador: `http://localhost:4040`

Deberías ver **2 túneles activos**:
- `backend` → `http://localhost:5000`
- `frontend` → `http://localhost:8000`

### Opción 2: Probar las URLs
1. Abre la URL del backend en tu navegador
2. Deberías ver la respuesta de tu API Flask
3. Abre la URL del frontend
4. Deberías ver tu página de login

---

## 🐛 Solución de Problemas

### Error: "authtoken not found"
**Solución:** Verifica que reemplazaste `TU_TOKEN_AQUI` en `ngrok.yml`

### Error: "config file not found"
**Solución:** Asegúrate de estar en la carpeta correcta:
```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
```

### Error: "port already in use"
**Solución:** Verifica que tu backend y frontend estén corriendo:
- Backend: `http://localhost:5000`
- Frontend: `http://localhost:8000`

### Solo veo 1 túnel en lugar de 2
**Solución:** Verifica que el archivo `ngrok.yml` tenga la sintaxis correcta (espacios, no tabs)

---

## 📝 Comandos Completos

### 1. Detener ngrok anterior (si está corriendo)
```powershell
# Presiona Ctrl+C en la terminal de ngrok
```

### 2. Iniciar ngrok con configuración
```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
C:\ngrok\ngrok.exe start --all --config ngrok.yml
```

### 3. Actualizar sistema
```powershell
# En otra terminal
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
.\configurar_ngrok_completo.ps1 -BackendUrl "https://TU-URL-BACKEND.ngrok-free.app"
```

### 4. Verificar
```powershell
.\configurar_ngrok_completo.ps1 -VerificarSolamente
```

---

## 🎉 Resumen

**Antes:**
- ❌ 2 terminales de ngrok
- ❌ Error ERR_NGROK_108
- ❌ No funciona con cuenta gratuita

**Ahora:**
- ✅ 1 terminal de ngrok
- ✅ 2 túneles simultáneos
- ✅ Funciona con cuenta gratuita

---

## 📚 Documentación Oficial

Para más información sobre configuración de ngrok:
- https://ngrok.com/docs/agent/config/
- https://ngrok.com/docs/errors/err_ngrok_108

---

**¡Ahora sí puedes exponer ambos servicios con la cuenta gratuita! 🚀**
