# --- Comentarios de desarrollo ---
# Este archivo implementa la barra lateral derecha de la aplicación.
# Muestra los filtros de búsqueda y metadatos.
# Utiliza PyQt6 para la interfaz gráfica.
# Señales: filters_changed.
# Métodos clave: init_ui, create_text_search_section, create_attributes_section, create_date_section, create_location_section, create_advanced_section.
# Para mantenimiento: actualizar los textos y opciones según la evolución de la UI.
"""Barra lateral derecha - Filtros de búsqueda y metadatos"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox,
                              QPushButton, QScrollArea, QFrame, QCheckBox,
                              QHBoxLayout, QSlider, QDateEdit, QGroupBox, QTabWidget, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTimer
import config
from i18n import _

def create_right_sidebar() -> QWidget:
    # For compatibility with refactored main_window.py
    return FiltersSidebar()

class FiltersSidebar(QWidget):
    def set_drive_filter(self, drive_label: str):
        """Set the drive filter combo to the given drive label and apply filters."""
        try:
            if not hasattr(self, 'drive_combo') or self.drive_combo is None:
                return
            idx = self.drive_combo.findText(drive_label)
            if idx != -1:
                self.drive_combo.setCurrentIndex(idx)
            else:
                # If not found, add it and select
                self.drive_combo.addItem(drive_label)
                self.drive_combo.setCurrentIndex(self.drive_combo.count() - 1)
            self.apply_filters()
        except RuntimeError:
            # Widget has been deleted
            pass
    """Right sidebar for search filters and metadata"""
    filters_changed = pyqtSignal(dict)  # Emits filter parameters
    filters_reset = pyqtSignal()  # Emits when filters are reset

    def __init__(self):
        """Initialize the FiltersSidebar UI and connect signals."""
        super().__init__()
        self.init_ui()

    def on_auto_apply_toggled(self, state: int):
        """Toggle auto-apply behavior and update apply button state."""
        enabled = state == Qt.CheckState.Checked
        self.apply_btn.setEnabled(not enabled)
        if enabled:
            # Apply immediately when enabling auto-apply
            self.apply_filters()

    def init_ui(self):
        """Set up all widgets and layout for the sidebar."""
        layout = QVBoxLayout(self)

        # Action buttons at the top
        button_layout = QHBoxLayout()
        self.apply_btn = QPushButton(_("Apply Filters"))
        self.apply_btn.clicked.connect(self.apply_filters)
        button_layout.addWidget(self.apply_btn)
        self.auto_apply_check = QCheckBox(_("Apply automatically"))
        self.auto_apply_check.setChecked(True)
        self.auto_apply_check.stateChanged.connect(self.on_auto_apply_toggled)
        button_layout.addWidget(self.auto_apply_check)
        self.reset_btn = QPushButton(_("Reset"))
        self.reset_btn.clicked.connect(self.reset_filters)
        button_layout.addWidget(self.reset_btn)
        layout.addLayout(button_layout)

        # Create tabbed interface
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_search_tab(), _("Search"))
        self.tabs.addTab(self.create_filters_tab(), _("Filters"))
        self.tabs.addTab(self.create_advanced_tab(), _("Advanced"))
        layout.addWidget(self.tabs)

        # Debounce timer for auto-apply (avoid firing search on every keystroke)
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(200)
        self._debounce_timer.timeout.connect(self.apply_filters)

        # Connect all filter widgets to auto-apply handler
        self.connect_filter_signals()

        # Set apply button state based on auto-apply
        self.apply_btn.setEnabled(not self.auto_apply_check.isChecked())

    def connect_filter_signals(self):
        """Connect all filter widgets to the auto-apply handler"""
        # Search tab
        if hasattr(self, 'universal_search') and self.universal_search:
            self.universal_search.textChanged.connect(self.on_filter_changed)
        if hasattr(self, 'universal_case_sensitive') and self.universal_case_sensitive:
            self.universal_case_sensitive.stateChanged.connect(self.on_filter_changed)
        if hasattr(self, 'search_filename') and self.search_filename:
            self.search_filename.stateChanged.connect(self.on_filter_changed)
        if hasattr(self, 'search_path') and self.search_path:
            self.search_path.stateChanged.connect(self.on_filter_changed)
        if hasattr(self, 'search_comments') and self.search_comments:
            self.search_comments.stateChanged.connect(self.on_filter_changed)
        if hasattr(self, 'search_metadata') and self.search_metadata:
            self.search_metadata.stateChanged.connect(self.on_filter_changed)
        if hasattr(self, 'search_tags') and self.search_tags:
            self.search_tags.stateChanged.connect(self.on_filter_changed)

        # Filters tab
        if hasattr(self, 'type_combo') and self.type_combo:
            self.type_combo.currentIndexChanged.connect(self.on_filter_changed)
        if hasattr(self, 'size_preset') and self.size_preset:
            self.size_preset.currentTextChanged.connect(self.on_filter_changed)
        if hasattr(self, 'drive_combo') and self.drive_combo:
            self.drive_combo.currentIndexChanged.connect(self.on_filter_changed)
        if hasattr(self, 'path_input') and self.path_input:
            self.path_input.textChanged.connect(self.on_filter_changed)

        # Advanced tab
        if hasattr(self, 'date_preset') and self.date_preset:
            self.date_preset.currentIndexChanged.connect(self.on_filter_changed)
        if hasattr(self, 'date_from') and self.date_from:
            self.date_from.dateChanged.connect(self.on_filter_changed)
        if hasattr(self, 'date_to') and self.date_to:
            self.date_to.dateChanged.connect(self.on_filter_changed)
        if hasattr(self, 'min_rating_combo') and self.min_rating_combo:
            self.min_rating_combo.currentIndexChanged.connect(self.on_filter_changed)
        if hasattr(self, 'has_comments_check') and self.has_comments_check:
            self.has_comments_check.stateChanged.connect(self.on_filter_changed)
        if hasattr(self, 'tags_input') and self.tags_input:
            self.tags_input.textChanged.connect(self.on_filter_changed)

    def on_filter_changed(self, *args):
        """Called when any filter widget changes; apply immediately for search text, debounce for others"""
        sender = self.sender()

        # For universal search, use a typing delay
        if hasattr(self, 'universal_search') and self.universal_search and sender == self.universal_search:
            # Stop any existing timer
            if hasattr(self, '_search_timer') and self._search_timer.isActive():
                self._search_timer.stop()
            # Start a new timer with 500ms delay
            if not hasattr(self, '_search_timer'):
                self._search_timer = QTimer(self)
                self._search_timer.setSingleShot(True)
                self._search_timer.timeout.connect(self.apply_filters)
            self._search_timer.start(500)
        # Use debounce for other changes
        elif self.auto_apply_check.isChecked():
            # restart debounce timer
            self._debounce_timer.start()
    
    def create_search_tab(self) -> QWidget:
        """Create the search tab with universal search and content filters"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Universal search
        layout.addWidget(QLabel("<b>" + _("Search everywhere:") + "</b>"))
        self.universal_search = QLineEdit()
        self.universal_search.setPlaceholderText(_("Search everywhere:"))
        layout.addWidget(self.universal_search)

        # Case sensitivity
        self.universal_case_sensitive = QCheckBox(_("Match case"))
        layout.addWidget(self.universal_case_sensitive)

        # Content type filters
        layout.addWidget(QLabel("<b>" + _("Search in:") + "</b>"))
        self.search_filename = QCheckBox(_("Filename"))
        self.search_filename.setChecked(True)
        layout.addWidget(self.search_filename)

        self.search_path = QCheckBox(_("File path"))
        self.search_path.setChecked(True)
        layout.addWidget(self.search_path)

        self.search_comments = QCheckBox(_("Comments"))
        self.search_comments.setChecked(True)
        layout.addWidget(self.search_comments)

        self.search_metadata = QCheckBox(_("Custom metadata"))
        self.search_metadata.setChecked(True)
        layout.addWidget(self.search_metadata)

        self.search_tags = QCheckBox(_("Tags"))
        self.search_tags.setChecked(True)
        layout.addWidget(self.search_tags)

        layout.addStretch()
        return widget

    def create_filters_tab(self) -> QWidget:
        """Create the filters tab with basic file filters"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # File type
        layout.addWidget(QLabel("<b>" + _("File type:") + "</b>"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            _("All types"),
            _("Documents"),
            _("Images"),
            _("Audio"),
            _("Video"),
            _("Archives"),
            _("Code"),
            _("Other")
        ])
        layout.addWidget(self.type_combo)

        # Size filter
        layout.addWidget(QLabel("<b>" + _("Size:") + "</b>"))
        self.size_preset = QComboBox()
        self.size_preset.addItems([
            _("Any size"),
            "< 1 MB",
            "1-10 MB",
            "10-100 MB",
            "100 MB - 1 GB",
            "> 1 GB"
        ])
        layout.addWidget(self.size_preset)

        # Location filters
        layout.addWidget(QLabel("<b>" + _("Location:") + "</b>"))
        layout.addWidget(QLabel(_("Drive:")))
        self.drive_combo = QComboBox()
        self.drive_combo.addItem(_("All drives"))
        layout.addWidget(self.drive_combo)

        layout.addWidget(QLabel(_("Path contains:")))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("ex: /documents/")
        layout.addWidget(self.path_input)

        layout.addStretch()
        return widget

    def create_advanced_tab(self) -> QWidget:
        """Create the advanced tab with date and metadata filters"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Date filters
        layout.addWidget(QLabel("<b>" + _("Modification date:") + "</b>"))
        self.date_preset = QComboBox()
        self.date_preset.addItems([
            _("Any date"),
            _("Today"),
            _("Last 7 days"),
            _("Last 30 days"),
            _("Last year"),
            _("Custom range")
        ])
        layout.addWidget(self.date_preset)

        # Custom date range (shown when "Custom range" is selected)
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel(_("From:")))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addYears(-1))
        date_layout.addWidget(self.date_from)

        date_layout.addWidget(QLabel(_("To:")))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        date_layout.addWidget(self.date_to)
        layout.addLayout(date_layout)

        # Metadata filters
        layout.addWidget(QLabel("<b>" + _("Metadata:") + "</b>"))
        layout.addWidget(QLabel(_("Minimum rating:")))
        self.min_rating_combo = QComboBox()
        self.min_rating_combo.addItems([
            _("Any rating"),
            "★☆☆☆☆ (1+)",
            "★★☆☆☆ (2+)",
            "★★★☆☆ (3+)",
            "★★★★☆ (4+)",
            "★★★★★ (5)"
        ])
        layout.addWidget(self.min_rating_combo)

        self.has_comments_check = QCheckBox(_("Only files with comments"))
        layout.addWidget(self.has_comments_check)

        layout.addWidget(QLabel(_("Tags:")))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("tag1, tag2")
        layout.addWidget(self.tags_input)

        layout.addStretch()
        return widget
    
    def get_size_limits_from_preset(self):
        """Get min/max size from the current preset"""
        if not hasattr(self, 'size_preset') or not self.size_preset:
            return (None, None)
        preset = self.size_preset.currentText()
        presets = {
            "< 1 MB": (None, 1024*1024),
            "1-10 MB": (1024*1024, 10*1024*1024),
            "10-100 MB": (10*1024*1024, 100*1024*1024),
            "100 MB - 1 GB": (100*1024*1024, 1024*1024*1024),
            "> 1 GB": (1024*1024*1024, None)
        }
        return presets.get(preset, (None, None))

    def apply_filters(self):
        """Collect and emit filter parameters"""
        try:
            # If debounce timer is running, stop it before applying
            self._debounce_timer.stop()
        except Exception:
            pass

        try:
            # Get size limits from preset
            min_size, max_size = self.get_size_limits_from_preset()

            filters = {
                'query': '',  # No simple search anymore
                'universal_search': self.universal_search.text() if hasattr(self, 'universal_search') and self.universal_search else '',
                'case_sensitive': False,  # No simple search case sensitivity
                'use_regex': False,  # No regex option
                'universal_case_sensitive': self.universal_case_sensitive.isChecked() if hasattr(self, 'universal_case_sensitive') and self.universal_case_sensitive else False,
                'search_filename': self.search_filename.isChecked() if hasattr(self, 'search_filename') and self.search_filename else True,
                'search_path': self.search_path.isChecked() if hasattr(self, 'search_path') and self.search_path else True,
                'search_comments': self.search_comments.isChecked() if hasattr(self, 'search_comments') and self.search_comments else True,
                'search_metadata': self.search_metadata.isChecked() if hasattr(self, 'search_metadata') and self.search_metadata else True,
                'search_tags': self.search_tags.isChecked() if hasattr(self, 'search_tags') and self.search_tags else True,
                'file_type': self.type_combo.currentText() if hasattr(self, 'type_combo') and self.type_combo else 'Todos los tipos',
                'min_size': min_size,
                'max_size': max_size,
                'date_preset': self.date_preset.currentText() if hasattr(self, 'date_preset') and self.date_preset else 'Cualquier fecha',
                'date_from': self.date_from.date().toString(Qt.DateFormat.ISODate) if hasattr(self, 'date_from') and self.date_from else QDate.currentDate().addYears(-1).toString(Qt.DateFormat.ISODate),
                'date_to': self.date_to.date().toString(Qt.DateFormat.ISODate) if hasattr(self, 'date_to') and self.date_to else QDate.currentDate().toString(Qt.DateFormat.ISODate),
                'drive': self.drive_combo.currentText() if hasattr(self, 'drive_combo') and self.drive_combo else 'Todas las unidades',
                'path_contains': self.path_input.text() if hasattr(self, 'path_input') and self.path_input else '',
                'min_rating': self.min_rating_combo.currentIndex() if hasattr(self, 'min_rating_combo') and self.min_rating_combo and self.min_rating_combo.currentIndex() > 0 else None,
                'has_comments': True if hasattr(self, 'has_comments_check') and self.has_comments_check and self.has_comments_check.isChecked() else None,
                'tags': [tag.strip() for tag in self.tags_input.text().split(',') if tag.strip()] if hasattr(self, 'tags_input') and self.tags_input else []
            }
            self.filters_changed.emit(filters)
        except RuntimeError:
            # Widgets have been deleted, skip applying filters
            pass
    
    def reset_filters(self):
        """Reset all filters to default"""
        try:
            if hasattr(self, 'universal_search') and self.universal_search:
                self.universal_search.clear()
            if hasattr(self, 'universal_case_sensitive') and self.universal_case_sensitive:
                self.universal_case_sensitive.setChecked(False)
            if hasattr(self, 'search_filename') and self.search_filename:
                self.search_filename.setChecked(True)
            if hasattr(self, 'search_path') and self.search_path:
                self.search_path.setChecked(True)
            if hasattr(self, 'search_comments') and self.search_comments:
                self.search_comments.setChecked(True)
            if hasattr(self, 'search_metadata') and self.search_metadata:
                self.search_metadata.setChecked(True)
            if hasattr(self, 'search_tags') and self.search_tags:
                self.search_tags.setChecked(True)
            if hasattr(self, 'type_combo') and self.type_combo:
                self.type_combo.setCurrentIndex(0)
            if hasattr(self, 'size_preset') and self.size_preset:
                self.size_preset.setCurrentIndex(0)
            if hasattr(self, 'drive_combo') and self.drive_combo:
                self.drive_combo.setCurrentIndex(0)
            if hasattr(self, 'path_input') and self.path_input:
                self.path_input.clear()
            if hasattr(self, 'date_preset') and self.date_preset:
                self.date_preset.setCurrentIndex(0)
            if hasattr(self, 'min_rating_combo') and self.min_rating_combo:
                self.min_rating_combo.setCurrentIndex(0)
            if hasattr(self, 'has_comments_check') and self.has_comments_check:
                self.has_comments_check.setChecked(False)
            if hasattr(self, 'tags_input') and self.tags_input:
                self.tags_input.clear()
            self.apply_filters()
        except RuntimeError:
            # Widgets have been deleted, skip reset
            pass
        
        # Emit signal that filters have been reset
        self.filters_reset.emit()
    
    def load_drives(self, drives: list):
        """Load drives into combo box. Safe against missing drive_combo."""
        try:
            if not hasattr(self, 'drive_combo') or self.drive_combo is None:
                import logging
                logging.warning("FiltersSidebar: drive_combo not initialized.")
                return
            current_text = self.drive_combo.currentText()
            self.drive_combo.clear()
            self.drive_combo.addItem("All Drives")
            for drive in drives:
                label = drive.get('drive_label', 'Unknown')
                self.drive_combo.addItem(label, drive['id'])
            index = self.drive_combo.findText(current_text)
            if index >= 0:
                self.drive_combo.setCurrentIndex(index)
        except RuntimeError:
            # Widget has been deleted
            pass
