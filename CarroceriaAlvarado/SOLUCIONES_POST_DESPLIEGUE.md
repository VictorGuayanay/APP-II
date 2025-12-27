# 🔧 Soluciones Post-Despliegue

## 1️⃣ Problema: Solo funciona en modo incógnito

**Causa:** Caché del navegador con URLs antiguas

**Solución:**
```
Chrome: Ctrl + Shift + Delete → Borrar "Imágenes y archivos en caché"
Firefox: Ctrl + Shift + Delete → Borrar "Caché"
```

Después de limpiar el caché, funcionará en modo normal.

---

## 2️⃣ Problema: ñ y tildes aparecen como �

**Causa:** Python's `http.server` no envía headers UTF-8 correctamente

**Solución:** Usar el servidor UTF-8 mejorado

### Paso 1: Detener el servidor actual
Terminal del frontend → `Ctrl + C`

### Paso 2: Usar el nuevo servidor
```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\frontend
python server_utf8.py
```

Este servidor envía los headers UTF-8 correctos para HTML, CSS y JS.

---

## 3️⃣ Problema: Tablas vacías (sin registros)

**Causa:** Base de datos sin datos de prueba

**Soluciones:**

### Opción A: Crear datos manualmente
Los usuarios pueden usar los botones "+ Agregar":
- **Categorías:** Botón "+ Agregar Categoría"
- **Empleados:** Ir a "Ingreso Empleados"
- **Clientes:** Ir a "Ingreso Clientes"
- **Órdenes:** Ir a "Órdenes de Trabajo"

### Opción B: Insertar datos de prueba en la BD
Si quieres que los usuarios vean datos desde el inicio, puedes insertar registros de prueba en SQL Server.

**Ejemplo para Categorías:**
```sql
USE CarroceriaAlvaradoDB;

INSERT INTO Categorias_Materiales (codigo_prefijo, nombre, descripcion, estado)
VALUES 
    ('PIN', 'Pintura', 'Materiales de pintura y acabados', 1),
    ('MEC', 'Mecánica', 'Repuestos y herramientas mecánicas', 1),
    ('ELE', 'Eléctrica', 'Componentes eléctricos', 1),
    ('CAR', 'Carrocería', 'Piezas de carrocería', 1);
```

---

## 🚀 Pasos Recomendados

### 1. Reiniciar frontend con servidor UTF-8
```powershell
# Detener servidor actual (Ctrl+C)
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\frontend
python server_utf8.py
```

### 2. Limpiar caché del navegador
- Chrome: `Ctrl + Shift + Delete`
- Seleccionar "Imágenes y archivos en caché"
- Borrar datos

### 3. Probar de nuevo
- Abrir: `https://d28e6c933c44.ngrok-free.app`
- Las ñ y tildes deberían verse correctamente

### 4. Crear datos de prueba (opcional)
- Usar los botones "+ Agregar" en cada módulo
- O insertar datos directamente en SQL Server

---

## 📝 Nota sobre ngrok

Recuerda que las URLs de ngrok **cambian cada vez que reinicias ngrok** (versión gratuita). Si reinicias ngrok:

1. Copia las nuevas URLs
2. Ejecuta: `.\actualizar_urls.ps1 -BackendUrl "NUEVA_URL_BACKEND"`
3. Reinicia el frontend

---

**¡Reinicia el frontend con `server_utf8.py` y las ñ y tildes funcionarán! 🎉**
