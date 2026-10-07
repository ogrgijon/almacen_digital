"""SQLite database manager for drive inventory"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import config


class DatabaseManager:
    """Manages SQLite database operations for drive inventory"""
    
    def get_folder_size_hierarchy(self, drive_id: int, parent_folder_id: Optional[int] = None, max_depth: int = 3, max_folders: int = 1000) -> list:
        """
        Recursively get folder/file sizes for a drive, starting from parent_folder_id (None=root).
        Returns a list of dicts: { 'name': str, 'size': int, 'children': [ ... ] }
        Limits depth for performance and total folders to prevent excessive processing.
        """
        if not hasattr(self, '_folder_count'):
            self._folder_count = 0
        if self._folder_count > max_folders:
            return []  # Stop processing if we've hit the limit
        # Get folders at this level
        if parent_folder_id is None:
            self.cursor.execute("SELECT id, folder_name FROM folders WHERE drive_id = ? AND (parent_folder_id IS NULL OR parent_folder_id = 0)", (drive_id,))
        else:
            self.cursor.execute("SELECT id, folder_name FROM folders WHERE drive_id = ? AND parent_folder_id = ?", (drive_id, parent_folder_id))
        folders = self.cursor.fetchall()

        result = []
        for folder in folders:
            if self._folder_count > max_folders:
                break
            self._folder_count += 1
            folder_id = folder['id']
            folder_name = folder['folder_name']
            # Get total size of files directly in this folder
            self.cursor.execute("SELECT SUM(file_size) as total FROM files WHERE drive_id = ? AND parent_folder_id = ?", (drive_id, folder_id))
            file_size = self.cursor.fetchone()['total'] or 0
            # Recurse for subfolders
            children = []
            if max_depth > 0:
                children = self.get_folder_size_hierarchy(drive_id, folder_id, max_depth-1, max_folders)
                # Add up all children sizes
                children_size = sum(child['size'] for child in children)
            else:
                children_size = 0
            total_size = file_size + children_size
            result.append({
                'name': folder_name,
                'size': total_size,
                'children': children
            })
        # Add files directly in this level (not in any folder, e.g. root)
        if parent_folder_id is None:
            self.cursor.execute("SELECT file_name, file_size FROM files WHERE drive_id = ? AND (parent_folder_id IS NULL OR parent_folder_id = 0)", (drive_id,))
            files = self.cursor.fetchall()
            for f in files:
                result.append({'name': f['file_name'], 'size': f['file_size'] or 0, 'children': []})
        return result
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database manager with optional custom path"""
        self.db_path = db_path or config.DATABASE_PATH
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self._connect()
        try:
            self._create_tables()
        except Exception as e:
            print(f"Database initialization error: {e}")
            raise
    
    def _connect(self):
        """Connect to SQLite database with optimized settings"""
        self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        
        # Enable optimizations
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.cursor.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for better concurrency
        self.cursor.execute("PRAGMA synchronous = NORMAL")  # Faster writes, still safe
        self.cursor.execute("PRAGMA cache_size = -64000")  # 64MB cache
        self.cursor.execute("PRAGMA temp_store = MEMORY")  # Keep temp tables in memory
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        
        # Drives table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS drives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drive_letter TEXT,
                drive_label TEXT,
                serial_number TEXT UNIQUE,
                capacity_bytes INTEGER,
                free_space_bytes INTEGER,
                last_scan_date TEXT,
                file_count INTEGER DEFAULT 0,
                folder_count INTEGER DEFAULT 0,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Folders table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drive_id INTEGER NOT NULL,
                folder_name TEXT NOT NULL,
                folder_path TEXT NOT NULL,
                parent_folder_id INTEGER,
                level INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (drive_id) REFERENCES drives(id) ON DELETE CASCADE
            )
        """)
        
        # Files table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drive_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                file_extension TEXT,
                modified_date TEXT,
                created_date TEXT,
                parent_folder_id INTEGER,
                comments TEXT,
                rating INTEGER DEFAULT 0,
                FOREIGN KEY (drive_id) REFERENCES drives(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_folder_id) REFERENCES folders(id) ON DELETE CASCADE
            )
        """)
        
        # Tags table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE NOT NULL,
                color TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # File tags junction table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_tags (
                file_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (file_id, tag_id),
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)
        
        # Custom metadata table for flexible key-value metadata
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                meta_key TEXT NOT NULL,
                meta_value TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                UNIQUE(file_id, meta_key)
            )
        """)
        
        # Create indexes for performance
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_name ON files(file_name)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_extension ON files(file_extension)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_size ON files(file_size)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_drive ON files(drive_id)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_modified ON files(modified_date)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_folders_parent ON folders(parent_folder_id)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_folders_drive_parent ON folders(drive_id, parent_folder_id)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_parent ON files(parent_folder_id)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_drive_parent ON files(drive_id, parent_folder_id)
        """)
        
        # Sync metadata table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_metadata (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                unique_id TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                last_modified TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
        
        # Initialize sync metadata if not exists
        self._initialize_sync_metadata()
        
        # Run migrations for existing databases
        self._run_migrations()
    
    def _initialize_sync_metadata(self):
        """Initialize sync metadata if it doesn't exist"""
        import uuid
        from datetime import datetime
        
        self.cursor.execute("SELECT COUNT(*) FROM sync_metadata")
        if self.cursor.fetchone()[0] == 0:
            unique_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            self.cursor.execute("""
                INSERT INTO sync_metadata (id, unique_id, version, last_modified)
                VALUES (1, ?, 1, ?)
            """, (unique_id, now))
            self.connection.commit()
    
    def _run_migrations(self):
        """Run database migrations for existing databases"""
        try:
            # Check drives table columns
            self.cursor.execute("PRAGMA table_info(drives)")
            drive_columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'free_space_bytes' not in drive_columns:
                print("Adding free_space_bytes column to drives table...")
                self.cursor.execute("ALTER TABLE drives ADD COLUMN free_space_bytes INTEGER")
            
            # Check if comments column exists, add it if not
            self.cursor.execute("PRAGMA table_info(files)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'comments' not in columns:
                print("Adding comments column to files table...")
                self.cursor.execute("ALTER TABLE files ADD COLUMN comments TEXT")
            
            if 'rating' not in columns:
                print("Adding rating column to files table...")
                self.cursor.execute("ALTER TABLE files ADD COLUMN rating INTEGER DEFAULT 0")
            
            # Check if file_metadata table exists
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='file_metadata'")
            if not self.cursor.fetchone():
                print("Creating file_metadata table...")
                self.cursor.execute("""
                    CREATE TABLE file_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_id INTEGER NOT NULL,
                        meta_key TEXT NOT NULL,
                        meta_value TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                        UNIQUE(file_id, meta_key)
                    )
                """)
            
            self.connection.commit()
        except Exception as e:
            print(f"Error running migrations: {e}")
    
    # ==================== DRIVE OPERATIONS ====================
    
    def add_drive(self, drive_letter: str, drive_label: str, serial_number: str, 
                  capacity_bytes: int, notes: str = "", free_space_bytes: Optional[int] = None) -> int:
        """Add a new drive to inventory"""
        try:
            self.cursor.execute("""
                INSERT INTO drives (drive_letter, drive_label, serial_number, 
                                  capacity_bytes, free_space_bytes, notes, last_scan_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (drive_letter, drive_label, serial_number, capacity_bytes, 
                  free_space_bytes, notes, datetime.now().isoformat()))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Drive with this serial number already exists, update it
            return self.update_drive_by_serial(serial_number, drive_letter, drive_label, capacity_bytes, free_space_bytes)
    
    def update_drive_by_serial(self, serial_number: str, drive_letter: str, 
                              drive_label: str, capacity_bytes: int, free_space_bytes: Optional[int] = None) -> Optional[int]:
        """Update existing drive information"""
        self.cursor.execute("""
            UPDATE drives 
            SET drive_letter = ?, drive_label = ?, capacity_bytes = ?, free_space_bytes = ?, last_scan_date = ?
            WHERE serial_number = ?
        """, (drive_letter, drive_label, capacity_bytes, free_space_bytes, datetime.now().isoformat(), serial_number))
        self.connection.commit()
        
        # Return the drive ID
        self.cursor.execute("SELECT id FROM drives WHERE serial_number = ?", (serial_number,))
        result = self.cursor.fetchone()
        return result['id'] if result else None
    
    def get_all_drives(self) -> List[Dict]:
        """Get all drives in inventory"""
        try:
            self.cursor.execute("""
                SELECT * FROM drives ORDER BY last_scan_date DESC
            """)
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching drives: {e}")
            return []
    
    def get_drive_by_id(self, drive_id: int) -> Optional[Dict]:
        """Get drive by ID"""
        self.cursor.execute("SELECT * FROM drives WHERE id = ?", (drive_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_drive_by_serial(self, serial_number: str) -> Optional[Dict]:
        """Get drive by serial number"""
        self.cursor.execute("SELECT * FROM drives WHERE serial_number = ?", (serial_number,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def delete_drive(self, drive_id: int):
        """Delete drive and all associated data"""
        self.cursor.execute("DELETE FROM drives WHERE id = ?", (drive_id,))
        self.connection.commit()
    
    def update_drive_notes(self, drive_id: int, notes: str):
        """Update notes for a drive"""
        self.cursor.execute("""
            UPDATE drives SET notes = ?, last_scan_date = ?
            WHERE id = ?
        """, (notes, datetime.now().isoformat(), drive_id))
        self.connection.commit()
    
    def update_drive_counts(self, drive_id: int):
        """Update file and folder counts for a drive"""
        # Count files
        self.cursor.execute("SELECT COUNT(*) as count FROM files WHERE drive_id = ?", (drive_id,))
        file_count = self.cursor.fetchone()['count']
        
        # Count folders
        self.cursor.execute("SELECT COUNT(*) as count FROM folders WHERE drive_id = ?", (drive_id,))
        folder_count = self.cursor.fetchone()['count']
        
        # Update drive
        self.cursor.execute("""
            UPDATE drives SET file_count = ?, folder_count = ?, last_scan_date = ?
            WHERE id = ?
        """, (file_count, folder_count, datetime.now().isoformat(), drive_id))
        self.connection.commit()
    
    # ==================== FOLDER OPERATIONS ====================
    
    def add_folder(self, drive_id: int, folder_name: str, folder_path: str, 
                   parent_folder_id: Optional[int] = None, level: int = 0) -> int:
        """Add a folder to inventory"""
        self.cursor.execute("""
            INSERT INTO folders (drive_id, folder_name, folder_path, parent_folder_id, level)
            VALUES (?, ?, ?, ?, ?)
        """, (drive_id, folder_name, folder_path, parent_folder_id, level))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def add_folders_batch(self, folders: List[tuple]) -> List[int]:
        """Add multiple folders at once for better performance and return their IDs"""
        if not folders:
            return []
        
        # Insert folders
        self.cursor.executemany("""
            INSERT INTO folders (drive_id, folder_name, folder_path, parent_folder_id, level)
            VALUES (?, ?, ?, ?, ?)
        """, folders)
        
        # Get the IDs of the inserted folders
        # Since executemany doesn't return IDs directly, we need to query them back
        # This assumes the folders were inserted in order and we can get the last N IDs
        folder_count = len(folders)
        self.cursor.execute("""
            SELECT id FROM folders 
            WHERE drive_id = ? 
            ORDER BY id DESC 
            LIMIT ?
        """, (folders[0][0], folder_count))  # folders[0][0] is drive_id
        
        inserted_ids = [row['id'] for row in self.cursor.fetchall()]
        inserted_ids.reverse()  # Reverse to match insertion order
        
        self.connection.commit()
        return inserted_ids
    
    def get_folders_by_drive(self, drive_id: int, max_level: int = None, limit: int = None, offset: int = None) -> List[Dict]:
        """Get all folders for a drive with statistics, optionally limited by level and pagination"""
        # First get all folders
        level_filter = " AND f.level <= ?" if max_level is not None else ""
        limit_clause = " LIMIT ? OFFSET ?" if limit is not None and offset is not None else ""
        
        params = [drive_id]
        if max_level is not None:
            params.append(max_level)
        if limit is not None and offset is not None:
            params.extend([limit, offset])
            
        self.cursor.execute(f"""
            SELECT f.* FROM folders f
            WHERE f.drive_id = ? {level_filter}
            ORDER BY f.level, f.folder_path, f.folder_name
            {limit_clause}
        """, params)
        
        folders = [dict(row) for row in self.cursor.fetchall()]
        
        # Calculate statistics for each folder
        for folder in folders:
            folder_id = folder['id']
            folder_path = folder['folder_path']
            
            # Count direct files in this folder
            self.cursor.execute("""
                SELECT COUNT(*) as file_count, COALESCE(SUM(file_size), 0) as total_size
                FROM files 
                WHERE drive_id = ? AND parent_folder_id = ?
            """, (drive_id, folder_id))
            
            file_stats = self.cursor.fetchone()
            folder['file_count'] = file_stats['file_count'] if file_stats else 0
            folder['total_size'] = file_stats['total_size'] if file_stats else 0
            
            # Count subfolders (direct children)
            self.cursor.execute("""
                SELECT COUNT(*) as subfolder_count
                FROM folders 
                WHERE drive_id = ? AND parent_folder_id = ?
            """, (drive_id, folder_id))
            
            subfolder_stats = self.cursor.fetchone()
            folder['subfolder_count'] = subfolder_stats['subfolder_count'] if subfolder_stats else 0
            
            # Count total subfolders recursively (all descendants)
            self.cursor.execute("""
                WITH RECURSIVE folder_tree AS (
                    SELECT id FROM folders WHERE id = ?
                    UNION ALL
                    SELECT f.id FROM folders f
                    INNER JOIN folder_tree ft ON f.parent_folder_id = ft.id
                )
                SELECT COUNT(*) - 1 as total_subfolder_count FROM folder_tree
            """, (folder_id,))
            
            total_subfolder_stats = self.cursor.fetchone()
            folder['total_subfolder_count'] = total_subfolder_stats['total_subfolder_count'] if total_subfolder_stats else 0
        
        return folders
    
    def get_folders_count_by_drive(self, drive_id: int, max_level: int = None) -> int:
        """Get total count of folders for a drive, optionally limited by level"""
        level_filter = " AND level <= ?" if max_level is not None else ""
        params = [drive_id]
        if max_level is not None:
            params.append(max_level)
            
        self.cursor.execute(f"""
            SELECT COUNT(*) as count FROM folders
            WHERE drive_id = ? {level_filter}
        """, params)
        
        result = self.cursor.fetchone()
        return result['count'] if result else 0
    
    def clear_folders_by_drive(self, drive_id: int):
        """Clear all folders for a drive (used before rescan)"""
        self.cursor.execute("DELETE FROM folders WHERE drive_id = ?", (drive_id,))
        self.connection.commit()
    
    def clear_drive_data(self, drive_id: int):
        """Clear both files and folders for a drive in single transaction"""
        try:
            self.cursor.execute("BEGIN TRANSACTION")
            self.cursor.execute("DELETE FROM files WHERE drive_id = ?", (drive_id,))
            self.cursor.execute("DELETE FROM folders WHERE drive_id = ?", (drive_id,))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
    
    # ==================== FILE OPERATIONS ====================
    
    def add_file(self, drive_id: int, file_name: str, file_path: str, file_size: int,
                 file_extension: str, modified_date: str, created_date: str = None,
                 parent_folder_id: Optional[int] = None) -> int:
        """Add a file to inventory"""
        self.cursor.execute("""
            INSERT INTO files (drive_id, file_name, file_path, file_size, file_extension,
                             modified_date, created_date, parent_folder_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (drive_id, file_name, file_path, file_size, file_extension,
              modified_date, created_date, parent_folder_id))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def add_files_batch(self, files: List[tuple]):
        """Add multiple files at once for better performance"""
        if not files:
            return
        try:
            self.cursor.execute("BEGIN TRANSACTION")
            self.cursor.executemany("""
                INSERT INTO files (drive_id, file_name, file_path, file_size, file_extension,
                                 modified_date, created_date, parent_folder_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, files)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"Error in batch insert: {e}")
            raise
    
    def get_files_by_drive(self, drive_id: int, limit: int = None) -> List[Dict]:
        """Get all files for a drive"""
        query = "SELECT * FROM files WHERE drive_id = ? ORDER BY file_path"
        if limit:
            query += f" LIMIT {limit}"
        self.cursor.execute(query, (drive_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def clear_files_by_drive(self, drive_id: int):
        """Clear all files for a drive (used before rescan)"""
        self.cursor.execute("DELETE FROM files WHERE drive_id = ?", (drive_id,))
        self.connection.commit()
    
    # ==================== SEARCH OPERATIONS ====================
    
    def search_files(self, query: str = "", drive_ids: List[int] = None,
                    extensions: List[str] = None, min_size: int = None,
                    max_size: int = None, date_from: str = None, date_to: str = None,
                    path_contains: str = None, tags: List[str] = None,
                    has_comments: bool = None, min_rating: int = None,
                    universal_search: str = "", search_filename: bool = True,
                    search_path: bool = True, search_comments: bool = True,
                    search_metadata: bool = True, search_tags: bool = True,
                    universal_case_sensitive: bool = False,
                    limit: int = None, offset: int = None) -> tuple[List[Dict], int]:
        """Advanced file search with multiple filters and pagination
        
        Args:
            query: Search in filename (legacy parameter)
            drive_ids: Filter by drive IDs
            extensions: Filter by file extensions
            min_size, max_size: Filter by file size
            date_from, date_to: Filter by modification date
            path_contains: Filter by path containing text
            tags: Filter by tag names
            has_comments: Filter files that have/don't have comments
            min_rating: Filter by minimum rating
            universal_search: Universal search across multiple content types
            search_filename: Whether to search in filenames
            search_path: Whether to search in paths
            search_comments: Whether to search in comments
            search_metadata: Whether to search in custom metadata
            search_tags: Whether to search in tags
            universal_case_sensitive: Whether universal search is case sensitive
        
        Returns:
            Tuple of (results, total_count)
        """
        
        sql = """SELECT DISTINCT f.*, d.drive_label, d.drive_letter 
                  FROM files f 
                  JOIN drives d ON f.drive_id = d.id 
                  LEFT JOIN file_tags ft ON f.id = ft.file_id
                  LEFT JOIN tags t ON ft.tag_id = t.id
                  LEFT JOIN file_metadata fm ON f.id = fm.file_id
                  WHERE 1=1"""
        count_sql = """SELECT COUNT(DISTINCT f.id) as count 
                       FROM files f 
                       JOIN drives d ON f.drive_id = d.id 
                       LEFT JOIN file_tags ft ON f.id = ft.file_id
                       LEFT JOIN tags t ON ft.tag_id = t.id
                       LEFT JOIN file_metadata fm ON f.id = fm.file_id
                       WHERE 1=1"""
        params = []
        
        # Universal search across multiple content types
        if universal_search:
            search_conditions = []
            search_term = f"%{universal_search}%"
            
            if search_filename:
                if universal_case_sensitive:
                    search_conditions.append("f.file_name LIKE ? COLLATE BINARY")
                else:
                    search_conditions.append("f.file_name LIKE ? COLLATE NOCASE")
                params.append(search_term)
            if search_path:
                if universal_case_sensitive:
                    search_conditions.append("f.file_path LIKE ? COLLATE BINARY")
                else:
                    search_conditions.append("f.file_path LIKE ? COLLATE NOCASE")
                params.append(search_term)
            if search_comments:
                if universal_case_sensitive:
                    search_conditions.append("f.comments LIKE ? COLLATE BINARY")
                else:
                    search_conditions.append("f.comments LIKE ? COLLATE NOCASE")
                params.append(search_term)
            if search_metadata:
                if universal_case_sensitive:
                    search_conditions.append("fm.meta_value LIKE ? COLLATE BINARY")
                else:
                    search_conditions.append("fm.meta_value LIKE ? COLLATE NOCASE")
                params.append(search_term)
            if search_tags:
                if universal_case_sensitive:
                    search_conditions.append("t.tag_name LIKE ? COLLATE BINARY")
                else:
                    search_conditions.append("t.tag_name LIKE ? COLLATE NOCASE")
                params.append(search_term)
            
            if search_conditions:
                sql += " AND (" + " OR ".join(search_conditions) + ")"
                count_sql += " AND (" + " OR ".join(search_conditions) + ")"
        
        # Legacy filename search (for backward compatibility)
        elif query:
            sql += " AND f.file_name LIKE ?"
            count_sql += " AND f.file_name LIKE ?"
            params.append(f"%{query}%")
        
        # Filter by drive IDs
        if drive_ids:
            placeholders = ",".join("?" * len(drive_ids))
            sql += f" AND f.drive_id IN ({placeholders})"
            count_sql += f" AND f.drive_id IN ({placeholders})"
            params.extend(drive_ids)
        
        # Filter by extensions
        if extensions:
            placeholders = ",".join("?" * len(extensions))
            sql += f" AND f.file_extension IN ({placeholders})"
            count_sql += f" AND f.file_extension IN ({placeholders})"
            params.extend(extensions)
        
        # Filter by size
        if min_size is not None:
            sql += " AND f.file_size >= ?"
            count_sql += " AND f.file_size >= ?"
            params.append(min_size)
        if max_size is not None:
            sql += " AND f.file_size <= ?"
            count_sql += " AND f.file_size <= ?"
            params.append(max_size)
        
        # Filter by date
        if date_from:
            sql += " AND f.modified_date >= ?"
            count_sql += " AND f.modified_date >= ?"
            params.append(date_from)
        if date_to:
            sql += " AND f.modified_date <= ?"
            count_sql += " AND f.modified_date <= ?"
            params.append(date_to)
        
        # Filter by path
        if path_contains:
            sql += " AND f.file_path LIKE ?"
            count_sql += " AND f.file_path LIKE ?"
            params.append(f"%{path_contains}%")
        
        # Filter by tags
        if tags:
            placeholders = ",".join("?" * len(tags))
            sql += f" AND t.tag_name IN ({placeholders})"
            count_sql += f" AND t.tag_name IN ({placeholders})"
            params.extend(tags)
        
        # Filter by comments presence
        if has_comments is not None:
            if has_comments:
                sql += " AND f.comments IS NOT NULL AND f.comments != ''"
                count_sql += " AND f.comments IS NOT NULL AND f.comments != ''"
            else:
                sql += " AND (f.comments IS NULL OR f.comments = '')"
                count_sql += " AND (f.comments IS NULL OR f.comments = '')"
        
        # Filter by minimum rating
        if min_rating is not None and min_rating > 0:
            sql += " AND f.rating >= ?"
            count_sql += " AND f.rating >= ?"
            params.append(min_rating)
        
        sql += " ORDER BY f.id"
        
        if limit:
            sql += f" LIMIT {limit}"
        if offset:
            sql += f" OFFSET {offset}"
        
        # Get total count
        self.cursor.execute(count_sql, params)
        total_count = self.cursor.fetchone()['count']
        
        # Get results
        self.cursor.execute(sql, params)
        results = [dict(row) for row in self.cursor.fetchall()]
        
        return results, total_count
    
    def get_file_statistics(self) -> Dict:
        """Get overall file statistics"""
        stats = {}
        
        # Total files
        self.cursor.execute("SELECT COUNT(*) as count FROM files")
        stats['total_files'] = self.cursor.fetchone()['count']
        
        # Total size
        self.cursor.execute("SELECT SUM(file_size) as total FROM files")
        stats['total_size'] = self.cursor.fetchone()['total'] or 0
        
        # File type distribution
        self.cursor.execute("""
            SELECT file_extension, COUNT(*) as count 
            FROM files 
            GROUP BY file_extension 
            ORDER BY count DESC 
            LIMIT 10
        """)
        stats['top_extensions'] = [dict(row) for row in self.cursor.fetchall()]
        
        return stats
    
    def get_drive_statistics(self, drive_id: int) -> Dict:
        """Get statistics for a specific drive"""
        stats = {}
        
        # File count for this drive
        self.cursor.execute("SELECT COUNT(*) as count FROM files WHERE drive_id = ?", (drive_id,))
        stats['file_count'] = self.cursor.fetchone()['count']
        
        # Folder count for this drive
        self.cursor.execute("SELECT COUNT(*) as count FROM folders WHERE drive_id = ?", (drive_id,))
        stats['folder_count'] = self.cursor.fetchone()['count']
        
        # Total size for this drive
        self.cursor.execute("SELECT SUM(file_size) as total FROM files WHERE drive_id = ?", (drive_id,))
        stats['total_size'] = self.cursor.fetchone()['total'] or 0
        
        return stats
    
    # ==================== TAG OPERATIONS ====================
    
    def add_tag(self, tag_name: str, color: str = None) -> int:
        """Add a new tag"""
        try:
            self.cursor.execute("INSERT INTO tags (tag_name, color) VALUES (?, ?)", 
                              (tag_name, color))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Tag already exists
            self.cursor.execute("SELECT id FROM tags WHERE tag_name = ?", (tag_name,))
            return self.cursor.fetchone()['id']
    
    def get_all_tags(self) -> List[Dict]:
        """Get all tags"""
        self.cursor.execute("SELECT * FROM tags ORDER BY tag_name")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def tag_file(self, file_id: int, tag_id: int):
        """Add tag to file"""
        try:
            self.cursor.execute("INSERT INTO file_tags (file_id, tag_id) VALUES (?, ?)", 
                              (file_id, tag_id))
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass  # Already tagged
    
    def untag_file(self, file_id: int, tag_id: int):
        """Remove tag from file"""
        self.cursor.execute("DELETE FROM file_tags WHERE file_id = ? AND tag_id = ?", 
                          (file_id, tag_id))
        self.connection.commit()
    
    def get_file_tags(self, file_id: int) -> List[Dict]:
        """Get all tags for a file"""
        self.cursor.execute("""
            SELECT t.* FROM tags t
            JOIN file_tags ft ON t.id = ft.tag_id
            WHERE ft.file_id = ?
        """, (file_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== UTILITY OPERATIONS ====================
    
    def vacuum(self):
        """Optimize database by reclaiming space and defragmenting"""
        try:
            self.cursor.execute("VACUUM")
            self.connection.commit()
        except Exception as e:
            print(f"Vacuum error: {e}")
    
    def analyze(self):
        """Update query optimizer statistics for better performance"""
        try:
            self.cursor.execute("ANALYZE")
            self.connection.commit()
        except Exception as e:
            print(f"Analyze error: {e}")
    
    def get_db_size(self) -> int:
        """Get database file size in bytes"""
        try:
            return self.db_path.stat().st_size
        except Exception:
            return 0
    
    def get_table_counts(self) -> Dict[str, int]:
        """Get row counts for all tables"""
        counts = {}
        tables = ['drives', 'files', 'folders', 'tags', 'file_tags']
        for table in tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                counts[table] = self.cursor.fetchone()['count']
            except Exception:
                counts[table] = 0
        return counts
    
    def update_file_comments(self, file_id: int, comments: str):
        """Update comments for a file"""
        self.cursor.execute("""
            UPDATE files SET comments = ? WHERE id = ?
        """, (comments, file_id))
        self.connection.commit()
    
    def update_file_rating(self, file_id: int, rating: int):
        """Update rating for a file (0-5 stars)"""
        rating = max(0, min(5, rating))  # Ensure rating is between 0 and 5
        self.cursor.execute("""
            UPDATE files SET rating = ? WHERE id = ?
        """, (rating, file_id))
        self.connection.commit()
    
    def get_file_metadata(self, file_id: int) -> dict:
        """Get comments and rating for a file"""
        self.cursor.execute("""
            SELECT comments, rating FROM files WHERE id = ?
        """, (file_id,))
        row = self.cursor.fetchone()
        if row:
            return {
                'comments': row['comments'] or '',
                'rating': row['rating'] or 0
            }
        return {'comments': '', 'rating': 0}
    
    # ==================== CUSTOM METADATA OPERATIONS ====================
    
    def set_file_metadata(self, file_id: int, key: str, value: str):
        """Set custom metadata for a file"""
        self.cursor.execute("""
            INSERT INTO file_metadata (file_id, meta_key, meta_value, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(file_id, meta_key) DO UPDATE SET
                meta_value = excluded.meta_value,
                updated_at = CURRENT_TIMESTAMP
        """, (file_id, key, value))
        self.connection.commit()
    
    def get_file_custom_metadata(self, file_id: int) -> Dict[str, str]:
        """Get all custom metadata for a file"""
        self.cursor.execute("""
            SELECT meta_key, meta_value FROM file_metadata 
            WHERE file_id = ? ORDER BY meta_key
        """, (file_id,))
        return {row['meta_key']: row['meta_value'] for row in self.cursor.fetchall()}
    
    def delete_file_metadata(self, file_id: int, key: str):
        """Delete specific metadata key for a file"""
        self.cursor.execute("""
            DELETE FROM file_metadata WHERE file_id = ? AND meta_key = ?
        """, (file_id, key))
        self.connection.commit()
    
    def get_all_file_metadata(self, file_id: int) -> Dict[str, any]:
        """Get complete metadata for a file (comments, rating, tags, custom)"""
        metadata = self.get_file_metadata(file_id)
        metadata['tags'] = self.get_file_tags(file_id)
        metadata['custom'] = self.get_file_custom_metadata(file_id)
        return metadata
    
    # ==================== INVENTORY XML IMPORT OPERATIONS ====================
    
    def find_file_by_path(self, drive_id: int, file_path: str) -> Optional[int]:
        """Find a file by its path and return its ID"""
        self.cursor.execute("""
            SELECT id FROM files WHERE drive_id = ? AND file_path = ?
        """, (drive_id, file_path))
        row = self.cursor.fetchone()
        return row['id'] if row else None
    
    def find_folder_by_path(self, drive_id: int, folder_path: str) -> Optional[int]:
        """Find a folder by its path and return its ID"""
        self.cursor.execute("""
            SELECT id FROM folders WHERE drive_id = ? AND folder_path = ?
        """, (drive_id, folder_path))
        row = self.cursor.fetchone()
        return row['id'] if row else None
    
    def apply_inventory_metadata(self, drive_id: int, inventory_xmls: List[Dict]) -> Dict[str, int]:
        """
        Apply metadata from inventory XML files to corresponding files/folders
        
        Args:
            drive_id: ID of the drive being scanned
            inventory_xmls: List of inventory XML metadata dictionaries
        
        Returns:
            Dictionary with counts: {'files_updated': N, 'folders_updated': N, 'not_found': N}
        """
        stats = {'files_updated': 0, 'folders_updated': 0, 'not_found': 0}
        
        for inv_xml in inventory_xmls:
            try:
                target_path = inv_xml['target_path']
                is_folder = inv_xml['is_folder']
                comments = inv_xml.get('comments', '')
                rating = inv_xml.get('rating', 0)
                custom = inv_xml.get('custom', {})
                
                if is_folder:
                    # Find the folder
                    folder_id = self.find_folder_by_path(drive_id, target_path)
                    if folder_id:
                        # Folders don't have comments/ratings in current schema
                        # Could be extended in the future
                        stats['folders_updated'] += 1
                    else:
                        stats['not_found'] += 1
                else:
                    # Find the file
                    file_id = self.find_file_by_path(drive_id, target_path)
                    if file_id:
                        # Update comments and rating
                        if comments:
                            self.update_file_comments(file_id, comments)
                        if rating > 0:
                            self.update_file_rating(file_id, rating)
                        
                        # Update custom metadata
                        for key, value in custom.items():
                            self.set_file_metadata(file_id, key, value)
                        
                        stats['files_updated'] += 1
                    else:
                        stats['not_found'] += 1
            
            except Exception as e:
                import logging
                logging.exception(f"Error applying inventory metadata for {inv_xml.get('target_path', 'unknown')}: {e}")
                stats['not_found'] += 1
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                print(f"Error closing database: {e}")
    
    def increment_version(self):
        """Increment the database version for sync tracking"""
        from datetime import datetime
        try:
            now = datetime.now().isoformat()
            self.cursor.execute("""
                UPDATE sync_metadata 
                SET version = version + 1, last_modified = ?
                WHERE id = 1
            """, (now,))
            self.connection.commit()
        except Exception as e:
            print(f"Error incrementing version: {e}")
    
    def get_sync_metadata(self):
        """Get sync metadata for the database"""
        try:
            self.cursor.execute("""
                SELECT unique_id, version, last_modified 
                FROM sync_metadata 
                WHERE id = 1
            """)
            row = self.cursor.fetchone()
            if row:
                return {
                    'unique_id': row['unique_id'],
                    'version': row['version'],
                    'last_modified': row['last_modified']
                }
            return None
        except Exception as e:
            print(f"Error getting sync metadata: {e}")
            return None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
