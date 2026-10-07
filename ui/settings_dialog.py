"""
Diálogo general de configuración de la aplicación.
Permite configurar sincronización, interfaz y otras opciones.
"""

import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QCheckBox, QRadioButton,
    QButtonGroup, QFileDialog, QMessageBox, QSpinBox, QGroupBox,
    QComboBox, QFormLayout, QProgressBar
)
from PyQt6.QtCore import Qt, QThread
import config
from i18n import _


class SettingsDialog(QDialog):
    """Diálogo general de configuración con múltiples pestañas"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Almacén Digital Settings"))
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout(self)

        # Tab widget
        self.tab_widget = QTabWidget()

        # Sync tab
        self.sync_tab = self.create_sync_tab()
        self.tab_widget.addTab(self.sync_tab, _("🔄 Synchronization"))

        # UI tab
        self.ui_tab = self.create_ui_tab()
        self.tab_widget.addTab(self.ui_tab, _("🎨 Interface"))

        # Scan tab
        self.scan_tab = self.create_scan_tab()
        self.tab_widget.addTab(self.scan_tab, _("🔍 Scanning"))

        # Search tab
        self.search_tab = self.create_search_tab()
        self.tab_widget.addTab(self.search_tab, _("🔎 Search"))

        # Language tab
        self.language_tab = self.create_language_tab()
        self.tab_widget.addTab(self.language_tab, _("🌐 Language"))

        # Export tab
        self.export_tab = self.create_export_tab()
        self.tab_widget.addTab(self.export_tab, _("📤 Export"))

        # Initialize export worker variables
        self.export_thread = None
        self.export_worker = None

        layout.addWidget(self.tab_widget)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton(_("Save"))
        save_btn.clicked.connect(self.save_settings)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton(_("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Load settings after all UI elements are created
        self.load_settings()

    def create_sync_tab(self):
        """Crea la pestaña de sincronización"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Enable sync checkbox
        self.enable_sync_cb = QCheckBox(_("Enable automatic synchronization"))
        self.enable_sync_cb.stateChanged.connect(self.on_enable_sync_changed)
        layout.addWidget(self.enable_sync_cb)

        # Backup path group
        path_group = QGroupBox(_("Backup Location"))
        path_layout = QVBoxLayout()

        path_info = QLabel(
            _("Specify the path to the database backup file.\n"
            "This file should be in a synchronized folder (Google Drive, OneDrive, etc.)")
        )
        path_info.setWordWrap(True)
        path_layout.addWidget(path_info)

        path_input_layout = QHBoxLayout()
        self.backup_path_edit = QLineEdit()
        path_input_layout.addWidget(self.backup_path_edit)

        browse_btn = QPushButton(_("Browse..."))
        browse_btn.clicked.connect(self.browse_backup_path)
        path_input_layout.addWidget(browse_btn)

        path_layout.addLayout(path_input_layout)
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        # Direction group
        direction_group = QGroupBox(_("Synchronization Direction"))
        direction_layout = QVBoxLayout()

        self.sync_direction_group = QButtonGroup()

        self.bidirectional_rb = QRadioButton(_("Bidirectional (synchronize in both directions)"))
        self.sync_direction_group.addButton(self.bidirectional_rb, 0)

        self.from_backup_rb = QRadioButton(_("From backup (download changes from backup)"))
        self.sync_direction_group.addButton(self.from_backup_rb, 1)

        self.to_backup_rb = QRadioButton(_("To backup (upload changes to backup)"))
        self.sync_direction_group.addButton(self.to_backup_rb, 2)

        direction_layout.addWidget(self.bidirectional_rb)
        direction_layout.addWidget(self.from_backup_rb)
        direction_layout.addWidget(self.to_backup_rb)

        direction_group.setLayout(direction_layout)
        layout.addWidget(direction_group)

        # Timing options
        timing_group = QGroupBox(_("Synchronization Timing"))
        timing_layout = QVBoxLayout()

        self.sync_on_startup_cb = QCheckBox(_("On application startup"))
        timing_layout.addWidget(self.sync_on_startup_cb)

        self.sync_on_shutdown_cb = QCheckBox(_("On application shutdown"))
        timing_layout.addWidget(self.sync_on_shutdown_cb)

        timing_group.setLayout(timing_layout)
        layout.addWidget(timing_group)

        # Test button
        test_layout = QHBoxLayout()
        test_layout.addStretch()
        test_btn = QPushButton(_("Test Connection"))
        test_btn.clicked.connect(self.test_connection)
        test_layout.addWidget(test_btn)
        layout.addLayout(test_layout)

        layout.addStretch()
        return widget

    def create_ui_tab(self):
        """Crea la pestaña de interfaz"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Window settings
        window_group = QGroupBox(_("Window"))
        window_layout = QFormLayout()

        self.window_width_sb = QSpinBox()
        self.window_width_sb.setRange(800, 3000)
        self.window_width_sb.setValue(config.WINDOW_DEFAULT_WIDTH)
        window_layout.addRow(_("Default width:"), self.window_width_sb)

        self.window_height_sb = QSpinBox()
        self.window_height_sb.setRange(600, 2000)
        self.window_height_sb.setValue(config.WINDOW_DEFAULT_HEIGHT)
        window_layout.addRow(_("Default height:"), self.window_height_sb)

        window_group.setLayout(window_layout)
        layout.addWidget(window_group)

        # Theme settings
        theme_group = QGroupBox(_("Theme"))
        theme_layout = QVBoxLayout()

        theme_info = QLabel(_("The dark theme is integrated in the code. To change colors, edit config.py"))
        theme_info.setWordWrap(True)
        theme_info.setStyleSheet("color: #888;")
        theme_layout.addWidget(theme_info)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        layout.addStretch()
        return widget

    def create_scan_tab(self):
        """Crea la pestaña de escaneo"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Scan depth
        depth_group = QGroupBox(_("Scan Depth"))
        depth_layout = QFormLayout()

        self.scan_depth_sb = QSpinBox()
        self.scan_depth_sb.setRange(-1, 20)
        self.scan_depth_sb.setValue(config.DEFAULT_SCAN_DEPTH)
        self.scan_depth_sb.setSpecialValueText(_("Unlimited"))
        depth_layout.addRow(_("Maximum depth:"), self.scan_depth_sb)

        depth_group.setLayout(depth_layout)
        layout.addWidget(depth_group)

        # Excluded folders
        folders_group = QGroupBox(_("Excluded Folders"))
        folders_layout = QVBoxLayout()

        folders_info = QLabel(
            _("These folders will be ignored during scanning. One per line:")
        )
        folders_layout.addWidget(folders_info)

        self.excluded_folders_edit = QLineEdit()
        self.excluded_folders_edit.setPlaceholderText(_("Ex: $RECYCLE.BIN, System Volume Information"))
        folders_layout.addWidget(self.excluded_folders_edit)

        folders_group.setLayout(folders_layout)
        layout.addWidget(folders_group)

        layout.addStretch()
        return widget

    def create_search_tab(self):
        """Crea la pestaña de búsqueda"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Search settings
        search_group = QGroupBox(_("Search Configuration"))
        search_layout = QFormLayout()

        self.search_debounce_sb = QSpinBox()
        self.search_debounce_sb.setRange(100, 2000)
        self.search_debounce_sb.setValue(config.SEARCH_DEBOUNCE_MS)
        self.search_debounce_sb.setSuffix(" ms")
        search_layout.addRow(_("Search delay:"), self.search_debounce_sb)

        self.max_results_sb = QSpinBox()
        self.max_results_sb.setRange(1000, 100000)
        self.max_results_sb.setValue(config.MAX_SEARCH_RESULTS)
        self.max_results_sb.setSingleStep(1000)
        search_layout.addRow(_("Maximum results:"), self.max_results_sb)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        layout.addStretch()
        return widget

    def create_language_tab(self):
        """Crea la pestaña de idioma"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Language settings
        lang_group = QGroupBox(_("Language Configuration"))
        lang_layout = QFormLayout()

        self.language_combo = QComboBox()
        self.language_combo.addItem(_("Spanish"), "es")
        self.language_combo.addItem(_("English"), "en")
        
        # Set current language
        current_lang = config.LANGUAGE
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        lang_layout.addRow(_("Select Language:"), self.language_combo)

        info_label = QLabel(
            _("Note: The application needs to restart for the language change to take effect.")
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888; font-style: italic;")
        lang_layout.addRow("", info_label)

        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)

        layout.addStretch()
        return widget

    def create_export_tab(self):
        """Crea la pestaña de exportación"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Título y descripción
        title_label = QLabel(_("📤 Export Database"))
        title_label.setObjectName('sectionHeader')
        layout.addWidget(title_label)

        description = QLabel(
            _("Export the entire database to an Excel file (XLSX) with the following structure:\n"
            "• First sheet: Drive index with statistics\n"
            "• Subsequent sheets: One per drive with folder breakdown (folders only)")
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Grupo de opciones de exportación
        export_group = QGroupBox(_("Export Options"))
        export_layout = QVBoxLayout()

        # Selección de formato
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel(_("Format:")))
        self.format_combo = QComboBox()
        self.format_combo.addItem(_("Excel (XLSX)"), "xlsx")
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        export_layout.addLayout(format_layout)

        # Selección de nivel de carpetas
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel(_("Folder depth:")))
        self.level_combo = QComboBox()
        self.level_combo.addItem(_("All folders"), None)
        self.level_combo.addItem(_("Root only (level 0)"), 0)
        self.level_combo.addItem(_("Up to level 1"), 1)
        self.level_combo.addItem(_("Up to level 2"), 2)
        self.level_combo.addItem(_("Up to level 3"), 3)
        self.level_combo.addItem(_("Up to level 5"), 5)
        self.level_combo.addItem(_("Up to level 10"), 10)
        level_layout.addWidget(self.level_combo)
        level_layout.addStretch()
        export_layout.addLayout(level_layout)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Barra de progreso (inicialmente oculta)
        self.export_progress_bar = QProgressBar()
        self.export_progress_bar.setVisible(False)
        self.export_progress_label = QLabel("")
        self.export_progress_label.setVisible(False)
        layout.addWidget(self.export_progress_bar)
        layout.addWidget(self.export_progress_label)

        # Botón de exportación
        export_layout = QHBoxLayout()
        export_layout.addStretch()

        self.export_btn = QPushButton(_("📤 Export Database"))
        self.export_btn.setMinimumHeight(40)
        self.export_btn.clicked.connect(self.export_database)
        export_layout.addWidget(self.export_btn)

        # Botón de cancelar (inicialmente oculto)
        self.cancel_export_btn = QPushButton(_("❌ Cancel Export"))
        self.cancel_export_btn.setVisible(False)
        self.cancel_export_btn.clicked.connect(self.cancel_export)
        export_layout.addWidget(self.cancel_export_btn)

        layout.addLayout(export_layout)

        # Información adicional
        info_label = QLabel(
            _("<b>Note:</b> Export may take several minutes depending on database size.\n"
            "The resulting file will contain folder information only, not individual files.")
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; margin-top: 20px;")
        layout.addWidget(info_label)

        layout.addStretch()
        return widget

    def on_enable_sync_changed(self, state):
        """Habilita/deshabilita controles de sincronización"""
        enabled = state == Qt.CheckState.Checked.value
        self.backup_path_edit.setEnabled(enabled)
        self.bidirectional_rb.setEnabled(enabled)
        self.from_backup_rb.setEnabled(enabled)
        self.to_backup_rb.setEnabled(enabled)
        self.sync_on_startup_cb.setEnabled(enabled)
        self.sync_on_shutdown_cb.setEnabled(enabled)

    def browse_backup_path(self):
        """Abre diálogo para seleccionar ruta del respaldo"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            _("Select Backup File"),
            str(Path.home()),
            "SQLite Database (*.db);;All Files (*.*)"
        )

        if file_path:
            self.backup_path_edit.setText(file_path)

    def test_connection(self):
        """Prueba la conexión al archivo de respaldo"""
        backup_path = self.backup_path_edit.text().strip()

        if not backup_path:
            QMessageBox.warning(self, _("Error"), _("Please specify the backup path"))
            return

        from core.sync_manager import SyncManager
        sync_manager = SyncManager(str(config.DATABASE_PATH))

        backup_file = Path(backup_path)

        try:
            backup_dir = backup_file.parent
            if not backup_dir.exists():
                QMessageBox.warning(
                    self,
                    _("Directory Not Found"),
                    _("The directory does not exist:\n{backup_dir}\n\n"
                    "Make sure the synchronized folder is available.").format(backup_dir=backup_dir)
                )
                return

            # Check if we can write to the directory
            test_file = backup_dir / ".hddinventory_test"
            try:
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                QMessageBox.warning(
                    self,
                    _("Access Error"),
                    _("Cannot write to directory:\n{backup_dir}\n\nError: {e}").format(backup_dir=backup_dir, e=e)
                )
                return

            # Check backup file status
            if backup_file.exists():
                metadata = sync_manager.get_db_metadata(backup_file)
                if metadata:
                    unique_id, version, last_modified = metadata
                    QMessageBox.information(
                        self,
                        _("Connection Successful"),
                        _("Backup file found and valid.\n\n"
                        "ID: {unique_id}\n"
                        "Version: {version}\n"
                        "Last modified: {last_modified}").format(unique_id=unique_id, version=version, last_modified=last_modified)
                    )
                else:
                    QMessageBox.warning(
                        self,
                        _("Invalid Backup"),
                        _("The file exists but does not contain valid synchronization metadata.")
                    )
            else:
                QMessageBox.information(
                    self,
                    _("New File"),
                    _("The backup file does not exist yet.\n"
                    "It will be created automatically on the first synchronization.\n\n"
                    "Location: {backup_file}").format(backup_file=backup_file)
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                _("Error"),
                _("Error testing connection:\n{e}").format(e=e)
            )

    def load_settings(self):
        """Carga la configuración actual"""
        # Sync settings
        self.enable_sync_cb.setChecked(config.SYNC_ENABLED)

        if config.SYNC_BACKUP_PATH:
            self.backup_path_edit.setText(str(config.SYNC_BACKUP_PATH))

        direction = config.SYNC_DIRECTION
        if direction == "bidirectional":
            self.bidirectional_rb.setChecked(True)
        elif direction == "from_backup":
            self.from_backup_rb.setChecked(True)
        elif direction == "to_backup":
            self.to_backup_rb.setChecked(True)
        else:
            self.bidirectional_rb.setChecked(True)

        self.sync_on_startup_cb.setChecked(config.SYNC_ON_STARTUP)
        self.sync_on_shutdown_cb.setChecked(config.SYNC_ON_SHUTDOWN)

        # UI settings
        self.window_width_sb.setValue(config.WINDOW_DEFAULT_WIDTH)
        self.window_height_sb.setValue(config.WINDOW_DEFAULT_HEIGHT)

        # Scan settings
        self.scan_depth_sb.setValue(config.DEFAULT_SCAN_DEPTH)
        self.excluded_folders_edit.setText(", ".join(config.EXCLUDED_FOLDERS))

        # Search settings
        self.search_debounce_sb.setValue(config.SEARCH_DEBOUNCE_MS)
        self.max_results_sb.setValue(config.MAX_SEARCH_RESULTS)

        # Update enabled state
        self.on_enable_sync_changed(Qt.CheckState.Checked.value if config.SYNC_ENABLED else Qt.CheckState.Unchecked.value)

    def save_settings(self):
        """Guarda la configuración"""
        # Validate sync settings
        if self.enable_sync_cb.isChecked():
            backup_path = self.backup_path_edit.text().strip()
            if not backup_path:
                QMessageBox.warning(
                    self,
                    _("Error"),
                    _("Please specify the backup file path")
                )
                return

            if not self.sync_on_startup_cb.isChecked() and not self.sync_on_shutdown_cb.isChecked():
                QMessageBox.warning(
                    self,
                    _("Error"),
                    _("Please select at least one synchronization timing")
                )
                return

        # Update config
        # Sync
        config.SYNC_ENABLED = self.enable_sync_cb.isChecked()
        config.SYNC_BACKUP_PATH = self.backup_path_edit.text().strip() if config.SYNC_ENABLED else None

        if self.bidirectional_rb.isChecked():
            config.SYNC_DIRECTION = "bidirectional"
        elif self.from_backup_rb.isChecked():
            config.SYNC_DIRECTION = "from_backup"
        elif self.to_backup_rb.isChecked():
            config.SYNC_DIRECTION = "to_backup"

        config.SYNC_ON_STARTUP = self.sync_on_startup_cb.isChecked()
        config.SYNC_ON_SHUTDOWN = self.sync_on_shutdown_cb.isChecked()

        # UI
        config.WINDOW_DEFAULT_WIDTH = self.window_width_sb.value()
        config.WINDOW_DEFAULT_HEIGHT = self.window_height_sb.value()

        # Scan
        config.DEFAULT_SCAN_DEPTH = self.scan_depth_sb.value()
        config.EXCLUDED_FOLDERS = [f.strip() for f in self.excluded_folders_edit.text().split(",") if f.strip()]

        # Search
        config.SEARCH_DEBOUNCE_MS = self.search_debounce_sb.value()
        config.MAX_SEARCH_RESULTS = self.max_results_sb.value()

        # Language
        new_language = self.language_combo.currentData()
        language_changed = new_language != config.LANGUAGE
        config.LANGUAGE = new_language

        # Save to settings file
        self.save_settings_to_file()

        if language_changed:
            QMessageBox.information(
                self,
                _("Restart required"),
                _("The application needs to restart for the language change to take effect.")
            )
        else:
            QMessageBox.information(
                self,
                _("Settings Saved"),
                _("Settings have been saved successfully.\n"
                "Some changes require restarting the application.")
            )

        self.accept()

    def export_database(self):
        """Exporta la base de datos a un archivo XLSX usando un worker en background"""
        try:
            # Obtener formato seleccionado
            format_type = self.format_combo.currentData()

            # Obtener nivel máximo seleccionado
            max_level = self.level_combo.currentData()

            # Diálogo para seleccionar ubicación del archivo
            file_filter = "Excel Files (*.xlsx);;All Files (*.*)"
            default_name = "hddinventory_export.xlsx"

            file_path, selected_filter = QFileDialog.getSaveFileName(
                self,
                _("Save Export"),
                "",  # Start in current directory
                file_filter
            )

            if not file_path:
                return  # Usuario canceló

            # If no extension, add .xlsx
            if not file_path.lower().endswith('.xlsx'):
                file_path += '.xlsx'

            # Deshabilitar controles durante la exportación
            self._set_export_controls_enabled(False)
            self.export_progress_bar.setVisible(True)
            self.export_progress_label.setVisible(True)
            self.export_progress_bar.setValue(0)
            self.export_progress_label.setText(_("Starting export..."))

            # Crear worker y thread
            from pathlib import Path
            from ui.manage_workers import ExportWorker

            output_path = Path(file_path)
            self.export_worker = ExportWorker(output_path, max_level)
            self.export_thread = QThread()

            # Conectar señales
            self.export_worker.moveToThread(self.export_thread)
            self.export_worker.progress.connect(self._on_export_progress)
            self.export_worker.finished.connect(self._on_export_finished)
            self.export_thread.started.connect(self.export_worker.run)

            # Iniciar exportación
            self.export_thread.start()

        except Exception as e:
            QMessageBox.critical(
                self,
                _("Error"),
                _("Error starting export:\n{error}").format(error=str(e))
            )
            self._set_export_controls_enabled(True)
            self.export_progress_bar.setVisible(False)
            self.export_progress_label.setVisible(False)

    def _set_export_controls_enabled(self, enabled: bool):
        """Habilita/deshabilita los controles de exportación"""
        self.export_btn.setEnabled(enabled)
        self.format_combo.setEnabled(enabled)
        self.level_combo.setEnabled(enabled)
        self.cancel_export_btn.setVisible(not enabled)

    def _on_export_progress(self, percent: int):
        """Maneja las actualizaciones de progreso de la exportación"""
        self.export_progress_bar.setValue(percent)
        self.export_progress_label.setText(_("Exporting... {percent}% completed").format(percent=percent))

    def _on_export_finished(self, success: bool, message: str):
        """Maneja la finalización de la exportación"""
        # Limpiar thread y worker
        if self.export_thread:
            self.export_thread.quit()
            self.export_thread.wait()
            self.export_thread = None
        self.export_worker = None

        # Ocultar progreso
        self.export_progress_bar.setVisible(False)
        self.export_progress_label.setVisible(False)

        # Re-habilitar controles
        self._set_export_controls_enabled(True)

        # Mostrar resultado
        if success:
            QMessageBox.information(
                self,
                _("Export Completed"),
                _("{message}\n\n"
                "The file contains:\n"
                "• First sheet: Drive index\n"
                "• Subsequent sheets: Folders by drive").format(message=message)
            )
        else:
            QMessageBox.warning(
                self,
                _("Export Error"),
                message
            )

    def cancel_export(self):
        """Cancela la exportación en curso"""
        if self.export_worker:
            self.export_worker.cancel()
            self.export_progress_label.setText(_("Canceling export..."))

    def save_settings_to_file(self):
        """Guarda la configuración en el archivo de settings"""
        try:
            settings = {}
            if config.SETTINGS_PATH.exists():
                with open(config.SETTINGS_PATH, 'r') as f:
                    settings = json.load(f)

            # Sync settings
            settings['sync'] = {
                'enabled': config.SYNC_ENABLED,
                'backup_path': config.SYNC_BACKUP_PATH,
                'direction': config.SYNC_DIRECTION,
                'on_startup': config.SYNC_ON_STARTUP,
                'on_shutdown': config.SYNC_ON_SHUTDOWN
            }

            # UI settings
            settings['ui'] = {
                'window_width': config.WINDOW_DEFAULT_WIDTH,
                'window_height': config.WINDOW_DEFAULT_HEIGHT
            }

            # Scan settings
            settings['scan'] = {
                'default_depth': config.DEFAULT_SCAN_DEPTH,
                'excluded_folders': config.EXCLUDED_FOLDERS
            }

            # Search settings
            settings['search'] = {
                'debounce_ms': config.SEARCH_DEBOUNCE_MS,
                'max_results': config.MAX_SEARCH_RESULTS
            }

            # Language settings
            settings['language'] = config.LANGUAGE

            with open(config.SETTINGS_PATH, 'w') as f:
                json.dump(settings, f, indent=2)

        except Exception as e:
            QMessageBox.warning(
                self,
                _("Error"),
                _("Could not save settings:\n{error}").format(error=e)
            )