from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QButtonGroup
from PyQt6.QtCore import Qt
import config
from typing import Tuple
from i18n import _

def create_top_bar(switch_mode_callback, settings_callback=None) -> Tuple[QWidget, dict, QButtonGroup, QPushButton]:
    """Create top bar with mode switcher buttons and settings button. Returns (widget, mode_buttons, button_group, settings_button)"""
    top_bar = QWidget()
    top_bar.setFixedHeight(50)
    top_bar.setStyleSheet(f"background-color: {config.COLORS['panel_bg']};")

    layout = QHBoxLayout(top_bar)
    layout.setContentsMargins(20, 0, 20, 0)
    layout.setSpacing(0)

    # App title/logo with icon
    title_layout = QHBoxLayout()
    title_layout.setSpacing(8)
    
    # Icon label
    icon_label = QLabel()
    from PyQt6.QtGui import QPixmap
    icon_path = config.BASE_DIR / "icon.ico"
    if icon_path.exists():
        pixmap = QPixmap(str(icon_path))
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        else:
            icon_label.setText("📦")  # Fallback emoji
    else:
        icon_label.setText("📦")  # Fallback emoji
    icon_label.setFixedSize(24, 24)
    title_layout.addWidget(icon_label)
    
    # Text label
    text_label = QLabel(config.APP_NAME)
    text_label.setStyleSheet(f"""
        font-size: 14pt;
        font-weight: bold;
        color: {config.COLORS['accent_primary']};
    """)
    title_layout.addWidget(text_label)
    
    # Create a container widget for the title
    title_widget = QWidget()
    title_widget.setLayout(title_layout)
    layout.addWidget(title_widget)

    layout.addSpacing(40)

    # Mode switcher buttons
    mode_buttons = {}
    button_group = QButtonGroup(top_bar)
    modes = [
        ('inventory', f'📦 {_("Inventory")}'),
        ('manage', f'💾 {_("Manage")}'),
        ('statistics', f'📊 {_("Statistics")}')
    ]
    for mode_id, mode_label in modes:
        btn = QPushButton(mode_label)
        btn.setCheckable(True)
        btn.setObjectName('modeButton')
        btn.clicked.connect(lambda checked, m=mode_id: switch_mode_callback(m))
        mode_buttons[mode_id] = btn
        button_group.addButton(btn)
        layout.addWidget(btn)

    layout.addStretch()

    # Settings button
    settings_button = QPushButton("⚙️")
    settings_button.setFixedSize(40, 40)
    settings_button.setToolTip(_("Settings"))
    settings_button.setObjectName('settingsButton')
    settings_button.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            border: none;
            color: {config.COLORS['text_secondary']};
            font-size: 16pt;
            padding: 0;
        }}
        QPushButton:hover {{
            color: {config.COLORS['accent_primary']};
            background-color: {config.COLORS['hover']};
        }}
    """)
    if settings_callback:
        settings_button.clicked.connect(settings_callback)
    layout.addWidget(settings_button)

    mode_buttons['inventory'].setChecked(True)
    return top_bar, mode_buttons, button_group, settings_button
