# Development Guide - Almacén Digital

## 📋 General Information

**Almacén Digital** is a desktop application developed in Python for cataloging and searching files across multiple external hard drives. It uses a modular architecture with a PyQt6-based graphical interface and an SQLite database system for persistent storage.

- **Version**: 1.0.0
- **Date**: January 2026
- **Status**: Production
- **License**: Creative Commons Non-Commercial (CC BY-NC)

## 🏗️ Application Architecture

### Architectural Pattern
The application follows a modified **MVC (Model-View-Controller)** architecture with clear separation of responsibilities:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   INTERFACE     │    │   CONTROLLER    │    │     MODEL       │
│     (UI)        │◄──►│     (APP)       │◄──►│    (CORE)       │
│                 │    │                 │    │                 │
│ - main_window   │    │ - controller    │    │ - database      │
│ - sidebars      │    │ - handlers      │    │ - scanner       │
│ - views         │    │ - sync_manager  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Architecture Layers

#### 1. **Presentation Layer (UI)**
- **Purpose**: User interface and visual experience
- **Framework**: PyQt6 with dark theme
- **Components**: Windows, panels, sidebars, views

#### 2. **Application Layer (APP)**
- **Purpose**: Coordination between UI and business logic
- **Pattern**: Main controller with event handlers
- **Functions**: Event management, operation coordination

#### 3. **Domain/Core Layer**
- **Purpose**: Business logic and data access
- **Components**: Database, scanner, synchronization, utilities

## 📁 Project Structure

```
HDDINVENTORY/
├── main.py                 # 🏠 Main entry point
├── config.py              # ⚙️ Global configuration
├── requirements.txt       # 📦 Project dependencies
│
├── app/                   # 🎯 Application logic
│   ├── __init__.py
│   ├── drive_handlers.py  # 🖱️ Drive event handlers
│   └── filter_handlers.py # 🔍 Filter handlers
│
├── core/                  # 🧠 Business logic
│   ├── __init__.py
│   ├── database.py        # 💾 SQLite database management
│   ├── scanner.py         # 🔍 File and directory scanning
│   ├── excel_exporter.py  # 📊 Excel export
│   ├── sync_manager.py    # 🔄 Synchronization management
│   └── smart/            # 💽 S.M.A.R.T. support
│       ├── __init__.py
│       ├── smart_reader.py # 📖 S.M.A.R.T. data reader
│       └── smart_db.py     # 💾 S.M.A.R.T. database
│
├── ui/                    # 🎨 User interface
│   ├── __init__.py
│   ├── main_window.py     # 🏠 Main window
│   ├── top_bar.py         # 📋 Top bar with navigation
│   ├── left_sidebar.py    # 📂 Left sidebar (drives)
│   ├── right_sidebar.py   # 🔍 Right sidebar (filters)
│   ├── center_view.py     # 📋 Center results view
│   ├── manage_view.py     # 💽 Drive management
│   ├── statistics_view.py # 📊 Statistics view
│   ├── statistics_panel.py # 📈 Detailed statistics panel
│   ├── status_bar.py      # 📊 Status bar
│   ├── styles.py          # 🎨 Styles and themes
│   └── manage_dialogs.py  # 💬 Management dialogs
│
├── utils/                 # 🛠️ Utilities
│   ├── __init__.py
│   ├── settings.py        # ⚙️ Settings management
│   └── helpers.py         # 🔧 Helper functions
│
├── data/                  # 💾 Application data
│   ├── inventory.db       # Main database
│   ├── settings.json      # User settings
│   └── app.log           # Log file
│
├── docs/                  # 📚 Documentation
│   ├── ARCHITECTURE.md    # 🏗️ Technical architecture
│   ├── USER_GUIDE.md      # 👥 User guide
│   ├── GUIA_DESARROLLO.md # 👨‍💻 This guide
│   └── *.md              # Additional documents
│
└── tests/                 # 🧪 Tests
    ├── __init__.py
    └── test_*.py         # Test files
```

