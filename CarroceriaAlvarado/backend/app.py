from flask import Flask, request, jsonify
from flask_cors import CORS  # Nueva importación
import pyodbc
import bcrypt
import json

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Configuración de la conexión a SQL Server
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-OJ81G31\\SQLEXPRESS;"
    "DATABASE=CarroceriaAlvaradoDB;"
    "Trusted_Connection=yes;"
)

def get_db_connection():
    """Función para establecer conexión con la base de datos."""
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        raise Exception(f"Error al conectar a la base de datos: {str(e)}")

# Ruta para registrar un nuevo usuario
@app.route('/registro', methods=['POST'])
def registrar_usuario():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        rol = data.get('rol', 'Empleado')  # Valor por defecto 'Empleado'
        estado = data.get('estado', 'Activo')  # Valor por defecto 'Activo'

        if not username or not password:
            return jsonify({'error': 'Username y password son requeridos'}), 400

        # Encriptar la contraseña
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Usuarios (username, password_hash, rol, estado) VALUES (?, ?, ?, ?)",
            (username, hashed_password, rol, estado)
        )
        conn.commit()
        conn.close()

        return jsonify({'message': 'Usuario registrado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username y password son requeridos'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM Usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            hashed_password = user[0]  # El hash ya es bytes porque el campo es VARBINARY
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return jsonify({'message': 'Login exitoso'}), 200
            else:
                return jsonify({'error': 'Credenciales inválidas'}), 401
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta inicial para verificar que la aplicación funciona
@app.route('/')
def hello():
    return "¡API de Autenticación funcionando! Prueba /registro o /login"

if __name__ == '__main__':
    app.run(debug=True)