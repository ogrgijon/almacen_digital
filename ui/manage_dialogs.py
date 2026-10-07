"""Dialogs for drive management functionality.

This module contains dialog classes used in the drive management view:
- AddDeviceDialog: Dialog for adding new devices to inventory
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout
from i18n import _


class AddDeviceDialog(QDialog):
    """Dialog for registering a new device to the inventory.
    
    This dialog wraps the connected devices box to provide a modal
    interface for selecting and adding a drive to the inventory.
    """
    
    def __init__(self, connected_box, parent=None):
        """Initialize the add device dialog.
        
        Args:
            connected_box: QGroupBox containing connected devices UI
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.setWindowTitle(_("Register New Device"))
        layout = QVBoxLayout(self)
        layout.addWidget(connected_box)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
