#!/usr/bin/env python3
"""
Script para compilar archivos .po a .mo
"""

import polib
from pathlib import Path

def compile_translations():
    """Compila todos los archivos .po a .mo"""
    locales_dir = Path(__file__).parent / 'locales'
    
    for po_file in locales_dir.rglob('*.po'):
        mo_file = po_file.with_suffix('.mo')
        print(f"Compilando {po_file} -> {mo_file}")
        
        try:
            po = polib.pofile(str(po_file))
            po.save_as_mofile(str(mo_file))
            print(f"  ✓ Compilado exitosamente")
        except Exception as e:
            print(f"  ✗ Error: {e}")

if __name__ == '__main__':
    compile_translations()
