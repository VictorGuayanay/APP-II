# APP-II - Sistema de Gestión de Inventario y Recursos Humanos
## Estructura del Proyecto
CarroceriaAlvarado/
├── backend/          # Código del backend (Flask)
│   ├── app.py
│   ├── routes/
│   └── models/
├── frontend/         # Código del frontend (HTML, CSS, JS)
├── scripts/          # Scripts SQL para la base de datos
├── docs/            # Documentación del proyecto
│   ├── Historias_Usuario/  # Nueva carpeta para documentación adicional
│   │   ├── Subido V2 de historias de Usuario
|   |── Historias_Técnicas/  # Nueva carpeta para documentación adicional
│   │   ├── Subido V2 de historias técnicas
|   |── Requerimientos/  # Nueva carpeta para documentación adicional
│   │   ├── Subido V2 de requerimientos
|   |── ProductBacklog/  # Nueva carpeta para documentación adicional
│   │   ├── Subido V2 del productbacklog
│   └── README.md
├── .gitignore       # Archivos a ignorar por Git
└── requirements.txt

## Diseño e Implementación de la Base de Datos
- Base de datos creada: `CarroceriaAlvaradoDB`.
- Motor de base de datos: Microsoft SQL Server 2019.
- Tablas:
  - `Usuarios`: Gestión de autenticación (username, password_hash, rol).
  - `Materiales`: Gestión del inventario (nombre, cantidad, precio_unitario).
  - `Empleados`: Gestión de recursos humanos (nombre, cedula, rol).
  - `Clientes`: Registro de clientes (nombre, cedula, telefono).
  - `OrdenesTrabajo`: Gestión de trabajos (id_cliente, id_empleado, estado).
  - `DetalleOrdenMateriales`: Relación entre órdenes y materiales (cantidad_usada).
  - `ComprobantesPago`: Registro de pagos (monto, metodo_pago).
  - `ReportesOperativos`: Almacena reportes generados (tipo_reporte, datos).
- Conexión: Configurada en `backend/app.py` usando `pyodbc` con una prueba inicial exitosa.
- Consultas: Implementadas rutas `/usuarios` y `/materiales` para listar datos.
- Script SQL disponible en `scripts/database.sql`.


## Configuración del Entorno
1. Instalar Git: `git --version`
2. Configurar Git:
   - `git config --global user.name "Victor Guayanay"`
   - `git config --global user.email victor.guayanay@espoch.edu.ec`
3. Clonar el repositorio: `git clone https://github.com/VictorGuayanay/APP-II.git`
4. Instalar Python 3.9+: `python --version`
5. Instalar dependencias: `pip install flask flask-session pyodbc bcrypt`
6. Probar Flask: `cd CarroceriaAlvarado/backend && python app.py`

## Implementación de la API de Autenticación
- Tarea: HT-003.
- Descripción: Implementación de rutas para registrar usuarios y autenticación.
- Rutas:
  - `/registro` (POST): Registra un nuevo usuario con contraseña encriptada usando bcrypt.
  - `/login` (POST): Verifica las credenciales del usuario y devuelve un mensaje de éxito.
- Tecnologías: Flask, pyodbc, bcrypt.
- Notas: Campo password_hash cambiado a VARBINARY para almacenar correctamente los hashes.
- Estado: Implementado y probado con éxito.

## Desarrollo de la Interfaz de Inicio de Sesión
- Tarea: HT-006.
- Descripción: Desarrollo de una interfaz de usuario para iniciar sesión que interactúa con la API de autenticación.
- Archivos:
  - `frontend/index.html`: Estructura del formulario adaptada de una plantilla moderna.
  - `frontend/css/`: Estilos (util.css, main.css) y dependencias.
  - `frontend/js/main.js`: Lógica para enviar solicitudes a la API.
  - `frontend/vendor/`: Dependencias de la plantilla (Bootstrap, jQuery, etc.).
  - `frontend/fonts/`: Fuentes utilizadas.
  - `frontend/images/`: Imágenes de fondo.
- Tecnologías: HTML, CSS, JavaScript, Bootstrap, jQuery.
- Notas: Se adaptó una plantilla de login moderna para mejorar el diseño visual y funcionalidad. Se habilitó CORS en el backend para permitir la conexión.
- Estado: Implementado y probado con éxito.

## Implementación de la Funcionalidad de Inicio de Sesión
- Historia de Usuario: HU-001.
- Descripción: Integración final del inicio de sesión con redirección a un dashboard.
- Archivos:
  - `frontend/dashboard.html`: Página principal después del login.
  - `frontend/js/main.js`: Actualizado para manejar errores de credenciales y redirigir.
- Pruebas Realizadas:
  - Login exitoso: Redirige al dashboard correctamente.
  - Credenciales incorrectas: Muestra "Credenciales inválidas".
  - Usuario no encontrado: Muestra "Usuario no encontrado".
  - Servidor no disponible: Muestra "Error al conectar con el servidor. Asegúrate de que el servidor esté activo."
- Notas: Ajustado el manejo de errores en el frontend para procesar respuestas de la API correctamente.
- Estado: Completado.

### Estado
- Flask probado con éxito: la ruta raíz ('/') devuelve '¡Entorno Flask funcionando!'
- Eliminada la carpeta backend/utils ya que no se necesita por ahora.
- Creada la carpeta docs/documentacion para documentación adicional.
- Añadidos archivos informe.pdf y notas.txt a docs/documentacion.
- Creada la base de datos con las tablas refinadas y conexión inicial con Flask.
- Implementadas consultas iniciales para usuarios y materiales.
- Implementada la API de autenticación (HT-003) con manejo correcto de hashes.
- Desarrollada la interfaz de inicio de sesión (HT-006) con una plantilla moderna adaptada y CORS habilitado.
- Completada la funcionalidad de inicio de sesión (HU-001) con ajustes en el manejo de errores.
- Documentado el backlog del Sprint 1 y avances del Sprint 2.
- Sprint 2 Completado.