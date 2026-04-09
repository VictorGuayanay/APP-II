# ✅ SOLUCIÓN COMPLETA - Carrocería Alvarado Listo para Desplegar

## 🐛 Problema Original
```
Error: Invalid column name 'rol' en tabla Usuarios
Razón: La BD tenía estructura incompleta
```

## ✅ Solución Aplicada (5 cambios)

| # | Componente | Cambio | Archivo |
|---|-----------|--------|---------|
| 1️⃣ | **Base de Datos** | Agregadas columnas faltantes (email, rol, estado, intentos_fallidos, bloqueado) | `scripts/fix_usuarios_table.sql` |
| 2️⃣ | **Backend** | Puerto: 5000 → **5001** (para no interferir) | `backend/app.py` |
| 3️⃣ | **Frontend Config** | API URL: 5000 → **5001** | `frontend/js/config.js` |
| 4️⃣ | **Usuario Admin** | Script para crear usuario de prueba (admin/123456) | `scripts/crear_usuario_admin.sql` |
| 5️⃣ | **Automatización** | Script batch para ejecutar todo con 1 click | `INICIAR.bat` |

---

## 🚀 INSTRUCCIONES DE EJECUCIÓN (3 pasos)

### ✋ IMPORTANTE: ANTES DE COMIENZA, EJECUTA LOS SCRIPTS SQL

**Abre SQL Server Management Studio (SSMS):**

#### Paso 1️⃣: Actualizar la Base de Datos
```
1. Conecta a: DESKTOP-OJ81G31\SQLEXPRESS
2. Abre BD: CarroceriaAlvaradoDB
3. Abre archivo: scripts/fix_usuarios_table.sql
4. Ejecuta (F5)
5. Verifica que se agregaron las columnas
```

#### Paso 2️⃣: Crear Usuario Admin de Prueba
```
1. En SSMS, abre: scripts/crear_usuario_admin.sql
2. Ejecuta (F5)
3. Verifica que se creó el usuario admin
```

---

### 🎮 EJECUTAR LA APLICACIÓN (Opción A: Automático)

**Windows - Doble click en:**
```
📁 INICIAR.bat
```

Esto abrirá automáticamente:
- ✅ Terminal 1: Backend (Puerto 5001)
- ✅ Terminal 2: Frontend (Puerto 8000)
- ✅ Navegador: http://127.0.0.1:8000

---

### 🎮 EJECUTAR LA APLICACIÓN (Opción B: Manual)

**Terminal 1 - Backend:**
```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\backend
python app.py
```
Esperado:
```
Running on http://127.0.0.1:5001
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\frontend
python -m http.server 8000
```
Esperado:
```
Serving HTTP on 0.0.0.0 port 8000
```

---

## 🔐 CREDENCIALES DE PRUEBA

| Campo | Valor |
|-------|-------|
| **Usuario** | `admin` |
| **Contraseña** | `123456` |
| **Rol** | Administrador |

---

## 🌐 URLS FINALES

| Servicio | URL | Puerto |
|----------|-----|--------|
| **Frontend** | http://127.0.0.1:8000 | 8000 |
| **Backend** | http://127.0.0.1:5001 | 5001 |
| **Otro Proyecto** | http://127.0.0.1:5000 | 5000 *(No interfiere)* |

---

## 📋 CHECKLIST DE VERIFICACIÓN

```
[ ] 1. Ejecuté fix_usuarios_table.sql en SSMS
[ ] 2. Ejecuté crear_usuario_admin.sql en SSMS
[ ] 3. Ejecuté INICIAR.bat (o levantè backends manualmente)
[ ] 4. Accedí a http://127.0.0.1:8000
[ ] 5. Vi página de login
[ ] 6. Login con admin / 123456
[ ] 7. Accedí al dashboard correctamente
```

---

## 🆘 TROUBLESHOOTING RÁPIDO

| Problema | Solución |
|----------|----------|
| ❌ SQL Error "Invalid column name 'rol'" | Ejecuta `scripts/fix_usuarios_table.sql` en SSMS |
| ❌ Frontend no conecta al backend | Verifica `frontend/js/config.js` tiene `http://127.0.0.1:5001` |
| ❌ Puerto 5001 ya en uso | Cambia en `backend/app.py` línea 4037 a otro puerto (ej: 5002) |
| ❌ Login dice "Error de BD" | Ejecuta `scripts/crear_usuario_admin.sql` para crear usuario admin |
| ❌ "Module pyodbc not found" | `pip install -r requirements.txt` |
| ❌ CORS error en navegador | Ya está configurado, verifica console (F12) para más detalles |

---

## 📁 ARCHIVOS IMPORTANTES

```
CarroceriaAlvarado/
├── INICIAR.bat ⭐ <- EJECUTA ESTO PARA EMPEZAR
├── INSTRUCCIONES_EJECUCION.md <- Lee para detalles completos
├── backend/
│   ├── app.py (PUERTO CAMBIADO: 5001)
│   └── requirements.txt
├── frontend/
│   ├── js/config.js (API URL: 5001)
│   └── [archivos HTML]
└── scripts/
    ├── fix_usuarios_table.sql ⭐ <- EJECUTA PRIMERO EN SSMS
    └── crear_usuario_admin.sql ⭐ <- EJECUTA SEGUNDO EN SSMS
```

---

## ✨ TODO LISTO PARA DESPLEGAR

**Próximo paso:** Ejecuta los scripts SQL y luego haz doble click en `INICIAR.bat`

¡La aplicación estará corriendo en 30 segundos! 🚀

---

*Última revisión: 7 Abril 2026*
