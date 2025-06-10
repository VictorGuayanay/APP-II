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


# --- Variables Globales para Configuración (Simulación - Idealmente irían en BD o archivo de config) ---
# Valores por defecto basados en tu código actual o en valores comunes.
APP_CONFIG = {
    "reset_token_expiry_minutes": 15, # Duración actual en send_reset_email
    "max_failed_login_attempts": 5,    # Un valor común
    "global_low_stock_threshold": 10 # Valor para limite de stock bajo
}


CORS(app) # Permite CORS para todas las rutas

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-OJ81G31\SQLEXPRESS;" # Asegúrate que este nombre de servidor sea correcto para ti
    "DATABASE=CarroceriaAlvaradoDB;"
    "Trusted_Connection=yes;"
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "victorguayanay@gmail.com" # Reemplaza con tu correo
SMTP_PASSWORD = "qzgl wxpz stvw uxdp" # Reemplaza con tu contraseña de aplicación (considera variables de entorno)

def get_db_connection():
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"!!!!!!!! ERROR CRÍTICO AL CONECTAR A LA BASE DE DATOS: {str(e)} !!!!!!!!")
        # En un entorno real, podrías querer reintentar o manejar esto de forma más robusta.
        raise Exception(f"Error al conectar a la base de datos: {str(e)}")

def send_reset_email(email, user_id):
    try:
        # Usar el valor de APP_CONFIG para la expiración
        expiry_minutes = APP_CONFIG.get('reset_token_expiry_minutes', 15) # Fallback a 15 si no está en config
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

        # ... (resto del código para configurar y enviar el email) ...
        # (El código para msg, body y smtplib.SMTP permanece igual)

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
    # (Tu código de /registro como lo tenías, asegurándote que no modifique app.config['SECRET_KEY'])
    # ... (código de la función /registro) ...
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
            
            # Guardar el token de reseteo y su expiración en la BD (si no lo estás haciendo ya)
            # Esto es opcional pero más seguro para invalidar tokens usados o viejos.
            # exp_time_db = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
            # temp_reset_token = jwt.encode({'user_id': user_id, 'exp': exp_time_db}, app.config['SECRET_KEY'], algorithm="HS256")
            # cursor.execute("UPDATE Usuarios SET reset_token = ?, reset_token_expiry = ? WHERE id_usuario = ?", 
            #                (temp_reset_token, exp_time_db, user_id))
            # conn.commit()
            # if not send_reset_email(email_req, user_id, temp_reset_token): # Modificar send_reset_email para usar este token
            
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

# --- ENDPOINTS DE GESTIÓN DE USUARIOS ---
@app.route('/usuarios', methods=['GET'])
@admin_required
def get_all_usuarios(admin_user_id_from_token):
    print(f"API /usuarios GET: Solicitud recibida por admin con ID: {admin_user_id_from_token}")
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
@admin_required # Solo administradores pueden desbloquear
def desbloquear_usuario(admin_user_id_from_token, user_id):
    print(f"API /usuarios/{user_id}/desbloquear PUT: Solicitud de admin ID {admin_user_id_from_token} para desbloquear usuario ID {user_id}")
    
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
@admin_required
def cambiar_estado_usuario(admin_user_id_from_token, user_id):
    # (Tu código de /usuarios/<id>/estado PUT como lo tenías)
    # ... (código de la función /usuarios/<id>/estado PUT) ...
    print(f"API /usuarios/{user_id}/estado PUT: Admin ID {admin_user_id_from_token} cambiando estado de usuario ID {user_id}")
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
@admin_required
def actualizar_usuario(admin_user_id_from_token, user_id):
    # (Tu código de /usuarios/<id> PUT como lo tenías)
    # ... (código de la función /usuarios/<id> PUT para actualizar datos) ...
    print(f"API /usuarios/{user_id} PUT (actualizar datos): Admin ID {admin_user_id_from_token} actualizando usuario ID {user_id}")
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
@admin_required
def get_usuario_por_id(admin_user_id_from_token, user_id):
    # (Tu código de /usuarios/<id> GET como lo tenías)
    # ... (código de la función /usuarios/<id> GET) ...
    print(f"API /usuarios/{user_id} GET: Admin ID {admin_user_id_from_token} solicitando usuario ID {user_id}")
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

#configuraciones
@app.route('/configuraciones', methods=['GET'])
@admin_required 
def get_configuraciones(admin_user_id_from_token): # El nombre del argumento debe coincidir con lo que pasa el decorador
    print(f"API GET /configuraciones: Solicitud de Admin ID {admin_user_id_from_token}. Config actual: {APP_CONFIG}")
    # Devolver una copia para evitar modificar el original directamente si se pasa por referencia en algunos contextos Python
    return jsonify(APP_CONFIG.copy()), 200

