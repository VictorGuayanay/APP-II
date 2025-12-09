import sqlite3

conn = sqlite3.connect('inventario.db')
cursor = conn.cursor()

# Listar tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tablas en la base de datos:")
for table in tables:
    print(f"  - {table[0]}")

# Ver estructura de la tabla de materiales
print("\nBuscando tabla de materiales...")
for table in tables:
    if 'material' in table[0].lower():
        print(f"\nEstructura de {table[0]}:")
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

conn.close()
