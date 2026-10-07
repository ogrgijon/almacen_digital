"""Drive management view for adding or reviewing inventory devices."""

from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QMessageBox,
    QGroupBox,
    QProgressBar,
)

import config
from utils.helpers import (
    get_available_drives,
    get_drive_label,
    get_drive_serial_number,
    format_file_size,
)
from core.scanner import FileScanner
from i18n import _


def _color(key: str, fallback: str) -> str:
    return config.COLORS.get(key, fallback)


from PyQt6.QtWidgets import QDialog, QVBoxLayout as QVBoxLayoutDialog

class AddDeviceDialog(QDialog):
    def __init__(self, connected_box, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Register New Device"))
        layout = QVBoxLayoutDialog(self)
        layout.addWidget(connected_box)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

class ScanWorker(QObject):
    finished = pyqtSignal(list, list, list, str, int)  # Added inventory_xmls list
    progress = pyqtSignal(str)
    
    def __init__(self, drive_letter):
        super().__init__()
        self.drive_letter = drive_letter
        self._cancelled = False
        self.scanner = None
    
    def run(self):
        """Scan drive in background thread"""
        from core.scanner import FileScanner
        self.scanner = FileScanner(progress_callback=self._on_progress)
        # Ensure drive_letter has backslash for proper scanning
        scan_root = self.drive_letter.rstrip(':') + ':\\'
        folders, files, inventory_xmls = self.scanner.scan_drive(scan_root)
        if not self._cancelled:
            # Safely sum file sizes, handling empty strings
            def safe_size(f):
                size = f.get('file_size', 0)
                try:
                    return int(float(size)) if size else 0
                except (ValueError, TypeError):
                    return 0
            total_size = sum(safe_size(f) for f in files)
            verbose = '\n'.join(self.scanner.errors)
            self.finished.emit(folders, files, inventory_xmls, verbose, total_size)
    
    def _on_progress(self, message):
        """Handle progress updates from scanner"""
        if not self._cancelled:
            self.progress.emit(message)
    
    def cancel(self):
        """Cancel the scan operation"""
        self._cancelled = True
        if self.scanner:
            self.scanner.cancel()

class ManageDrivesView(QWidget):
    drive_added = pyqtSignal(dict)
    drive_removed = pyqtSignal()
    stats_updated = pyqtSignal()
    view_drive_index = pyqtSignal(int)

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        from core.database import DatabaseManager
        self.db = db if db is not None and hasattr(db, 'add_file') else DatabaseManager()
        self.connected_drives: List[Dict] = []
        self.inventory_drives: List[Dict] = []
        self.inventory_filtered_drives: List[Dict] = []
        self.selected_connected_drive: Optional[Dict] = None
        self.selected_inventory_drive: Optional[Dict] = None
        self._connected_detail_hint = (
            _("Select a drive to learn about its capacity, format and free space.")
        )
        self.scan_status_label = QLabel("")
        self.scan_status_label.setStyleSheet(f"color: {_color('accent', '#3EB489')}; font-size: 13px;")
        self.scan_status_label.hide()
        self.scan_progress_bar = QProgressBar()
        self.scan_progress_bar.setMinimum(0)
        self.scan_progress_bar.setMaximum(100)
        self.scan_progress_bar.setTextVisible(True)
        self.scan_progress_bar.hide()
        self._progress_anim_timer = QTimer()
        self._progress_anim_timer.setInterval(300)
        self._progress_anim_timer.timeout.connect(self._animate_progress_bar)
        self._progress_anim_state = 0
        self._scan_active = False
        self.cancel_btn = None
        self.open_btn = None
        self.remove_btn = None
        self.update_inventory_btn = None
        # self.inventory_list will be set in _build_inventory_box()
        self.inventory_status_label = None
        self.body_layout = None
        self._build_ui()

        # Timer to refresh connected drives periodically
        self._refresh_timer = QTimer()
        self._refresh_timer.setInterval(5000)  # 5 seconds
        self._refresh_timer.timeout.connect(self.refresh_connected_drives)
        self._refresh_timer.start()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(14)

        # Header with icon
        header_row = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setPixmap(QIcon.fromTheme("drive-harddisk").pixmap(32, 32))
        header_row.addWidget(header_icon)
        header = QLabel(_("Device Manager"))
        header.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {_color('text_primary', '#FFFFFF')};"
        )
        header.setWordWrap(True)
        header_row.addWidget(header)
        header_row.addStretch(1)
        root.addLayout(header_row)

        # Step-by-step guidance
        step_label = QLabel(_("1. Review your current inventory. 2. To add a new device, click 'Add Device'. 3. Follow the steps to register the drive."))
        step_label.setStyleSheet(f"color: {_color('text_secondary', '#AAAAAA')}; font-size: 13px;")
        step_label.setWordWrap(True)
        root.addWidget(step_label)

        summary_row = QHBoxLayout()
        self.connected_count_label = QLabel(_("Detected: 0 connected"))
        self.connected_count_label.setStyleSheet(
            f"color: {_color('text_secondary', '#AAAAAA')}; font-weight: 600;"
        )
        summary_row.addWidget(self.connected_count_label)

        self.inventory_count_label = QLabel(_("Inventory: 0 drives"))
        self.inventory_count_label.setStyleSheet(
            f"color: {_color('text_secondary', '#AAAAAA')}; font-weight: 600;"
        )
        summary_row.addWidget(self.inventory_count_label)

        summary_row.addStretch(1)
        self.show_connected_btn = QPushButton(QIcon.fromTheme("list-add"), _("Add Device"))
        self.show_connected_btn.setStyleSheet("font-size: 14px; padding: 6px 18px; font-weight: bold;")
        self.show_connected_btn.clicked.connect(self._show_connected_box)
        summary_row.addWidget(self.show_connected_btn)
        root.addLayout(summary_row)

        self.feedback_label = QLabel("")
        self.feedback_label.setStyleSheet(f"color: {_color('warning', '#E0A800')};")
        self.feedback_label.setWordWrap(True)
        root.addWidget(self.feedback_label)

        # Section title for inventory
        inventory_title = QLabel(_("Device Inventory"))
        inventory_title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {_color('accent', '#3EB489')}; margin-top: 10px;")
        root.addWidget(inventory_title)

        self.body_layout = QHBoxLayout()
        self.body_layout.setSpacing(14)
        self.inventory_box = self._build_inventory_box()
        self.body_layout.addWidget(self.inventory_box, 1)
        root.addLayout(self.body_layout)

        # Connected devices box for popup
        self.connected_box = self._build_connected_box()
        self.connected_box.hide()
        self.add_device_dialog = None

        root.addWidget(self.scan_status_label)
        root.addWidget(self.scan_progress_bar)
        root.addStretch(1)

        # Now that all widgets are created, refresh data
        self.refresh_data()

    def _show_connected_box(self):
        self.connected_box.show()
        self.add_device_dialog = AddDeviceDialog(self.connected_box, self)
        # Stop the refresh timer while dialog is open to prevent clearing selection
        if hasattr(self, '_refresh_timer') and self._refresh_timer:
            self._refresh_timer.stop()
        self.add_device_dialog.exec()
        # Restart the refresh timer after dialog closes
        if hasattr(self, '_refresh_timer') and self._refresh_timer:
            self._refresh_timer.start()
        self.connected_box.hide()
        self.show_connected_btn.show()
        self.inventory_box.show()

    def _build_connected_box(self) -> QGroupBox:
        box = QGroupBox(_("Connected devices"))
        box.setStyleSheet("QGroupBox { border: none; }")
        layout = QVBoxLayout(box)

        info_row = QHBoxLayout()
        info_label = QLabel(_("Select a device to save it to inventory."))
        info_label.setStyleSheet(f"color: {_color('text_secondary', '#AAAAAA')};")
        info_row.addWidget(info_label)
        info_row.addStretch(1)
        refresh_btn = QPushButton(_("Refresh list"))
        refresh_btn.clicked.connect(self.refresh_connected_drives)
        info_row.addWidget(refresh_btn)
        layout.addLayout(info_row)

        self.connected_list = QListWidget()
        self.connected_list.itemSelectionChanged.connect(self._on_connected_selection_changed)
        layout.addWidget(self.connected_list)

        self.connected_summary = QLabel(_("No selection."))
        self.connected_summary.setStyleSheet(f"color: {_color('text_secondary', '#AAAAAA')};")
        layout.addWidget(self.connected_summary)

        self.connected_detail_label = QLabel(self._connected_detail_hint)
        self.connected_detail_label.setStyleSheet(
            f"color: {_color('text_secondary', '#AAAAAA')}; font-size: 12px;"
        )
        self.connected_detail_label.setWordWrap(True)
        layout.addWidget(self.connected_detail_label)

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel(_("Register in inventory")))
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel(_("Inventory name:")))
        self.friendly_name_input = QLineEdit()
        self.friendly_name_input.setPlaceholderText(_("e.g. Photo backup 2026"))
        self.friendly_name_input.textChanged.connect(self._update_add_button_state)
        name_row.addWidget(self.friendly_name_input)
        form_layout.addLayout(name_row)

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        self.notes_input.setPlaceholderText(_("Notes or observations (optional)"))
        form_layout.addWidget(self.notes_input)

        self.duplicate_warning = QLabel("")
        self.duplicate_warning.setStyleSheet(f"color: {_color('error', '#E55353')}; font-weight: bold;")
        self.duplicate_warning.hide()
        form_layout.addWidget(self.duplicate_warning)

        add_row = QHBoxLayout()
        add_row.addStretch(1)
        self.add_btn = QPushButton(_("Add to inventory"))
        self.add_btn.setEnabled(False)
        self.add_btn.clicked.connect(self._handle_add_drive)
        add_row.addWidget(self.add_btn)
        form_layout.addLayout(add_row)

        layout.addLayout(form_layout)
        return box

    def _build_inventory_box(self) -> QGroupBox:
        box = QGroupBox("")
        box.setStyleSheet("QGroupBox { border: none; }")
        layout = QVBoxLayout(box)

        # Header
        header_row = QHBoxLayout()
        header_row.addWidget(QLabel(_("View the current status of each drive.")))
        header_row.addStretch(1)
        refresh_btn = QPushButton(_("Refresh inventory"))
        refresh_btn.clicked.connect(self.refresh_inventory)
        header_row.addWidget(refresh_btn)
        layout.addLayout(header_row)

        # Filter
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel(_("Search:")))
        self.inventory_filter_input = QLineEdit()
        self.inventory_filter_input.setPlaceholderText(_("Filter by name, letter or serial"))
        self.inventory_filter_input.textChanged.connect(self._apply_inventory_filter)
        filter_row.addWidget(self.inventory_filter_input)
        clear_filter_btn = QPushButton(_("Clear"))
        clear_filter_btn.clicked.connect(self.inventory_filter_input.clear)
        filter_row.addWidget(clear_filter_btn)
        layout.addLayout(filter_row)

        # Summary of totals
        self.inventory_summary_label = QLabel("")
        self.inventory_summary_label.setStyleSheet(f"color: {_color('accent', '#3EB489')}; font-weight: bold; font-size: 14px; margin: 5px 0px;")
        layout.addWidget(self.inventory_summary_label)

        # Inventory list
        self.inventory_list = QTreeWidget()
        self.inventory_list.setHeaderHidden(True)
        self.inventory_list.setIndentation(15)
        self.inventory_list.itemSelectionChanged.connect(self._on_inventory_selection_changed)
        self.inventory_list.itemDoubleClicked.connect(self._emit_view_inventory)
        layout.addWidget(self.inventory_list)

        # Status label
        self.inventory_status_label = QLabel(_("Select a drive for more actions."))
        self.inventory_status_label.setStyleSheet(f"color: {_color('text_secondary', '#AAAAAA')};")
        layout.addWidget(self.inventory_status_label)

        # Action buttons
        button_row = QHBoxLayout()
        self.open_btn = QPushButton(_("Open in inventory"))
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self._emit_view_inventory)
        button_row.addWidget(self.open_btn)

        self.remove_btn = QPushButton(_("Remove from inventory"))
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self._handle_remove_drive)
        button_row.addWidget(self.remove_btn)

        self.update_inventory_btn = QPushButton(_("Update Device Inventory"))
        self.update_inventory_btn.setEnabled(False)
        self.update_inventory_btn.clicked.connect(self._handle_update_inventory)
        button_row.addWidget(self.update_inventory_btn)

        button_row.addStretch(1)
        layout.addLayout(button_row)

        return box

    def refresh_data(self) -> None:
        self.refresh_connected_drives()
        self.refresh_inventory()

    def load_drives(self) -> None:
        """Compatibility helper for legacy code paths."""
        self.refresh_inventory()

    def refresh_connected_drives(self) -> None:
        self.connected_list.clear()
        self.connected_drives = []
        self.selected_connected_drive = None
        if hasattr(self, 'connected_detail_label'):
            self.connected_detail_label.setText(self._connected_detail_hint)
        try:
            raw_drives = get_available_drives()
        except Exception as exc:
            self._show_feedback(
                _("Could not read connected devices: {exc}").format(exc=exc),
                error=True,
            )
            self._update_summary_counts()
            return

        if not raw_drives:
            item = QListWidgetItem(_("No connected drives."))
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.connected_list.addItem(item)
            self.connected_summary.setText(_("Connect a USB/HDD device to begin."))
            self._update_add_button_state()
            self._update_summary_counts()
            return

        seen_letters = set()
        for drive in raw_drives:
            enriched = self._enrich_connected_drive(drive)
            letter = enriched.get('letter')
            if not letter or letter in seen_letters:
                continue
            seen_letters.add(letter)
            self.connected_drives.append(enriched)
            subtitle = (
                f"{enriched['label']} • {enriched['total_human']} "
                f"({enriched['free_human']} libres)"
            )
            item = QListWidgetItem(f"{letter} — {subtitle}")
            item.setData(Qt.ItemDataRole.UserRole, enriched)
            self.connected_list.addItem(item)

        self.connected_summary.setText(_("Select a drive to add it."))
        self._update_add_button_state()
        self._update_summary_counts()

        # Reload inventory data to ensure we have the latest drive information
        self.inventory_drives = self.db.get_all_drives() if hasattr(self.db, 'get_all_drives') else []

        # Update free space for connected drives that are already in inventory
        try:
            for connected_drive in self.connected_drives:
                letter = connected_drive.get('letter', '').upper()
                free_space = connected_drive.get('free')
                if letter and free_space is not None and free_space > 0:
                    # Find matching drive in inventory
                    inventory_drive = next((d for d in self.inventory_drives if (d.get('drive_letter') or '').upper() == letter), None)
                    if inventory_drive and inventory_drive.get('serial_number'):
                        # Update free space in database
                        self.db.update_drive_by_serial(
                            inventory_drive['serial_number'],
                            inventory_drive.get('drive_letter', ''),
                            inventory_drive.get('drive_label', ''),
                            inventory_drive.get('capacity_bytes', 0),
                            free_space
                        )
        except Exception as e:
            print(f"Warning: Could not update free space for connected drives: {e}")

        # Refresh inventory display with updated data
        if hasattr(self, 'inventory_list') and self.inventory_list:
            self._apply_inventory_filter()
            self._update_inventory_totals()

    def refresh_inventory(self) -> None:
        """Refresh inventory list from database"""
        if not hasattr(self, 'inventory_list') or self.inventory_list is None:
            return
        self.inventory_list.clear()
        self.inventory_filtered_drives = []
        self.selected_inventory_drive = None
        if self.open_btn:
            self.open_btn.setEnabled(False)
        if self.remove_btn:
            self.remove_btn.setEnabled(False)

        if not self.db:
            item = QTreeWidgetItem(self.inventory_list, [_("No database connection.")])
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            if self.inventory_status_label:
                self.inventory_status_label.setText(_("Connect to database to view inventory."))
            self.inventory_drives = []
            self._update_summary_counts()
            return

        try:
            self.inventory_drives = self.db.get_all_drives() if hasattr(self.db, 'get_all_drives') else []
            self._apply_inventory_filter()
            self._update_summary_counts()
            self._update_inventory_totals()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._show_feedback(f"Error al cargar inventario: {e}", error=True)

    def _apply_inventory_filter(self) -> None:
        if not hasattr(self, 'inventory_list') or self.inventory_list is None:
            return
        query = self.inventory_filter_input.text().strip().lower() if hasattr(self, 'inventory_filter_input') and self.inventory_filter_input else ""
        drives = self.inventory_drives or []
        self.inventory_list.clear()
        self.inventory_filtered_drives = []

        if not drives:
            placeholder = QTreeWidgetItem(self.inventory_list, [_("No registered devices.")])
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            if self.inventory_status_label:
                self.inventory_status_label.setText(_("Add your first drive from the list above."))
            return

        filtered = [
            drive for drive in drives
            if not query
            or query in (drive.get('drive_label') or '').lower()
            or query in (drive.get('drive_letter') or '').lower()
            or query in (drive.get('serial_number') or '').lower()
            or query in (drive.get('notes') or '').lower()
        ]
        if not filtered:
            placeholder = QTreeWidgetItem(self.inventory_list, [_("No matches with current filter.")])
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            if self.inventory_status_label:
                self.inventory_status_label.setText(_("No results for '{query}'").format(query=self.inventory_filter_input.text().strip()))
            return

        connected_letters = self._connected_letters()
        for drive in filtered:
            letter = (drive.get('drive_letter') or '').strip().upper()
            if letter and not letter.endswith(':'):
                letter += ':'
            status_connected = letter in connected_letters
            status_text = _("Connected") if status_connected else _("Disconnected")
            label = drive.get('drive_label') or _('Unnamed')
            subtitle = drive.get('last_scan_date', _('No scan'))
            notes = drive.get('notes', '').strip()
            capacity = drive.get('capacity_bytes', 0)
            capacity_text = format_file_size(capacity) if capacity else _("Unknown")
            
            # Get free space from database or connected drive
            free_space = ""
            free_space_bytes = drive.get('free_space_bytes')
            if free_space_bytes is not None and free_space_bytes > 0:
                free_space = f" | {_('Free')}: {format_file_size(free_space_bytes)}"
            elif status_connected:
                # Fallback to connected drive info if no stored free space
                connected_drive = next((d for d in self.connected_drives if (d.get('letter') or '').upper() == letter.upper()), None)
                if connected_drive:
                    free_bytes = connected_drive.get('free', 0)
                    free_h = connected_drive.get('free_human', '')
                    # Only show if free space is greater than 0 and not showing as "0 Bytes"
                    if free_bytes > 0 and free_h and not free_h.startswith('0 '):
                        free_space = f" | {_('Free')}: {free_h}"
            
            # Main display line
            display = f"{label} ({letter or 'N/A'}) — {status_text} | {_('Capacity')}: {capacity_text}{free_space} | {_('Last scan')}: {subtitle}"
            
            # Create main item
            item = QTreeWidgetItem(self.inventory_list, [display])
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            if status_connected:
                item.setForeground(0, Qt.GlobalColor.darkGreen)
            item.setData(0, Qt.ItemDataRole.UserRole, drive)
            
            # Add notes as a child item if they exist
            if notes:
                notes_item = QTreeWidgetItem(item, [f"📝 {_('Notes')}: {notes}"])
                notes_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                notes_item.setForeground(0, QColor(config.COLORS.get('text_secondary', '#AAAAAA')))
                # Make it slightly smaller font
                font = notes_item.font(0)
                font.setPointSize(max(1, font.pointSize() - 1))
                notes_item.setFont(0, font)
                # Store drive data and mark as notes item
                notes_item.setData(0, Qt.ItemDataRole.UserRole, drive)
                notes_item.setData(0, Qt.ItemDataRole.UserRole + 1, "notes")  # Mark as notes item
                # Start collapsed
                item.setExpanded(False)

        self.inventory_filtered_drives = filtered
        summary = _("Showing {count} of {total} drives").format(count=len(filtered), total=len(drives))
        if query:
            summary += _(" • Filter: '{query}'").format(query=self.inventory_filter_input.text().strip())
        if self.inventory_status_label:
            self.inventory_status_label.setText(summary)

    def _enrich_connected_drive(self, drive: Dict) -> Dict:
        letter = self._extract_drive_letter(
            drive.get('device') or drive.get('mountpoint')
        )
        label = drive.get('label')
        if not label and letter:
            try:
                label = get_drive_label(letter)
            except Exception:
                label = None

        total_h = drive.get('total_human') or format_file_size(drive.get('total', 0))
        free_h = drive.get('free_human') or format_file_size(drive.get('free', 0))
        return {
            **drive,
            'letter': letter,
            'label': label or (f"{_('Drive')} {letter}" if letter else _('Drive without letter')),
            'total_human': total_h,
            'free_human': free_h,
        }

    def _extract_drive_letter(self, raw_path: Optional[str]) -> Optional[str]:
        if not raw_path:
            return None
        sanitized = raw_path.replace('/', '\\')
        letter = sanitized.split(':', 1)[0] if ':' in sanitized else sanitized[0]
        if not letter:
            return None
        return f"{letter.upper()}:"

    def _on_connected_selection_changed(self) -> None:
        items = self.connected_list.selectedItems()
        if not items:
            self.selected_connected_drive = None
            self.connected_summary.setText(_("No selection."))
            self._update_add_button_state()
            return

        drive = items[0].data(Qt.ItemDataRole.UserRole)
        if not isinstance(drive, dict):
            self.selected_connected_drive = None
            self._update_add_button_state()
            return

        self.selected_connected_drive = drive
        letter = drive.get('letter', 'N/A')
        label = drive.get('label')
        self.connected_summary.setText(f"{letter} — {label}")
        if not self.friendly_name_input.text().strip():
            self.friendly_name_input.setText(label)
        self._update_add_button_state()
        self.duplicate_warning.hide()

    def _handle_add_drive(self) -> None:
        if not self.db:
            QMessageBox.warning(self, _("Inventory"), _("No database connection."))
            return
        if not self.selected_connected_drive:
            self._show_feedback(_("Select a connected drive."), error=True)
            return

        friendly_name = self.friendly_name_input.text().strip()
        notes = self.notes_input.toPlainText().strip()
        drive_info = self.selected_connected_drive
        letter = drive_info.get('letter')
        if not letter:
            self._show_feedback(_("Could not determine drive letter."), error=True)
            return

        serial = get_drive_serial_number(letter) or drive_info.get('device')
        existing = self.db.get_all_drives()

        if serial and any((d.get('serial_number') or '').lower() == serial.lower() for d in existing):
            self._show_feedback(_("This device is already registered by serial number."), error=True)
            self.duplicate_warning.setText(_("Duplicate device: already exists in inventory."))
            self.duplicate_warning.show()
            return

        if any(
            (d.get('drive_label') or '').lower() == friendly_name.lower()
            and (d.get('drive_letter') or '').upper() == letter.upper()
            for d in existing
        ):
            self._show_feedback(_("A device with the same name and letter already exists."), error=True)
            self.duplicate_warning.setText(_("Name already used for that letter."))
            self.duplicate_warning.show()
            return

        try:
            capacity = drive_info.get('total') or 0
            free_space = drive_info.get('free') or 0
            drive_id = self.db.add_drive(letter, friendly_name, serial or '', capacity, notes, free_space)
            
            # Close dialog immediately
            if self.add_device_dialog:
                self.add_device_dialog.close()
            
            # Force multiple refreshes to ensure device shows up
            self.refresh_inventory()
            
            # Switch to inventory view to show the new drive
            if hasattr(self.parent(), 'switch_mode'):
                self.parent().switch_mode('inventory')
            
            # Process events to ensure UI updates
            from PyQt6.QtWidgets import QApplication
            QApplication.processEvents()
            
            # Show scan feedback
            if self.scan_status_label:
                self.scan_status_label.setText(_("(Device added. Starting scan...)"))
                self.scan_status_label.show()
            if self.scan_progress_bar:
                self.scan_progress_bar.setValue(0)
                self.scan_progress_bar.show()
            
            # Start scan animation
            self._progress_anim_state = 0
            if self._progress_anim_timer:
                self._progress_anim_timer.start()
            
            # Start background scan with small delay to ensure UI updates first
            QTimer.singleShot(200, lambda: self._start_scan_thread(letter, rescan=True, is_new_drive=True))
        except Exception as exc:
            QMessageBox.critical(self, _("Inventory"), _("Could not register drive: {error}").format(error=exc))

    def _animate_progress_bar(self):
        if self._scan_active:
            self._progress_anim_state = (self._progress_anim_state + 1) % 4
            dots = '.' * self._progress_anim_state
            self.scan_progress_bar.setFormat(_("Updating{dots}%p%").format(dots=dots))
        else:
            self._progress_anim_timer.stop()
            self.scan_progress_bar.setFormat("%p%")

    # ...existing code...
    # Remove legacy scan methods. Use unified scan logic below.

    def _update_inventory_progress(self, percent):
        # Mark the device in inventory list as updating
        if not self.inventory_list:
            return
        # Iterate through top-level items in QTreeWidget
        for i in range(self.inventory_list.topLevelItemCount()):
            item = self.inventory_list.topLevelItem(i)
            drive = item.data(0, Qt.ItemDataRole.UserRole) if item else None
            selected_drive = getattr(self, 'selected_inventory_drive', None)
            if isinstance(drive, dict) and isinstance(selected_drive, dict) and drive.get('id') == selected_drive.get('id'):
                if item and hasattr(item, 'setText'):
                    item.setText(_("{label} ({letter}) — Updating... {percent}%").format(
                        label=drive.get('drive_label', _('Unnamed')), 
                        letter=drive.get('drive_letter', 'N/A'), 
                        percent=percent
                    ))
                if item and hasattr(item, 'setForeground'):
                    item.setForeground(Qt.GlobalColor.blue)
            elif isinstance(drive, dict) and isinstance(selected_drive, dict) and drive.get('id') == selected_drive.get('id'):
                if item and hasattr(item, 'setText'):
                    item.setText(_("{label} ({letter}) — Update completed").format(
                        label=drive.get('drive_label', _('Unnamed')), 
                        letter=drive.get('drive_letter', 'N/A')
                    ))
                if item and hasattr(item, 'setForeground'):
                    item.setForeground(Qt.GlobalColor.darkGreen)

    def _on_inventory_selection_changed(self) -> None:
        items = self.inventory_list.selectedItems() if self.inventory_list else []
        if not items:
            self.selected_inventory_drive = None
            if self.open_btn:
                self.open_btn.setEnabled(False)
            if self.remove_btn:
                self.remove_btn.setEnabled(False)
            if hasattr(self, 'cancel_btn') and self.cancel_btn:
                self.cancel_btn.hide()
            if hasattr(self, 'edit_notes_btn') and self.edit_notes_btn:
                self.edit_notes_btn.hide()
            if self.inventory_status_label:
                self.inventory_status_label.setText(
                    _("Select a drive for more actions.")
                )
            return

        selected_item = items[0]
        item_type = selected_item.data(0, Qt.ItemDataRole.UserRole + 1)
        
        # Check if this is a notes item
        if item_type == "notes":
            drive = selected_item.data(0, Qt.ItemDataRole.UserRole)
            if isinstance(drive, dict):
                self.selected_inventory_drive = drive
                if self.inventory_status_label:
                    self.inventory_status_label.setText(
                        _("Notes for {label} - Double-click or use Edit Notes button").format(
                            label=drive.get('drive_label', _('Unnamed'))
                        )
                )
                if self.open_btn:
                    self.open_btn.setEnabled(False)
                if self.remove_btn:
                    self.remove_btn.setEnabled(False)
                if hasattr(self, 'cancel_btn') and self.cancel_btn:
                    self.cancel_btn.hide()
                # Show edit notes button
                if not hasattr(self, 'edit_notes_btn') or not self.edit_notes_btn:
                    self.edit_notes_btn = QPushButton(_("Edit Notes"))
                    self.edit_notes_btn.clicked.connect(self._edit_notes)
                    if hasattr(self, 'body_layout') and self.body_layout:
                        self.body_layout.addWidget(self.edit_notes_btn)
                if self.edit_notes_btn:
                    self.edit_notes_btn.show()
                return

        # Handle regular drive items
        drive = selected_item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(drive, dict):
            self.selected_inventory_drive = None
            if self.open_btn:
                self.open_btn.setEnabled(False)
            if self.remove_btn:
                self.remove_btn.setEnabled(False)
            if hasattr(self, 'cancel_btn') and self.cancel_btn:
                self.cancel_btn.hide()
            if hasattr(self, 'edit_notes_btn') and self.edit_notes_btn:
                self.edit_notes_btn.hide()
            return

        self.selected_inventory_drive = drive
        letter = (drive.get('drive_letter') or 'N/A').upper()
        serial = drive.get('serial_number') or _('No serial')
        status = _("Connected") if self._drive_is_connected(letter) else _("Disconnected")
        if self.inventory_status_label:
            self.inventory_status_label.setText(
                f"{drive.get('drive_label', _('Unnamed'))} ({letter}) — {status} | SN: {serial}"
            )
        if self.open_btn:
            self.open_btn.setEnabled(True)
        if self.remove_btn:
            self.remove_btn.setEnabled(True)
        if hasattr(self, 'cancel_btn') and self.cancel_btn:
            self.cancel_btn.hide()
        if hasattr(self, 'edit_notes_btn') and self.edit_notes_btn:
            self.edit_notes_btn.hide()

        # Enable update inventory button
        if self.update_inventory_btn:
            self.update_inventory_btn.setEnabled(True)

    def _edit_notes(self) -> None:
        """Edit notes for the selected drive"""
        if not self.selected_inventory_drive:
            return
        
        drive = self.selected_inventory_drive
        current_notes = drive.get('notes', '')
        
        # Create edit dialog
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle(_("Edit Notes - {label}").format(label=drive.get('drive_label', _('Unnamed'))))
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(300)
        
        layout = QVBoxLayout(dialog)
        
        # Notes input
        notes_label = QLabel(_("Notes:"))
        layout.addWidget(notes_label)
        
        notes_input = QTextEdit()
        notes_input.setPlainText(current_notes)
        notes_input.setMaximumHeight(200)
        layout.addWidget(notes_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        save_btn = QPushButton(_("Save"))
        save_btn.clicked.connect(lambda: self._save_notes(dialog, notes_input, drive))
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton(_("Cancel"))
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()

    def _save_notes(self, dialog, notes_input, drive) -> None:
        """Save the edited notes"""
        new_notes = notes_input.toPlainText().strip()
        
        try:
            # Update database
            self.db.update_drive_notes(drive['id'], new_notes)
            
            # Update local data
            drive['notes'] = new_notes
            
            # Refresh display
            self._apply_inventory_filter()
            
            # Show success message
            self._show_feedback(_("Notes updated successfully"))
            
            dialog.accept()
            
        except Exception as exc:
            QMessageBox.critical(self, _("Error"), _("Could not update notes: {error}").format(error=exc))

    def _cancel_scan(self):
        if hasattr(self, 'scan_worker') and hasattr(self, 'scan_thread') and self._scan_active:
            self.scan_worker.cancel()
            if self.scan_status_label:
                self.scan_status_label.setText(_("(Scan cancelled)"))
            if self.scan_progress_bar:
                self.scan_progress_bar.hide()
            self._scan_active = False
            if hasattr(self, 'cancel_btn') and self.cancel_btn:
                self.cancel_btn.hide()

    def _emit_view_inventory(self, _item: Optional[QTreeWidgetItem] = None) -> None:
        # Check if this is a notes item
        if _item and _item.data(0, Qt.ItemDataRole.UserRole + 1) == "notes":
            self._edit_notes()
            return
        
        if self.selected_inventory_drive:
            self.view_drive_index.emit(self.selected_inventory_drive['id'])

    def _drive_is_connected(self, letter: str) -> bool:
        if not letter:
            return False
        normalized = letter.upper()
        if not normalized.endswith(':'):
            normalized += ':'
        return any((drive.get('letter') or '').upper() == normalized for drive in self.connected_drives)

    def _show_feedback(self, message: str, error: bool = False) -> None:
        if not message:
            self.feedback_label.clear()
            return
        color = _color('error', '#E55353') if error else _color('success', '#3EB489')
        self.feedback_label.setStyleSheet(f"color: {color};")
        self.feedback_label.setText(message)

    def _connected_letters(self) -> set:
        letters = set()
        for drive in self.connected_drives:
            letter = (drive.get('letter') or '').strip().upper()
            if not letter:
                continue
            if not letter.endswith(':'):
                letter += ':'
            letters.add(letter)
        return letters

    def _update_summary_counts(self) -> None:
        if not hasattr(self, 'connected_count_label'):
            return
        connected_detected = len(self.connected_drives)
        self.connected_count_label.setText(_("Detected: {count} connected").format(count=connected_detected))

        total_inventory = len(self.inventory_drives or [])
        letters = self._connected_letters()
        inventory_connected = 0
        for drive in self.inventory_drives or []:
            raw_letter = (drive.get('drive_letter') or '').strip().upper()
            if not raw_letter:
                continue
            normalized = raw_letter if raw_letter.endswith(':') else f"{raw_letter}:"
            if normalized in letters:
                inventory_connected += 1
        self.inventory_count_label.setText(
            _("Inventory: {total} drives ({connected} connected)").format(total=total_inventory, connected=inventory_connected)
        )

    def _update_inventory_totals(self) -> None:
        """Update the inventory totals summary (capacity and free space)"""
        if not hasattr(self, 'inventory_summary_label'):
            return
        
        drives = self.inventory_drives or []
        if not drives:
            self.inventory_summary_label.setText("")
            return
        
        total_capacity = 0
        total_free_space = 0
        
        for drive in drives:
            # Add capacity
            capacity = drive.get('capacity_bytes', 0)
            if capacity and capacity > 0:
                total_capacity += capacity
            
            # Add free space - prefer stored value, fallback to connected drive info
            free_space = drive.get('free_space_bytes', 0)
            if free_space and free_space > 0:
                total_free_space += free_space
            else:
                # Fallback to connected drive info if available
                letter = (drive.get('drive_letter') or '').strip().upper()
                if letter and not letter.endswith(':'):
                    letter += ':'
                connected_drive = next((d for d in self.connected_drives if (d.get('letter') or '').upper() == letter), None)
                if connected_drive:
                    free_bytes = connected_drive.get('free', 0)
                    if free_bytes and free_bytes > 0:
                        total_free_space += free_bytes
        
        capacity_text = format_file_size(total_capacity) if total_capacity > 0 else _("Unknown")
        free_text = format_file_size(total_free_space) if total_free_space > 0 else _("Unknown")
        
        summary_text = _("Total Capacity: {capacity} | Total Free Space: {free}").format(
            capacity=capacity_text, free=free_text
        )
        self.inventory_summary_label.setText(summary_text)

    def _handle_remove_drive(self) -> None:
        if not self.db or not self.selected_inventory_drive:
            return
        drive = self.selected_inventory_drive
        label = drive.get('drive_label', 'Sin nombre')
        
        # Create custom QMessageBox with translated buttons
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(_("Remove device"))
        msg_box.setText(_("Do you want to remove '{label}' from inventory? This will delete its registered information.").format(label=label))
        
        # Add custom buttons with translated text
        yes_button = msg_box.addButton(_("Yes"), QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton(_("No"), QMessageBox.ButtonRole.NoRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == yes_button:
            try:
                self.db.delete_drive(drive['id'])
                self._show_feedback(_("'{label}' was removed from inventory.").format(label=label))
                self.drive_removed.emit()
                self.refresh_data()
            except Exception as exc:
                QMessageBox.critical(self, _("Inventory"), _("Could not remove drive: {exc}").format(exc=exc))

    def _update_add_button_state(self) -> None:
        has_selection = self.selected_connected_drive is not None
        has_name = bool(self.friendly_name_input.text().strip())
        self.add_btn.setEnabled(has_selection and has_name)

    def _handle_update_inventory(self):
        selected = self.inventory_list.selectedItems() if self.inventory_list else []
        if not selected:
            return
        item = selected[0]
        drive = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        if not drive:
            return
        drive_letter = drive.get('drive_letter') if isinstance(drive, dict) else None
        if not drive_letter:
            return
        self._start_scan_thread(drive_letter, rescan=True)

    def _start_scan_thread(self, drive_letter, rescan=False, is_new_drive=False):
        self._scan_active = True
        self.scan_worker = ScanWorker(drive_letter)
        self.scan_thread = QThread()
        self.scan_worker.moveToThread(self.scan_thread)
        self.scan_thread.started.connect(self.scan_worker.run)
        self.scan_worker.progress.connect(self._on_scan_progress)
        self.scan_worker.finished.connect(lambda folders, files, inventory_xmls, verbose, scanned_size: self._on_scan_finished(folders, files, inventory_xmls, verbose, scanned_size, drive_letter, rescan, is_new_drive))
        self.scan_thread.start()
        if self.scan_status_label:
            self.scan_status_label.setText(_("(Scanning device...)"))
            self.scan_status_label.show()
        if self.scan_progress_bar:
            self.scan_progress_bar.setValue(0)
            self.scan_progress_bar.show()

    def _on_scan_progress(self, message):
        """Handle real-time scan progress updates"""
        if self.scan_status_label:
            self.scan_status_label.setText(message)
        # Keep progress bar indeterminate during scan since we don't know total
        if self.scan_progress_bar:
            # Show indeterminate progress (animated)
            current_value = self.scan_progress_bar.value()
            if current_value >= 90:
                self.scan_progress_bar.setValue(10)
            else:
                self.scan_progress_bar.setValue(current_value + 10)

    def _on_scan_finished(self, folders, files, inventory_xmls, verbose, scanned_size, drive_letter, rescan, is_new_drive=False):
        
        # Clean up thread first (non-blocking)
        if hasattr(self, 'scan_thread'):
            self.scan_thread.quit()
            # Don't wait here, it blocks UI - let it finish on its own
        
        # Update UI immediately
        if self.scan_status_label:
            self.scan_status_label.setText(_("(Saving to database...)"))
        if self.scan_progress_bar:
            self.scan_progress_bar.setValue(50)
        
        # Process DB updates asynchronously to avoid freezing
        if rescan:
            QTimer.singleShot(100, lambda: self._process_scan_results(folders, files, inventory_xmls, drive_letter, is_new_drive))
        else:
            self._finish_scan_ui(len(files), len(folders), is_new_drive, drive_letter)
    
    def _process_scan_results(self, folders, files, inventory_xmls, drive_letter, is_new_drive=False):
        """Process scan results in batches to avoid UI freeze"""
        from PyQt6.QtWidgets import QApplication
        
        drive = next((d for d in self.inventory_drives if (d.get('drive_letter') or '').upper() == drive_letter.upper()), None)
        drive_id = drive.get('id') if drive and drive.get('id') is not None else None
        
        if drive_id is None:
            self._finish_scan_ui(len(files), len(folders))
            return
        
        try:
            # Clear existing data efficiently
            if hasattr(self.db, 'clear_drive_data'):
                self.db.clear_drive_data(drive_id)
            else:
                if hasattr(self.db, 'clear_files_by_drive'):
                    self.db.clear_files_by_drive(drive_id)
                if hasattr(self.db, 'clear_folders_by_drive'):
                    self.db.clear_folders_by_drive(drive_id)
            
            # Build folder path to ID mapping for parent relationships
            folder_path_to_id = {}
            
            # Process folders in hierarchical order (parents first)
            if folders:
                # Sort folders by level to ensure parents are inserted before children
                folders_sorted = sorted(folders, key=lambda f: f.get('level', 0))
                
                folder_tuples = []
                for f in folders_sorted:
                    folder_name = f.get('folder_name', '')
                    folder_path = f.get('folder_path', '')
                    parent_path = f.get('parent_path', '')
                    level = f.get('level', 0)
                    
                    # Determine parent_folder_id from parent_path
                    parent_folder_id = None
                    if parent_path and parent_path in folder_path_to_id:
                        parent_folder_id = folder_path_to_id[parent_path]
                    
                    folder_tuples.append((drive_id, folder_name, folder_path, parent_folder_id, level))
                
                # Insert folders in batches
                if hasattr(self.db, 'add_folders_batch'):
                    batch_size = 1000
                    inserted_ids_all = []
                    for i in range(0, len(folder_tuples), batch_size):
                        batch = folder_tuples[i:i+batch_size]
                        inserted_ids = self.db.add_folders_batch(batch)
                        inserted_ids_all.extend(inserted_ids)
                        
                        progress = int(25 + (i / len(folder_tuples)) * 25) if folder_tuples else 50
                        if self.scan_progress_bar:
                            self.scan_progress_bar.setValue(progress)
                        QApplication.processEvents()
                    
                    # Build mapping of paths to IDs for all inserted folders
                    for j, folder_tuple in enumerate(folder_tuples):
                        if j < len(inserted_ids_all):
                            folder_path = folder_tuple[2]  # folder_path is at index 2
                            folder_path_to_id[folder_path] = inserted_ids_all[j]
            
            # Process files using batch insert for better performance
            if files:
                file_tuples = []
                for f in files:
                    file_name = f.get('file_name', '')
                    file_path = f.get('file_path', '')
                    file_size = f.get('file_size', 0)
                    file_extension = f.get('file_extension', '')
                    modified_date = f.get('modified_date', '')
                    created_date = f.get('created_date', None)
                    parent_path = f.get('parent_path', '')
                    
                    # Determine parent_folder_id from parent_path
                    parent_folder_id = None
                    if parent_path and parent_path in folder_path_to_id:
                        parent_folder_id = folder_path_to_id[parent_path]
                    
                    file_tuples.append((drive_id, file_name, file_path, file_size, 
                                      file_extension, modified_date, created_date, parent_folder_id))
                
                if hasattr(self.db, 'add_files_batch'):
                    batch_size = 1000
                    for i in range(0, len(file_tuples), batch_size):
                        batch = file_tuples[i:i+batch_size]
                        self.db.add_files_batch(batch)
                        progress = int(50 + (i / len(file_tuples)) * 50) if file_tuples else 100
                        if self.scan_progress_bar:
                            self.scan_progress_bar.setValue(progress)
                        QApplication.processEvents()
            
            # Update counts
            if hasattr(self.db, 'update_drive_counts'):
                self.db.update_drive_counts(drive_id)
            
            # Apply metadata from inventory XML files
            if inventory_xmls and hasattr(self.db, 'apply_inventory_metadata'):
                try:
                    stats = self.db.apply_inventory_metadata(drive_id, inventory_xmls)
                    print(f"Inventory XML import: {stats['files_updated']} files updated, "
                          f"{stats['folders_updated']} folders updated, "
                          f"{stats['not_found']} not found")
                    if self.scan_status_label:
                        self.scan_status_label.setText(_(f"(Imported metadata for {stats['files_updated']} files)"))
                except Exception as e:
                    print(f"Error applying inventory metadata: {e}")
            
            # Update free space from current drive info
            try:
                # Get current drive information to capture free space
                from utils.helpers import get_available_drives
                current_drives = get_available_drives()
                current_drive = next((d for d in current_drives if (d.get('device') or '').upper().startswith(drive_letter.upper())), None)
                
                if current_drive and current_drive.get('free') is not None and current_drive.get('free') > 0:
                    free_space_bytes = current_drive.get('free')
                    # Update the drive with current free space
                    if hasattr(self.db, 'update_drive_by_serial'):
                        serial = drive.get('serial_number')
                        if serial:
                            self.db.update_drive_by_serial(serial, drive_letter, 
                                                         drive.get('drive_label', ''), 
                                                         drive.get('capacity_bytes', 0), 
                                                         free_space_bytes)
            except Exception as e:
                print(f"Warning: Could not update free space: {e}")
        
        except Exception as e:
            print(f"Error processing scan results: {e}")
            self._show_feedback(_("Error saving: {error}").format(error=e), error=True)
        
        # Finish up
        self._finish_scan_ui(len(files), len(folders), is_new_drive, drive_letter)
    
    def _finish_scan_ui(self, file_count, folder_count, is_new_drive=False, drive_letter=None):
        """Complete scan UI updates"""
        print(f"Finishing scan UI. Files: {file_count}, Folders: {folder_count}, Is new drive: {is_new_drive}")
        
        # Refresh inventory to show updated counts
        try:
            self.refresh_data()
        except Exception as e:
            print(f"Error refreshing data: {e}")
        
        if self.scan_status_label:
            self.scan_status_label.setText(_("(Update completed)"))
        if self.scan_progress_bar:
            self.scan_progress_bar.setValue(100)
            self.scan_progress_bar.setFormat("%p%")
            self.scan_progress_bar.hide()
        self._scan_active = False
        if self._progress_anim_timer:
            self._progress_anim_timer.stop()
        self._update_inventory_progress(100)
        if hasattr(self, 'cancel_btn') and self.cancel_btn:
            self.cancel_btn.hide()
        
        feedback_msg = _("Device updated: {files} files, {folders} folders").format(files=file_count, folders=folder_count)
        print(feedback_msg)
        self._show_feedback(feedback_msg)
        
        # Emit signal to update other parts of the application if this was a new drive
        if is_new_drive:
            # Get the newly added drive info
            drives = self.db.get_all_drives()
            new_drive = next((d for d in drives if d.get('drive_letter', '').upper() == drive_letter.upper()), None)
            if new_drive:
                self.drive_added.emit(new_drive)
        
        # Always emit stats updated signal to refresh bottom statistics
        self.stats_updated.emit()


