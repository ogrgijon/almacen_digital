"""Helper utility functions"""

import psutil
from pathlib import Path
from typing import List, Dict, Optional
import humanize


def get_available_drives() -> List[Dict]:
    """Get list of available drives on the system"""
    drives = []
    
    for partition in psutil.disk_partitions(all=False):
        # Only include removable drives and fixed drives
        if 'removable' in partition.opts.lower() or 'fixed' in partition.opts.lower():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                # Get volume label
                drive_letter = partition.device.rstrip('\\')
                
                drive_info = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'opts': partition.opts,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent,
                    'total_human': humanize.naturalsize(usage.total),
                    'free_human': humanize.naturalsize(usage.free),
                }
                
                drives.append(drive_info)
            except (PermissionError, OSError):
                continue
    
    return drives


def get_drive_serial_number(drive_letter: str) -> Optional[str]:
    """Get serial number of a drive (Windows only)"""
    try:
        import ctypes
        import string
        
        # Ensure drive letter format
        if not drive_letter.endswith(':'):
            drive_letter = drive_letter.rstrip('\\') + ':'
        
        if not drive_letter.endswith('\\'):
            drive_letter += '\\'
        
        # Get volume information
        volumeNameBuffer = ctypes.create_unicode_buffer(1024)
        fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
        serial_number = ctypes.c_ulong(0)
        max_component_length = ctypes.c_ulong(0)
        file_system_flags = ctypes.c_ulong(0)
        
        result = ctypes.windll.kernel32.GetVolumeInformationW(
            drive_letter,
            volumeNameBuffer,
            ctypes.sizeof(volumeNameBuffer),
            ctypes.byref(serial_number),
            ctypes.byref(max_component_length),
            ctypes.byref(file_system_flags),
            fileSystemNameBuffer,
            ctypes.sizeof(fileSystemNameBuffer)
        )
        
        if result:
            return f"{serial_number.value:X}"
        else:
            return None
    
    except Exception as e:
        import logging
        logging.exception(f"Error getting drive serial: {e}")
        return None


def get_drive_label(drive_letter: str) -> str:
    """Get volume label of a drive"""
    try:
        import ctypes
        
        # Normalize drive letter format
        if not drive_letter:
            return "Unknown Drive"
        
        # Extract just the drive letter if it's a full path
        if '\\' in drive_letter:
            drive_letter = drive_letter.split('\\')[0]
        
        # Ensure format is "C:"
        if not drive_letter.endswith(':'):
            if len(drive_letter) == 1:
                drive_letter = drive_letter + ':'
            else:
                drive_letter = drive_letter.rstrip('\\').rstrip(':') + ':'
        
        # Add backslash for API call
        drive_path = drive_letter + '\\'
        
        volumeNameBuffer = ctypes.create_unicode_buffer(1024)
        fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
        serial_number = ctypes.c_ulong(0)
        max_component_length = ctypes.c_ulong(0)
        file_system_flags = ctypes.c_ulong(0)
        
        result = ctypes.windll.kernel32.GetVolumeInformationW(
            drive_path,
            volumeNameBuffer,
            ctypes.sizeof(volumeNameBuffer),
            ctypes.byref(serial_number),
            ctypes.byref(max_component_length),
            ctypes.byref(file_system_flags),
            fileSystemNameBuffer,
            ctypes.sizeof(fileSystemNameBuffer)
        )
        
        if result and volumeNameBuffer.value:
            return volumeNameBuffer.value
        else:
            # Return drive letter without label
            return f"Drive {drive_letter[0].upper()}"
    
    except Exception as e:
        import logging
        logging.exception(f"Error getting drive label for {drive_letter}: {e}")
        # Try to extract drive letter for fallback
        try:
            letter = drive_letter[0] if drive_letter else 'X'
            return f"Drive {letter.upper()}"
        except Exception:
            logging.exception("Unexpected error extracting fallback drive letter")
            return "Unknown Drive"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    return humanize.naturalsize(size_bytes)


def format_date(date_string: str) -> str:
    """Format ISO date string to readable format"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(date_string)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        import logging
        logging.exception("Error parsing date string")
        return date_string


def get_file_category(extension: str) -> str:
    """Get file category based on extension"""
    import config
    
    extension = extension.lower()
    
    for category, extensions in config.FILE_CATEGORIES.items():
        if extension in extensions:
            return category
    
    return 'Other'


def get_file_icon_char(extension: str) -> str:
    """Get emoji/character icon for file type"""
    category = get_file_category(extension)
    
    icons = {
        'Documents': '📄',
        'Images': '🖼️',
        'Audio': '🎵',
        'Video': '🎬',
        'Archives': '📦',
        'Code': '💻',
        'Other': '📎'
    }
    
    return icons.get(category, '📎')


def truncate_path(path: str, max_length: int = 50) -> str:
    """Truncate path with ellipsis if too long"""
    if len(path) <= max_length:
        return path
    
    # Try to keep filename
    parts = path.split('\\')
    if len(parts) > 1:
        filename = parts[-1]
        if len(filename) < max_length - 5:
            prefix_len = max_length - len(filename) - 5
            return path[:prefix_len] + '...' + '\\' + filename
    
    return path[:max_length - 3] + '...'


def find_smartctl():
    """Find smartctl executable in PATH or common locations."""
    import shutil
    import os
    # Check PATH
    path = shutil.which('smartctl')
    if path:
        return path
    # Check common locations on Windows
    common_paths = [
        r'C:\Program Files\smartmontools\bin\smartctl.exe',
        r'C:\Program Files (x86)\smartmontools\bin\smartctl.exe',
    ]
    for p in common_paths:
        if os.path.exists(p):
            return p
    return None
