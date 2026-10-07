"""Event handlers for drive-related operations.

This module contains handlers for drive selection, addition, and removal events.
"""

import logging
from typing import Dict, Any
from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


class DriveEventHandlers:
    """Handles drive-related events and operations.
    
    This class manages:
    - Drive selection from sidebar
    - Drive addition to inventory
    - Drive removal from inventory
    - Switching to drive view
    """
    
    def __init__(self, app_context):
        """Initialize drive event handlers.
        
        Args:
            app_context: Reference to main application context with db, window, etc.
        """
        self.ctx = app_context
        self._last_selected_drive_id = None
    
    def on_view_drive_index(self, drive_id: int):
        """Switch to Inventory mode and display drive contents.
        
        Shows root folders of the selected drive.
        
        Args:
            drive_id: ID of drive to view
        """
        self.ctx.window.switch_mode('inventory')
        drive = self.ctx.db.get_drive_by_id(drive_id)
        if not drive:
            self.ctx.results_view.load_results([])
            return
        
        drive_label = drive.get('drive_label', '')
        set_drive_filter = getattr(self.ctx.right_sidebar, 'set_drive_filter', None)
        
        if callable(set_drive_filter):
            set_drive_filter(drive_label)
        else:
            self._fallback_show_drive_folders(drive_id, drive)
    
    def _fallback_show_drive_folders(self, drive_id: int, drive: Dict):
        """Fallback method to show drive folders directly.
        
        Args:
            drive_id: Drive database ID
            drive: Drive data dictionary
        """
        drive_letter = drive.get('drive_letter', '').rstrip('\\')
        all_folders = self.ctx.db.get_folders_by_drive(drive_id)
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
        self.ctx.results_view.load_results(results)
    
    def on_drive_selected(self, drive_id: int):
        """Handle drive selection from sidebar.
        
        Shows only root folders for performance.
        
        Args:
            drive_id: ID of selected drive
        """
        self._last_selected_drive_id = drive_id
        try:
            drive = self.ctx.db.get_drive_by_id(drive_id)
            if not drive:
                self.ctx.results_view.load_results([])
                return
            
            drive_letter = drive.get('drive_letter', '').rstrip('\\')
            all_folders = self.ctx.db.get_folders_by_drive(drive_id)
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
            
            self.ctx.results_view.load_results(results)
            self.ctx.window.update_status(f"Showing root folders from {drive['drive_label']}")
            
        except Exception as e:
            logger.exception(f"Error loading drive folders: {e}")
            QMessageBox.warning(self.ctx.window, "Error", f"Error loading drive folders:\n{str(e)}")
    
    def on_drive_added(self, drive: Dict):
        """Reload drives in sidebar after adding new drive.
        
        Args:
            drive: Newly added drive data
        """
        drives = self.ctx.db.get_all_drives()
        if hasattr(self.ctx.left_sidebar, 'load_drives'):
            self.ctx.left_sidebar.load_drives(drives)
        logger.info(f"Drive added: {drive.get('drive_label', 'Unknown')}")
    
    def on_drive_removed(self):
        """Reload drives in sidebar after removal."""
        drives = self.ctx.db.get_all_drives()
        if hasattr(self.ctx.left_sidebar, 'load_drives'):
            self.ctx.left_sidebar.load_drives(drives)
        logger.info("Drive removed from inventory")
    
    def get_last_selected_drive_id(self):
        """Get the last selected drive ID.
        
        Returns:
            int or None: Last selected drive ID
        """
        return self._last_selected_drive_id
