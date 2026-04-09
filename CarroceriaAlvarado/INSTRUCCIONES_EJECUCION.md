# 🚀 Guía de Ejecución - Carrocería Alvarado

## ⚙️ REQUISITOS PREVIOS

### 1. Base de Datos (PRIMERO)
**Antes de ejecutar cualquier cosa, ejecuta el script SQL:**

- Abre **SQL Server Management Studio (SSMS)**
- Conecta a: `DESKTOP-OJ81G31\SQLEXPRESS`
- Abre base de datos: `CarroceriaAlvaradoDB`
- Ejecuta script: `scripts/fix_usuarios_table.sql`
- Verifica que el script se ejecute sin errores

**Si es la primera vez, ejecuta también:**
- `scripts/database.sql` para crear la BD desde cero

---

## 🐍 PASO 1: Configurar y Ejecutar Backend

### 1.1 Abrir terminal PowerShell en carpeta `backend/`
```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\backend
```

### 1.2 Ejecutar app.py en puerto 5001
```powershell
python app.py
```

**Esperado:**
```
 * Running on http://127.0.0.1:5001
 * Debug mode: off
```

### 1.3 Verificar que el backend está corriendo
- Abre en navegador: http://127.0.0.1:5001
- Deberías ver mensajes de error (es normal si accedes sin token JWT), lo importante es que el servidor responda

---

## 🌐 PASO 2: Ejecutar Frontend

### 2.1 NUEVA terminal PowerShell en carpeta `frontend/`
```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\frontend
python -m http.server 8000
```

**Esperado:**
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

### 2.2 Abrir en navegador
- Ve a: **http://127.0.0.1:8000**
- Deberías ver la página de LOGIN

---

## 🔑 PASO 3: Probar login

### Credenciales de Prueba
Necesitas primero crear un usuario. Puedes:

**Opción A: Registrarse desde el frontend**
1. En http://127.0.0.1:8000, busca opción de "Registrarse"
2. Crea usuario con:
   - Username: `admin`
   - Email: `admin@carroceria.com`
   - Password: `123456`
   - Rol: Administrador

**Opción B: Insertar usuario directo en BD (recomendado para testing)**
En SSMS, ejecuta:
```sql
USE CarroceriaAlvaradoDB;

-- Insertar usuario admin de prueba
INSERT INTO Usuarios (username, email, password_hash, rol, estado, intentos_fallidos, bloqueado)
VALUES (
    'admin',
    'admin@carroceria.com',
    0x2432622431322428423642424843424253427566672e385661496254334150486155397141537a534c6b4e4f565835594d6569615845556f5370386f757a414d,
    'Administrador',
    1,
    0,
    0
);
```
*(Esto inserta un usuario con password "123456" hasheada con bcrypt)*

### Login en Frontend
1. Ve a: http://127.0.0.1:8000
2. Ingresa credenciales:
   - Usuario: `admin`
   - Contraseña: `123456`
3. Click en "Ingresar"

---

## ✅ Verificar que todo funciona

| Componente | URL | Esperado |
|------------|-----|----------|
| **Backend** | http://127.0.0.1:5001 | Responde (puede mostrar error 401/403) |
| **Frontend** | http://127.0.0.1:8000 | Página de login carga |
| **Login** | Ingresa admin/123456 | Redirige a dashboard |
| **Base de Datos** | SSMS | Tabla Usuarios con columnas: id_usuario, username, email, password_hash, rol, estado, intentos_fallidos, bloqueado |

---

## 🔴 Troubleshooting

### Error: "Invalid column name 'rol'"
**Solución:** Ejecuta el script `scripts/fix_usuarios_table.sql` en SSMS

### Error: "Connection refused" en frontend
**Solución:** 
- Verifica que backend está ejecutándose en terminal 1
- Revisa que config.js tiene: `API_BASE_URL = 'http://127.0.0.1:5001'`

### Error: "Port 5001 already in use"
**Solución:** 
- El otro proyecto está usando este puerto
- Cambia en app.py la línea: `app.run(debug=False, port=5002)` (o cualquier puerto libre)

### Error: "Module not found: pyodbc"
**Solución:**
```powershell
pip install -r requirements.txt
```

### Error de autenticación después de login
**Solución:**
- Limpia localStorage en browser (DevTools F12 → Application → Clear All)
- Intenta login nuevamente

---

## ⚡ Comandos Rápidos (Copiar y Pegar)

### Terminal 1 - Backend
```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\backend
python app.py
```

### Terminal 2 - Frontend
```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\frontend
python -m http.server 8000
```

### Terminal 3 - Navegar a la app
```powershell
Start-Process "http://127.0.0.1:8000"
```

---

## 📌 Puertos Utilizados

| Servicio | Puerto | URL |
|----------|--------|-----|
| **Backend Flask** | 5001 | http://127.0.0.1:5001 |
| **Frontend HTTP** | 8000 | http://127.0.0.1:8000 |
| **Otro Proyecto** | 5000 | *No interfiere* |

---

## 🎯 Próximos Pasos

Una vez que todo esté funcionando:
1. Crea más usuarios desde el panel de admin
2. Prueba crear órdenes de trabajo
3. Prueba gestión de inventario
4. Prueba reportes

¡Éxito! 🚀
