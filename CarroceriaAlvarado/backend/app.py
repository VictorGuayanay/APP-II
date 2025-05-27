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
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15) # Token válido por 15 minutos
        
        # Loguear la SECRET_KEY usada para ENCODE el token de reseteo
        secret_key_for_encode = app.config.get('SECRET_KEY')
        print(f"DEBUG send_reset_email: SECRET_KEY para ENCODE (reseteo): '{secret_key_for_encode}'")

        token_payload = {
            'user_id': user_id,
            'exp': exp_time # PyJWT maneja la conversión a timestamp si es un objeto datetime
        }
        # Usar app.config['SECRET_KEY'] consistentemente
        token = jwt.encode(token_payload, secret_key_for_encode, algorithm="HS256")
        
        print(f"DEBUG send_reset_email: Token de reseteo GENERADO para user_id {user_id}: {token}")

        reset_link = f"http://127.0.0.1:8000/new_pass.html?token={token}" # Asumiendo frontend en puerto 8000

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
    # (Tu código de /login, asegurándote que use app.config['SECRET_KEY'] para encode)
    # ... (código de la función /login) ...
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
            # Asegúrate de que la tabla Usuarios tenga un campo 'estado' para verificar si el usuario está activo
            cursor.execute(
                "SELECT id_usuario, email, password_hash, rol, estado FROM Usuarios WHERE username = ?",
                (username,)
            )
            user_db_data = cursor.fetchone()

            if not user_db_data:
                print(f"Login - Usuario no encontrado: {username}")
                return jsonify({'error': 'Usuario no encontrado'}), 404

            user_id, email, db_password_hash, rol, user_estado = user_db_data
            
            if not user_estado: # Verificar si el usuario está activo (estado = 1 o True)
                print(f"Login - Intento de login para usuario inactivo: {username}")
                return jsonify({'error': 'La cuenta de usuario está inactiva.'}), 403 # Forbidden

            if bcrypt.checkpw(password.encode('utf-8'), db_password_hash):
                print(f"Login - Contraseña correcta para {username}")
                exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
                
                secret_key_for_encode = app.config.get('SECRET_KEY')
                print(f"DEBUG login: SECRET_KEY para ENCODE (sesión): '{secret_key_for_encode}'")

                token_payload = {
                    'user_id': user_id,
                    'email': email,
                    'rol': rol,
                    'username': username, 
                    'exp': exp_time 
                }
                token = jwt.encode(token_payload, secret_key_for_encode, algorithm="HS256")
                
                print(f"Login - Exitoso para {username}. Token generado. Enviando respuesta.")
                return jsonify({
                    'message': 'Login exitoso', 
                    'token': token, 
                    'rol': rol,
                    'username': username 
                }), 200
            else:
                print(f"Login - Contraseña incorrecta para {username}")
                return jsonify({'error': 'Credenciales inválidas'}), 401
        except Exception as db_e:
            if conn: conn.rollback()
            print(f"Error de BD en /login: {str(db_e)}")
            return jsonify({'error': f'Error de base de datos en login: {str(db_e)}'}), 500
        finally:
            if conn: conn.close()
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
    # (Tu código de /usuarios GET como lo tenías)
    # ... (código de la función /usuarios GET) ...
    print(f"API /usuarios GET: Solicitud recibida por admin con ID: {admin_user_id_from_token}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, username, email, rol, estado FROM Usuarios")
        
        columns = [column[0] for column in cursor.description]
        usuarios = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        print(f"API /usuarios GET: Devolviendo {len(usuarios)} usuarios.")
        return jsonify(usuarios), 200
    except Exception as e:
        print(f"Error en /usuarios GET: {str(e)}")
        return jsonify({'error': f'Error interno del servidor al obtener usuarios: {str(e)}'}), 500
    finally:
        if conn: conn.close()


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

