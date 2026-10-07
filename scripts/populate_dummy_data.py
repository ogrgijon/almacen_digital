#!/usr/bin/env python3
"""
Script to populate the HDDInventory database with dummy data for screenshots
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random
import os

def create_dummy_data():
    """Create realistic dummy data for screenshots"""

    # Connect to database
    db_path = Path("data/inventory.db")
    if not db_path.exists():
        print("Database not found. Please run the application first to create the database.")
        return

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("Adding dummy data to database...")

    # Sample drive data
    drives = [
        {
            'drive_letter': 'C:',
            'drive_label': 'Windows SSD',
            'serial_number': 'SSD123456789',
            'capacity_bytes': 500 * 1024 * 1024 * 1024,  # 500GB
            'free_space_bytes': 150 * 1024 * 1024 * 1024,  # 150GB free
            'file_count': 12543,
            'folder_count': 2341,
            'notes': 'Primary Windows installation drive',
            'last_scan_date': datetime.now().isoformat()
        },
        {
            'drive_letter': 'D:',
            'drive_label': 'Data HDD',
            'serial_number': 'HDD987654321',
            'capacity_bytes': 2000 * 1024 * 1024 * 1024,  # 2TB
            'free_space_bytes': 800 * 1024 * 1024 * 1024,   # 800GB free
            'file_count': 45231,
            'folder_count': 5678,
            'notes': 'Storage for documents and media',
            'last_scan_date': (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            'drive_letter': 'E:',
            'drive_label': 'Backup USB',
            'serial_number': 'USB111222333',
            'capacity_bytes': 1000 * 1024 * 1024 * 1024,  # 1TB
            'free_space_bytes': 300 * 1024 * 1024 * 1024,   # 300GB free
            'file_count': 18756,
            'folder_count': 1234,
            'notes': 'External backup drive',
            'last_scan_date': (datetime.now() - timedelta(days=7)).isoformat()
        }
    ]

    # Insert drives
    drive_ids = []
    for drive in drives:
        cursor.execute("""
            INSERT INTO drives (drive_letter, drive_label, serial_number, capacity_bytes,
                              free_space_bytes, file_count, folder_count, notes, last_scan_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (drive['drive_letter'], drive['drive_label'], drive['serial_number'],
              drive['capacity_bytes'], drive['free_space_bytes'], drive['file_count'],
              drive['folder_count'], drive['notes'], drive['last_scan_date']))

        drive_ids.append(cursor.lastrowid)

    # Sample folder structure for each drive
    folder_structures = {
        drive_ids[0]: [  # C: drive
            {'name': 'Windows', 'path': 'C:\\Windows', 'parent': None, 'level': 0},
            {'name': 'Program Files', 'path': 'C:\\Program Files', 'parent': None, 'level': 0},
            {'name': 'Users', 'path': 'C:\\Users', 'parent': None, 'level': 0},
            {'name': 'Documents', 'path': 'C:\\Users\\User\\Documents', 'parent': None, 'level': 1},
            {'name': 'Pictures', 'path': 'C:\\Users\\User\\Pictures', 'parent': None, 'level': 1},
            {'name': 'Downloads', 'path': 'C:\\Users\\User\\Downloads', 'parent': None, 'level': 1},
        ],
        drive_ids[1]: [  # D: drive
            {'name': 'Movies', 'path': 'D:\\Movies', 'parent': None, 'level': 0},
            {'name': 'Music', 'path': 'D:\\Music', 'parent': None, 'level': 0},
            {'name': 'Photos', 'path': 'D:\\Photos', 'parent': None, 'level': 0},
            {'name': 'Documents', 'path': 'D:\\Documents', 'parent': None, 'level': 0},
            {'name': 'Projects', 'path': 'D:\\Projects', 'parent': None, 'level': 0},
            {'name': 'Action', 'path': 'D:\\Movies\\Action', 'parent': None, 'level': 1},
            {'name': 'Comedy', 'path': 'D:\\Movies\\Comedy', 'parent': None, 'level': 1},
        ],
        drive_ids[2]: [  # E: drive
            {'name': 'Backup', 'path': 'E:\\Backup', 'parent': None, 'level': 0},
            {'name': 'Archives', 'path': 'E:\\Archives', 'parent': None, 'level': 0},
            {'name': 'System Images', 'path': 'E:\\System Images', 'parent': None, 'level': 0},
        ]
    }

    # Insert folders
    folder_ids = {}
    for drive_id, folders in folder_structures.items():
        for folder in folders:
            cursor.execute("""
                INSERT INTO folders (drive_id, folder_name, folder_path, parent_folder_id, level)
                VALUES (?, ?, ?, ?, ?)
            """, (drive_id, folder['name'], folder['path'], folder['parent'], folder['level']))

            folder_ids[f"{drive_id}_{folder['path']}"] = cursor.lastrowid

    # Sample files with realistic data
    file_types = {
        'Documents': ['.docx', '.pdf', '.txt', '.xlsx', '.pptx'],
        'Images': ['.jpg', '.png', '.gif', '.bmp', '.tiff'],
        'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Programs': ['.exe', '.msi', '.bat', '.cmd', '.ps1']
    }

    sample_files = [
        # C: drive files
        {'drive_id': drive_ids[0], 'folder_path': 'C:\\Users\\User\\Documents', 'name': 'Project_Plan.docx', 'size': 245760, 'ext': '.docx', 'rating': 4},
        {'drive_id': drive_ids[0], 'folder_path': 'C:\\Users\\User\\Documents', 'name': 'Budget_2024.xlsx', 'size': 189440, 'ext': '.xlsx', 'rating': 3},
        {'drive_id': drive_ids[0], 'folder_path': 'C:\\Users\\User\\Documents', 'name': 'Meeting_Notes.txt', 'size': 5120, 'ext': '.txt', 'rating': 0},
        {'drive_id': drive_ids[0], 'folder_path': 'C:\\Users\\User\\Pictures', 'name': 'Vacation_001.jpg', 'size': 3145728, 'ext': '.jpg', 'rating': 5},
        {'drive_id': drive_ids[0], 'folder_path': 'C:\\Users\\User\\Pictures', 'name': 'Family_Portrait.png', 'size': 2097152, 'ext': '.png', 'rating': 4},
        {'drive_id': drive_ids[0], 'folder_path': 'C:\\Users\\User\\Downloads', 'name': 'Setup_Program.exe', 'size': 52428800, 'ext': '.exe', 'rating': 0},
        {'drive_id': drive_ids[0], 'folder_path': 'C:\\Users\\User\\Downloads', 'name': 'Manual.pdf', 'size': 1572864, 'ext': '.pdf', 'rating': 2},

        # D: drive files
        {'drive_id': drive_ids[1], 'folder_path': 'D:\\Movies\\Action', 'name': 'Die_Hard.mp4', 'size': 4294967296, 'ext': '.mp4', 'rating': 5},  # 4GB
        {'drive_id': drive_ids[1], 'folder_path': 'D:\\Movies\\Action', 'name': 'John_Wick.mkv', 'size': 8589934592, 'ext': '.mkv', 'rating': 5},  # 8GB
        {'drive_id': drive_ids[1], 'folder_path': 'D:\\Movies\\Comedy', 'name': 'Superbad.avi', 'size': 1610612736, 'ext': '.avi', 'rating': 4},  # 1.5GB
        {'drive_id': drive_ids[1], 'folder_path': 'D:\\Music', 'name': 'Favorite_Songs.mp3', 'size': 5242880, 'ext': '.mp3', 'rating': 4},
        {'drive_id': drive_ids[1], 'folder_path': 'D:\\Music', 'name': 'Classical_Collection.flac', 'size': 104857600, 'ext': '.flac', 'rating': 5},  # 100MB
        {'drive_id': drive_ids[1], 'folder_path': 'D:\\Photos', 'name': 'Wedding_Day.jpg', 'size': 5242880, 'ext': '.jpg', 'rating': 5},
        {'drive_id': drive_ids[1], 'folder_path': 'D:\\Photos', 'name': 'Summer_Vacation.png', 'size': 3145728, 'ext': '.png', 'rating': 4},
        {'drive_id': drive_ids[1], 'folder_path': 'D:\\Documents', 'name': 'Tax_Return_2023.pdf', 'size': 1048576, 'ext': '.pdf', 'rating': 3},
        {'drive_id': drive_ids[1], 'folder_path': 'D:\\Documents', 'name': 'Recipes.docx', 'size': 131072, 'ext': '.docx', 'rating': 2},
        {'drive_id': drive_ids[1], 'folder_path': 'D:\\Projects', 'name': 'Website_Backup.zip', 'size': 536870912, 'ext': '.zip', 'rating': 0},  # 512MB

        # E: drive files
        {'drive_id': drive_ids[2], 'folder_path': 'E:\\Backup', 'name': 'System_Backup_2024.zip', 'size': 10737418240, 'ext': '.zip', 'rating': 0},  # 10GB
        {'drive_id': drive_ids[2], 'folder_path': 'E:\\Backup', 'name': 'Documents_Backup.rar', 'size': 2147483648, 'ext': '.rar', 'rating': 0},  # 2GB
        {'drive_id': drive_ids[2], 'folder_path': 'E:\\Archives', 'name': 'Old_Photos.7z', 'size': 5368709120, 'ext': '.7z', 'rating': 3},  # 5GB
        {'drive_id': drive_ids[2], 'folder_path': 'E:\\System Images', 'name': 'Windows_10_Image.iso', 'size': 4294967296, 'ext': '.iso', 'rating': 0},  # 4GB
    ]

    # Insert files
    file_ids = []
    for file_info in sample_files:
        folder_id = folder_ids.get(f"{file_info['drive_id']}_{file_info['folder_path']}")
        if folder_id is None:
            # Find folder by path if not in our mapping
            cursor.execute("SELECT id FROM folders WHERE drive_id = ? AND folder_path = ?",
                         (file_info['drive_id'], file_info['folder_path']))
            result = cursor.fetchone()
            folder_id = result['id'] if result else None

        # Generate random dates
        base_date = datetime.now() - timedelta(days=random.randint(1, 365))
        modified_date = base_date.isoformat()
        created_date = (base_date - timedelta(days=random.randint(0, 30))).isoformat()

        cursor.execute("""
            INSERT INTO files (drive_id, file_name, file_path, file_size, file_extension,
                             modified_date, created_date, parent_folder_id, rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (file_info['drive_id'], file_info['name'],
              f"{file_info['folder_path']}\\{file_info['name']}",
              file_info['size'], file_info['ext'], modified_date, created_date,
              folder_id, file_info['rating']))

        file_ids.append(cursor.lastrowid)

    # Add some tags
    tags = [
        ('Important', '#FF5722'),
        ('Personal', '#2196F3'),
        ('Work', '#4CAF50'),
        ('Archive', '#9C27B0'),
        ('Media', '#FF9800')
    ]

    tag_ids = []
    for tag_name, color in tags:
        cursor.execute("INSERT INTO tags (tag_name, color) VALUES (?, ?)", (tag_name, color))
        tag_ids.append(cursor.lastrowid)

    # Add some file tags
    file_tags = [
        (file_ids[0], tag_ids[2]),  # Project_Plan.docx -> Work
        (file_ids[1], tag_ids[2]),  # Budget_2024.xlsx -> Work
        (file_ids[3], tag_ids[1]),  # Vacation_001.jpg -> Personal
        (file_ids[4], tag_ids[1]),  # Family_Portrait.png -> Personal
        (file_ids[7], tag_ids[1]),  # Wedding_Day.jpg -> Personal
        (file_ids[8], tag_ids[1]),  # Summer_Vacation.png -> Personal
        (file_ids[9], tag_ids[0]),  # Tax_Return_2023.pdf -> Important
        (file_ids[10], tag_ids[0]), # Recipes.docx -> Important
    ]

    for file_id, tag_id in file_tags:
        cursor.execute("INSERT INTO file_tags (file_id, tag_id) VALUES (?, ?)", (file_id, tag_id))

    # Add some metadata
    metadata = [
        (file_ids[0], 'author', 'John Doe'),
        (file_ids[0], 'last_printed', '2024-01-10'),
        (file_ids[3], 'camera', 'Canon EOS R5'),
        (file_ids[3], 'resolution', '6000x4000'),
        (file_ids[7], 'event', 'Wedding Day'),
        (file_ids[7], 'people', 'John, Jane'),
    ]

    for file_id, key, value in metadata:
        cursor.execute("""
            INSERT INTO file_metadata (file_id, meta_key, meta_value)
            VALUES (?, ?, ?)
        """, (file_id, key, value))

    # Update drive statistics to match actual counts
    for drive_id in drive_ids:
        cursor.execute("SELECT COUNT(*) as file_count FROM files WHERE drive_id = ?", (drive_id,))
        actual_file_count = cursor.fetchone()['file_count']

        cursor.execute("SELECT COUNT(*) as folder_count FROM folders WHERE drive_id = ?", (drive_id,))
        actual_folder_count = cursor.fetchone()['folder_count']

        cursor.execute("SELECT SUM(file_size) as total_size FROM files WHERE drive_id = ?", (drive_id,))
        total_size = cursor.fetchone()['total_size'] or 0

        cursor.execute("""
            UPDATE drives SET file_count = ?, folder_count = ? WHERE id = ?
        """, (actual_file_count, actual_folder_count, drive_id))

    conn.commit()
    conn.close()

    print("✅ Dummy data added successfully!")
    print(f"Added {len(drives)} drives, {len(sample_files)} files, and {len(tags)} tags")
    print("You can now run the application to see the data in the interface.")

if __name__ == "__main__":
    create_dummy_data()