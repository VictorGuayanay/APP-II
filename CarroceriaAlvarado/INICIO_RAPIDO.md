# ⚡ Inicio Rápido - Despliegue con ngrok (Cuenta Gratuita)

## 🎯 Solución para Cuenta Gratuita

La cuenta gratuita de ngrok **solo permite 1 agente simultáneo**, pero podemos exponer **ambos puertos** (5000 y 8000) usando **un solo agente** con archivo de configuración.

---

## 🚀 3 Pasos Rápidos

### 1️⃣ Configurar ngrok.yml

**Opción A: Script Automático** ⭐ **Recomendado**
```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
.\configurar_token_ngrok.ps1
```
El script te pedirá tu authtoken.

**Opción B: Manual**
1. Abre `ngrok.yml`
2. Reemplaza `TU_TOKEN_AQUI` con tu authtoken real
3. Guarda el archivo

---

### 2️⃣ Iniciar ngrok (1 sola terminal)

```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
C:\ngrok\ngrok.exe start --all --config ngrok.yml
```

**Resultado esperado:**
```
Forwarding    https://abc123.ngrok-free.app -> http://localhost:5000
Forwarding    https://xyz789.ngrok-free.app -> http://localhost:8000
```

📝 **Copia ambas URLs**

---

### 3️⃣ Actualizar Sistema

```powershell
# En otra terminal
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
.\configurar_ngrok_completo.ps1 -BackendUrl "https://abc123.ngrok-free.app"
```

> ⚠️ Usa la URL del **backend** (puerto 5000)

---

## 📤 Compartir con Usuarios

Envía a tus usuarios la URL del **frontend** (puerto 8000):
```
https://xyz789.ngrok-free.app
```

---

## 🔍 Verificar que Funciona

Abre en tu navegador: `http://localhost:4040`

Deberías ver **2 túneles activos**:
- `backend` → puerto 5000
- `frontend` → puerto 8000

---

## 🛑 Detener y Revertir

```powershell
# 1. Detener ngrok (Ctrl+C en la terminal de ngrok)

# 2. Revertir configuración
.\configurar_ngrok_completo.ps1 -Revertir
```

---

## 📋 Checklist Completo

### Antes de Empezar
- [ ] Backend corriendo: `python app.py` (puerto 5000)
- [ ] Frontend corriendo: `python -m http.server 8000` (puerto 8000)
- [ ] ngrok instalado en `C:\ngrok\`
- [ ] Authtoken de ngrok obtenido

### Configuración
- [ ] Ejecutar `.\configurar_token_ngrok.ps1` (o editar `ngrok.yml` manualmente)
- [ ] Verificar que `ngrok.yml` tiene tu authtoken real

### Despliegue
- [ ] Ejecutar `ngrok start --all --config ngrok.yml`
- [ ] Copiar URL del backend (puerto 5000)
- [ ] Copiar URL del frontend (puerto 8000)
- [ ] Ejecutar `.\configurar_ngrok_completo.ps1 -BackendUrl "URL_BACKEND"`
- [ ] Verificar en `http://localhost:4040`

### Compartir
- [ ] Enviar URL del frontend a usuarios
- [ ] Enviar formulario de feedback
- [ ] Monitorear peticiones en `localhost:4040`

### Finalizar
- [ ] Detener ngrok (Ctrl+C)
- [ ] Revertir configuración

---

## 🐛 Problemas Comunes

### Error: "ERR_NGROK_108"
**Causa:** Intentaste ejecutar 2 instancias de ngrok  
**Solución:** Usa el archivo de configuración con `start --all`

### Error: "authtoken not found"
**Causa:** No configuraste el authtoken en `ngrok.yml`  
**Solución:** Ejecuta `.\configurar_token_ngrok.ps1`

### Solo veo 1 túnel
**Causa:** Error en la sintaxis de `ngrok.yml`  
**Solución:** Verifica que uses espacios (no tabs) y la sintaxis correcta

### "Failed to fetch"
**Causa:** URLs no actualizadas en el sistema  
**Solución:** Ejecuta `.\configurar_ngrok_completo.ps1 -BackendUrl "URL"`

---

## 📚 Documentación Completa

- **Solución detallada:** `docs/SOLUCION_NGROK_GRATUITO.md`
- **Guía completa:** `docs/DESPLIEGUE_NGROK.md`
- **Flujo de trabajo:** `FLUJO_TRABAJO.md`

---

## 💡 Comandos para Copiar

```powershell
# 1. Configurar token
.\configurar_token_ngrok.ps1

# 2. Iniciar ngrok
C:\ngrok\ngrok.exe start --all --config ngrok.yml

# 3. Actualizar sistema (en otra terminal)
.\configurar_ngrok_completo.ps1 -BackendUrl "https://TU-URL-BACKEND.ngrok-free.app"

# 4. Verificar
.\configurar_ngrok_completo.ps1 -VerificarSolamente

# 5. Revertir al finalizar
.\configurar_ngrok_completo.ps1 -Revertir
```

---

**¡Listo en 3 pasos! 🎉**
