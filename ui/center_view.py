"""
Vista central - Muestra resultados de archivos en tabla, cuadrícula y árbol

Comentarios de desarrollo:
- Este archivo implementa la vista principal para mostrar resultados de búsqueda de archivos.
- Utiliza PyQt6 para la interfaz gráfica.
- Incluye modos de visualización: tabla, cuadrícula y árbol (solo tabla implementada).
- Los métodos principales gestionan la carga de resultados, búsqueda, selección y actualización automática.
- Mantener la separación de lógica de UI y datos.
- Revisar el uso de señales para comunicación con otras vistas/controladores.
- Para mantenimiento: documentar cualquier cambio en la estructura de resultados o señales.
- Consultar el backlog para futuras implementaciones de grid/tree view.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                              QComboBox, QHeaderView, QAbstractItemView, QButtonGroup,
                              QMenu, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QIcon, QPixmap, QPainter
import config
from utils.helpers import format_file_size, format_date, get_file_icon_char, get_available_drives
from ui.file_metadata_dialog import FileMetadataDialog
from i18n import _
import os


class ResultsView(QWidget):
        # --- Comentarios de desarrollo ---
        # Esta clase gestiona la vista central de resultados de archivos.
        # Señales: statistics_requested, file_selected, search_requested.
        # Métodos clave: init_ui, load_results, switch_view, on_search, clear_search.
        # El timer interno actualiza la lista de unidades conectadas cada 10 segundos.
        # Para mantenimiento: revisar la lógica de actualización y señales al modificar la estructura.
    statistics_requested = pyqtSignal(str)  # drive_letter
    """Center view for displaying file results"""
    
    # Signals
    file_selected = pyqtSignal(dict)  # file info
    search_requested = pyqtSignal(str)  # search query
    page_requested = pyqtSignal(dict, int, int)  # filters, page, page_size
    star_filter_changed = pyqtSignal(int)  # minimum star rating (0-5)
    
    def __init__(self, db=None):
        # Inicializa la vista y configura el timer de actualización automática.
        super().__init__()
        self.db = db
        self.current_view = 'table'
        self.current_results = []
        self.connected_drive_letters = set()
        
        # Pagination state
        self.current_page = 1
        self.page_size = 100  # Results per page
        self.total_results = 0
        self.current_filters = {}  # Store current search filters
        
        self.init_ui()
        # Auto-update connected drives every 10 seconds
        self._auto_update_timer = QTimer(self)
        self._auto_update_timer.setInterval(10000)
        self._auto_update_timer.timeout.connect(self._update_connected_drives)
        self._auto_update_timer.start()
        self._update_connected_drives()
    
    def init_ui(self):
        # Construye la interfaz de usuario principal (barra de herramientas, tabla de resultados, info).
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Top toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Results table
        self.results_table = self.create_results_table()
        layout.addWidget(self.results_table)
        
        # Pagination controls
        pagination_bar = self.create_pagination_bar()
        layout.addWidget(pagination_bar)
        
        # Results info bar
        self.results_info = QLabel(_("No results"))
        self.results_info.setObjectName('subHeader')
        layout.addWidget(self.results_info)
    
    def _update_connected_drives(self):
        # Actualiza la lista de letras de unidades conectadas y refresca la vista si hay resultados.
        """Update list of connected drive letters"""
        try:
            drives = get_available_drives()
            self.connected_drive_letters = set()
            for drive in drives:
                letter = drive.get('device', '').replace('/', '\\').split(':')[0].upper()
                if letter:
                    self.connected_drive_letters.add(f"{letter}:")
        except Exception as e:
            print(f"Error updating connected drives: {e}")
        # Refresh display if results are loaded
        if self.current_results:
            self.load_results(self.current_results)
    
    def _create_status_icon(self, is_connected: bool) -> QIcon:
        # Crea un icono circular azul/gris para indicar el estado de conexión de la unidad.
        """Create a blue or grey circle icon for connection status"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        painter = QPainter(pixmap)
        color = QColor(33, 150, 243) if is_connected else QColor(160, 160, 160)
        painter.setBrush(color)
        painter.setPen(QColor(0, 0, 0, 0))
        painter.drawEllipse(2, 2, 12, 12)
        painter.end()
        return QIcon(pixmap)
    
    def create_toolbar(self) -> QWidget:
        # Construye la barra de herramientas superior (búsqueda, orden, estadísticas, modos de vista).
        """Create toolbar with search, view, and statistics options"""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        columns = ['', 'Comments', 'Name', 'Size', 'Type', 'Modified', 'Drive', 'Path']
        
        # Star rating filter
        toolbar_layout.addWidget(QLabel("⭐"))
        self.star_combo = QComboBox()
        self.star_combo.addItem(_("All"), 0)  # All ratings
        self.star_combo.addItem("⭐", 1)     # 1+ stars
        self.star_combo.addItem("⭐⭐", 2)   # 2+ stars
        self.star_combo.addItem("⭐⭐⭐", 3) # 3+ stars
        self.star_combo.addItem("⭐⭐⭐⭐", 4) # 4+ stars
        self.star_combo.addItem("⭐⭐⭐⭐⭐", 5) # 5+ stars
        self.star_combo.setCurrentIndex(0)  # Default to "All"
        self.star_combo.setToolTip(_("Filter by minimum star rating"))
        self.star_combo.currentIndexChanged.connect(self.on_star_filter_changed)
        toolbar_layout.addWidget(self.star_combo)
        
        toolbar_layout.addSpacing(10)
        
        # Search box
        toolbar_layout.addWidget(QLabel("🔍"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(_("Quick search..."))
        self.search_box.returnPressed.connect(self.on_search)
        toolbar_layout.addWidget(self.search_box, 1)

        toolbar_layout.addSpacing(20)
        # Sort options
        toolbar_layout.addWidget(QLabel(_("Sort:")))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([_("Name"), _("Size"), _("Type"), _("Modified Date"), _("Drive")])
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        toolbar_layout.addWidget(self.sort_combo)

        toolbar_layout.addSpacing(20)

        # # Statistics button
        # stats_btn = QPushButton("📊 Estadísticas")
        # stats_btn.setToolTip("Mostrar estadísticas de la unidad seleccionada")
        # stats_btn.clicked.connect(self.show_statistics_for_selected_drive)
        # toolbar_layout.addWidget(stats_btn)

        # toolbar_layout.addSpacing(20)

        # View mode buttons
        toolbar_layout.addWidget(QLabel(_("View:")))

        view_group = QButtonGroup(toolbar)

        self.table_view_btn = QPushButton("≡")
        self.table_view_btn.setCheckable(True)
        self.table_view_btn.setChecked(True)
        self.table_view_btn.setToolTip(_("Table view"))
        self.table_view_btn.setFixedWidth(40)
        self.table_view_btn.clicked.connect(lambda: self.switch_view('table'))
        view_group.addButton(self.table_view_btn)
        toolbar_layout.addWidget(self.table_view_btn)

        # self.grid_view_btn = QPushButton("⊞")
        # self.grid_view_btn.setCheckable(True)
        # self.grid_view_btn.setToolTip("Vista de cuadrícula")
        # self.grid_view_btn.setFixedWidth(40)
        # self.grid_view_btn.clicked.connect(lambda: self.switch_view('grid'))
        # view_group.addButton(self.grid_view_btn)
        # toolbar_layout.addWidget(self.grid_view_btn)

        # self.tree_view_btn = QPushButton("⋮")
        # self.tree_view_btn.setCheckable(True)
        # self.tree_view_btn.setToolTip("Vista de árbol")
        # self.tree_view_btn.setFixedWidth(40)
        # self.tree_view_btn.clicked.connect(lambda: self.switch_view('tree'))
        # view_group.addButton(self.tree_view_btn)
        # toolbar_layout.addWidget(self.tree_view_btn)

        return toolbar
    
    def on_star_filter_changed(self, index):
        """Handle star rating filter change"""
        rating = self.star_combo.itemData(index)
        self.star_filter_changed.emit(rating)

    def create_pagination_bar(self):
        """Create pagination controls bar"""
        from PyQt6.QtWidgets import QHBoxLayout, QWidget
        
        pagination_widget = QWidget()
        layout = QHBoxLayout(pagination_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Previous page button
        self.prev_page_btn = QPushButton("◀ " + _("Previous"))
        self.prev_page_btn.clicked.connect(self.prev_page)
        layout.addWidget(self.prev_page_btn)
        
        # Page info label
        self.page_info_label = QLabel(_("Page") + " 1 " + _("of") + " 1")
        layout.addWidget(self.page_info_label)
        
        # Next page button
        self.next_page_btn = QPushButton(_("Next") + " ▶")
        self.next_page_btn.clicked.connect(self.next_page)
        layout.addWidget(self.next_page_btn)
        
        # Page size selector
        layout.addStretch()
        layout.addWidget(QLabel(_("Results per page:")))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["50", "100", "200", "500"])
        self.page_size_combo.setCurrentText("100")
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_changed)
        layout.addWidget(self.page_size_combo)
        
        # Initially hide pagination controls
        pagination_widget.setVisible(False)
        self.pagination_widget = pagination_widget
        
        return pagination_widget

    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_current_page()
    
    def next_page(self):
        """Go to next page"""
        total_pages = (self.total_results + self.page_size - 1) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self.load_current_page()
    
    def on_page_size_changed(self, size_text):
        """Handle page size change"""
        self.page_size = int(size_text)
        self.current_page = 1
        self.load_current_page()
    
    def load_current_page(self):
        """Load current page of results"""
        offset = (self.current_page - 1) * self.page_size
        self.page_requested.emit(self.current_filters, self.current_page, self.page_size)
    
    def update_pagination_controls(self):
        """Update pagination controls based on current state"""
        total_pages = (self.total_results + self.page_size - 1) // self.page_size
        
        # Update page info
        self.page_info_label.setText(_("Page {current} of {total} ({results:,} results)").format(
            current=self.current_page, 
            total=max(1, total_pages), 
            results=self.total_results
        ))
        
        # Update button states
        self.prev_page_btn.setEnabled(self.current_page > 1)
        self.next_page_btn.setEnabled(self.current_page < total_pages)

    # def show_statistics_for_selected_drive(self):
    #         # Muestra el panel de estadísticas para la unidad seleccionada (emite señal).
    #     """Show statistics panel for the selected drive in the main window"""
    #     if not hasattr(self, 'results_table') or self.results_table is None:
    #         print("Results table not available.")
    #         return
    #     selection_model = self.results_table.selectionModel()
    #     if selection_model is None:
    #         print("No selection model available.")
    #         return
    #     selected_rows = selection_model.selectedRows()
    #     if not selected_rows:
    #         print("No drive selected for statistics.")
    #         return
    #     row = selected_rows[0].row()
    #     item = self.results_table.item(row, 1)
    #     drive_letter = item.text() if item else None
    #     if not drive_letter:
    #         print("No drive letter found for selected row.")
    #         return
    #     # Emit signal to main window to show statistics for this drive
    #     self.statistics_requested.emit(drive_letter)
    
    def create_results_table(self) -> QTableWidget:
            # Crea la tabla de resultados y configura columnas, selección y señales.
        """Create results table widget"""
        table = QTableWidget()
        
        # Set columns
        columns = ['', _('Info'), _('Name'), _('Size'), _('Type'), _('Modified'), _('Drive'), _('Path')]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        # Configure table
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSortingEnabled(True)

        # Set column widths
        header = table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Icon
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Comments
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Name
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Size
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Type
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Modified
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Drive
            header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Path
        table.setColumnWidth(0, 30)  # Icon column
        table.setColumnWidth(1, 30)  # Comments column

        # Connect signals
        table.itemSelectionChanged.connect(self.on_selection_changed)
        table.cellClicked.connect(self.on_cell_clicked)
        
        # Enable context menu
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_file_context_menu)
        
        return table
    
    def on_cell_clicked(self, row: int, column: int):
        """Handle cell clicks, specifically for comments column"""
        if column == 1:  # Comments column
            # Get the file data from the Name column (column 2)
            name_item = self.results_table.item(row, 2)  # Name column
            if name_item:
                file_data = name_item.data(Qt.ItemDataRole.UserRole)
                if file_data:
                    self.edit_file_metadata(file_data)
    
    def load_results(self, results: list, total_count: int = None):
            # Carga los resultados de búsqueda en la tabla y actualiza la barra de información.
        """Load search results into table"""
        
        self.current_results = results
        
        # Handle pagination
        if total_count is not None:
            self.total_results = total_count
            self.update_pagination_controls()
            self.pagination_widget.setVisible(total_count > 0)
        else:
            self.total_results = len(results)
            self.pagination_widget.setVisible(False)
        
        self.results_table.setRowCount(0)
        self.results_table.setSortingEnabled(False)

        for row_idx, file_data in enumerate(results):
            self.results_table.insertRow(row_idx)

            # Icon
            icon = get_file_icon_char(file_data.get('file_extension', ''))
            icon_item = QTableWidgetItem(icon)
            icon_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row_idx, 0, icon_item)

            # Comments (moved to second column)
            has_comments = bool(file_data.get('comments')) or file_data.get('rating', 0) > 0
            comments_item = QTableWidgetItem()
            if has_comments:
                comments_item.setText("💬")  # Comments icon
                comments_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row_idx, 1, comments_item)

            # Name
            name_item = QTableWidgetItem(file_data.get('file_name', ''))
            name_item.setData(Qt.ItemDataRole.UserRole, file_data)
            self.results_table.setItem(row_idx, 2, name_item)

            # Size (robust: default to 0 if not a valid number)
            size = file_data.get('file_size', 0)
            try:
                size_val = int(float(size))
            except (TypeError, ValueError):
                size_val = 0
            size_item = QTableWidgetItem(format_file_size(size_val))
            size_item.setData(Qt.ItemDataRole.UserRole, size_val)  # Store for sorting
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.results_table.setItem(row_idx, 3, size_item)

            # Type
            ext = file_data.get('file_extension', '').upper()
            type_item = QTableWidgetItem(ext)
            self.results_table.setItem(row_idx, 4, type_item)

            # Modified date
            modified = file_data.get('modified_date', '')
            if modified:
                try:
                    modified = format_date(modified)
                except:  # Consider catching specific exceptions instead of bare except
                    pass
            modified_item = QTableWidgetItem(modified)
            self.results_table.setItem(row_idx, 5, modified_item)

            # Drive
            drive = file_data.get('drive_label', file_data.get('drive_letter', ''))
            drive_item = QTableWidgetItem(drive)
            self.results_table.setItem(row_idx, 6, drive_item)

            # Path
            path = file_data.get('file_path', '')
            path_item = QTableWidgetItem(path)
            path_item.setToolTip(path)  # Show full path on hover
            self.results_table.setItem(row_idx, 7, path_item)

        self.results_table.setSortingEnabled(True)

        count = len(results)
        def safe_size(f):
            try:
                return int(float(f.get('file_size', 0)))
            except (TypeError, ValueError):
                return 0
        total_size = sum(safe_size(f) for f in results)
        
        # Update results info with pagination info if applicable
        if total_count is not None and total_count > len(results):
            start_item = (self.current_page - 1) * self.page_size + 1
            end_item = min(self.current_page * self.page_size, total_count)
            self.results_info.setText(
                _("Showing {start:,}-{end:,} of {total:,} files | Total size: {size}").format(
                    start=start_item, end=end_item, total=total_count, size=format_file_size(total_size)
                )
            )
        else:
            self.results_info.setText(
                _("Found {count:,} files | Total size: {size}").format(
                    count=count, size=format_file_size(total_size)
                )
            )
    
    def on_search(self):
            # Maneja la búsqueda rápida y emite la señal correspondiente.
        """Handle search request"""
        query = self.search_box.text()
        self.search_requested.emit(query)
    
    def clear_search(self):
            # Limpia la caja de búsqueda y recarga los resultados.
        """Clear search box"""
        self.search_box.clear()
        self.on_search()
    
    def on_selection_changed(self):
            # Maneja el cambio de selección en la tabla y emite la señal con los datos del archivo.
        """Handle selection change"""
        selected = self.results_table.selectedItems()
        if selected:
            # Get file data from Name column of selected row
            row = selected[0].row()
            name_item = self.results_table.item(row, 2)  # Name column
            if name_item:
                file_data = name_item.data(Qt.ItemDataRole.UserRole)
                if file_data:
                    self.file_selected.emit(file_data)
    
    def show_file_context_menu(self, pos):
            # Muestra el menú contextual para abrir archivo o carpeta.
        """Show context menu for selected file"""
        # Get selected row
        selected_items = self.results_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        name_item = self.results_table.item(row, 2)  # Name column
        if not name_item:
            return
        
        file_data = name_item.data(Qt.ItemDataRole.UserRole)
        if not file_data:
            return
        
        # Create context menu
        menu = QMenu(self)
        is_folder = file_data.get('is_folder', False)
        
        # Add edit metadata action
        action_edit_metadata = menu.addAction(_("Edit Metadata"))
        menu.addSeparator()  # Add separator before file operations
        
        if is_folder:
            action_open_containing = menu.addAction(_("Open containing folder"))
        else:
            action_open_file = menu.addAction(_("Open file"))
            action_open_containing = menu.addAction(_("Open containing folder"))
        
        # Get global position for menu
        global_pos = self.results_table.viewport().mapToGlobal(pos)
        action = menu.exec(global_pos)
        
        if action == action_edit_metadata:
            self.edit_file_metadata(file_data)
        elif action == action_open_containing:
            self.open_folder(file_data)
        elif not is_folder and action == action_open_file:
            self.open_file(file_data)
    
    def open_file(self, file_data):
            # Abre el archivo seleccionado usando el programa predeterminado.
        """Open the selected file with default application"""
        file_path = file_data.get('file_path', '')
        drive_letter = file_data.get('drive_letter', '') or ''
        
        if not drive_letter:
            QMessageBox.warning(self, _("Error"), _("Could not determine drive letter."))
            return
        
        # Normalize drive_letter to have exactly one backslash
        drive_letter = str(drive_letter).strip()
        if not drive_letter.endswith(':'):
            drive_letter += ':'
        drive_letter += '\\'
        
        # Normalize file_path to use single backslashes
        file_path = file_path.replace('\\\\', '\\').lstrip('\\')
        
        # Construct full path
        if os.path.isabs(file_path):
            full_path = file_path
        else:
            full_path = os.path.join(drive_letter, file_path)
        
        try:
            # Check if the drive is accessible
            try:
                drive_exists = os.path.exists(drive_letter)
            except:
                drive_exists = False
            if not drive_exists:
                QMessageBox.warning(self, _("Error"), _("Drive {drive} is not connected or accessible.").format(drive=drive_letter.rstrip('\\')))
                return
            # Check if the file exists
            try:
                file_exists = os.path.exists(full_path)
            except:
                file_exists = False
            if not file_exists:
                QMessageBox.warning(self, _("Error"), _("File does not exist or is not accessible: {path}").format(path=full_path))
                return
            os.startfile(full_path)
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Could not open file: {error}").format(error=e))
    
    def open_folder(self, file_data):
            # Abre la carpeta contenedora del archivo seleccionado.
        """Open the folder containing the selected file"""
        file_path = file_data.get('file_path', '')
        drive_letter = file_data.get('drive_letter', '') or ''
        
        if not drive_letter:
            QMessageBox.warning(self, _("Error"), _("Could not determine drive letter."))
            return
        
        # Normalize drive_letter to have exactly one backslash
        drive_letter = str(drive_letter).strip()
        if not drive_letter.endswith(':'):
            drive_letter += ':'
        drive_letter += '\\'
        
        # Normalize file_path to use single backslashes
        file_path = file_path.replace('\\\\', '\\').lstrip('\\')
        
        # Construct full path
        if os.path.isabs(file_path):
            full_path = file_path
        else:
            full_path = os.path.join(drive_letter, file_path)
        
        # Get the containing folder
        folder_path = os.path.dirname(full_path)
        if not folder_path:
            folder_path = drive_letter
        
        try:
            # Check if the drive is accessible
            try:
                drive_exists = os.path.exists(drive_letter)
            except:
                drive_exists = False
            if not drive_exists:
                QMessageBox.warning(self, _("Error"), _("Drive {drive} is not connected or accessible.").format(drive=drive_letter.rstrip('\\')))
                return
            # Check if the folder exists
            try:
                folder_exists = os.path.exists(folder_path)
            except:
                folder_exists = False
            if not folder_exists:
                QMessageBox.warning(self, _("Error"), _("Folder does not exist or is not accessible: {path}").format(path=folder_path))
                return
            os.startfile(folder_path)
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Could not open folder: {error}").format(error=e))
    
    def on_sort_changed(self, sort_by: str):
            # Cambia el orden de la tabla según la opción seleccionada.
        """Handle sort option change"""
        column_map = {
            _("Name"): 2,  # Name column
            _("Size"): 3,  # Size column
            _("Type"): 4,    # Type column
            _("Modified Date"): 5,  # Modified column
            _("Drive"): 6   # Drive column
        }
        
        column = column_map.get(sort_by, 2)
        self.results_table.sortItems(column, Qt.SortOrder.AscendingOrder)
    
    def edit_file_metadata(self, file_data):
        """Open metadata editing dialog for the selected file"""
        try:
            # Create and show the metadata dialog
            dialog = FileMetadataDialog(file_data, self.db, self)
            if dialog.exec():
                # If dialog was accepted (metadata was saved), refresh the current results
                # to show updated metadata in the table
                self.search_requested.emit(self.search_box.text() if self.search_box.text() else "")
        except Exception as e:
            QMessageBox.warning(self, _("Error"), _("Could not open metadata dialog: {error}").format(error=e))
    
    def switch_view(self, view_type: str):
            # Cambia el modo de visualización (solo indicador, grid/tree pendiente de implementación).
        """Switch between view modes"""
        self.current_view = view_type
        
        # Implement grid and tree views (see design docs or backlog)
        # For now, just update the current view indicator
        if view_type == 'grid':
            self.results_info.setText(f"{self.results_info.text()} | {_('Grid view (coming soon)')}")
        elif view_type == 'tree':
            self.results_info.setText(f"{self.results_info.text()} | {_('Tree view (coming soon)')}")
    
    def clear_results(self):
            # Limpia todos los resultados de la tabla y la barra de información.
        """Clear all results"""
        self.results_table.setRowCount(0)
        self.current_results = []
        self.results_info.setText(_("No results"))

