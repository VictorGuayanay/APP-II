import pyodbc
import os
from dotenv import load_dotenv

load_dotenv(r'c:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\backend\.env')

conn_str = (
    f"DRIVER={{{os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')}}};"
    f"SERVER={os.environ.get('DB_SERVER', r'DESKTOP-OJ81G31\SQLEXPRESS')};" 
    f"DATABASE={os.environ.get('DB_NAME', 'CarroceriaAlvaradoDB')};"
    f"Trusted_Connection={os.environ.get('DB_TRUSTED_CONNECTION', 'yes')};"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario, username, email FROM Usuarios")
    rows = cursor.fetchall()
    print("Usuarios en la base de datos:")
    for row in rows:
        print(f"ID: {row[0]}, User: {row[1]}, Email: {row[2]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