## 🔧 Technologies and Libraries

### Main Framework
- **PyQt6** (6.6.0+): Native GUI framework for Python
  - Modern and native widgets
  - Signals and slots for component communication
  - Full desktop application support

### Visualization and Graphics
- **Matplotlib**: Statistical chart generation
  - Treemaps for folder size visualization
  - Donut charts for file type distribution
  - Background rendering to avoid UI blocking

- **Squarify** (0.4.0+): Treemap algorithm
  - Square treemap diagram generation
  - Hierarchical directory size visualization

- **PyQt6-Charts** (6.6.0+): Qt-integrated charts
  - Native alternative for statistical charts

### Database and Storage
- **SQLite3**: Embedded database
  - Serverless, single file
  - ACID transactions
  - Performance optimizations (WAL, cache)

### System Utilities
- **psutil** (5.9.0+): System information
  - Disk and partition monitoring
  - System hardware information

- **Pillow** (PIL) (10.0.0+): Image processing
  - Image manipulation for previews
  - Support for multiple formats

### Export and Data
- **openpyxl** (3.1.0+): Excel manipulation
  - Data export to XLSX format
  - Structured sheet creation
  - Cell formatting and styles

### Python Utilities
- **humanize** (4.9.0+): Human-readable formatting
  - Readable file sizes (KB, MB, GB)
  - Formatted numbers for display

## 🏠 Entry Point (main.py)

### HDDInventoryApp Class
**Location**: `main.py` (858 lines)
**Purpose**: Main application controller

#### Main Features:
1. **Qt Initialization**: QApplication setup
2. **Logging Configuration**: File and console logging system
3. **Settings Loading**: Synchronization settings
4. **Component Creation**: Main window and views instantiation
5. **Signal Connection**: Component linking
6. **Initial Data Loading**: Data population on startup

#### Main Method:
```python
def run(self) -> int:
    """Runs the application and returns exit code"""
    # Complete initialization
    # Signal connections
    # Initial data loading
    # Qt event loop execution
```

## 🎯 Application Layer (app/)

### DriveEventHandlers (drive_handlers.py)
**Location**: `app/drive_handlers.py` (145 lines)
**Purpose**: Drive-related event management

#### Features:
- **Drive Selection**: Switch to inventory view
- **Drive Addition**: Dialogs and validation
- **Drive Removal**: Confirmation and cleanup
- **Drive Updates**: Rescanning and updating

#### Key Methods:
- `on_view_drive_index()`: Shows selected drive content
- `on_add_drive()`: Adds new drive to inventory
- `on_remove_drive()`: Removes drive from inventory

### FilterEventHandlers (filter_handlers.py)
**Location**: `app/filter_handlers.py` (247 lines)
**Purpose**: Search filter management

#### Features:
- **Text Filters**: Search by filename
- **Type Filters**: File extension
- **Size Filters**: Size range
- **Date Filters**: Modification date range

## 🧠 Domain/Core Layer

### DatabaseManager (database.py)
**Location**: `core/database.py` (938 lines)
**Purpose**: Complete SQLite database abstraction

