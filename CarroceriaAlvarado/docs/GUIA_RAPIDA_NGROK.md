# ⚡ Guía Rápida de Despliegue con ngrok

## 🎯 Pasos Rápidos (5 minutos)

### 1️⃣ Instalar ngrok
```powershell
# Descarga desde: https://ngrok.com/download
# Extrae ngrok.exe a C:\ngrok\
```

### 2️⃣ Configurar Token
```powershell
# Obtén tu token desde: https://dashboard.ngrok.com
ngrok config add-authtoken TU_TOKEN_AQUI
```

### 3️⃣ Exponer Backend (Terminal 1)
```powershell
cd C:\ngrok
.\ngrok http 5000 --host-header="localhost:5000"
```
📝 **Copia la URL del backend** (ejemplo: `https://abc123.ngrok-free.app`)

### 4️⃣ Exponer Frontend (Terminal 2)
```powershell
cd C:\ngrok
.\ngrok http 8000 --host-header="localhost:8000"
```
📝 **Copia la URL del frontend** (ejemplo: `https://xyz789.ngrok-free.app`)

### 5️⃣ Actualizar Configuración del Frontend

**Archivo:** `frontend/js/config.js`

```javascript
// CAMBIAR ESTA LÍNEA:
const API_BASE_URL = 'http://127.0.0.1:5000';

// POR TU URL DE NGROK DEL BACKEND:
const API_BASE_URL = 'https://abc123.ngrok-free.app';
```

### 6️⃣ Compartir con Usuarios

Envía a tus usuarios de prueba:
- **URL del Sistema:** `https://xyz789.ngrok-free.app`
- **Instrucción:** "Haz clic en 'Visit Site' cuando veas la advertencia de ngrok"

---

## 🔄 Para Detener el Despliegue

1. Presiona `Ctrl + C` en ambas terminales de ngrok
2. Revierte el cambio en `frontend/js/config.js`:
   ```javascript
   const API_BASE_URL = 'http://127.0.0.1:5000';
   ```

---

## 📋 Checklist de Funcionalidades para Probar

Comparte esta lista con tus usuarios de prueba:

### ✅ Órdenes de Trabajo
- [ ] Ver listado de órdenes
- [ ] Crear nueva orden
- [ ] Editar orden existente
- [ ] Ver detalles de orden
- [ ] Calcular recursos
- [ ] Imprimir PDF de orden
- [ ] Verificar que órdenes finalizadas aparecen en verde

### ✅ Inventario
- [ ] Ver materiales
- [ ] Añadir material
- [ ] Editar material
- [ ] Verificar unidades de medida

### ✅ Comprobantes
- [ ] Consultar comprobantes
- [ ] Generar PDF
- [ ] Verificar leyenda "SIN VALOR TRIBUTARIO"

### ✅ Navegación
- [ ] Menú lateral funciona
- [ ] Submenús se expanden
- [ ] Página activa resaltada en azul

---

## 🐛 Problemas Comunes

### "ERR_NGROK_3200"
```powershell
ngrok config add-authtoken TU_TOKEN_AQUI
```

### CORS Errors
Verifica que `backend/app.py` tenga:
```python
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}})
```

### Los cambios no se ven
- Limpia caché: `Ctrl + Shift + R`
- Verifica que actualizaste `config.js`

---

## 📊 Monitorear Peticiones

Abre en tu navegador: `http://localhost:4040`

Verás todas las peticiones HTTP en tiempo real.

---

## 💡 Notas Importantes

- ⚠️ Las URLs de ngrok cambian cada vez que lo reinicias (versión gratuita)
- ⚠️ Los usuarios verán una pantalla de advertencia (normal en versión gratuita)
- ⚠️ Límite de 40 conexiones/minuto en versión gratuita
- 💰 Para URLs fijas sin advertencias: Plan Basic ($8/mes)

---

**¡Todo listo para recibir feedback! 🚀**
