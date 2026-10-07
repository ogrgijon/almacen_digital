

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel
from PyQt6.QtCore import Qt
from core.database import DatabaseManager
from ui.statistics_panel import StatisticsPanel
from i18n import _

def create_statistics_widget(smart_info_callback=None) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    # Set initial styling
    from ui.styles import get_dark_stylesheet
    widget.setStyleSheet(get_dark_stylesheet())

    # Show loading message initially
    loading_label = QLabel(_("🔄 Loading statistics panel..."))
    loading_label.setStyleSheet("""
        QLabel {
            color: #e0e0e0;
            font-size: 14px;
            text-align: center;
            padding: 40px;
        }
    """)
    loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(loading_label)

    # Load statistics widget asynchronously
    from PyQt6.QtCore import QTimer
    def load_statistics():
        try:
            layout.removeWidget(loading_label)
            loading_label.deleteLater()
            
            db = DatabaseManager()
            drives = db.get_all_drives()
            if not drives:
                layout.addWidget(QLabel(_("No drives found in inventory.")))
                return

            drive_selector = QComboBox()
            drive_selector.addItems([f"{d.get('drive_label', _('Unknown'))} ({d.get('drive_letter', '')})" for d in drives])
            layout.addWidget(QLabel(_("Select Drive:")))
            layout.addWidget(drive_selector)

            # Panel holder
            panel_holder = QVBoxLayout()
            layout.addLayout(panel_holder)

            def show_panel(idx):
                # Remove previous panel
                while panel_holder.count():
                    item = panel_holder.takeAt(0)
                    w = item.widget()
                    if w:
                        w.setParent(None)
                drive = drives[idx]
                panel = StatisticsPanel(str(db.db_path), drive['id'], drive.get('drive_letter', ''), smart_info_callback)
                panel_holder.addWidget(panel)

            drive_selector.currentIndexChanged.connect(show_panel)
            show_panel(0)
            
        except Exception as e:
            layout.removeWidget(loading_label)
            loading_label.deleteLater()
            error_label = QLabel(_("Error loading statistics: {error}").format(error=str(e)))
            error_label.setStyleSheet("color: #f44336; padding: 20px;")
            layout.addWidget(error_label)

    QTimer.singleShot(100, load_statistics)  # Load after window is shown
    
    return widget