#### Database Schema:
```sql
-- Drives
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

-- Folders
CREATE TABLE folders (
    id INTEGER PRIMARY KEY,
    drive_id INTEGER,
    folder_name TEXT,
    folder_path TEXT,
    parent_folder_id INTEGER,
    level INTEGER
);

-- Files
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

#### Key Features:
- **CRUD Operations**: Create, read, update, delete
- **Folder Hierarchy**: Recursive structure management
- **Statistics**: Size and count calculations
- **Optimizations**: Performance indexes
- **Transactions**: Atomic operations

#### Important Methods:
- `get_folder_size_hierarchy()`: Hierarchical structure with sizes
- `get_file_statistics()`: General file statistics
- `search_files()`: Advanced search with filters

### FileScanner (scanner.py)
**Location**: `core/scanner.py`
**Purpose**: Recursive filesystem scanning

#### Features:
- **Recursive Scanning**: Complete directory traversal
- **Change Detection**: Comparison with existing data
- **Error Handling**: Permissions, locked files
- **Progress**: UI update callbacks
- **Filters**: System folder exclusion

### SyncManager (sync_manager.py)
**Location**: `core/sync_manager.py`
**Purpose**: Synchronization between multiple devices

#### Features:
- **Versioning**: Conflict resolution system
- **Synchronization Modes**:
  - Bidirectional: Automatic synchronization
  - Read-only: Download only
  - Write-only: Upload only
- **Change Detection**: Timestamp and version comparison
- **Automatic Backup**: Backup before overwriting

### ExcelExporter (excel_exporter.py)
**Location**: `core/excel_exporter.py`
**Purpose**: Data export to Excel

#### Features:
- **Structured Sheets**: Drive index + individual data
- **Depth Control**: Configurable folder levels
- **Background Processing**: No UI blocking
- **Statistics**: Count and size columns

## 💽 S.M.A.R.T. Module (core/smart/)

### SmartReader (smart_reader.py)
**Location**: `core/smart/smart_reader.py`
**Purpose**: Reading S.M.A.R.T. data from drives

#### Features:
- **smartctl Interface**: Communication with external tool
- **Health Analysis**: PASSED/FAILED/CAUTION status
- **Detailed Metrics**: Temperature, reallocated sectors, power-on hours
- **Recommendations**: Replacement suggestions

### SmartDB (smart_db.py)
**Location**: `core/smart/smart_db.py`
**Purpose**: Historical S.M.A.R.T. data storage

#### Features:
- **Temporal History**: Metric tracking over time
- **Trends**: Degradation analysis
- **Alerts**: Critical change detection

## 🎨 User Interface Layer (ui/)

### MainWindow (main_window.py)
**Location**: `ui/main_window.py` (537 lines)
**Purpose**: Main application window

#### Architecture:
- **Main Layout**: Adjustable panel splitters
- **View Modes**: Inventory, Management, Statistics
- **Navigation**: Top bar with mode buttons
- **Signals**: Component communication

#### Components:
- **Top Bar**: Navigation and settings
- **Left Sidebar**: Drive list
- **Center Stack**: Main views (3 modes)
- **Right Sidebar**: Filters and options
- **Status Bar**: Information and progress

### StatisticsPanel (statistics_panel.py)
**Location**: `ui/statistics_panel.py` (1277 lines)
**Purpose**: Complete statistics and visualization panel

#### Features:
- **Overview**: Drive and file summary
- **Treemap**: Hierarchical size visualization (lazy loading)
- **Type Distribution**: Optimized donut chart for dark theme
- **Largest Files**: Top files table
- **S.M.A.R.T.**: Health status and trends

### Styles (styles.py)
**Location**: `ui/styles.py`
**Purpose**: Visual theme definition

#### Features:
- **Dark Theme**: Professional theme
- **Color Palette**: Defined in config.py
- **Consistent Styles**: Globally applied
- **Responsive**: Adaptable to different sizes

## ⚙️ Configuration (config.py)

### Global Constants:
```python
# Application information
APP_NAME = "Almacén Digital"
APP_VERSION = "1.0.0"

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "inventory.db"

# Scanning configuration
DEFAULT_SCAN_DEPTH = -1  # Unlimited
EXCLUDED_FOLDERS = ["$RECYCLE.BIN", "System Volume Information"]

# UI configuration
WINDOW_MIN_WIDTH = 1280
WINDOW_DEFAULT_WIDTH = 1600
```

## 🔄 Data Flow

### 1. Application Startup
```
main.py → HDDInventoryApp.__init__() → Qt configuration
                                      → Settings loading
                                      → MainWindow creation
                                      → Component initialization
                                      → Initial data loading
```

### 2. Scanning Operation
```
UI (Button) → DriveEventHandlers → DatabaseManager.create_drive()
                              → FileScanner.scan_drive() → DatabaseManager.insert_files()
                                                           → Statistics update
