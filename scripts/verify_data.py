#!/usr/bin/env python3
"""
Quick verification script to check dummy data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import DatabaseManager

def verify_data():
    db = DatabaseManager()

    # Check drives
    drives = db.get_all_drives()
    print(f"Found {len(drives)} drives:")
    for drive in drives:
        print(f"  {drive['drive_letter']} - {drive['drive_label']} ({drive['file_count']} files, {drive['folder_count']} folders)")

    # Check files
    if drives:
        drive_id = drives[0]['id']
        files = db.get_files_by_drive(drive_id, limit=5)
        print(f"\nFirst 5 files from {drives[0]['drive_letter']}:")
        for file in files:
            print(f"  {file['file_name']} ({file['file_size']} bytes)")

    # Check tags
    tags = db.get_all_tags()
    print(f"\nFound {len(tags)} tags:")
    for tag in tags:
        print(f"  {tag['tag_name']} ({tag['color']})")

if __name__ == "__main__":
    verify_data()