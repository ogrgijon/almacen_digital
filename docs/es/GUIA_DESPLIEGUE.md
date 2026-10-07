# Construyendo Almacén Digital para Distribución

Esta guía explica cómo construir ejecutables independientes para Windows, macOS y Linux.

## Prerrequisitos

### Todas las Plataformas
- Python 3.9 o superior
- Todas las dependencias instaladas (`pip install -r requirements.txt`)
- PyInstaller se instalará automáticamente por el script de construcción

### Windows
- Windows 10 o superior
- Visual C++ Redistributable (generalmente preinstalado)

### macOS
- macOS 10.13 (High Sierra) o superior
- Herramientas de Línea de Comandos de Xcode: `xcode-select --install`

### Linux
- La mayoría de distribuciones modernas (Ubuntu 20.04+, Fedora 33+, etc.)
- Herramientas de desarrollo: `sudo apt-get install build-essential` (Ubuntu/Debian)

## Construcción Rápida

### Windows
```cmd
# Construcción regular (ejecutable único)
scripts\build.bat

# Construcción portable (carpeta con todos los archivos)
scripts\build.bat --portable
```

### macOS / Linux
```bash
chmod +x scripts/build.sh

# Construcción regular (ejecutable único)
./scripts/build.sh

# Construcción portable (carpeta con todos los archivos)
./scripts/build.sh --portable
```

## Tipos de Construcción

### Construcción Regular
- Archivo ejecutable único
- Tamaño de descarga menor (~100-150MB)
- Inicio ligeramente más lento (descomprime en carpeta temporal)
- Configuraciones almacenadas en perfil de usuario
- **Mejor para**: Instalación estándar en una sola computadora

### Construcción Portable
- Carpeta con ejecutable y todas las dependencias
- Tamaño de descarga mayor (~200-300MB)
- Inicio más rápido (no requiere descompresión)
- Configuraciones almacenadas en carpeta de aplicación
- Puede ejecutarse desde unidades USB o cualquier ubicación
- **Mejor para**: Ejecutar en múltiples computadoras, unidades USB o sistemas sin derechos de administrador

## Qué Hace el Proceso de Construcción

1. **Limpia** artefactos de construcción anteriores
2. **Instala** PyInstaller si no está presente
3. **Construye** un ejecutable independiente usando PyInstaller
4. **Empaqueta** el ejecutable con documentación
5. **Crea** carpeta de release específica para cada plataforma en `release/`

## Salida de Construcción

Después de construir, encontrarás:

### Construcción Regular
```
release/
├── windows/          # Construcción Windows
│   ├── AlmacenDigital.exe
│   ├── README.md
│   ├── LICENSE
│   ├── INSTALL.txt
│   └── docs/
├── macos/           # Construcción macOS
│   ├── AlmacenDigital.app
│   ├── README.md
│   ├── LICENSE
│   ├── INSTALL.txt
│   └── docs/
└── linux/           # Construcción Linux
    ├── AlmacenDigital
    ├── README.md
    ├── LICENSE
    ├── INSTALL.txt
    └── docs/
```

### Construcción Portable
```
release/
├── windows-portable/
│   ├── AlmacenDigital/          # Carpeta con ejecutable y dependencias
│   │   ├── AlmacenDigital.exe
│   │   ├── _internal/           # Todas las dependencias
│   │   └── ...
│   ├── Run_AlmacenDigital.bat  # Script lanzador
│   ├── README.md
│   ├── LICENSE
│   ├── INSTALL.txt
│   └── docs/
├── macos-portable/
│   ├── AlmacenDigital/
│   ├── Run_AlmacenDigital.sh
│   └── ...
└── linux-portable/
    ├── AlmacenDigital/
    ├── Run_AlmacenDigital.sh
    └── ...
```

## Distribución

### Windows

