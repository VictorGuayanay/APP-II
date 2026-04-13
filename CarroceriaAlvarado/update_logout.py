import os
import re

def update_logout_buttons(directory):
    html_files = [f for f in os.listdir(directory) if f.endswith('.html')]
    
    # regex for logout button
    # Patterns to match: <a ... id="logoutButton" ...>Cerrar Sesión</a>
    logout_pattern = re.compile(r'<a[^>]*id="logoutButton"[^>]*>.*?Cerrar Sesión.*?</a>', re.IGNORECASE)
    
    new_button = '<a href="#" id="logoutButton" class="btn-logout ms-3"><i class="fa fa-sign-out"></i> Cerrar Sesión</a>'
    
    for filename in html_files:
        path = os.path.join(directory, filename)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if 'logoutButton' in content:
            new_content = logout_pattern.sub(new_button, content)
            
            if new_content != content:
                print(f"Updating logout button in {filename}...")
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

if __name__ == "__main__":
    frontend_dir = r"c:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\frontend"
    update_logout_buttons(frontend_dir)
    print("Standardization complete!")
