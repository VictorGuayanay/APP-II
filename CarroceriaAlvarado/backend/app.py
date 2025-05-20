from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import bcrypt
import jwt
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

SECRET_KEY = "mi_clave_secreta_123"

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-OJ81G31\SQLEXPRESS;"
    "DATABASE=CarroceriaAlvaradoDB;"
    "Trusted_Connection=yes;"
)

# Configuración para enviar correos (ejemplo con Gmail)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "victorguayanay@gmail.com"  # Reemplaza con tu correo
SMTP_PASSWORD = "qzgl wxpz stvw uxdp"  # Reemplaza con tu contraseña de aplicación

def get_db_connection():
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        raise Exception(f"Error al conectar a la base de datos: {str(e)}")

def send_reset_email(email, user_id):
    try:
        # Generar token JWT para el restablecimiento
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
        token = jwt.encode({
            'user_id': user_id,
            'exp': int(exp_time.timestamp())
        }, SECRET_KEY, algorithm="HS256")

        # Crear el enlace de restablecimiento
        reset_link = f"http://127.0.0.1:8000/new_pass.html?token={token}"

        # Configurar el correo
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = "Restablecer Contraseña - Carrocería Alvarado"

        body = f"""
        Hola,

        Recibimos una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace para establecer una nueva contraseña:
        {reset_link}

        Este enlace es válido por 15 minutos. Si no solicitaste este cambio, ignora este correo.

        Saludos,
        Equipo Carrocería Alvarado
        """
        msg.attach(MIMEText(body, 'plain'))

        # Enviar el correo
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")
        return False

@app.route('/registro', methods=['POST'])
def registrar_usuario():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        rol = data.get('rol', 'Empleado')
        estado_str = data.get('estado', 'Activo') # Obtener el estado como string

        print(f"Recibidos: username={username}, email={email}, password={password}, rol={rol}, estado_str={estado_str}")

        if not username or not email or not password:
            return jsonify({'error': 'Usuario, correo y contraseña son requeridos'}), 400

        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Correo electrónico inválido'}), 400

        # Convertir el estado string a bit (1 para Activo, 0 para Inactivo u otro)
        estado_bit = 1 if estado_str.lower() == 'activo' else 0

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Usuarios (username, email, password_hash, rol, estado) VALUES (?, ?, ?, ?, ?)",
            (username, email, hashed_password, rol, estado_bit) # Usar el estado_bit convertido
        )
        conn.commit()
        conn.close()

        return jsonify({'message': 'Usuario registrado exitosamente'}), 201
    except Exception as e:
        print(f"Error en registro: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        print("Recibida solicitud de login")
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        print(f"Username: {username}, Password: {password}")

        if not username or not password:
            print("Faltan campos requeridos")
            return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_usuario, email, password_hash, rol FROM Usuarios WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()

        if not user:
            print("Usuario no encontrado")
            conn.close()
            return jsonify({'error': 'Usuario no encontrado'}), 404

        user_id, email, hashed_password, rol = user
        print(f"Usuario encontrado - ID: {user_id}, Email: {email}, Rol: {rol}")
        print(f"Hash almacenado: {hashed_password.hex()}")

        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            print("Contraseña correcta, generando token")
            exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
            token = jwt.encode({
                'user_id': user_id,
                'email': email,
                'rol': rol,
                'exp': int(exp_time.timestamp())
            }, SECRET_KEY, algorithm="HS256")
            conn.close()
            print("Login exitoso, enviando respuesta")
            return jsonify({'message': 'Login exitoso', 'token': token, 'rol': rol}), 200
        else:
            print("Contraseña incorrecta")
            conn.close()
            return jsonify({'error': 'Credenciales inválidas'}), 401

    except Exception as e:
        print(f"Error en login: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reset_password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Correo electrónico es requerido'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_usuario FROM Usuarios WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({'error': 'Correo no registrado'}), 404

        user_id = user[0]
        if send_reset_email(email, user_id):
            return jsonify({'message': 'Instrucciones enviadas a su correo electrónico'}), 200
        else:
            return jsonify({'error': 'Error al enviar el correo'}), 500

    except Exception as e:
        print(f"Error en reset_password: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/new_password', methods=['POST'])
def new_password():
    try:
        data = request.get_json()
        token = data.get('token')
        password = data.get('password')

        if not token or not password:
            return jsonify({'error': 'Token y contraseña son requeridos'}), 400

        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = decoded['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'El enlace ha expirado'}), 400
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Enlace inválido'}), 400

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Usuarios SET password_hash = ? WHERE id_usuario = ?",
            (hashed_password, user_id)
        )
        conn.commit()
        conn.close()

        return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200

    except Exception as e:
        print(f"Error en new_password: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def hello():
    return "¡API de Autenticación funcionando! Prueba /registro, /login, /reset_password o /new_password"

if __name__ == '__main__':
    app.run(debug=True)