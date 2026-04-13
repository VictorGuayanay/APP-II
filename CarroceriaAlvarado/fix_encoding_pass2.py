
import os

replacements = {
    "pógina": "página",
    "Cólculo": "Cálculo",
    "Carrocerï¿½as": "Carrocerías",
    "Administraciï¿½n": "Administración",
    "Visiï¿½n": "Visión",
    "Aï¿½adir": "Añadir",
    "ï¿½rdenes": "Órdenes",
    "configuraciï¿½n": "configuración",
    "Sesiï¿½n": "Sesión",
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
