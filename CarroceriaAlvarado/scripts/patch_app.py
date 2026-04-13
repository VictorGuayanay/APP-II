#!/usr/bin/env python3
"""
Script de parcheo para app.py - Carrocería Alvarado
Aplica todos los cambios de hardening de producción en el orden correcto:
  1. Agrega imports de Flask-Limiter
  2. Agrega Limiter y blacklist cache después de APP_CONFIG
  3. Inserta decoradores (token_required, admin_required, roles_required) ANTES de las rutas
  4. Agrega rate limiting en /login y /reset_password
  5. Mejora el endpoint /logout con revocación de token (SEC-09)
  6. Agrega las funciones de utilidad para BD (cargar_config_desde_bd, 
     guardar_config_en_bd, revocar_token, es_token_revocado) - BE-03, SEC-09
  7. Modifica update_configuraciones para persistir en BD
  8. Agrega llamada de inicio cargar_config_desde_bd() al final
"""
import sys

APP_PY = 'app.py'

with open(APP_PY, 'r', encoding='utf-8') as f:
    content = f.read()

# =============================================================
# 1. Agregar imports de Flask-Limiter (después de flask_cors)
# =============================================================
OLD_IMPORT = 'from flask_cors import CORS\nimport pyodbc'
NEW_IMPORT = ('from flask_cors import CORS\n'
              'from flask_limiter import Limiter\n'
              'from flask_limiter.util import get_remote_address\n'
              'import pyodbc')
if 'flask_limiter' not in content:
    content = content.replace(OLD_IMPORT, NEW_IMPORT, 1)
    print('[1] Imports de Flask-Limiter agregados.')
else:
    print('[1] Flask-Limiter ya importado.')

# =============================================================
# 2. Agregar Limiter + blacklist cache después de APP_CONFIG
# =============================================================
# Busca el bloque de APP_CONFIG y agrega después
OLD_APP_CONFIG_BLOCK = (
    'APP_CONFIG = {\n'
    '    "reset_token_expiry_minutes"'
)
LIMITER_BLOCK = (
    '\n\n# --- RATE LIMITING (SEC-06) ---\n'
    'limiter = Limiter(\n'
    '    get_remote_address,\n'
    '    app=app,\n'
    '    default_limits=[],\n'
    '    storage_uri="memory://"\n'
    ')\n'
    '\n'
    '# Caché en memoria para JWT blacklist (se persiste en BD)\n'
    '_TOKEN_BLACKLIST_CACHE = set()\n'
)

# Encontrar el fin del bloque APP_CONFIG (cierre })
if '_TOKEN_BLACKLIST_CACHE' not in content:
    # Encontrar posición del } de cierre de APP_CONFIG
    idx = content.find(OLD_APP_CONFIG_BLOCK)
    if idx >= 0:
        close_brace = content.find('\n}', idx)
        insert_pos = close_brace + 2  # después del cierre
        content = content[:insert_pos] + LIMITER_BLOCK + content[insert_pos:]
        print('[2] Limiter y blacklist cache agregados.')
    else:
        print('[2] ERROR: No se encontró APP_CONFIG block.')
else:
    print('[2] Limiter y blacklist ya presentes.')

# =============================================================
# 3. Agregar funciones de utilidad (BE-03 + SEC-09) justo 
#    después de get_db_connection()
# =============================================================
UTIL_FUNCTIONS = '''

# ================================================================
# BE-03: PERSISTENCIA DE CONFIGURACIONES EN BASE DE DATOS
# ================================================================
def cargar_config_desde_bd():
    """Carga configuraciones desde SQL Server al iniciar la app."""
    global APP_CONFIG
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT clave, valor FROM Configuraciones WHERE activo = 1")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                clave, valor = row[0], row[1]
                if clave in APP_CONFIG:
                    try:
                        APP_CONFIG[clave] = int(valor)
                    except (ValueError, TypeError):
                        APP_CONFIG[clave] = valor
            print(f"APP INIT: Configuraciones cargadas desde BD: {APP_CONFIG}")
        else:
            print("APP INIT: Tabla Configuraciones vacía, usando valores .env")
    except Exception as e:
        print(f"APP INIT: No se pudo cargar config desde BD: {str(e)}")
    finally:
        if conn:
            conn.close()


def guardar_config_en_bd(clave, valor):
    """Guarda o actualiza una configuración en la BD (MERGE)."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            MERGE Configuraciones AS target
            USING (VALUES (?, ?)) AS source (clave, valor)
            ON target.clave = source.clave
            WHEN MATCHED THEN
                UPDATE SET valor = source.valor, fecha_actualizacion = GETDATE()
            WHEN NOT MATCHED THEN
                INSERT (clave, valor, activo, fecha_actualizacion)
                VALUES (source.clave, source.valor, 1, GETDATE());
        """, (clave, str(valor)))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error guardando config '{clave}' en BD: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()


# ================================================================
# SEC-09: BLACKLIST DE TOKENS JWT EN BASE DE DATOS
# ================================================================
def revocar_token(token):
    """Agrega un token a la blacklist en BD al hacer logout."""
    conn = None
    try:
        secret_key = app.config.get('SECRET_KEY')
        try:
            decoded = __import__('jwt').decode(token, secret_key, algorithms=["HS256"])
            exp = decoded.get('exp')
            user_id = decoded.get('user_id')
            import datetime as _dt
            expiry_dt = _dt.datetime.fromtimestamp(exp, tz=_dt.timezone.utc) if exp else None
        except Exception:
            expiry_dt = None
            user_id = None
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO TokensRevocados (token_hash, id_usuario, fecha_revocacion, fecha_expiracion)
            VALUES (?, ?, GETDATE(), ?)
        """, (str(hash(token)), user_id, expiry_dt))
        conn.commit()
        _TOKEN_BLACKLIST_CACHE.add(hash(token))
        return True
    except Exception as e:
        print(f"Error revocando token: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()


def es_token_revocado(token):
    """Verifica si un token está en la blacklist (caché + BD)."""
    token_hash = hash(token)
    if token_hash in _TOKEN_BLACKLIST_CACHE:
        return True
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM TokensRevocados WHERE token_hash = ? "
            "AND (fecha_expiracion IS NULL OR fecha_expiracion > GETDATE())",
            (str(token_hash),)
        )
        if cursor.fetchone():
            _TOKEN_BLACKLIST_CACHE.add(token_hash)
            return True
        return False
    except Exception as e:
        print(f"Error verificando blacklist: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

'''

