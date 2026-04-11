import os
import re

frontend_dir = r'c:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\frontend'
html_files = [f for f in os.listdir(frontend_dir) if f.endswith('.html')]

# Patterns to clean up
READY_BLOCK_REGEX = re.compile(r'\$\(document\)\.ready\(function\s*\(\)\s*\{.*?//\s*---', re.DOTALL)
SIDEBAR_TOGGLE_REGEX = re.compile(r'\$\(\'#sidebarCollapse\'\)\.on\(\'click\'.*?\}\);', re.DOTALL)
LOGOUT_REGEX = re.compile(r'\$\(\'#logoutButton\'\)\.on\(\'click\'.*?\}\);', re.DOTALL)
AUTH_STUFF_REGEX = re.compile(r'const\s+token\s*=\s*localStorage\.getItem\(\'token\'\);.*?if\s*\(!token\).*?\}.*?if\s*\(loggedInUsername\).*?\}', re.DOTALL)

def clean_html(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # 1. Standardize card class
    content = content.replace('class="card"', 'class="dashboard-card shadow-sm"')
    content = content.replace('class="card animate', 'class="dashboard-card shadow-sm animate')
    
    # 2. Fix script tags (clean up previous attempts)
    content = re.sub(r'<script src="js/config\.js"></script>.*?(<script src="vendor/jquery)', r'<script src="js/config.js"></script>\n    <script src="js/dashboard-core.js"></script>\n    \1', content, flags=re.DOTALL)
    
    # 3. Remove redundant scripts - This is tricky with regex, so we'll do specific replacements
    # but only for blocks we are sure about.
    
    # Actually, let's just do the ones we identified as highly redundant
    content = re.sub(r'//\s*Funcionalidad para mostrar/ocultar el sidebar.*?\}\);', '', content, flags=re.DOTALL)
    content = re.sub(r'//\s*--- Protecci.n de P.gina.*?//\s*---', '// ---', content, flags=re.DOTALL) # Handles encoded chars
    content = re.sub(r'\$\(\'#logoutButton\'\)\.on\(\'click\'.*?\}\);', '', content, flags=re.DOTALL|re.IGNORECASE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

for html_file in html_files:
    if html_file not in ['index.html', 'register.html', 'reset_pass.html', 'new_pass.html', 'registrer.html']:
        print(f"Cleaning {html_file}...")
        clean_html(os.path.join(frontend_dir, html_file))

print("Cleanup complete.")
