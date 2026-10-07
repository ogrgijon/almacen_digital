
"""
Punto de entrada principal para HDDInventory.
Gestiona el arranque de la aplicación y la conexión de los componentes principales.
"""

from typing import Any

import sys
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont
from ui.main_window import MainWindow
from ui.left_sidebar import CollectionsSidebar
from ui.right_sidebar import FiltersSidebar
from ui.center_view import ResultsView
from ui.manage_view import ManageDrivesView
from core.database import DatabaseManager
from core.sync_manager import SyncManager
import config
import utils.settings
import i18n
from utils.settings import load_sync_settings, save_legal_settings


def show_legal_disclaimer():
    """
    Muestra el diálogo de descargo de responsabilidad legal la primera vez que se ejecuta la aplicación.
    """
    dialog = QDialog()
    from i18n import _
    dialog.setWindowTitle(_("Aviso Legal - Almacén Digital"))
    dialog.setModal(True)
    dialog.setFixedSize(600, 400)
    
    layout = QVBoxLayout()
    
    # Imagen splash
    splash_label = QLabel()
    splash_path = config.BASE_DIR / "splash.png"
    if splash_path.exists():
        pixmap = QPixmap(str(splash_path))
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(500, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            splash_label.setPixmap(scaled_pixmap)
            splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            splash_label.setText("Almacén Digital")
            splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            splash_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
    else:
        splash_label.setText("Almacén Digital")
        splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        splash_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
    layout.addWidget(splash_label)
    
    # Texto del aviso
    text_label = QLabel()
    text_label.setWordWrap(True)
    text_label.setText(_("AVISOLEGAL_TEXT"))
    text_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
    
    layout.addWidget(text_label)
    
    # Botón aceptar
    button_layout = QHBoxLayout()
    accept_button = QPushButton(_("Aceptar"))
    accept_button.clicked.connect(dialog.accept)
    button_layout.addStretch()
    button_layout.addWidget(accept_button)
    button_layout.addStretch()
    
    layout.addLayout(button_layout)
    
    dialog.setLayout(layout)
    dialog.exec()


class HDDInventoryApp:
    """
    Controlador principal de la aplicación.
    Se encarga de inicializar la interfaz, cargar datos y conectar señales.
    """
    def __init__(self):
        """
        Inicializa la aplicación, la base de datos y todos los paneles principales.
        Conecta las señales y carga los datos iniciales.
        """
        try:
            self.splash = None
            # Configuración de logging
            logging.basicConfig(
                filename=str(config.LOG_PATH),
                level=logging.INFO,
                format='%(asctime)s %(levelname)s %(name)s: %(message)s'
            )
            logging.getLogger().addHandler(logging.StreamHandler())

            # Load all settings from file (sync, UI, scan, search, language)
            load_sync_settings()

            # Initialize i18n with configured language
            i18n.set_language(config.LANGUAGE)

            # Inicialización de la aplicación Qt
            self.app = QApplication(sys.argv)
            self.app.setApplicationName(config.APP_NAME)
            self.app.setApplicationVersion(config.APP_VERSION)

            # Set application icon if available
            from PyQt6.QtGui import QIcon
            icon_path = config.BASE_DIR / "icon.ico"
            if icon_path.exists():
                self.app.setWindowIcon(QIcon(str(icon_path)))

            # --- SPLASH SCREEN ---
            if config.FIRST_RUN_ACKNOWLEDGED:
                from PyQt6.QtWidgets import QSplashScreen
                from PyQt6.QtGui import QPixmap
                splash_path = config.BASE_DIR / "splash.png"
                if splash_path.exists():
                    pixmap = QPixmap(str(splash_path))
                    if not pixmap.isNull():
                        splash_pixmap = pixmap.scaled(500, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    else:
                        splash_pixmap = QPixmap(500, 250)
                else:
                    splash_pixmap = QPixmap(500, 250)
                self.splash = QSplashScreen(splash_pixmap)
                self.splash.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
                self.splash.show()
                self.app.processEvents()

            # Show legal disclaimer if first run
            if not config.FIRST_RUN_ACKNOWLEDGED:
                show_legal_disclaimer()
                config.FIRST_RUN_ACKNOWLEDGED = True
                save_legal_settings()

            # Inicialización de componentes principales
            self.db = DatabaseManager()
            self.sync_manager = SyncManager(str(config.DATABASE_PATH))
            self.left_sidebar = CollectionsSidebar()
            self.right_sidebar = FiltersSidebar()
            self.results_view = ResultsView(self.db)
            self.manage_view = ManageDrivesView(self.db)

            # Ventana principal
            self.window = MainWindow(results_view=self.results_view, manage_view=self.manage_view)
            self.window.set_left_sidebar_widget(self.left_sidebar)
            self.window.set_right_sidebar_widget(self.right_sidebar)
            self.setup_connections()

            # Defer heavy operations to after window is shown
            def finish_splash_and_load():
                self.window.show()
                if self.splash:
                    self.splash.finish(self.window)
                def load_initial_data_async():
                    try:
                        self.load_initial_data()
                        self.sync_on_startup()
                        self.window.switch_mode('inventory')
                    except Exception as e:
                        logging.exception(f"Error in async initialization: {e}")
                QTimer.singleShot(100, load_initial_data_async)

            QTimer.singleShot(100, finish_splash_and_load)
        except Exception as e:
            logging.exception(f"Exception in HDDInventoryApp.__init__: {e}")
            QMessageBox.critical(None, "Error de inicio", f"No se pudo iniciar la aplicación:\n{e}")
            sys.exit(1)

    def setup_connections(self):
        """
        Conecta todas las señales entre los paneles y la ventana principal.
        """
        # Señales de la ventana principal
        self.window.mode_changed.connect(self.on_mode_changed)
        # Señales del panel izquierdo
        self.left_sidebar.drive_selected.connect(self.on_drive_selected)
        self.left_sidebar.quick_filter_selected.connect(self.on_quick_filter)
        # Señales del panel derecho
        self.right_sidebar.filters_changed.connect(self.on_filters_changed)
        self.right_sidebar.filters_reset.connect(self.on_filters_reset)
        # Señales de la vista de resultados
        self.results_view.search_requested.connect(self.on_quick_search)
        self.results_view.file_selected.connect(self.on_file_selected)
        self.results_view.page_requested.connect(self.on_page_requested)
        self.results_view.star_filter_changed.connect(self.on_star_filter_changed)
        # Señales de la vista de gestión
        self.manage_view.drive_added.connect(self.on_drive_added)
        self.manage_view.drive_removed.connect(self.on_drive_removed)
        self.manage_view.stats_updated.connect(self.on_stats_updated)
        self.manage_view.view_drive_index.connect(self.on_view_drive_index)

    def on_view_drive_index(self, drive_id: int):
        """
        Cambia a modo Inventario, filtra por el drive seleccionado y muestra solo las carpetas raíz.
        """
        self.window.switch_mode('inventory')
        # Get the drive info
        drive = self.db.get_drive_by_id(drive_id)
        if not drive:
            self.results_view.load_results([])
            return
        drive_label = drive.get('drive_label', '')
        set_drive_filter = getattr(self.right_sidebar, 'set_drive_filter', None)
        if callable(set_drive_filter):
            set_drive_filter(drive_label)
            # This should trigger the filter logic via signals
        else:
            # If not found, fallback to previous logic
            drive_letter = drive.get('drive_letter', '').rstrip('\\')
            all_folders = self.db.get_folders_by_drive(drive_id)
            folders = [f for f in all_folders if (f['folder_path'] == drive_letter or f['folder_path'] == '')]
            results = [
                {
                    'file_name': f['folder_name'],
                    'file_path': f['folder_path'],
                    'file_size': '',
                    'file_extension': '',
                    'modified_date': '',
                    'drive_label': drive.get('drive_label', ''),
                    'drive_letter': drive_letter,
                    'is_folder': True
                }
                for f in folders
            ]
            self.results_view.load_results(results)
    
    def load_initial_data(self):
        """
        Carga los datos iniciales al arrancar la aplicación.
        """
        # Get drives and statistics
        drives = self.db.get_all_drives()
        stats = self.db.get_file_statistics()
        
        # Update UI
        # Safely call load_drives if it exists on left_sidebar
        if hasattr(self.left_sidebar, 'load_drives') and callable(getattr(self.left_sidebar, 'load_drives')):
            self.left_sidebar.load_drives(drives)
        else:
            logging.warning("CollectionsSidebar does not have a 'load_drives' method.")
        if hasattr(self.right_sidebar, 'load_drives') and callable(getattr(self.right_sidebar, 'load_drives')):
            self.right_sidebar.load_drives(drives)
        else:
            logging.warning("FiltersSidebar does not have a 'load_drives' method.")
        
        self.window.update_stats(
            files_count=stats.get('total_files', 0),
            drives_count=len(drives),
            total_size=stats.get('total_size', 0)
        )
        
        # Load all files initially
        if stats.get('total_files', 0) > 0:
            # Defer loading files to avoid blocking UI
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(50, lambda: self.load_all_files())
        else:
            self.window.update_status(_("Ready - Add a drive to begin"))
    
    def load_all_files(self, limit=None):
        """
        Carga todos los archivos (con límite opcional para paginación).
        """
        try:
            if limit is None:
                # Initial load - use pagination
                current_filters = {}
                self.results_view.current_filters = current_filters
                self.results_view.current_page = 1
                
                results, total_count = self.db.search_files(
                    limit=self.results_view.page_size,
                    offset=0
                )
                self.results_view.load_results(results, total_count)
                self.window.update_status(f"Mostrando página 1 ({len(results)} de {total_count:,} archivos)")
            else:
                # Legacy call with specific limit
                results, _ = self.db.search_files(limit=limit)
                self.results_view.load_results(results)
                self.window.update_status(f"Showing {len(results):,} files")
        except Exception as e:
            QMessageBox.warning(self.window, "Error", f"Error loading files:\n{str(e)}")
    
    def on_mode_changed(self, mode: str):
        """
        Maneja los cambios de modo de la aplicación.
        """
        # Reload data for manage mode
        if mode == 'manage':
            self.manage_view.load_drives()
        # Focus search box in search mode
        if mode == 'search':
            try:
                self.results_view.search_box.setFocus()
            except Exception:
                pass
    
    def on_drive_selected(self, drive_id: int):
        """
        Maneja la selección de un drive desde la barra lateral izquierda.
        Muestra solo las carpetas raíz para mejor rendimiento.
        """
        self._last_selected_drive_id = drive_id
        try:
            drive = self.db.get_drive_by_id(drive_id)
            if not drive:
                self.results_view.load_results([])
                return
            drive_letter = drive.get('drive_letter', '').rstrip('\\')
            all_folders = self.db.get_folders_by_drive(drive_id)
            folders = [f for f in all_folders if f.get('level', 0) == 0]
            results = [
                {
                    'file_name': f['folder_name'],
                    'file_path': f['folder_path'],
                    'file_size': '',
                    'file_extension': '',
                    'modified_date': '',
                    'drive_label': drive.get('drive_label', ''),
                    'drive_letter': drive_letter,
                    'is_folder': True
                }
                for f in folders
            ]
            self.results_view.load_results(results)
            self.window.update_status(f"Showing root folders from {drive['drive_label']}")
        except Exception as e:
            QMessageBox.warning(self.window, "Error", f"Error loading drive folders:\n{str(e)}")
    
    def on_quick_filter(self, filter_type: str):
        """
        Maneja la selección de filtros rápidos.
        """
        # Map Spanish filter types to English
        filter_mapping = {
            'documentos': 'documents',
            'imagenes': 'images',
            'audio': 'audio',
            'videos': 'videos',
            'comprimidos': 'archives',
            'archivos_grandes': 'large_files'
        }
        filter_type = filter_mapping.get(filter_type, filter_type)

        extensions = []

        if filter_type == 'root_folders':
            # Show root folders for the last selected drive, or all drives if none selected
            drive_id = getattr(self, '_last_selected_drive_id', None)
            if drive_id is None:
                # Try to get the first drive
                drives = self.db.get_all_drives()
                if not drives:
                    self.results_view.load_results([])
                    self.window.update_status("No drives available")
                    return
                drive_id = drives[0]['id']
            drive = self.db.get_drive_by_id(drive_id)
            if not drive:
                self.results_view.load_results([])
                self.window.update_status("Drive not found")
                return
            
            # Set up pagination for root folders
            current_filters = {'filter_type': 'root_folders', 'drive_id': drive_id}
            self.results_view.current_filters = current_filters
            self.results_view.current_page = 1
            
            # Get first page
            folders = self.db.get_folders_by_drive(drive_id, limit=self.results_view.page_size, offset=0)
            root_folders = [f for f in folders if f.get('level', 0) == 0]
            total_count = self.db.get_folders_count_by_drive(drive_id, max_level=0)  # Only root folders
            
            drive_letter = drive.get('drive_letter', '').rstrip('\\')
            results = [
                {
                    'file_name': f['folder_name'],
                    'file_path': f['folder_path'],
                    'file_size': '',
                    'file_extension': '',
                    'modified_date': '',
                    'drive_label': drive.get('drive_label', ''),
                    'drive_letter': drive_letter,
                    'is_folder': True
                }
                for f in root_folders
            ]
            self.results_view.load_results(results, total_count)
            self.window.update_status(f"Showing root folders from {drive['drive_label']}")
            return

        elif filter_type == 'folders':
            # Show folders from selected drive or all drives
            drive_id = getattr(self, '_last_selected_drive_id', None)
            if drive_id:
                # Show folders only from selected drive
                current_filters = {'filter_type': 'folders', 'drive_id': drive_id}
                self.results_view.current_filters = current_filters
                self.results_view.current_page = 1
                
                drive = self.db.get_drive_by_id(drive_id)
                if not drive:
                    self.results_view.load_results([])
                    self.window.update_status("Drive not found")
                    return
                
                total_count = self.db.get_folders_count_by_drive(drive_id)
                folders = self.db.get_folders_by_drive(drive_id, limit=self.results_view.page_size, offset=0)
                
                drive_letter = drive.get('drive_letter', '').rstrip('\\')
                results = [
                    {
                        'file_name': f['folder_name'],
                        'file_path': f['folder_path'],
                        'file_size': '',
                        'file_extension': '',
                        'modified_date': '',
                        'drive_label': drive.get('drive_label', ''),
                        'drive_letter': drive_letter,
                        'is_folder': True
                    }
                    for f in folders
                ]
                
                self.results_view.load_results(results, total_count)
                self.window.update_status(f"Showing folders from {drive['drive_label']}")
                return
            else:
                # Show all folders from all drives with pagination
                current_filters = {'filter_type': 'folders'}
                self.results_view.current_filters = current_filters
                self.results_view.current_page = 1
                
                # For simplicity, we'll paginate through all folders across all drives
                # Get all drives first
                drives = self.db.get_all_drives()
                if not drives:
                    self.results_view.load_results([])
                    self.window.update_status("No drives available")
                    return
                
                # Calculate total folder count across all drives
                total_count = sum(self.db.get_folders_count_by_drive(d['id']) for d in drives)
                
                # Get first page of folders from all drives combined
                all_folders = []
                remaining = self.results_view.page_size
                offset = 0
                
                for drive in drives:
                    if remaining <= 0:
                        break
                    folders = self.db.get_folders_by_drive(drive['id'], limit=remaining, offset=offset)
                    for f in folders:
                        f = dict(f)
                        f['drive_id'] = drive['id']
                        all_folders.append(f)
                    remaining -= len(folders)
                    # For next drive, start from offset 0 since we're combining
                    offset = 0
                
                results = []
                for f in all_folders:
                    drive = self.db.get_drive_by_id(f['drive_id'])
                    results.append({
                        'file_name': f['folder_name'],
                        'file_path': f['folder_path'],
                        'file_size': '',
                        'file_extension': '',
                        'modified_date': '',
                        'drive_label': drive.get('drive_label', '') if drive else '',
                        'drive_letter': drive.get('drive_letter', '') if drive else '',
                        'is_folder': True
                    })
                
                self.results_view.load_results(results, total_count)
                self.window.update_status(f"Showing all folders ({total_count:,})")
                return

        if filter_type == 'documents':
            extensions = config.FILE_CATEGORIES['Documents']
        elif filter_type == 'images':
            extensions = config.FILE_CATEGORIES['Images']
        elif filter_type == 'audio':
            extensions = config.FILE_CATEGORIES['Audio']
        elif filter_type == 'videos':
            extensions = config.FILE_CATEGORIES['Video']
        elif filter_type == 'archives':
            extensions = config.FILE_CATEGORIES['Archives']
        elif filter_type == 'large_files':
            # Files > 100MB
            current_filters = {'min_size': 100*1024*1024}
            if hasattr(self, '_last_selected_drive_id') and self._last_selected_drive_id:
                current_filters['drive_ids'] = [self._last_selected_drive_id]
            self.results_view.current_filters = current_filters
            self.results_view.current_page = 1
            results, total_count = self.db.search_files(
                limit=config.MAX_SEARCH_RESULTS,
                offset=0,
                **current_filters
            )
            self.results_view.load_results(results, total_count)
            self.window.update_status(f"Showing large files (>100MB)")
            return

        if extensions:
            current_filters = {'extensions': extensions}
            if hasattr(self, '_last_selected_drive_id') and self._last_selected_drive_id:
                current_filters['drive_ids'] = [self._last_selected_drive_id]
            self.results_view.current_filters = current_filters
            self.results_view.current_page = 1
            results, total_count = self.db.search_files(
                limit=config.MAX_SEARCH_RESULTS,
                offset=0,
                **current_filters
            )
            self.results_view.load_results(results, total_count)
            self.window.update_status(f"Showing {filter_type}")
    
    def on_star_filter_changed(self, min_rating: int):
        """
        Maneja el filtro de calificación de estrellas.
        """
        try:
            if min_rating == 0:
                # Show all files (clear the rating filter)
                self.load_all_files()
                self.window.update_status("Mostrando todos los archivos")
                return
            
            # Set up pagination for star rating filter
            current_filters = {'min_rating': min_rating}
            self.results_view.current_filters = current_filters
            self.results_view.current_page = 1
            
            # Get first page of results
            results, total_count = self.db.search_files(
                limit=self.results_view.page_size,
                offset=0,
                **current_filters
            )
            self.results_view.load_results(results, total_count)
            
            star_text = "⭐" * min_rating
            self.window.update_status(f"Mostrando archivos con {min_rating}+ estrellas ({star_text}) - {total_count:,} resultados")
        except Exception as e:
            QMessageBox.warning(self.window, "Error", f"Error applying star filter:\n{str(e)}")
    
    def on_filters_changed(self, filters: dict):
        """
        Maneja los cambios de filtros desde la barra lateral derecha.
        """
        try:
            # Show search progress
            self.window.show_search_progress("Buscando...")
            
            # Extract filter parameters
            query = filters.get('query', '')
            file_type = filters.get('file_type', 'All Types')
            min_size = filters.get('min_size')
            max_size = filters.get('max_size')
            date_from = filters.get('date_from')
            date_to = filters.get('date_to')
            path_contains = filters.get('path_contains', '')
            
            # Unified advanced search parameters
            universal_search = filters.get('universal_search', '')
            search_filename = filters.get('search_filename', True)
            search_path = filters.get('search_path', True)
            search_comments = filters.get('search_comments', True)
            search_metadata = filters.get('search_metadata', True)
            search_tags = filters.get('search_tags', True)
            universal_case_sensitive = filters.get('universal_case_sensitive', False)
            min_rating = filters.get('min_rating')
            has_comments = filters.get('has_comments')
            tags = filters.get('tags')

            # Get extensions for file type
            extensions = []
            if file_type != 'All Types' and file_type != 'Todos los tipos':
                # Map Spanish UI names to English config keys
                type_mapping = {
                    'Documentos': 'Documents',
                    'Imágenes': 'Images',
                    'Audio': 'Audio',
                    'Video': 'Video',
                    'Comprimidos': 'Archives',
                    'Código': 'Code',
                    'Otros': 'Other'
                }
                config_key = type_mapping.get(file_type, file_type)
                extensions = config.FILE_CATEGORIES.get(config_key, [])

            # Get drive IDs
            drive_ids = []
            drive_text = filters.get('drive', 'All Drives')
            if drive_text != 'All Drives':
                drives = self.db.get_all_drives()
                for drive in drives:
                    if drive['drive_label'] == drive_text:
                        drive_ids = [drive['id']]
                        break

            # Ensure min_size and max_size are ints or None
            min_size_val = min_size if isinstance(min_size, int) and min_size is not None else None
            max_size_val = max_size if isinstance(max_size, int) and max_size is not None else None

            # Ensure date_from and date_to are strings
            date_from_val = date_from if filters.get('date_preset') == 'Custom range' and isinstance(date_from, str) and date_from else ''
            date_to_val = date_to if filters.get('date_preset') == 'Custom range' and isinstance(date_to, str) and date_to else ''

            # Ensure path_contains is a string
            path_contains_val = path_contains if isinstance(path_contains, str) and path_contains else ''

            # Store current filters in results view
            current_filters = {
                'query': '' if universal_search else query,  # Use simple query only if no universal search
                'drive_ids': drive_ids,
                'extensions': extensions,
                'min_size': min_size_val,
                'max_size': max_size_val,
                'date_from': date_from_val,
                'date_to': date_to_val,
                'path_contains': path_contains_val,
                'universal_search': universal_search,
                'search_filename': search_filename,
                'search_path': search_path,
                'search_comments': search_comments,
                'search_metadata': search_metadata,
                'search_tags': search_tags,
                'universal_case_sensitive': universal_case_sensitive,
                'tags': tags,
                'has_comments': has_comments,
                'min_rating': min_rating
            }
            self.results_view.current_filters = current_filters
            self.results_view.current_page = 1  # Reset to first page when filters change
            
            # Get first page of results
            results, total_count = self.db.search_files(
                limit=self.results_view.page_size,
                offset=0,
                **current_filters
            )

            self.results_view.load_results(results, total_count)
            from i18n import _
            self.window.update_status(_("Found {total_count:,} files matching filters").format(total_count=total_count))
            self.window.hide_search_progress()

        except Exception as e:
            self.window.hide_search_progress()
            from i18n import _
            QMessageBox.warning(self.window, _( "Error" ), _( "Error applying filters:\n{error}" ).format(error=str(e)))
    
    def on_filters_reset(self):
        """
        Maneja el reset de filtros desde la barra lateral derecha.
        También limpia la búsqueda del center view.
        """
        try:
            # Clear the search box in results view
            if hasattr(self.results_view, 'search_box'):
                self.results_view.search_box.clear()
            
            # Clear selected drive from left sidebar
            self._last_selected_drive_id = None
            if hasattr(self.left_sidebar, 'drives_tree') and self.left_sidebar.drives_tree:
                self.left_sidebar.drives_tree.clearSelection()
                self.left_sidebar.drives_tree.setCurrentItem(None)
            
            # Reset filters (this will trigger on_filters_changed with empty filters)
            self.on_filters_changed({})
        except Exception as e:
            QMessageBox.warning(self.window, "Error", f"Error resetting filters:\n{str(e)}")
    
    def on_quick_search(self, query: str):
        """
        Maneja la búsqueda rápida desde la vista de resultados.
        """
        try:
            if not query:
                self.load_all_files()
            else:
                # Show search progress
                self.window.show_search_progress("Buscando...")
                
                # Store search filters - use universal search for quick search
                current_filters = {
                    'universal_search': query,
                    'search_filename': True,
                    'search_path': True,
                    'search_comments': True,
                    'search_metadata': True,
                    'search_tags': True
                }
                self.results_view.current_filters = current_filters
                self.results_view.current_page = 1
                
                # Get first page of results
                results, total_count = self.db.search_files(
                    limit=self.results_view.page_size,
                    offset=0,
                    **current_filters
                )
                self.results_view.load_results(results, total_count)
                self.window.update_status(f"Search: '{query}' - {total_count:,} results")
                self.window.hide_search_progress()
        except Exception as e:
            self.window.hide_search_progress()
            QMessageBox.warning(self.window, "Error", f"Error searching:\n{str(e)}")
    
    def on_file_selected(self, file_data: dict):
        """
        Maneja la selección de un archivo en la vista de resultados.
        """
        # Update status with file info
        name = file_data.get('file_name', '')
        is_folder = file_data.get('is_folder', False)
        
        if is_folder:
            self.window.update_status(f"Selected: {name} (Folder)")
        else:
            size = file_data.get('file_size', 0)
            # Handle empty string or invalid size values
            try:
                size_val = int(float(size)) if size else 0
            except (ValueError, TypeError):
                size_val = 0
            from utils.helpers import format_file_size
            self.window.update_status(f"Selected: {name} ({format_file_size(size_val)})")

    def on_page_requested(self, filters, page, page_size):
        """
        Maneja las solicitudes de paginación desde la vista de resultados.
        """
        try:
            # Show search progress
            self.window.show_search_progress(f"Cargando página {page}...")
            
            # Calculate offset
            offset = (page - 1) * page_size
            
            # Check for custom filter types
            filter_type = filters.get('filter_type')
            
            if filter_type == 'root_folders':
                # Handle root folders pagination
                drive_id = filters.get('drive_id')
                if drive_id:
                    drive = self.db.get_drive_by_id(drive_id)
                    if drive:
                        folders = self.db.get_folders_by_drive(drive_id, limit=page_size, offset=offset)
                        root_folders = [f for f in folders if f.get('level', 0) == 0]
                        total_count = self.db.get_folders_count_by_drive(drive_id, max_level=0)
                        
                        drive_letter = drive.get('drive_letter', '').rstrip('\\')
                        results = [
                            {
                                'file_name': f['folder_name'],
                                'file_path': f['folder_path'],
                                'file_size': '',
                                'file_extension': '',
                                'modified_date': '',
                                'drive_label': drive.get('drive_label', ''),
                                'drive_letter': drive_letter,
                                'is_folder': True
                            }
                            for f in root_folders
                        ]
                        
                        self.results_view.load_results(results, total_count)
                        self.results_view.current_page = page
                        self.window.update_status(f"Mostrando página {page} de carpetas raíz")
                        self.window.hide_search_progress()
                        return
            
            elif filter_type == 'folders':
                # Handle all folders pagination
                drives = self.db.get_all_drives()
                total_count = sum(self.db.get_folders_count_by_drive(d['id']) for d in drives)
                
                # Get paginated folders from all drives combined
                all_folders = []
                remaining = page_size
                current_offset = offset
                
                for drive in drives:
                    if remaining <= 0:
                        break
                    
                    # Calculate how many folders to get from this drive
                    drive_folder_count = self.db.get_folders_count_by_drive(drive['id'])
                    
                    if current_offset >= drive_folder_count:
                        # Skip this drive entirely
                        current_offset -= drive_folder_count
                        continue
                    
                    # Get folders from this drive
                    folders_to_get = min(remaining, drive_folder_count - current_offset)
                    if folders_to_get > 0:
                        folders = self.db.get_folders_by_drive(drive['id'], limit=folders_to_get, offset=current_offset)
                        for f in folders:
                            f = dict(f)
                            f['drive_id'] = drive['id']
                            all_folders.append(f)
                        remaining -= len(folders)
                        current_offset = 0  # Reset offset for next drive
                
                results = []
                for f in all_folders:
                    drive = self.db.get_drive_by_id(f['drive_id'])
                    results.append({
                        'file_name': f['folder_name'],
                        'file_path': f['folder_path'],
                        'file_size': '',
                        'file_extension': '',
                        'modified_date': '',
                        'drive_label': drive.get('drive_label', '') if drive else '',
                        'drive_letter': drive.get('drive_letter', '') if drive else '',
                        'is_folder': True
                    })
                
                self.results_view.load_results(results, total_count)
                self.results_view.current_page = page
                self.window.update_status(f"Mostrando página {page} de todas las carpetas")
                self.window.hide_search_progress()
                return
            
            # Default: Apply current filters with pagination using search_files
            results, total_count = self.db.search_files(
                limit=page_size,
                offset=offset,
                **filters
            )
            
            self.results_view.load_results(results, total_count)
            self.results_view.current_page = page
            self.window.update_status(f"Mostrando página {page} ({len(results)} de {total_count:,} resultados)")
            self.window.hide_search_progress()
            
        except Exception as e:
            self.window.hide_search_progress()
            QMessageBox.warning(self.window, "Error", f"Error al cargar página:\n{str(e)}")

    def on_drive_added(self, drive):
        """
        Recarga los drives en la barra lateral tras añadir uno nuevo.
        """
        drives = self.db.get_all_drives()
        stats = self.db.get_file_statistics()
        
        if hasattr(self.left_sidebar, 'load_drives'):
            self.left_sidebar.load_drives(drives)
        
        self.window.update_stats(
            files_count=stats.get('total_files', 0),
            drives_count=len(drives),
            total_size=stats.get('total_size', 0)
        )
        
        # Reload statistics panel if loaded
        self.window.reload_statistics()

    def on_stats_updated(self):
        """
        Actualiza las estadísticas en la barra inferior cuando cambian los datos.
        """
        drives = self.db.get_all_drives()
        stats = self.db.get_file_statistics()
        self.window.update_stats(
            files_count=stats.get('total_files', 0),
            drives_count=len(drives),
            total_size=stats.get('total_size', 0)
        )

    def on_drive_removed(self):
        """
        Recarga todos los componentes de la UI tras eliminar un drive.
        """
        # Get updated drives and statistics
        drives = self.db.get_all_drives()
        stats = self.db.get_file_statistics()
        
        # Update UI components
        if hasattr(self.left_sidebar, 'load_drives'):
            self.left_sidebar.load_drives(drives)
        if hasattr(self.right_sidebar, 'load_drives'):
            self.right_sidebar.load_drives(drives)
        
        self.window.update_stats(
            files_count=stats.get('total_files', 0),
            drives_count=len(drives),
            total_size=stats.get('total_size', 0)
        )
        
        # Reload files or clear results if no drives left
        if stats.get('total_files', 0) > 0:
            self.load_all_files()
        else:
            self.results_view.load_results([])
            self.window.update_status("Ready - Add a drive to begin")
        
        # Reload statistics panel if loaded
        self.window.reload_statistics()
    
    def run(self):
        """
        Ejecuta el bucle principal de la aplicación.
        """
        print("Almacén Digital - Starting GUI application...")
        self.window.show()
        print("Main window displayed. The application should now be visible.")
        print("If you don't see the window, try running this command directly in a Windows terminal:")
        print("  python main.py")
        print("Or double-click run.bat")
        print("")
        
        result = self.app.exec()
        print(f"Application closed with exit code {result}")
        logging.info(f"Application exited with code {result}")
        return result
    
    def cleanup(self):
        """
        Libera recursos antes de salir.
        """
        # Perform sync on shutdown if enabled
        self.sync_on_shutdown()
        
        if self.db:
            self.db.close()
    
    def sync_on_startup(self):
        """Perform database sync on application startup"""
        if not config.SYNC_ENABLED or not config.SYNC_ON_STARTUP:
            return
        
        if not config.SYNC_BACKUP_PATH:
            logging.warning("Sync enabled but no backup path configured")
            return
        
        # Perform sync asynchronously to avoid blocking UI
        from PyQt6.QtCore import QTimer
        def do_sync():
            try:
                from pathlib import Path
                backup_path = Path(config.SYNC_BACKUP_PATH)
                
                success, message = self.sync_manager.auto_sync(backup_path, config.SYNC_DIRECTION)
                
                if success:
                    logging.info(f"Startup sync successful: {message}")
                    # Reload database if synced from backup
                    if "from backup" in message.lower():
                        self.db.close()
                        self.db = DatabaseManager()
                        self.results_view.db = self.db
                        self.manage_view.db = self.db
                        self.load_initial_data()
                else:
                    logging.warning(f"Startup sync: {message}")
                    
            except Exception as e:
                logging.error(f"Error during startup sync: {e}")
        
        QTimer.singleShot(200, do_sync)  # Start sync after UI is responsive
    
    def sync_on_shutdown(self):
        """Perform database sync on application shutdown"""
        if not config.SYNC_ENABLED or not config.SYNC_ON_SHUTDOWN:
            return
        
        if not config.SYNC_BACKUP_PATH:
            return
        
        try:
            from pathlib import Path
            backup_path = Path(config.SYNC_BACKUP_PATH)
            
            # Increment version before syncing out
            self.db.increment_version()
            
            success, message = self.sync_manager.auto_sync(backup_path, config.SYNC_DIRECTION)
            
            if success:
                logging.info(f"Shutdown sync successful: {message}")
            else:
                logging.warning(f"Shutdown sync: {message}")
                
        except Exception as e:
            logging.error(f"Error during shutdown sync: {e}")





# --- Punto de entrada principal ---
def main():
    """
    Arranca la aplicación principal.
    """
    app = HDDInventoryApp()
    try:
        exit_code = app.run()
    finally:
        app.cleanup()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
