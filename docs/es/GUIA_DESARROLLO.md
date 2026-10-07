# Guía de Desarrollo - Almacen Digital

## 📋 Información General

**Almacen Digital** es una aplicación de escritorio desarrollada en Python para catalogar y buscar archivos en múltiples discos duros externos. Utiliza una arquitectura modular con interfaz gráfica basada en PyQt6 y un sistema de base de datos SQLite para el almacenamiento persistente.

- **Versión**: 1.0.0
- **Fecha**: Enero 2026
- **Estado**: Producción
- **Licencia**: Creative Commons Non-Commercial (CC BY-NC)

## 🏗️ Arquitectura de la Aplicación

### Patrón Arquitectónico
La aplicación sigue una arquitectura **MVC (Model-View-Controller)** modificada con separación clara de responsabilidades:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   INTERFACE     │    │   CONTROLADOR   │    │     MODELO      │
│     (UI)        │◄──►│     (APP)       │◄──►│    (CORE)       │
│                 │    │                 │    │                 │
│ - main_window   │    │ - controller    │    │ - database      │
│ - sidebars      │    │ - handlers      │    │ - scanner       │
│ - views         │    │ - managers      │    │ - sync_manager  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Capas de la Arquitectura

#### 1. **Capa de Presentación (UI)**
- **Propósito**: Interfaz gráfica de usuario y experiencia visual
- **Framework**: PyQt6 con tema oscuro
- **Componentes**: Ventanas, paneles, barras laterales, vistas

#### 2. **Capa de Aplicación (APP)**
- **Propósito**: Coordinación entre UI y lógica de negocio
- **Patrón**: Controlador principal con manejadores de eventos
- **Funciones**: Gestión de eventos, coordinación de operaciones

#### 3. **Capa de Dominio/Core**
- **Propósito**: Lógica de negocio y acceso a datos
- **Componentes**: Base de datos, escáner, sincronización, utilidades

## 📁 Estructura del Proyecto

```
HDDINVENTORY/
├── main.py                 # 🏠 Punto de entrada principal
├── config.py              # ⚙️ Configuración global
├── requirements.txt       # 📦 Dependencias del proyecto
│
├── app/                   # 🎯 Lógica de aplicación
│   ├── __init__.py
│   ├── drive_handlers.py  # 🖱️ Manejadores de eventos de discos
│   └── filter_handlers.py # 🔍 Manejadores de filtros
│
├── core/                  # 🧠 Lógica de negocio
│   ├── __init__.py
│   ├── database.py        # 💾 Gestión de base de datos SQLite
│   ├── scanner.py         # 🔍 Escaneo de archivos y directorios
│   ├── excel_exporter.py  # 📊 Exportación a Excel
│   ├── sync_manager.py    # 🔄 Gestión de sincronización
│   └── smart/            # 💽 Soporte S.M.A.R.T.
│       ├── __init__.py
│       ├── smart_reader.py # 📖 Lector de datos S.M.A.R.T.
│       └── smart_db.py     # 💾 Base de datos S.M.A.R.T.
│
├── ui/                    # 🎨 Interfaz de usuario
│   ├── __init__.py
│   ├── main_window.py     # 🏠 Ventana principal
│   ├── top_bar.py         # 📋 Barra superior con navegación
│   ├── left_sidebar.py    # 📂 Barra lateral izquierda (discos)
│   ├── right_sidebar.py   # 🔍 Barra lateral derecha (filtros)
│   ├── center_view.py     # 📋 Vista central de resultados
│   ├── manage_view.py     # 💽 Gestión de discos
│   ├── statistics_view.py # 📊 Vista de estadísticas
│   ├── statistics_panel.py # 📈 Panel de estadísticas detallado
│   ├── status_bar.py      # 📊 Barra de estado
│   ├── styles.py          # 🎨 Estilos y temas
│   └── manage_dialogs.py  # 💬 Diálogos de gestión
│
├── utils/                 # 🛠️ Utilidades
│   ├── __init__.py
│   ├── settings.py        # ⚙️ Gestión de configuración
│   └── helpers.py         # 🔧 Funciones auxiliares
│
├── data/                  # 💾 Datos de aplicación
│   ├── inventory.db       # Base de datos principal
│   ├── settings.json      # Configuración de usuario
│   └── app.log           # Archivo de logs
│
├── docs/                  # 📚 Documentación
│   ├── ARCHITECTURE.md    # 🏗️ Arquitectura técnica
│   ├── USER_GUIDE.md      # 👥 Guía de usuario
│   ├── GUIA_DESARROLLO.md # 👨‍💻 Esta guía
│   └── *.md              # Documentos adicionales
│
└── tests/                 # 🧪 Pruebas
    ├── __init__.py
    └── test_*.py         # Archivos de prueba
```

