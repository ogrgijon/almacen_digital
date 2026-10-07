"""Application configuration"""

import os
import sys
from pathlib import Path

# Application info
APP_NAME = "Almacén Digital"
APP_VERSION = "1.1.0"
APP_AUTHOR = "OGRGijon"

# Paths
BASE_DIR = Path(__file__).parent
if getattr(sys, "frozen", False):
    DATA_DIR = Path(sys.executable).resolve().parent / "data"
else:
    DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "inventory.db"
SETTINGS_PATH = DATA_DIR / "settings.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# XML metadata filename (stored on each drive)
XML_METADATA_FILENAME = ".drive_inventory_meta.xml"

# Database settings
DB_VERSION = 1

# Scan settings
DEFAULT_SCAN_DEPTH = -1  # -1 means unlimited
EXCLUDED_FOLDERS = [
    "$RECYCLE.BIN",
    "System Volume Information",
    "$Windows.~BT",
    "Windows.old",
    "hiberfil.sys",
    "pagefile.sys",
    "swapfile.sys",
]

EXCLUDED_EXTENSIONS = []  # Can add extensions to exclude

# UI settings
WINDOW_MIN_WIDTH = 1280
WINDOW_MIN_HEIGHT = 720
WINDOW_DEFAULT_WIDTH = 1600
WINDOW_DEFAULT_HEIGHT = 900

# File size limits for display
MAX_FILE_SIZE_DISPLAY = 1024 * 1024 * 1024 * 1024  # 1 TB

# Search settings
SEARCH_DEBOUNCE_MS = 300  # Milliseconds to wait before searching
MAX_SEARCH_RESULTS = 10000  # Maximum results to display

# Logging
LOG_PATH = DATA_DIR / "hddinventory.log"

# Sync settings
SYNC_ENABLED = False  # Enable/disable sync on startup/shutdown
SYNC_BACKUP_PATH = None  # Path to backup database file (in cloud-synced folder)
SYNC_DIRECTION = "bidirectional"  # "from_backup", "to_backup", or "bidirectional"
SYNC_ON_STARTUP = True  # Sync when app starts
SYNC_ON_SHUTDOWN = True  # Sync when app closes

# Colors (Dark theme)
COLORS = {
    'background': '#191919',
    'panel_bg': '#252525',
    'panel_border': '#3a3a3a',
    'text_primary': '#e0e0e0',
    'text_secondary': '#a0a0a0',
    'accent_primary': '#d89000',
    'accent_hover': '#ffa726',
    'selection': '#2d5d7b',
    'success': '#4caf50',
    'warning': '#ff9800',
    'error': '#f44336',
    'scrollbar': '#3a3a3a',
    'button': '#404040',
    'button_hover': '#505050',
    'input_bg': '#2d2d2d',
    'hover': '#303030',
}

# File type categories
FILE_CATEGORIES = {
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.tiff', '.webp', '.raw'],
    'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.opus'],
    'Video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'],
    'Code': ['.py', '.js', '.html', '.css', '.cpp', '.c', '.h', '.java', '.cs', '.php', '.rb'],
    'Other': []
}

# Legal disclaimer settings
FIRST_RUN_ACKNOWLEDGED = False

# Language settings
LANGUAGE = 'es'  # Default language: 'es' or 'en'
