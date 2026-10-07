# S.M.A.R.T. Integration Module

## Overview

This module provides utilities for accessing and storing S.M.A.R.T. (Self-Monitoring, Analysis, and Reporting Technology) health data for drives.

- `smart_reader.py`: Fetches S.M.A.R.T. health and key attributes using `smartctl` (Windows, requires smartmontools in PATH).
- `smart_db.py`: Stores and retrieves S.M.A.R.T. history in the database for trace/alert utilities.

## Usage

### Fetching S.M.A.R.T. Status
```python
from core.smart.smart_reader import get_smart_status
status = get_smart_status('E')  # Example: E drive
print(status['status'], status['attributes'])
```

### Logging S.M.A.R.T. History
```python
from core.smart.smart_db import SmartDB
sdb = SmartDB('data/inventory.db')
sdb.add_smart_entry(drive_id, status, attributes)
history = sdb.get_smart_history(drive_id)
```

## Database Schema
- Table: `smart_history`
  - `id` INTEGER PRIMARY KEY
  - `drive_id` INTEGER (foreign key)
  - `date` TEXT (ISO8601)
  - `status` TEXT
  - `reallocated_sectors` INTEGER
  - `temperature` INTEGER
  - `power_on_hours` INTEGER
  - `raw_json` TEXT (optional, for full dump)

## Requirements
- Python 3.9+
- smartctl (Windows, in PATH)
- SQLite3

## Extending
- Add more S.M.A.R.T. attributes as needed
- Use in background scan/refresh routines to log health
- Use in UI to display health and trace/alert user