## 🔧 Tecnologías y Librerías

### Framework Principal
- **PyQt6** (6.6.0+): Framework GUI nativo para Python
  - Widgets modernos y nativos
  - Señales y slots para comunicación entre componentes
  - Soporte completo para aplicaciones de escritorio

### Visualización y Gráficos
- **Matplotlib**: Generación de gráficos estadísticos
  - Treemaps para visualización de tamaños de carpeta
  - Gráficos de dona para distribución de tipos de archivo
  - Renderizado en segundo plano para evitar bloqueo de UI

- **Squarify** (0.4.0+): Algoritmo de treemap
  - Generación de diagramas de árbol cuadrados
  - Visualización jerárquica de tamaños de directorio

- **PyQt6-Charts** (6.6.0+): Gráficos integrados en Qt
  - Alternativa nativa para gráficos estadísticos

### Base de Datos y Almacenamiento
- **SQLite3**: Base de datos embebida
  - Sin servidor, archivo único
  - Transacciones ACID
  - Optimizaciones de rendimiento (WAL, cache)

### Utilidades del Sistema
- **psutil** (5.9.0+): Información del sistema
  - Monitoreo de discos y particiones
  - Información de hardware del sistema

- **Pillow** (PIL) (10.0.0+): Procesamiento de imágenes
  - Manipulación de imágenes para previews
  - Soporte para múltiples formatos

### Exportación y Datos
- **openpyxl** (3.1.0+): Manipulación de Excel
  - Exportación de datos a formato XLSX
  - Creación de hojas estructuradas
  - Formato de celdas y estilos

### Utilidades Python
- **humanize** (4.9.0+): Formateo human-readable
  - Tamaños de archivo legibles (KB, MB, GB)
  - Números formateados para display

## 🏠 Punto de Entrada (main.py)

### Clase HDDInventoryApp
**Ubicación**: `main.py` (858 líneas)
**Propósito**: Controlador principal de la aplicación

#### Funcionalidades Principales:
1. **Inicialización de Qt**: Configuración de QApplication
2. **Configuración de Logging**: Sistema de logs a archivo y consola
3. **Carga de Configuración**: Settings de sincronización
4. **Creación de Componentes**: Instancia ventana principal y vistas
5. **Conexión de Señales**: Enlace entre componentes
6. **Carga Inicial de Datos**: Población de datos al inicio

#### Método Principal:
```python
def run(self) -> int:
    """Ejecuta la aplicación y retorna código de salida"""
    # Inicialización completa
    # Conexión de señales
    # Carga de datos iniciales
    # Ejecución del loop de eventos Qt
```

## 🎯 Capa de Aplicación (app/)

### DriveEventHandlers (drive_handlers.py)
**Ubicación**: `app/drive_handlers.py` (145 líneas)
**Propósito**: Gestión de eventos relacionados con discos

#### Funcionalidades:
- **Selección de Disco**: Cambio a vista de inventario
- **Adición de Discos**: Diálogos y validación
- **Eliminación de Discos**: Confirmación y limpieza
- **Actualización de Discos**: Reescaneo y actualización

#### Métodos Clave:
- `on_view_drive_index()`: Muestra contenido de disco seleccionado
- `on_add_drive()`: Agrega nuevo disco al inventario
- `on_remove_drive()`: Elimina disco del inventario

