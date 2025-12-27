#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para Corregir Codificación UTF-8 en Archivos HTML
Carrocería Alvarado - 2025-12-27
"""

import os
import glob
from pathlib import Path

def fix_encoding():
    """Corrige la codificación de todos los archivos HTML en el directorio frontend"""
    
    frontend_dir = "frontend"
    archivos_corregidos = 0
    archivos_con_error = 0
    
    print("\n" + "="*50)
    print("  Corrección de Codificación UTF-8")
    print("="*50 + "\n")
    
    # Obtener todos los archivos HTML
    html_files = glob.glob(os.path.join(frontend_dir, "*.html"))
    
    if not html_files:
        print(f"❌ No se encontraron archivos HTML en {frontend_dir}")
        return
    
    print(f"Encontrados {len(html_files)} archivos HTML\n")
    
    for archivo_path in html_files:
        archivo_nombre = os.path.basename(archivo_path)
        
        try:
            print(f"Procesando: {archivo_nombre}...", end=" ")
            
            # Intentar leer con diferentes encodings
            contenido = None
            encoding_original = None
            
            # Intentar primero con latin-1 (Windows-1252)
            try:
                with open(archivo_path, 'r', encoding='latin-1') as f:
                    contenido = f.read()
                encoding_original = 'latin-1'
            except:
                pass
            
            # Si falla, intentar con cp1252
            if contenido is None:
                try:
                    with open(archivo_path, 'r', encoding='cp1252') as f:
                        contenido = f.read()
                    encoding_original = 'cp1252'
                except:
                    pass
            
            # Si falla, intentar con ISO-8859-1
            if contenido is None:
                try:
                    with open(archivo_path, 'r', encoding='iso-8859-1') as f:
                        contenido = f.read()
                    encoding_original = 'iso-8859-1'
                except:
                    pass
            
            if contenido is None:
                print("❌ ERROR: No se pudo leer el archivo")
                archivos_con_error += 1
                continue
            
            # Guardar con UTF-8 BOM
            with open(archivo_path, 'w', encoding='utf-8-sig') as f:
                f.write(contenido)
            
            print(f"✓ CORREGIDO (desde {encoding_original})")
            archivos_corregidos += 1
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            archivos_con_error += 1
    
    print("\n" + "="*50)
    print(f"Archivos corregidos: {archivos_corregidos}")
    print(f"Archivos con error: {archivos_con_error}")
    print("="*50 + "\n")
    
    if archivos_corregidos > 0:
        print("✓ Corrección completada!\n")
        print("Próximos pasos:")
        print("1. Refresca el navegador (Ctrl + Shift + R)")
        print("2. Verifica que las tildes y ñ se vean correctamente\n")

if __name__ == "__main__":
    fix_encoding()