# --- ENDPOINTS DE GESTIÓN DE INVENTARIO ---
@app.route('/inventory/entry', methods=['POST'])
@admin_required
def registrar_entrada_inventario(admin_user_id_from_token):
    # (Tu código de /inventory/entry como lo tenías)
    # ... (código de la función /inventory/entry) ...
    data = request.get_json()
    if not data: return jsonify({'error': 'No se recibieron datos JSON'}), 400
    print(f"API /inventory/entry POST: Admin ID {admin_user_id_from_token} registrando entrada. Datos: {data}")

    id_material = data.get('id_material')
    cantidad_entrada = data.get('cantidad_entrada')

    if id_material is None or cantidad_entrada is None:
        return jsonify({'error': 'Se requiere id_material y cantidad_entrada'}), 400
    try:
        cantidad_entrada = int(cantidad_entrada)
        if cantidad_entrada <= 0: return jsonify({'error': 'cantidad_entrada debe ser un número positivo'}), 400
    except ValueError: return jsonify({'error': 'cantidad_entrada debe ser un número entero'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cantidad, nombre FROM Materiales WHERE id_material = ?", (id_material,))
        material_actual = cursor.fetchone()
        if not material_actual: return jsonify({'error': f'Material con ID {id_material} no encontrado'}), 404
        
        stock_actual, nombre_material = material_actual
        nuevo_stock = stock_actual + cantidad_entrada
        fecha_actualizacion = datetime.datetime.now()

        sql_update = """
            UPDATE Materiales SET cantidad = ?, fecha_ultima_actualizacion = ?, id_usuario_ultima_actualizacion = ?
            WHERE id_material = ? """
        cursor.execute(sql_update, (nuevo_stock, fecha_actualizacion, admin_user_id_from_token, id_material))
        conn.commit()

        if cursor.rowcount == 0: return jsonify({'error': 'No se pudo actualizar el inventario del material'}), 500

        print(f"API /inventory/entry POST: Entrada para '{nombre_material}' (ID: {id_material}). Nuevo stock: {nuevo_stock}")
        return jsonify({'message': 'Entrada de inventario registrada', 'id_material': id_material, 
                        'nombre_material': nombre_material, 'cantidad_entrada': cantidad_entrada, 
                        'nuevo_stock': nuevo_stock}), 200
    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en /inventory/entry: {str(e)}")
        return jsonify({'error': f'Error interno al registrar entrada: {str(e)}'}), 500
    finally:
        if conn: conn.close()


@app.route('/inventory/exit', methods=['POST'])
@admin_required
def registrar_salida_inventario(admin_user_id_from_token):
    # (Tu código de /inventory/exit como lo tenías)
    # ... (código de la función /inventory/exit) ...
    data = request.get_json()
    if not data: return jsonify({'error': 'No se recibieron datos JSON'}), 400
    print(f"API /inventory/exit POST: Admin ID {admin_user_id_from_token} registrando salida. Datos: {data}")

    id_material = data.get('id_material')
    cantidad_salida = data.get('cantidad_salida')

    if id_material is None or cantidad_salida is None:
        return jsonify({'error': 'Se requiere id_material y cantidad_salida'}), 400
    try:
        cantidad_salida = int(cantidad_salida)
        if cantidad_salida <= 0: return jsonify({'error': 'cantidad_salida debe ser un número positivo'}), 400
    except ValueError: return jsonify({'error': 'cantidad_salida debe ser un número entero'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT cantidad, nombre FROM Materiales WHERE id_material = ?", (id_material,))
        material_actual = cursor.fetchone()
        if not material_actual: return jsonify({'error': f'Material con ID {id_material} no encontrado'}), 404
        
        stock_actual, nombre_material = material_actual

        if stock_actual < cantidad_salida:
            print(f"API /inventory/exit POST: Stock insuficiente para '{nombre_material}' (ID: {id_material}).")
            return jsonify({'error': 'Existencias insuficientes', 'id_material': id_material, 
                            'nombre_material': nombre_material, 'stock_actual': stock_actual, 
                            'cantidad_solicitada': cantidad_salida}), 400
        
        nuevo_stock = stock_actual - cantidad_salida
        fecha_actualizacion = datetime.datetime.now()

        sql_update = """
            UPDATE Materiales SET cantidad = ?, fecha_ultima_actualizacion = ?, id_usuario_ultima_actualizacion = ?
            WHERE id_material = ? """
        cursor.execute(sql_update, (nuevo_stock, fecha_actualizacion, admin_user_id_from_token, id_material))
        conn.commit()

        if cursor.rowcount == 0: return jsonify({'error': 'No se pudo actualizar el inventario'}), 500

        print(f"API /inventory/exit POST: Salida para '{nombre_material}' (ID: {id_material}). Nuevo stock: {nuevo_stock}")
        return jsonify({'message': 'Salida de inventario registrada', 'id_material': id_material, 
                        'nombre_material': nombre_material, 'cantidad_salida': cantidad_salida, 
                        'nuevo_stock': nuevo_stock}), 200
    except Exception as e:
        if conn: conn.rollback()
        print(f"Error en /inventory/exit: {str(e)}")
        return jsonify({'error': f'Error interno al registrar salida: {str(e)}'}), 500
    finally:
        if conn: conn.close()


# Ruta de prueba básica
@app.route('/')
def hello():
    return "¡API de Carrocería Alvarado funcionando!"

if __name__ == '__main__':
    app.run(debug=True, port=5000) # Ejecutar en puerto 5000
