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

## Configuración del Entorno
1. Instalar Git: `git --version`
2. Configurar Git:
   - `git config --global user.name "Victor Guayanay"`
   - `git config --global user.email victor.guayanay@espoch.edu.ec`
3. Clonar el repositorio: `git clone https://github.com/VictorGuayanay/APP-II.git`
4. Instalar Python 3.9+: `python --version`
5. Instalar dependencias: `pip install flask flask-session pyodbc bcrypt`
6. Probar Flask: `cd CarroceriaAlvarado/backend && python app.py`

### Estado
- Flask probado con éxito: la ruta raíz ('/') devuelve '¡Entorno Flask funcionando!'
- Eliminada la carpeta backend/utils ya que no se necesita por ahora.
- Creada la carpeta docs/documentacion para documentación adicional.
- Añadidos archivos informe.pdf y notas.txt a docs/documentacion.