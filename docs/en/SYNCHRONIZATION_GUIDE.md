# HDDInventory Database Synchronization

## General Description

HDDInventory includes database synchronization capability that allows sharing the inventory between multiple computers using a synchronized folder with an external cloud storage service.

## Features

- **Automatic Synchronization**: The application can synchronize automatically on startup and/or shutdown
- **Version Control**: Each change increments a version number to determine which database is more up-to-date
- **Unique ID**: Each inventory has a unique ID to prevent synchronizing incorrect databases
- **Three Synchronization Modes**:
  - **Bidirectional**: Synchronizes automatically using the most recent version
  - **Backup only read**: Only reads from backup, never writes (useful for read-only access)
  - **Backup only write**: Only writes to backup, never reads (useful for main computer)

## Initial Configuration

### 1. Configure Synchronized Folder

First, ensure you have a synchronized folder with your external cloud storage service:

- Configure a dedicated folder for HDDInventory in your synchronization service
- Example: `C:\Users\User\Synchronization\HDDInventory\`

### 2. Open Synchronization Configuration

In HDDInventory, go to:
- Menu → Settings → Synchronization
- Or use the quick access from the toolbar

### 3. Configure Parameters

1. **Enable automatic synchronization**: Check this box

2. **Backup Location**: Specify the complete path to the backup file
   - Example: `C:\Users\User\Synchronization\HDDInventory\inventory_backup.db`
   - Use the "Browse..." button to select the location
   - The file will be created automatically if it doesn't exist

3. **Synchronization Direction**: Select the appropriate mode
   - **Bidirectional** (recommended): For normal use on multiple computers
   - **Backup only read**: For computers where you only want to view the inventory
   - **Backup only write**: For the main computer that always has the most up-to-date data

4. **Synchronization Timing**: Select when to synchronize
   - **On startup**: Synchronizes when opening the application
   - **On shutdown**: Synchronizes when closing the application
   - You can select both (recommended)

5. **Test Connection**: Click to verify that the path is accessible

6. **Save**: Save the configuration

## Usage on Multiple Computers

### First Computer Setup (Computer A)

1. Configure HDDInventory normally and add your drives
2. Configure synchronization pointing to a cloud folder
3. Close the application (this will create the backup file)
4. Wait for the file to synchronize to the cloud

### Additional Computers Setup (Computer B, C, etc.)

1. Install HDDInventory
2. **DO NOT add drives yet**
3. Configure synchronization pointing to the same backup file
4. Close and reopen the application
5. The database will synchronize automatically from the backup
6. Now you can view and add your own drives

## How It Works

### Version System

Each time changes are made to the database:
- The version number is automatically incremented
- The modification date/time is recorded
- When synchronizing, the local version is compared with the backup version
- The highest version (most recent) is used

### Synchronization Process

#### Bidirectional Synchronization

1. On application startup or shutdown
2. Compares local version vs. backup version
3. If backup is newer: Updates the local database
4. If local is newer: Updates the backup file
5. If they are equal: Does nothing

#### Backup Only Read

1. On application startup
2. If backup is newer: Updates the local database
3. Never writes to backup

#### Backup Only Write

1. On application shutdown
2. Always updates the backup file with the local database
3. Never reads from backup

## Troubleshooting

### Backup file not found

**Problem**: The application cannot find the backup file

**Solutions**:
- Verify that the synchronized folder is connected and updated
- Ensure that the synchronization client is running
- Check folder permissions
- Use "Test Connection" in synchronization settings

### Different inventory IDs

**Problem**: "Different inventory IDs" in the log

**Explanation**: This means you are trying to synchronize with a database from a completely different inventory

**Solution**:
- Ensure all computers use the same backup file
- If you intentionally want to use a different database, create a new backup folder

### Synchronization conflicts

**Problem**: Changes made on multiple computers simultaneously

**Explanation**: The version system handles this automatically

**Behavior**:
- In bidirectional mode: The highest version wins
- Changes from the lower version will be lost
- It is recommended to work on one computer at a time

### Very slow synchronization

**Problem**: Synchronization takes a long time

**Solutions**:
- The first synchronization may take time due to file size
- Subsequent synchronizations are faster (only the complete file is copied)
- Consider using only shutdown synchronization if you have a large database
- Check your internet connection speed

## Best Practices

1. **Make regular backups**: The backup file IS a backup, but also make periodic copies

2. **Use bidirectional mode**: Unless you have a specific reason, use bidirectional mode

3. **Synchronize on startup and shutdown**: This ensures you always have the most recent version

4. **Check synchronization status**: Review the logs in `data/hddinventory.log` to see synchronization status

5. **Team work**: If multiple people use the inventory:
   - Coordinate who makes changes when
   - Close the application before another person opens it
   - Wait for synchronization to complete

6. **Dedicated folder**: Use a dedicated folder for the backup file
   - Don't mix with other files
   - Facilitates maintenance and backup

## Metadata Structure

The synchronization system adds a `sync_metadata` table to the database:

```sql
CREATE TABLE sync_metadata (
    id INTEGER PRIMARY KEY,
    unique_id TEXT NOT NULL,          -- Unique UUID of the inventory
    version INTEGER DEFAULT 1,        -- Incremental version number
    last_modified TEXT                -- ISO timestamp of last modification
)
```

This information allows:
- Identifying unique inventories
- Determining which version is more recent
- Tracking when changes were made

## Security and Privacy

- **Local data**: Your local database is always maintained
- **Automatic backup**: A `.db.bak` is created before overwriting
- **No server connection**: Everything works through shared files
- **Total control**: You control where the backup is stored
- **Privacy**: Data is only shared through your own synchronization configuration

## Limitations

- Not real-time synchronization (only on startup/shutdown)
- Does not handle merging conflicting changes (uses highest version)
- Requires manual synchronized folder configuration
- Complete file is copied each time (no delta sync)

## Support

For problems or questions:
1. Check the log file: `data/hddinventory.log`
2. Verify that the synchronization service is working
3. Use "Test Connection" in configuration
4. Report issues with log information