MARKER_AFTER = 'def get_db_connection():'
if 'cargar_config_desde_bd' not in content:
    # Encontrar el final de get_db_connection
    idx = content.find(MARKER_AFTER)
    if idx >= 0:
        # Buscar el final de esta función
        func_body_end = content.find('\ndef ', idx + len(MARKER_AFTER))
        if func_body_end < 0:
            func_body_end = content.find('\n@app.', idx + len(MARKER_AFTER))
        content = content[:func_body_end] + UTIL_FUNCTIONS + content[func_body_end:]
        print('[3] Funciones de utilidad BD agregadas.')
    else:
        print('[3] ERROR: No se encontró get_db_connection.')
else:
    print('[3] Funciones de utilidad ya presentes.')

# =============================================================
# 4. Mover decoradores ANTES de las rutas
# =============================================================
DEC_START_MARKER = '# --- DECORADORES ---\ndef token_required'
DEC_END_MARKER_AFTER = '    return decorator\n'  # fin de roles_required

FIRST_ROUTE_MARKER = "@app.route('/registro', methods=['POST'])"

if DEC_START_MARKER in content and FIRST_ROUTE_MARKER in content:
    # Extraer bloque decoradores
    dec_start_idx = content.find(DEC_START_MARKER)
    # Encontrar fin: último 'return decorator' antes de la primera @app.route después de los decoradores  
    search_from = dec_start_idx + len(DEC_START_MARKER)
    dec_end_idx = content.find(DEC_END_MARKER_AFTER, search_from) + len(DEC_END_MARKER_AFTER)
    
    decorator_block = content[dec_start_idx:dec_end_idx]
    
    # Verificar si ya está antes de /registro
    route_idx = content.find(FIRST_ROUTE_MARKER)
    if dec_start_idx > route_idx:
        # Decoradores están DESPUÉS de /registro → moverlos antes
        content_without_dec = content[:dec_start_idx].rstrip() + '\n\n' + content[dec_end_idx:]
        
        # Ahora insertarlos antes de /registro en el contenido sin decoradores
        route_idx2 = content_without_dec.find(FIRST_ROUTE_MARKER)
        content = (content_without_dec[:route_idx2] + 
                   decorator_block + '\n\n' + 
                   content_without_dec[route_idx2:])
        print('[4] Decoradores movidos antes de las rutas.')
    else:
        print('[4] Decoradores ya están antes de las rutas.')
else:
    print('[4] ADVERTENCIA: No se encontraron los marcadores de decoradores/rutas.')

# =============================================================
# 5. Rate limiting en /login y /reset_password
# =============================================================
OLD_LOGIN_ROUTE = "@app.route('/login', methods=['POST', 'OPTIONS'])\ndef login():"
NEW_LOGIN_ROUTE = ("@app.route('/login', methods=['POST', 'OPTIONS'])\n"
                   "@limiter.limit('10 per minute')  # SEC-06: Prevenir fuerza bruta\n"
                   "def login():")

OLD_RESET_ROUTE = "@app.route('/reset_password', methods=['POST'])\ndef reset_password_request():"
NEW_RESET_ROUTE = ("@app.route('/reset_password', methods=['POST'])\n"
                   "@limiter.limit('5 per minute')  # SEC-06: Limitar solicitudes de reseteo\n"
                   "def reset_password_request():")

if '@limiter.limit' not in content:
    content = content.replace(OLD_LOGIN_ROUTE, NEW_LOGIN_ROUTE, 1)
    content = content.replace(OLD_RESET_ROUTE, NEW_RESET_ROUTE, 1)
    print('[5] Rate limiting aplicado a /login y /reset_password.')
