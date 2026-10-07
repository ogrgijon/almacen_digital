"""XML metadata handler for file comments and ratings.

This module handles reading and writing XML metadata files that store
comments and ratings for files alongside the original files.
"""

import os
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, Dict


class FileMetadataHandler:
    """Handles XML metadata files for file comments and ratings"""
    
    @staticmethod
    def get_metadata_file_path(file_path: str, is_folder: bool = False) -> str:
        """Get the path for the metadata XML file"""
        dir_path = os.path.dirname(file_path) if not is_folder else file_path
        filename = os.path.basename(file_path)
        
        if is_folder:
            return os.path.join(dir_path, f"{filename}.inventory.folder.xml")
        else:
            return os.path.join(dir_path, f"{filename}.inventory.file.xml")
    
    @staticmethod
    def read_metadata(file_path: str, is_folder: bool = False) -> Dict[str, any]:
        """Read metadata from XML file"""
        xml_path = FileMetadataHandler.get_metadata_file_path(file_path, is_folder)
        
        if not os.path.exists(xml_path):
            return {'comments': '', 'rating': 0, 'custom': {}}
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            comments = root.find('comments')
            rating = root.find('rating')
            
            # Read custom metadata
            custom = {}
            custom_elem = root.find('custom_metadata')
            if custom_elem is not None:
                for meta_elem in custom_elem:
                    key = meta_elem.get('key')
                    if key and meta_elem.text:
                        custom[key] = meta_elem.text
            
            return {
                'comments': comments.text if comments is not None and comments.text else '',
                'rating': int(rating.text) if rating is not None and rating.text else 0,
                'custom': custom
            }
        except (ET.ParseError, ValueError, OSError) as e:
            print(f"Error reading metadata file {xml_path}: {e}")
            return {'comments': '', 'rating': 0, 'custom': {}}
    
    @staticmethod
    def write_metadata(file_path: str, comments: str, rating: int, is_folder: bool = False, custom_metadata: Dict[str, str] = None) -> bool:
        """Write metadata to XML file"""
        xml_path = FileMetadataHandler.get_metadata_file_path(file_path, is_folder)
        
        try:
            # Create root element
            root = ET.Element("file_metadata")
            root.set("version", "1.0")
            root.set("created", datetime.now().isoformat())
            root.set("file_path", file_path)
            
            # Add comments
            comments_elem = ET.SubElement(root, "comments")
            comments_elem.text = comments or ""
            
            # Add rating
            rating_elem = ET.SubElement(root, "rating")
            rating_elem.text = str(max(0, min(5, rating)))  # Ensure 0-5 range
            
            # Add custom metadata
            if custom_metadata:
                custom_elem = ET.SubElement(root, "custom_metadata")
                for key, value in custom_metadata.items():
                    meta_elem = ET.SubElement(custom_elem, "meta")
                    meta_elem.set("key", key)
                    meta_elem.text = value or ""
            
            # Write to file with pretty formatting
            tree = ET.ElementTree(root)
            tree.write(xml_path, encoding='utf-8', xml_declaration=True)
            
            return True
        except OSError as e:
            print(f"Error writing metadata file {xml_path}: {e}")
            return False
    
    @staticmethod
    def delete_metadata(file_path: str, is_folder: bool = False) -> bool:
        """Delete metadata XML file"""
        xml_path = FileMetadataHandler.get_metadata_file_path(file_path, is_folder)
        
        try:
            if os.path.exists(xml_path):
                os.remove(xml_path)
            return True
        except OSError as e:
            print(f"Error deleting metadata file {xml_path}: {e}")
            return False
    
    @staticmethod
    def has_metadata(file_path: str, is_folder: bool = False) -> bool:
        """Check if file has metadata"""
        xml_path = FileMetadataHandler.get_metadata_file_path(file_path, is_folder)
        return os.path.exists(xml_path)