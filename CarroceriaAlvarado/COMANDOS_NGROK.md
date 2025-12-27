# 🚀 Comandos para Iniciar ngrok

## ✅ Comando Correcto para Tu Configuración

Ya que:
- ngrok está en `E:\ngrok\`
- El proyecto está en `C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\`
- Ya configuraste tu authtoken (está en `C:\Users\ASUS\AppData\Local\ngrok\ngrok.yml`)

---

## 📝 Opción 1: Desde la Carpeta del Proyecto

```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
E:\ngrok\ngrok.exe start --all --config ngrok.yml
```

---

## 📝 Opción 2: Desde la Carpeta de ngrok

```powershell
cd E:\ngrok
.\ngrok.exe start --all --config C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\ngrok.yml
```

---

## ✅ Resultado Esperado

```
ngrok

Session Status                online
Account                       tu_email@example.com
Version                       3.x.x
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040

Forwarding                    https://abc123.ngrok-free.app -> http://localhost:5000
Forwarding                    https://xyz789.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

---

## 📋 Próximos Pasos

1. **Copia las URLs:**
   - Backend (5000): `https://abc123.ngrok-free.app`
   - Frontend (8000): `https://xyz789.ngrok-free.app`

2. **Actualiza el sistema:**
   ```powershell
   cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
   .\configurar_ngrok_completo.ps1 -BackendUrl "https://abc123.ngrok-free.app"
   ```

3. **Verifica:**
   - Abre `http://localhost:4040` para ver los túneles
   - Prueba la URL del frontend en tu navegador

4. **Comparte:**
   - Envía la URL del frontend a tus usuarios de prueba

---

## 🔍 Verificar Túneles Activos

Abre en tu navegador: **http://localhost:4040**

Deberías ver 2 túneles:
- ✅ `backend` → `http://localhost:5000`
- ✅ `frontend` → `http://localhost:8000`

---

## 🛑 Detener ngrok

Presiona `Ctrl + C` en la terminal donde está corriendo ngrok.

---

## 🔄 Revertir Configuración

Cuando termines las pruebas:

```powershell
cd C:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado
.\configurar_ngrok_completo.ps1 -Revertir
```

---

**¡Ahora sí debería funcionar! 🎉**
