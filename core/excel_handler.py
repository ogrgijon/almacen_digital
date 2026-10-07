"""Excel import/export handler"""

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import humanize


class ExcelHandler:
    """Handles Excel import/export operations"""
    
    @staticmethod
    def export_inventory(output_path: str, drives_data: List[Dict], 
                        db_manager, progress_callback=None) -> bool:
        """
        Export inventory to Excel file
        
        Args:
            output_path: Path to save Excel file
            drives_data: List of drive dictionaries
            db_manager: DatabaseManager instance
            progress_callback: Optional callback for progress updates
        
        Returns:
            True if successful
        """
        try:
            wb = Workbook()
            
            # Remove default sheet
            if 'Sheet' in wb.sheetnames:
                wb.remove(wb['Sheet'])
            
            # Create Index sheet
            index_sheet = wb.create_sheet("Index", 0)
            ExcelHandler._create_index_sheet(index_sheet, drives_data)
            
            # Create a sheet for each drive
            for idx, drive in enumerate(drives_data):
                if progress_callback:
                    progress_callback(idx + 1, len(drives_data), f"Exporting {drive['drive_label']}")
                
                # Get files for this drive
                files = db_manager.get_files_by_drive(drive['id'])
                
                # Create sheet with sanitized name
                sheet_name = ExcelHandler._sanitize_sheet_name(drive['drive_label'])
                sheet = wb.create_sheet(sheet_name)
                ExcelHandler._create_drive_sheet(sheet, files, drive)
            
            # Save workbook
            wb.save(output_path)
            return True
        
        except Exception as e:
            import logging
            logging.exception(f"Error exporting to Excel: {e}")
            return False
    
    @staticmethod
    def _create_index_sheet(sheet, drives_data: List[Dict]):
        """Create the index sheet with drive summary"""
        
        # Headers
        headers = ['Drive ID', 'Drive Name', 'Label', 'Capacity', 'Files', 'Folders', 
                  'Last Scan', 'Sheet Name']
        sheet.append(headers)
        
        # Style headers
        header_fill = PatternFill(start_color="D89000", end_color="D89000", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        # Add drive data
        for drive in drives_data:
            capacity = humanize.naturalsize(drive.get('capacity_bytes', 0))
            last_scan = drive.get('last_scan_date', 'Never')
            if last_scan and last_scan != 'Never':
                try:
                    dt = datetime.fromisoformat(last_scan)
                    last_scan = dt.strftime('%Y-%m-%d %H:%M')
                except:
                        import logging
                        logging.exception("Error parsing last_scan in Excel export")
            
            row = [
                drive.get('id', ''),
                drive.get('drive_label', ''),
                drive.get('drive_letter', ''),
                capacity,
                drive.get('file_count', 0),
                drive.get('folder_count', 0),
                last_scan,
                ExcelHandler._sanitize_sheet_name(drive.get('drive_label', ''))
            ]
            sheet.append(row)
        
        # Auto-adjust column widths
        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except Exception:
                    import logging
                    logging.exception("Error measuring cell value length for Excel export")
            adjusted_width = min(max_length + 2, 50)
            sheet.column_dimensions[column_letter].width = adjusted_width
    
    @staticmethod
    def _create_drive_sheet(sheet, files: List[Dict], drive_info: Dict):
        """Create a sheet for a single drive's files"""
        
        # Headers
        headers = ['Name', 'Path', 'Size', 'Size (Bytes)', 'Type', 'Modified Date', 'Created Date']
        sheet.append(headers)
        
        # Style headers
        header_fill = PatternFill(start_color="2D5D7B", end_color="2D5D7B", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        # Add file data
        for file_info in files:
            size_human = humanize.naturalsize(file_info.get('file_size', 0))
            modified = file_info.get('modified_date', '')
            if modified:
                try:
                    dt = datetime.fromisoformat(modified)
                    modified = dt.strftime('%Y-%m-%d %H:%M')
                except Exception:
                    import logging
                    logging.exception("Error parsing modified date in Excel export")
            
            created = file_info.get('created_date', '')
            if created:
                try:
                    dt = datetime.fromisoformat(created)
                    created = dt.strftime('%Y-%m-%d %H:%M')
                except Exception:
                    import logging
                    logging.exception("Error parsing created date in Excel export")
            
            row = [
                file_info.get('file_name', ''),
                file_info.get('file_path', ''),
                size_human,
                file_info.get('file_size', 0),
                file_info.get('file_extension', ''),
                modified,
                created
            ]
            sheet.append(row)
        
        # Auto-adjust column widths
        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except Exception:
                    import logging
                    logging.exception("Error measuring cell value length for Excel drive sheet")
            adjusted_width = min(max_length + 2, 80)
            sheet.column_dimensions[column_letter].width = adjusted_width
    
    @staticmethod
    def _sanitize_sheet_name(name: str) -> str:
        """Sanitize sheet name for Excel (max 31 chars, no special chars)"""
        # Remove invalid characters
        invalid_chars = ['\\', '/', '*', '?', ':', '[', ']']
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Limit to 31 characters
        if len(name) > 31:
            name = name[:31]
        
        return name or "Drive"
    
    @staticmethod
    def import_inventory(input_path: str, db_manager, progress_callback=None) -> Dict:
        """
        Import inventory from Excel file
        
        Args:
            input_path: Path to Excel file
            db_manager: DatabaseManager instance
            progress_callback: Optional callback for progress
        
        Returns:
            Dictionary with import statistics
        """
        try:
            wb = load_workbook(input_path, read_only=True)
            
            stats = {
                'drives_imported': 0,
                'files_imported': 0,
                'errors': []
            }
            
            # Read index sheet first
            if 'Index' not in wb.sheetnames:
                stats['errors'].append("No Index sheet found")
                return stats
            
            index_sheet = wb['Index']
            drive_mappings = {}
            
            # Skip header row
            for row in index_sheet.iter_rows(min_row=2, values_only=True):
                if not row[0]:  # Skip empty rows
                    continue
                
                drive_id = row[0]
                drive_label = row[1]
                drive_letter = row[2]
                sheet_name = row[7] if len(row) > 7 else drive_label
                
                drive_mappings[sheet_name] = {
                    'drive_id': drive_id,
                    'drive_label': drive_label,
                    'drive_letter': drive_letter
                }
            
            # Import each drive sheet
            for sheet_name in wb.sheetnames:
                if sheet_name == 'Index':
                    continue
                
                if sheet_name not in drive_mappings:
                    continue
                
                if progress_callback:
                    progress_callback(stats['drives_imported'], len(drive_mappings), f"Importing {sheet_name}")
                
                # Import drive data
                result = ExcelHandler._import_drive_sheet(
                    wb[sheet_name], 
                    drive_mappings[sheet_name],
                    db_manager
                )
                
                stats['drives_imported'] += 1
                stats['files_imported'] += result['files_imported']
                stats['errors'].extend(result['errors'])
            
            return stats
        
        except Exception as e:
            return {
                'drives_imported': 0,
                'files_imported': 0,
                'errors': [f"Import failed: {str(e)}"]
            }
    
    @staticmethod
    def _import_drive_sheet(sheet, drive_info: Dict, db_manager) -> Dict:
        """Import a single drive sheet"""
        
        result = {
            'files_imported': 0,
            'errors': []
        }
        
        try:
            # Add or update drive
            drive_id = db_manager.add_drive(
                drive_letter=drive_info['drive_letter'],
                drive_label=drive_info['drive_label'],
                serial_number=f"IMPORTED_{drive_info['drive_id']}",
                capacity_bytes=0
            )
            
            # Clear existing files for this drive
            db_manager.clear_files_by_drive(drive_id)
            
            # Import files (batch for performance)
            files_batch = []
            
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row[0]:  # Skip empty rows
                    continue
                
                try:
                    file_name = row[0]
                    file_path = row[1]
                    file_size = row[3] if len(row) > 3 else 0
                    file_extension = row[4] if len(row) > 4 else ''
                    modified_date = row[5] if len(row) > 5 else ''
                    created_date = row[6] if len(row) > 6 else ''
                    
                    files_batch.append((
                        drive_id, file_name, file_path, file_size,
                        file_extension, modified_date, created_date, None
                    ))
                    
                    # Batch insert every 1000 files
                    if len(files_batch) >= 1000:
                        db_manager.add_files_batch(files_batch)
                        result['files_imported'] += len(files_batch)
                        files_batch = []
                
                except Exception as e:
                    result['errors'].append(f"Error importing file: {str(e)}")
            
            # Insert remaining files
            if files_batch:
                db_manager.add_files_batch(files_batch)
                result['files_imported'] += len(files_batch)
            
            # Update drive counts
            db_manager.update_drive_counts(drive_id)
        
        except Exception as e:
            result['errors'].append(f"Error importing drive: {str(e)}")
        
        return result
