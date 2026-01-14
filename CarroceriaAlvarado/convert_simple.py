"""
Script simplificado para convertir Markdown a HTML y luego a PDF
Usa solo librerías estándar de Python y wkhtmltopdf si está disponible
"""

import os
import subprocess

def convert_md_to_html(md_file, html_file):
    """Convierte Markdown a HTML básico"""
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convertir Markdown básico a HTML
    html_content = md_content
    
    # Convertir headers
    html_content = html_content.replace('# ', '<h1>').replace('\n', '</h1>\n', 1)
    html_content = html_content.replace('## ', '<h2>').replace('\n', '</h2>\n')
    html_content = html_content.replace('### ', '<h3>').replace('\n', '</h3>\n')
    
    # Convertir tablas (básico)
    lines = html_content.split('\n')
    in_table = False
    new_lines = []
    
    for line in lines:
        if '|' in line and not line.strip().startswith('<!--'):
            if not in_table:
                new_lines.append('<table border="1" cellpadding="5" cellspacing="0">')
                in_table = True
            
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            
            if all(c.replace('-', '').strip() == '' for c in cells):
                # Es la línea separadora, ignorar
                continue
            
            # Determinar si es header (primera línea de la tabla)
            if '**' in line or line == lines[lines.index(line)]:
                new_lines.append('<tr>')
                for cell in cells:
                    new_lines.append(f'<th>{cell}</th>')
                new_lines.append('</tr>')
            else:
                new_lines.append('<tr>')
                for cell in cells:
                    new_lines.append(f'<td>{cell}</td>')
                new_lines.append('</tr>')
        else:
            if in_table:
                new_lines.append('</table>')
                in_table = False
            new_lines.append(line)
    
    html_content = '\n'.join(new_lines)
    
    # Convertir negrita
    import re
    html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
    html_content = re.sub(r'`(.*?)`', r'<code>\1</code>', html_content)
    
    # Crear HTML completo
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Diccionario de Datos</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                line-height: 1.6;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                border-bottom: 2px solid #95a5a6;
                padding-bottom: 5px;
                margin-top: 30px;
            }}
            h3 {{
                color: #7f8c8d;
                margin-top: 20px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th {{
                background-color: #3498db;
                color: white;
                padding: 10px;
                text-align: left;
            }}
            td {{
                padding: 8px;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: Courier New, monospace;
            }}
            strong {{
                color: #2c3e50;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✓ HTML creado: {html_file}")
    return html_file

if __name__ == "__main__":
    md_file = "docs/diccionario_datos.md"
    html_file = "docs/diccionario_datos.html"
    
    if os.path.exists(md_file):
        convert_md_to_html(md_file, html_file)
        print(f"\n✅ Archivo HTML creado exitosamente!")
        print(f"📄 Puedes abrir el archivo HTML en tu navegador")
        print(f"📄 Y usar 'Imprimir > Guardar como PDF' para crear el PDF")
        print(f"\n📁 Ubicación: {os.path.abspath(html_file)}")
    else:
        print(f"❌ No se encontró el archivo: {md_file}")
