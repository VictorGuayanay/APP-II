import os
import re

def update_html_files(directory):
    html_files = [f for f in os.listdir(directory) if f.endswith('.html')]
    
    # regexes for replacement
    # 1. CSS
    css_pattern = re.compile(r'<link rel="stylesheet".*?href=".*?bootstrap.*?\.min\.css".*?>', re.IGNORECASE)
    new_css = '<link rel="stylesheet" type="text/css" href="vendor/bootstrap/css/bootstrap5.min.css">'
    
    # 2. JS
    js_pattern = re.compile(r'<script src=".*?bootstrap.*?\.min\.js"></script>', re.IGNORECASE)
    new_js = '<script src="vendor/bootstrap/js/bootstrap5.bundle.min.js"></script>'
    
    # 3. Data-toggle, data-target, data-dismiss (BS4 to BS5)
    # We use negative lookahead to avoid double bs-bs
    toggle_pattern = re.compile(r'data-toggle=(["\'])(?!bs-)', re.IGNORECASE)
    target_pattern = re.compile(r'data-target=(["\'])(?!bs-)', re.IGNORECASE)
    dismiss_pattern = re.compile(r'data-dismiss=(["\'])(?!bs-)', re.IGNORECASE)
    
    for filename in html_files:
        path = os.path.join(directory, filename)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Apply replacements
        content = css_pattern.sub(new_css, content)
        content = js_pattern.sub(new_js, content)
        
        content = toggle_pattern.sub(r'data-bs-toggle=\1', content)
        content = target_pattern.sub(r'data-bs-target=\1', content)
        content = dismiss_pattern.sub(r'data-bs-dismiss=\1', content)
        
        if content != original_content:
            print(f"Updating {filename}...")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            # print(f"No changes needed for {filename}")
            pass

if __name__ == "__main__":
    frontend_dir = r"c:\Users\ASUS\Proyectos\APP-II\CarroceriaAlvarado\frontend"
    update_html_files(frontend_dir)
    print("Done!")
