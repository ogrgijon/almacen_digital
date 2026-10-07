# Almacén Digital - User Guide

## General Information
Almacén Digital is a professional application for inventorying external disks with a dark theme interface. It allows you to scan, catalog, and search files on all your external disks (HDDs, USB pendrives, etc.).

## Features

### ✨ Main Features
- **Manual disk scanning** - You choose which disks to scan
- **SQLite database** - Fast and searchable local database
- **Advanced search and filtering** - Find files quickly with multiple filters
- **Excel import/export** - Share and backup your inventory
- **XML metadata synchronization** - Track changes between scans
- **Professional dark theme** - Modern interface
- **Multiple view modes** - Table, grid, and tree views

## Getting Started

### Installation
1. Install Python 3.10 or higher
2. Run `install.bat` or manually: `pip install -r requirements.txt`
3. Run `run.bat` or manually: `python main.py`

## User Interface

### General Design
The interface consists of four main areas:

```
┌──────────────────────────────────────────────────┐
│  📋 Inventory | 🔍 Search | 💾 Manage | 📊 Statistics │  ← Mode Selector
├─────────┬───────────────────────────┬────────────┤
│         │                           │            │
│  LEFT   │        MAIN               │   RIGHT    │
│ PANEL   │        CONTENT            │   PANEL    │
│         │                           │            │
│Collections     Results View         Filters      │
│         │                           │            │
└─────────┴───────────────────────────┴────────────┘
│  Status: 1,234 files | 3 disks | 25 GB          │  ← Status Bar
└──────────────────────────────────────────────────┘
```

### Modes

#### 📋 Inventory Mode (Default)
Navigate all indexed files in a table view with complete details.

**Features:**
- Quick search bar at the top
- Sortable columns (Name, Size, Type, Date, Disk)
- View selector: Table (≡), Grid (⊞), Tree (⋮)
- File icons and details

**Usage:**
1. Use quick search to find files by name
2. Click column headers to sort
3. Select files to view details
4. Switch between view modes

#### 🔍 Search Mode
Advanced search with multiple filters (currently uses the same view as Inventory).

**Note:** Advanced search filters are integrated in the right panel in Inventory mode.

#### 💾 Manage Mode
Add, scan, and manage your disks.

**Features:**
- Add new disks to inventory
- Scan/rescan disks
- Export disk data to Excel
- Remove disks from inventory
- View disk statistics

**Adding a Disk:**
1. Click "💾 Manage" in the top bar
2. Click "+ Add New Disk"
3. Select disk from dropdown menu
4. Enter descriptive name (optional)
5. Click "Start Scan"
6. Wait for scan to complete (progress shown)
7. Done! Files are now searchable

**Disk Cards Show:**
- Disk name and label
- Connection status (⚫ disconnected / 🟢 connected)
- Capacity and file counts
- Last scan date
- Action buttons: Rescan, Export, Remove

#### 📊 Statistics Mode
View analysis and visualizations (coming soon).

### Left Panel - Collections

**All Disks:**
- List of all indexed disks
- Click to filter by disk
- Shows file counts

**Recent Scans:**
- Today
- This Week
- This Month

**Quick Filters:**
- 📄 Documents (PDF, DOC, TXT, etc.)
- 🖼️ Images (JPG, PNG, etc.)
- 🎵 Audio (MP3, WAV, etc.)
- 🎬 Videos (MP4, AVI, etc.)
- 📦 Archives (ZIP, RAR, etc.)
- 🔷 Large Files (>100MB)

### Right Panel - Filters

**Text Search:**
- **Universal Search:** Search in file names, paths, comments, metadata, and tags
- **Case Sensitive Option:** Checkbox to enable/disable case-sensitive search
- **Search Scope:** Checkboxes to control where to search (name, path, comments, metadata, tags)
- **Simple Search:** Legacy search by filename only
- Case matching option
- Regular expression support

**File Attributes:**
- File type dropdown menu
- Size range (min/max bytes)
- Quick size presets

**Date Range:**
- Presets: Today, Last 7 days, Last 30 days, etc.
- Custom date range selector

**Location:**
- Filter by specific disk
- Path contains text

**Metadata:**
- Minimum rating filter
- Files with/without comments
- Tag filtering

**Action Buttons:**
- "Apply Filters" - Execute search (shows progress bar)
- "Reset" - Clear all filters
- Auto-apply checkbox for instant filtering

**Search Progress:**
- Progress bar appears in status bar during search operations
- Shows messages "Searching..." or "Applying filters..."
- Automatically hides when search completes

## Workflows

### First Time Usage