### FilterEventHandlers (filter_handlers.py)
**Ubicación**: `app/filter_handlers.py` (247 líneas)
**Propósito**: Gestión de filtros de búsqueda

#### Funcionalidades:
- **Filtros de Texto**: Búsqueda por nombre de archivo
- **Filtros de Tipo**: Extensión de archivo
- **Filtros de Tamaño**: Rango de tamaños
- **Filtros de Fecha**: Rango de fechas de modificación

## 🧠 Capa de Dominio/Core

### DatabaseManager (database.py)
**Ubicación**: `core/database.py` (938 líneas)
**Propósito**: Abstracción completa de base de datos SQLite

#### Esquema de Base de Datos:
```sql
-- Discos
CREATE TABLE drives (
    id INTEGER PRIMARY KEY,
    drive_letter TEXT,
    drive_label TEXT,
    serial_number TEXT UNIQUE,
    capacity_bytes INTEGER,
    last_scan_date TEXT,
    file_count INTEGER,
    folder_count INTEGER
);

-- Carpetas
CREATE TABLE folders (
    id INTEGER PRIMARY KEY,
    drive_id INTEGER,
    folder_name TEXT,
    folder_path TEXT,
    parent_folder_id INTEGER,
    level INTEGER
);

-- Archivos
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    drive_id INTEGER,
    file_name TEXT,
    file_path TEXT,
    file_size INTEGER,
    file_extension TEXT,
    modified_date TEXT,
    parent_folder_id INTEGER
);
```

#### Funcionalidades Clave:
- **Operaciones CRUD**: Crear, leer, actualizar, eliminar
- **Jerarquía de Carpetas**: Gestión recursiva de estructura
- **Estadísticas**: Cálculos de tamaños y conteos
- **Optimizaciones**: Índices para rendimiento
- **Transacciones**: Operaciones atómicas

#### Métodos Importantes:
- `get_folder_size_hierarchy()`: Estructura jerárquica con tamaños
- `get_file_statistics()`: Estadísticas generales de archivos
- `search_files()`: Búsqueda con filtros avanzados

### FileScanner (scanner.py)
**Ubicación**: `core/scanner.py`
**Propósito**: Escaneo recursivo de sistemas de archivos

#### Funcionalidades:
- **Escaneo Recursivo**: Traversing completo de directorios
- **Detección de Cambios**: Comparación con datos existentes
- **Manejo de Errores**: Permisos, archivos bloqueados
- **Progreso**: Callbacks para actualización de UI
- **Filtros**: Exclusión de carpetas del sistema

### SyncManager (sync_manager.py)
**Ubicación**: `core/sync_manager.py`
**Propósito**: Sincronización entre múltiples equipos

#### Funcionalidades:
- **Versionado**: Sistema de versiones para resolución de conflictos
- **Modos de Sincronización**:
  - Bidireccional: Sincronización automática
  - Solo lectura: Descarga únicamente
  - Solo escritura: Carga únicamente
- **Detección de Cambios**: Comparación de timestamps y versiones
- **Respaldo Automático**: Backup antes de sobrescribir

### ExcelExporter (excel_exporter.py)
**Ubicación**: `core/excel_exporter.py`
**Propósito**: Exportación de datos a Excel

#### Funcionalidades:
- **Hojas Estructuradas**: Índice de discos + datos individuales
- **Control de Profundidad**: Niveles de carpeta configurables
- **Procesamiento en Segundo Plano**: Sin bloqueo de UI
- **Estadísticas**: Columnas de conteo y tamaño

## 💽 Módulo S.M.A.R.T. (core/smart/)

### SmartReader (smart_reader.py)
**Ubicación**: `core/smart/smart_reader.py`
**Propósito**: Lectura de datos S.M.A.R.T. de discos

