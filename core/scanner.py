"""File system scanner for drive inventory"""

import os
from pathlib import Path
from typing import Optional, Callable, List, Tuple, Dict
from datetime import datetime
import config


class FileScanner:
    """Scans drive and catalogs file structure"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Args:
            progress_callback: Function called with (current_path, files_scanned, folders_scanned)
        """
        self.progress_callback = progress_callback
        self.cancelled = False
        self.files_scanned = 0
        self.folders_scanned = 0
        self.errors = []
        self.inventory_xmls = []  # Store discovered inventory XML files
    
    def scan_drive(self, root_path: str, max_depth: int = -1) -> Tuple[List[dict], List[dict], List[dict]]:
        """
        Scan a drive and return lists of folders and files
        
        Args:
            root_path: Root path to scan (e.g., "E:\\")
            max_depth: Maximum depth to scan (-1 for unlimited)
        
        Returns:
            Tuple of (folders_list, files_list, inventory_xmls_list)
        """
        self.cancelled = False
        self.files_scanned = 0
        self.folders_scanned = 0
        self.errors = []
        self.inventory_xmls = []
        
        folders = []
        files = []
        
        root = Path(root_path)
        if not root.exists():
            self.errors.append(f"Path does not exist: {root_path}")
            return folders, files, self.inventory_xmls
        
        # Scan recursively
        self._scan_directory(root, folders, files, level=0, max_depth=max_depth, root_path=root)
        
        return folders, files, self.inventory_xmls
    
    def _scan_directory(self, path: Path, folders: List[dict], files: List[dict], 
                       level: int = 0, max_depth: int = -1, parent_path: str = "", root_path: Path = None):
        """Recursively scan directory"""
        
        if self.cancelled:
            return
        
        if max_depth != -1 and level > max_depth:
            return
        
        try:
            # Get all items in directory - use os.scandir for better performance
            items = os.scandir(path)
        except (PermissionError, OSError) as e:
            self.errors.append(f"Cannot access {path}: {str(e)}")
            return
        
        try:
            for item in items:
                if self.cancelled:
                    return
                
                try:
                    # Skip excluded folders
                    if item.name in config.EXCLUDED_FOLDERS:
                        continue
                    
                    item_path = Path(item.path)
                    
                    if item.is_dir():
                        try:
                            # It's a folder
                            rel_path = str(item_path.relative_to(root_path))
                            
                            # Validate that path is relative to device root (no drive letters)
                            if ':' in rel_path or rel_path.startswith('\\\\'):
                                self.errors.append(f"Invalid relative path for folder {item_path}: {rel_path}")
                                continue
                            
                            folder_info = {
                                'folder_name': item.name,
                                'folder_path': rel_path,
                                'parent_path': parent_path,
                                'level': level
                            }
                            folders.append(folder_info)
                            self.folders_scanned += 1
                            
                            # Report progress less frequently
                            if self.progress_callback and self.folders_scanned % 50 == 0:
                                msg = f"Carpetas encontradas: {self.folders_scanned:,} | Archivos encontrados: {self.files_scanned:,}"
                                self.progress_callback(msg)
                            
                            # Recursively scan subdirectory
                            self._scan_directory(item_path, folders, files, level + 1, max_depth, rel_path, root_path)
                        except (PermissionError, OSError) as e:
                            self.errors.append(f"Cannot access {item_path}: {str(e)}")
                            continue
                    
                    elif item.is_file():
                        try:
                            # Check if this is an inventory XML file
                            if self._is_inventory_xml(item.name):
                                # Parse and store the inventory XML metadata
                                self._process_inventory_xml(item_path, item.name, parent_path, root_path)
                                continue  # Skip adding it as a regular file
                            
                            # It's a file
                            # Use cached stat from DirEntry for better performance
                            stat = item.stat()
                            file_size = stat.st_size
                            modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
                            created_time = datetime.fromtimestamp(stat.st_ctime).isoformat()
                        except (OSError, ValueError):
                            file_size = 0
                            modified_time = datetime.now().isoformat()
                            created_time = datetime.now().isoformat()
                        
                        extension = Path(item.name).suffix.lower()
                        
                        # Skip excluded extensions
                        if extension in config.EXCLUDED_EXTENSIONS:
                            continue
                        
                        rel_path = str(item_path.relative_to(root_path))
                        
                        # Validate that path is relative to device root (no drive letters)
                        if ':' in rel_path or rel_path.startswith('\\\\'):
                            self.errors.append(f"Invalid relative path for file {item_path}: {rel_path}")
                            continue
                        
                        file_info = {
                            'file_name': item.name,
                            'file_path': rel_path,
                            'file_size': file_size,
                            'file_extension': extension,
                            'modified_date': modified_time,
                            'created_date': created_time,
                            'parent_path': parent_path
                        }
                        files.append(file_info)
                        self.files_scanned += 1
                        
                        # Report progress less frequently
                        if self.progress_callback and self.files_scanned % 200 == 0:
                            msg = f"Carpetas encontradas: {self.folders_scanned:,} | Archivos encontrados: {self.files_scanned:,}"
                            self.progress_callback(msg)
                except (PermissionError, OSError) as e:
                    self.errors.append(f"Cannot access {item_path}: {str(e)}")
                    continue
        finally:
            items.close()
    
    def cancel(self):
        """Cancel the current scan"""
        self.cancelled = True
    
    def get_stats(self) -> dict:
        """Get scan statistics"""
        return {
            'files_scanned': self.files_scanned,
            'folders_scanned': self.folders_scanned,
            'errors_count': len(self.errors),
            'errors': self.errors
        }
    
    def _is_inventory_xml(self, filename: str) -> bool:
        """Check if a file is an inventory XML file"""
        return filename.endswith('.inventory.xml') or \
               filename.endswith('.inventory.file.xml') or \
               filename.endswith('.inventory.folder.xml')
    
    def _process_inventory_xml(self, xml_path: Path, filename: str, parent_path: str, root_path: Path):
        """Process an inventory XML file and extract metadata"""
        try:
            # Read metadata directly from the XML file using xml.etree
            import xml.etree.ElementTree as ET
            tree = ET.parse(str(xml_path))
            root = tree.getroot()
            
            # Extract metadata from XML
            comments_elem = root.find('comments')
            rating_elem = root.find('rating')
            comments = comments_elem.text if comments_elem is not None and comments_elem.text else ''
            rating = int(rating_elem.text) if rating_elem is not None and rating_elem.text else 0
            
            # Extract custom metadata
            custom = {}
            custom_elem = root.find('custom_metadata')
            if custom_elem is not None:
                for meta_elem in custom_elem:
                    key = meta_elem.get('key')
                    if key and meta_elem.text:
                        custom[key] = meta_elem.text
            
            # Determine the target file or folder
            target_name = self._get_target_filename(filename)
            is_folder = filename.endswith('.inventory.folder.xml')
            
            # Calculate relative path for the target
            target_path = xml_path.parent / target_name
            try:
                rel_path = str(target_path.relative_to(root_path))
            except ValueError:
                # If relative path calculation fails, skip
                return
            
            # Store the inventory XML info for later processing
            inventory_info = {
                'target_name': target_name,
                'target_path': rel_path,
                'is_folder': is_folder,
                'parent_path': parent_path,
                'comments': comments,
                'rating': rating,
                'custom': custom
            }
            self.inventory_xmls.append(inventory_info)
            
        except Exception as e:
            self.errors.append(f"Error processing inventory XML {xml_path}: {str(e)}")
    
    def _get_target_filename(self, xml_filename: str) -> str:
        """Extract the target filename from an inventory XML filename"""
        # Remove .inventory.xml, .inventory.file.xml, or .inventory.folder.xml
        if xml_filename.endswith('.inventory.folder.xml'):
            return xml_filename[:-len('.inventory.folder.xml')]
        elif xml_filename.endswith('.inventory.file.xml'):
            return xml_filename[:-len('.inventory.file.xml')]
        elif xml_filename.endswith('.inventory.xml'):
            return xml_filename[:-len('.inventory.xml')]
        return xml_filename
