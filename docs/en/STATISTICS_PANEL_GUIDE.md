# Statistics Panel - Redesign - Overview

## Features
- Drive overview: total files, folders, drives, total size
- Pie chart: Used vs free space per drive (with warning if low)
- S.M.A.R.T. health status (OK, Caution, Failing) with icon
- File size treemap: largest folders/files, interactive
- File type distribution: pie/bar chart
- S.M.A.R.T. trace/history: table and trend chart
- Replacement recommendation if S.M.A.R.T. is "FAILING" or critical
- Table: largest files/folders by drive
- (Optional) Duplicate file analysis

## File Structure
- `ui/statistics_panel.py`: Main panel widget
- `core/smart/smart_reader.py`: S.M.A.R.T. data retrieval utility
- `core/smart/smart_db.py`: S.M.A.R.T. history database
- `ui/README_statistics_panel.md`: Module documentation
- `core/smart/README.md`: S.M.A.R.T. integration documents

## Extensibility
- Add new tabs/sections by extending `StatisticsPanel`
- Add new S.M.A.R.T. attributes in DB and UI as needed

## Integration Points
- Call S.M.A.R.T. retrieval/logging in scan/update routines
- Display panel in statistics mode (replace previous statistics_view)

## Requirements
- PyQt6, matplotlib, squarify, smartctl (Windows)

## Next Steps
- Integrate panel into main window
- Connect S.M.A.R.T. logging to scan/update
- Add more visualizations as needed</content>
<parameter name="filePath">c:\DOCS\PROYECTOS\HDDINVENTORY\docs\en\STATISTICS_PANEL_GUIDE.md