#### Funcionalidades:
- **Interface con smartctl**: Comunicación con herramienta externa
- **Análisis de Salud**: Estado PASSED/FAILED/CAUTION
- **Métricas Detalladas**: Temperatura, sectores reasignados, horas de encendido
- **Recomendaciones**: Sugerencias de reemplazo

### SmartDB (smart_db.py)
**Ubicación**: `core/smart/smart_db.py`
**Propósito**: Almacenamiento histórico de datos S.M.A.R.T.

#### Funcionalidades:
- **Historial Temporal**: Seguimiento de métricas a lo largo del tiempo
- **Tendencias**: Análisis de degradación
- **Alertas**: Detección de cambios críticos

## 🎨 Capa de Interfaz de Usuario (ui/)

### MainWindow (main_window.py)
**Ubicación**: `ui/main_window.py` (537 líneas)
**Propósito**: Ventana principal de la aplicación

#### Arquitectura:
- **Layout Principal**: Splitters para paneles ajustables
- **Modos de Vista**: Inventario, Gestión, Estadísticas
- **Navegación**: Barra superior con botones de modo
- **Señales**: Comunicación entre componentes

#### Componentes:
- **Top Bar**: Navegación y configuración
- **Left Sidebar**: Lista de discos
- **Center Stack**: Vistas principales (3 modos)
- **Right Sidebar**: Filtros y opciones
- **Status Bar**: Información y progreso

### StatisticsPanel (statistics_panel.py)
**Ubicación**: `ui/statistics_panel.py` (1277 líneas)
**Propósito**: Panel completo de estadísticas y visualizaciones

#### Características:
- **Vista General**: Resumen de discos y archivos
- **Treemap**: Visualización jerárquica de tamaños (carga diferida)
- **Distribución de Tipos**: Gráfico de dona optimizado para tema oscuro
- **Archivos Más Grandes**: Tabla de top archivos
- **S.M.A.R.T.**: Estado de salud y tendencias

### Styles (styles.py)
**Ubicación**: `ui/styles.py`
**Propósito**: Definición de tema visual

#### Características:
- **Tema Oscuro**: Tema profesional
- **Paleta de Colores**: Definida en config.py
- **Estilos Consistentes**: Aplicados globalmente
- **Responsive**: Adaptable a diferentes tamaños

## ⚙️ Configuración (config.py)

### Constantes Globales:
```python
# Información de aplicación
APP_NAME = "Almacen Digital"
APP_VERSION = "1.0.0"

# Rutas
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "inventory.db"

# Configuración de escaneo
DEFAULT_SCAN_DEPTH = -1  # Ilimitado
EXCLUDED_FOLDERS = ["$RECYCLE.BIN", "System Volume Information"]

# Configuración de UI
WINDOW_MIN_WIDTH = 1280
WINDOW_DEFAULT_WIDTH = 1600
```

## 🔄 Flujo de Datos

### 1. Inicio de Aplicación
```
main.py → HDDInventoryApp.__init__() → Configuración Qt
                                      → Carga de settings
                                      → Creación de MainWindow
                                      → Inicialización de componentes
                                      → Carga de datos iniciales
```

### 2. Operación de Escaneo
```
UI (Botón) → DriveEventHandlers → DatabaseManager.create_drive()
                              → FileScanner.scan_drive() → DatabaseManager.insert_files()
                                                           → Actualización de estadísticas
```

### 3. Búsqueda de Archivos
```
UI (Input) → FilterEventHandlers → DatabaseManager.search_files()
                               → ResultsView.update_results()
                               → Actualización de UI
```

### 4. Sincronización
```
SyncManager → Comparación de versiones → DatabaseManager.backup()
            → Copia de archivo → DatabaseManager.restore()
            → Actualización de UI
```

## 🚀 Despliegue y Distribución

### Requisitos del Sistema
- **SO**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python**: 3.9 o superior
- **Espacio**: 100MB mínimo + espacio para base de datos
- **Hardware**: Disco externo para catalogar

