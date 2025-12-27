# 📝 Lista de Archivos con URLs del Backend

Este documento lista todos los archivos HTML que contienen referencias a `http://127.0.0.1:5000` y que necesitarían ser actualizados si NO se usa el archivo `config.js`.

## ⚠️ IMPORTANTE

**Actualmente, el sistema usa URLs hardcodeadas en cada archivo HTML.**

Para facilitar el despliegue con ngrok, se ha creado:
- ✅ `frontend/js/config.js` - Archivo de configuración centralizado
- ✅ `configurar_ngrok.ps1` - Script para actualizar automáticamente

## 📋 Archivos que Contienen URLs del Backend

### Módulo: Órdenes de Trabajo
1. **listar_ordenes_trabajo.html**
   - Línea 147: GET `/ordenes-trabajo`
   - Línea 325: GET `/ordenes-trabajo/{id}/calcular-recursos`
   - Línea 357: GET `/ordenes-trabajo/{id}`

2. **orden_trabajo.html**
   - Línea 230: GET `/clientes`
   - Línea 259: GET `/empleados`
   - Línea 304: GET `/proveedores`
   - Línea 334: GET `/proveedores/{id}/materiales`
   - Línea 537: POST `/ordenes-trabajo`

3. **editar_orden.html**
   - Línea 255: GET `/clientes`
   - Línea 278: GET `/empleados`
   - Línea 324: GET `/empleados/disponibles`
   - Línea 435: GET `/proveedores`
   - Línea 465: GET `/proveedores/{id}/materiales`
   - Línea 618: PUT `/ordenes-trabajo/{id}`
   - Línea 654: GET `/ordenes-trabajo/{id}`

4. **detalle_orden.html**
   - Línea 404: Definición de `API_BASE_URL`
   - Línea 424: GET `/empleados`
   - Línea 451: GET `/materiales`
   - (Múltiples referencias más usando `API_BASE_URL`)

### Módulo: Inventario
5. **ver_inventario.html**
   - Línea 310: GET `/materiales`
   - Línea 593: GET `/proveedores`
   - Línea 616: GET `/categorias-materiales`
   - Línea 686: GET `/materiales/{id}`
   - Línea 776: PUT `/materiales/{id}`
   - Línea 816: GET `/configuraciones`
   - Línea 889: DELETE `/materiales/{id}`

6. **anadir_material.html**
   - (Verificar si tiene referencias)

7. **entradas_salidas_inventario.html**
   - Línea 160: GET `/materiales`
   - Línea 249: GET `/unidades`
   - Línea 331: POST `/inventory/entry`
   - Línea 381: POST `/inventory/exit`

### Módulo: Empleados
8. **ver_empleados.html**
   - Línea 182: GET `/empleados`
   - Línea 233: POST `/empleados`
   - Línea 281: GET `/empleados/{id}`
   - Línea 310: PUT `/empleados/{id}`

9. **ingresar_empleado.html**
   - Línea 162: POST `/empleados`

### Módulo: Clientes
10. **ingresar_cliente.html**
    - Línea 134: POST `/clientes`

### Módulo: Proveedores
11. **ver_proveedores.html**
    - Línea 197: GET `/proveedores`
    - Línea 286: GET `/proveedores/{id}`
    - Línea 323: PUT `/proveedores/{id}`
    - Línea 364: DELETE `/proveedores/{id}`

12. **ingresar_proveedor.html**
    - Línea 167: POST `/proveedores`

### Módulo: Comprobantes
13. **consultar_comprobantes.html**
    - (Verificar si tiene referencias)

### Módulo: Reportes
14. **reportes.html**
    - Línea 159: GET `/materiales`
    - Línea 173: GET `/empleados`
    - Línea 256: GET `/reportes/uso-materiales`

### Módulo: Dashboard
15. **vision_general.html**
    - Línea 134: GET `/dashboard/overview`

### Módulo: Categorías
16. **gestion_categorias.html**
    - Línea 214: GET `/categorias-materiales`
    - Línea 289: POST `/categorias-materiales`
    - Línea 313: GET `/categorias-materiales`
    - Línea 350: PUT `/categorias-materiales/{id}`
    - Línea 377: DELETE `/categorias-materiales/{id}`

### Autenticación
17. **registrer.html**
    - Línea 174: POST `/registro`

18. **index.html** (Login)
    - (Verificar si tiene referencias)

---

## 🔧 Soluciones para el Despliegue

### OPCIÓN 1: Usar config.js (Recomendado) ✨

**Ventajas:**
- ✅ Solo necesitas actualizar UN archivo
- ✅ Fácil de revertir
- ✅ Script automático disponible

**Pasos:**
1. Incluir `<script src="js/config.js"></script>` en cada HTML
2. Reemplazar todas las URLs hardcodeadas por `window.CONFIG.API_BASE_URL`
3. Usar el script `configurar_ngrok.ps1` para actualizar

**Estado actual:** ❌ NO implementado (requiere modificar todos los archivos HTML)

---

### OPCIÓN 2: Script de Reemplazo Masivo

**Ventajas:**
- ✅ No requiere modificar la estructura del código
- ✅ Rápido de implementar

**Desventajas:**
- ❌ Necesitas ejecutar el script cada vez
- ❌ Más propenso a errores

**Implementación:**
El script `configurar_ngrok.ps1` ya está disponible y funciona con `config.js`.

---

### OPCIÓN 3: Variable de Entorno (Avanzado)

**Ventajas:**
- ✅ Más profesional
- ✅ Fácil de configurar en diferentes entornos

**Desventajas:**
- ❌ Requiere cambiar la arquitectura del frontend
- ❌ Más complejo de implementar

---

## 📝 Recomendación Actual

Para el despliegue inmediato con ngrok:

1. **Usa el archivo `config.js` que ya está creado**
2. **Ejecuta el script `configurar_ngrok.ps1`** con tu URL de ngrok
3. **Verifica que el cambio se aplicó** en `frontend/js/config.js`

**Comando:**
```powershell
.\configurar_ngrok.ps1 -BackendUrl "https://tu-url-de-ngrok.app"
```

**Para revertir:**
```powershell
.\configurar_ngrok.ps1 -Revertir
```

---

## 🔮 Mejora Futura Recomendada

Para facilitar futuros despliegues, considera:

1. **Refactorizar todos los archivos HTML** para usar `window.CONFIG.API_BASE_URL`
2. **Crear un archivo `api.js`** con funciones helper para todas las peticiones
3. **Implementar un sistema de build** (webpack, vite) que maneje variables de entorno

Esto haría el sistema más mantenible y fácil de desplegar en diferentes entornos.

---

## ✅ Checklist de Archivos Actualizados

Marca los archivos que ya usan `window.CONFIG.API_BASE_URL`:

- [ ] listar_ordenes_trabajo.html
- [ ] orden_trabajo.html
- [ ] editar_orden.html
- [ ] detalle_orden.html
- [ ] ver_inventario.html
- [ ] anadir_material.html
- [ ] entradas_salidas_inventario.html
- [ ] ver_empleados.html
- [ ] ingresar_empleado.html
- [ ] ingresar_cliente.html
- [ ] ver_proveedores.html
- [ ] ingresar_proveedor.html
- [ ] consultar_comprobantes.html
- [ ] reportes.html
- [ ] vision_general.html
- [ ] gestion_categorias.html
- [ ] registrer.html
- [ ] index.html

**Estado actual:** 0/18 archivos actualizados

---

**Última actualización:** 2025-12-15
