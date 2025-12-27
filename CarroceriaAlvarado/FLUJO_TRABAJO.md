# 🔄 Flujo de Trabajo Visual - Despliegue con ngrok

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ANTES DE EMPEZAR                                 │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ Verificar    │
    │ Entorno      │  .\verificar_entorno.ps1
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ ¿Todo OK?    │───── NO ──→ Corregir errores
    └──────┬───────┘
           │ SÍ
           ▼

┌─────────────────────────────────────────────────────────────────────┐
│                    INSTALACIÓN DE NGROK                             │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────┐
    │ 1. Descargar ngrok                               │
    │    https://ngrok.com/download                    │
    │    Extraer a C:\ngrok\                           │
    └──────────────┬───────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────────────┐
    │ 2. Crear cuenta en ngrok.com                     │
    │    Obtener authtoken                             │
    └──────────────┬───────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────────────┐
    │ 3. Configurar token                              │
    │    cd C:\ngrok                                   │
    │    .\ngrok config add-authtoken TU_TOKEN         │
    └──────────────┬───────────────────────────────────┘
                   │
                   ▼

┌─────────────────────────────────────────────────────────────────────┐
│                    INICIAR SERVIDORES LOCALES                       │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────┐      ┌──────────────────────┐
    │ Terminal A           │      │ Terminal B           │
    │ ──────────           │      │ ──────────           │
    │ cd backend           │      │ cd frontend          │
    │ python app.py        │      │ python -m http       │
    │                      │      │   .server 8000       │
    │ Puerto: 5000         │      │ Puerto: 8000         │
    └──────────┬───────────┘      └──────────┬───────────┘
               │                             │
               └──────────┬──────────────────┘
                          │
                          ▼

┌─────────────────────────────────────────────────────────────────────┐
│                    EXPONER CON NGROK                                │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────┐      ┌──────────────────────┐
    │ Terminal C           │      │ Terminal D           │
    │ ──────────           │      │ ──────────           │
    │ cd C:\ngrok          │      │ cd C:\ngrok          │
    │ .\ngrok http 5000    │      │ .\ngrok http 8000    │
    │   --host-header=     │      │   --host-header=     │
    │   "localhost:5000"   │      │   "localhost:8000"   │
    │                      │      │                      │
    │ 📝 Copiar URL        │      │ 📝 Copiar URL        │
    │ Backend              │      │ Frontend             │
    └──────────┬───────────┘      └──────────┬───────────┘
               │                             │
               │  https://abc123.ngrok.app   │  https://xyz789.ngrok.app
               │                             │
               └──────────┬──────────────────┘
                          │
                          ▼

┌─────────────────────────────────────────────────────────────────────┐
│                    CONFIGURAR SISTEMA                               │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────┐
    │ Terminal E (en carpeta del proyecto)             │
    │ ──────────                                       │
    │ cd C:\Users\ASUS\Proyectos\APP-II\               │
    │    CarroceriaAlvarado                            │
    │                                                  │
    │ .\configurar_ngrok_completo.ps1 \                │
    │   -BackendUrl "https://abc123.ngrok.app"         │
    │                                                  │
    │ ✓ Actualiza todos los archivos HTML             │
    └──────────────┬───────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────────────┐
    │ Verificar actualización                          │
    │ .\configurar_ngrok_completo.ps1 -VerificarSolamente│
    └──────────────┬───────────────────────────────────┘
                   │
                   ▼

┌─────────────────────────────────────────────────────────────────────┐
│                    COMPARTIR CON USUARIOS                           │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────┐
    │ Enviar a usuarios de prueba:                     │
    │                                                  │
    │ 🔗 URL: https://xyz789.ngrok.app (frontend)      │
    │                                                  │
    │ 📋 Instrucciones:                                │
    │    1. Abrir URL en navegador                     │
    │    2. Hacer clic en "Visit Site"                 │
    │    3. Probar funcionalidades                     │
    │                                                  │
    │ 📝 Formulario: docs/FORMULARIO_FEEDBACK.md       │
    └──────────────┬───────────────────────────────────┘
                   │
                   ▼

