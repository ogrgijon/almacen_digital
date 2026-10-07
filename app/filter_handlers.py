"""Event handlers for filter and search operations.

This module contains handlers for filtering, searching, and quick filter operations.
"""

import logging
from PyQt6.QtWidgets import QMessageBox
import config

logger = logging.getLogger(__name__)


class FilterEventHandlers:
    """Handles filter and search-related events.
    
    This class manages:
    - Quick filter selection (documents, images, etc.)
    - Advanced filter changes from sidebar
    - Quick search from results view
    - File selection events
    """
    
    def __init__(self, app_context):
        """Initialize filter event handlers.
        
        Args:
            app_context: Reference to main application context
        """
        self.ctx = app_context
    
    def on_quick_filter(self, filter_type: str):
        """Handle quick filter selection.
        
        Filters include: documents, images, audio, videos, archives, 
        large_files, folders, root_folders.
        
        Args:
            filter_type: Type of quick filter to apply
        """
        if filter_type == 'root_folders':
            self._show_root_folders()
        elif filter_type == 'folders':
            self._show_all_folders()
        elif filter_type == 'large_files':
            self._show_large_files()
        else:
            self._show_by_category(filter_type)
    
    def _show_root_folders(self):
        """Show root folders from last selected drive or first drive."""
        from app.drive_handlers import DriveEventHandlers
        drive_handlers = DriveEventHandlers(self.ctx)
        drive_id = drive_handlers.get_last_selected_drive_id()
        
        if drive_id is None:
            drives = self.ctx.db.get_all_drives()
            if not drives:
                self.ctx.results_view.load_results([])
                self.ctx.window.update_status("No drives available")
                return
            drive_id = drives[0]['id']
        
        drive = self.ctx.db.get_drive_by_id(drive_id)
        if not drive:
            self.ctx.results_view.load_results([])
            self.ctx.window.update_status("Drive not found")
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
    
    def _show_all_folders(self):
        """Show all folders from all drives."""
        all_folders = []
        for d in self.ctx.db.get_all_drives():
            for f in self.ctx.db.get_folders_by_drive(d['id']):
                f = dict(f)
                f['drive_id'] = d['id']
                all_folders.append(f)
        
        results = []
        for f in all_folders:
            drive = self.ctx.db.get_drive_by_id(f['drive_id']) if 'drive_id' in f.keys() else None
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
        
        self.ctx.results_view.load_results(results)
        self.ctx.window.update_status(f"Showing all folders ({len(results):,})")
    
    def _show_large_files(self):
        """Show files larger than 100MB."""
        results, _ = self.ctx.db.search_files(
            min_size=100*1024*1024,
            limit=config.MAX_SEARCH_RESULTS
        )
        self.ctx.results_view.load_results(results)
        self.ctx.window.update_status(f"Showing large files (>100MB) - {len(results):,} found")
    
    def _show_by_category(self, category: str):
        """Show files by category (documents, images, etc.).
        
        Args:
            category: Category name matching config.FILE_CATEGORIES keys
        """
        category_map = {
            'documents': 'Documents',
            'images': 'Images',
            'audio': 'Audio',
            'videos': 'Video',
            'archives': 'Archives'
        }
        
        config_category = category_map.get(category)
        if not config_category:
            logger.warning(f"Unknown category: {category}")
            return
        
        extensions = config.FILE_CATEGORIES.get(config_category, [])
        if extensions:
            results, _ = self.ctx.db.search_files(
                extensions=extensions,
                limit=config.MAX_SEARCH_RESULTS
            )
            self.ctx.results_view.load_results(results)
            self.ctx.window.update_status(f"Showing {category} - {len(results):,} files")
    
    def on_filters_changed(self, filters: dict):
        """Handle filter changes from right sidebar.
        
        Applies multiple filter criteria simultaneously.
        
        Args:
            filters: Dictionary with filter parameters
        """
        try:
            # Extract filter parameters
            query = filters.get('query', '')
            file_type = filters.get('file_type', 'All Types')
            min_size = filters.get('min_size')
            max_size = filters.get('max_size')
            date_from = filters.get('date_from')
            date_to = filters.get('date_to')
            path_contains = filters.get('path_contains', '')
            
            # Get extensions for file type
            extensions = []
            if file_type != 'All Types':
                extensions = config.FILE_CATEGORIES.get(file_type, [])
            
            # Get drive IDs
            drive_ids = []
            drive_text = filters.get('drive', 'All Drives')
            if drive_text != 'All Drives':
                drives = self.ctx.db.get_all_drives()
                for drive in drives:
                    if drive['drive_label'] == drive_text:
                        drive_ids = [drive['id']]
                        break
            
            # Sanitize numeric parameters
            min_size_val = min_size if isinstance(min_size, int) and min_size is not None else 0
            max_size_val = max_size if isinstance(max_size, int) and max_size is not None else 0
            
            # Sanitize date parameters
            date_from_val = date_from if filters.get('date_preset') == 'Custom range' and isinstance(date_from, str) and date_from else ''
            date_to_val = date_to if filters.get('date_preset') == 'Custom range' and isinstance(date_to, str) and date_to else ''
            
            # Sanitize path parameter
            path_contains_val = path_contains if isinstance(path_contains, str) and path_contains else ''
            
            results, _ = self.ctx.db.search_files(
                query=query,
                drive_ids=drive_ids,
                extensions=extensions,
                min_size=min_size_val,
                max_size=max_size_val,
                date_from=date_from_val,
                date_to=date_to_val,
                path_contains=path_contains_val,
                limit=config.MAX_SEARCH_RESULTS
            )
            
            self.ctx.results_view.load_results(results)
            self.ctx.window.update_status(f"Found {len(results):,} files matching filters")
            
        except Exception as e:
            logger.exception(f"Error applying filters: {e}")
            QMessageBox.warning(self.ctx.window, "Error", f"Error applying filters:\n{str(e)}")
    
    def on_quick_search(self, query: str):
        """Handle quick search from results view.
        
        Args:
            query: Search query string
        """
        try:
            if not query:
                self._load_all_files()
            else:
                results, _ = self.ctx.db.search_files(
                    query=query,
                    limit=config.MAX_SEARCH_RESULTS
                )
                self.ctx.results_view.load_results(results)
                self.ctx.window.update_status(f"Search: '{query}' - {len(results):,} results")
        except Exception as e:
            logger.exception(f"Error searching: {e}")
            QMessageBox.warning(self.ctx.window, "Error", f"Error searching:\n{str(e)}")
    
    def on_file_selected(self, file_data: dict):
        """Handle file selection from results view.
        
        Updates status bar with file information.
        
        Args:
            file_data: Selected file data dictionary
        """
        name = file_data.get('file_name', '')
        size = file_data.get('file_size', 0)
        from utils.helpers import format_file_size
        self.ctx.window.update_status(f"Selected: {name} ({format_file_size(size)})")
    
    def _load_all_files(self, limit=1000):
        """Load all files with a limit.
        
        Args:
            limit: Maximum number of files to load
        """
        try:
            results, _ = self.ctx.db.search_files(limit=limit)
            self.ctx.results_view.load_results(results)
            self.ctx.window.update_status(f"Showing {len(results):,} files")
        except Exception as e:
            logger.exception(f"Error loading files: {e}")
            QMessageBox.warning(self.ctx.window, "Error", f"Error loading files:\n{str(e)}")