@app.route('/configuraciones', methods=['PUT'])
@admin_required 
def update_configuraciones(admin_user_id_from_token): # El nombre del argumento debe coincidir
    global APP_CONFIG # Necesario para modificar la variable global
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    print(f"API PUT /configuraciones: Admin ID {admin_user_id_from_token} actualizando. Datos recibidos: {data}")

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


@app.route('/materiales', methods=['GET'])
@token_required # O @admin_required si solo los admins pueden ver la lista completa
def get_todos_los_materiales(decoded_user_rol, decoded_user_id): # Argumentos del decorador @token_required
    # Si usas @admin_required, el argumento sería admin_user_id_from_token
    print(f"API GET /materiales: Solicitud recibida por usuario ID {decoded_user_id} con rol {decoded_user_rol}")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Consulta para obtener todos los campos relevantes de la tabla Materiales
        # Basado en tu CarroceriaAlvaradoDB.sql: id_material, nombre, descripcion, cantidad, precio_unitario, fecha_ultima_actualizacion
        sql_query = """
            SELECT id_material, nombre, descripcion, cantidad, precio_unitario, fecha_ultima_actualizacion 
            FROM Materiales
            ORDER BY nombre ASC 
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
@admin_required # O el decorador de rol que hayas decidido para esta acción
def crear_nuevo_material(admin_user_id_from_token): # El argumento depende del decorador
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    nombre = data.get('nombre')
    descripcion = data.get('descripcion') # Puede ser None o vacío si es opcional
    precio_unitario_str = data.get('precio_unitario')
    
    cantidad_inicial = 0 # Los nuevos materiales se crean con stock 0
    fecha_actual = datetime.datetime.now()

    # Validaciones básicas
    if not nombre:
        return jsonify({'error': 'El nombre del material es requerido'}), 400
    if precio_unitario_str is None: # El precio puede ser 0, pero el campo debe estar presente
        return jsonify({'error': 'El precio unitario es requerido'}), 400

    try:
        precio_unitario = float(precio_unitario_str)
        if precio_unitario < 0:
            return jsonify({'error': 'El precio unitario no puede ser negativo'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'El precio unitario debe ser un número válido'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Opcional: Verificar si ya existe un material con el mismo nombre
        cursor.execute("SELECT id_material FROM Materiales WHERE nombre = ?", (nombre,))
        if cursor.fetchone():
            conn.close() # Cerrar conexión antes de retornar
            return jsonify({'error': f'Ya existe un material con el nombre "{nombre}"'}), 409 # 409 Conflict
        
        sql_insert = """
            INSERT INTO Materiales (nombre, descripcion, cantidad, precio_unitario, 
                                    fecha_ultima_actualizacion, id_usuario_ultima_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        # admin_user_id_from_token viene del decorador @admin_required
        cursor.execute(sql_insert, 
                       (nombre, descripcion, cantidad_inicial, precio_unitario, 
                        fecha_actual, admin_user_id_from_token))
        conn.commit()
        
        # Opcional: Obtener el ID del material recién insertado para devolverlo
        # new_material_id = cursor.execute("SELECT @@IDENTITY AS id").fetchone()[0] 
        # (Esto es específico de SQL Server y pyodbc; podría variar)

        print(f"API POST /materiales: Material '{nombre}' creado por admin ID {admin_user_id_from_token}.")
        return jsonify({'message': f'Material "{nombre}" creado exitosamente.'}), 201 # 201 Created

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
@admin_required # O el rol apropiado para gestión de inventario
def registrar_entrada_inventario(admin_user_id_from_token):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    print(f"API /inventory/entry POST: Admin ID {admin_user_id_from_token} registrando entrada. Datos: {data}")

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
        cursor.execute(sql_update, (nuevo_stock, fecha_actualizacion, admin_user_id_from_token, id_material))
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
@admin_required # O el rol apropiado
def registrar_salida_inventario(admin_user_id_from_token):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    print(f"API /inventory/exit POST: Admin ID {admin_user_id_from_token} registrando salida. Datos: {data}")

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
        cursor.execute(sql_update, (nuevo_stock, fecha_actualizacion, admin_user_id_from_token, id_material))
        
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
@admin_required # O el rol apropiado para gestión de inventario
def eliminar_material(admin_user_id_from_token, id_material):
    print(f"API DELETE /materiales/{id_material}: Solicitud de admin ID {admin_user_id_from_token}")
    
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



@app.route('/empleados', methods=['GET'])
@token_required # Asumimos que cualquier usuario autenticado puede necesitar ver la lista de empleados
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


@app.route('/clientes', methods=['GET'])
@token_required # Asumimos que cualquier usuario autenticado puede necesitar ver la lista de clientes
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



@app.route('/ordenes-trabajo', methods=['POST'])
@admin_required # Solo usuarios autorizados pueden crear órdenes de trabajo
def crear_orden_trabajo(admin_user_id_from_token):
    print(f"API POST /ordenes-trabajo: Solicitud de admin ID {admin_user_id_from_token} para crear nueva orden.")
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    # --- Obtención de datos del frontend ---
    id_empleado = data.get('id_empleado')
    id_cliente = data.get('id_cliente')
    fecha_inicio_str = data.get('fecha_inicio')
    descripcion = data.get('descripcion')
    # Se obtiene la fecha de finalización (puede ser opcional)
    fecha_fin_str = data.get('fecha_fin') 

    # --- Validación de datos de entrada ---
    if not all([id_empleado, id_cliente, fecha_inicio_str, descripcion]):
        return jsonify({'error': 'Faltan campos requeridos (id_empleado, id_cliente, fecha_inicio, descripcion).'}), 400

    # --- Validación y conversión de fechas ---
    try:
        fecha_inicio = datetime.date.fromisoformat(fecha_inicio_str)
        # Opcional: No permitir crear órdenes con fecha pasada
        if fecha_inicio < datetime.date.today():
            return jsonify({'error': 'La fecha de inicio no puede ser en el pasado.'}), 400
        
        # Validar fecha_fin solo si se proporciona
        fecha_fin = None # Valor por defecto es NULL
        if fecha_fin_str: # Si el frontend envía una fecha_fin
            fecha_fin = datetime.date.fromisoformat(fecha_fin_str)
            # Validar que la fecha de fin no sea anterior a la de inicio
            if fecha_fin < fecha_inicio:
                return jsonify({'error': 'La fecha de finalización no puede ser anterior a la fecha de inicio.'}), 400

    except (ValueError, TypeError):
        return jsonify({'error': 'El formato de fecha es inválido. Use AAAA-MM-DD.'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Opcional pero recomendado: Verificar que el id_empleado y id_cliente existan
        cursor.execute("SELECT COUNT(*) FROM Empleados WHERE id_empleado = ?", (id_empleado,))
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': f'El empleado con ID {id_empleado} no existe.'}), 404
        
        cursor.execute("SELECT COUNT(*) FROM Clientes WHERE id_cliente = ?", (id_cliente,))
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': f'El cliente con ID {id_cliente} no existe.'}), 404
        
        # --- Preparar el INSERT a la tabla OrdenesTrabajo ---
        # Se añade la columna fecha_fin a la sentencia INSERT
        sql_insert = """
            INSERT INTO OrdenesTrabajo (id_empleado, id_cliente, fecha_inicio, fecha_fin, descripcion, id_usuario_creador, estado, fecha_ultima_actualizacion, id_usuario_ultima_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)
        """
        params = (
            id_empleado, 
            id_cliente, 
            fecha_inicio, 
            fecha_fin, # Se añade el valor de fecha_fin
            descripcion, 
            admin_user_id_from_token, # id_usuario_creador
            'Pendiente', # estado inicial
            admin_user_id_from_token # id_usuario_ultima_actualizacion
        )
        
        cursor.execute(sql_insert, params)
        
        # Obtener el ID de la orden recién creada para devolverlo
        cursor.execute("SELECT @@IDENTITY AS id;")
        nueva_orden_id = cursor.fetchone()[0]
        
        conn.commit()
        
        print(f"API POST /ordenes-trabajo: Orden de trabajo creada con ID: {nueva_orden_id}")
        return jsonify({
            'message': 'Orden de trabajo creada exitosamente.',
            'id_orden_creada': nueva_orden_id
        }), 201 # 201 Created

    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en POST /ordenes-trabajo: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al crear la orden de trabajo: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            print("API POST /ordenes-trabajo: Conexión a BD cerrada.")


@app.route('/notificaciones', methods=['GET'])
@token_required # Cualquier usuario autenticado puede ver las notificaciones
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


@app.route('/dashboard/overview', methods=['GET'])
@token_required # Cualquier usuario autenticado puede ver el dashboard
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


@app.route('/clientes', methods=['POST'])
@admin_required # Solo usuarios autorizados (admins) pueden registrar nuevos clientes
def registrar_cliente(admin_user_id_from_token):
    print(f"API POST /clientes: Solicitud de admin ID {admin_user_id_from_token} para registrar nuevo cliente.")
    
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


@app.route('/empleados', methods=['POST'])
@admin_required # Solo usuarios autorizados (admins) pueden registrar nuevos empleados
def registrar_empleado(admin_user_id_from_token):
    print(f"API POST /empleados: Solicitud de admin ID {admin_user_id_from_token} para registrar nuevo empleado.")
    
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



# Ruta de prueba básica
@app.route('/')
def hello():
    return "¡API de Carrocería Alvarado funcionando!"

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Ejecutar en puerto 5000
