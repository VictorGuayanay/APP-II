from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc
import bcrypt
import jwt # Asegúrate que sea PyJWT
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps

app = Flask(__name__)
# 1. Configuración de SECRET_KEY (CRUCIAL Y ÚNICA VEZ)
# Esta es la clave que se usará para TODAS las operaciones de JWT (encode/decode)
app.config['SECRET_KEY'] = "123456789" # ¡CAMBIA ESTO POR UNA CLAVE MÁS SEGURA Y COMPLEJA EN PRODUCCIÓN!
print(f"APP INIT: app.config['SECRET_KEY'] establecida como: '{app.config.get('SECRET_KEY')}'")

#  Variables Globales para Configuración
APP_CONFIG = {
    "reset_token_expiry_minutes": 15, # Duración actual en send_reset_email
    "max_failed_login_attempts": 5,    # intentos para iniciar sesion
    "global_low_stock_threshold": 10 # Valor para limite de stock bajo
}


CORS(app) 

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-OJ81G31\SQLEXPRESS;" 
    "DATABASE=CarroceriaAlvaradoDB;"
    "Trusted_Connection=yes;"
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "victorguayanay@gmail.com" 
SMTP_PASSWORD = "qzgl wxpz stvw uxdp" 



def get_db_connection():
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"!!!!!!!! ERROR CRÍTICO AL CONECTAR A LA BASE DE DATOS: {str(e)} !!!!!!!!")
        raise Exception(f"Error al conectar a la base de datos: {str(e)}")


def send_reset_email(email, user_id):
    try:
        expiry_minutes = APP_CONFIG.get('reset_token_expiry_minutes', 15) #15 min tiempo que dura el token para reestablecer contraseña
        print(f"DEBUG send_reset_email: Duración del token de reseteo establecida en: {expiry_minutes} minutos.")
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expiry_minutes)
        
        secret_key_for_encode = app.config.get('SECRET_KEY')
        print(f"DEBUG send_reset_email: SECRET_KEY para ENCODE (reseteo): '{secret_key_for_encode}'")

        token_payload = {
            'user_id': user_id,
            'exp': exp_time 
        }
        token = jwt.encode(token_payload, secret_key_for_encode, algorithm="HS256")
        
        print(f"DEBUG send_reset_email: Token de reseteo GENERADO para user_id {user_id}: {token}")

        reset_link = f"http://127.0.0.1:8000/new_pass.html?token={token}" 

        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = "Restablecer Contraseña - Carrocería Alvarado"
        body = f"""
        Hola,

        Recibimos una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace para establecer una nueva contraseña:
        {reset_link}

        Este enlace es válido por {expiry_minutes} minutos. Si no solicitaste este cambio, ignora este correo.

        Saludos,
        Equipo Carrocería Alvarado
        """
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo de restablecimiento: {str(e)}")
        return False
    

