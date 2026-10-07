"""
Diálogo de configuración de sincronización.
Permite al usuario configurar la sincronización de base de datos.
"""

import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QRadioButton, QButtonGroup, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
import config
from i18n import _


class SyncSettingsDialog(QDialog):
    """Diálogo para configurar la sincronización de base de datos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Sync Settings"))
        self.setModal(True)
        self.setMinimumWidth(600)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout(self)
        
        # Enable sync checkbox
        self.enable_sync_cb = QCheckBox(_("Enable automatic synchronization"))
        self.enable_sync_cb.stateChanged.connect(self.on_enable_changed)
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
        self.backup_path_edit.setPlaceholderText(_("Ex: C:/Users/User/Google Drive/HDDInventory/inventory_backup.db"))
        path_input_layout.addWidget(self.backup_path_edit)
        
        browse_btn = QPushButton(_("Browse..."))
        browse_btn.clicked.connect(self.browse_backup_path)
        path_input_layout.addWidget(browse_btn)
        
        path_layout.addLayout(path_input_layout)
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        # Sync direction group
        direction_group = QGroupBox(_("Sync Direction"))
        direction_layout = QVBoxLayout()
        
        self.direction_group = QButtonGroup(self)
        
        self.bidirectional_rb = QRadioButton(_("Bidirectional (automatic)"))
        self.bidirectional_rb.setToolTip(_("Synchronizes automatically using the most recent version"))
        self.direction_group.addButton(self.bidirectional_rb, 0)
        direction_layout.addWidget(self.bidirectional_rb)
        
        self.from_backup_rb = QRadioButton(_("Only from backup"))
        self.from_backup_rb.setToolTip(_("Only updates from backup, never writes"))
        self.direction_group.addButton(self.from_backup_rb, 1)
        direction_layout.addWidget(self.from_backup_rb)
        
        self.to_backup_rb = QRadioButton(_("Only to backup"))
        self.to_backup_rb.setToolTip(_("Only writes to backup, never reads"))
        self.direction_group.addButton(self.to_backup_rb, 2)
        direction_layout.addWidget(self.to_backup_rb)
        
        direction_group.setLayout(direction_layout)
        layout.addWidget(direction_group)
        
        # Sync timing group
        timing_group = QGroupBox(_("Sync Timing"))
        timing_layout = QVBoxLayout()
        
        self.sync_on_startup_cb = QCheckBox(_("Synchronize when starting the application"))
        timing_layout.addWidget(self.sync_on_startup_cb)
        
        self.sync_on_shutdown_cb = QCheckBox(_("Synchronize when closing the application"))
        timing_layout.addWidget(self.sync_on_shutdown_cb)
        
        timing_group.setLayout(timing_layout)
        layout.addWidget(timing_group)
        
        # Info label
        info_label = QLabel(
            _("<b>Note:</b> Synchronization uses a unique ID and version number to "
              "determine which database is more up-to-date. Make sure all "
              "computers share the same backup file.")
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #a0a0a0; padding: 10px;")
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        test_btn = QPushButton(_("Test Connection"))
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)
        
        save_btn = QPushButton(_("Save"))
        save_btn.clicked.connect(self.save_settings)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton(_("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Initial state
        self.on_enable_changed(Qt.CheckState.Unchecked.value)
    
    def on_enable_changed(self, state):
        """Habilita/deshabilita controles según el checkbox"""
        enabled = state == Qt.CheckState.Checked.value
        self.backup_path_edit.setEnabled(enabled)
        self.bidirectional_rb.setEnabled(enabled)
        self.from_backup_rb.setEnabled(enabled)
        self.to_backup_rb.setEnabled(enabled)
        self.sync_on_startup_cb.setEnabled(enabled)
        self.sync_on_shutdown_cb.setEnabled(enabled)
    
    def browse_backup_path(self):
        """Abre un diálogo para seleccionar la ruta del respaldo"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            _("Select Backup File"),
            str(Path.home()),
            "SQLite Database (*.db);;All Files (*.*)"
        )
        
        if file_path:
            self.backup_path_edit.setText(file_path)
    
    def load_settings(self):
        """Carga la configuración actual"""
        self.enable_sync_cb.setChecked(config.SYNC_ENABLED)
        
        if config.SYNC_BACKUP_PATH:
            self.backup_path_edit.setText(str(config.SYNC_BACKUP_PATH))
        
        # Set direction radio button
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
    
    def test_connection(self):
        """Prueba la conexión al archivo de respaldo"""
        backup_path = self.backup_path_edit.text().strip()
        
        if not backup_path:
            QMessageBox.warning(self, _("Error"), _("Please specify the backup path"))
            return
        
        from core.sync_manager import SyncManager
        sync_manager = SyncManager(str(config.DATABASE_PATH))
        
        backup_file = Path(backup_path)
        
        # Check if directory is accessible
        try:
            backup_dir = backup_file.parent
            if not backup_dir.exists():
                QMessageBox.warning(
                    self,
                    _("Directory Not Found"),
                    _("The directory does not exist:\n{dir}\n\n"
                      "Make sure the synchronized folder is available.").format(dir=backup_dir)
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
                    _("Cannot write to directory:\n{dir}\n\nError: {error}").format(dir=backup_dir, error=e)
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
                          "ID: {id}\n"
                          "Version: {version}\n"
                          "Last modified: {modified}").format(id=unique_id, version=version, modified=last_modified)
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
                      "Location: {location}").format(location=backup_file)
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                _("Error"),
                _("Error testing connection:\n{error}").format(error=e)
            )
    
    def save_settings(self):
        """Guarda la configuración"""
        # Validate
        if self.enable_sync_cb.isChecked():
            backup_path = self.backup_path_edit.text().strip()
            if not backup_path:
                QMessageBox.warning(
                    self,
                    _("Error"),
                    _("Please specify the backup file path")
                )
                return
            
            # Validate that at least one timing option is selected
            if not self.sync_on_startup_cb.isChecked() and not self.sync_on_shutdown_cb.isChecked():
                QMessageBox.warning(
                    self,
                    _("Error"),
                    _("Please select at least one synchronization timing")
                )
                return
        
        # Update config
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
        
        # Save to settings file
        self.save_settings_to_file()
        
        QMessageBox.information(
            self,
            _("Settings Saved"),
            _("Synchronization settings have been saved successfully.\n"
              "Changes will be applied on the next application start.")
        )
        
        self.accept()
    
    def save_settings_to_file(self):
        """Guarda la configuración en el archivo de settings"""
        try:
            settings = {}
            if config.SETTINGS_PATH.exists():
                with open(config.SETTINGS_PATH, 'r') as f:
                    settings = json.load(f)
            
            settings['sync'] = {
                'enabled': config.SYNC_ENABLED,
                'backup_path': config.SYNC_BACKUP_PATH,
                'direction': config.SYNC_DIRECTION,
                'on_startup': config.SYNC_ON_STARTUP,
                'on_shutdown': config.SYNC_ON_SHUTDOWN
            }
            
            with open(config.SETTINGS_PATH, 'w') as f:
                json.dump(settings, f, indent=2)
        
        except Exception as e:
            QMessageBox.warning(
                self,
                _("Error"),
                _("Could not save settings:\n{error}").format(error=e)
            )