┌─────────────────────────────────────────────────────────────────────┐
│                    MONITOREAR PRUEBAS                               │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────┐      ┌──────────────────────┐
    │ Navegador            │      │ Terminales           │
    │ ──────────           │      │ ──────────           │
    │ http://localhost:    │      │ Ver logs de:         │
    │   4040               │      │ • Backend (Terminal A)│
    │                      │      │ • Frontend (Terminal B)│
    │ Ver peticiones HTTP  │      │ • ngrok (Terminales  │
    │ en tiempo real       │      │   C y D)             │
    └──────────┬───────────┘      └──────────┬───────────┘
               │                             │
               └──────────┬──────────────────┘
                          │
                          ▼
    ┌──────────────────────────────────────────────────┐
    │ Recopilar feedback de usuarios                   │
    └──────────────┬───────────────────────────────────┘
                   │
                   ▼

┌─────────────────────────────────────────────────────────────────────┐
│                    FINALIZAR PRUEBAS                                │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────┐
    │ 1. Detener ngrok                                 │
    │    Ctrl + C en Terminales C y D                  │
    └──────────────┬───────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────────────┐
    │ 2. Revertir configuración                        │
    │    .\configurar_ngrok_completo.ps1 -Revertir     │
    └──────────────┬───────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────────────┐
    │ 3. Analizar feedback                             │
    │    Revisar formularios de usuarios               │
    └──────────────┬───────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────────────┐
    │ 4. Implementar mejoras                           │
    │    Basado en feedback recibido                   │
    └──────────────────────────────────────────────────┘

```

---

## 📊 Resumen de Terminales Necesarias

| Terminal | Propósito | Comando | Estado |
|----------|-----------|---------|--------|
| **A** | Backend | `cd backend && python app.py` | Mantener abierta |
| **B** | Frontend | `cd frontend && python -m http.server 8000` | Mantener abierta |
| **C** | ngrok Backend | `cd C:\ngrok && .\ngrok http 5000 --host-header="localhost:5000"` | Mantener abierta |
| **D** | ngrok Frontend | `cd C:\ngrok && .\ngrok http 8000 --host-header="localhost:8000"` | Mantener abierta |
| **E** | Configuración | `.\configurar_ngrok_completo.ps1 -BackendUrl "URL"` | Cerrar después |

---

## 🎯 URLs Importantes

| Servicio | URL Local | URL Pública (ngrok) | Propósito |
|----------|-----------|---------------------|-----------|
| **Backend API** | http://127.0.0.1:5000 | https://abc123.ngrok.app | API del sistema |
| **Frontend** | http://127.0.0.1:8000 | https://xyz789.ngrok.app | Interfaz de usuario |
| **ngrok Inspector** | http://127.0.0.1:4040 | - | Monitoreo de peticiones |

---

## ⏱️ Tiempo Estimado

| Fase | Tiempo | Notas |
|------|--------|-------|
| Instalación de ngrok | 5 min | Solo primera vez |
| Configuración inicial | 3 min | Solo primera vez |
| Exponer servicios | 2 min | Cada sesión |
| Actualizar configuración | 1 min | Cada sesión |
| Pruebas de usuarios | Variable | Depende del alcance |
| Revertir cambios | 1 min | Al finalizar |

**Total primera vez:** ~15 minutos  
**Total sesiones siguientes:** ~5 minutos

---

## 🔄 Ciclo de Vida de una Sesión de Pruebas

```
Inicio → Verificar → Exponer → Configurar → Compartir → Monitorear → Finalizar
  ↑                                                                        ↓
  └────────────────────────── Revertir ←──────────────────────────────────┘
```

---

## 📝 Notas Importantes

1. **No cerrar terminales:** Mantén las terminales A, B, C y D abiertas durante toda la sesión.

2. **URLs temporales:** En la versión gratuita de ngrok, las URLs cambian cada vez que reinicias.

3. **Pantalla de advertencia:** Los usuarios verán una advertencia de ngrok. Deben hacer clic en "Visit Site".

4. **Monitoreo continuo:** Revisa http://localhost:4040 para ver todas las peticiones en tiempo real.

5. **Revertir siempre:** No olvides revertir los cambios al finalizar las pruebas.

---

## 🚀 Comando Rápido para Copiar

```powershell
# Verificar entorno
.\verificar_entorno.ps1

# Configurar ngrok (reemplaza con tu URL real)
.\configurar_ngrok_completo.ps1 -BackendUrl "https://abc123.ngrok-free.app"

# Verificar configuración
.\configurar_ngrok_completo.ps1 -VerificarSolamente

# Revertir al finalizar
.\configurar_ngrok_completo.ps1 -Revertir
```

---

**¡Sigue este flujo y tendrás un despliegue exitoso! 🎉**
