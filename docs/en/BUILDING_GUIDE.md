# Building Almacén Digital for Distribution

This guide explains how to build standalone executables for Windows, macOS, and Linux.

## Prerequisites

### All Platforms
- Python 3.9 or higher
- All dependencies installed (`pip install -r requirements.txt`)
- PyInstaller must be installed before building (`python -m pip install -r requirements.txt`)

### Windows
- Windows 10 or higher
- Visual C++ Redistributable (usually pre-installed)

### macOS
- macOS 10.13 (High Sierra) or higher
- Xcode Command Line Tools: `xcode-select --install`

### Linux
- Most modern distributions (Ubuntu 20.04+, Fedora 33+, etc.)
- Development tools: `sudo apt-get install build-essential` (Ubuntu/Debian)

## Quick Build

### Windows
```cmd
# Regular build (single executable)
scripts\build.bat

# Portable build (folder with all files)
scripts\build.bat --portable
```

### macOS / Linux
```bash
chmod +x scripts/build.sh

# Regular build (single executable)
./scripts/build.sh

# Portable build (folder with all files)
./scripts/build.sh --portable
```

## Build Types

### Regular Build
- Single executable file
- Smaller download size (~100-150MB)
- Slightly slower startup (unpacks to temp folder)
- Settings stored in user profile
- **Best for**: Standard installation on a single computer

### Portable Build
- Folder with executable and all dependencies
- Larger download size (~200-300MB)
- Faster startup (no unpacking needed)
- Settings stored in application folder
- Can run from USB drives or any location
- **Best for**: Running on multiple computers, USB drives, or systems without admin rights

## What the Build Process Does

1. **Cleans** previous build artifacts
2. **Builds** a standalone executable using PyInstaller
3. **Packages** the executable
4. **Creates** platform-specific release folder in `release/`

The build never bundles the developer's `data/` directory. The packaged application
creates a clean `data/` directory beside the executable on first launch, so local
databases, settings, and logs are not accidentally published.

## Build Output

After building, you'll find:

### Regular Build
```
release/
├── windows/          # Windows build
│   ├── AlmacenDigital.exe
│   ├── README.md
│   ├── LICENSE
│   ├── INSTALL.txt
│   └── docs/
├── macos/           # macOS build
│   ├── AlmacenDigital.app
│   ├── README.md
│   ├── LICENSE
│   ├── INSTALL.txt
│   └── docs/
└── linux/           # Linux build
    ├── AlmacenDigital
    ├── README.md
    ├── LICENSE
    ├── INSTALL.txt
    └── docs/
```

### Portable Build
```
release/
├── windows-portable/
│   └── AlmacenDigital/          # Only the portable application and dependencies
│   │   ├── AlmacenDigital.exe
│   │   ├── _internal/           # All dependencies
│   │   └── ...
├── macos-portable/
│   ├── AlmacenDigital/
│   ├── Run_AlmacenDigital.sh
│   └── ...
└── linux-portable/
    ├── AlmacenDigital/
    ├── Run_AlmacenDigital.sh
    └── ...
```

## Distribution

### Windows

