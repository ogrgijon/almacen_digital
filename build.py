#!/usr/bin/env python3
"""
Build script for creating executables for HDDInventory
Supports Windows, macOS, and Linux
Supports both regular and portable builds

Usage:
    python build.py              # Regular build
    python build.py --portable   # Portable build
"""

import sys
import os
import shutil
import platform
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent


def get_platform_name():
    """Get normalized platform name"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    return system

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous builds...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        path = ROOT_DIR / dir_name
        if path.exists():
            shutil.rmtree(path)
            print(f"   Removed {dir_name}/")

def build_executable(portable=False):
    """Build executable using PyInstaller
    
    Args:
        portable: If True, creates portable build with --onedir
    """
    platform_name = get_platform_name()
    build_type = "portable" if portable else "regular"
    print(f"\nBuilding {build_type} version for {platform_name}...")
    
    # Base PyInstaller command
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--name=AlmacenDigital',
        '--windowed',
        '--onedir' if portable else '--onefile',  # Portable uses onedir
    ]
    
    # Add icon if it exists
    if (ROOT_DIR / 'icon.ico').exists():
        cmd.append('--icon=icon.ico')
    
    cmd.extend([
        f'--add-data=locales{os.pathsep}locales',
    ])
    
    # Add splash if it exists
    if (ROOT_DIR / 'splash.png').exists():
        cmd.append(f'--add-data=splash.png{os.pathsep}.')
    
    # Add icon to data if it exists
    if (ROOT_DIR / 'icon.ico').exists():
        cmd.append(f'--add-data=icon.ico{os.pathsep}.')
    
    cmd.extend([
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=PyQt6.QtCharts',
        '--hidden-import=matplotlib',
        '--hidden-import=matplotlib.backends.backend_qtagg',
        '--hidden-import=PIL',
        '--hidden-import=openpyxl',
        '--hidden-import=psutil',
        '--hidden-import=squarify',
        '--hidden-import=polib',
        '--collect-all=matplotlib',
        'main.py'
    ])
    
    # Platform-specific adjustments
    if platform_name == 'windows':
        # Windows-specific: use --noconsole instead of --windowed
        cmd[cmd.index('--windowed')] = '--noconsole'
    elif platform_name == 'macos':
        # macOS-specific: create .app bundle
        cmd.extend([
            '--osx-bundle-identifier=com.ogr.almacendigital',
        ])
    
    # Execute PyInstaller
    import subprocess
    result = subprocess.run(cmd, cwd=ROOT_DIR, check=False)
    
    if result.returncode == 0:
        print(f"\n[OK] {build_type.capitalize()} build successful for {platform_name}!")
        print(f"   Executable location: dist/")
        return True
    else:
        print(f"\n[ERROR] Build failed with code {result.returncode}")
        return False

def create_release_package(portable=False):
    """Create release package with documentation
    
    Args:
        portable: If True, creates portable package structure
    """
    platform_name = get_platform_name()
    build_type = "portable" if portable else "regular"
    print(f"\nCreating {build_type} release package for {platform_name}...")
    
    # Create release directory
    suffix = "-portable" if portable else ""
    release_dir = Path('release') / f"{platform_name}{suffix}"
    release_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable or portable folder
    dist_dir = Path('dist')
    
    if portable:
        # For portable builds, copy the entire folder
        portable_folder = dist_dir / 'AlmacenDigital'
        if portable_folder.exists():
            shutil.copytree(portable_folder, release_dir / 'AlmacenDigital', dirs_exist_ok=True)
            bundled_data = release_dir / 'AlmacenDigital' / '_internal' / 'data'
            if bundled_data.exists():
                shutil.rmtree(bundled_data)
            (release_dir / 'AlmacenDigital' / 'data').mkdir(exist_ok=True)
            print("   [OK] Copied AlmacenDigital folder (portable)")
            
            # Create launcher scripts for portable version
            create_portable_launcher(release_dir, platform_name)
    else:
        # For regular builds, copy single executable
        if platform_name == 'windows':
            exe_name = 'AlmacenDigital.exe'
        elif platform_name == 'macos':
            exe_name = 'AlmacenDigital.app'
        else:
            exe_name = 'AlmacenDigital'
        
        if (dist_dir / exe_name).exists():
            if platform_name == 'macos' and (dist_dir / exe_name).is_dir():
                # Copy entire .app bundle for macOS
                shutil.copytree(dist_dir / exe_name, release_dir / exe_name, dirs_exist_ok=True)
            else:
                shutil.copy2(dist_dir / exe_name, release_dir / exe_name)
            print(f"   [OK] Copied {exe_name}")
    
    # Copy documentation
    docs_to_copy = ['README.md', 'LICENSE']
    for doc in docs_to_copy:
        if Path(doc).exists():
            shutil.copy2(doc, release_dir / doc)
            print(f"   [OK] Copied {doc}")
    
    # Copy docs folder
    if Path('docs').exists():
        shutil.copytree('docs', release_dir / 'docs', dirs_exist_ok=True)
        print("   [OK] Copied docs/")
    
    # Create README for the release
    create_release_readme(release_dir, platform_name, portable)
    
    print(f"\n[OK] {build_type.capitalize()} release package created in: {release_dir}")
    return release_dir

def create_portable_launcher(release_dir, platform_name):
    """Create launcher scripts for portable version"""
    if platform_name == 'windows':
        # Create Windows batch launcher
        launcher_content = """@echo off