@app.route('/registro', methods=['POST'])
def registrar_usuario():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos JSON'}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        rol = data.get('rol', 'Empleado') 
        estado_str = data.get('estado', 'Activo')

        print(f"Registro - Recibidos: username={username}, email={email}, password={'******' if password else None}, rol={rol}, estado_str={estado_str}")

        if not username or not email or not password:
            return jsonify({'error': 'Usuario, correo y contraseña son requeridos'}), 400
        if '@' not in email or '.' not in email: 
            return jsonify({'error': 'Correo electrónico inválido'}), 400

        estado_bit = 1 if estado_str.lower() == 'activo' else 0
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id_usuario FROM Usuarios WHERE username = ?", (username,))
            if cursor.fetchone():
                return jsonify({'error': 'El nombre de usuario ya existe'}), 409
            
            cursor.execute("SELECT id_usuario FROM Usuarios WHERE email = ?", (email,))
            if cursor.fetchone():
                return jsonify({'error': 'El correo electrónico ya está registrado'}), 409

            cursor.execute(
                "INSERT INTO Usuarios (username, email, password_hash, rol, estado) VALUES (?, ?, ?, ?, ?)",
                (username, email, hashed_password, rol, estado_bit)
            )
            conn.commit()
            return jsonify({'message': 'Usuario registrado exitosamente'}), 201
        except Exception as db_e:
            if conn: conn.rollback()
            print(f"Error de BD en /registro: {str(db_e)}")
            return jsonify({'error': f'Error de base de datos en registro: {str(db_e)}'}), 500
        finally:
            if conn: conn.close()
    except Exception as e:
        print(f"Error general en /registro: {str(e)}")
        return jsonify({'error': f'Error interno del servidor en registro: {str(e)}'}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data: return jsonify({'error': 'No se recibieron datos JSON'}), 400

        username = data.get('username')
        password = data.get('password')
        print(f"Login - Recibido: Username: {username}, Password: {'******' if password else None}")

        if not username or not password: return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400
        
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Obtener id_usuario, hash, rol, estado, intentos_fallidos y si está bloqueado
            cursor.execute(
                "SELECT id_usuario, email, password_hash, rol, estado, intentos_fallidos, bloqueado FROM Usuarios WHERE username = ?",
                (username,)
            )
            user_db_data = cursor.fetchone()

            if not user_db_data:
                print(f"Login - Usuario no encontrado: {username}")
                return jsonify({'error': 'Usuario no encontrado'}), 404

            user_id, email, db_password_hash, rol, user_estado_activo, intentos_fallidos_actuales, bloqueado_actual = user_db_data
            
            # Verificar si la cuenta está bloqueada permanentemente por el admin (campo 'estado')
            if not user_estado_activo:
                print(f"Login - Intento de login para cuenta inactiva (por admin): {username}")
                return jsonify({'error': 'Su cuenta ha sido desactivada por un administrador.'}), 403

            # Verificar si la cuenta está bloqueada por intentos fallidos (campo 'bloqueado')
            if bloqueado_actual:
                print(f"Login - Intento de login para cuenta bloqueada por intentos: {username}")
                return jsonify({'error': 'Su cuenta ha sido bloqueada debido a múltiples intentos fallidos. Contacte al administrador.'}), 403

            # Verificar contraseña
            if bcrypt.checkpw(password.encode('utf-8'), db_password_hash):
                print(f"Login - Contraseña correcta para {username}")
                
                # Si el login es exitoso, resetear intentos_fallidos y el estado de bloqueo (si aplica)
                if intentos_fallidos_actuales > 0 or bloqueado_actual: # Solo actualizar si es necesario
                    cursor.execute("UPDATE Usuarios SET intentos_fallidos = 0, bloqueado = 0 WHERE id_usuario = ?", (user_id,))
                    conn.commit()
                    print(f"Login - Intentos fallidos reseteados y cuenta desbloqueada para user_id: {user_id}")

                exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
                secret_key_for_encode = app.config.get('SECRET_KEY')
                print(f"DEBUG login: SECRET_KEY para ENCODE (sesión): '{secret_key_for_encode}'")

                token_payload = {
                    'user_id': user_id, 'email': email, 'rol': rol,
                    'username': username, 'exp': exp_time 
                }
                token = jwt.encode(token_payload, secret_key_for_encode, algorithm="HS256")
                
                print(f"Login - Exitoso para {username}. Token generado. Enviando respuesta.")
                return jsonify({
                    'message': 'Login exitoso', 'token': token, 
                    'rol': rol, 'username': username 
                }), 200
            else:
                # Contraseña incorrecta
                print(f"Login - Contraseña incorrecta para {username}")
                intentos_fallidos_actuales += 1
                max_intentos = APP_CONFIG.get('max_failed_login_attempts', 5)
                intentos_restantes = max_intentos - intentos_fallidos_actuales
                
                mensaje_error_base = "Credenciales inválidas."
                nuevo_estado_bloqueo = bloqueado_actual # Por defecto no cambia

                if intentos_fallidos_actuales >= max_intentos:
                    nuevo_estado_bloqueo = 1 # Bloquear la cuenta (True)
                    cursor.execute("UPDATE Usuarios SET intentos_fallidos = ?, bloqueado = ? WHERE id_usuario = ?", 
                                   (intentos_fallidos_actuales, nuevo_estado_bloqueo, user_id))
                    conn.commit()
                    print(f"Login - Usuario {username} (ID: {user_id}) bloqueado por exceder intentos. Intentos: {intentos_fallidos_actuales}")
                    mensaje_error_base = f"Contraseña incorrecta. Su cuenta ha sido bloqueada tras {intentos_fallidos_actuales} intentos fallidos. Contacte al administrador."
                    return jsonify({
                        'error': mensaje_error_base,
                        'account_locked': True
                    }), 401 # O 403 si prefieres para cuentas bloqueadas
                else:
                    cursor.execute("UPDATE Usuarios SET intentos_fallidos = ? WHERE id_usuario = ?", 
                                   (intentos_fallidos_actuales, user_id))
                    conn.commit()
                    print(f"Login - Usuario {username} (ID: {user_id}) intento fallido {intentos_fallidos_actuales}/{max_intentos}.")
                    mensaje_error_base = f"Credenciales inválidas. Le quedan {intentos_restantes} {'intento' if intentos_restantes == 1 else 'intentos'}."
                    return jsonify({
                        'error': mensaje_error_base,
                        'attempts_made': intentos_fallidos_actuales,
                        'attempts_remaining': intentos_restantes,
                        'account_locked': False
                    }), 401
        
        except Exception as db_e:
            # No cerrar la conexión aquí si se va a usar en finally
            print(f"Error de BD en /login: {str(db_e)}")
            return jsonify({'error': f'Error de base de datos en login: {str(db_e)}'}), 500
        finally:
            if conn: 
                conn.close()
                print("Login - Conexión a BD cerrada.")
    except Exception as e:
        print(f"Error general en /login: {str(e)}")
        return jsonify({'error': f'Error interno del servidor en login: {str(e)}'}), 500


@app.route('/reset_password', methods=['POST'])
def reset_password_request():
    # (Tu código de /reset_password como lo tenías)
    # ... (código de la función /reset_password) ...
    try:
        data = request.get_json()
        if not data: return jsonify({'error': 'No se recibieron datos JSON'}), 400
        email_req = data.get('email') # Renombrado para evitar conflicto con variable 'email' de la función

        if not email_req: return jsonify({'error': 'Correo electrónico es requerido'}), 400

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_usuario FROM Usuarios WHERE email = ?", (email_req,))
            user_db_data = cursor.fetchone()

            if not user_db_data: 
                # No revelar si el correo existe o no por seguridad, pero para depuración es útil.
                print(f"Reset Password - Correo no registrado: {email_req}")
                return jsonify({'error': 'Si el correo está registrado, se enviarán instrucciones.'}), 200 # O 404 si prefieres ser explícito

            user_id = user_db_data[0]
            if send_reset_email(email_req, user_id): # Usando el token generado dentro de send_reset_email
                return jsonify({'message': 'Instrucciones enviadas a su correo electrónico'}), 200
            else:
                return jsonify({'error': 'Error al enviar el correo de restablecimiento'}), 500
        except Exception as db_e:
            if conn: conn.rollback()
            print(f"Error de BD en /reset_password: {str(db_e)}")
            return jsonify({'error': f'Error de base de datos: {str(db_e)}'}), 500
        finally:
            if conn: conn.close()
    except Exception as e:
        print(f"Error general en /reset_password: {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


@app.route('/new_password', methods=['POST'])
def set_new_password():
    print("API /new_password POST: Solicitud recibida.")
    try:
        data = request.get_json()
        if not data:
            print("API /new_password POST: Error - No se recibieron datos JSON.")
            return jsonify({'error': 'No se recibieron datos JSON'}), 400
        
        token_from_request = data.get('token')
        new_password_str = data.get('password')

        print(f"API /new_password POST: Token recibido: {'Sí' if token_from_request else 'No'}, Nueva contraseña recibida: {'Sí' if new_password_str else 'No'}")
        print(f"API /new_password POST: Token a decodificar: '{token_from_request}'")

        if not token_from_request or not new_password_str:
            return jsonify({'error': 'Token y nueva contraseña son requeridos'}), 400

        user_id = None 
        try:
            secret_key_in_use = app.config.get('SECRET_KEY')
            if not secret_key_in_use:
                print("API /new_password POST: CRITICAL SERVER ERROR - app.config['SECRET_KEY'] no está definida.")
                return jsonify({'error': 'Error de configuración del servidor.'}), 500
            print(f"API /new_password POST: Decodificando token. SECRET_KEY usada: '{secret_key_in_use}'")
            
            decoded_token = jwt.decode(token_from_request, secret_key_in_use, algorithms=["HS256"])
            user_id = decoded_token['user_id']
            print(f"API /new_password POST: Token decodificado OK. User ID: {user_id}")

        except jwt.ExpiredSignatureError:
            print("API /new_password POST: Error - El enlace de restablecimiento ha expirado.")
            return jsonify({'error': 'El enlace de restablecimiento ha expirado'}), 401 
        except jwt.InvalidTokenError as ive: 
            print(f"API /new_password POST: Error - Enlace de restablecimiento inválido. Detalles de PyJWT: {str(ive)}")
            return jsonify({'error': 'Enlace de restablecimiento inválido'}), 401 
        except Exception as e_jwt: 
            print(f"API /new_password POST: Error inesperado al decodificar token JWT: {str(e_jwt)}")
            return jsonify({'error': f'Error al procesar el token: {str(e_jwt)}'}), 400
        
        if len(new_password_str) < 3:
            print("API /new_password POST: Error - La nueva contraseña es demasiado corta.")
            return jsonify({'error': 'La contraseña debe tener al menos 3 caracteres.'}), 400

        salt = bcrypt.gensalt()
        hashed_new_password = bcrypt.hashpw(new_password_str.encode('utf-8'), salt)

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            sql_update = """
                UPDATE Usuarios 
                SET password_hash = ?, reset_token = NULL, reset_token_expiry = NULL 
                WHERE id_usuario = ?
            """
            cursor.execute(sql_update, (hashed_new_password, user_id))
            conn.commit()
            
            if cursor.rowcount == 0:
                print(f"API /new_password POST: No se actualizó la contraseña para user_id {user_id} (usuario no encontrado o sin cambios).")
                return jsonify({'error': 'No se pudo actualizar la contraseña, usuario no encontrado o sin cambios necesarios.'}), 404 
            
            print(f"API /new_password POST: Contraseña actualizada exitosamente para user_id {user_id}.")
            return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200
        except pyodbc.Error as db_pyodbc_error:
            if conn: conn.rollback()
            print(f"API /new_password POST: Error de base de datos (pyodbc): {str(db_pyodbc_error)}")
            return jsonify({'error': f'Error de base de datos al actualizar contraseña: {str(db_pyodbc_error)}'}), 500
        except Exception as db_e:
            if conn: conn.rollback()
            print(f"API /new_password POST: Error de base de datos (general): {str(db_e)}")
            return jsonify({'error': f'Error de base de datos al actualizar contraseña: {str(db_e)}'}), 500
        finally:
            if conn:
                conn.close()
                print("API /new_password POST: Conexión a BD cerrada.")
    except Exception as e: 
        print(f"Error general no esperado en /new_password: {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    
# --- DECORADORES ---
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        print(f"API Protegida - @token_required: Cabecera Authorization: {auth_header}")

        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                print(f"API Protegida - @token_required: Token extraído: {token}")
            except IndexError:
                print("API Protegida - @token_required: Error - Formato de token inválido.")
                return jsonify({'error': 'Formato de token inválido ("Bearer <token>")'}), 401
        
        if not token:
            print("API Protegida - @token_required: Error - Token es requerido.")
            return jsonify({'error': 'Token de autorización es requerido'}), 401

        try:
            secret_key_for_decode = app.config.get('SECRET_KEY')
            print(f"API Protegida - @token_required: Decodificando token de sesión. SECRET_KEY usada: '{secret_key_for_decode}'")
            print(f"API Protegida - @token_required: Token de sesión a decodificar: '{token}'")
            
            data = jwt.decode(token, secret_key_for_decode, algorithms=["HS256"])
            decoded_user_rol = data.get('rol')
            decoded_user_id = data.get('user_id')
            # decoded_username = data.get('username') # Si incluiste username en el token de sesión
            print(f"API Protegida - @token_required: Token de sesión OK. Rol: {decoded_user_rol}, ID: {decoded_user_id}")
        except jwt.ExpiredSignatureError:
            print("API Protegida - @token_required: Error - Token de sesión ha expirado.")
            return jsonify({'error': 'Token de sesión ha expirado'}), 401
        except jwt.InvalidTokenError as ive:
            print(f"API Protegida - @token_required: Error - Token de sesión inválido. Detalles: {str(ive)}")
            return jsonify({'error': 'Token de sesión inválido'}), 401
        except Exception as e:
            print(f"API Protegida - @token_required: Excepción al decodificar token de sesión: {str(e)}")
            return jsonify({'error': f'Error al procesar token de sesión: {str(e)}'}), 401
            
        return f(decoded_user_rol=decoded_user_rol, decoded_user_id=decoded_user_id, *args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    @token_required 
    def decorated_admin_function(decoded_user_rol, decoded_user_id, *args, **kwargs):
        print(f"API Protegida - @admin_required: Verificando rol. Rol del token: {decoded_user_rol}")
        if decoded_user_rol != 'Administrador':
            print("API Protegida - @admin_required: Error - Acceso denegado. No es Administrador.")
            return jsonify({'error': 'Acceso denegado. Se requieren permisos de administrador.'}), 403
        
        print(f"API Protegida - @admin_required: Acceso de Admin OK para user_id: {decoded_user_id}")
        return f(admin_user_id_from_token=decoded_user_id, *args, **kwargs)
    return decorated_admin_function


def roles_required(*required_roles):
    def decorator(f):
        @wraps(f)
        @token_required # Primero, se asegura de que el token sea válido y obtiene el rol
        def decorated_function(decoded_user_rol, decoded_user_id, *args, **kwargs):
            
            print(f"API Protegida - @roles_required: Verificando rol '{decoded_user_rol}' contra roles permitidos: {required_roles}")

            # Comprobar si el rol del usuario está en la lista de roles requeridos
            if decoded_user_rol not in required_roles:
                print(f"API Protegida - @roles_required: Acceso denegado para rol '{decoded_user_rol}'.")
                return jsonify({'error': 'Acceso denegado. No tiene los permisos necesarios para esta acción.'}), 403
            
            print(f"API Protegida - @roles_required: Acceso concedido para rol '{decoded_user_rol}'.")
            # Si el rol es válido, se ejecuta la función del endpoint
            return f(decoded_user_rol=decoded_user_rol, decoded_user_id=decoded_user_id, *args, **kwargs)
        return decorated_function
    return decorator



# --- ENDPOINTS DE GESTIÓN DE USUARIOS ---
@app.route('/usuarios', methods=['GET'])
@roles_required('Administrador')
def get_all_usuarios(decoded_user_rol, decoded_user_id):
    print(f"API /usuarios GET: Solicitud recibida por admin con ID: {decoded_user_rol, decoded_user_id}")
    conn = None  # Inicializar a None
    try:
        conn = get_db_connection() # Obtener la conexión
        cursor = conn.cursor()
        # Se incluye 'bloqueado' en la consulta SELECT
        cursor.execute("SELECT id_usuario, username, email, rol, estado, bloqueado FROM Usuarios")
        
        columns = [column[0] for column in cursor.description]
        usuarios = []
        for row in cursor.fetchall():
            user_dict = dict(zip(columns, row))
            user_dict['estado'] = bool(user_dict['estado']) # Asegurar que sea booleano
            user_dict['bloqueado'] = bool(user_dict['bloqueado']) # Asegurar que sea booleano
            usuarios.append(user_dict)
            
        # NO SE CIERRA LA CONEXIÓN AQUÍ (SE ELIMINÓ EL conn.close() DE ESTE LUGAR)
        
        print(f"API /usuarios GET: Devolviendo {len(usuarios)} usuarios.")
        return jsonify(usuarios), 200

    except Exception as e:
        print(f"Error en /usuarios GET: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al obtener usuarios: {str(e)}'}), 500
    finally:
        if conn: # Solo intentar cerrar si la conexión se estableció (conn no es None)
            conn.close()
            print("API /usuarios GET: Conexión a BD cerrada desde el bloque finally.")

@app.route('/usuarios/<int:user_id>/desbloquear', methods=['PUT']) # O podrías usar POST
@roles_required('Administrador') # Solo administradores pueden desbloquear
def desbloquear_usuario(decoded_user_rol, decoded_user_id, user_id):
    print(f"API /usuarios/{user_id}/desbloquear PUT: Solicitud de admin ID {decoded_user_rol, decoded_user_id} para desbloquear usuario ID {user_id}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si el usuario existe primero
        cursor.execute("SELECT bloqueado FROM Usuarios WHERE id_usuario = ?", (user_id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            print(f"API /usuarios/{user_id}/desbloquear PUT: Error - Usuario ID {user_id} no encontrado.")
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # Desbloquear al usuario y resetear los intentos fallidos
        print(f"API /usuarios/{user_id}/desbloquear PUT: Actualizando 'bloqueado = 0' e 'intentos_fallidos = 0'.")
        cursor.execute("UPDATE Usuarios SET bloqueado = 0, intentos_fallidos = 0 WHERE id_usuario = ?", (user_id,))
        conn.commit()
        
        # Aunque cursor.rowcount sea 0 (si ya estaba desbloqueado y con 0 intentos), 
        # el estado final es el deseado. Se considera éxito.
        print(f"API /usuarios/{user_id}/desbloquear PUT: Usuario ID {user_id} desbloqueado exitosamente o ya estaba en el estado deseado.")
        return jsonify({'message': f'Usuario {user_id} desbloqueado exitosamente.'}), 200

    except Exception as e:
        if conn: 
            try:
                conn.rollback()
                print(f"API /usuarios/{user_id}/desbloquear PUT: Rollback realizado debido a error.")
            except Exception as rb_e:
                print(f"API /usuarios/{user_id}/desbloquear PUT: Error durante el rollback: {rb_e}")
        print(f"Error en /usuarios/{user_id}/desbloquear PUT: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al desbloquear usuario: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print(f"API /usuarios/{user_id}/desbloquear PUT: Conexión a BD cerrada desde el bloque finally.")

@app.route('/usuarios/<int:user_id>/estado', methods=['PUT'])
@roles_required('Administrador')
def cambiar_estado_usuario(decoded_user_rol, decoded_user_id, user_id):
    # (Tu código de /usuarios/<id>/estado PUT como lo tenías)
    # ... (código de la función /usuarios/<id>/estado PUT) ...
    print(f"API /usuarios/{user_id}/estado PUT: Admin ID {decoded_user_rol, decoded_user_id} cambiando estado de usuario ID {user_id}")
    try:
        data = request.get_json()
        if not data or 'estado' not in data or not isinstance(data['estado'], bool):
            print(f"API /usuarios/{user_id}/estado PUT: Error - Datos inválidos: {data}")
            return jsonify({'error': "Datos inválidos. Se requiere 'estado' (true/false)."}), 400

        nuevo_estado_bool = data['estado']
        nuevo_estado_bit = 1 if nuevo_estado_bool else 0
        
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id_usuario FROM Usuarios WHERE id_usuario = ?", (user_id,))
            if not cursor.fetchone():
                print(f"API /usuarios/{user_id}/estado PUT: Error - Usuario ID {user_id} no encontrado.")
                return jsonify({'error': 'Usuario no encontrado'}), 404

            cursor.execute("UPDATE Usuarios SET estado = ? WHERE id_usuario = ?", (nuevo_estado_bit, user_id))
            conn.commit()
            
            if cursor.rowcount == 0:
                print(f"API /usuarios/{user_id}/estado PUT: No se actualizó fila para usuario ID {user_id}.")
                return jsonify({'message': f'Estado del usuario {user_id} no requirió cambios.'}), 200 
                
            print(f"API /usuarios/{user_id}/estado PUT: Estado del usuario ID {user_id} cambiado a {nuevo_estado_bool}.")
            return jsonify({'message': f'Estado del usuario {user_id} actualizado a {"Activo" if nuevo_estado_bool else "Inactivo"}.'}), 200
        except Exception as db_e:
            if conn: conn.rollback()
            print(f"Error de BD en /usuarios/{user_id}/estado PUT: {str(db_e)}")
            return jsonify({'error': f'Error de BD: {str(db_e)}'}), 500
        finally:
            if conn: conn.close()
    except Exception as e:
        print(f"Error general en /usuarios/{user_id}/estado PUT: {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/usuarios/<int:user_id>', methods=['PUT'])
@roles_required('Administrador')
def actualizar_usuario(decoded_user_rol, decoded_user_id, user_id):
    # (Tu código de /usuarios/<id> PUT como lo tenías)
    # ... (código de la función /usuarios/<id> PUT para actualizar datos) ...
    print(f"API /usuarios/{user_id} PUT (actualizar datos): Admin ID {decoded_user_rol, decoded_user_id} actualizando usuario ID {user_id}")
    try:
        data = request.get_json()
        if not data: return jsonify({'error': "No se recibieron datos JSON."}), 400

        nuevo_username = data.get('username')
        nuevo_email = data.get('email')
        nuevo_rol = data.get('rol')

        if not nuevo_username and not nuevo_email and not nuevo_rol:
            return jsonify({'error': "No se proporcionaron datos para actualizar."}), 400
        
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT username, email, rol FROM Usuarios WHERE id_usuario = ?", (user_id,))
            usuario_actual = cursor.fetchone()
            if not usuario_actual: return jsonify({'error': 'Usuario no encontrado'}), 404

            update_fields = []
            params = []

            if nuevo_username and nuevo_username != usuario_actual[0]:
                cursor.execute("SELECT id_usuario FROM Usuarios WHERE username = ? AND id_usuario != ?", (nuevo_username, user_id))
                if cursor.fetchone(): return jsonify({'error': f"Username '{nuevo_username}' ya en uso."}), 409
                update_fields.append("username = ?")
                params.append(nuevo_username)
            
            if nuevo_email and nuevo_email != usuario_actual[1]:
                if '@' not in nuevo_email or '.' not in nuevo_email: return jsonify({'error': 'Email inválido'}), 400
                cursor.execute("SELECT id_usuario FROM Usuarios WHERE email = ? AND id_usuario != ?", (nuevo_email, user_id))
                if cursor.fetchone(): return jsonify({'error': f"Email '{nuevo_email}' ya en uso."}), 409
                update_fields.append("email = ?")
                params.append(nuevo_email)

            if nuevo_rol and nuevo_rol != usuario_actual[2]:
                roles_validos = ['Administrador', 'Empleado', 'Supervisor'] 
                if nuevo_rol not in roles_validos: return jsonify({'error': f"Rol '{nuevo_rol}' inválido."}), 400
                update_fields.append("rol = ?")
                params.append(nuevo_rol)
            
            if not update_fields:
                return jsonify({'message': "No hay cambios para aplicar."}), 200

            query = f"UPDATE Usuarios SET {', '.join(update_fields)} WHERE id_usuario = ?"
            params.append(user_id)
            
            print(f"API /usuarios/{user_id} PUT (actualizar datos): Query: {query}, Params: {params}")
            cursor.execute(query, tuple(params))
            conn.commit()
            
            print(f"API /usuarios/{user_id} PUT (actualizar datos): Usuario ID {user_id} actualizado.")
            return jsonify({'message': f'Usuario {user_id} actualizado correctamente.'}), 200
        
        except pyodbc.IntegrityError as ie:
            if conn: conn.rollback()
            print(f"Error de Integridad en /usuarios/{user_id} PUT (actualizar datos): {str(ie)}")
            return jsonify({'error': f'Error de integridad de datos: {str(ie)}'}), 409
        except Exception as db_e:
            if conn: conn.rollback()
            print(f"Error de BD en /usuarios/{user_id} PUT (actualizar datos): {str(db_e)}")
            return jsonify({'error': f'Error de BD: {str(db_e)}'}), 500
        finally:
            if conn: conn.close()
    except Exception as e:
        print(f"Error general en /usuarios/{user_id} PUT (actualizar datos): {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/usuarios/<int:user_id>', methods=['GET'])
@roles_required('Administrador')
def get_usuario_por_id(decoded_user_rol, decoded_user_id, user_id):
    # (Tu código de /usuarios/<id> GET como lo tenías)
    # ... (código de la función /usuarios/<id> GET) ...
    print(f"API /usuarios/{user_id} GET: Admin ID {decoded_user_rol, decoded_user_id} solicitando usuario ID {user_id}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, username, email, rol, estado FROM Usuarios WHERE id_usuario = ?", (user_id,))
        
        columns = [column[0] for column in cursor.description]
        user_data_row = cursor.fetchone()

        if user_data_row:
            usuario = dict(zip(columns, user_data_row))
            print(f"API /usuarios/{user_id} GET: Usuario ID {user_id} encontrado: {usuario}")
            return jsonify(usuario), 200
        else:
            print(f"API /usuarios/{user_id} GET: Error - Usuario ID {user_id} no encontrado.")
            return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        print(f"Error en /usuarios/{user_id} GET: {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    finally:
        if conn: conn.close()



# --- ENDPOINTS DE CONFIGURACIONES ---
@app.route('/configuraciones', methods=['GET'])
@roles_required('Administrador', 'Supervisor')
def get_configuraciones(decoded_user_rol, decoded_user_id): # El nombre del argumento debe coincidir con lo que pasa el decorador
    print(f"API GET /configuraciones: Solicitud de Admin ID {decoded_user_rol, decoded_user_id}. Config actual: {APP_CONFIG}")
    # Devolver una copia para evitar modificar el original directamente si se pasa por referencia en algunos contextos Python
    return jsonify(APP_CONFIG.copy()), 200

@app.route('/configuraciones', methods=['PUT'])
@roles_required('Administrador', 'Supervisor')
def update_configuraciones(decoded_user_rol, decoded_user_id): # El nombre del argumento debe coincidir
    global APP_CONFIG # Necesario para modificar la variable global
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    print(f"API PUT /configuraciones: Admin ID {decoded_user_rol, decoded_user_id} actualizando. Datos recibidos: {data}")

    updated_fields = []
    # Guardar una copia de la configuración actual para poder revertir en caso de error
    original_config_copy = APP_CONFIG.copy() 

    try:
        new_expiry = data.get('reset_token_expiry_minutes')
        new_attempts = data.get('max_failed_login_attempts')
        new_low_stock_threshold = data.get('global_low_stock_threshold') # NUEVO campo

        if new_expiry is not None:
            new_expiry_int = int(new_expiry) # Puede lanzar ValueError
            if new_expiry_int <= 0:
                # Para ser más específico, este error lo capturará el ValueError general del try-except
                raise ValueError("reset_token_expiry_minutes debe ser un entero positivo.")
            APP_CONFIG['reset_token_expiry_minutes'] = new_expiry_int
            updated_fields.append('Duración del token de reseteo')
        
        if new_attempts is not None:
            new_attempts_int = int(new_attempts) # Puede lanzar ValueError
            if new_attempts_int <= 0:
                raise ValueError("max_failed_login_attempts debe ser un entero positivo.")
            APP_CONFIG['max_failed_login_attempts'] = new_attempts_int
            updated_fields.append('Máximos intentos de login')

        # NUEVO: Manejar la actualización del umbral global de stock bajo
        if new_low_stock_threshold is not None:
            new_low_stock_threshold_int = int(new_low_stock_threshold) # Puede lanzar ValueError
            if new_low_stock_threshold_int < 0: # Permitimos 0, si no se quiere resaltado o si stock 0 ya es "bajo"
                raise ValueError("global_low_stock_threshold debe ser un entero no negativo.")
            APP_CONFIG['global_low_stock_threshold'] = new_low_stock_threshold_int
            updated_fields.append('Umbral global de stock bajo')
            
        if not updated_fields:
            # Si no se envió ninguno de los campos esperados en el JSON
            return jsonify({'error': 'No se proporcionaron campos válidos para actualizar (reset_token_expiry_minutes, max_failed_login_attempts, global_low_stock_threshold).'}), 400

        print(f"API PUT /configuraciones: Nuevas configuraciones aplicadas: {APP_CONFIG}")
        return jsonify({'message': f'Configuraciones ({", ".join(updated_fields)}) actualizadas exitosamente.'}), 200
        
    except ValueError as ve: # Captura errores de conversión int() o de las validaciones lógicas que usan raise ValueError
        APP_CONFIG = original_config_copy # Revertir a la config original si algo falla durante la actualización
        print(f"API PUT /configuraciones: Error de valor en los datos - {str(ve)}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        APP_CONFIG = original_config_copy # Revertir en caso de otros errores inesperados
        print(f"API PUT /configuraciones: Error inesperado - {str(e)}")
        return jsonify({'error': f'Error interno del servidor al actualizar configuraciones: {str(e)}'}), 500



# --- ENDPOINTS DE MATERIALES/INVENTARIO---
@app.route('/materiales', methods=['GET'])
@roles_required ('Administrador', 'Supervisor') # O @admin_required si solo los admins pueden ver la lista completa
def get_todos_los_materiales(decoded_user_rol, decoded_user_id): # Argumentos del decorador @token_required
    # Si usas @admin_required, el argumento sería admin_user_id_from_token
    print(f"API GET /materiales: Solicitud recibida por usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Consulta con LEFT JOIN para incluir información del proveedor y unidad
        sql_query = """
            SELECT 
                m.id_material, 
                m.nombre, 
                m.descripcion, 
                m.cantidad, 
                m.precio_unitario,
                m.precio_compra,
                m.precio_venta,
                m.porcentaje_ganancia,
                m.fecha_ultima_actualizacion,
                m.id_proveedor,
                m.id_unidad,
                p.nombre_proveedor,
                p.ruc,
                u.nombre_unidad,
                u.abreviatura AS abreviatura_unidad
            FROM Materiales m
            LEFT JOIN Proveedores p ON m.id_proveedor = p.id_proveedor
            LEFT JOIN Unidades_de_Medida u ON m.id_unidad = u.id_unidad
            ORDER BY m.nombre ASC 
        """
        cursor.execute(sql_query)
        
        columns = [column[0] for column in cursor.description]
        materiales = []
        for row in cursor.fetchall():
            material_dict = dict(zip(columns, row))
            # Asegurar que los campos numéricos y de fecha se manejen bien para JSON
            if 'cantidad' in material_dict and material_dict['cantidad'] is not None:
                material_dict['cantidad'] = int(material_dict['cantidad'])
            if 'precio_unitario' in material_dict and material_dict['precio_unitario'] is not None:
                material_dict['precio_unitario'] = float(material_dict['precio_unitario'])
            if 'precio_compra' in material_dict and material_dict['precio_compra'] is not None:
                material_dict['precio_compra'] = float(material_dict['precio_compra'])
            if 'precio_venta' in material_dict and material_dict['precio_venta'] is not None:
                material_dict['precio_venta'] = float(material_dict['precio_venta'])
            if 'porcentaje_ganancia' in material_dict and material_dict['porcentaje_ganancia'] is not None:
                material_dict['porcentaje_ganancia'] = int(material_dict['porcentaje_ganancia'])
            if 'fecha_ultima_actualizacion' in material_dict and material_dict['fecha_ultima_actualizacion'] is not None:
                # Convertir datetime a string ISO para JSON, si no lo hace automáticamente el driver/jsonify
                material_dict['fecha_ultima_actualizacion'] = material_dict['fecha_ultima_actualizacion'].isoformat()
            
            materiales.append(material_dict)
            
        print(f"API GET /materiales: Devolviendo {len(materiales)} materiales.")
        return jsonify(materiales), 200

    except Exception as e:
        print(f"Error en GET /materiales: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al obtener materiales: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API GET /materiales: Conexión a BD cerrada desde el bloque finally.")
            
@app.route('/materiales', methods=['POST']) # ¡ASEGÚRATE QUE methods=['POST'] ESTÉ AQUÍ!
@roles_required ('Administrador', 'Supervisor')
def crear_nuevo_material(decoded_user_rol, decoded_user_id): # El argumento depende del decorador
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    nombre = data.get('nombre')
    descripcion = data.get('descripcion') # Puede ser None o vacío si es opcional
    
    # NUEVO: Soporte para sistema de doble precio
    precio_compra_str = data.get('precio_compra')
    porcentaje_ganancia = data.get('porcentaje_ganancia')
    id_proveedor = data.get('id_proveedor')  # Proveedor opcional
    
    # Compatibilidad con código antiguo que usa precio_unitario
    if precio_compra_str is None:
        precio_compra_str = data.get('precio_unitario')
    
    cantidad_inicial = 0 # Los nuevos materiales se crean con stock 0
    fecha_actual = datetime.datetime.now()

    # Validaciones básicas
    if not nombre:
        return jsonify({'error': 'El nombre del material es requerido'}), 400
    if precio_compra_str is None:
        return jsonify({'error': 'El precio de compra es requerido'}), 400

    try:
        precio_compra = float(precio_compra_str)
        if precio_compra < 0:
            return jsonify({'error': 'El precio de compra no puede ser negativo'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'El precio de compra debe ser un número válido'}), 400

    # Validar y calcular precio de venta
    if porcentaje_ganancia is None:
        porcentaje_ganancia = 20  # Default 20%
    
    try:
        porcentaje_ganancia = int(porcentaje_ganancia)
        if porcentaje_ganancia < 5 or porcentaje_ganancia > 50:
            return jsonify({'error': 'El porcentaje de ganancia debe estar entre 5% y 50%'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'El porcentaje de ganancia debe ser un número válido'}), 400
    
    # Calcular precio de venta automáticamente
    precio_venta = round(precio_compra * (1 + porcentaje_ganancia / 100), 2)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Validar que el proveedor existe si se proporciona
        if id_proveedor:
            cursor.execute("SELECT id_proveedor FROM Proveedores WHERE id_proveedor = ?", (id_proveedor,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'error': f'El proveedor con ID {id_proveedor} no existe'}), 404

        # Opcional: Verificar si ya existe un material con el mismo nombre
        cursor.execute("SELECT id_material FROM Materiales WHERE nombre = ?", (nombre,))
        if cursor.fetchone():
            conn.close() # Cerrar conexión antes de retornar
            return jsonify({'error': f'Ya existe un material con el nombre "{nombre}"'}), 409 # 409 Conflict
        
        sql_insert = """
            INSERT INTO Materiales (nombre, descripcion, cantidad, precio_unitario, 
                                    precio_compra, precio_venta, porcentaje_ganancia,
                                    fecha_ultima_actualizacion, id_usuario_ultima_actualizacion, id_proveedor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        # Mantener precio_unitario sincronizado con precio_compra por compatibilidad
        cursor.execute(sql_insert, 
                       (nombre, descripcion, cantidad_inicial, precio_compra,
                        precio_compra, precio_venta, porcentaje_ganancia,
                        fecha_actual, decoded_user_id, id_proveedor))
        conn.commit()

        print(f"API POST /materiales: Material '{nombre}' creado por admin ID {decoded_user_rol, decoded_user_id}. Precio compra: {precio_compra}, Precio venta: {precio_venta}, Margen: {porcentaje_ganancia}%")
        return jsonify({
            'message': f'Material "{nombre}" creado exitosamente.',
            'precio_compra': precio_compra,
            'precio_venta': precio_venta,
            'porcentaje_ganancia': porcentaje_ganancia
        }), 201 # 201 Created

    except pyodbc.Error as db_err: # Captura errores específicos de pyodbc
        if conn: conn.rollback()
        print(f"Error de BD en POST /materiales: {str(db_err)}")
        return jsonify({'error': f'Error de base de datos al crear material: {str(db_err)}'}), 500
    except Exception as e:
        if conn: conn.rollback() # Asegurar rollback si la conexión se estableció
        print(f"Error general en POST /materiales: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al crear material: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API POST /materiales: Conexión a BD cerrada.")
                        
@app.route('/inventory/entry', methods=['POST'])
@roles_required ('Administrador', 'Supervisor')
def registrar_entrada_inventario(decoded_user_rol, decoded_user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    print(f"API /inventory/entry POST: Admin ID {decoded_user_rol, decoded_user_id} registrando entrada. Datos: {data}")

    nombre_material = data.get('nombre_material') # CAMBIO: Buscar por nombre
    cantidad_entrada = data.get('cantidad_entrada')
    # precio_unitario_entrada = data.get('precio_unitario_entrada') # Opcional

    if not nombre_material or cantidad_entrada is None: # CAMBIO: nombre_material es requerido
        return jsonify({'error': 'Se requiere nombre_material y cantidad_entrada'}), 400

    try:
        cantidad_entrada = int(cantidad_entrada)
        if cantidad_entrada <= 0:
            return jsonify({'error': 'cantidad_entrada debe ser un número positivo'}), 400
    except ValueError:
        return jsonify({'error': 'cantidad_entrada debe ser un número entero'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # CAMBIO: Verificar si el material existe por nombre y obtener su ID y stock
        cursor.execute("SELECT id_material, cantidad FROM Materiales WHERE nombre = ?", (nombre_material,))
        material_actual_data = cursor.fetchone()

        if not material_actual_data:
            conn.close() # Cerrar conexión si el material no se encuentra
            return jsonify({'error': f'Material con nombre "{nombre_material}" no encontrado'}), 404
        
        id_material = material_actual_data[0]
        stock_actual = material_actual_data[1]
        
        nuevo_stock = stock_actual + cantidad_entrada
        fecha_actualizacion = datetime.datetime.now()

        sql_update = """
            UPDATE Materiales 
            SET cantidad = ?, fecha_ultima_actualizacion = ?, id_usuario_ultima_actualizacion = ?
            WHERE id_material = ? 
        """
        # Si se permite actualizar precio_unitario, se añadiría a este UPDATE y a los params
        cursor.execute(sql_update, (nuevo_stock, fecha_actualizacion, decoded_user_id, id_material))
        conn.commit()

        if cursor.rowcount == 0:
            conn.close() 
            return jsonify({'error': 'No se pudo actualizar el inventario del material'}), 500

        print(f"API /inventory/entry POST: Entrada registrada para material '{nombre_material}' (ID: {id_material}). Nuevo stock: {nuevo_stock}")
        return jsonify({
            'message': 'Entrada de inventario registrada exitosamente',
            'id_material': id_material,
            'nombre_material': nombre_material,
            'cantidad_entrada': cantidad_entrada,
            'nuevo_stock': nuevo_stock
        }), 200

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en /inventory/entry: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al registrar entrada: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API /inventory/entry POST: Conexión a BD cerrada.")

@app.route('/inventory/exit', methods=['POST'])
@roles_required ('Administrador', 'Supervisor') 
def registrar_salida_inventario (decoded_user_rol, decoded_user_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    print(f"API /inventory/exit POST: Admin ID {decoded_user_rol, decoded_user_id} registrando salida. Datos: {data}")

    nombre_material = data.get('nombre_material') # CAMBIO: Buscar por nombre
    cantidad_salida = data.get('cantidad_salida')
    # id_orden_trabajo = data.get('id_orden_trabajo') # Opcional

    if not nombre_material or cantidad_salida is None: # CAMBIO: nombre_material es requerido
        return jsonify({'error': 'Se requiere nombre_material y cantidad_salida'}), 400

    try:
        cantidad_salida = int(cantidad_salida)
        if cantidad_salida <= 0:
            return jsonify({'error': 'cantidad_salida debe ser un número positivo'}), 400
    except ValueError:
        return jsonify({'error': 'cantidad_salida debe ser un número entero'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # CAMBIO: Verificar si el material existe por nombre y obtener su ID y stock
        cursor.execute("SELECT id_material, cantidad FROM Materiales WHERE nombre = ?", (nombre_material,))
        material_actual_data = cursor.fetchone()

        if not material_actual_data:
            conn.close()
            return jsonify({'error': f'Material con nombre "{nombre_material}" no encontrado'}), 404
        
        id_material = material_actual_data[0]
        stock_actual = material_actual_data[1]

        if stock_actual < cantidad_salida:
            conn.close()
            print(f"API /inventory/exit POST: Stock insuficiente para material '{nombre_material}' (ID: {id_material}). Solicitado: {cantidad_salida}, Disponible: {stock_actual}")
            return jsonify({
                'error': 'Existencias insuficientes para registrar la salida',
                'nombre_material': nombre_material,
                'stock_actual': stock_actual,
                'cantidad_solicitada': cantidad_salida
            }), 400
        
        nuevo_stock = stock_actual - cantidad_salida
        fecha_actualizacion = datetime.datetime.now()

        sql_update = """
            UPDATE Materiales 
            SET cantidad = ?, fecha_ultima_actualizacion = ?, id_usuario_ultima_actualizacion = ?
            WHERE id_material = ? 
        """
        cursor.execute(sql_update, (nuevo_stock, fecha_actualizacion, decoded_user_id, id_material))
        
        # Lógica opcional para DetalleOrdenMateriales si es necesario
        # if id_orden_trabajo:
        #     # ... (código para insertar en DetalleOrdenMateriales) ...

        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'No se pudo actualizar el inventario del material'}), 500

        print(f"API /inventory/exit POST: Salida registrada para material '{nombre_material}' (ID: {id_material}). Nuevo stock: {nuevo_stock}")
        return jsonify({
            'message': 'Salida de inventario registrada exitosamente',
            'id_material': id_material, 
            'nombre_material': nombre_material,
            'cantidad_salida': cantidad_salida,
            'nuevo_stock': nuevo_stock
        }), 200

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en /inventory/exit: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al registrar salida: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API /inventory/exit POST: Conexión a BD cerrada.")

@app.route('/materiales/<int:id_material>', methods=['DELETE'])
@roles_required('Administrador', 'Supervisor')
def eliminar_material(decoded_user_rol, decoded_user_id, id_material):
    print(f"API DELETE /materiales/{id_material}: Solicitud de admin ID {decoded_user_rol, decoded_user_id}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Paso 1: Verificar si el material existe y si tiene stock
        cursor.execute("SELECT nombre, cantidad FROM Materiales WHERE id_material = ?", (id_material,))
        material = cursor.fetchone()

        if not material:
            print(f"API DELETE /materiales/{id_material}: Material no encontrado.")
            return jsonify({'error': 'Material no encontrado'}), 404

        nombre_material = material[0]
        stock_actual = material[1]

        # VERIFICACIÓN IMPORTANTE: No permitir eliminar si hay stock.
        if stock_actual > 0:
            print(f"API DELETE /materiales/{id_material}: Intento de eliminar material '{nombre_material}' con stock ({stock_actual}). Denegado.")
            return jsonify({'error': f'No se puede eliminar el material "{nombre_material}" porque aún tiene {stock_actual} unidades en stock. Primero ajuste el stock a cero.'}), 409 # 409 Conflict

        # (Opcional: Verificar aquí si el material tiene dependencias en DetalleOrdenMateriales u otras tablas)
        # Ejemplo:
        # cursor.execute("SELECT COUNT(*) FROM DetalleOrdenMateriales WHERE id_material = ?", (id_material,))
        # if cursor.fetchone()[0] > 0:
        #     # if conn: conn.close() # Considerar cerrar aquí si no se usa finally en este sub-bloque
        #     return jsonify({'error': 'Este material está referenciado en órdenes de trabajo y no puede ser eliminado.'}), 409


        # Paso 2: Si las verificaciones pasan, proceder a eliminar
        cursor.execute("DELETE FROM Materiales WHERE id_material = ?", (id_material,))
        conn.commit()

        if cursor.rowcount == 0:
            # Esto es improbable si la verificación de existencia pasó, pero es un control.
            print(f"API DELETE /materiales/{id_material}: No se eliminó ninguna fila (material no encontrado después de la verificación inicial o ya eliminado).")
            return jsonify({'error': 'No se pudo eliminar el material o ya no existía.'}), 404 
        
        print(f"API DELETE /materiales/{id_material}: Material '{nombre_material}' (ID: {id_material}) eliminado exitosamente.")
        return jsonify({'message': f'Material "{nombre_material}" (ID: {id_material}) eliminado exitosamente.'}), 200

    except pyodbc.IntegrityError as ie: 
        if conn: conn.rollback()
        print(f"Error de Integridad en DELETE /materiales/{id_material}: {str(ie)}")
        # Este error es común si hay claves foráneas apuntando a este material y no están configuradas para ON DELETE SET NULL o CASCADE
        return jsonify({'error': f'Error de integridad: No se puede eliminar el material porque está referenciado en otros registros (ej. órdenes de trabajo). Detalles: {str(ie)}'}), 409
    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en DELETE /materiales/{id_material}: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al eliminar material: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print(f"API DELETE /materiales/{id_material}: Conexión a BD cerrada desde el bloque finally.")


# --- Endpoint: GET /materiales/<id> - Obtener un material específico ---
@app.route('/materiales/<int:id_material>', methods=['GET'])
@roles_required('Administrador', 'Supervisor', 'Encargado de Inventario')
def get_material_por_id(decoded_user_rol, decoded_user_id, id_material):
    print(f"API GET /materiales/{id_material}: Usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql_query = """
            SELECT 
                m.id_material, 
                m.nombre, 
                m.descripcion, 
                m.cantidad, 
                m.precio_unitario,
                m.precio_compra,
                m.precio_venta,
                m.porcentaje_ganancia,
                m.fecha_ultima_actualizacion,
                m.id_proveedor,
                p.nombre_proveedor,
                p.ruc
            FROM Materiales m
            LEFT JOIN Proveedores p ON m.id_proveedor = p.id_proveedor
            WHERE m.id_material = ?
        """
        cursor.execute(sql_query, (id_material,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': 'Material no encontrado'}), 404
        
        columns = [column[0] for column in cursor.description]
        material = dict(zip(columns, row))
        
        # Convertir tipos para JSON
        if 'cantidad' in material and material['cantidad'] is not None:
            material['cantidad'] = int(material['cantidad'])
        if 'precio_unitario' in material and material['precio_unitario'] is not None:
            material['precio_unitario'] = float(material['precio_unitario'])
        if 'precio_compra' in material and material['precio_compra'] is not None:
            material['precio_compra'] = float(material['precio_compra'])
        if 'precio_venta' in material and material['precio_venta'] is not None:
            material['precio_venta'] = float(material['precio_venta'])
        if 'porcentaje_ganancia' in material and material['porcentaje_ganancia'] is not None:
            material['porcentaje_ganancia'] = int(material['porcentaje_ganancia'])
        if 'fecha_ultima_actualizacion' in material and material['fecha_ultima_actualizacion'] is not None:
            material['fecha_ultima_actualizacion'] = material['fecha_ultima_actualizacion'].isoformat()
        
        return jsonify(material), 200
    
    except Exception as e:
        print(f"Error en GET /materiales/{id_material}: {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()


# --- Endpoint: PUT /materiales/<id> - Actualizar un material ---
@app.route('/materiales/<int:id_material>', methods=['PUT'])
@roles_required('Administrador', 'Supervisor')
def actualizar_material(decoded_user_rol, decoded_user_id, id_material):
    print(f"API PUT /materiales/{id_material}: Usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400
    
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    
    # NUEVO: Soporte para sistema de doble precio
    precio_compra = data.get('precio_compra')
    porcentaje_ganancia = data.get('porcentaje_ganancia')
    id_proveedor = data.get('id_proveedor')
    
    # Compatibilidad con código antiguo
    if precio_compra is None:
        precio_compra = data.get('precio_unitario')
    
    # Validaciones
    if not nombre:
        return jsonify({'error': 'El nombre del material es requerido'}), 400
    if precio_compra is None:
        return jsonify({'error': 'El precio de compra es requerido'}), 400
    
    try:
        precio_compra = float(precio_compra)
        if precio_compra < 0:
            return jsonify({'error': 'El precio de compra no puede ser negativo'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'El precio de compra debe ser un número válido'}), 400
    
    # Validar y calcular precio de venta
    if porcentaje_ganancia is None:
        porcentaje_ganancia = 20  # Default 20%
    
    try:
        porcentaje_ganancia = int(porcentaje_ganancia)
        if porcentaje_ganancia < 5 or porcentaje_ganancia > 50:
            return jsonify({'error': 'El porcentaje de ganancia debe estar entre 5% y 50%'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'El porcentaje de ganancia debe ser un número válido'}), 400
    
    # Calcular precio de venta automáticamente
    precio_venta = round(precio_compra * (1 + porcentaje_ganancia / 100), 2)
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el material existe
        cursor.execute("SELECT id_material FROM Materiales WHERE id_material = ?", (id_material,))
        if not cursor.fetchone():
            return jsonify({'error': 'Material no encontrado'}), 404
        
        # Validar que el proveedor existe si se proporciona
        if id_proveedor:
            cursor.execute("SELECT id_proveedor FROM Proveedores WHERE id_proveedor = ?", (id_proveedor,))
            if not cursor.fetchone():
                return jsonify({'error': f'El proveedor con ID {id_proveedor} no existe'}), 404
        
        # Actualizar el material
        sql_update = """
            UPDATE Materiales 
            SET nombre = ?, 
                descripcion = ?, 
                precio_unitario = ?,
                precio_compra = ?,
                precio_venta = ?,
                porcentaje_ganancia = ?,
                id_proveedor = ?,
                fecha_ultima_actualizacion = ?,
                id_usuario_ultima_actualizacion = ?
            WHERE id_material = ?
        """
        fecha_actual = datetime.datetime.now()
        cursor.execute(sql_update, (nombre, descripcion, precio_compra, 
                                   precio_compra, precio_venta, porcentaje_ganancia,
                                   id_proveedor, fecha_actual, decoded_user_id, id_material))
        conn.commit()
        
        print(f"API PUT /materiales/{id_material}: Material actualizado exitosamente. Precio compra: {precio_compra}, Precio venta: {precio_venta}, Margen: {porcentaje_ganancia}%")
        return jsonify({
            'message': f'Material "{nombre}" actualizado exitosamente.',
            'precio_compra': precio_compra,
            'precio_venta': precio_venta,
            'porcentaje_ganancia': porcentaje_ganancia
        }), 200
    
    except pyodbc.Error as db_err:
        if conn: conn.rollback()
        print(f"Error de BD en PUT /materiales/{id_material}: {str(db_err)}")
        return jsonify({'error': f'Error de base de datos: {str(db_err)}'}), 500
    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en PUT /materiales/{id_material}: {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()


# --- ENDPOINTS DE GESTION DE EMPLEADOS---
@app.route('/empleados', methods=['GET'])
@roles_required('Administrador')
def get_todos_los_empleados(decoded_user_rol, decoded_user_id):
    print(f"API GET /empleados: Solicitud recibida por usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Seleccionar solo empleados activos para asignarlos a nuevas órdenes
        # Se seleccionan los campos que el frontend necesita para el combobox (ID y nombre)
        sql_query = "SELECT id_empleado, nombre, rol FROM Empleados WHERE estado = 1 ORDER BY nombre ASC"
        cursor.execute(sql_query)
        
        columns = [column[0] for column in cursor.description]
        empleados = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        print(f"API GET /empleados: Devolviendo {len(empleados)} empleados activos.")
        return jsonify(empleados), 200

    except Exception as e:
        print(f"Error en GET /empleados: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al obtener empleados: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API GET /empleados: Conexión a BD cerrada desde el bloque finally.")

@app.route('/empleados', methods=['POST'])
@roles_required('Administrador')
def registrar_empleado(decoded_user_rol, decoded_user_id):
    print(f"API POST /empleados: Solicitud de admin ID {decoded_user_rol, decoded_user_id} para registrar nuevo empleado.")
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    # Obtener datos del frontend
    nombre = data.get('nombre')
    cedula = data.get('cedula')
    rol = data.get('rol')
    telefono = data.get('telefono')
    fecha_contratacion_str = data.get('fecha_contratacion')

    # Validación de datos de entrada
    if not all([nombre, cedula, rol, telefono, fecha_contratacion_str]):
        return jsonify({'error': 'Faltan campos requeridos (nombre, cedula, rol, telefono, fecha_contratacion).'}), 400

    # Validación y conversión de la fecha
    try:
        fecha_contratacion = datetime.date.fromisoformat(fecha_contratacion_str)
    except (ValueError, TypeError):
        return jsonify({'error': 'El formato de fecha_contratacion es inválido. Use AAAA-MM-DD.'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si la cédula ya existe para evitar duplicados
        cursor.execute("SELECT id_empleado FROM Empleados WHERE cedula = ?", (cedula,))
        if cursor.fetchone():
            return jsonify({'error': 'La cédula ya está registrada para otro empleado.'}), 409 # Conflict

        # Preparar el INSERT a la tabla Empleados. El estado por defecto es 1 (activo).
        sql_insert = "INSERT INTO Empleados (nombre, cedula, rol, telefono, fecha_contratacion) VALUES (?, ?, ?, ?, ?)"
        params = (nombre, cedula, rol, telefono, fecha_contratacion)
        
        cursor.execute(sql_insert, params)
        
        # Obtener el ID del empleado recién creado
        cursor.execute("SELECT @@IDENTITY AS id;")
        nuevo_empleado_id = cursor.fetchone()[0]
        
        conn.commit()
        
        print(f"API POST /empleados: Empleado creado con ID: {nuevo_empleado_id}")
        return jsonify({
            'message': 'Empleado registrado exitosamente.',
            'id_empleado_creado': nuevo_empleado_id
        }), 201 # 201 Created

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en POST /empleados: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al registrar el empleado: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API POST /empleados: Conexión a BD cerrada.")


# --- ENDPOINTS DE GESTION DE CLIENTES---
@app.route('/clientes', methods=['GET'])
@roles_required('Administrador', 'Supervisor')
def get_todos_los_clientes(decoded_user_rol, decoded_user_id):
    print(f"API GET /clientes: Solicitud recibida por usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Seleccionar solo clientes activos
        # Se seleccionan los campos que el frontend necesita (ID y nombre)
        sql_query = "SELECT id_cliente, nombre FROM Clientes WHERE estado = 1 ORDER BY nombre ASC"
        cursor.execute(sql_query)
        
        columns = [column[0] for column in cursor.description]
        clientes = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        print(f"API GET /clientes: Devolviendo {len(clientes)} clientes activos.")
        return jsonify(clientes), 200

    except Exception as e:
        print(f"Error en GET /clientes: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al obtener clientes: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API GET /clientes: Conexión a BD cerrada desde el bloque finally.")

@app.route('/clientes', methods=['POST'])
@roles_required('Administrador', 'Supervisor')
def registrar_cliente(decoded_user_rol, decoded_user_id):
    print(f"API POST /clientes: Solicitud de admin ID {decoded_user_rol, decoded_user_id} para registrar nuevo cliente.")
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    # Obtener datos del frontend
    nombre = data.get('nombre')
    cedula = data.get('cedula')
    telefono = data.get('telefono')
    email = data.get('email')

    # Validación de datos de entrada
    if not all([nombre, cedula, telefono, email]):
        return jsonify({'error': 'Faltan campos requeridos (nombre, cedula, telefono, email).'}), 400

    if '@' not in email or '.' not in email:
        return jsonify({'error': 'El formato del correo electrónico es inválido.'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si la cédula o el email ya existen para evitar duplicados
        cursor.execute("SELECT id_cliente FROM Clientes WHERE cedula = ? OR email = ?", (cedula, email))
        if cursor.fetchone():
            return jsonify({'error': 'La cédula o el correo electrónico ya están registrados para otro cliente.'}), 409 # Conflict

        # Preparar el INSERT a la tabla Clientes. El estado por defecto es 1 (activo).
        sql_insert = "INSERT INTO Clientes (nombre, cedula, telefono, email) VALUES (?, ?, ?, ?)"
        params = (nombre, cedula, telefono, email)
        
        cursor.execute(sql_insert, params)
        
        # Obtener el ID del cliente recién creado
        cursor.execute("SELECT @@IDENTITY AS id;")
        nuevo_cliente_id = cursor.fetchone()[0]
        
        conn.commit()
        
        print(f"API POST /clientes: Cliente creado con ID: {nuevo_cliente_id}")
        return jsonify({
            'message': 'Cliente registrado exitosamente.',
            'id_cliente_creado': nuevo_cliente_id
        }), 201 # 201 Created

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en POST /clientes: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al registrar el cliente: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API POST /clientes: Conexión a BD cerrada.")



# --- ENDPOINTS DE GESTION DE PROVEEDORES---
@app.route('/proveedores', methods=['GET'])
@roles_required('Administrador', 'Supervisor')
def get_todos_los_proveedores(decoded_user_rol, decoded_user_id):
    print(f"API GET /proveedores: Solicitud recibida por usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Consulta para obtener todos los proveedores
        sql_query = """
            SELECT id_proveedor, ruc, nombre_proveedor, razon_social, direccion, 
                   descripcion, telefono, email, estado, fecha_registro 
            FROM Proveedores
            ORDER BY nombre_proveedor ASC
        """
        cursor.execute(sql_query)
        
        columns = [column[0] for column in cursor.description]
        proveedores = []
        for row in cursor.fetchall():
            proveedor_dict = dict(zip(columns, row))
            # Convertir fecha a string ISO para JSON
            if 'fecha_registro' in proveedor_dict and proveedor_dict['fecha_registro'] is not None:
                proveedor_dict['fecha_registro'] = proveedor_dict['fecha_registro'].isoformat()
            proveedores.append(proveedor_dict)
        
        print(f"API GET /proveedores: Devolviendo {len(proveedores)} proveedores.")
        return jsonify(proveedores), 200

    except Exception as e:
        print(f"Error en GET /proveedores: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al obtener proveedores: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API GET /proveedores: Conexión a BD cerrada.")

@app.route('/proveedores', methods=['POST'])
@roles_required('Administrador', 'Supervisor')
def registrar_proveedor(decoded_user_rol, decoded_user_id):
    print(f"API POST /proveedores: Solicitud de {decoded_user_rol} ID {decoded_user_id} para registrar nuevo proveedor.")
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    # Obtener datos del frontend
    ruc = data.get('ruc')
    nombre_proveedor = data.get('nombre_proveedor')
    razon_social = data.get('razon_social')
    direccion = data.get('direccion', '')
    descripcion = data.get('descripcion', '')
    telefono = data.get('telefono', '')
    email = data.get('email', '')

    # Validación de datos requeridos
    if not all([ruc, nombre_proveedor, razon_social]):
        return jsonify({'error': 'Faltan campos requeridos (ruc, nombre_proveedor, razon_social).'}), 400

    # Validar formato de RUC (13 dígitos)
    if not ruc.isdigit() or len(ruc) != 13:
        return jsonify({'error': 'El RUC debe contener exactamente 13 dígitos numéricos.'}), 400

    # Validar email si se proporciona
    if email and ('@' not in email or '.' not in email):
        return jsonify({'error': 'El formato del correo electrónico es inválido.'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si el RUC ya existe
        cursor.execute("SELECT id_proveedor FROM Proveedores WHERE ruc = ?", (ruc,))
        if cursor.fetchone():
            return jsonify({'error': 'El RUC ya está registrado para otro proveedor.'}), 409

        # Verificar si el email ya existe (si se proporciona)
        if email:
            cursor.execute("SELECT id_proveedor FROM Proveedores WHERE email = ?", (email,))
            if cursor.fetchone():
                return jsonify({'error': 'El correo electrónico ya está registrado para otro proveedor.'}), 409

        # Insertar nuevo proveedor
        sql_insert = """
            INSERT INTO Proveedores (ruc, nombre_proveedor, razon_social, direccion, descripcion, telefono, email) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (ruc, nombre_proveedor, razon_social, direccion, descripcion, telefono, email)
        
        cursor.execute(sql_insert, params)
        
        # Obtener el ID del proveedor recién creado
        cursor.execute("SELECT @@IDENTITY AS id;")
        nuevo_proveedor_id = cursor.fetchone()[0]
        
        conn.commit()
        
        print(f"API POST /proveedores: Proveedor creado con ID: {nuevo_proveedor_id}")
        return jsonify({
            'message': 'Proveedor registrado exitosamente.',
            'id_proveedor_creado': nuevo_proveedor_id
        }), 201

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en POST /proveedores: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al registrar el proveedor: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API POST /proveedores: Conexión a BD cerrada.")

@app.route('/proveedores/<int:id_proveedor>', methods=['GET'])
@roles_required('Administrador', 'Supervisor')
def get_proveedor_por_id(decoded_user_rol, decoded_user_id, id_proveedor):
    print(f"API GET /proveedores/{id_proveedor}: Solicitud de {decoded_user_rol} ID {decoded_user_id}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql_query = """
            SELECT id_proveedor, ruc, nombre_proveedor, razon_social, direccion, 
                   descripcion, telefono, email, estado, fecha_registro 
            FROM Proveedores 
            WHERE id_proveedor = ?
        """
        cursor.execute(sql_query, (id_proveedor,))
        
        columns = [column[0] for column in cursor.description]
        proveedor_row = cursor.fetchone()

        if proveedor_row:
            proveedor = dict(zip(columns, proveedor_row))
            # Convertir fecha a string ISO para JSON
            if 'fecha_registro' in proveedor and proveedor['fecha_registro'] is not None:
                proveedor['fecha_registro'] = proveedor['fecha_registro'].isoformat()
            
            print(f"API GET /proveedores/{id_proveedor}: Proveedor encontrado.")
            return jsonify(proveedor), 200
        else:
            print(f"API GET /proveedores/{id_proveedor}: Proveedor no encontrado.")
            return jsonify({'error': 'Proveedor no encontrado'}), 404

    except Exception as e:
        print(f"Error en GET /proveedores/{id_proveedor}: {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print(f"API GET /proveedores/{id_proveedor}: Conexión a BD cerrada.")

@app.route('/proveedores/<int:id_proveedor>', methods=['PUT'])
@roles_required('Administrador', 'Supervisor')
def actualizar_proveedor(decoded_user_rol, decoded_user_id, id_proveedor):
    print(f"API PUT /proveedores/{id_proveedor}: {decoded_user_rol} ID {decoded_user_id} actualizando proveedor")
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON.'}), 400

    # Obtener datos a actualizar
    nuevo_ruc = data.get('ruc')
    nuevo_nombre = data.get('nombre_proveedor')
    nueva_razon_social = data.get('razon_social')
    nueva_direccion = data.get('direccion')
    nueva_descripcion = data.get('descripcion')
    nuevo_telefono = data.get('telefono')
    nuevo_email = data.get('email')
    nuevo_estado = data.get('estado')

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar que el proveedor existe
        cursor.execute("SELECT ruc, email FROM Proveedores WHERE id_proveedor = ?", (id_proveedor,))
        proveedor_actual = cursor.fetchone()
        if not proveedor_actual:
            return jsonify({'error': 'Proveedor no encontrado'}), 404

        update_fields = []
        params = []

        # Validar y agregar RUC si se proporciona
        if nuevo_ruc:
            if not nuevo_ruc.isdigit() or len(nuevo_ruc) != 13:
                return jsonify({'error': 'El RUC debe contener exactamente 13 dígitos numéricos.'}), 400
            if nuevo_ruc != proveedor_actual[0]:
                cursor.execute("SELECT id_proveedor FROM Proveedores WHERE ruc = ? AND id_proveedor != ?", (nuevo_ruc, id_proveedor))
                if cursor.fetchone():
                    return jsonify({'error': f"RUC '{nuevo_ruc}' ya está en uso."}), 409
                update_fields.append("ruc = ?")
                params.append(nuevo_ruc)

        # Validar y agregar email si se proporciona
        if nuevo_email:
            if '@' not in nuevo_email or '.' not in nuevo_email:
                return jsonify({'error': 'Email inválido'}), 400
            if nuevo_email != proveedor_actual[1]:
                cursor.execute("SELECT id_proveedor FROM Proveedores WHERE email = ? AND id_proveedor != ?", (nuevo_email, id_proveedor))
                if cursor.fetchone():
                    return jsonify({'error': f"Email '{nuevo_email}' ya está en uso."}), 409
                update_fields.append("email = ?")
                params.append(nuevo_email)

        # Agregar otros campos
        if nuevo_nombre:
            update_fields.append("nombre_proveedor = ?")
            params.append(nuevo_nombre)
        
        if nueva_razon_social:
            update_fields.append("razon_social = ?")
            params.append(nueva_razon_social)
        
        if nueva_direccion is not None:
            update_fields.append("direccion = ?")
            params.append(nueva_direccion)
        
        if nueva_descripcion is not None:
            update_fields.append("descripcion = ?")
            params.append(nueva_descripcion)
        
        if nuevo_telefono is not None:
            update_fields.append("telefono = ?")
            params.append(nuevo_telefono)
        
        if nuevo_estado and nuevo_estado in ['Activo', 'Inactivo']:
            update_fields.append("estado = ?")
            params.append(nuevo_estado)

        if not update_fields:
            return jsonify({'message': 'No hay cambios para aplicar.'}), 200

        # Construir y ejecutar query
        query = f"UPDATE Proveedores SET {', '.join(update_fields)} WHERE id_proveedor = ?"
        params.append(id_proveedor)
        
        print(f"API PUT /proveedores/{id_proveedor}: Query: {query}")
        cursor.execute(query, tuple(params))
        conn.commit()
        
        print(f"API PUT /proveedores/{id_proveedor}: Proveedor actualizado.")
        return jsonify({'message': f'Proveedor {id_proveedor} actualizado correctamente.'}), 200

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en PUT /proveedores/{id_proveedor}: {str(e)}")
        return jsonify({'error': f'Error de BD: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print(f"API PUT /proveedores/{id_proveedor}: Conexión a BD cerrada.")

@app.route('/proveedores/<int:id_proveedor>', methods=['DELETE'])
@roles_required('Administrador')
def eliminar_proveedor(decoded_user_rol, decoded_user_id, id_proveedor):
    print(f"API DELETE /proveedores/{id_proveedor}: Admin ID {decoded_user_id} eliminando proveedor")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar que el proveedor existe
        cursor.execute("SELECT id_proveedor FROM Proveedores WHERE id_proveedor = ?", (id_proveedor,))
        if not cursor.fetchone():
            return jsonify({'error': 'Proveedor no encontrado'}), 404

        # Eliminar proveedor (hard delete)
        # Nota: Si hay relaciones con otras tablas, considerar soft delete (cambiar estado a 'Inactivo')
        cursor.execute("DELETE FROM Proveedores WHERE id_proveedor = ?", (id_proveedor,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"API DELETE /proveedores/{id_proveedor}: Proveedor eliminado.")
            return jsonify({'message': f'Proveedor {id_proveedor} eliminado exitosamente.'}), 200
        else:
            return jsonify({'error': 'No se pudo eliminar el proveedor.'}), 500

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en DELETE /proveedores/{id_proveedor}: {str(e)}")
        return jsonify({'error': f'Error de BD: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print(f"API DELETE /proveedores/{id_proveedor}: Conexión a BD cerrada.")



# ============================================
# Endpoint: GET /proveedores/<id>/materiales
# Descripción: Obtener todos los materiales de un proveedor específico
# ============================================
@app.route('/proveedores/<int:id_proveedor>/materiales', methods=['GET'])
@roles_required('Administrador', 'Supervisor')
def get_materiales_por_proveedor(decoded_user_rol, decoded_user_id, id_proveedor):
    print(f"API GET /proveedores/{id_proveedor}/materiales: Usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar que el proveedor existe
        cursor.execute("SELECT id_proveedor, nombre_proveedor FROM Proveedores WHERE id_proveedor = ?", (id_proveedor,))
        proveedor = cursor.fetchone()
        if not proveedor:
            return jsonify({'error': 'Proveedor no encontrado'}), 404

        # Obtener materiales del proveedor
        sql_query = """
            SELECT 
                id_material, 
                nombre, 
                descripcion, 
                cantidad, 
                precio_unitario, 
                fecha_ultima_actualizacion
            FROM Materiales
            WHERE id_proveedor = ?
            ORDER BY nombre ASC
        """
        cursor.execute(sql_query, (id_proveedor,))
        
        columns = [column[0] for column in cursor.description]
        materiales = []
        for row in cursor.fetchall():
            material_dict = dict(zip(columns, row))
            # Convertir tipos para JSON
            if 'cantidad' in material_dict and material_dict['cantidad'] is not None:
                material_dict['cantidad'] = int(material_dict['cantidad'])
            if 'precio_unitario' in material_dict and material_dict['precio_unitario'] is not None:
                material_dict['precio_unitario'] = float(material_dict['precio_unitario'])
            if 'fecha_ultima_actualizacion' in material_dict and material_dict['fecha_ultima_actualizacion'] is not None:
                material_dict['fecha_ultima_actualizacion'] = material_dict['fecha_ultima_actualizacion'].isoformat()
            
            materiales.append(material_dict)
        
        print(f"API GET /proveedores/{id_proveedor}/materiales: Devolviendo {len(materiales)} materiales.")
        return jsonify(materiales), 200

    except Exception as e:
        print(f"Error en GET /proveedores/{id_proveedor}/materiales: {str(e)}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print(f"API GET /proveedores/{id_proveedor}/materiales: Conexión a BD cerrada.")

@app.route('/unidades', methods=['GET'])
@roles_required('Administrador', 'Supervisor', 'Encargado de Inventario')
def get_unidades(decoded_user_rol, decoded_user_id):
    """Obtener todas las unidades de medida activas"""
    print(f"API GET /unidades: Solicitud de usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id_unidad, nombre_unidad, abreviatura, descripcion, estado
            FROM Unidades_de_Medida
            WHERE estado = 'Activo'
            ORDER BY nombre_unidad ASC
        """)
        
        columns = [column[0] for column in cursor.description]
        unidades = []
        for row in cursor.fetchall():
            unidad_dict = dict(zip(columns, row))
            unidades.append(unidad_dict)
        
        print(f"API GET /unidades: Devolviendo {len(unidades)} unidades.")
        return jsonify(unidades), 200
    
    except Exception as e:
        print(f"Error en GET /unidades: {str(e)}")
        return jsonify({'error': f'Error al obtener unidades: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API GET /unidades: Conexión a BD cerrada.")


@app.route('/unidades', methods=['POST'])
@roles_required('Administrador')
def crear_unidad(decoded_user_rol, decoded_user_id):
    """Crear una nueva unidad de medida (solo Administrador)"""
    print(f"API POST /unidades: Solicitud de admin ID {decoded_user_id}")
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400
    
    nombre_unidad = data.get('nombre_unidad', '').strip()
    abreviatura = data.get('abreviatura', '').strip()
    descripcion = data.get('descripcion', '').strip()
    
    if not nombre_unidad or not abreviatura:
        return jsonify({'error': 'Nombre y abreviatura son obligatorios'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si ya existe
        cursor.execute("SELECT id_unidad FROM Unidades_de_Medida WHERE nombre_unidad = ?", (nombre_unidad,))
        if cursor.fetchone():
            return jsonify({'error': f'La unidad "{nombre_unidad}" ya existe'}), 409
        
        # Insertar nueva unidad
        cursor.execute("""
            INSERT INTO Unidades_de_Medida (nombre_unidad, abreviatura, descripcion)
            VALUES (?, ?, ?)
        """, (nombre_unidad, abreviatura, descripcion))
        conn.commit()
        
        # Obtener el ID de la unidad creada
        cursor.execute("SELECT @@IDENTITY AS id")
        new_id = cursor.fetchone()[0]
        
        print(f"API POST /unidades: Unidad '{nombre_unidad}' creada con ID {new_id}")
        return jsonify({
            'message': f'Unidad "{nombre_unidad}" creada exitosamente',
            'id_unidad': new_id
        }), 201
    
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error en POST /unidades: {str(e)}")
        return jsonify({'error': f'Error al crear unidad: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API POST /unidades: Conexión a BD cerrada.")


@app.route('/unidades/<int:id_unidad>', methods=['PUT'])
@roles_required('Administrador')
def actualizar_unidad(decoded_user_rol, decoded_user_id, id_unidad):
    """Actualizar una unidad de medida existente (solo Administrador)"""
    print(f"API PUT /unidades/{id_unidad}: Solicitud de admin ID {decoded_user_id}")
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400
    
    nombre_unidad = data.get('nombre_unidad', '').strip()
    abreviatura = data.get('abreviatura', '').strip()
    descripcion = data.get('descripcion', '').strip()
    estado = data.get('estado', 'Activo')
    
    if not nombre_unidad and not abreviatura and not descripcion and not estado:
        return jsonify({'error': 'No se proporcionaron datos para actualizar'}), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que la unidad existe
        cursor.execute("SELECT id_unidad FROM Unidades_de_Medida WHERE id_unidad = ?", (id_unidad,))
        if not cursor.fetchone():
            return jsonify({'error': 'Unidad no encontrada'}), 404
        
        # Construir query de actualización
        update_fields = []
        params = []
        
        if nombre_unidad:
            # Verificar que el nuevo nombre no esté en uso
            cursor.execute("""
                SELECT id_unidad FROM Unidades_de_Medida 
                WHERE nombre_unidad = ? AND id_unidad != ?
            """, (nombre_unidad, id_unidad))
            if cursor.fetchone():
                return jsonify({'error': f'El nombre "{nombre_unidad}" ya está en uso'}), 409
            update_fields.append("nombre_unidad = ?")
            params.append(nombre_unidad)
        
        if abreviatura:
            update_fields.append("abreviatura = ?")
            params.append(abreviatura)
        
        if descripcion:
            update_fields.append("descripcion = ?")
            params.append(descripcion)
        
        if estado:
            if estado not in ['Activo', 'Inactivo']:
                return jsonify({'error': 'Estado debe ser "Activo" o "Inactivo"'}), 400
            update_fields.append("estado = ?")
            params.append(estado)
        
        if not update_fields:
            return jsonify({'message': 'No hay cambios para aplicar'}), 200
        
        query = f"UPDATE Unidades_de_Medida SET {', '.join(update_fields)} WHERE id_unidad = ?"
        params.append(id_unidad)
        
        cursor.execute(query, tuple(params))
        conn.commit()
        
        print(f"API PUT /unidades/{id_unidad}: Unidad actualizada")
        return jsonify({'message': f'Unidad {id_unidad} actualizada exitosamente'}), 200
    
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error en PUT /unidades/{id_unidad}: {str(e)}")
        return jsonify({'error': f'Error al actualizar unidad: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print(f"API PUT /unidades/{id_unidad}: Conexión a BD cerrada.")


@app.route('/unidades/<int:id_unidad>', methods=['DELETE'])
@roles_required('Administrador')
def eliminar_unidad(decoded_user_rol, decoded_user_id, id_unidad):
    """Eliminar una unidad de medida (solo si no está en uso)"""
    print(f"API DELETE /unidades/{id_unidad}: Solicitud de admin ID {decoded_user_id}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que la unidad existe
        cursor.execute("SELECT nombre_unidad FROM Unidades_de_Medida WHERE id_unidad = ?", (id_unidad,))
        unidad = cursor.fetchone()
        if not unidad:
            return jsonify({'error': 'Unidad no encontrada'}), 404
        
        nombre_unidad = unidad[0]
        
        # Verificar si está en uso por algún material
        cursor.execute("SELECT COUNT(*) FROM Materiales WHERE id_unidad = ?", (id_unidad,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            return jsonify({
                'error': f'No se puede eliminar la unidad "{nombre_unidad}" porque está siendo usada por {count} material(es)'
            }), 409
        
        # Eliminar la unidad
        cursor.execute("DELETE FROM Unidades_de_Medida WHERE id_unidad = ?", (id_unidad,))
        conn.commit()
        
        print(f"API DELETE /unidades/{id_unidad}: Unidad '{nombre_unidad}' eliminada")
        return jsonify({'message': f'Unidad "{nombre_unidad}" eliminada exitosamente'}), 200
    
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error en DELETE /unidades/{id_unidad}: {str(e)}")
        return jsonify({'error': f'Error al eliminar unidad: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print(f"API DELETE /unidades/{id_unidad}: Conexión a BD cerrada.")


@app.route('/ordenes-trabajo', methods=['POST'])
@roles_required('Administrador', 'Supervisor')
def crear_orden_trabajo(decoded_user_rol, decoded_user_id):
    print(f"API POST /ordenes-trabajo (lógica híbrida): Solicitud de usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    id_cliente = data.get('id_cliente')
    fecha_inicio_str = data.get('fecha_inicio')
    fecha_fin_str = data.get('fecha_fin')
    descripcion = data.get('descripcion')
    tipo_trabajo = data.get('tipo_trabajo') 
    manual_employee_ids = data.get('manual_employee_ids')

    if not all([id_cliente, fecha_inicio_str, descripcion]):
        return jsonify({'error': 'Faltan campos requeridos (cliente, fecha_inicio, descripcion).'}), 400
    
    if not tipo_trabajo and not manual_employee_ids:
        return jsonify({'error': 'Debe proporcionar un "tipo_trabajo" o una lista de empleados.'}), 400

    try:
        fecha_inicio = datetime.date.fromisoformat(fecha_inicio_str)
        fecha_fin = datetime.date.fromisoformat(fecha_fin_str) if fecha_fin_str else None
        if fecha_fin and fecha_inicio and fecha_fin < fecha_inicio:
            return jsonify({'error': 'La fecha de finalización no puede ser anterior a la de inicio.'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'El formato de fecha es inválido. Use AAAA-MM-DD.'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.autocommit = False 

        ids_empleados_a_asignar = []

        if manual_employee_ids:
            print("Procesando asignación manual...")
            if not isinstance(manual_employee_ids, list) or len(manual_employee_ids) == 0:
                return jsonify({'error': 'La lista de empleados para asignación manual es inválida.'}), 400
            ids_empleados_a_asignar = manual_employee_ids
        else:
            print("Procesando asignación automática...")
            recursos_recomendados = 1
            if fecha_fin and fecha_inicio:
                duracion_dias = (fecha_fin - fecha_inicio).days + 1
                if duracion_dias <= 5: recursos_recomendados = 1
                elif duracion_dias <= 15: recursos_recomendados = 2
                else: recursos_recomendados = 3
            
            mapeo_rol = {'Pintura': '%Pintor%', 'Electrico': '%Electricista%', 'Enderezada': '%Enderezador%', 'Tapiceria': '%Tapicero%', 'Mecanica': '%Mecánico%'}
            rol_buscado = mapeo_rol.get(tipo_trabajo)
            if not rol_buscado:
                return jsonify({'error': f'Tipo de trabajo "{tipo_trabajo}" inválido.'}), 400

            sql_buscar_empleados = """
                SELECT TOP (?) e.id_empleado FROM Empleados e
                LEFT JOIN (SELECT id_empleado, COUNT(*) as ordenes_activas FROM AsignacionesOrdenEmpleado aoe JOIN OrdenesTrabajo ot ON aoe.id_orden = ot.id_orden WHERE ot.estado NOT IN ('Completado', 'Cancelado', 'Finalizado') GROUP BY id_empleado) ot_activas ON e.id_empleado = ot_activas.id_empleado
                WHERE e.estado = 1 AND e.rol LIKE ?
                ORDER BY ISNULL(ot_activas.ordenes_activas, 0) ASC
            """
            cursor.execute(sql_buscar_empleados, recursos_recomendados, rol_buscado)
            empleados_encontrados = cursor.fetchall()

            if len(empleados_encontrados) < recursos_recomendados:
                conn.rollback()
                return jsonify({
                    'error': f'Asignación automática falló. No hay suficientes empleados disponibles para "{tipo_trabajo}".',
                    'manual_assignment_required': True
                }), 409

            ids_empleados_a_asignar = [row[0] for row in empleados_encontrados]

        # --- CORRECCIÓN DE LA SENTENCIA INSERT ---
        # La tabla OrdenesTrabajo (después de eliminar id_empleado) tiene estas columnas para insertar:
        # id_cliente, fecha_inicio, fecha_fin, descripcion, estado, id_usuario_creador, 
        # fecha_ultima_actualizacion, id_usuario_ultima_actualizacion
        sql_insert_orden = """
            INSERT INTO OrdenesTrabajo 
                (id_cliente, fecha_inicio, fecha_fin, descripcion, estado, 
                 id_usuario_creador, fecha_ultima_actualizacion, id_usuario_ultima_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, GETDATE(), ?)
        """
        # 7 placeholders (?) y 1 función (GETDATE())
        
        # CORRECCIÓN: La tupla de parámetros ahora tiene 7 elementos que coinciden con los '?'
        params_orden = (
            id_cliente,                 # 1
            fecha_inicio,               # 2
            fecha_fin,                  # 3
            descripcion,                # 4
            'Asignado',                 # 5 (para la columna 'estado')
            decoded_user_id,            # 6 (para 'id_usuario_creador')
            decoded_user_id             # 7 (para 'id_usuario_ultima_actualizacion')
        )
        
        cursor.execute(sql_insert_orden, params_orden)
        cursor.execute("SELECT @@IDENTITY AS id;")
        nueva_orden_id = cursor.fetchone()[0]

        for id_empleado in ids_empleados_a_asignar:
            cursor.execute("INSERT INTO AsignacionesOrdenEmpleado (id_orden, id_empleado) VALUES (?, ?)", (nueva_orden_id, id_empleado))
        
        conn.commit()
        
        print(f"Orden ID {nueva_orden_id} creada y asignada a empleados: {ids_empleados_a_asignar}")
        return jsonify({
            'message': f'Orden de trabajo creada y asignada a {len(ids_empleados_a_asignar)} empleado(s).',
            'id_orden_creada': nueva_orden_id,
            'ids_empleados_asignados': ids_empleados_a_asignar
        }), 201

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en POST /ordenes-trabajo: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al crear la orden: {str(e)}'}), 500
    finally:
        if conn:
            conn.autocommit = True
            conn.close()

@app.route('/ordenes-trabajo/<int:id_orden>/calcular-recursos', methods=['GET'])
@roles_required('Administrador', 'Supervisor')
def calcular_recursos_orden(decoded_user_rol, decoded_user_id, id_orden):
    print(f"API GET /ordenes-trabajo/{id_orden}/calcular-recursos: Solicitud de usuario ID {decoded_user_id}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener las fechas de la orden de trabajo para calcular la duración
        sql_query = "SELECT fecha_inicio, fecha_fin FROM OrdenesTrabajo WHERE id_orden = ?"
        cursor.execute(sql_query, id_orden)
        orden = cursor.fetchone()

        if not orden:
            return jsonify({'error': f'Orden de trabajo con ID {id_orden} no encontrada.'}), 404

        fecha_inicio = orden[0]
        fecha_fin = orden[1]

        # Validar que ambas fechas existan para poder calcular la duración
        if not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'No se puede calcular, la orden no tiene una fecha de inicio y/o finalización definida.'}), 400

        # Calcular la duración en días (se suma 1 para que sea inclusivo)
        if fecha_fin < fecha_inicio:
             return jsonify({'error': 'La fecha de fin no puede ser anterior a la fecha de inicio.'}), 400
             
        duracion_dias = (fecha_fin - fecha_inicio).days + 1
        
        # Lógica de negocio simple para el cálculo de recursos
        # Esto podría hacerse más complejo o leerse desde APP_CONFIG en el futuro
        if duracion_dias <= 5:
            recursos_recomendados = 1
        elif duracion_dias <= 15:
            recursos_recomendados = 2
        else:
            recursos_recomendados = 3

        mensaje = f"Para una duración de {duracion_dias} día(s), se recomiendan {recursos_recomendados} empleado(s)."
        
        print(f"API GET /ordenes-trabajo/{id_orden}/calcular-recursos: {mensaje}")
        
        return jsonify({
            'id_orden': id_orden,
            'duracion_dias': duracion_dias,
            'recursos_recomendados': recursos_recomendados,
            'mensaje': mensaje
        }), 200

    except Exception as e:
        print(f"Error en GET /ordenes-trabajo/<id>/calcular-recursos: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al calcular recursos: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API GET /ordenes-trabajo/<id>/calcular-recursos: Conexión a BD cerrada.")

@app.route('/ordenes-trabajo', methods=['GET'])
@roles_required('Administrador', 'Supervisor')
def get_todas_las_ordenes(decoded_user_rol, decoded_user_id):
    print(f"API GET /ordenes-trabajo (lógica multi-empleado): Solicitud de usuario ID {decoded_user_id}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Obtener todas las órdenes con el nombre del cliente
        sql_ordenes = """
            SELECT ot.id_orden, ot.descripcion, ot.estado, ot.fecha_inicio, ot.fecha_fin, c.nombre as nombre_cliente
            FROM OrdenesTrabajo ot
            JOIN Clientes c ON ot.id_cliente = c.id_cliente
            ORDER BY ot.fecha_inicio DESC
        """
        cursor.execute(sql_ordenes)
        
        columns = [column[0] for column in cursor.description]
        ordenes = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # 2. Para cada orden, obtener la lista de empleados asignados
        for orden in ordenes:
            sql_empleados = """
                SELECT e.nombre
                FROM Empleados e
                JOIN AsignacionesOrdenEmpleado a ON e.id_empleado = a.id_empleado
                WHERE a.id_orden = ?
            """
            cursor.execute(sql_empleados, orden['id_orden'])
            # Crear una lista de nombres de empleados
            nombres_empleados = [row[0] for row in cursor.fetchall()]
            orden['empleados_asignados'] = nombres_empleados # Añadir la lista al objeto de la orden
            
            # Formatear fechas
            if orden.get('fecha_inicio'): orden['fecha_inicio'] = orden['fecha_inicio'].isoformat()
            if orden.get('fecha_fin'): orden['fecha_fin'] = orden['fecha_fin'].isoformat()

        return jsonify(ordenes), 200

    except Exception as e:
        print(f"Error en GET /ordenes-trabajo: {str(e)}")
        return jsonify({'error': 'Error interno del servidor al obtener las órdenes.'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/ordenes-trabajo/<int:id_orden>', methods=['GET'])
@roles_required('Administrador', 'Supervisor')
def get_detalles_orden(decoded_user_rol, decoded_user_id, id_orden):
    """
    Obtiene los detalles completos de una orden de trabajo específica,
    incluyendo la lista de empleados y materiales ya asignados.
    """
    print(f"API GET /ordenes-trabajo/{id_orden}: Solicitud de detalles por usuario ID {decoded_user_id}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # --- 1. Obtener datos principales de la orden (sin el join a Empleados) ---
        sql_orden = """
            SELECT 
                ot.id_orden, ot.descripcion, ot.estado, ot.fecha_inicio, ot.fecha_fin, 
                c.nombre as nombre_cliente, c.id_cliente
            FROM OrdenesTrabajo ot
            JOIN Clientes c ON ot.id_cliente = c.id_cliente
            WHERE ot.id_orden = ?
        """
        cursor.execute(sql_orden, id_orden)
        orden_data = cursor.fetchone()

        if not orden_data:
            return jsonify({'error': f'Orden de trabajo con ID {id_orden} no encontrada.'}), 404

        columns = [column[0] for column in cursor.description]
        orden_json = dict(zip(columns, orden_data))
        
        # Formatear fechas para que sean compatibles con JSON
        if orden_json.get('fecha_inicio'):
            orden_json['fecha_inicio'] = orden_json['fecha_inicio'].isoformat()
        if orden_json.get('fecha_fin'):
            orden_json['fecha_fin'] = orden_json['fecha_fin'].isoformat()

        # --- 2. Obtener la LISTA de empleados asignados desde la nueva tabla ---
        sql_empleados = """
            SELECT e.id_empleado, e.nombre, e.rol as cargo_empleado
            FROM Empleados e
            JOIN AsignacionesOrdenEmpleado a ON e.id_empleado = a.id_empleado
            WHERE a.id_orden = ?
        """
        cursor.execute(sql_empleados, id_orden)
        columns_empleados = [column[0] for column in cursor.description]
        empleados_asignados = [dict(zip(columns_empleados, row)) for row in cursor.fetchall()]
        
        # Añadir la lista de empleados al objeto de la orden
        orden_json['empleados_asignados'] = empleados_asignados

        # --- 3. Obtener materiales asignados a esa orden (como ya lo teníamos planeado) ---
        sql_materiales = """
            SELECT 
                d.id_detalle, d.id_material, m.nombre as nombre_material, 
                d.cantidad_usada, d.costo_total
            FROM DetalleOrdenMateriales d
            JOIN Materiales m ON d.id_material = m.id_material
            WHERE d.id_orden = ?
            ORDER BY d.id_detalle ASC
        """
        cursor.execute(sql_materiales, id_orden)
        
        columns_materiales = [column[0] for column in cursor.description]
        materiales_asignados = []
        for row in cursor.fetchall():
            material_dict = dict(zip(columns_materiales, row))
            # Convertir Decimal a float para que sea compatible con JSON
            if material_dict.get('costo_total'):
                material_dict['costo_total'] = float(material_dict['costo_total'])
            materiales_asignados.append(material_dict)

        # Añadir la lista de materiales al objeto de la orden
        orden_json['materiales_asignados'] = materiales_asignados
        
        print(f"API GET /ordenes-trabajo/{id_orden}: Devolviendo detalles, {len(empleados_asignados)} empleado(s) y {len(materiales_asignados)} material(es).")
        return jsonify(orden_json), 200

    except Exception as e:
        print(f"Error en GET /ordenes-trabajo/{id_orden}: {str(e)}")
        return jsonify({'error': 'Error interno del servidor al obtener detalles de la orden.'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/ordenes-trabajo/<int:id_orden>/materiales', methods=['POST'])
@roles_required('Administrador', 'Supervisor')
def anadir_material_a_orden(decoded_user_rol, decoded_user_id, id_orden):
    """
    Añade un material a una orden de trabajo existente y descuenta el stock del inventario.
    """
    print(f"API POST /ordenes-trabajo/{id_orden}/materiales: Solicitud de usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    nombre_material = data.get('nombre_material')
    cantidad_str = data.get('cantidad_usada')

    if not nombre_material or not cantidad_str:
        return jsonify({'error': 'Se requiere nombre_material y cantidad_usada.'}), 400

    try:
        cantidad_usada = int(cantidad_str)
        if cantidad_usada <= 0:
            return jsonify({'error': 'La cantidad usada debe ser un número positivo.'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'La cantidad usada debe ser un número entero.'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.autocommit = False # Iniciar transacción para asegurar consistencia

        # 1. Obtener ID, stock y precio del material por su nombre
        cursor.execute("SELECT id_material, cantidad, precio_unitario FROM Materiales WHERE nombre = ?", (nombre_material,))
        material = cursor.fetchone()

        if not material:
            return jsonify({'error': f'Material con nombre "{nombre_material}" no encontrado.'}), 404
        
        id_material, stock_actual, precio_unitario = material
        
        # 2. Verificar si hay stock suficiente
        if stock_actual < cantidad_usada:
            return jsonify({
                'error': 'Existencias insuficientes para añadir el material.',
                'nombre_material': nombre_material,
                'stock_actual': stock_actual,
                'cantidad_solicitada': cantidad_usada
            }), 409 # Conflict

        # 3. Actualizar el stock en la tabla Materiales (descontar)
        nuevo_stock = stock_actual - cantidad_usada
        fecha_actualizacion = datetime.datetime.now()
        sql_update_stock = """
            UPDATE Materiales SET cantidad = ?, fecha_ultima_actualizacion = ?, id_usuario_ultima_actualizacion = ?
            WHERE id_material = ?
        """
       
        params_update = (nuevo_stock, fecha_actualizacion, decoded_user_id, id_material)
        cursor.execute(sql_update_stock, params_update)

        # 4. Insertar el registro en la tabla de detalles de la orden
        costo_total_detalle = cantidad_usada * precio_unitario
        sql_insert_detalle = """
            INSERT INTO DetalleOrdenMateriales (id_orden, id_material, cantidad_usada, costo_total)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(sql_insert_detalle, (id_orden, id_material, cantidad_usada, costo_total_detalle))

        # 5. Confirmar la transacción
        conn.commit()
        
        print(f"API POST /ordenes-trabajo/{id_orden}/materiales: Material ID {id_material} añadido a la orden. Nuevo stock: {nuevo_stock}")
        return jsonify({'message': f'Material "{nombre_material}" añadido a la orden de trabajo exitosamente.'}), 201

    except Exception as e:
        if conn:
            conn.rollback() # Revertir todos los cambios si algo falla
            print(f"Error en POST /ordenes-trabajo/{id_orden}/materiales. Se hizo ROLLBACK. Error: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al añadir material: {str(e)}'}), 500
    finally:
        if conn:
            conn.autocommit = True # Restaurar autocommit
            conn.close() 
            
@app.route('/ordenes-trabajo/<int:id_orden>/modificar-asignacion', methods=['PUT'])
@roles_required('Administrador', 'Supervisor')
def modificar_asignacion_empleado(decoded_user_rol, decoded_user_id, id_orden):
    """
    Modifica una asignación existente, reemplazando un empleado antiguo por uno nuevo en una orden.
    """
    print(f"API PUT /ordenes-trabajo/{id_orden}/modificar-asignacion: Solicitud de admin ID {decoded_user_rol, decoded_user_id}")
    
    data = request.get_json()
    if not data or 'id_empleado_antiguo' not in data or 'id_empleado_nuevo' not in data:
        return jsonify({'error': 'Se requiere id_empleado_antiguo y id_empleado_nuevo.'}), 400

    id_empleado_antiguo = data.get('id_empleado_antiguo')
    id_empleado_nuevo = data.get('id_empleado_nuevo')

    if id_empleado_antiguo == id_empleado_nuevo:
        return jsonify({'error': 'El nuevo empleado no puede ser el mismo que el empleado actual.'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Verificar que el nuevo empleado exista y esté activo
        cursor.execute("SELECT COUNT(*) FROM Empleados WHERE id_empleado = ? AND estado = 1", (id_empleado_nuevo,))
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': f'El nuevo empleado (ID: {id_empleado_nuevo}) no existe o está inactivo.'}), 404

        # 2. Verificar que no estemos asignando un empleado que ya está en esa orden
        cursor.execute("SELECT COUNT(*) FROM AsignacionesOrdenEmpleado WHERE id_orden = ? AND id_empleado = ?", (id_orden, id_empleado_nuevo))
        if cursor.fetchone()[0] > 0:
            return jsonify({'error': 'El nuevo empleado ya está asignado a esta orden de trabajo.'}), 409 # Conflict

        # 3. Actualizar la tabla de asignaciones
        sql_update = """
            UPDATE AsignacionesOrdenEmpleado
            SET id_empleado = ? 
            WHERE id_orden = ? AND id_empleado = ?
        """
        params = (id_empleado_nuevo, id_orden, id_empleado_antiguo)
        cursor.execute(sql_update, params)
        conn.commit()

        if cursor.rowcount == 0:
            # Esto significa que el empleado "antiguo" no estaba asignado a esa orden.
            return jsonify({'error': 'No se encontró la asignación original para modificar.'}), 404
        
        print(f"API PUT /ordenes-trabajo/{id_orden}/modificar-asignacion: Empleado {id_empleado_antiguo} reemplazado por {id_empleado_nuevo}")
        return jsonify({'message': f'Asignación en la orden #{id_orden} actualizada correctamente.'}), 200

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en PUT /ordenes-trabajo/{id_orden}/modificar-asignacion: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al modificar la asignación: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()


# --- ENDPOINTS DE ORDENES DE NOTIFICACIONES---
@app.route('/notificaciones', methods=['GET'])
@roles_required('Administrador', 'Supervisor')
def get_notificaciones(decoded_user_rol, decoded_user_id):
    print(f"API GET /notificaciones: Solicitud recibida por usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    notificaciones = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # --- Lógica 1: Notificaciones de Stock Bajo ---
        umbral_stock_bajo = APP_CONFIG.get('global_low_stock_threshold', 10) # Usar valor de config con fallback
        print(f"API GET /notificaciones: Verificando stock bajo con umbral de {umbral_stock_bajo}.")

        sql_stock_bajo = "SELECT id_material, nombre, cantidad FROM Materiales WHERE cantidad <= ?"
        cursor.execute(sql_stock_bajo, umbral_stock_bajo)
        
        for material in cursor.fetchall():
            id_material, nombre, cantidad = material
            mensaje = f"Alerta de stock: '{nombre}' solo tiene {cantidad} unidades restantes."
            notificacion_stock = {
                "tipo": "stock_bajo",
                "mensaje": mensaje,
                "id_recurso": id_material,
                "recurso_tipo": "material"
            }
            notificaciones.append(notificacion_stock)

        # --- Lógica 2: Notificaciones de Órdenes Próximas a Vencer ---
        dias_aviso_vencimiento = 7 # Definimos que "próxima a vencer" es en 7 días o menos
        fecha_hoy = datetime.date.today()
        fecha_limite = fecha_hoy + datetime.timedelta(days=dias_aviso_vencimiento)
        print(f"API GET /notificaciones: Verificando órdenes que vencen antes de {fecha_limite}.")

        # Unimos OrdenesTrabajo con Clientes para obtener el nombre del cliente para el mensaje
        sql_ordenes_vencer = """
            SELECT ot.id_orden, ot.descripcion, ot.fecha_fin, c.nombre as nombre_cliente
            FROM OrdenesTrabajo ot
            JOIN Clientes c ON ot.id_cliente = c.id_cliente
            WHERE ot.fecha_fin IS NOT NULL 
              AND ot.fecha_fin >= ? 
              AND ot.fecha_fin <= ?
              AND ot.estado NOT IN ('Completado', 'Cancelado', 'Finalizado')
            ORDER BY ot.fecha_fin ASC
        """
        cursor.execute(sql_ordenes_vencer, fecha_hoy, fecha_limite)
        
        for orden in cursor.fetchall():
            id_orden, descripcion, fecha_fin, nombre_cliente = orden
            dias_restantes = (fecha_fin - fecha_hoy).days
            
            if dias_restantes == 0:
                mensaje_vencimiento = f"¡Hoy vence! Orden #{id_orden} para '{nombre_cliente}'."
            elif dias_restantes == 1:
                mensaje_vencimiento = f"Vence mañana: Orden #{id_orden} para '{nombre_cliente}'."
            else:
                mensaje_vencimiento = f"Vence en {dias_restantes} días: Orden #{id_orden} para '{nombre_cliente}'."
            
            notificacion_orden = {
                "tipo": "orden_vencimiento",
                "mensaje": mensaje_vencimiento,
                "id_recurso": id_orden,
                "recurso_tipo": "orden_trabajo"
            }
            notificaciones.append(notificacion_orden)

        print(f"API GET /notificaciones: Se encontraron {len(notificaciones)} notificaciones en total.")
        return jsonify(notificaciones), 200

    except Exception as e:
        print(f"Error en GET /notificaciones: {str(e)}")
        # No devolver el error detallado al cliente por seguridad
        return jsonify({'error': 'Error interno del servidor al generar notificaciones.'}), 500
    finally:
        if conn:
            conn.close()
            print("API GET /notificaciones: Conexión a BD cerrada.")


# --- ENDPOINTS DE ORDENES DE DASHBOARD---
@app.route('/dashboard/overview', methods=['GET'])
@roles_required('Administrador', 'Supervisor')
def get_dashboard_overview(decoded_user_rol, decoded_user_id):
    print(f"API GET /dashboard/overview: Solicitud recibida por usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    overview_data = {}
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # --- 1. Obtener Materiales con Stock Bajo ---
        umbral_stock_bajo = APP_CONFIG.get('global_low_stock_threshold', 10) # Usar valor de config con fallback
        
        sql_stock_bajo = """
            SELECT TOP 5 id_material, nombre, cantidad 
            FROM Materiales 
            WHERE cantidad <= ? 
            ORDER BY cantidad ASC
        """
        cursor.execute(sql_stock_bajo, umbral_stock_bajo)
        
        columns_stock = [column[0] for column in cursor.description]
        materiales_stock_bajo = [dict(zip(columns_stock, row)) for row in cursor.fetchall()]
        overview_data['materiales_stock_bajo'] = materiales_stock_bajo

        # --- 2. Obtener Órdenes de Trabajo Recientes o Activas ---
        # Por ejemplo, las últimas 5 órdenes que no estén "Completado" o "Cancelado"
        sql_ordenes = """
            SELECT TOP 5 ot.id_orden, ot.descripcion, ot.estado, ot.fecha_inicio, c.nombre as nombre_cliente
            FROM OrdenesTrabajo ot
            JOIN Clientes c ON ot.id_cliente = c.id_cliente
            WHERE ot.estado NOT IN ('Completado', 'Cancelado', 'Finalizado')
            ORDER BY ot.fecha_inicio DESC
        """
        cursor.execute(sql_ordenes)

        columns_ordenes = [column[0] for column in cursor.description]
        ordenes_recientes = []
        for row in cursor.fetchall():
            orden_dict = dict(zip(columns_ordenes, row))
            if orden_dict.get('fecha_inicio'):
                orden_dict['fecha_inicio'] = orden_dict['fecha_inicio'].isoformat()
            ordenes_recientes.append(orden_dict)
        
        overview_data['ordenes_recientes'] = ordenes_recientes

        print(f"API GET /dashboard/overview: Devolviendo {len(materiales_stock_bajo)} alertas de stock y {len(ordenes_recientes)} órdenes recientes.")
        return jsonify(overview_data), 200

    except Exception as e:
        print(f"Error en GET /dashboard/overview: {str(e)}")
        return jsonify({'error': 'Error interno del servidor al obtener datos para el dashboard.'}), 500
    finally:
        if conn:
            conn.close()
            print("API GET /dashboard/overview: Conexión a BD cerrada.")


# --- INICIO DE NUEVO ENDPOINT PARA REPORTES ---
@app.route('/reportes/uso-materiales', methods=['GET'])
@roles_required('Administrador')
def reporte_uso_materiales(decoded_user_rol, decoded_user_id):
    print(f"API GET /reportes/uso-materiales: Solicitud de admin ID {decoded_user_rol, decoded_user_id}")

    # --- Obtener parámetros de la URL ---
    fecha_desde_str = request.args.get('fecha_desde')
    fecha_hasta_str = request.args.get('fecha_hasta')
    # NUEVO: Obtener filtros opcionales
    id_material_filtro = request.args.get('id_material', type=int)
    id_empleado_filtro = request.args.get('id_empleado', type=int)

    # --- Validación de fechas (obligatorias) ---
    if not fecha_desde_str or not fecha_hasta_str:
        return jsonify({'error': 'Los parámetros "fecha_desde" y "fecha_hasta" son requeridos.'}), 400
    try:
        fecha_desde = datetime.date.fromisoformat(fecha_desde_str)
        fecha_hasta = datetime.date.fromisoformat(fecha_hasta_str)
        if fecha_desde > fecha_hasta:
             return jsonify({'error': 'La fecha "desde" no puede ser posterior a la fecha "hasta".'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'El formato de fecha es inválido. Use AAAA-MM-DD.'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # --- Construcción Dinámica de la Consulta SQL ---
        params = [fecha_desde, fecha_hasta]
        
        # Base de la consulta
        sql_base = """
            SELECT 
                d.id_detalle, ot.id_orden, ot.fecha_inicio, c.nombre AS nombre_cliente,
                m.nombre AS nombre_material, d.cantidad_usada, m.precio_unitario, d.costo_total
            FROM 
                DetalleOrdenMateriales d
            JOIN Materiales m ON d.id_material = m.id_material
            JOIN OrdenesTrabajo ot ON d.id_orden = ot.id_orden
            JOIN Clientes c ON ot.id_cliente = c.id_cliente
        """

        # Lista de condiciones WHERE
        where_conditions = ["ot.fecha_inicio BETWEEN ? AND ?"]

        # Añadir filtro por material si se proporcionó
        if id_material_filtro:
            where_conditions.append("d.id_material = ?")
            params.append(id_material_filtro)
            print(f"Reporte filtrado por id_material: {id_material_filtro}")
        
        # Añadir filtro por empleado si se proporcionó
        if id_empleado_filtro:
            # Usamos una subconsulta para filtrar las órdenes donde el empleado está asignado
            where_conditions.append("ot.id_orden IN (SELECT id_orden FROM AsignacionesOrdenEmpleado WHERE id_empleado = ?)")
            params.append(id_empleado_filtro)
            print(f"Reporte filtrado por id_empleado: {id_empleado_filtro}")

        # Unir todas las condiciones
        sql_reporte = f"{sql_base} WHERE {' AND '.join(where_conditions)} ORDER BY ot.fecha_inicio, ot.id_orden;"
        
        print("SQL Query a ejecutar:", sql_reporte)
        print("Parámetros:", tuple(params))
        
        cursor.execute(sql_reporte, tuple(params))
        
        columns = [column[0] for column in cursor.description]
        reporte_data = []
        for row in cursor.fetchall():
            reporte_dict = dict(zip(columns, row))
            # Formatear datos para JSON
            if reporte_dict.get('fecha_inicio'):
                reporte_dict['fecha_inicio'] = reporte_dict['fecha_inicio'].isoformat()
            if reporte_dict.get('precio_unitario'):
                reporte_dict['precio_unitario'] = float(reporte_dict['precio_unitario'])
            if reporte_dict.get('costo_total'):
                reporte_dict['costo_total'] = float(reporte_dict['costo_total'])
            reporte_data.append(reporte_dict)

        print(f"API GET /reportes/uso-materiales: Devolviendo {len(reporte_data)} registros para el reporte.")
        return jsonify(reporte_data), 200

    except Exception as e:
        print(f"Error en GET /reportes/uso-materiales: {str(e)}")
        return jsonify({'error': 'Error interno del servidor al generar el reporte.'}), 500
    finally:
        if conn:
            conn.close()


# --- ENDPOINT PARA REGISTRO DE COMPROBANTES DE PAGO
@app.route('/comprobantes-pago', methods=['POST'])
@roles_required('Administrador', 'Supervisor')
def registrar_comprobante_pago(decoded_user_rol, decoded_user_id):
    print(f"API POST /comprobantes-pago: Solicitud de admin ID {decoded_user_rol, decoded_user_id}")
    
    data = request.get_json()
    if not data or 'id_orden' not in data:
        return jsonify({'error': 'Se requiere el "id_orden" para generar el comprobante.'}), 400

    id_orden = data.get('id_orden')
    
    # El método de pago podría venir del frontend o tener un valor por defecto
    metodo_pago = data.get('metodo_pago', 'No especificado')

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Verificar que la orden de trabajo exista
        cursor.execute("SELECT COUNT(*) FROM OrdenesTrabajo WHERE id_orden = ?", (id_orden,))
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': f'La orden de trabajo con ID {id_orden} no existe.'}), 404

        # 2. Verificar si ya existe un comprobante para esta orden para evitar duplicados
        cursor.execute("SELECT id_comprobante FROM ComprobantesPago WHERE id_orden = ?", (id_orden,))
        if cursor.fetchone():
            return jsonify({'error': f'Ya existe un comprobante de pago para la orden #{id_orden}.'}), 409 # Conflict

        # 3. Calcular el monto total sumando los costos de los materiales asignados
        sql_sum = "SELECT SUM(costo_total) FROM DetalleOrdenMateriales WHERE id_orden = ?"
        cursor.execute(sql_sum, id_orden)
        monto_total = cursor.fetchone()[0]

        # Si no hay materiales, el monto podría ser None o 0.
        if monto_total is None:
            monto_total = 0.0

        print(f"Monto total calculado para la orden #{id_orden}: {monto_total}")

        # 4. Preparar el INSERT a la tabla ComprobantesPago
        sql_insert = """
            INSERT INTO ComprobantesPago 
                (id_orden, monto, fecha_emision, metodo_pago, estado_pago, id_usuario_registrador, 
                 fecha_ultima_actualizacion, id_usuario_ultima_actualizacion)
            VALUES (?, ?, GETDATE(), ?, ?, ?, GETDATE(), ?)
        """
        params = (
            id_orden, 
            monto_total, 
            metodo_pago, 
            'Pagado', # Estado por defecto
            decoded_user_id,
            decoded_user_id
        )
        
        cursor.execute(sql_insert, params)
        
        cursor.execute("SELECT @@IDENTITY AS id;")
        nuevo_comprobante_id = cursor.fetchone()[0]
        
        conn.commit()
        
        print(f"API POST /comprobantes-pago: Comprobante creado con ID: {nuevo_comprobante_id}")
        return jsonify({
            'message': 'Comprobante de pago generado exitosamente.',
            'id_comprobante_creado': nuevo_comprobante_id,
            'monto_calculado': float(monto_total)
        }), 201

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en POST /comprobantes-pago: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al registrar el comprobante: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/comprobantes-pago', methods=['GET'])
@roles_required('Administrador', 'Supervisor')
def consultar_comprobantes_pago(decoded_user_rol, decoded_user_id):
    print(f"API GET /comprobantes-pago: Solicitud de usuario ID {decoded_user_id} con rol {decoded_user_rol}")

    # Obtener parámetros de fecha opcionales de la URL
    fecha_desde_str = request.args.get('fecha_desde')
    fecha_hasta_str = request.args.get('fecha_hasta')

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Consulta base que une las tablas para obtener información completa
        sql_base = """
            SELECT 
                cp.id_comprobante,
                cp.id_orden,
                cp.monto,
                cp.fecha_emision,
                cp.metodo_pago,
                cp.estado_pago,
                c.nombre AS nombre_cliente,
                u.username AS nombre_usuario_registrador
            FROM 
                ComprobantesPago cp
            JOIN 
                OrdenesTrabajo ot ON cp.id_orden = ot.id_orden
            JOIN 
                Clientes c ON ot.id_cliente = c.id_cliente
            JOIN 
                Usuarios u ON cp.id_usuario_registrador = u.id_usuario
        """
        
        where_conditions = []
        params = []

        # Añadir filtros de fecha si se proporcionan
        if fecha_desde_str:
            where_conditions.append("cp.fecha_emision >= ?")
            params.append(datetime.date.fromisoformat(fecha_desde_str))
        
        if fecha_hasta_str:
            where_conditions.append("cp.fecha_emision <= ?")
            params.append(datetime.date.fromisoformat(fecha_hasta_str))

        # Construir la consulta final
        if where_conditions:
            sql_query = f"{sql_base} WHERE {' AND '.join(where_conditions)} ORDER BY cp.fecha_emision DESC"
        else:
            sql_query = f"{sql_base} ORDER BY cp.fecha_emision DESC"

        print("SQL Query a ejecutar:", sql_query)
        print("Parámetros:", tuple(params))
        
        cursor.execute(sql_query, tuple(params))
        
        columns = [column[0] for column in cursor.description]
        comprobantes = []
        for row in cursor.fetchall():
            comprobante_dict = dict(zip(columns, row))
            # Formatear datos para que sean amigables en JSON
            if comprobante_dict.get('fecha_emision'):
                comprobante_dict['fecha_emision'] = comprobante_dict['fecha_emision'].isoformat()
            if comprobante_dict.get('monto'):
                comprobante_dict['monto'] = float(comprobante_dict['monto'])
            comprobantes.append(comprobante_dict)

        print(f"API GET /comprobantes-pago: Devolviendo {len(comprobantes)} comprobantes.")
        return jsonify(comprobantes), 200

    except (ValueError, TypeError):
        return jsonify({'error': 'El formato de fecha es inválido. Use AAAA-MM-DD.'}), 400
    except Exception as e:
        print(f"Error en GET /comprobantes-pago: {str(e)}")
        return jsonify({'error': 'Error interno del servidor al consultar los comprobantes.'}), 500
    finally:
        if conn:
            conn.close()
            print("API GET /comprobantes-pago: Conexión a BD cerrada.")
         
    
    
# --- FINALIZAR ORDEN DE TRABAJO
@app.route('/ordenes-trabajo/<int:id_orden>/confirmar-uso-y-finalizar', methods=['PUT'])
@roles_required('Administrador', 'Supervisor')
def confirmar_y_finalizar_orden(decoded_user_rol, decoded_user_id, id_orden):
    """
    Confirma las cantidades finales de materiales usados, devuelve el sobrante al stock,
    actualiza los costos y marca la orden como 'Finalizado'.
    """
    print(f"API PUT /ordenes-trabajo/{id_orden}/confirmar-uso-y-finalizar: Solicitud de admin ID {decoded_user_rol, decoded_user_id}")
    
    # El frontend enviará una lista de los materiales con sus cantidades finales
    # Formato esperado: [{"id_detalle": <int>, "cantidad_usada_final": <int>}, ...]
    materiales_confirmados = request.get_json()
    if not isinstance(materiales_confirmados, list):
        return jsonify({'error': 'Se esperaba una lista de materiales confirmados.'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.autocommit = False # Iniciar transacción

        for material in materiales_confirmados:
            id_detalle = material.get('id_detalle')
            cantidad_usada_final = material.get('cantidad_usada_final')

            if id_detalle is None or cantidad_usada_final is None or int(cantidad_usada_final) < 0:
                raise ValueError("Datos de material inválidos. Cada material debe tener id_detalle y cantidad_usada_final no negativa.")

            # 1. Obtener la cantidad asignada originalmente y el id_material del detalle
            cursor.execute("SELECT id_material, cantidad_usada, costo_total FROM DetalleOrdenMateriales WHERE id_detalle = ?", (id_detalle,))
            detalle_actual = cursor.fetchone()
            if not detalle_actual:
                raise ValueError(f"No se encontró el detalle de material con ID {id_detalle}.")

            id_material_actual = detalle_actual.id_material
            cantidad_asignada = detalle_actual.cantidad_usada
            
            if int(cantidad_usada_final) > cantidad_asignada:
                raise ValueError(f"La cantidad usada final ({cantidad_usada_final}) no puede ser mayor a la cantidad asignada ({cantidad_asignada}) para el detalle #{id_detalle}.")
            
            # 2. Calcular y devolver el stock sobrante
            cantidad_sobrante = cantidad_asignada - int(cantidad_usada_final)
            if cantidad_sobrante > 0:
                print(f"Devolviendo {cantidad_sobrante} unidades del material ID {id_material_actual} al inventario.")
                cursor.execute("UPDATE Materiales SET cantidad = cantidad + ? WHERE id_material = ?", (cantidad_sobrante, id_material_actual))

            # 3. Actualizar el detalle de la orden con la cantidad y costo reales
            cursor.execute("SELECT precio_unitario FROM Materiales WHERE id_material = ?", (id_material_actual,))
            precio_unitario = cursor.fetchone()[0]
            nuevo_costo_total = int(cantidad_usada_final) * precio_unitario
            
            cursor.execute("UPDATE DetalleOrdenMateriales SET cantidad_usada = ?, costo_total = ? WHERE id_detalle = ?",
                           (int(cantidad_usada_final), nuevo_costo_total, id_detalle))

        # 4. Finalmente, actualizar el estado de la orden de trabajo a 'Finalizado'
        fecha_fin_actualizada = datetime.date.today()
        sql_update_orden = "UPDATE OrdenesTrabajo SET estado = 'Finalizado', fecha_fin = ?, fecha_ultima_actualizacion = GETDATE(), id_usuario_ultima_actualizacion = ? WHERE id_orden = ?"
        cursor.execute(sql_update_orden, (fecha_fin_actualizada, decoded_user_id, id_orden))
        
        conn.commit() # Confirmar todos los cambios de la transacción
        
        print(f"API: Orden de trabajo #{id_orden} finalizada y materiales actualizados.")
        return jsonify({'message': f'Orden de trabajo #{id_orden} finalizada y stock de materiales actualizado correctamente.'}), 200

    except ValueError as ve:
        if conn: conn.rollback()
        print(f"Error de validación en la transacción: {str(ve)}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en PUT /ordenes-trabajo/{id_orden}/confirmar-uso-y-finalizar: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al finalizar la orden: {str(e)}'}), 500
    finally:
        if conn:
            conn.autocommit = True
            conn.close()
        
            
# Ruta de prueba básica
@app.route('/')
def hello():
    return "¡API de Carrocería Alvarado funcionando!"

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Ejecutar en puerto 5000
