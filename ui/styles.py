"""Dark theme styles"""

import config


def get_dark_stylesheet() -> str:
    """Get complete dark theme stylesheet for the application"""
    
    colors = config.COLORS
    
    return f"""
    /* Main Window and Base Styling */
    QMainWindow {{
        background-color: {colors['background']};
        color: {colors['text_primary']};
    }}
    
    QWidget {{
        background-color: {colors['background']};
        color: {colors['text_primary']};
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
    }}
    
    /* Panels and Containers */
    QFrame {{
        background-color: {colors['panel_bg']};
        border: none;
        border-radius: 2px;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {colors['button']};
        color: {colors['text_primary']};
        border: none;
        border-radius: 3px;
        padding: 6px 16px;
        min-height: 24px;
    }}
    
    QPushButton:hover {{
        background-color: {colors['button_hover']};
        border: none;
    }}
    
    QPushButton:pressed {{
        background-color: {colors['accent_primary']};
    }}
    
    QPushButton:disabled {{
        background-color: {colors['panel_bg']};
        color: {colors['text_secondary']};
        border: none;
    }}
    
    /* Mode buttons (top bar) */
    QPushButton#modeButton {{
        background-color: transparent;
        border: none;
        border-bottom: 3px solid transparent;
        border-radius: 0px;
        padding: 8px 20px;
        font-size: 11pt;
        font-weight: bold;
    }}
    
    QPushButton#modeButton:hover {{
        background-color: {colors['hover']};
        border-bottom: 3px solid {colors['accent_hover']};
    }}
    
    QPushButton#modeButton:checked {{
        background-color: {colors['panel_bg']};
        border-bottom: 3px solid {colors['accent_primary']};
        color: {colors['accent_primary']};
    }}
    
    /* Advanced search button */
    QPushButton#advancedSearchButton {{
        background-color: transparent;
        border: 1px solid {colors['panel_border']};
        border-radius: 3px;
        padding: 6px 12px;
        font-size: 10pt;
        color: {colors['text_primary']};
    }}
    
    QPushButton#advancedSearchButton:hover {{
        background-color: {colors['hover']};
        border: 1px solid {colors['accent_primary']};
    }}
    
    QPushButton#advancedSearchButton:checked {{
        background-color: {colors['accent_primary']};
        color: {colors['background']};
        border: 1px solid {colors['accent_primary']};
    }}
    
    /* Input fields */
    QLineEdit {{
        background-color: {colors['input_bg']};
        color: {colors['text_primary']};
        border: none;
        border-radius: 3px;
        padding: 6px;
        selection-background-color: {colors['selection']};
    }}
    
    QLineEdit:focus {{
        border: 1px solid {colors['accent_primary']};
    }}
    
    QTextEdit, QPlainTextEdit {{
        background-color: {colors['input_bg']};
        color: {colors['text_primary']};
        border: none;
        border-radius: 3px;
        padding: 6px;
        selection-background-color: {colors['selection']};
    }}
    
    /* ComboBox */
    QComboBox {{
        background-color: {colors['input_bg']};
        color: {colors['text_primary']};
        border: none;
        border-radius: 3px;
        padding: 6px;
        min-height: 24px;
    }}
    
    QComboBox:hover {{
        border: 1px solid {colors['accent_primary']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {colors['text_primary']};
        margin-right: 5px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {colors['panel_bg']};
        color: {colors['text_primary']};
        selection-background-color: {colors['selection']};
        border: none;
    }}
    
    /* CheckBox and RadioButton */
    QCheckBox, QRadioButton {{
        color: {colors['text_primary']};
        spacing: 8px;
    }}
    
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {colors['panel_border']};
        border-radius: 3px;
        background-color: {colors['input_bg']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {colors['accent_primary']};
        border: 1px solid {colors['accent_primary']};
    }}
    
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
        border: 1px solid {colors['accent_primary']};
    }}
    
    /* Tables and Lists */
    QTableView, QTreeView, QListView {{
        background-color: {colors['background']};
        alternate-background-color: {colors['panel_bg']};
        color: {colors['text_primary']};
        border: none;
        gridline-color: {colors['panel_border']};
        selection-background-color: {colors['selection']};
        selection-color: {colors['text_primary']};
    }}
    
    QTableView::item:hover, QTreeView::item:hover, QListView::item:hover {{
        background-color: {colors['hover']};
    }}
    
    QHeaderView::section {{
        background-color: {colors['panel_bg']};
        color: {colors['text_primary']};
        border: none;
        padding: 6px;
        font-weight: bold;
    }}
    
    QHeaderView::section:hover {{
        background-color: {colors['button_hover']};
    }}
    
    /* ScrollBars */
    QScrollBar:vertical {{
        background-color: {colors['background']};
        width: 14px;
        border: none;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {colors['scrollbar']};
        border-radius: 7px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {colors['button_hover']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: {colors['background']};
        height: 14px;
        border: none;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {colors['scrollbar']};
        border-radius: 7px;
        min-width: 30px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {colors['button_hover']};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* TabWidget */
    QTabWidget::pane {{
        border: none;
        background-color: {colors['background']};
    }}
    
    QTabBar::tab {{
        background-color: {colors['panel_bg']};
        color: {colors['text_primary']};
        border: none;
        padding: 8px 16px;
        margin-right: 2px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {colors['background']};
        border-bottom: 2px solid {colors['accent_primary']};
    }}
    
    QTabBar::tab:hover {{
        background-color: {colors['hover']};
    }}
    
    /* Progress Bar */
    QProgressBar {{
        background-color: {colors['input_bg']};
        border: none;
        border-radius: 3px;
        text-align: center;
        color: {colors['text_primary']};
        height: 20px;
    }}
    
    QProgressBar::chunk {{
        background-color: {colors['accent_primary']};
        border-radius: 2px;
    }}
    
    /* Splitter */
    QSplitter::handle {{
        background-color: {colors['panel_border']};
    }}
    
    QSplitter::handle:hover {{
        background-color: {colors['accent_primary']};
    }}
    
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    
    QSplitter::handle:vertical {{
        height: 2px;
    }}
    
    /* Labels */
    QLabel {{
        color: {colors['text_primary']};
        background-color: transparent;
        border: none;
    }}
    
    QLabel#sectionHeader {{
        font-size: 11pt;
        font-weight: bold;
        color: {colors['accent_primary']};
        padding: 5px;
    }}
    
    QLabel#subHeader {{
        font-size: 9pt;
        color: {colors['text_secondary']};
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {colors['panel_bg']};
        color: {colors['text_primary']};
        border-top: 1px solid {colors['panel_border']};
    }}
    
    /* ToolBar */
    QToolBar {{
        background-color: {colors['panel_bg']};
        border: none;
        padding: 4px;
        spacing: 4px;
    }}
    
    QToolButton {{
        background-color: transparent;
        color: {colors['text_primary']};
        border: 1px solid transparent;
        border-radius: 3px;
        padding: 6px;
    }}
    
    QToolButton:hover {{
        background-color: {colors['hover']};
        border: 1px solid {colors['accent_primary']};
    }}
    
    QToolButton:pressed {{
        background-color: {colors['accent_primary']};
    }}
    
    /* Menu */
    QMenuBar {{
        background-color: {colors['panel_bg']};
        color: {colors['text_primary']};
        border-bottom: 1px solid {colors['panel_border']};
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 6px 12px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {colors['hover']};
    }}
    
    QMenu {{
        background-color: {colors['panel_bg']};
        color: {colors['text_primary']};
        border: 1px solid {colors['panel_border']};
    }}
    
    QMenu::item {{
        padding: 6px 30px 6px 20px;
    }}
    
    QMenu::item:selected {{
        background-color: {colors['selection']};
    }}
    
    /* Tooltips */
    QToolTip {{
        background-color: {colors['panel_bg']};
        color: {colors['text_primary']};
        border: 1px solid {colors['accent_primary']};
        padding: 4px;
    }}
    
    /* GroupBox */
    QGroupBox {{
        color: {colors['text_primary']};
        border: none;
        border-radius: 4px;
        margin-top: 12px;
        padding-top: 12px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        background-color: {colors['background']};
    }}
    
    /* Slider */
    QSlider::groove:horizontal {{
        border: 1px solid {colors['panel_border']};
        height: 6px;
        background: {colors['input_bg']};
        border-radius: 3px;
    }}
    
    QSlider::handle:horizontal {{
        background: {colors['accent_primary']};
        border: 1px solid {colors['accent_primary']};
        width: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {colors['accent_hover']};
    }}
    """


def get_mode_button_style(is_active: bool) -> str:
    """Get style for mode switcher buttons"""
    colors = config.COLORS
    
    if is_active:
        return f"""
            QPushButton {{
                background-color: {colors['panel_bg']};
                color: {colors['accent_primary']};
                border: none;
                border-bottom: 3px solid {colors['accent_primary']};
                border-radius: 0px;
                padding: 10px 24px;
                font-size: 11pt;
                font-weight: bold;
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {colors['text_primary']};
                border: none;
                border-bottom: 3px solid transparent;
                border-radius: 0px;
                padding: 10px 24px;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {colors['hover']};
                border-bottom: 3px solid {colors['accent_hover']};
            }}
        """