```

### 3. File Search
```
UI (Input) → FilterEventHandlers → DatabaseManager.search_files()
                               → ResultsView.update_results()
                               → UI update
```

### 4. Synchronization
```
SyncManager → Version comparison → DatabaseManager.backup()
            → File copy → DatabaseManager.restore()
            → UI update
```

## 🚀 Deployment and Distribution

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python**: 3.9 or higher
- **Space**: 100MB minimum + space for database
- **Hardware**: External drive for cataloging

### Installation
```bash
# Clone repository
git clone <repository-url>
cd hddinventory

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Packaging
- **PyInstaller**: For binary distribution
- **cx_Freeze**: Alternative for Windows
- **Installation Scripts**: `install.bat`, `run.bat`

## 🧪 Testing

### Test Structure
```
tests/
├── __init__.py
├── test_database.py    # Database tests
├── test_scanner.py     # Scanning tests
├── test_ui.py         # Interface tests
└── test_sync.py       # Synchronization tests
```

### Test Types
- **Unit Tests**: Individual functions
- **Integration Tests**: Interacting components
- **UI Tests**: Graphical interface (with PyQt testing)
- **Performance Tests**: Scanning and search operations

## 🔧 Development and Contribution

### Environment Setup
```bash
# Virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# All dependencies (including development tools)
pip install -r requirements.txt

# Pre-commit hooks
pre-commit install
```

### Code Standards
- **Black**: Automatic formatting (100 character line length)
- **isort**: Import sorting
- **flake8**: Linting and style
- **mypy**: Type checking

### Commit Architecture
```
feat: new functionality
fix: bug correction
docs: documentation changes
style: formatting changes
refactor: code refactoring
test: add or modify tests
```

## 📊 Performance Metrics

### Database
- **Indexed Files**: Up to 1M files per database
- **Typical Size**: ~100MB per 1M files
- **Search Speed**: < 100ms for complex queries
- **Scan Speed**: ~30 seconds per 10,000 files

### User Interface
- **Startup**: < 2 seconds (with lazy statistics loading)
- **Memory**: < 150MB typical usage
- **Responsive**: No blocking on heavy operations

### Synchronization
- **File Size**: Complete (no delta sync)
- **Speed**: Network connection dependent
- **Conflict Resolution**: Version-based (last wins)

## 🔒 Security and Privacy

### Implemented Measures
- **Local Data**: Database resides on user's device
- **No External Connections**: Everything works offline
- **User Control**: User controls data location
- **Encryption**: SQLite doesn't encrypt (user can add)

### Considerations
- **File Permissions**: Full access to scanned folders
- **Sensitive Data**: No external data transmission
- **Backup**: Automatic backups before synchronization

## 🚀 Roadmap and Future Improvements

### Version 1.1 (Planned)
- [ ] **Real-time Synchronization**: WebSocket for instant sync
- [ ] **Database Compression**: File size reduction
- [ ] **REST API**: Remote data access
- [ ] **Plugins**: Extensible plugin system

### Performance Improvements
- [ ] **Advanced Indexing**: Full-text search
- [ ] **Metadata Cache**: Acceleration of common operations
- [ ] **Lazy Loading**: On-demand loading of large data

### New Features
- [ ] **Duplicate Analysis**: Duplicate file detection
- [ ] **Image Previews**: Thumbnails for multimedia files
- [ ] **Tags and Categories**: Personal organization system
- [ ] **Advanced Export**: More formats (CSV, JSON, XML)

---

## 📞 Contact and Support

- **Repository**: [GitHub Repository]
- **Issues**: Bug reports and feature requests
- **Documentation**: [docs/INDEX.md](docs/INDEX.md)
- **License**: Creative Commons Non-Commercial (CC BY-NC)

---

**Developed with ❤️ using Python, PyQt6 and SQLite**</content>
<parameter name="filePath">c:\DOCS\PROYECTOS\HDDINVENTORY\docs\en\DEVELOPMENT_GUIDE.md