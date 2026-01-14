"""
Script para convertir el diccionario de datos de Markdown a PDF
Usa markdown2 y weasyprint para la conversión
"""

import os
import sys

# Intentar importar las librerías necesarias
try:
    import markdown2
    print("✓ markdown2 disponible")
except ImportError:
    print("✗ markdown2 no está instalado")
    print("Instalando markdown2...")
    os.system("pip install markdown2")
    import markdown2

try:
    from weasyprint import HTML, CSS
    print("✓ weasyprint disponible")
except ImportError:
    print("✗ weasyprint no está instalado")
    print("Instalando weasyprint...")
    os.system("pip install weasyprint")
    from weasyprint import HTML, CSS

def markdown_to_pdf(md_file, pdf_file):
    """Convierte un archivo Markdown a PDF"""
    
    # Leer el archivo Markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convertir Markdown a HTML
    html_content = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks', 'header-ids'])
    
    # Crear HTML completo con estilos
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
                line-height: 1.4;
                color: #333;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                font-size: 24pt;
                page-break-after: avoid;
            }}
            h2 {{
                color: #34495e;
                border-bottom: 2px solid #95a5a6;
                padding-bottom: 5px;
                margin-top: 20px;
                font-size: 18pt;
                page-break-after: avoid;
            }}
            h3 {{
                color: #7f8c8d;
                font-size: 14pt;
                margin-top: 15px;
                page-break-after: avoid;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 15px 0;
                font-size: 9pt;
                page-break-inside: avoid;
            }}
            th {{
                background-color: #3498db;
                color: white;
                padding: 8px;
                text-align: left;
                font-weight: bold;
            }}
            td {{
                border: 1px solid #ddd;
                padding: 6px;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }}
            pre {{
                background-color: #f4f4f4;
                padding: 10px;
                border-left: 3px solid #3498db;
                overflow-x: auto;
                page-break-inside: avoid;
            }}
            strong {{
                color: #2c3e50;
            }}
            .page-break {{
                page-break-after: always;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convertir HTML a PDF
    print(f"Convirtiendo {md_file} a PDF...")
    HTML(string=full_html).write_pdf(pdf_file)
    print(f"✓ PDF creado exitosamente: {pdf_file}")

if __name__ == "__main__":
    # Rutas de archivos
    md_file = "docs/diccionario_datos.md"
    pdf_file = "docs/diccionario_datos.pdf"
    
    # Verificar que existe el archivo Markdown
    if not os.path.exists(md_file):
        print(f"Error: No se encontró el archivo {md_file}")
        sys.exit(1)
    
    # Convertir a PDF
    try:
        markdown_to_pdf(md_file, pdf_file)
        print(f"\n✅ Conversión completada exitosamente!")
        print(f"📄 Archivo PDF: {os.path.abspath(pdf_file)}")
    except Exception as e:
        print(f"\n❌ Error durante la conversión: {str(e)}")
        sys.exit(1)
