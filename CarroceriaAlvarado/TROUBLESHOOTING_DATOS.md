# 🔍 Troubleshooting: Datos No Se Visualizan

## Problema
Creaste datos de prueba pero no aparecen en la tabla.

---

## ✅ Pasos de Diagnóstico

### 1. Verificar en DevTools (F12)

**Abre DevTools en el navegador:**
1. Presiona `F12`
2. Ve a la pestaña **"Console"**
3. Busca errores en rojo
4. Ve a la pestaña **"Network"**
5. Recarga la página (`F5`)
6. Busca la petición a `/categorias-materiales`
7. Haz clic en ella y verifica:
   - **Status Code:** Debería ser `200 OK`
   - **Response:** Debería mostrar un array con tus datos

**¿Qué significa cada resultado?**

- ✅ **200 OK + datos en Response:** El backend funciona, problema en el frontend
- ❌ **404 Not Found:** La URL está mal o el endpoint no existe
- ❌ **500 Internal Server Error:** Error en el backend
- ❌ **No aparece la petición:** El JavaScript no se está ejecutando

---

### 2. Verificar los Datos en la Base de Datos

**Opción A: SQL Server Management Studio**
```sql
USE CarroceriaAlvaradoDB;
SELECT * FROM Categorias_Materiales;
```

**Opción B: Desde Python**
```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\backend
python check_db.py
```

**¿Los datos existen en la BD?**
- ✅ **Sí:** Problema en el backend o frontend
- ❌ **No:** Los datos no se guardaron correctamente

---

### 3. Verificar Logs del Backend

**En la terminal donde corre `python app.py`, busca:**

```
127.0.0.1 - - [fecha] "GET /categorias-materiales HTTP/1.1" 200 -
```

**¿Qué significa?**
- ✅ **Aparece:** El backend recibió la petición
- ❌ **No aparece:** El frontend no está haciendo la petición

---

### 4. Probar el Endpoint Directamente

**Abre en el navegador:**
```
https://553682876eea.ngrok-free.app/categorias-materiales
```

**¿Qué ves?**
- ✅ **Array JSON con datos:** El backend funciona
- ❌ **Error o vacío:** Problema en el backend

---

## 🔧 Soluciones Según el Problema

### Problema: Petición no llega al backend

**Causa:** JavaScript no se está ejecutando o hay error

**Solución:**
1. Abre DevTools → Console
2. Busca errores en rojo
3. Comparte el error para ayudarte

---

### Problema: Backend retorna 404

**Causa:** URL incorrecta o endpoint no existe

**Solución:**
Verifica que el backend tenga el endpoint `/categorias-materiales`

---

### Problema: Backend retorna 500

**Causa:** Error en el código del backend

**Solución:**
1. Mira los logs del backend (terminal)
2. Busca el error
3. Comparte el error para ayudarte

---

### Problema: Backend retorna array vacío []

**Causa:** No hay datos en la base de datos

**Solución:**
1. Verifica que los datos existan en SQL Server
2. Si no existen, créalos de nuevo

---

## 📝 Información que Necesito

Para ayudarte mejor, comparte:

1. **Captura de DevTools → Network:**
   - La petición a `/categorias-materiales`
   - Status Code
   - Response

2. **Captura de DevTools → Console:**
   - Errores en rojo (si los hay)

3. **¿Los datos existen en la BD?**
   - Ejecuta: `SELECT * FROM Categorias_Materiales;`

4. **Logs del backend:**
   - ¿Aparece la petición GET?

---

## 🎯 Prueba Rápida

**Abre esta URL en el navegador:**
```
https://553682876eea.ngrok-free.app/categorias-materiales
```

**¿Qué ves?**
- Si ves un array JSON → El backend funciona
- Si ves error → Comparte el error

---

**Realiza estos pasos y comparte los resultados para ayudarte a solucionar el problema. 🔧**
