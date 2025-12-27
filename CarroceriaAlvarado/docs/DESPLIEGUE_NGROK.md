# 🚀 Instrucciones Completas de Despliegue con ngrok
## Sistema Carrocería Alvarado

---

## 📦 Preparación Inicial

### Estado Actual del Sistema
✅ Backend corriendo en: `http://localhost:5000`  
✅ Frontend corriendo en: `http://localhost:8000`  
✅ Archivo de configuración creado: `frontend/js/config.js`

---

## 🔧 PASO 1: Instalar y Configurar ngrok

### 1.1 Descargar ngrok
1. Ve a: https://ngrok.com/download
2. Descarga la versión para Windows
3. Extrae `ngrok.exe` en una carpeta (recomendado: `C:\ngrok\`)

### 1.2 Crear Cuenta y Obtener Token
1. Regístrate en: https://dashboard.ngrok.com/signup
2. Inicia sesión y copia tu **Authtoken**
3. Abre PowerShell y ejecuta:
   ```powershell
   cd C:\ngrok
   .\ngrok config add-authtoken TU_TOKEN_AQUI
   ```

---

## 🌐 PASO 2: Exponer los Servicios con ngrok

### 2.1 Exponer el Backend (Puerto 5000)

**Abre una NUEVA terminal PowerShell** y ejecuta:

```powershell
cd C:\ngrok
.\ngrok http 5000 --host-header="localhost:5000"
```

**Resultado esperado:**
```
Forwarding    https://abc123-xyz.ngrok-free.app -> http://localhost:5000
```

📝 **IMPORTANTE:** Copia la URL completa (ejemplo: `https://abc123-xyz.ngrok-free.app`)

⚠️ **DEJA ESTA TERMINAL ABIERTA** - Si la cierras, el túnel se desconectará

---

### 2.2 Exponer el Frontend (Puerto 8000)

**Abre OTRA terminal PowerShell** (nueva ventana) y ejecuta:

```powershell
cd C:\ngrok
.\ngrok http 8000 --host-header="localhost:8000"
```

**Resultado esperado:**
```
Forwarding    https://def456-uvw.ngrok-free.app -> http://localhost:8000
```

📝 **IMPORTANTE:** Copia esta URL también (ejemplo: `https://def456-uvw.ngrok-free.app`)

⚠️ **DEJA ESTA TERMINAL ABIERTA** también

---

## ⚙️ PASO 3: Configurar el Frontend

Tienes **DOS OPCIONES** para actualizar la configuración:

### OPCIÓN A: Usar el Script Automático (Recomendado) ✨

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
.\configurar_ngrok.ps1 -BackendUrl "https://abc123-xyz.ngrok-free.app"
```

> ⚠️ Reemplaza `https://abc123-xyz.ngrok-free.app` con TU URL real de ngrok del backend

---

### OPCIÓN B: Editar Manualmente

1. Abre el archivo: `frontend/js/config.js`
2. Busca la línea:
   ```javascript
   const API_BASE_URL = 'http://127.0.0.1:5000';
   ```
3. Cámbiala por:
   ```javascript
   const API_BASE_URL = 'https://abc123-xyz.ngrok-free.app';
   ```
   > ⚠️ Usa TU URL de ngrok del backend (sin barra final)

4. Guarda el archivo

---

## 📤 PASO 4: Compartir con Usuarios de Prueba

### 4.1 Información para Compartir

Envía a tus usuarios el siguiente mensaje:

```
🔗 URL del Sistema: https://def456-uvw.ngrok-free.app

📋 Instrucciones de Acceso:
1. Abre el enlace en tu navegador (Chrome, Firefox o Edge)
2. Verás una pantalla de advertencia de ngrok
3. Haz clic en el botón "Visit Site"
4. Ya puedes usar el sistema

⚠️ Nota: La pantalla de advertencia es normal y segura.
```

### 4.2 Credenciales de Prueba
Proporciona las credenciales que tengas configuradas en tu sistema.

---

## 🧪 PASO 5: Funcionalidades para Probar

Comparte esta lista de verificación con tus usuarios:

### ✅ Módulo: Órdenes de Trabajo
- [ ] Ver listado de órdenes de trabajo
- [ ] Crear nueva orden de trabajo
- [ ] Editar orden existente
- [ ] Ver detalles completos de una orden
- [ ] Calcular recursos necesarios
- [ ] Imprimir PDF de la orden
- [ ] Verificar que órdenes "Finalizadas" aparecen con fondo verde

### ✅ Módulo: Inventario
- [ ] Ver listado de materiales
- [ ] Añadir nuevo material
- [ ] Editar material existente
- [ ] Verificar que se muestran las unidades de medida
- [ ] Registrar entrada de inventario
- [ ] Registrar salida de inventario

### ✅ Módulo: Empleados
- [ ] Ver listado de empleados
- [ ] Ingresar nuevo empleado
- [ ] Editar información de empleado

### ✅ Módulo: Clientes y Proveedores
- [ ] Ingresar nuevo cliente
- [ ] Ver listado de proveedores
- [ ] Ingresar nuevo proveedor
- [ ] Editar proveedor

### ✅ Módulo: Comprobantes
- [ ] Consultar comprobantes
- [ ] Generar PDF de comprobante
- [ ] Verificar que el PDF incluye "DOCUMENTO SIN VALOR TRIBUTARIO"

### ✅ Navegación y UI
- [ ] Menú lateral se abre/cierra correctamente
- [ ] Submenús se expanden al hacer clic
- [ ] La página activa se resalta en azul
- [ ] Todos los botones responden correctamente

---

## 📊 PASO 6: Monitorear las Pruebas

### 6.1 Interfaz de Inspección de ngrok

Mientras los usuarios prueban, puedes monitorear todas las peticiones:

1. Abre tu navegador
2. Ve a: `http://localhost:4040`
3. Verás en tiempo real:
   - Todas las peticiones HTTP
   - Códigos de respuesta
   - Tiempos de respuesta
   - Errores (si los hay)

### 6.2 Logs del Backend

Revisa la terminal donde corre `python app.py` para ver:
- Peticiones recibidas
- Errores del servidor
- Consultas a la base de datos

---

## 📝 PASO 7: Recopilar Feedback

### 7.1 Formulario de Feedback

Crea un documento compartido (Google Docs, Excel, etc.) con estas secciones:

**1. Información del Usuario**
- Nombre:
- Fecha de prueba:
- Navegador usado:

**2. Funcionalidades Probadas**
- Lista de funcionalidades que probó
- ✅ Funcionó correctamente
- ❌ Tuvo problemas

**3. Errores Encontrados**
- Descripción del error:
- Pasos para reproducirlo:
- Captura de pantalla (si es posible):

**4. Sugerencias de Mejora**
- ¿Qué mejorarías?
- ¿Qué funcionalidad falta?
- ¿Qué te confundió?

**5. Calificación General**
- Facilidad de uso: ⭐⭐⭐⭐⭐
- Diseño visual: ⭐⭐⭐⭐⭐
- Velocidad: ⭐⭐⭐⭐⭐

---

## 🛑 PASO 8: Finalizar las Pruebas

### 8.1 Detener ngrok

Cuando termines las pruebas:

1. Ve a cada terminal de ngrok
2. Presiona `Ctrl + C`
3. Confirma que se detuvo

### 8.2 Revertir Configuración

**OPCIÓN A: Usar el Script**
```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
.\configurar_ngrok.ps1 -Revertir
```

**OPCIÓN B: Manual**
1. Abre `frontend/js/config.js`
2. Cambia de vuelta a:
   ```javascript
   const API_BASE_URL = 'http://127.0.0.1:5000';
   ```

---

## 🐛 Solución de Problemas

### Problema 1: "ERR_NGROK_3200"
**Causa:** Token no configurado o inválido  
**Solución:**
```powershell
ngrok config add-authtoken TU_TOKEN_AQUI
```

---

### Problema 2: CORS Errors en el Navegador
**Causa:** El backend no permite peticiones desde la URL de ngrok  
**Solución:** Verifica que `backend/app.py` tenga:
```python
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}})
```

---

### Problema 3: "This site can't be reached"
**Causa:** El servidor local no está corriendo o ngrok apunta al puerto incorrecto  
**Solución:**
1. Verifica que el backend esté corriendo: `python app.py`
2. Verifica que el frontend esté corriendo: `python -m http.server 8000`
3. Verifica que ngrok apunte a los puertos correctos (5000 y 8000)

---

### Problema 4: Los cambios no se reflejan
**Causa:** Caché del navegador  
**Solución:**
1. Presiona `Ctrl + Shift + R` para recargar sin caché
2. O abre en modo incógnito

---

### Problema 5: "Failed to fetch" en las peticiones
**Causa:** La URL del backend no está actualizada en config.js  
**Solución:**
1. Verifica que `frontend/js/config.js` tenga la URL correcta de ngrok
2. Recarga la página con `Ctrl + Shift + R`

---

### Problema 6: Pantalla de advertencia de ngrok no desaparece
**Causa:** Es el comportamiento normal de la versión gratuita  
**Solución:** Los usuarios deben hacer clic en "Visit Site" cada vez

---

## 💡 Limitaciones de la Versión Gratuita

⚠️ **URLs Temporales**
- Las URLs cambian cada vez que reinicias ngrok
- Necesitarás actualizar `config.js` cada vez

⚠️ **Pantalla de Advertencia**
- Los usuarios verán una advertencia antes de acceder
- Deben hacer clic en "Visit Site"

⚠️ **Límites de Conexión**
- Máximo 40 conexiones por minuto
- Suficiente para pruebas pequeñas

⚠️ **Sin Dominios Personalizados**
- No puedes usar tu propio dominio

---

## 💰 Upgrade a ngrok de Pago (Opcional)

Si necesitas:
- ✅ URLs fijas que no cambien
- ✅ Sin pantalla de advertencia
- ✅ Más conexiones simultáneas
- ✅ Dominios personalizados

**Planes disponibles:**
- **Basic:** $8/mes - URLs fijas, sin advertencias
- **Pro:** $20/mes - Más conexiones, dominios personalizados
- **Enterprise:** Contactar ventas

---

## 📞 Contacto y Soporte

Si tienes problemas durante el despliegue:

1. **Revisa los logs:**
   - Terminal del backend
   - Terminal del frontend
   - Interfaz de ngrok: http://localhost:4040

2. **Verifica la configuración:**
   - `frontend/js/config.js` tiene la URL correcta
   - ngrok está corriendo en ambos puertos
   - Los servidores locales están activos

3. **Documentación oficial:**
   - ngrok: https://ngrok.com/docs
   - Flask CORS: https://flask-cors.readthedocs.io/

---

## ✅ Checklist Final

Antes de compartir con usuarios, verifica:

- [ ] Backend corriendo en localhost:5000
- [ ] Frontend corriendo en localhost:8000
- [ ] ngrok instalado y configurado con authtoken
- [ ] ngrok exponiendo backend (puerto 5000) - Terminal 1 abierta
- [ ] ngrok exponiendo frontend (puerto 8000) - Terminal 2 abierta
- [ ] `frontend/js/config.js` actualizado con URL de ngrok del backend
- [ ] URLs de ngrok anotadas (backend y frontend)
- [ ] Instrucciones enviadas a usuarios de prueba
- [ ] Formulario de feedback preparado
- [ ] Interfaz de monitoreo abierta: http://localhost:4040

---

## 🎉 ¡Listo para Recibir Feedback!

Una vez completados todos los pasos, tu sistema estará accesible desde cualquier lugar para que los usuarios finales lo prueben.

**Recuerda:**
- Mantén las terminales de ngrok abiertas durante las pruebas
- Monitorea las peticiones en http://localhost:4040
- Recopila todo el feedback de los usuarios
- Revierte los cambios cuando termines

**¡Buena suerte con las pruebas! 🚀**