REM Almacén Digital Portable Launcher
cd /d "%~dp0"
start "" "AlmacenDigital\\AlmacenDigital.exe"
"""
        launcher_path = release_dir / 'Run_AlmacenDigital.bat'
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        print("   [OK] Created Run_AlmacenDigital.bat launcher")
    else:
        # Create Unix shell launcher
        launcher_content = """#!/bin/bash
# Almacén Digital Portable Launcher
cd "$(dirname "$0")"
./AlmacenDigital/AlmacenDigital
"""
        launcher_path = release_dir / 'Run_AlmacenDigital.sh'
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        # Make executable
        os.chmod(launcher_path, 0o755)
        print("   [OK] Created Run_AlmacenDigital.sh launcher")

def create_release_readme(release_dir, platform_name, portable=False):
    """Create platform-specific README for release"""
    build_type = "PORTABLE" if portable else "REGULAR"
    readme_content = f"""# Almacén Digital - {platform_name.upper()} {build_type} Release

## Installation

"""
    
    if platform_name == 'windows':
        if portable:
            readme_content += """### Windows Portable
1. Extract the ZIP file to any location (USB drive, Desktop, etc.)
2. Double-click `Run_AlmacenDigital.bat` to launch the application
3. Alternatively, navigate to `AlmacenDigital` folder and run `AlmacenDigital.exe`
4. If Windows Defender SmartScreen appears, click "More info" and "Run anyway"
5. Grant administrator privileges when prompted (needed for S.M.A.R.T. drive health monitoring)

**Portable Features**:
- No installation required
- Run from any location including USB drives
- Settings and database stored in the application folder
- Move the entire folder to run on different computers

**Note**: The first run may take a few seconds to initialize the database.
"""
        else:
            readme_content += """### Windows
1. Extract the ZIP file to a folder of your choice
2. Double-click `AlmacenDigital.exe` to run
3. If Windows Defender SmartScreen appears, click "More info" and "Run anyway"
4. Grant administrator privileges when prompted (needed for S.M.A.R.T. drive health monitoring)

**Note**: The first run may take a few seconds to initialize the database.
"""
    elif platform_name == 'macos':
        if portable:
            readme_content += """### macOS Portable
1. Extract the archive to any location (USB drive, Desktop, etc.)
2. Run `./Run_AlmacenDigital.sh` or navigate to AlmacenDigital folder and open the app
3. If you see "AlmacenDigital cannot be opened because it is from an unidentified developer":
   - Right-click the app and select "Open"
   - Click "Open" in the dialog
4. Grant necessary permissions when prompted

**Portable Features**:
- No installation required
- Run from any location including external drives
- Settings and database stored in the application folder
- Move the entire folder to run on different Macs