**Construcción Regular:**
1. Comprimir la carpeta `release/windows/` en un archivo ZIP
2. Los usuarios pueden extraer y ejecutar `AlmacenDigital.exe`
3. Opcional: Crear un instalador usando [Inno Setup](https://jrsoftware.org/isinfo.php)

**Construcción Portable:**
1. Comprimir la carpeta `release/windows-portable/` en un archivo ZIP llamado `AlmacenDigital-Portable-Windows.zip`
2. Los usuarios pueden extraer en unidad USB o cualquier carpeta
3. Ejecutar vía `Run_AlmacenDigital.bat` o directamente desde `AlmacenDigital/AlmacenDigital.exe`
4. Base de datos y configuraciones almacenadas en carpeta de aplicación (completamente portable)

### macOS

**Construcción Regular:**
1. Crear un archivo DMG:
   ```bash
   hdiutil create -volname "AlmacenDigital" -srcfolder release/macos/ -ov -format UDZO AlmacenDigital.dmg
   ```
2. Los usuarios pueden abrir el DMG y arrastrar la aplicación a Aplicaciones

**Construcción Portable:**
1. Comprimir la carpeta `release/macos-portable/` en un archivo ZIP
2. Los usuarios pueden extraer en cualquier ubicación
3. Usar el script `Run_AlmacenDigital.sh` para lanzar

### Linux

**Construcción Regular:**
1. Comprimir la carpeta `release/linux/` en un tar.gz:
   ```bash
   cd release
   tar -czf AlmacenDigital-linux.tar.gz linux/
   ```
2. Opcional: Crear un paquete .deb o .rpm para instalación más fácil

**Construcción Portable:**
1. Comprimir la carpeta `release/linux-portable/`:
   ```bash
   cd release
   tar -czf AlmacenDigital-Portable-Linux.tar.gz linux-portable/
   ```
2. Los usuarios pueden extraer en cualquier ubicación incluyendo unidades USB
3. Usar el lanzador `Run_AlmacenDigital.sh`

## Comparación: Portable vs Regular

**Cuándo usar Portable:**
- Ejecutar desde unidades USB o almacenamiento externo
- Necesidad de usar en múltiples computadoras
- Deseo de que configuraciones/base de datos viajen con la aplicación
- No tener derechos de administrador para instalación
- Deseo de tiempos de inicio más rápidos

**Cuándo usar Regular:**
- Instalar en una sola computadora
- Deseo de tamaño de descarga menor
- Instalación estándar en Archivos de Programa
- Configuraciones almacenadas en perfil de usuario

## Configuración Personalizada de Construcción

Puedes modificar `build.py` para personalizar la construcción:

- **Ícono**: Cambiar `--icon=icon.ico` para usar un ícono diferente
- **Nombre**: Modificar `--name=AlmacenDigital` para cambiar el nombre del ejecutable
- **Archivos adicionales**: Agregar más entradas `--add-data` para recursos extra
- **Importaciones ocultas**: Agregar `--hidden-import` para módulos que PyInstaller no detecte
- **Tipo de construcción**: Usar flag `--portable` para construcción portable

### Construcción Manual con PyInstaller

Si necesitas más control, puedes ejecutar PyInstaller directamente:

**Construcción regular (archivo único):**
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

**Construcción portable (carpeta):**
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

### Creando un Archivo Spec

Para construcciones más complejas, crea un archivo `.spec`:

```bash
pyi-makespec --onefile --windowed main.py
```

Edita el archivo `main.spec` generado, luego construye con:

```bash
pyinstaller main.spec
```

## Solución de Problemas

### Windows: "La aplicación no pudo iniciarse"
- Instalar Visual C++ Redistributable
- Ejecutar como administrador
- Verificar configuraciones de antivirus (puede necesitar lista blanca)

### macOS: "La aplicación no puede abrirse"
- Clic derecho → Abrir (solo la primera vez)
- Otorgar permisos en Preferencias del Sistema → Seguridad y Privacidad
- Firma de código: `codesign --force --deep --sign - AlmacenDigital.app`

### Linux: Bibliotecas faltantes
```bash
# Ubuntu/Debian
sudo apt-get install libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0

# Fedora/CentOS
sudo dnf install xcb-util-wm xcb-util-image xcb-util-keysyms xcb-util-renderutil
```

### Advertencias de PyInstaller durante la construcción
- Revisar las importaciones ocultas faltantes
- Agregar módulos problemáticos a `--hidden-import`
- Usar `--collect-all` para paquetes complejos como matplotlib

## Optimización de Tamaño

La construcción por defecto crea un ejecutable de ~100-150MB. Para reducir el tamaño:

1. **Usar modo onedir para mejor inicio** (ya usa onedir en portable):
   ```bash
   pyinstaller --onedir main.py
   ```

2. **Excluir paquetes innecesarios**:
   ```bash
   --exclude-module tkinter --exclude-module IPython --exclude-module pytest
   ```

3. **Usar compresión UPX** (reduce ~30%):
   ```bash
   pyinstaller --upx-dir=/path/to/upx main.py
   ```

**Nota**: Las construcciones regulares (--onefile) son más pequeñas pero más lentas al iniciar. Las construcciones portables (--onedir) son más grandes pero inician más rápido y son verdaderamente portables.

## Firma de Código

### Windows (Opcional)
```cmd
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com AlmacenDigital.exe
```

### macOS (Recomendado)
```bash
codesign --force --deep --sign "Developer ID Application: Tu Nombre" AlmacenDigital.app
```

### Notarización (macOS)
Requerido para Catalina+ para evitar advertencias de Gatekeeper:
```bash
xcrun altool --notarize-app --primary-bundle-id com.ogr.almacendigital \
    --username "tu-apple-id@example.com" \
    --password "contraseña-específica-de-app" \
    --file AlmacenDigital.dmg
```

## Construcciones Automatizadas (CI/CD)

### Ejemplo de GitHub Actions

Crear `.github/workflows/build.yml`:

```yaml
name: Construir

on: [push, pull_request]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]

    steps:
    - uses: actions/checkout@v2

    - name: Configurar Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Instalar dependencias
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller

    - name: Construir
      run: python build.py

    - name: Subir artefactos
      uses: actions/upload-artifact@v2
      with:
        name: ${{ matrix.os }}-build
        path: release/
```

## Probando la Construcción

Antes de distribuir, probar el ejecutable:

1. **Entorno limpio**: Probar en una máquina sin Python instalado
2. **Diferentes versiones de OS**: Probar en versiones antiguas y nuevas del sistema operativo
3. **Permisos**: Probar con y sin privilegios de administrador
4. **Red**: Probar con y sin conexión a internet
5. **Antivirus**: Verificar si el software antivirus principal lo marca

## Soporte

Para problemas de construcción:
1. Revisar documentación de PyInstaller: https://pyinstaller.readthedocs.io/
2. Revisar advertencias y errores de construcción
3. Probar en un entorno Python limpio
4. Reportar problemas con logs de error completos

---

**¡Feliz Construcción!** 🚀
