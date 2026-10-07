from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
import config
from i18n import _

def create_status_bar() -> (QStatusBar, QLabel, QLabel, QProgressBar):
    status_bar = QStatusBar()
    status_bar.setStyleSheet(f"""
        QStatusBar {{
            background-color: {config.COLORS['panel_bg']};
            border-top: 1px solid {config.COLORS['panel_border']};
            padding: 4px;
        }}
    """)
    status_label = QLabel(_("Ready"))
    status_bar.addWidget(status_label)
    status_bar.addPermanentWidget(QLabel("|"))
    stats_label = QLabel(f"0 {_('files')} | 0 {_('drives')}")
    status_bar.addPermanentWidget(stats_label)

    # Botón Acerca de
    about_btn = QPushButton(_("About:"))
    about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    about_btn.setStyleSheet("QPushButton { border: none; color: white; background: transparent; padding: 0 8px; } QPushButton:hover { color: #fff; text-decoration: underline; }")
    status_bar.addPermanentWidget(about_btn)

    # Search progress bar (initially hidden)
    progress_bar = QProgressBar()
    progress_bar.setVisible(False)
    progress_bar.setRange(0, 0)  # Indeterminate progress
    progress_bar.setFixedWidth(200)
    progress_bar.setStyleSheet(f"""
        QProgressBar {{
            border: 1px solid {config.COLORS['panel_border']};
            border-radius: 3px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {config.COLORS['accent_primary']};
        }}
    """)
    status_bar.addPermanentWidget(progress_bar)

    # Devolver el botón para conectar la señal en MainWindow
    return status_bar, status_label, stats_label, progress_bar, about_btn
