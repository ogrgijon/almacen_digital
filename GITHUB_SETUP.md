# GitHub Repository Preparation Guide / Guía de Preparación del Repositorio GitHub

> **🇪🇸 [Versión en Español](#español) | 🇺🇸 [English Version](#english)**

---

## English

This document contains important instructions for preparing your repository for public release on GitHub.

### Before First Commit

#### 1. Review and Clean

- [x] Review all code for sensitive information (passwords, API keys, personal data)
- [x] Update .gitignore to exclude build artifacts and sensitive files
- [x] Remove or clean any test data with personal information
- [x] Verify all documentation is up to date

#### 2. Check These Files

**Must Review:**
- [ ] `config.py` - No hardcoded paths or sensitive data
- [ ] `data/settings.json` - Already in .gitignore, but verify
- [ ] `utils/helpers.py` - Check for hardcoded paths (lines 215-216 have Windows paths for smartctl - these are OK as they're standard locations)
- [ ] `scripts/populate_dummy_data.py` - Has example paths (C:\, D:\) - these are fine as dummy data

**Already Protected by .gitignore:**
- `data/` folder (database, logs, settings)
- `build/` folder (build artifacts)
- `release/` folder (compiled binaries)
- `__pycache__/` folders
- `.venv/` virtual environment

#### 3. Initialize Git Repository

```bash
# Navigate to project directory
cd c:\DOCS\PROYECTOS\ALMACEN_DIGITAL

# Initialize git (if not already done)
git init

# Add all files (respecting .gitignore)
git add .

# Initial commit
git commit -m "Initial commit: Almacén Digital v1.1.0"
```

#### 4. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `almacen_digital`
3. Description: "Desktop application to catalog and search files across multiple external hard drives - Aplicación de escritorio para catalogar y buscar archivos en múltiples discos duros externos"
4. Choose: **Public**
5. Do NOT initialize with README (we already have one)
6. Do NOT add .gitignore (we already have one)
7. Do NOT add license (we already have one)
8. Click "Create repository"

#### 5. Push to GitHub

```bash
# Add remote repository
git remote add origin https://github.com/ogrgijon/almacen_digital.git

# Push to GitHub
git branch -M main
git push -u origin main
```

#### 6. Configure Repository Settings

**About Section:**
- Description: "🗂️ Desktop application to catalog and search files across multiple external drives | Aplicación para catalogar archivos en discos externos"
- Website: Leave empty or add your LinkedIn
- Topics: `python`, `pyqt6`, `desktop-app`, `file-catalog`, `disk-management`, `sqlite`, `hdd-inventory`, `external-drives`, `file-search`, `bilingual`

**Features to Enable:**
- ✅ Issues
- ✅ Discussions (optional, for community)
- ✅ Preserve this repository (optional)

**Security:**
- Go to Settings → Security → Enable security advisories
- Enable Dependabot alerts

#### 7. Create First Release

1. Go to Releases → "Create a new release"
2. Tag: `v1.1.0`
3. Title: `Almacén Digital v1.1.0`
4. Description: Copy from CHANGELOG.md
5. Attach binaries (if you have compiled versions)
6. Mark as "Latest release"
7. Publish

#### 8. Add Repository Badges

The README already includes these badges:
- Python version
- PyQt6 version
- Documentation status
- Production ready status
- License

#### 9. Set Up GitHub Actions (Optional)

Consider adding CI/CD workflows for:
- Automated testing
- Code quality checks
- Automated builds
- Release automation

### Post-Release Checklist

- [ ] Verify all links in README work correctly
- [ ] Test clone and installation from fresh directory
- [ ] Check that documentation renders correctly on GitHub
- [ ] Verify images display correctly (splash.png, screenshots)
- [ ] Test installation scripts on clean environment
- [ ] Share repository link on social media/LinkedIn

### Files Already Cleaned/Created

✅ `.gitignore` - Comprehensive ignore rules
✅ `LICENSE` - Moved to root, CC BY-NC 4.0
✅ `README.md` - Bilingual, comprehensive
✅ `CONTRIBUTING.md` - Contribution guidelines
✅ `CODE_OF_CONDUCT.md` - Community standards
✅ `CHANGELOG.md` - Version history
✅ `SECURITY.md` - Security policy
✅ `AUTHORS.md` - Credits and attribution
✅ `DISCLAIMER.md` - Legal disclaimers
✅ `install.bat` / `install.sh` - Installation scripts
✅ `data/.gitkeep` - Track directory structure

### Notes

**Build and Release Folders:**
- These folders are already in .gitignore
- They will not be committed to the repository
- Users will download releases from GitHub Releases page
- Keep these folders locally for building releases

**Data Folder:**
- Tracked as empty directory via .gitkeep
- All contents ignored (.db, .json, .log files)
- Users will generate their own data

---

## Español

Este documento contiene instrucciones importantes para preparar tu repositorio para lanzamiento público en GitHub.

### Antes del Primer Commit

#### 1. Revisar y Limpiar

- [x] Revisar todo el código para información sensible (contraseñas, claves API, datos personales)
- [x] Actualizar .gitignore para excluir artefactos de construcción y archivos sensibles
- [x] Remover o limpiar datos de prueba con información personal
- [x] Verificar que toda la documentación esté actualizada

#### 2. Verificar Estos Archivos

**Debe Revisar:**
- [ ] `config.py` - Sin rutas hardcoded o datos sensibles
- [ ] `data/settings.json` - Ya en .gitignore, pero verificar
- [ ] `utils/helpers.py` - Verificar rutas hardcoded (líneas 215-216 tienen rutas de Windows para smartctl - están bien, son ubicaciones estándar)
- [ ] `scripts/populate_dummy_data.py` - Tiene rutas de ejemplo (C:\, D:\) - están bien como datos de ejemplo

**Ya Protegidos por .gitignore:**
- Carpeta `data/` (base de datos, logs, configuración)
- Carpeta `build/` (artefactos de construcción)
- Carpeta `release/` (binarios compilados)
- Carpetas `__pycache__/`
- Entorno virtual `.venv/`

#### 3. Inicializar Repositorio Git

```bash
# Navegar al directorio del proyecto
cd c:\DOCS\PROYECTOS\ALMACEN_DIGITAL

# Inicializar git (si no está hecho)
git init

# Añadir todos los archivos (respetando .gitignore)
git add .

# Commit inicial
git commit -m "Initial commit: Almacén Digital v1.1.0"
```

#### 4. Crear Repositorio GitHub

1. Ir a https://github.com/new
2. Nombre del repositorio: `almacen_digital`
3. Descripción: "Desktop application to catalog and search files across multiple external hard drives - Aplicación de escritorio para catalogar y buscar archivos en múltiples discos duros externos"
4. Elegir: **Public**
5. NO inicializar con README (ya tenemos uno)
6. NO añadir .gitignore (ya tenemos uno)
7. NO añadir licencia (ya tenemos una)
8. Click "Create repository"

#### 5. Push a GitHub

```bash
# Añadir repositorio remoto
git remote add origin https://github.com/ogrgijon/almacen_digital.git

# Push a GitHub
git branch -M main
git push -u origin main
```

#### 6. Configurar Ajustes del Repositorio

**Sección About:**
- Descripción: "🗂️ Desktop application to catalog and search files across multiple external drives | Aplicación para catalogar archivos en discos externos"
- Sitio web: Dejar vacío o añadir tu LinkedIn
- Topics: `python`, `pyqt6`, `desktop-app`, `file-catalog`, `disk-management`, `sqlite`, `hdd-inventory`, `external-drives`, `file-search`, `bilingual`

**Funcionalidades a Habilitar:**
- ✅ Issues
- ✅ Discussions (opcional, para comunidad)
- ✅ Preserve this repository (opcional)

**Seguridad:**
- Ir a Settings → Security → Habilitar security advisories
- Habilitar alertas de Dependabot

#### 7. Crear Primer Release

1. Ir a Releases → "Create a new release"
2. Tag: `v1.1.0`
3. Título: `Almacén Digital v1.1.0`
4. Descripción: Copiar de CHANGELOG.md
5. Adjuntar binarios (si tienes versiones compiladas)
6. Marcar como "Latest release"
7. Publicar

#### 8. Añadir Badges del Repositorio

El README ya incluye estos badges:
- Versión de Python
- Versión de PyQt6
- Estado de documentación
- Estado de producción
- Licencia

#### 9. Configurar GitHub Actions (Opcional)

Considerar añadir workflows CI/CD para:
- Testing automatizado
- Verificaciones de calidad de código
- Construcciones automatizadas
- Automatización de releases

### Checklist Post-Lanzamiento

- [ ] Verificar que todos los enlaces en README funcionen correctamente
- [ ] Probar clone e instalación desde directorio limpio
- [ ] Verificar que la documentación se renderice correctamente en GitHub
- [ ] Verificar que las imágenes se muestren correctamente (splash.png, screenshots)
- [ ] Probar scripts de instalación en entorno limpio
- [ ] Compartir enlace del repositorio en redes sociales/LinkedIn

### Archivos Ya Limpiados/Creados

✅ `.gitignore` - Reglas completas de ignorar
✅ `LICENSE` - Movido a raíz, CC BY-NC 4.0
✅ `README.md` - Bilingüe, completo
✅ `CONTRIBUTING.md` - Pautas de contribución
✅ `CODE_OF_CONDUCT.md` - Estándares de comunidad
✅ `CHANGELOG.md` - Historial de versiones
✅ `SECURITY.md` - Política de seguridad
✅ `AUTHORS.md` - Créditos y atribución
✅ `DISCLAIMER.md` - Descargos legales
✅ `install.bat` / `install.sh` - Scripts de instalación
✅ `data/.gitkeep` - Rastrear estructura de directorios

### Notas

**Carpetas Build y Release:**
- Estas carpetas ya están en .gitignore
- No se commitearán al repositorio
- Los usuarios descargarán releases desde la página de GitHub Releases
- Mantén estas carpetas localmente para construir releases

**Carpeta Data:**
- Rastreada como directorio vacío vía .gitkeep
- Todo el contenido ignorado (archivos .db, .json, .log)
- Los usuarios generarán sus propios datos

---

**Ready to publish! / ¡Listo para publicar!**