**Regular Build:**
1. Compress the `release/windows/` folder to a ZIP file
2. Users can extract and run `AlmacenDigital.exe`
3. Optional: Create an installer using [Inno Setup](https://jrsoftware.org/isinfo.php)

**Portable Build:**
1. Compress only the `release/windows-portable/AlmacenDigital/` folder to a ZIP file named `AlmacenDigital-Portable-Windows.zip`
2. Users can extract to USB drive or any folder
3. Run `AlmacenDigital/AlmacenDigital.exe`
4. Database and settings are stored in the app folder (fully portable)

### macOS

**Regular Build:**
1. Create a DMG file:
   ```bash
   hdiutil create -volname "AlmacenDigital" -srcfolder release/macos/ -ov -format UDZO AlmacenDigital.dmg
   ```
2. Users can open the DMG and drag the app to Applications

**Portable Build:**
1. Compress the `release/macos-portable/` folder to a ZIP file
2. Users can extract to any location
3. Use the `Run_AlmacenDigital.sh` script to launch

### Linux

**Regular Build:**
1. Compress the `release/linux/` folder to a tar.gz:
   ```bash
   cd release
   tar -czf AlmacenDigital-linux.tar.gz linux/
   ```
2. Optional: Create a .deb or .rpm package for easier installation

**Portable Build:**
1. Compress the `release/linux-portable/` folder:
   ```bash
   cd release
   tar -czf AlmacenDigital-Portable-Linux.tar.gz linux-portable/
   ```
2. Users can extract to any location including USB drives
3. Use the `Run_AlmacenDigital.sh` launcher

## Comparison: Portable vs Regular

**When to use Portable:**
- Running from USB drives or external storage
- Need to use on multiple computers
- Want settings/database to travel with the app
- Don't have admin rights for installation
- Want faster startup times

**When to use Regular:**
- Installing on a single computer
- Want smaller download size
- Standard installation in Program Files
- Settings stored in user profile

## Custom Build Configuration

You can modify `build.py` to customize the build:

- **Icon**: Change `--icon=icon.ico` to use a different icon
- **Name**: Modify `--name=AlmacenDigital` to change the executable name
- **Additional files**: Add more `--add-data` entries for extra resources
- **Hidden imports**: Add `--hidden-import` for modules that PyInstaller misses
- **Build type**: Use `--portable` flag for portable build

### Manual PyInstaller Build

If you need more control, you can run PyInstaller directly:

**Regular build (single file):**
```bash
pyinstaller --name=AlmacenDigital \
    --windowed \
    --onefile \
    --icon=icon.ico \
    --add-data=locales:locales \
    --add-data=splash.png:. \
    --add-data=icon.ico:. \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtGui \
    --hidden-import=PyQt6.QtWidgets \
    --hidden-import=PyQt6.QtCharts \
    --collect-all=matplotlib \
    main.py
```

**Portable build (folder):**
```bash
pyinstaller --name=AlmacenDigital \
    --windowed \
    --onedir \
    --icon=icon.ico \
    --add-data=locales:locales \
    --add-data=splash.png:. \
    --add-data=icon.ico:. \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtGui \
    --hidden-import=PyQt6.QtWidgets \
    --hidden-import=PyQt6.QtCharts \
    --collect-all=matplotlib \
    main.py
```

### Creating a Spec File

For more complex builds, create a `.spec` file:

```bash
pyi-makespec --onefile --windowed main.py
```

Edit the generated `main.spec` file, then build with:

```bash
pyinstaller main.spec
```

## Troubleshooting

### Windows: "Application failed to start"
- Install Visual C++ Redistributable
- Run as administrator
- Check antivirus settings (may need to whitelist)

### macOS: "App cannot be opened"
- Right-click → Open (first time only)
- Grant permissions in System Preferences → Security & Privacy
- Code signing: `codesign --force --deep --sign - AlmacenDigital.app`

### Linux: Missing libraries
```bash
# Ubuntu/Debian
sudo apt-get install libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0

# Fedora/CentOS
sudo dnf install xcb-util-wm xcb-util-image xcb-util-keysyms xcb-util-renderutil
```

### PyInstaller warnings during build
- Review missing hidden imports
- Add problematic modules to `--hidden-import`
- Use `--collect-all` for complex packages like matplotlib

## Size Optimization

The default build creates a ~100-150MB executable. To reduce size:

1. **Use onedir mode for better startup** (already uses onedir in portable):
   ```bash
   pyinstaller --onedir main.py
   ```

2. **Exclude unnecessary packages**:
   ```bash
   --exclude-module tkinter --exclude-module IPython --exclude-module pytest
   ```

3. **Use UPX compression** (reduces ~30%):
   ```bash
   pyinstaller --upx-dir=/path/to/upx main.py
   ```

**Note**: Regular builds (--onefile) are smaller but slower to start. Portable builds (--onedir) are larger but start faster and are truly portable.

## Code Signing

### Windows (Optional)
```cmd
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com AlmacenDigital.exe
```

### macOS (Recommended)
```bash
codesign --force --deep --sign "Developer ID Application: Your Name" AlmacenDigital.app
```

### Notarization (macOS)
Required for Catalina+ to avoid Gatekeeper warnings:
```bash
xcrun altool --notarize-app --primary-bundle-id com.ogr.almacendigital \
    --username "your-apple-id@example.com" \
    --password "app-specific-password" \
    --file AlmacenDigital.dmg
```

## Automated Builds (CI/CD)

### GitHub Actions Example

Create `.github/workflows/build.yml`:

```yaml
name: Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller

    - name: Build
      run: python build.py

    - name: Upload artifacts
      uses: actions/upload-artifact@v2
      with:
        name: ${{ matrix.os }}-build
        path: release/
```

## Testing the Build

Before distribution, test the executable:

1. **Clean environment**: Test on a machine without Python installed
2. **Different OS versions**: Test on older and newer OS versions
3. **Permissions**: Test with and without administrator privileges
4. **Network**: Test with and without internet connection
5. **Antivirus**: Check if major antivirus software flags it

## Support

For build issues:
1. Check PyInstaller documentation: https://pyinstaller.readthedocs.io/
2. Review build warnings and errors
3. Test in a clean Python environment
4. Report issues with full error logs

---

**Happy Building!** 🚀</content>
<parameter name="filePath">c:\DOCS\PROYECTOS\HDDINVENTORY\docs\en\BUILDING_GUIDE.md