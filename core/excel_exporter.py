"""
Módulo para exportar datos de la base de datos a archivos Excel (XLSX).
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from core.database import DatabaseManager


class ExcelExporter:
    """Clase para exportar datos de HDDInventory a Excel"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db = DatabaseManager(db_path)
        self.logger = logging.getLogger(__name__)

    def export_database(self, output_path: Path, max_level: int = None, progress_callback = None) -> bool:
        """
        Exporta toda la base de datos a un archivo XLSX.

        Args:
            output_path: Ruta donde guardar el archivo XLSX
            max_level: Nivel máximo de carpetas a exportar (None = todos los niveles)
            progress_callback: Función opcional para reportar progreso (recibe porcentaje 0-100)

        Returns:
            bool: True si la exportación fue exitosa
        """
        try:
            self.logger.info(f"Starting database export to {output_path}")

            # Crear workbook
            wb = Workbook()

            # Eliminar hoja por defecto
            wb.remove(wb.active)

            # Obtener todos los drives
            drives = self.db.get_all_drives()
            self.logger.info(f"Found {len(drives)} drives to export")

            # Reportar progreso inicial
            if progress_callback:
                progress_callback(5)

            # Crear hoja de índice de drives
            self._create_drives_index_sheet(wb, drives)
            
            if progress_callback:
                progress_callback(20)

            # Crear una hoja por cada drive con sus carpetas
            total_drives = len(drives)
            for i, drive in enumerate(drives):
                self._create_drive_folders_sheet(wb, drive, max_level)
                
                # Reportar progreso
                if progress_callback:
                    progress = 20 + (i + 1) * 70 // total_drives  # 20-90%
                    progress_callback(progress)

            # Guardar el archivo
            wb.save(output_path)
            
            if progress_callback:
                progress_callback(100)
                
            self.logger.info(f"Database export completed successfully: {output_path}")

            return True

        except Exception as e:
            self.logger.error(f"Error during database export: {e}")
            return False
        finally:
            if self.db:
                self.db.close()

    def _create_drives_index_sheet(self, wb: Workbook, drives: List[Dict[str, Any]]) -> None:
        """Crea la hoja de índice de unidades"""
        ws = wb.create_sheet("Drives Index")

        # Estilos
        header_font = Font(bold=True, size=12)
        header_fill = PatternFill(start_color="FF4472C4", end_color="FF4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")

        # Encabezados
        headers = ["Drive Label", "Drive Letter", "Total Files", "Total Folders", "Total Size", "Last Scanned"]
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment

        # Datos de drives
        for row_num, drive in enumerate(drives, 2):
            ws.cell(row=row_num, column=1, value=drive.get('drive_label', ''))
            ws.cell(row=row_num, column=2, value=drive.get('drive_letter', ''))

            # Obtener estadísticas del drive
            drive_stats = self._get_drive_stats(drive['id'])
            ws.cell(row=row_num, column=3, value=drive_stats.get('file_count', 0))
            ws.cell(row=row_num, column=4, value=drive_stats.get('folder_count', 0))
            ws.cell(row=row_num, column=5, value=self._format_file_size(drive_stats.get('total_size', 0)))
            ws.cell(row=row_num, column=6, value=drive.get('last_scanned', ''))

        # Autoajustar columnas
        self._auto_adjust_columns(ws)

        # Congelar fila de encabezados
        ws.freeze_panes = "A2"

    def _create_drive_folders_sheet(self, wb: Workbook, drive: Dict[str, Any], max_level: int = None) -> None:
        """Crea una hoja con las carpetas de un drive específico"""
        sheet_name = self._sanitize_sheet_name(drive.get('drive_label', f"Drive_{drive['id']}"))
        ws = wb.create_sheet(sheet_name)

        # Estilos
        header_font = Font(bold=True, size=12)
        header_fill = PatternFill(start_color="FF4472C4", end_color="FF4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        level_fill = PatternFill(start_color="FFE6E6FA", end_color="FFE6E6FA", fill_type="solid")

        # Encabezados
        headers = ["Level", "Folder Name", "Path", "File Count", "Subfolder Count", "Total Subfolders", "Total Size"]
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment

        # Obtener carpetas del drive
        folders = self.db.get_folders_by_drive(drive['id'], max_level)

        # Ordenar por path para mejor jerarquía visual
        folders.sort(key=lambda x: (x.get('level', 0), x.get('folder_path', ''), x.get('folder_name', '')))

        row_num = 2
        for folder in folders:
            level = folder.get('level', 0)
            folder_name = folder.get('folder_name', '')
            folder_path = folder.get('folder_path', '')
            file_count = folder.get('file_count', 0)
            subfolder_count = folder.get('subfolder_count', 0)
            total_subfolder_count = folder.get('total_subfolder_count', 0)
            total_size = folder.get('total_size', 0)

            # Aplicar indentación visual según el nivel
            indent = "  " * level
            display_name = f"{indent}{folder_name}"

            ws.cell(row=row_num, column=1, value=level)
            ws.cell(row=row_num, column=2, value=display_name)
            ws.cell(row=row_num, column=3, value=folder_path)
            ws.cell(row=row_num, column=4, value=file_count)
            ws.cell(row=row_num, column=5, value=subfolder_count)
            ws.cell(row=row_num, column=6, value=total_subfolder_count)
            ws.cell(row=row_num, column=7, value=self._format_file_size(total_size))

            # Resaltar niveles según profundidad
            if level == 0:
                # Nivel raíz - fondo ligeramente diferente
                for col in range(1, 8):
                    ws.cell(row=row_num, column=col).fill = level_fill

            row_num += 1

        # Autoajustar columnas
        self._auto_adjust_columns(ws)

        # Congelar fila de encabezados
        ws.freeze_panes = "A2"

    def _get_drive_stats(self, drive_id: int) -> Dict[str, Any]:
        """Obtiene estadísticas de un drive específico"""
        try:
            # Obtener estadísticas del drive desde la base de datos
            stats = self.db.get_drive_statistics(drive_id)
            return stats if stats else {}
        except Exception as e:
            self.logger.warning(f"Error getting drive stats for drive {drive_id}: {e}")
            return {}

    def _format_file_size(self, size_bytes: int) -> str:
        """Formatea el tamaño de archivo en formato legible"""
        if size_bytes == 0:
            return "0 B"

        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return ".1f"
            size_bytes /= 1024.0
        return ".1f"

    def _sanitize_sheet_name(self, name: str) -> str:
        """Sanea el nombre de la hoja para Excel (máximo 31 caracteres, sin caracteres especiales)"""
        # Remover caracteres no válidos para nombres de hoja
        invalid_chars = ['[', ']', ':', '*', '?', '/', '\\']
        sanitized = name
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')

        # Limitar a 31 caracteres
        if len(sanitized) > 31:
            sanitized = sanitized[:28] + "..."

        return sanitized if sanitized else "Drive"

    def _auto_adjust_columns(self, ws) -> None:
        """Autoajusta el ancho de las columnas basado en el contenido"""
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)

            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass

            # Establecer ancho mínimo y máximo
            adjusted_width = min(max(max_length + 2, 10), 50)
            ws.column_dimensions[column_letter].width = adjusted_width