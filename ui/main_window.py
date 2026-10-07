"""Main application window"""


from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QStackedWidget, QLabel, QButtonGroup, QPushButton, QComboBox, QStatusBar
from PyQt6.QtCore import Qt, pyqtSignal
import logging
import config
from utils.helpers import find_smartctl
from ui.top_bar import create_top_bar
from ui.left_sidebar import create_left_sidebar
from ui.right_sidebar import create_right_sidebar
from ui.center_view import ResultsView
from ui.manage_view import ManageDrivesView
from ui.statistics_view import create_statistics_widget
from ui.status_bar import create_status_bar
from typing import Tuple
from i18n import _
from ui.styles import get_dark_stylesheet

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):


    """Main application window"""

    mode_changed = pyqtSignal(str)  # Emits: 'inventory', 'manage', 'statistics'

    def __init__(self, results_view=None, manage_view=None):
        # Inicializar atributos de barra de estado para evitar errores en llamadas tempranas
        self.stats_label = None
        self.status_label = None
        # Check for smartctl and show help if missing
        self.smartctl_available = find_smartctl() is not None
        """Initialize the main application window and layout."""
        logger.debug("MainWindow.__init__ start")
        super().__init__()
        self.current_mode = 'inventory'

        # Set window icon if available
        from PyQt6.QtGui import QIcon
        icon_path = config.BASE_DIR / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Window setup
        self.setWindowTitle(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        self.resize(config.WINDOW_DEFAULT_WIDTH, config.WINDOW_DEFAULT_HEIGHT)
        self.setStyleSheet(get_dark_stylesheet())

        # Central layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar
        try:
            top_bar, self.mode_buttons, self.button_group, self.settings_button = self.create_top_bar()
            main_layout.addWidget(top_bar)
        except Exception as e:
            logger.exception("Failed to create top bar: %s", e)

        # Sidebars and center stack
        try:
            self.left_sidebar = create_left_sidebar()
            # Create placeholder with layout for right sidebar that will be replaced later
            self.right_sidebar = QWidget()
            layout = QVBoxLayout(self.right_sidebar)
            layout.setContentsMargins(0, 0, 0, 0)
        except Exception as e:
            logger.exception("Failed to create sidebars: %s", e)
            self.left_sidebar = QWidget()
            self.right_sidebar = QWidget()

        self.center_stack = QStackedWidget()
        self.center_stack.setMinimumWidth(600)
        
        # Use provided widgets or fallback to default
        self.inventory_widget = results_view if results_view is not None else ResultsView()
        self.manage_widget = manage_view if manage_view is not None else ManageDrivesView(None)
        
        # Create statistics widget placeholder - will be loaded lazily
        self.statistics_widget = QWidget()  # Placeholder
        self.statistics_loaded = False  # Flag to track if statistics widget has been loaded
        
        self.center_stack.addWidget(self.inventory_widget)
        self.center_stack.addWidget(self.manage_widget)
        self.center_stack.addWidget(self.statistics_widget)

        # Add splitter for main content area
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.content_splitter.setChildrenCollapsible(False)
        self.content_splitter.addWidget(self.left_sidebar)
        self.content_splitter.addWidget(self.center_stack)
        self.content_splitter.addWidget(self.right_sidebar)
        self.content_splitter.setSizes([200, 800, 200])
        main_layout.addWidget(self.content_splitter, 1)

        # Status bar (must be before any method that uses self.stats_label)
        try:
            result = create_status_bar()
            # Nuevo: puede devolver 4 o 5 elementos
            if len(result) == 5:
                self.status_bar, self.status_label, self.stats_label, self.search_progress, self.about_btn = result
                self.about_btn.clicked.connect(self.show_legal_disclaimer)
            else:
                self.status_bar, self.status_label, self.stats_label, self.search_progress = result
            self.setStatusBar(self.status_bar)
        except Exception as e:
            logger.exception("Failed to create status bar: %s", e)
    def show_legal_disclaimer(self):
        from main import show_legal_disclaimer
        show_legal_disclaimer()

    def create_search_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(_("📦 Inventory View"))
        label.setObjectName('sectionHeader')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        info = QLabel(_("Browse, search, and filter your indexed files and folders"))
        info.setObjectName('subHeader')
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        layout.addStretch()
        return widget

    def create_manage_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(_("💾 Manage Drives"))
        label.setObjectName('sectionHeader')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        info = QLabel(_("Add, scan, and manage your drives"))
        info.setObjectName('subHeader')
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        layout.addStretch()
        return widget

    def create_top_bar(self) -> Tuple[QWidget, dict, QButtonGroup, QPushButton]:
        """Create top bar with mode switcher buttons and settings button"""
        top_bar, self.mode_buttons, self.button_group, self.settings_button = create_top_bar(
            self.switch_mode,
            self.show_settings_dialog
        )
        return top_bar, self.mode_buttons, self.button_group, self.settings_button



    def create_statistics_widget(self) -> QWidget:
        """Create Statistics mode widget with live stats and charts"""
        from core.database import DatabaseManager
        from utils.helpers import format_file_size
        import matplotlib
        matplotlib.use('Agg')  # Use non-GUI backend for rendering
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from PyQt6.QtWidgets import QSizePolicy

        widget = QWidget()
        layout = QVBoxLayout(widget)

        label = QLabel(_("📊 Statistics"))
        label.setObjectName('sectionHeader')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        db = DatabaseManager()
        stats = db.get_file_statistics()
        drives = db.get_all_drives()
        total_folders = sum(d.get('folder_count', 0) for d in drives)
        total_files = stats.get('total_files', 0)
        total_size = stats.get('total_size', 0)
        total_drives = len(drives)

        info = QLabel(f"<b>{_('Total files')}:</b> {total_files:,}<br>"
                      f"<b>{_('Total folders')}:</b> {total_folders:,}<br>"
                      f"<b>{_('Total drives')}:</b> {total_drives}<br>"
                      f"<b>{_('Total size')}:</b> {format_file_size(total_size)}")
        info.setObjectName('subHeader')
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        # --- Pie chart: Used vs Free space per drive ---
        for d in drives:
            drive_label = d.get('drive_label', 'Unknown')
            used = d.get('capacity_bytes', 0) - d.get('free_bytes', 0) if 'free_bytes' in d else 0
            free = d.get('free_bytes', 0) if 'free_bytes' in d else 0
            cap = d.get('capacity_bytes', 0)
            # Ensure used and free are not None and are numbers
            pie_values = [v for v in [used, free] if v is not None]
            if cap > 0 and all(isinstance(v, (int, float)) for v in pie_values) and sum(pie_values) > 0:
                fig, ax = plt.subplots(figsize=(3, 3))
                ax.pie(pie_values, labels=["Used", "Free"], autopct='%1.1f%%', colors=['#ff9999','#99ff99'])
                ax.set_title(f"{drive_label} Space Usage")
                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                layout.addWidget(canvas)
                plt.close(fig)
            elif cap > 0:
                layout.addWidget(QLabel(f"{drive_label}: No space data to display."))

        # --- Bar chart: File and Folder count per drive ---
        if drives:
            labels = [d.get('drive_label', 'Unknown') for d in drives]
            file_counts = [d.get('file_count', 0) for d in drives]
            folder_counts = [d.get('folder_count', 0) for d in drives]
            if any(file_counts) or any(folder_counts):
                fig, ax = plt.subplots(figsize=(5, 3))
                x = range(len(drives))
                ax.bar(x, file_counts, width=0.4, label='Files', color='#4f81bd')
                ax.bar([i + 0.4 for i in x], folder_counts, width=0.4, label='Folders', color='#c0504d')
                ax.set_xticks([i + 0.2 for i in x])
                ax.set_xticklabels(labels, rotation=30, ha='right')
                ax.set_ylabel('Count')
                ax.set_title('Files and Folders per Drive')
                ax.legend()
                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                layout.addWidget(canvas)
                plt.close(fig)
            else:
                layout.addWidget(QLabel("No file or folder data to display."))

        # --- Pie chart: File type distribution (top extensions) ---
        top_exts = stats.get('top_extensions', [])
        if top_exts:
            sizes = [e['count'] for e in top_exts]
            labels = [e['file_extension'] or '[none]' for e in top_exts]
            if any(sizes):
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
                ax.set_title('Top File Types')
                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                layout.addWidget(canvas)
                plt.close(fig)
            else:
                layout.addWidget(QLabel(_("No file type data to display.")))

        layout.addStretch()
        
        left_label = QLabel("🗂️" +_(" COLLECTIONS"))
        left_label.setObjectName('sectionHeader')
        left_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # (No change to create_statistics_widget, create_search_widget, create_manage_widget, etc.)
        db = DatabaseManager()
        stats = db.get_file_statistics()
        drives = db.get_all_drives()
        total_folders = sum(d.get('folder_count', 0) for d in drives)
        total_files = stats.get('total_files', 0)
        total_size = stats.get('total_size', 0)
        total_drives = len(drives)

        info = QLabel(f"<b>{_('Total files')}:</b> {total_files:,}<br>"
                      f"<b>{_('Total folders')}:</b> {total_folders:,}<br>"
                      f"<b>{_('Total drives')}:</b> {total_drives}<br>"
                      f"<b>{_('Total size')}:</b> {format_file_size(total_size)}")
        info.setObjectName('subHeader')
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        # --- Pie chart: Used vs Free space per drive (improved handling) ---
        for d in drives:
            drive_label = d.get('drive_label', 'Unknown')
            cap = d.get('capacity_bytes', 0)
            free = d.get('free_bytes', None)
            used = cap - free if (cap and free is not None) else None
            # Only use values that are not None and are numbers
            pie_values = [v for v in [used, free] if isinstance(v, (int, float)) and v is not None]
            if cap and free is not None and cap > 0 and len(pie_values) == 2:
                fig, ax = plt.subplots(figsize=(3, 3))
                ax.pie(pie_values, labels=["Used", "Free"], autopct='%1.1f%%', colors=['#ff9999','#99ff99'])
                ax.set_title(f"{drive_label} Space Usage")
                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                layout.addWidget(canvas)
                plt.close(fig)
            elif cap > 0:
                layout.addWidget(QLabel(f"{drive_label}: No space data to display (missing free_bytes)."))
            else:
                layout.addWidget(QLabel(f"{drive_label}: No capacity data to display."))

        # --- Bar chart: File and Folder count per drive ---
        if drives:
            labels = [d.get('drive_label', 'Unknown') for d in drives]
            file_counts = [d.get('file_count', 0) for d in drives]
            folder_counts = [d.get('folder_count', 0) for d in drives]
            if any(file_counts) or any(folder_counts):
                fig, ax = plt.subplots(figsize=(5, 3))
                x = range(len(drives))
                ax.bar(x, file_counts, width=0.4, label='Files', color='#4f81bd')
                ax.bar([i + 0.4 for i in x], folder_counts, width=0.4, label='Folders', color='#c0504d')
                ax.set_xticks([i + 0.2 for i in x])
                ax.set_xticklabels(labels, rotation=30, ha='right')
                ax.set_ylabel('Count')
                ax.set_title('Files and Folders per Drive')
                ax.legend()
                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                layout.addWidget(canvas)
                plt.close(fig)
            else:
                layout.addWidget(QLabel("No file or folder data to display."))

        # --- Pie chart: File type distribution (top extensions) ---
        top_exts = stats.get('top_extensions', [])
        if top_exts:
            sizes = [e['count'] for e in top_exts]
            labels = [e['file_extension'] or '[none]' for e in top_exts]
            if any(sizes):
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
                ax.set_title('Top File Types')
                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                layout.addWidget(canvas)
                plt.close(fig)
            else:
                layout.addWidget(QLabel(_("No file type data to display.")))

        # --- Hierarchical file/folder consumption (treemap) ---
        if drives:
            layout.addWidget(QLabel(_("<b>File Consumption by Folder (Treemap)</b>")))
            treemap_row = QHBoxLayout()
            drive_selector = QComboBox()
            drive_selector.addItems([f"{d.get('drive_label', 'Unknown')} ({d.get('drive_letter', '')})" for d in drives])
            treemap_row.addWidget(QLabel(_("Drive:")))
            treemap_row.addWidget(drive_selector)
            show_btn = QPushButton(_("Show Treemap"))
            treemap_row.addWidget(show_btn)
            layout.addLayout(treemap_row)

            treemap_canvas_holder = QWidget()
            treemap_canvas_layout = QVBoxLayout(treemap_canvas_holder)
            layout.addWidget(treemap_canvas_holder)

            def plot_treemap_for_drive(idx):
                # Clear previous
                for i in reversed(range(treemap_canvas_layout.count())):
                    item = treemap_canvas_layout.itemAt(i)
                    if item is not None:
                        w = item.widget()
                        if w is not None:
                            w.setParent(None)
                drive = drives[idx]
                hierarchy = db.get_folder_size_hierarchy(drive['id'], 0, max_depth=3)
                import squarify
                def flatten_hierarchy(nodes, parent_name=""):
                    flat = []
                    for n in nodes:
                        label = f"{parent_name}/{n['name']}" if parent_name else n['name']
                        if n['children']:
                            flat.extend(flatten_hierarchy(n['children'], label))
                        else:
                            flat.append({'label': label, 'size': n['size']})
                    return flat
                flat = flatten_hierarchy(hierarchy)
                sizes = [f['size'] for f in flat if f['size'] > 0]
                labels = [f['label'] for f in flat if f['size'] > 0]
                if not sizes:
                    treemap_canvas_layout.addWidget(QLabel("No file size data for this drive."))
                    return
                fig, ax = plt.subplots(figsize=(7, 4))
                squarify.plot(sizes=sizes, label=labels, ax=ax, alpha=0.7, text_kwargs={'fontsize':8})
                ax.set_title(f"{drive.get('drive_label', 'Unknown')} - Folder/File Space Usage")
                ax.axis('off')
                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                treemap_canvas_layout.addWidget(canvas)
                plt.close(fig)

            def on_show_btn():
                idx = drive_selector.currentIndex()
                plot_treemap_for_drive(idx)

            show_btn.clicked.connect(on_show_btn)
            # Show treemap for first drive by default
            if drives:
                plot_treemap_for_drive(0)

        layout.addStretch()
        return widget
    
    def create_status_bar(self) -> QStatusBar:
        """Create bottom status bar"""
        from PyQt6.QtWidgets import QPushButton
        status_bar = QStatusBar()
        status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {config.COLORS['panel_bg']};
                border-top: 1px solid {config.COLORS['panel_border']};
                padding: 4px;
            }}
        """)

        # Add status labels
        self.status_label = QLabel(_("Ready"))
        status_bar.addWidget(self.status_label)

        status_bar.addPermanentWidget(QLabel("|"))

        self.stats_label = QLabel(f"0 {_('files')} | 0 {_('drives')}")
        status_bar.addPermanentWidget(self.stats_label)

        # --- Acerca de ---
        about_btn = QPushButton(_("About:"))
        about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        about_btn.setStyleSheet("QPushButton { border: none; color: white; background: transparent; padding: 0 8px; } QPushButton:hover { color: #fff; text-decoration: underline; }")
        about_btn.clicked.connect(self.show_legal_disclaimer)
        status_bar.addPermanentWidget(about_btn)

        return status_bar

    def show_legal_disclaimer(self):
        from main import show_legal_disclaimer
        show_legal_disclaimer()
    
    def show_settings_dialog(self):
        """Show the settings dialog"""
        try:
            from ui.settings_dialog import SettingsDialog
            dialog = SettingsDialog(self)
            if dialog.exec():
                # Settings were saved, reload them
                from utils.settings import load_sync_settings
                load_sync_settings()
                self.update_status(_("Settings saved"))
        except Exception as e:
            logger.exception(f"Error showing settings dialog: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, _("Error"), f"{_('Failed to open settings dialog')}:\n{str(e)}")
    
    def switch_mode(self, mode: str):
        """Switch between modes and update top menu button state"""
        if mode == self.current_mode:
            return

        self.current_mode = mode

        # Lazy load statistics widget when switching to statistics mode
        if mode == 'statistics' and not self.statistics_loaded:
            self._load_statistics_widget()

        # Update center stack
        mode_index = {
            'inventory': 0,
            'manage': 1,
            'statistics': 2
        }
        self.center_stack.setCurrentIndex(mode_index[mode])

        # Update top menu button state
        if hasattr(self, 'mode_buttons') and mode in self.mode_buttons:
            self.mode_buttons[mode].setChecked(True)

        # Emit signal
        self.mode_changed.emit(mode)
    
    def _load_statistics_widget(self):
        """Load the statistics widget on demand"""
        try:
            from ui.statistics_view import create_statistics_widget
            self.update_status("Loading statistics...")
            
            # Create the actual statistics widget
            stats_widget = create_statistics_widget(None)
            
            # Replace the placeholder
            index = self.center_stack.indexOf(self.statistics_widget)
            self.center_stack.removeWidget(self.statistics_widget)
            self.statistics_widget.deleteLater()  # Clean up placeholder
            self.statistics_widget = stats_widget
            self.center_stack.insertWidget(index, self.statistics_widget)
            
            self.statistics_loaded = True
            self.update_status("Statistics loaded")
            
        except Exception as e:
            logger.exception("Failed to load statistics widget: %s", e)
            self.update_status("Failed to load statistics")
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.setText(message)
    
    def show_search_progress(self, message: str = "Buscando..."):
        """Show search progress bar with optional message"""
        self.status_label.setText(message)
        if hasattr(self, 'search_progress'):
            self.search_progress.setVisible(True)
    
    def hide_search_progress(self):
        """Hide search progress bar"""
        if hasattr(self, 'search_progress'):
            self.search_progress.setVisible(False)
    
    def update_stats(self, files_count: int, drives_count: int, total_size: int = 0):
        """Update statistics in status bar"""
        from utils.helpers import format_file_size
        stats_text = f"{files_count:,} {_('files')} | {drives_count} {_('drives')}"
        if total_size > 0:
            stats_text += f" | {format_file_size(total_size)}"
        if hasattr(self, 'stats_label') and self.stats_label is not None:
            self.stats_label.setText(stats_text)
    
    def set_left_sidebar_widget(self, widget: QWidget):
        """Replace left sidebar content"""
        layout = self.left_sidebar.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                w = item.widget() if item else None
                if w is not None:
                    w.deleteLater()
            layout.addWidget(widget)
    
    def set_right_sidebar_widget(self, widget: QWidget):
        """Replace right sidebar content"""
        layout = self.right_sidebar.layout()
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                w = item.widget() if item else None
                if w is not None:
                    w.deleteLater()
            layout.addWidget(widget)

    def reload_statistics(self):
        """Reload the statistics widget if it's loaded"""
        if self.statistics_loaded:
            self._load_statistics_widget()


