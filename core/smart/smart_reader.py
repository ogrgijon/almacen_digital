"""
smart_reader.py - S.M.A.R.T. data access utility

Provides functions to fetch S.M.A.R.T. health and attributes for a given drive.
Supports Windows (smartctl required in PATH).
"""
import subprocess
import ctypes
import re
from typing import Dict, Optional

class SmartStatus:
    OK = 'OK'
    CAUTION = 'CAUTION'
    FAILING = 'FAILING'
    UNKNOWN = 'UNKNOWN'
    NOT_SUPPORTED = 'NOT_SUPPORTED'


def normalize_drive_letter(drive_letter: str) -> Optional[str]:
    """Return a canonical drive letter or None for invalid input."""
    if not isinstance(drive_letter, str):
        return None

    match = re.fullmatch(r'\s*([A-Za-z]):\\?\s*', drive_letter)
    return f'{match.group(1).upper()}:' if match else None


def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except (AttributeError, OSError):
        return False


def get_physical_drive_number(drive_letter: str) -> Optional[int]:
    """Get the physical drive number for a given drive letter."""
    normalized_drive_letter = normalize_drive_letter(drive_letter)
    if normalized_drive_letter is None:
        return None

    try:
        # Pass the drive letter as an argument instead of interpolating it into PowerShell.
        command = (
            'param([string]$DriveLetter) '
            '(Get-Partition -DriveLetter $DriveLetter | '
            'Select-Object -ExpandProperty DiskNumber)'
        )
        result = subprocess.run(
            [
                'powershell.exe',
                '-NoProfile',
                '-NonInteractive',
                '-Command',
                command,
                normalized_drive_letter[0],
            ],
            capture_output=True,
            text=True,
            timeout=5,
            shell=False,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            disk_number = int(result.stdout.strip())
            return disk_number if disk_number >= 0 else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    return None


def get_smart_status(drive_letter: str, smartctl_path: str = 'smartctl') -> Dict[str, Optional[str]]:
    """
    Fetch S.M.A.R.T. health status and key attributes for a drive.
    Returns a dict: { 'status': SmartStatus, 'attributes': { ... } }
    """
    # Check if running as admin
    if not is_admin():
        return {'status': SmartStatus.NOT_SUPPORTED, 'attributes': {}, 'error': 'Administrator privileges required'}
    
    # Get physical drive number
    disk_num = get_physical_drive_number(drive_letter)
    if disk_num is None:
        return {'status': SmartStatus.NOT_SUPPORTED, 'attributes': {}, 'error': 'Could not map drive letter to physical disk'}
    
    # Try different device types with physical drive path
    device_options = [
        [],  # Default
        ['-d', 'sat'],  # SAT (SCSI-to-ATA Translation) - common for USB/external drives
        ['-d', 'ata'],  # ATA/SATA
        ['-d', 'nvme'],  # NVMe drives
        ['-d', 'scsi'],  # SCSI
    ]
    
    for options in device_options:
        # Use /dev/pd notation which smartctl understands on Windows
        cmd = [smartctl_path, '-a'] + options + [f'/dev/pd{disk_num}']
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = result.stdout + result.stderr
            
            # Check for success (return code 0 or specific SMART warnings)
            # smartctl can return non-zero for drives with warnings but still provide data
            if 'Unable to detect device type' not in output and 'Open failed' not in output:
                # Parse SMART status
                if 'SMART overall-health self-assessment test result: PASSED' in output:
                    status = SmartStatus.OK
                elif 'SMART overall-health self-assessment test result: FAILED' in output:
                    status = SmartStatus.FAILING
                elif 'CAUTION' in output or 'WARNING' in output:
                    status = SmartStatus.CAUTION
                elif 'SMART support is: Enabled' in output or 'SMART support is: Available' in output:
                    # SMART is supported but we couldn't determine health
                    status = SmartStatus.UNKNOWN
                else:
                    continue  # Try next device type
                
                # Parse key attributes
                attributes = {}
                for line in output.splitlines():
                    parts = line.split()
                    if len(parts) > 9:
                        if 'Reallocated_Sector_Ct' in line:
                            attributes['Reallocated_Sector_Ct'] = parts[9]
                        elif 'Temperature_Celsius' in line or 'Airflow_Temperature_Cel' in line:
                            attributes['Temperature_Celsius'] = parts[9]
                        elif 'Power_On_Hours' in line:
                            attributes['Power_On_Hours'] = parts[9]
                
                return {'status': status, 'attributes': attributes}
        except Exception as e:
            continue
    
    # If all attempts failed
    return {'status': SmartStatus.NOT_SUPPORTED, 'attributes': {}, 'error': 'Drive does not support SMART or is not accessible'}
