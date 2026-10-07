# Changelog / Registro de Cambios

> **🇪🇸 [Versión en Español](#español) | 🇺🇸 [English Version](#english)**

All notable changes to Almacén Digital will be documented in this file.

Todos los cambios notables en Almacén Digital se documentarán en este archivo.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto sigue [Semantic Versioning](https://semver.org/lang/es/).

---

## English

## [Unreleased]

### Added
- Bilingual README (English/Spanish)
- CODE_OF_CONDUCT.md for community guidelines
- CONTRIBUTING.md with contribution guidelines
- Comprehensive .gitignore for better repository hygiene
- data/.gitkeep to track directory structure
- CHANGELOG.md for version tracking

### Changed
- Improved documentation structure
- Enhanced LICENSE visibility (moved to root)
- Updated repository links for public release

## [1.1.0] - 2026-01-12

### Added
- Modular architecture with app/core/ui separation
- Real-time connection status indicators (blue/gray circles)
- Auto-refresh connection status every 10 seconds
- Background workers for non-blocking operations
- Comprehensive bilingual documentation (900+ lines)
  - Developer Guide (DEVELOPMENT_GUIDE.md / GUIA_DESARROLLO.md)
  - Synchronization Guide (SYNCHRONIZATION_GUIDE.md / GUIA_SINCRONIZACION.md)
  - Statistics Documentation (STATISTICS_PANEL_GUIDE.md / GUIA_PANEL_ESTADISTICAS.md)
  - Building Guide (BUILDING_GUIDE.md / GUIA_DESPLIEGUE.md)
  - I18N Guide (I18N_GUIDE.md / GUIA_I18n.md)
- Internationalization system with Spanish translations
- Excel export with background processing and progress tracking
- Settings dialog with comprehensive configuration options
- Portable build option for USB/travel use
- Launcher scripts for portable versions
- Dummy data population script for testing

### Changed
- Refactored large files into focused modules (<300 lines average)
- Improved code organization and maintainability
- Enhanced performance for statistics loading
- Optimized search with pagination support
- Better error handling and user feedback
- Updated UI with modern dark theme

### Fixed
- Memory leaks in long-running sessions
- UI freezing during large file operations
- Database locking issues
- S.M.A.R.T. monitoring stability
- Connection status detection reliability

## [1.0.0] - 2025-12-01

### Added
- Initial release
- File cataloging and indexing system
- Fast search across multiple drives
- Drive management interface
- Basic statistics and visualizations
- SQLite database backend
- PyQt6 dark theme UI
- S.M.A.R.T. drive health monitoring
- Multi-device sync capability
- Excel export functionality

### Features
- Catalog external drives and storage devices
- Search files even when drives are disconnected
- Filter by file type, size, date
- View drive statistics and health
- Export catalog to Excel
- Sync database across multiple computers

---

## Español

## [No Publicado]

### Añadido
- README bilingüe (Inglés/Español)
- CODE_OF_CONDUCT.md para pautas de la comunidad
- CONTRIBUTING.md con pautas de contribución
- .gitignore completo para mejor higiene del repositorio
- data/.gitkeep para rastrear estructura de directorios
- CHANGELOG.md para seguimiento de versiones

### Cambiado
- Estructura de documentación mejorada
- Visibilidad mejorada de LICENSE (movido a raíz)
- Enlaces del repositorio actualizados para lanzamiento público

## [1.1.0] - 2026-01-12

### Añadido
- Arquitectura modular con separación app/core/ui
- Indicadores de estado de conexión en tiempo real (círculos azul/gris)
- Auto-actualización de estado de conexión cada 10 segundos
- Workers en segundo plano para operaciones no bloqueantes
- Documentación bilingüe completa (900+ líneas)
  - Guía de Desarrollo (DEVELOPMENT_GUIDE.md / GUIA_DESARROLLO.md)
  - Guía de Sincronización (SYNCHRONIZATION_GUIDE.md / GUIA_SINCRONIZACION.md)
  - Documentación de Estadísticas (STATISTICS_PANEL_GUIDE.md / GUIA_PANEL_ESTADISTICAS.md)
  - Guía de Construcción (BUILDING_GUIDE.md / GUIA_DESPLIEGUE.md)
  - Guía I18N (I18N_GUIDE.md / GUIA_I18n.md)
- Sistema de internacionalización con traducciones al español
- Exportación Excel con procesamiento en segundo plano y seguimiento de progreso
- Diálogo de configuración con opciones completas
- Opción de construcción portable para uso en USB/viajes
- Scripts de lanzamiento para versiones portables
- Script de población de datos de ejemplo para pruebas

### Cambiado
- Refactorización de archivos grandes en módulos enfocados (<300 líneas promedio)
- Organización de código y mantenibilidad mejoradas
- Rendimiento mejorado para carga de estadísticas
- Búsqueda optimizada con soporte de paginación
- Mejor manejo de errores y retroalimentación al usuario
- UI actualizada con tema oscuro moderno

### Corregido
- Fugas de memoria en sesiones de larga duración
- Congelamiento de UI durante operaciones con archivos grandes
- Problemas de bloqueo de base de datos
- Estabilidad de monitoreo S.M.A.R.T.
- Confiabilidad de detección de estado de conexión

## [1.0.0] - 2025-12-01

### Añadido
- Lanzamiento inicial
- Sistema de catalogación e indexación de archivos
- Búsqueda rápida a través de múltiples discos
- Interfaz de gestión de discos
- Estadísticas y visualizaciones básicas
- Backend de base de datos SQLite
- UI con tema oscuro PyQt6
- Monitoreo de salud de disco S.M.A.R.T.
- Capacidad de sincronización multi-dispositivo
- Funcionalidad de exportación Excel

### Funcionalidades
- Catalogar discos externos y dispositivos de almacenamiento
- Buscar archivos incluso cuando los discos están desconectados
- Filtrar por tipo de archivo, tamaño, fecha
- Ver estadísticas y salud de discos
- Exportar catálogo a Excel
- Sincronizar base de datos entre múltiples computadoras

---

## Version Guidelines / Pautas de Versión

### Version Format / Formato de Versión: MAJOR.MINOR.PATCH

- **MAJOR**: Incompatible API changes or major rewrites / Cambios incompatibles de API o reescrituras mayores
- **MINOR**: New features in a backwards-compatible manner / Nuevas funcionalidades de manera compatible
- **PATCH**: Backwards-compatible bug fixes / Correcciones de errores compatibles

### Categories / Categorías

- **Added / Añadido**: New features / Nuevas funcionalidades
- **Changed / Cambiado**: Changes in existing functionality / Cambios en funcionalidad existente
- **Deprecated / Obsoleto**: Soon-to-be removed features / Funcionalidades que pronto se eliminarán
- **Removed / Eliminado**: Removed features / Funcionalidades eliminadas
- **Fixed / Corregido**: Bug fixes / Correcciones de errores
- **Security / Seguridad**: Security vulnerability fixes / Correcciones de vulnerabilidades de seguridad

---

[Unreleased]: https://github.com/ogrgijon/almacen_digital/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/ogrgijon/almacen_digital/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/ogrgijon/almacen_digital/releases/tag/v1.0.0
