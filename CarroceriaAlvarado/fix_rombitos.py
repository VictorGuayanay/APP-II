
import os

replacements = {
    "ï¿½": "",  # Temporary marker for the rombitos
    "Carrocerï¿½as": "Carrocerías",
    "Carrocerï¿½aa": "Carrocerías",
    "Administraciï¿½n": "Administración",
    "Visiï¿½n": "Visión",
    "Aï¿½adir": "Añadir",
    "ï¿½rdenes": "Órdenes",
    "configuraciï¿½n": "configuración",
    "Configuraciï¿½n": "Configuración",
    "Menï¿½": "Menú",
    "Sesiï¿½n": "Sesión",
    "Descripciï¿½n": "Descripción",
    "Cï¿½lculo": "Cálculo",
    "lï¿½gica": "lógica",
    "ï¿½rdenes": "Órdenes",
    "dï¿½a": "día",
    "dï¿½as": "días",
    "maï¿½ana": "mañana",
    "maï¿½ana": "mañana",
    "estï¿½": "está",
    "ï¿½Vence": "¡Vence",
    "ï¿½Orden": "¡Orden",
    "segï¿½n": "según",
    "especï¿½fica": "específica",
    "generarï¿½": "generará",
    "ï¿½l": "él",
    "Funciï¿½n": "Función",
    "estï¿½ndar": "estándar",
    "autotable": "autotable", # Keep
    "Riobamba": "Riobamba",
    "Telï¿½fono": "Teléfono",
    "Tï¿½tulo": "Título",
    "Direcciï¿½n": "Dirección",
    "ï¿½": "ó", # Often standalone ï¿½ is ó in this codebase (e.g. descripciï¿½n)
}

def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        for search, replace in replacements.items():
            content = content.replace(search, replace)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {filepath}")
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")

def main():
    root_dir = "frontend"
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith((".html", ".js", ".css")):
                fix_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
