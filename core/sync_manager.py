"""
Módulo de sincronización de base de datos.
Permite sincronizar la base de datos local con una copia de respaldo
en directorios compartidos (Google Drive, OneDrive, etc.).
"""

import os
import shutil
import sqlite3
import logging
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime


class SyncManager:
    """
    Gestiona la sincronización de la base de datos con copias de respaldo.
    """
    
    def __init__(self, local_db_path: str):
        """
        Inicializa el gestor de sincronización.
        
        Args:
            local_db_path: Ruta a la base de datos local
        """
        self.local_db_path = Path(local_db_path)
        self.logger = logging.getLogger(__name__)
    
    def get_db_metadata(self, db_path: Path) -> Optional[Tuple[str, int, datetime]]:
        """
        Obtiene los metadatos de sincronización de una base de datos.
        
        Args:
            db_path: Ruta a la base de datos
            
        Returns:
            Tupla (unique_id, version, last_modified) o None si no existe
        """
        try:
            if not db_path.exists():
                return None
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Verificar si existe la tabla de metadatos
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='sync_metadata'
            """)
            
            if not cursor.fetchone():
                conn.close()
                return None
            
            # Obtener metadatos
            cursor.execute("""
                SELECT unique_id, version, last_modified 
                FROM sync_metadata 
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                unique_id, version, last_modified_str = row
                last_modified = datetime.fromisoformat(last_modified_str)
                return (unique_id, version, last_modified)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting metadata from {db_path}: {e}")
            return None
    
    def should_sync(self, backup_path: Path) -> Tuple[bool, str]:
        """
        Determina si se debe realizar la sincronización.
        
        Args:
            backup_path: Ruta al archivo de respaldo
            
        Returns:
            Tupla (should_sync, reason) donde should_sync es True si debe sincronizar
        """
        # Verificar si existe el respaldo
        if not backup_path.exists():
            return (False, "Backup file does not exist")
        
        # Obtener metadatos local y del respaldo
        local_meta = self.get_db_metadata(self.local_db_path)
        backup_meta = self.get_db_metadata(backup_path)
        
        # Si no hay metadatos en el respaldo, no sincronizar
        if not backup_meta:
            return (False, "Backup has no sync metadata")
        
        # Si no hay metadatos locales, sincronizar
        if not local_meta:
            return (True, "Local database has no metadata - will sync from backup")
        
        local_id, local_version, local_modified = local_meta
        backup_id, backup_version, backup_modified = backup_meta
        
        # Verificar que sean del mismo inventario
        if local_id != backup_id:
            return (False, f"Different inventory IDs (local: {local_id}, backup: {backup_id})")
        
        # Comparar versiones
        if backup_version > local_version:
            return (True, f"Backup is newer (v{backup_version} > v{local_version})")
        
        if backup_version == local_version:
            # Comparar fechas de modificación
            if backup_modified > local_modified:
                return (True, f"Backup modified more recently ({backup_modified} > {local_modified})")
        
        return (False, f"Local database is up to date (v{local_version})")
    
    def sync_from_backup(self, backup_path: Path) -> bool:
        """
        Sincroniza la base de datos local desde el respaldo.
        
        Args:
            backup_path: Ruta al archivo de respaldo
            
        Returns:
            True si la sincronización fue exitosa
        """
        try:
            # Crear respaldo de la base de datos actual
            if self.local_db_path.exists():
                backup_local = self.local_db_path.with_suffix('.db.bak')
                shutil.copy2(self.local_db_path, backup_local)
                self.logger.info(f"Created local backup at {backup_local}")
            
            # Copiar el respaldo a la ubicación local
            shutil.copy2(backup_path, self.local_db_path)
            self.logger.info(f"Synced database from {backup_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error syncing from backup: {e}")
            return False
    
    def sync_to_backup(self, backup_path: Path) -> bool:
        """
        Sincroniza la base de datos local al respaldo.
        
        Args:
            backup_path: Ruta al archivo de respaldo
            
        Returns:
            True si la sincronización fue exitosa
        """
        try:
            # Crear directorio del respaldo si no existe
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copiar la base de datos local al respaldo
            shutil.copy2(self.local_db_path, backup_path)
            self.logger.info(f"Synced database to {backup_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error syncing to backup: {e}")
            return False
    
    def auto_sync(self, backup_path: Path, direction: str = "bidirectional") -> Tuple[bool, str]:
        """
        Realiza sincronización automática basada en la dirección especificada.
        
        Args:
            backup_path: Ruta al archivo de respaldo
            direction: "from_backup", "to_backup", o "bidirectional"
            
        Returns:
            Tupla (success, message)
        """
        try:
            if direction == "from_backup":
                # Solo desde respaldo
                should_sync, reason = self.should_sync(backup_path)
                if should_sync:
                    if self.sync_from_backup(backup_path):
                        return (True, f"Synced from backup: {reason}")
                    else:
                        return (False, "Failed to sync from backup")
                else:
                    return (False, f"No sync needed: {reason}")
            
            elif direction == "to_backup":
                # Solo hacia respaldo
                if self.sync_to_backup(backup_path):
                    return (True, "Synced to backup")
                else:
                    return (False, "Failed to sync to backup")
            
            elif direction == "bidirectional":
                # Bidireccional - elegir la versión más reciente
                should_sync, reason = self.should_sync(backup_path)
                
                if should_sync:
                    # El respaldo es más nuevo
                    if self.sync_from_backup(backup_path):
                        return (True, f"Synced from backup: {reason}")
                    else:
                        return (False, "Failed to sync from backup")
                else:
                    # Local es más nuevo o igual - actualizar respaldo
                    local_meta = self.get_db_metadata(self.local_db_path)
                    backup_meta = self.get_db_metadata(backup_path)
                    
                    if local_meta and (not backup_meta or local_meta[1] >= backup_meta[1]):
                        if self.sync_to_backup(backup_path):
                            return (True, "Synced to backup (local is newer)")
                        else:
                            return (False, "Failed to sync to backup")
                    else:
                        return (False, f"No sync needed: {reason}")
            
            else:
                return (False, f"Invalid sync direction: {direction}")
                
        except Exception as e:
            self.logger.error(f"Error in auto_sync: {e}")
            return (False, f"Sync error: {str(e)}")