### Instalación
```bash
# Clonar repositorio
git clone <repository-url>
cd hddinventory

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

### Empaquetado
- **PyInstaller**: Para distribución binaria
- **cx_Freeze**: Alternativa para Windows
- **Scripts de instalación**: `install.bat`, `run.bat`

## 🧪 Pruebas

### Estructura de Pruebas
```
tests/
├── __init__.py
├── test_database.py    # Pruebas de base de datos
├── test_scanner.py     # Pruebas de escaneo
├── test_ui.py         # Pruebas de interfaz
└── test_sync.py       # Pruebas de sincronización
```

### Tipos de Pruebas
- **Unitarias**: Funciones individuales
- **Integración**: Componentes interactuando
- **UI**: Interfaz gráfica (con PyQt testing)
- **Performance**: Operaciones de escaneo y búsqueda

## 🔧 Desarrollo y Contribución

### Configuración del Entorno
```bash
# Entorno virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Todas las dependencias (incluyendo herramientas de desarrollo)
pip install -r requirements.txt

# Pre-commit hooks
pre-commit install
```

### Estándares de Código
- **Black**: Formateo automático (línea de 100 caracteres)
- **isort**: Ordenamiento de imports
- **flake8**: Linting y estilo
- **mypy**: Type checking

### Arquitectura de Commits
```
feat: nueva funcionalidad
fix: corrección de bug
docs: cambios en documentación
style: cambios de formato
refactor: refactorización de código
test: agregar o modificar pruebas
```

## 📊 Métricas de Rendimiento

### Base de Datos
- **Archivos indexados**: Hasta 1M archivos por base de datos
- **Tamaño típico**: ~100MB por 1M archivos
- **Velocidad de búsqueda**: < 100ms para consultas complejas
- **Velocidad de escaneo**: ~30 segundos por 10,000 archivos

### Interfaz de Usuario
- **Inicio**: < 2 segundos (con carga diferida de estadísticas)
- **Memoria**: < 150MB uso típico
- **Responsive**: Sin bloqueo en operaciones pesadas

### Sincronización
- **Tamaño de archivo**: Completo (no delta sync)
- **Velocidad**: Dependiente de conexión de red
- **Resolución de conflictos**: Basada en versiones (última gana)

## 🔒 Seguridad y Privacidad

### Medidas Implementadas
- **Datos Locales**: Base de datos reside en equipo del usuario
- **Sin Conexiones Externas**: Todo funciona offline
- **Control de Usuario**: Usuario controla ubicación de datos
- **Encriptación**: SQLite no encripta (usuario puede agregar)

### Consideraciones
- **Permisos de Archivo**: Acceso completo a carpetas escaneadas
- **Datos Sensibles**: No se transmiten datos externos
- **Backup**: Respaldos automáticos antes de sincronización

## 🚀 Roadmap y Mejoras Futuras

### Versión 1.1 (Planificada)
- [ ] **Sincronización en Tiempo Real**: WebSocket para sync instantáneo
- [ ] **Compresión de Base de Datos**: Reducción de tamaño de archivo
- [ ] **API REST**: Acceso remoto a datos
- [ ] **Plugins**: Sistema extensible de plugins

### Mejoras de Rendimiento
- [ ] **Indexación Avanzada**: Búsqueda full-text
- [ ] **Cache de Metadatos**: Aceleración de operaciones comunes
- [ ] **Lazy Loading**: Carga bajo demanda de datos grandes

### Nuevas Características
- [ ] **Análisis de Duplicados**: Detección de archivos duplicados
- [ ] **Previews de Imagen**: Thumbnails para archivos multimedia
- [ ] **Etiquetas y Categorías**: Sistema de organización personal
- [ ] **Exportación Avanzada**: Más formatos (CSV, JSON, XML)

---

## 📞 Contacto y Soporte

- **Repositorio**: [GitHub Repository]
- **Issues**: Reporte de bugs y solicitudes de features
- **Documentación**: [docs/INDEX.md](docs/INDEX.md)
- **Licencia**: Creative Commons Non-Commercial (CC BY-NC)

---

**Desarrollado con ❤️ usando Python, PyQt6 y SQLite**