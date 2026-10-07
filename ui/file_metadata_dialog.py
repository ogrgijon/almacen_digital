"""File metadata dialog for editing comments and ratings."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QTextEdit, QComboBox, QPushButton, QFrame, 
                              QDialogButtonBox, QMessageBox, QWidget, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
import os
from i18n import _


class FileMetadataDialog(QDialog):
    """Dialog for editing file comments and ratings"""
    
    def __init__(self, file_data: dict, db, parent=None):
        super().__init__(parent)
        self.file_data = file_data
        self.db = db
        self.file_id = file_data.get('id')
        
        is_folder = self.file_data.get('is_folder', False)
        item_type = _("Folder") if is_folder else _("File")
        self.setWindowTitle(_("Edit {item} Metadata").format(item=item_type))
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.init_ui()
        self.load_current_metadata()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)
        
        is_folder = self.file_data.get('is_folder', False)
        
        # File information section
        file_info_frame = QFrame()
        file_info_frame.setFrameStyle(QFrame.Shape.Box)
        file_info_layout = QVBoxLayout(file_info_frame)
        
        file_name = self.file_data.get('file_name', '')
        file_path = self.file_data.get('file_path', '')
        file_size = self.file_data.get('file_size', 0)
        drive_letter = self.file_data.get('drive_letter', '')
        
        # Format file size
        def format_size(size):
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size / (1024 * 1024):.1f} MB"
            else:
                return f"{size / (1024 * 1024 * 1024):.1f} GB"
        
        item_type_label = "Carpeta" if is_folder else "Archivo"
        file_info_layout.addWidget(QLabel(f"<b>{item_type_label}:</b> {file_name}"))
        if not is_folder:
            file_info_layout.addWidget(QLabel(f"<b>Tamaño:</b> {format_size(file_size)}"))
        file_info_layout.addWidget(QLabel(f"<b>Unidad:</b> {drive_letter}"))
        file_info_layout.addWidget(QLabel(f"<b>Ruta:</b> {file_path}"))
        
        layout.addWidget(file_info_frame)
        
        # Rating section
        rating_layout = QHBoxLayout()
        rating_layout.addWidget(QLabel("<b>Calificación:</b>"))
        
        self.rating_combo = QComboBox()
        self.rating_combo.addItems([
            "Sin calificación",
            "★☆☆☆☆ (1 estrella)",
            "★★☆☆☆ (2 estrellas)", 
            "★★★☆☆ (3 estrellas)",
            "★★★★☆ (4 estrellas)",
            "★★★★★ (5 estrellas)"
        ])
        rating_layout.addWidget(self.rating_combo)
        rating_layout.addStretch()
        layout.addLayout(rating_layout)
        
        # Comments section
        layout.addWidget(QLabel("<b>Comentarios:</b>"))
        self.comments_edit = QTextEdit()
        item_type = "esta carpeta" if is_folder else "este archivo"
        self.comments_edit.setPlaceholderText(f"Añade comentarios sobre {item_type}...")
        self.comments_edit.setMaximumHeight(150)
        layout.addWidget(self.comments_edit)
        
        # Custom metadata section
        layout.addWidget(QLabel("<b>Metadatos Personalizados:</b>"))
        
        # Custom metadata list
        self.custom_metadata_widget = QWidget()
        self.custom_metadata_layout = QVBoxLayout(self.custom_metadata_widget)
        self.custom_metadata_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add existing custom metadata
        self.custom_fields = {}  # key -> (key_edit, value_edit, remove_btn)
        
        # Add button for new metadata
        add_btn = QPushButton("➕ Añadir Metadato")
        add_btn.clicked.connect(self.add_custom_field)
        self.custom_metadata_layout.addWidget(add_btn)
        
        layout.addWidget(self.custom_metadata_widget)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_metadata)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_current_metadata(self):
        """Load current metadata from database and XML"""
        comments = ""
        rating = 0
        custom_metadata = {}
        
        # First try to load from database
        if self.file_id:
            metadata = self.db.get_file_metadata(self.file_id)
            comments = metadata.get('comments', '')
            rating = metadata.get('rating', 0)
            custom_metadata = self.db.get_file_custom_metadata(self.file_id)
        
        # If no database data, try to load from XML file
        if not comments and rating == 0 and not custom_metadata:
            drive_letter = self.file_data.get('drive_letter', '')
            file_path = self.file_data.get('file_path', '')
            is_folder = self.file_data.get('is_folder', False)
            
            if drive_letter and file_path:
                full_path = os.path.join(drive_letter + '\\', file_path.lstrip('\\'))
                
                # Import here to avoid circular imports
                from core.xml_metadata import FileMetadataHandler
                
                xml_metadata = FileMetadataHandler.read_metadata(full_path, is_folder)
                comments = xml_metadata.get('comments', '')
                rating = xml_metadata.get('rating', 0)
                custom_metadata = xml_metadata.get('custom', {})
        
        self.comments_edit.setPlainText(comments)
        self.rating_combo.setCurrentIndex(rating)
        
        # Load custom metadata fields
        for key, value in custom_metadata.items():
            self.add_custom_field(key, value)
    
    def save_metadata(self):
        """Save metadata to database and XML file"""
        comments = self.comments_edit.toPlainText().strip()
        rating = self.rating_combo.currentIndex()
        
        try:
            # Save to database
            if self.file_id:
                self.db.update_file_comments(self.file_id, comments)
                self.db.update_file_rating(self.file_id, rating)
            
            # Save custom metadata to database
            if self.file_id:
                for key, (key_edit, value_edit, _) in self.custom_fields.items():
                    new_key = key_edit.text().strip()
                    new_value = value_edit.text().strip()
                    
                    if new_key and new_value:
                        self.db.set_file_metadata(self.file_id, new_key, new_value)
                    elif key:  # Remove if key was cleared
                        self.db.delete_file_metadata(self.file_id, key)
            
            # Collect custom metadata for XML
            custom_metadata = {}
            for key, (key_edit, value_edit, _) in self.custom_fields.items():
                xml_key = key_edit.text().strip()
                xml_value = value_edit.text().strip()
                if xml_key and xml_value:
                    custom_metadata[xml_key] = xml_value
            
            # Save to XML file (if we have the full path)
            drive_letter = self.file_data.get('drive_letter', '')
            file_path = self.file_data.get('file_path', '')
            is_folder = self.file_data.get('is_folder', False)
            
            if drive_letter and file_path:
                full_path = os.path.join(drive_letter + '\\', file_path.lstrip('\\'))
                
                # Import here to avoid circular imports
                from core.xml_metadata import FileMetadataHandler
                
                if comments or rating > 0 or custom_metadata:
                    # Create/update XML file
                    FileMetadataHandler.write_metadata(full_path, comments, rating, is_folder, custom_metadata)
                else:
                    # Remove XML file if no metadata
                    FileMetadataHandler.delete_metadata(full_path, is_folder)
            
            QMessageBox.information(self, _("Saved"), _("Metadata saved successfully."))
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, _("Error"), _("Error saving metadata:\n{error}").format(error=str(e)))
    
    def add_custom_field(self, key: str = "", value: str = ""):
        """Add a custom metadata field"""
        # Create widgets for the field
        field_widget = QWidget()
        field_layout = QHBoxLayout(field_widget)
        field_layout.setContentsMargins(0, 0, 0, 0)
        
        key_edit = QLineEdit(key)
        key_edit.setPlaceholderText("Nombre del metadato")
        key_edit.setMaximumWidth(150)
        
        value_edit = QLineEdit(value)
        value_edit.setPlaceholderText("Valor del metadato")
        
        remove_btn = QPushButton("❌")
        remove_btn.setMaximumWidth(40)
        remove_btn.clicked.connect(lambda: self.remove_custom_field(field_widget))
        
        field_layout.addWidget(key_edit)
        field_layout.addWidget(value_edit)
        field_layout.addWidget(remove_btn)
        
        # Insert before the add button
        add_btn_index = self.custom_metadata_layout.count() - 1
        self.custom_metadata_layout.insertWidget(add_btn_index, field_widget)
        
        # Store reference
        field_key = key or f"field_{len(self.custom_fields)}"
        self.custom_fields[field_key] = (key_edit, value_edit, remove_btn)
    
    def remove_custom_field(self, field_widget):
        """Remove a custom metadata field"""
        # Find and remove from custom_fields dict
        for key, (key_edit, value_edit, btn) in list(self.custom_fields.items()):
            if field_widget.layout().itemAt(0).widget() == key_edit:
                del self.custom_fields[key]
                break
        
        # Remove from layout
        field_widget.setParent(None)
        field_widget.deleteLater()