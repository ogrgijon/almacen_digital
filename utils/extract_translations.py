#!/usr/bin/env python3
"""
Script to extract translatable strings from Python source files
"""

import re
import os
from pathlib import Path
import polib

def extract_strings_from_file(file_path):
    """Extract translatable strings from a Python file"""
    strings = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all _("string") patterns
        pattern = r'_\(\s*["\']([^"\']+)["\']\s*\)'
        matches = re.findall(pattern, content)
        strings.extend(matches)

        # Find all _("string with {placeholder}").format() patterns
        pattern_format = r'_\(\s*["\']([^"\']*\{[^}]+\}[^"\']*)["\']\s*\)'
        matches_format = re.findall(pattern_format, content)
        strings.extend(matches_format)

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return strings

def extract_all_strings():
    """Extract strings from all Python files"""
    all_strings = set()

    # Find all Python files
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', '.vscode']]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                strings = extract_strings_from_file(file_path)
                all_strings.update(strings)

    return sorted(list(all_strings))

def update_po_files(strings):
    """Update .po files with new strings"""
    locales_dir = Path('locales')

    for lang_dir in locales_dir.iterdir():
        if lang_dir.is_dir():
            po_file = lang_dir / 'LC_MESSAGES' / 'almacen.po'
            if po_file.exists():
                print(f"Updating {po_file}")
                po = polib.pofile(str(po_file))

                # Add new strings
                for string in strings:
                    if not po.find(string):
                        entry = polib.POEntry(
                            msgid=string,
                            msgstr="" if lang_dir.name != 'en' else string
                        )
                        po.append(entry)

                po.save(str(po_file))
                print(f"  ✓ Updated {po_file}")

if __name__ == '__main__':
    print("Extracting translatable strings...")
    strings = extract_all_strings()
    print(f"Found {len(strings)} unique strings")

    print("Updating .po files...")
    update_po_files(strings)

    print("Compiling translations...")
    os.system('python utils/compile_translations.py')