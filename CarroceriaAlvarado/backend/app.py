from flask import Flask
import pyodbc

app = Flask(__name__)

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

@app.route('/')
def hello():
    return "¡Aplicación Flask funcionando! Prueba /usuarios o /materiales"

@app.route('/usuarios')
def listar_usuarios():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, username, rol, estado FROM Usuarios")
        usuarios = cursor.fetchall()
        conn.close()

        # Convertir los resultados en una lista de diccionarios para facilitar la lectura
        usuarios_list = [
            {'id_usuario': row[0], 'username': row[1], 'rol': row[2], 'estado': row[3]}
            for row in usuarios
        ]
        return {'usuarios': usuarios_list}
    except Exception as e:
        return {'error': str(e)}

@app.route('/materiales')
def listar_materiales():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_material, nombre, descripcion, cantidad, precio_unitario FROM Materiales")
        materiales = cursor.fetchall()
        conn.close()

        # Convertir los resultados en una lista de diccionarios
        materiales_list = [
            {'id_material': row[0], 'nombre': row[1], 'descripcion': row[2], 
             'cantidad': row[3], 'precio_unitario': float(row[4])}
            for row in materiales
        ]
        return {'materiales': materiales_list}
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    app.run(debug=True)