else:
    print('[5] Rate limiting ya presente.')

# =============================================================
# 6. Mejorar /logout con revocación de token (SEC-09)
# =============================================================
OLD_LOGOUT_BODY = (
    'try:\n'
    '        # Obtener el token del header para logging\n'
    '        auth_header = request.headers.get(\'Authorization\')'
)
NEW_LOGOUT_BODY = (
    'try:\n'
    '        auth_header = request.headers.get(\'Authorization\')'
)

if '# Obtener el token del header para logging' in content:
    content = content.replace(OLD_LOGOUT_BODY, NEW_LOGOUT_BODY, 1)

OLD_LOGOUT_PRINT = 'print(f"API /logout POST: Usuario {username} (ID: {user_id}) ha cerrado sesión")'
NEW_LOGOUT_PRINT = (
    'revocar_token(token)  # SEC-09\n'
    '                print(f"API /logout POST: Token revocado para {username} (ID: {user_id})")'
)
if 'ha cerrado sesión' in content and 'revocar_token(token)' not in content:
    content = content.replace(OLD_LOGOUT_PRINT, NEW_LOGOUT_PRINT, 1)
    print('[6] Revocación de token en /logout aplicada.')
else:
    print('[6] Logout ya tiene revocación o no requiere cambio.')

# =============================================================
# 7. Verificación de blacklist en token_required
# =============================================================
OLD_TOKEN_CHECK = (
    "data = jwt.decode(token, secret_key_for_decode, algorithms=[\"HS256\"])\n"
    "            decoded_user_rol = data.get('rol')\n"
    "            decoded_user_id = data.get('user_id')"
)
NEW_TOKEN_CHECK = (
    "data = jwt.decode(token, secret_key_for_decode, algorithms=[\"HS256\"])\n"
    "            decoded_user_rol = data.get('rol')\n"
    "            decoded_user_id = data.get('user_id')\n"
    "\n"
    "            # SEC-09: Verificar blacklist de tokens revocados\n"
    "            if es_token_revocado(token):\n"
    "                return jsonify({'error': 'Sesión expirada. Inicia sesión nuevamente.'}), 401"
)
if 'es_token_revocado' not in content:
    content = content.replace(OLD_TOKEN_CHECK, NEW_TOKEN_CHECK, 1)
    print('[7] Verificación de blacklist en @token_required aplicada.')
else:
    print('[7] Verificación de blacklist ya presente.')

# =============================================================
# 8. Persistir configuraciones en update_configuraciones
# =============================================================
if 'guardar_config_en_bd(' not in content:
    content = content.replace(
        "APP_CONFIG['reset_token_expiry_minutes'] = new_expiry_int",
        "APP_CONFIG['reset_token_expiry_minutes'] = new_expiry_int\n"
        "            guardar_config_en_bd('reset_token_expiry_minutes', new_expiry_int)  # BE-03",
        1
    )
    content = content.replace(
        "APP_CONFIG['max_failed_login_attempts'] = new_attempts_int",
        "APP_CONFIG['max_failed_login_attempts'] = new_attempts_int\n"
        "            guardar_config_en_bd('max_failed_login_attempts', new_attempts_int)  # BE-03",
        1
    )
    content = content.replace(
        "APP_CONFIG['global_low_stock_threshold'] = new_low_stock_threshold_int",
        "APP_CONFIG['global_low_stock_threshold'] = new_low_stock_threshold_int\n"
        "            guardar_config_en_bd('global_low_stock_threshold', new_low_stock_threshold_int)  # BE-03",
        1
    )
    print('[8] Persistencia en BD para configuraciones aplicada.')
else:
    print('[8] Persistencia ya presente.')

# =============================================================
# 9. Agregar llamada de inicio al final del archivo
# =============================================================
INIT_CALL = (
    '\n# ================================================================\n'
    '# INICIALIZACIÓN (BE-03): Cargar config desde BD al arrancar\n'
    '# ================================================================\n'
    'with app.app_context():\n'
    '    try:\n'
    '        cargar_config_desde_bd()\n'
    '    except Exception as _e:\n'
    '        print(f"APP INIT: cargar_config_desde_bd falló: {_e}. Usando .env.")\n'
)
MAIN_BLOCK = "if __name__ == '__main__':"

if 'cargar_config_desde_bd()' not in content and MAIN_BLOCK in content:
    content = content.replace(MAIN_BLOCK, INIT_CALL + '\n' + MAIN_BLOCK, 1)
    print('[9] Llamada de inicio cargar_config_desde_bd() agregada.')
elif 'cargar_config_desde_bd()' in content:
    print('[9] Llamada de inicio ya presente.')

# =============================================================
# Guardar sin BOM
# =============================================================
import ast
try:
    ast.parse(content)
    print('\n✅ Sintaxis Python válida.')
except SyntaxError as e:
    print(f'\n❌ Error de sintaxis: {e}')
    sys.exit(1)

with open(APP_PY, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(content)

print(f'✅ app.py actualizado correctamente ({len(content.splitlines())} líneas)')
