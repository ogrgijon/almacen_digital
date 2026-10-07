"""Background workers for drive management operations.

This module contains QThread-based worker classes for time-consuming operations:
- ScanWorker: Handles background drive scanning
- ExportWorker: Handles background database export to Excel
"""

from PyQt6.QtCore import QObject, pyqtSignal


class ScanWorker(QObject):
    """Background worker for scanning drive contents.
    
    This worker runs drive scanning in a separate thread to prevent
    UI blocking during lengthy scan operations.
    
    Signals:
        finished: Emitted when scan completes with (folders, files, verbose, total_size)
    """
    
    finished = pyqtSignal(list, list, str, int)
    
    def __init__(self, drive_letter):
        """Initialize the scan worker.
        
        Args:
            drive_letter: Drive letter to scan (e.g., 'D:')
        """
        super().__init__()
        self.drive_letter = drive_letter
        self._cancelled = False
        self.scanner = None
    
    def run(self):
        """Execute the drive scan operation.
        
        Scans the specified drive and emits the finished signal with results.
        Can be cancelled mid-scan via the cancel() method.
        """
        from core.scanner import FileScanner
        self.scanner = FileScanner()
        folders, files, inventory_xmls = self.scanner.scan_drive(self.drive_letter)
        if not self._cancelled:
            # Safely sum file sizes, handling empty strings
            def safe_size(f):
                size = f.get('file_size', 0)
                try:
                    return int(float(size)) if size else 0
                except (ValueError, TypeError):
                    return 0
            total_size = sum(safe_size(f) for f in files)
            verbose = '\n'.join(self.scanner.errors)
            # Note: inventory_xmls not emitted here - would need signal update if needed
            self.finished.emit(folders, files, verbose, total_size)
    
    def cancel(self):
        """Cancel the ongoing scan operation.
        
        Sets the cancellation flag and notifies the scanner to stop.
        """
        self._cancelled = True
        if self.scanner:
            self.scanner.cancel()


class ExportWorker(QObject):
    """Background worker for exporting database to Excel.
    
    This worker runs database export in a separate thread to prevent
    UI blocking during lengthy export operations.
    
    Signals:
        progress: Emitted with progress percentage (0-100)
        finished: Emitted when export completes with (success, message)
    """
    
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, output_path, max_level=None):
        """Initialize the export worker.
        
        Args:
            output_path: Path where to save the Excel file
            max_level: Maximum folder level to export (None = all levels)
        """
        super().__init__()
        self.output_path = output_path
        self.max_level = max_level
        self._cancelled = False
    
    def run(self):
        """Execute the database export operation.
        
        Exports the database to Excel and emits progress and finished signals.
        Can be cancelled mid-export via the cancel() method.
        """
        try:
            if self._cancelled:
                self.finished.emit(False, "Export cancelled")
                return
            
            from core.excel_exporter import ExcelExporter
            import config
            
            exporter = ExcelExporter(str(config.DATABASE_PATH))
            
            def progress_callback(percent):
                if self._cancelled:
                    return
                self.progress.emit(percent)
            
            success = exporter.export_database(self.output_path, self.max_level, progress_callback)
            
            if self._cancelled:
                self.finished.emit(False, "Export cancelled")
                return
            
            if success:
                message = f"Database exported successfully to:\n{self.output_path}"
            else:
                message = "Export failed. Check application logs for details."
            
            self.finished.emit(success, message)
            
        except Exception as e:
            self.finished.emit(False, f"Export error: {str(e)}")
    
    def cancel(self):
        """Cancel the ongoing export operation.
        
        Sets the cancellation flag to stop the export.
        """
        self._cancelled = True