**Note**: macOS may require granting disk access permissions in System Preferences > Security & Privacy.
"""
        else:
            readme_content += """### macOS
1. Open the DMG file
2. Drag `AlmacenDigital.app` to your Applications folder
3. If you see "AlmacenDigital cannot be opened because it is from an unidentified developer":
   - Right-click the app and select "Open"
   - Click "Open" in the dialog
4. Grant necessary permissions when prompted

**Note**: macOS may require granting disk access permissions in System Preferences > Security & Privacy.
"""
    else:
        if portable:
            readme_content += """### Linux Portable
1. Extract the archive to any location (USB drive, home folder, etc.)
2. Run: `./Run_AlmacenDigital.sh`
3. Alternatively: `cd AlmacenDigital && ./AlmacenDigital`
4. Grant necessary permissions when prompted

**Portable Features**:
- No installation required
- Run from any location including external drives
- Settings and database stored in the application folder
- Move the entire folder to run on different Linux systems

**Dependencies**: Most Linux distributions should have all required libraries. If you encounter issues, install:
- `sudo apt-get install libxcb-xinerama0` (Ubuntu/Debian)
- `sudo dnf install xcb-util-xinerama` (Fedora)
"""
        else:
            readme_content += """### Linux
1. Extract the archive to a folder of your choice
2. Make the file executable: `chmod +x AlmacenDigital`
3. Run: `./AlmacenDigital`
4. Grant necessary permissions when prompted

**Dependencies**: Most Linux distributions should have all required libraries. If you encounter issues, install:
- `sudo apt-get install libxcb-xinerama0` (Ubuntu/Debian)
- `sudo dnf install xcb-util-xinerama` (Fedora)
"""
    
    readme_content += """

## Quick Start

1. **Add a Drive**: Click "💾 Gestionar" → "Agregar Dispositivo"
2. **Search Files**: Use the "📦 Inventario" tab to search
3. **View Statistics**: Check "📊 Estadísticas" for visualizations

## Features

- 📦 **Smart Cataloging** - Index all files and folders from external drives
- 🔍 **Instant Search** - Find files across all drives in milliseconds
- 💾 **Offline Access** - Search your catalog even when drives are disconnected
- 📊 **Rich Visualizations** - Charts and diagrams for storage analysis
- 🔄 **Auto-Update** - Connection status updates every 10 seconds
- 📤 **Excel Export** - Export database to Excel format

## Documentation

Full documentation is available in the `docs/` folder:
- `GUIA_DESARROLLO.md` - Developer guide (Spanish)
- `GUIA_SINCRONIZACION.md` - Multi-device sync guide
- `DOC_ESTADISTICAS.md` - Statistics system documentation

## Support

- Issues: https://github.com/yourusername/hddinventory/issues
- Email: your.email@example.com

## License

Creative Commons Non-Commercial (CC BY-NC)

---
Built with ❤️ using Python and PyQt6
"""
    
    with open(release_dir / 'INSTALL.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("   [OK] Created INSTALL.txt")

def main():
    """Main build process"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Build Almacén Digital executable')
    parser.add_argument('--portable', action='store_true', 
                       help='Create portable build (folder) instead of single executable')
    args = parser.parse_args()
    
    build_type = "Portable" if args.portable else "Regular"
    
    print("=" * 60)
    print(f"  Almacén Digital - Build System ({build_type})")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("\n[ERROR] PyInstaller not found.")
        print("Install it with: python -m pip install -r requirements.txt")
        sys.exit(1)
    
    # Clean previous builds
    clean_build()
    
    # Build executable
    if not build_executable(portable=args.portable):
        sys.exit(1)
    
    # Create release package
    release_dir = create_release_package(portable=args.portable)
    
    print("\n" + "=" * 60)
    print(f"  {build_type} Build Complete!")
    print("=" * 60)
    print(f"\nRelease package: {release_dir}")
    
    if args.portable:
        print("\nPortable build created!")
        print("   - Can run from USB drives or any folder")
        print("   - Settings stored in app folder")
        print("   - Use the launcher script for easy execution")
    
    print("\nYou can now distribute the contents of the release folder!")
    
if __name__ == '__main__':
    main()