1. **Launch the application**
   ```
   python main.py
   ```

2. **Switch to Manage mode**
   - Click "💾 Manage" in the top bar

3. **Add your first disk**
   - Click "+ Add New Disk"
   - Select disk (e.g. E:\)
   - Enter name: "Work USB"
   - Click "Start Scan"
   - Wait for completion

4. **Browse files**
   - Switch to "📋 Inventory" mode
   - All files are now searchable!

### Daily Search Workflow

1. **Open the application**
2. **Search for files:**
   - **Quick search:** Type in search box, press Enter
   - **Advanced:** Use filters in right panel in Inventory mode, filters apply automatically or click "Apply Filters"
3. **Filter results:**
   - Click quick filters in left panel
   - Adjust filters in right panel (expand/collapse sections as needed)
4. **View details:**
   - Click file row to see details
   - Sort by any column

### Adding More Disks

1. Connect new disk
2. Go to Manage mode
3. Click "+ Add New Disk"
4. Select and scan
5. Files from all disks are now searchable together!

### Rescanning a Disk

When reconnecting a disk you've scanned before:

1. Go to Manage mode
2. Find the disk card
3. Click "🔄 Rescan"
4. Choose "Quick Update" (uses XML metadata) or "Full Scan"
5. Only changes are updated

### Exporting Data

**Export to Excel:**
1. Go to Manage mode
2. Click "📤 Export" on disk card
3. Choose save location
4. Excel file created with:
   - Index sheet (all disks)
   - One sheet per disk with files

**Export Search Results:**
1. Search/filter desired files
2. Click "Export Results" (coming soon)
3. Only filtered files are exported

## Tips and Tricks

### Performance
- Scan results are cached in local database
- Quick searches are instant (no disk access required)
- XML metadata allows fast update detection

### Keyboard Shortcuts
- `Ctrl+F` - Focus search box
- `Ctrl+R` - Refresh results
- `Escape` - Clear search

### File Organization
- Use descriptive names for disks ("Work USB" not "Drive E:")
- Add notes to disks in Manage mode
- Use tags to organize files (coming soon)

### Best Practices
- Rescan disks periodically to keep inventory updated
- Export to Excel for backup/sharing
- XML metadata stays on disk for fast synchronization

## Troubleshooting

### Disk Not Detected
- Make sure disk is connected
- Verify disk is formatted (NTFS, FAT32, exFAT)
- Try disconnecting and reconnecting

### Scan Errors
- "Access denied" - Run as administrator for system disks
- "Cannot access" - Check file/folder permissions
- Cancel and restart scan if it freezes

### Slow Performance
- Large disks (>1TB) take time to scan initially
- Use Quick Update for subsequent scans
- Close other applications during scanning

### Database Issues
- Database location: `data/inventory.db`
- Backup this file to preserve inventory
- Delete to restart from scratch

## File Locations

```
HDDINVENTORY/
├── data/
│   ├── inventory.db        ← Main database
│   └── settings.json       ← Application settings
├── main.py                 ← Run this to start
├── requirements.txt        ← Dependencies
├── install.bat            ← Install dependencies
└── run.bat                ← Quick start script
```

## XML Metadata

Each scanned disk receives a hidden XML file:
- Location: Disk root (e.g. `E:\.drive_inventory_meta.xml`)
- Purpose: Track last scan, file counts, disk ID
- Used for: Fast synchronization detection, update notifications

**Don't delete this file!** - It enables quick updates!

## Keyboard Shortcuts Reference

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Focus search |
| `Ctrl+R` | Refresh |
| `Escape` | Clear search |
| `F11` | Fullscreen (coming soon) |
| `Ctrl+1` | Inventory mode |
| `Ctrl+2` | Search mode |
| `Ctrl+3` | Manage mode |
| `Ctrl+4` | Statistics mode |

## Advanced Features (Coming Soon)

- **File preview** - Preview images, documents
- **Duplicate detection** - Find duplicate files by hash
- **Virtual collections** - Create custom file groups
- **Tags** - Tag and categorize files
- **Statistics** - Charts and analysis
- **Grid view** - Thumbnail grid like photo gallery
- **Tree view** - Hierarchical folder structure

## Support and Development

This is an open source project. For issues, suggestions, or contributions:
- Check README.md for project structure
- Database schema in `core/database.py`
- UI components in `ui/` folder

## Version History

**v1.0.0** (Current)
- Initial release
- Manual disk scanning
- SQLite database
- Advanced search and filtering
- Excel import/export
- XML metadata synchronization
- Professional dark theme
- Disk management interface

---

**Happy Organizing! 📦🔍**