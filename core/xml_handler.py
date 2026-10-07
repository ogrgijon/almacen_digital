"""XML metadata handler for drive sync"""

import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import config


class XMLHandler:
    """Handles XML metadata files on drives"""
    
    @staticmethod
    def create_metadata(drive_path: str, drive_info: Dict) -> bool:
        """
        Create XML metadata file on drive
        
        Args:
            drive_path: Root path of drive (e.g., "E:\\")
            drive_info: Dictionary with drive information
        
        Returns:
            True if successful, False otherwise
        """
        try:
            xml_path = Path(drive_path) / config.XML_METADATA_FILENAME
            
            # Create XML structure
            root = ET.Element("drive_inventory")
            
            # Add drive information
            ET.SubElement(root, "drive_id").text = str(drive_info.get('id', ''))
            ET.SubElement(root, "serial_number").text = drive_info.get('serial_number', '')
            ET.SubElement(root, "drive_name").text = drive_info.get('drive_label', '')
            ET.SubElement(root, "last_scan").text = datetime.now().isoformat()
            ET.SubElement(root, "total_files").text = str(drive_info.get('file_count', 0))
            ET.SubElement(root, "total_folders").text = str(drive_info.get('folder_count', 0))
            ET.SubElement(root, "capacity_bytes").text = str(drive_info.get('capacity_bytes', 0))
            
            # Create tree and write to file
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")
            tree.write(str(xml_path), encoding='utf-8', xml_declaration=True)
            
            # Hide the file on Windows
            try:
                import ctypes
                FILE_ATTRIBUTE_HIDDEN = 0x02
                ctypes.windll.kernel32.SetFileAttributesW(str(xml_path), FILE_ATTRIBUTE_HIDDEN)
            except Exception:
                import logging
                logging.exception("Failed to hide XML metadata file (non-critical)")
            
            return True
        
        except Exception as e:
            import logging
            logging.exception(f"Error creating XML metadata: {e}")
            return False
    
    @staticmethod
    def read_metadata(drive_path: str) -> Optional[Dict]:
        """
        Read XML metadata from drive
        
        Args:
            drive_path: Root path of drive
        
        Returns:
            Dictionary with metadata or None if not found/error
        """
        try:
            xml_path = Path(drive_path) / config.XML_METADATA_FILENAME
            
            if not xml_path.exists():
                return None
            
            tree = ET.parse(str(xml_path))
            root = tree.getroot()
            
            metadata = {}
            for child in root:
                metadata[child.tag] = child.text
            
            return metadata
        
        except Exception as e:
            import logging
            logging.exception(f"Error reading XML metadata: {e}")
            return None
    
    @staticmethod
    def update_metadata(drive_path: str, drive_info: Dict) -> bool:
        """
        Update existing XML metadata
        
        Args:
            drive_path: Root path of drive
            drive_info: Updated drive information
        
        Returns:
            True if successful
        """
        # Simply recreate the file
        return XMLHandler.create_metadata(drive_path, drive_info)
    
    @staticmethod
    def metadata_exists(drive_path: str) -> bool:
        """Check if metadata file exists on drive"""
        xml_path = Path(drive_path) / config.XML_METADATA_FILENAME
        return xml_path.exists()
    
    @staticmethod
    def get_last_scan_date(drive_path: str) -> Optional[str]:
        """Get last scan date from metadata"""
        metadata = XMLHandler.read_metadata(drive_path)
        if metadata:
            return metadata.get('last_scan')
        return None
