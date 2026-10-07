"""
statistics_panel.py - Best-in-class statistics panel for Almacén Digital

Displays:
- Drive overview (consumption, free space, S.M.A.R.T. health)
- File size treemap
- File type distribution
- S.M.A.R.T. trace/history and replacement recommendation
- Largest files/folders

Modular, well-documented, and ready for extension.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, 
                             QTableWidget, QTableWidgetItem, QFrame, QGridLayout, QHeaderView, QPushButton)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from core.smart.smart_reader import get_smart_status, SmartStatus
from core.smart.smart_db import SmartDB
from core.database import DatabaseManager
from utils.helpers import format_file_size, find_smartctl
import config
from i18n import _

class StatisticsPanel(QWidget):
    """Comprehensive statistics panel with device health and usage analytics."""
    def __init__(self, db_path: str, drive_id: int, drive_letter: str, smart_info_callback=None, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.drive_id = drive_id
        self.drive_letter = drive_letter
        self.smart_info_callback = smart_info_callback
        self.colors = config.COLORS
        
        # Set dark theme background
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text_primary']};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors['panel_border']};
                border-radius: 10px;
                margin: 8px;
                background: {self.colors['panel_bg']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        self.setLayout(layout)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabBar::tab {{
                background: {self.colors['panel_bg']};
                color: {self.colors['text_primary']};
                padding: 10px 24px;
                margin: 2px;
                border-radius: 8px 8px 0 0;
                font-size: 14px;
            }}
            QTabBar::tab:selected {{
                background: {self.colors['button']};
                color: {self.colors['text_primary']};
            }}
        """)
        layout.addWidget(self.tabs)

        import shutil
        self.smartctl_path = find_smartctl()
        self.smartctl_available = self.smartctl_path is not None

        self._init_overview_tab()
        self._init_treemap_tab()
        self._init_filetype_tab()
        
        # Check if SMART data is available before creating the tab
        smart_data_available = self._check_smart_data_available()
        if smart_data_available:
            self._init_smart_trace_tab()
            
        self._init_largest_files_tab()

    def _check_smart_data_available(self):
        """Check if there's any SMART data available for this drive."""
        if not self.smartctl_available:
            return False
            
        # Check if we can get current SMART status
        from core.smart.smart_reader import get_smart_status
        smart = get_smart_status(self.drive_letter, self.smartctl_path)
        
        # Show tab if we have data OR if admin privileges are just needed
        if smart['status'] not in [SmartStatus.NOT_SUPPORTED, SmartStatus.UNKNOWN]:
            return True
            
        # Also show tab if admin is required (so user can elevate)
        if smart.get('error') == 'Administrator privileges required':
            return True
            
        # Check if there's historical SMART data
        db = SmartDB(self.db_path)
        history = db.get_smart_history(self.drive_id)
        db.close()
        
        return len(history) > 0

    def _init_overview_tab(self):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from core.database import DatabaseManager
        from utils.helpers import format_file_size

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        db = DatabaseManager()
        drive = db.get_drive_by_id(self.drive_id)
        if not drive:
            error_label = QLabel(_("Drive not found."))
            error_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
            layout.addWidget(error_label)
            self.tabs.addTab(tab, _("Overview"))
            return

        # Drive header with health status
        header_widget = self._create_drive_header(drive)
        layout.addWidget(header_widget)

        # Space usage visualization
        if drive.get('capacity_bytes', 0) > 0:
            space_widget = self._create_space_visualization(drive)
            layout.addWidget(space_widget)

        # Drive details
        details_widget = self._create_drive_details(drive)
        layout.addWidget(details_widget)

        # Note about data sources
        note_label = QLabel(_("📝 Note: File and folder statistics are from the last scan. Storage usage reflects current disk state."))
        note_label.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 11px; font-style: italic; margin-top: 8px;")
        layout.addWidget(note_label)

        layout.addStretch()  # Push content to top
        self.tabs.addTab(tab, _("📊 Overview"))

    def _create_drive_header(self, drive):
        """Create a styled header with drive info and health status"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.Box)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['panel_bg']};
                border: 1px solid {self.colors['panel_border']};
                border-radius: 6px;
                padding: 2px 4px;
                margin-bottom: 2px;
                min-height: 32px;
            }}
            QLabel {{
                color: {self.colors['text_primary']};
            }}
        """)

        header_layout = QHBoxLayout(header_frame)

        # Drive icon and basic info
        drive_icon = QLabel("💾")
        drive_icon.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(drive_icon)

        drive_info = QLabel(f"<b>{drive.get('drive_label', _('Unknown Drive'))}</b><br>"
                           f"<span style='color: #666;'>{drive.get('drive_letter', '')}</span>")
        drive_info.setStyleSheet("font-size: 14px;")
        header_layout.addWidget(drive_info)

        header_layout.addStretch()

        # Health status
        if self.smartctl_available:
            from core.smart.smart_reader import get_smart_status
            smart = get_smart_status(drive.get('drive_letter', ''), self.smartctl_path)
            status = smart['status']
            error = smart.get('error', '')

            # Color coding for health status
            if 'PASSED' in status.upper() or 'OK' in status.upper():
                status_color = "#4caf50"
                status_icon = "✅"
            elif 'FAILED' in status.upper() or 'FAILING' in status.upper():
                status_color = "#f44336"
                status_icon = "❌"
            elif 'NOT_SUPPORTED' in status.upper():
                if 'Administrator' in error:
                    # Create a button to elevate privileges
                    health_button = QPushButton(_("🔒 Run as Administrator"))
                    health_button.setStyleSheet("""
                        QPushButton {
                            color: #ff9800;
                            font-weight: bold;
                            font-size: 12px;
                            padding: 5px 10px;
                            background-color: #ff980022;
                            border-radius: 4px;
                            border: none;
                            text-align: left;
                        }
                        QPushButton:hover {
                            background-color: #ff980044;
                        }
                    """)
                    health_button.clicked.connect(self._elevate_to_admin)
                    health_label = health_button
                else:
                    status_color = "#9e9e9e"
                    status_icon = "🚫"
                    health_label = QLabel(_("{icon} S.M.A.R.T.: {status}").format(icon=status_icon, status=status))
                    health_label.setStyleSheet(f"""
                        QLabel {{
                            color: {status_color};
                            font-weight: bold;
                            font-size: 12px;
                            padding: 5px 10px;
                            background-color: {status_color}22;
                            border-radius: 4px;
                        }}
                    """)
            else:
                status_color = "#ff9800"
                status_icon = "⚠️"
                health_label = QLabel(_("{icon} S.M.A.R.T.: {status}").format(icon=status_icon, status=status))
                health_label.setStyleSheet(f"""
                    QLabel {{
                        color: {status_color};
                        font-weight: bold;
                        font-size: 12px;
                        padding: 5px 10px;
                        background-color: {status_color}22;
                        border-radius: 4px;
                    }}
                """)
        else:
            health_button = QPushButton(_("⚠️ S.M.A.R.T.: Unavailable"))
            health_button.setStyleSheet("""
                QPushButton {
                    color: #ff9800;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 5px 10px;
                    background-color: #ff980022;
                    border-radius: 4px;
                    border: none;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #ff980044;
                }
            """)
            if self.smart_info_callback:
                health_button.clicked.connect(self.smart_info_callback)
            health_label = health_button

        header_layout.addWidget(health_label)
        return header_frame

    def _create_space_visualization(self, drive):
        """Create an improved space usage visualization"""
        space_frame = QFrame()
        space_frame.setFrameStyle(QFrame.Shape.Box)
        space_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['panel_bg']};
                border: 1px solid {self.colors['panel_border']};
                border-radius: 6px;
                padding: 2px 4px;
                margin-bottom: 2px;
                min-height: 32px;
            }}
            QLabel {{
                color: {self.colors['text_primary']};
            }}
        """)

        space_layout = QVBoxLayout(space_frame)

        # Title
        title = QLabel(_("💿 Storage Usage"))
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        space_layout.addWidget(title)

        # Calculate space values using real-time data
        try:
            import shutil
            usage = shutil.disk_usage(self.drive_letter)
            capacity = usage.total
            free_bytes = usage.free
            used_bytes = usage.used
        except (OSError, AttributeError):
            # Fallback to database values if disk usage fails
            capacity = drive.get('capacity_bytes', 0)
            free_bytes = drive.get('free_space_bytes', 0) if drive.get('free_space_bytes') is not None else 0
            used_bytes = capacity - free_bytes

        if capacity > 0:
            used_percent = (used_bytes / capacity) * 100
            free_percent = (free_bytes / capacity) * 100

            # Determine color based on usage
            if used_percent >= 90:
                bar_color = "#f44336"  # Red
                status_text = _("Critical")
                status_color = "#f44336"
            elif used_percent >= 75:
                bar_color = "#ff9800"  # Orange
                status_text = _("Warning")
                status_color = "#ff9800"
            elif used_percent >= 50:
                bar_color = "#ffeb3b"  # Yellow
                status_text = _("Moderate")
                status_color = "#ff9800"
            else:
                bar_color = "#4caf50"  # Green
                status_text = _("Good")
                status_color = "#4caf50"

            # Progress bar visualization
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 1.2))
            fig.patch.set_facecolor(self.colors['panel_bg'])
            ax.set_facecolor(self.colors['panel_bg'])
            ax.barh([0], [used_percent/100], color=bar_color, height=0.6, edgecolor='black', linewidth=0.5)
            ax.barh([0], [free_percent/100], left=[used_percent/100], color='#e8f5e8', height=0.6,
                   edgecolor='black', linewidth=0.5)

            ax.set_xlim(0, 1)
            ax.set_ylim(-0.5, 0.5)
            ax.set_xticks([0, used_percent/100, 1])
            ax.set_xticklabels(['0%', f'{used_percent:.1f}%', '100%'])
            ax.set_yticks([])
            ax.set_title(f"{_('Space Usage:')} {status_text}", fontsize=11, fontweight='bold', color=status_color)

            # Add usage text on the bar
            ax.text(used_percent/200, 0, f'{_("Used:")} {format_file_size(used_bytes)}',
                   ha='center', va='center', fontsize=9, fontweight='bold', color='white')
            ax.text(used_percent/100 + free_percent/200, 0, f'{_("Free:")} {format_file_size(free_bytes)}',
                   ha='center', va='center', fontsize=9, fontweight='bold', color='black')

            fig.tight_layout()
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
            canvas = FigureCanvas(fig)
            space_layout.addWidget(canvas)
            plt.close(fig)

            # Detailed statistics
            stats_layout = QHBoxLayout()

            # Used space
            used_label = QLabel(_("<b>Used:</b> {size} ({percent:.1f}%)").format(size=format_file_size(used_bytes), percent=used_percent))
            used_label.setStyleSheet(f"color: {bar_color}; font-size: 12px;")
            stats_layout.addWidget(used_label)

            # Free space
            free_label = QLabel(_("<b>Free:</b> {size} ({percent:.1f}%)").format(size=format_file_size(free_bytes), percent=free_percent))
            free_label.setStyleSheet("color: #4caf50; font-size: 12px;")
            stats_layout.addWidget(free_label)

            # Total capacity
            total_label = QLabel(_("<b>Total:</b> {size}").format(size=format_file_size(capacity)))
            total_label.setStyleSheet("font-size: 12px;")
            stats_layout.addWidget(total_label)

            stats_layout.addStretch()
            space_layout.addLayout(stats_layout)

        return space_frame

    def _create_drive_details(self, drive):
        """Create detailed drive information widget"""
        details_frame = QFrame()
        details_frame.setFrameStyle(QFrame.Shape.Box)
        details_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['panel_bg']};
                border: 1px solid {self.colors['panel_border']};
                border-radius: 6px;
                padding: 2px 4px;
                margin-bottom: 2px;
                min-height: 32px;
            }}
            QLabel {{
                color: {self.colors['text_primary']};
            }}
        """)

        details_layout = QGridLayout(details_frame)
        details_layout.setSpacing(8)

        # Title
        details_title = QLabel(_("📋 Drive Details"))
        details_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        details_layout.addWidget(details_title, 0, 0, 1, 2)

        # Drive information
        details_layout.addWidget(QLabel(_("<b>Serial Number:</b>")), 1, 0)
        details_layout.addWidget(QLabel(drive.get('serial_number', _('Unknown'))), 1, 1)

        details_layout.addWidget(QLabel(_("<b>Capacity:</b>")), 2, 0)
        from utils.helpers import format_file_size
        details_layout.addWidget(QLabel(format_file_size(drive.get('capacity_bytes', 0))), 2, 1)

        details_layout.addWidget(QLabel(_("<b>Files:</b>")), 3, 0)
        details_layout.addWidget(QLabel(f"{drive.get('file_count', 0):,}"), 3, 1)

        details_layout.addWidget(QLabel(_("<b>Folders:</b>")), 4, 0)
        details_layout.addWidget(QLabel(f"{drive.get('folder_count', 0):,}"), 4, 1)

        details_layout.addWidget(QLabel(_("<b>Last Scanned:</b>")), 5, 0)
        details_layout.addWidget(QLabel(drive.get('last_scanned', _('Never'))), 5, 1)

        return details_frame

    def _init_treemap_tab(self):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        try:
            import squarify
        except ImportError:
            # Fallback if squarify not available
            tab = QWidget()
            layout = QVBoxLayout(tab)
            layout.setSpacing(4)
            layout.setContentsMargins(4, 4, 4, 4)

            error_label = QLabel(_("📊 Treemap requires 'squarify' package. Please install with: pip install squarify"))
            error_label.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 14px; text-align: center; padding: 40px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)
            self.tabs.addTab(tab, _("🗂️ Treemap"))
            return

        from core.database import DatabaseManager
        from utils.helpers import format_file_size

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)

        # Title
        title = QLabel(_("🗂️ Folder Size Treemap"))
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Description
        desc = QLabel(_("Visual representation of folder sizes. Larger rectangles represent larger folders."))
        desc.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 15px;")
        layout.addWidget(desc)

        # Loading content - will be replaced when tab is activated
        loading_label = QLabel(_("🔄 Analyzing folder structure...\nThis may take a few moments for large drives."))
        loading_label.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['text_primary']};
                font-size: 14px;
                text-align: center;
                padding: 60px 20px;
                background-color: {self.colors['panel_bg']};
                border-radius: 8px;
                border: 1px solid {self.colors['panel_border']};
            }}
        """)
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label.setWordWrap(True)
        layout.addWidget(loading_label)

        # Flag to track if treemap has been loaded
        treemap_loaded = False

        # Add tab to UI first
        self.tabs.addTab(tab, _("🗂️ Treemap"))

        # Connect tab change signal to load data only when this tab is selected
        def on_tab_changed(index):
            nonlocal treemap_loaded
            if self.tabs.tabText(index) == _("🗂️ Treemap") and not treemap_loaded:
                try:
                    # Load data asynchronously
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(100, lambda: self._load_treemap_data(layout, loading_label))
                    
                    treemap_loaded = True
                except RuntimeError:
                    # QLabel has been deleted, just mark as loaded to prevent further attempts
                    treemap_loaded = True

        self.tabs.currentChanged.connect(on_tab_changed)

    def _load_treemap_data(self, layout, loading_label):
        """Load treemap data asynchronously when tab is activated"""
        try:
            from core.database import DatabaseManager
            from utils.helpers import format_file_size
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
            import squarify
            import numpy as np

            db = DatabaseManager()
            # Limit depth and add operation counter for safety - reduced depth for better performance
            hierarchy = db.get_folder_size_hierarchy(self.drive_id, None, max_depth=1)  # Reduced depth for speed
            db.close()
            
            # Remove loading label
            layout.removeWidget(loading_label)
            loading_label.deleteLater()
            
            # Process the hierarchy data
            def flatten_hierarchy(nodes, parent_name=""):
                flat = []
                for n in nodes:
                    if not isinstance(n, dict) or 'name' not in n or 'size' not in n:
                        continue
                    label = f"{parent_name}/{n['name']}" if parent_name else n['name']
                    if n.get('children'):
                        flat.extend(flatten_hierarchy(n['children'], label))
                    else:
                        flat.append({'label': label, 'size': n['size']})
                return flat

            flat = flatten_hierarchy(hierarchy)
            sizes = [f['size'] for f in flat if f['size'] > 0]
            labels = [f['label'] for f in flat if f['size'] > 0]

            if sizes and len(sizes) > 0:
                # Sort by size for better visualization
                sorted_data = sorted(zip(sizes, labels), reverse=True)
                sizes, labels = zip(*sorted_data)

                # Limit to top 20 for readability
                sizes = sizes[:20]
                labels = labels[:20]

                # Create treemap
                fig, ax = plt.subplots(figsize=(10, 6))
                fig.patch.set_facecolor(self.colors['panel_bg'])
                ax.set_facecolor(self.colors['panel_bg'])

                # Color scheme based on size
                norm_sizes = np.array(sizes) / max(sizes) if max(sizes) > 0 else np.ones(len(sizes))
                colors = plt.cm.viridis(norm_sizes)

                try:
                    squarify.plot(sizes=sizes, label=None, ax=ax, alpha=0.8, color=colors,
                                 text_kwargs={'fontsize': 8, 'color': 'white', 'fontweight': 'bold'})
                except Exception as e:
                    ax.text(0.5, 0.5, _("Treemap error: {error}").format(error=str(e)), ha='center', va='center', transform=ax.transAxes)
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)

                ax.set_title(_("Folder Size Distribution"), fontsize=14, fontweight='bold', pad=20, color=self.colors['text_primary'])
                ax.axis('off')

                # Add legend with top folders
                legend_labels = []
                for i, (size, label) in enumerate(zip(sizes[:10], labels[:10])):
                    short_label = label.split('/')[-1] if '/' in label else label
                    if len(short_label) > 20:
                        short_label = short_label[:17] + "..."
                    legend_labels.append(f"{short_label}: {format_file_size(size)}")

                # Create legend
                legend_text = "\n".join(legend_labels)
                legend_label = QLabel(f"<b>{_('Top Folders:')}</b><br>{legend_text}")
                legend_label.setStyleSheet(f"""
                    QLabel {{
                        background: {self.colors['panel_bg']};
                        border: 1px solid {self.colors['panel_border']};
                        border-radius: 4px;
                        padding: 2px 4px;
                        font-size: 12px;
                        color: {self.colors['text_primary']};
                        line-height: 1.4;
                    }}
                """)
                legend_label.setWordWrap(True)

                # Layout with chart and legend
                from PyQt6.QtWidgets import QHBoxLayout
                content_layout = QHBoxLayout()
                canvas = FigureCanvas(fig)
                content_layout.addWidget(canvas, 3)  # Chart takes 3/4 of space
                content_layout.addWidget(legend_label, 1)  # Legend takes 1/4 of space

                layout.addLayout(content_layout)
                plt.close(fig)
            else:
                no_data_label = QLabel(_("📁 No folder size data available for this drive."))
                no_data_label.setStyleSheet(f"""
                    QLabel {{
                        color: {self.colors['text_secondary']};
                        font-size: 14px;
                        text-align: center;
                        padding: 40px;
                    }}
                """)
                no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(no_data_label)
                
        except Exception as e:
            # Remove loading label
            layout.removeWidget(loading_label)
            loading_label.deleteLater()
            
            error_label = QLabel(_("Error loading folder data: {error}").format(error=str(e)))
            error_label.setStyleSheet(f"color: #f44336; font-size: 14px; text-align: center; padding: 40px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)

    def _init_filetype_tab(self):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from core.database import DatabaseManager

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        # Title
        title = QLabel(_("📄 File Type Distribution"))
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Description
        desc = QLabel(_("Breakdown of files by type/extension on this drive."))
        desc.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 15px;")
        layout.addWidget(desc)

        db = DatabaseManager()
        if db.cursor:
            db.cursor.execute("""
                SELECT file_extension, COUNT(*) as count,
                       SUM(file_size) as total_size
                FROM files
                WHERE drive_id = ?
                GROUP BY file_extension
                ORDER BY count DESC
                LIMIT 15
            """, (self.drive_id,))
            top_exts = [dict(row) for row in db.cursor.fetchall()]
        else:
            top_exts = []

        if top_exts:
            # Create two-column layout: chart on left, details on right
            content_layout = QHBoxLayout()

            # Pie chart with better sizing and colors for dark theme
            fig, ax = plt.subplots(figsize=(4, 3.5))  # Smaller, more appropriate size
            fig.patch.set_facecolor(self.colors['panel_bg'])
            ax.set_facecolor(self.colors['panel_bg'])

            sizes = [e['count'] for e in top_exts]
            labels = [e['file_extension'] or '[no extension]' for e in top_exts]

            # Truncate long labels to prevent layout breaking
            labels = [label[:10] + '...' if len(label) > 10 else label for label in labels]

            # Dark theme friendly color scheme - use tab20 or custom dark colors
            import numpy as np
            # Create a dark theme friendly color palette
            dark_colors = [
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
                '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2'
            ]
            colors = dark_colors[:len(sizes)] if len(sizes) <= len(dark_colors) else plt.cm.tab20(np.linspace(0, 1, len(sizes)))

            wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct='%1.1f%%',
                                            startangle=140, colors=colors, pctdistance=0.8,
                                            wedgeprops=dict(width=0.6, edgecolor=self.colors['panel_border']))

            # Improve text styling for dark theme
            for autotext in autotexts:
                autotext.set_color('white')  # White text for better contrast on dark backgrounds
                autotext.set_fontweight('bold')
                autotext.set_fontsize(8)

            ax.set_title(_('File Type Distribution'), fontsize=12, fontweight='bold', pad=15, color=self.colors['text_primary'])

            # Create legend inside the plot area, not outside
            legend_labels = [f"{label} ({sizes[i]:,})" for i, label in enumerate(labels)]
            ax.legend(wedges[:8], legend_labels[:8], title=_("Top Types"), loc="lower center",
                     bbox_to_anchor=(0.5, -0.15), fontsize=7, ncol=2, frameon=False,
                     title_fontsize=8, labelcolor=self.colors['text_primary'])

            # Adjust layout to make room for legend
            fig.subplots_adjust(bottom=0.25)

            canvas = FigureCanvas(fig)
            content_layout.addWidget(canvas, 1)  # Chart takes 1/2 of space
            plt.close(fig)

            # Details table
            details_frame = QFrame()
            details_frame.setStyleSheet(f"""
                QFrame {{
                    background: {self.colors['panel_bg']};
                    border: 1px solid {self.colors['panel_border']};
                    border-radius: 4px;
                    padding: 2px 4px;
                    min-height: 24px;
                }}
            """)

            details_layout = QVBoxLayout(details_frame)

            details_title = QLabel(_("📊 Details"))
            details_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
            details_layout.addWidget(details_title)

            table = QTableWidget(len(top_exts), 4)
            table.setHorizontalHeaderLabels([_("Extension"), _("Count"), _("Total Size"), _("% of Total")])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            total_files = sum(e['count'] for e in top_exts)

            for row, ext in enumerate(top_exts):
                ext_name = ext['file_extension'] or '[no extension]'
                count = ext['count']
                total_size = ext['total_size'] or 0
                percentage = (count / total_files) * 100

                table.setItem(row, 0, QTableWidgetItem(ext_name))
                table.setItem(row, 1, QTableWidgetItem(f"{count:,}"))
                table.setItem(row, 2, QTableWidgetItem(format_file_size(total_size)))
                table.setItem(row, 3, QTableWidgetItem(f"{percentage:.1f}%"))

            # Style the table
            table.setAlternatingRowColors(True)
            table.setStyleSheet(f"""
                QTableWidget {{
                    gridline-color: {self.colors['panel_border']};
                    selection-background-color: {self.colors['selection']};
                    background-color: {self.colors['panel_bg']};
                    color: {self.colors['text_primary']};
                    font-size: 13px;
                    padding: 8px;
                }}
                QHeaderView::section {{
                    background-color: {self.colors['button']};
                    color: {self.colors['text_primary']};
                    padding: 12px 8px;
                    border: 1px solid {self.colors['panel_border']};
                    font-weight: bold;
                    font-size: 13px;
                }}
            """)

            details_layout.addWidget(table)
            content_layout.addWidget(details_frame, 1)  # Details take 1/3 of space

            layout.addLayout(content_layout)
        else:
            no_data_label = QLabel(_("📄 No file type data available for this drive."))
            no_data_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.colors['text_secondary']};
                    font-size: 14px;
                    text-align: center;
                    padding: 40px;
                }}
            """)
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_data_label)

        self.tabs.addTab(tab, _("📄 File Types"))

    def _init_smart_trace_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)

        # Check if admin privileges are required
        from core.smart.smart_reader import get_smart_status
        smart = get_smart_status(self.drive_letter, self.smartctl_path)
        
        if smart.get('error') == 'Administrator privileges required':
            # Show admin elevation prompt
            admin_frame = QFrame()
            admin_frame.setStyleSheet(f"""
                QFrame {{
                    background: {self.colors['panel_bg']};
                    border: 1px solid {self.colors['panel_border']};
                    border-radius: 8px;
                    padding: 20px;
                    margin: 10px;
                }}
            """)
            admin_layout = QVBoxLayout(admin_frame)
            
            admin_icon = QLabel("🔒")
            admin_icon.setStyleSheet("font-size: 48px; margin-bottom: 10px;")
            admin_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            admin_layout.addWidget(admin_icon)
            
            admin_title = QLabel(_("Administrator Privileges Required"))
            admin_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
            admin_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            admin_layout.addWidget(admin_title)
            
            admin_desc = QLabel(_("SMART data requires administrator privileges to access physical drives.\n\n"
                                "Click the button below to restart the application as administrator."))
            admin_desc.setStyleSheet(f"color: {self.colors['text_secondary']}; margin-bottom: 20px;")
            admin_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            admin_layout.addWidget(admin_desc)
            
            elevate_btn = QPushButton(_("🚀 Run as Administrator"))
            elevate_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.colors['accent_primary']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['accent_hover']};
                }}
            """)
            elevate_btn.clicked.connect(self._elevate_to_admin)
            admin_layout.addWidget(elevate_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            
            layout.addWidget(admin_frame)
            layout.addStretch()
            
        else:
            # Normal SMART tab content
            # Title and refresh button
            title_layout = QHBoxLayout()
            title = QLabel(_("🔧 S.M.A.R.T. Health Monitor"))
            title.setStyleSheet("font-size: 16px; font-weight: bold;")
            title_layout.addWidget(title)
            
            title_layout.addStretch()
            
            refresh_btn = QPushButton(_("🔄 Refresh"))
            refresh_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.colors['button']};
                    color: {self.colors['text_primary']};
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors['button_hover']};
                }}
            """)
            refresh_btn.clicked.connect(lambda: self._refresh_smart_tab(tab))
            title_layout.addWidget(refresh_btn)
            
            layout.addLayout(title_layout)

            # Current SMART status
            status = smart['status']
            attributes = smart.get('attributes', {})

            # Collect and save current SMART data
            self._collect_smart_data()

            # Current status display
            status_frame = QFrame()
            status_frame.setStyleSheet(f"""
                QFrame {{
                    background: {self.colors['panel_bg']};
                    border: 1px solid {self.colors['panel_border']};
                    border-radius: 8px;
                    padding: 10px;
                    margin-bottom: 15px;
                }}
            """)
            status_layout = QHBoxLayout(status_frame)
            
            # Status icon and text
            if 'PASSED' in status.upper() or 'OK' in status.upper():
                status_color = "#4caf50"
                status_icon = "✅"
            elif 'FAILED' in status.upper() or 'FAILING' in status.upper():
                status_color = "#f44336"
                status_icon = "❌"
            elif 'NOT_SUPPORTED' in status.upper():
                status_color = "#9e9e9e"
                status_icon = "🚫"
            else:
                status_color = "#ff9800"
                status_icon = "⚠️"
                
            status_label = QLabel(f"{status_icon} Current Status: {status}")
            status_label.setStyleSheet(f"""
                QLabel {{
                    color: {status_color};
                    font-weight: bold;
                    font-size: 14px;
                }}
            """)
            status_layout.addWidget(status_label)
            status_layout.addStretch()
            
            # Show key attributes if available
            if attributes:
                attr_text = []
                if 'Temperature_Celsius' in attributes:
                    attr_text.append(f"🌡️ {attributes['Temperature_Celsius']}°C")
                if 'Power_On_Hours' in attributes:
                    attr_text.append(f"⚡ {attributes['Power_On_Hours']}h")
                if 'Reallocated_Sector_Ct' in attributes:
                    attr_text.append(f"🔄 {attributes['Reallocated_Sector_Ct']} sectors")
                    
                if attr_text:
                    attr_label = QLabel(" | ".join(attr_text))
                    attr_label.setStyleSheet(f"color: {self.colors['text_secondary']}; font-size: 12px;")
                    status_layout.addWidget(attr_label)
            
            layout.addWidget(status_frame)

        # Historical data section
        db = SmartDB(self.db_path)
        history = db.get_smart_history(self.drive_id)

        if history:
            # History title
            history_title = QLabel(_("📊 Health History"))
            history_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px; margin-bottom: 5px;")
            layout.addWidget(history_title)

            table = QTableWidget(len(history), 5)
            table.setHorizontalHeaderLabels([_("📅 Date"), _("📊 Status"), _("🔄 Reallocated"), _("🌡️ Temp (°C)"), _("⚡ Power Hours")])

            # Style the table
            table.setAlternatingRowColors(True)
            table.setStyleSheet(f"""
                QTableWidget {{
                    gridline-color: {self.colors['panel_border']};
                    selection-background-color: {self.colors['selection']};
                    background-color: {self.colors['panel_bg']};
                    color: {self.colors['text_primary']};
                }}
                QHeaderView::section {{
                    background-color: {self.colors['button']};
                    color: {self.colors['text_primary']};
                    padding: 8px;
                    border: 1px solid {self.colors['panel_border']};
                    font-weight: bold;
                }}
            """)

            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            for row, entry in enumerate(history):
                date_item = QTableWidgetItem(str(entry.get('date', '')))
                table.setItem(row, 0, date_item)

                # Status with color coding
                status = str(entry.get('status', ''))
                status_item = QTableWidgetItem(status)
                if 'PASSED' in status.upper():
                    status_item.setBackground(QColor('#e8f5e8'))
                    status_item.setForeground(QColor('#2e7d32'))
                elif 'FAILED' in status.upper():
                    status_item.setBackground(QColor('#ffebee'))
                    status_item.setForeground(QColor('#c62828'))
                else:
                    status_item.setBackground(QColor('#fff3e0'))
                    status_item.setForeground(QColor('#ef6c00'))
                table.setItem(row, 1, status_item)

                # Reallocated sectors with warning colors
                reallocated = entry.get('reallocated_sectors', 0)
                reallocated_item = QTableWidgetItem(str(reallocated))
                if reallocated > 10:
                    reallocated_item.setBackground(QColor('#ffebee'))
                    reallocated_item.setForeground(QColor('#c62828'))
                elif reallocated > 0:
                    reallocated_item.setBackground(QColor('#fff3e0'))
                    reallocated_item.setForeground(QColor('#ef6c00'))
                table.setItem(row, 2, reallocated_item)

                # Temperature with color coding
                temp = entry.get('temperature', 0)
                temp_item = QTableWidgetItem(str(temp) if temp else '')
                if temp >= 50:
                    temp_item.setBackground(QColor('#ffebee'))
                    temp_item.setForeground(QColor('#c62828'))
                elif temp >= 40:
                    temp_item.setBackground(QColor('#fff3e0'))
                    temp_item.setForeground(QColor('#ef6c00'))
                table.setItem(row, 3, temp_item)

                power_hours_item = QTableWidgetItem(str(entry.get('power_on_hours', '')))
                table.setItem(row, 4, power_hours_item)

            layout.addWidget(table)

            # Summary statistics
            if len(history) > 1:
                summary_frame = self._create_smart_summary(history)
                layout.addWidget(summary_frame)

        else:
            # No historical data message
            no_history_label = QLabel(_("📊 No historical S.M.A.R.T. data available.\nData will be collected over time as the drive is monitored."))
            no_history_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.colors['text_secondary']};
                    font-size: 12px;
                    text-align: center;
                    padding: 20px;
                }}
            """)
            no_history_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_history_label)

        db.close()
        self.tabs.addTab(tab, _("🔧 S.M.A.R.T."))

    def _collect_smart_data(self):
        """Collect current SMART data for this drive."""
        if not self.smartctl_available:
            return
            
        from core.smart.smart_reader import get_smart_status
        smart = get_smart_status(self.drive_letter, self.smartctl_path)
        
        if smart['status'] not in [SmartStatus.NOT_SUPPORTED, SmartStatus.UNKNOWN]:
            # Save to database
            db = SmartDB(self.db_path)
            db.add_smart_entry(
                drive_id=self.drive_id,
                status=smart['status'],
                attributes=smart['attributes']
            )
            db.close()

    def _refresh_smart_tab(self, tab):
        """Refresh SMART data."""
        self._collect_smart_data()
        # Show a brief success message
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, _("SMART Data Updated"), 
                              _("SMART data has been refreshed and saved to the database."))

    def _elevate_to_admin(self):
        """Restart the application with administrator privileges."""
        from PyQt6.QtWidgets import QMessageBox
        import sys
        import os
        
        reply = QMessageBox.question(
            self, 
            _("Administrator Privileges Required"),
            _("SMART data requires administrator privileges to access physical drives.\n\n"
              "Would you like to restart the application as administrator?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                import ctypes
                import subprocess
                
                # Get the current executable path
                if getattr(sys, 'frozen', False):
                    # Running as compiled executable
                    exe_path = sys.executable
                else:
                    # Running as script
                    exe_path = sys.executable
                    script_path = os.path.abspath(sys.argv[0])
                
                # Use ShellExecute to run as administrator
                params = f'"{script_path}"' if not getattr(sys, 'frozen', False) else ''
                
                ctypes.windll.shell32.ShellExecuteW(
                    None,           # hwnd
                    "runas",        # lpOperation
                    exe_path,       # lpFile
                    params,         # lpParameters
                    None,           # lpDirectory
                    1               # nShowCmd (SW_SHOWNORMAL)
                )
                
                # Close current instance
                self.window().close()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    _("Elevation Failed"),
                    _("Failed to restart as administrator:\n\n{str(e)}")
                )

    def _create_smart_summary(self, history):
        """Create a summary of S.M.A.R.T. trends"""
        summary_frame = QFrame()
        summary_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['panel_bg']};
                border: 1px solid {self.colors['panel_border']};
                border-radius: 4px;
                padding: 2px 4px;
                min-height: 20px;
            }}
        """)

        summary_layout = QGridLayout(summary_frame)

        # Title
        summary_title = QLabel(_("📈 Trends Summary"))
        summary_title.setStyleSheet("font-size: 15px; font-weight: bold; margin-bottom: 10px;")
        summary_layout.addWidget(summary_title, 0, 0, 1, 2)

        # Calculate trends
        recent = history[0]  # Most recent
        oldest = history[-1]  # Oldest

        temp_trend = "→"
        if len(history) > 1:
            temp_change = recent.get('temperature', 0) - oldest.get('temperature', 0)
            if temp_change > 5:
                temp_trend = _("📈 Rising")
            elif temp_change < -5:
                temp_trend = _("📉 Falling")
            else:
                temp_trend = _("→ Stable")

        reallocated_trend = "→"
        if len(history) > 1:
            reallocated_change = recent.get('reallocated_sectors', 0) - oldest.get('reallocated_sectors', 0)
            if reallocated_change > 0:
                reallocated_trend = _("⚠️ Increasing")
            else:
                reallocated_trend = _("✅ Stable")

        # Summary items
        summary_layout.addWidget(QLabel(_("<b>Current Status:</b>")), 1, 0)
        summary_layout.addWidget(QLabel(recent.get('status', _('Unknown'))), 1, 1)

        summary_layout.addWidget(QLabel(_("<b>Temperature Trend:</b>")), 2, 0)
        summary_layout.addWidget(QLabel(temp_trend), 2, 1)

        summary_layout.addWidget(QLabel(_("<b>Reallocated Sectors:</b>")), 3, 0)
        summary_layout.addWidget(QLabel(reallocated_trend), 3, 1)

        summary_layout.addWidget(QLabel(_("<b>Power On Hours:</b>")), 4, 0)
        summary_layout.addWidget(QLabel(_("{hours:,} hours").format(hours=recent.get('power_on_hours', 0))), 4, 1)

        return summary_frame

    def _init_largest_files_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)

        # Title
        title = QLabel("📄 " + _("Largest Files"))
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Description
        desc = QLabel(_("Top 20 largest files on this drive by size."))
        desc.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 15px;")
        layout.addWidget(desc)

        db = DatabaseManager()
        if db.cursor:
            db.cursor.execute("""
                SELECT file_name, file_size, file_path, file_extension FROM files WHERE drive_id = ? ORDER BY file_size DESC LIMIT 20
            """, (self.drive_id,))
            files = [dict(row) for row in db.cursor.fetchall()]
        else:
            files = []

        if files:
            from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

            table = QTableWidget(len(files), 4)
            table.setHorizontalHeaderLabels([_("📄 File Name"), _("📊 Size"), _("📂 Path"), _("🏷️ Type")])

            # Style the table
            table.setAlternatingRowColors(True)
            table.setStyleSheet(f"""
                QTableWidget {{
                    gridline-color: {self.colors['panel_border']};
                    selection-background-color: {self.colors['selection']};
                    background-color: {self.colors['panel_bg']};
                    color: {self.colors['text_primary']};
                    font-size: 13px;
                    border-radius: 6px;
                    padding: 2px 4px;
                }}
                QHeaderView::section {{
                    background-color: {self.colors['button']};
                    color: {self.colors['text_primary']};
                    padding: 8px 4px;
                    border: 1px solid {self.colors['panel_border']};
                    font-weight: bold;
                    font-size: 13px;
                }}
                QTableWidget::item:selected {{
                    background: {self.colors['selection']};
                    color: {self.colors['text_primary']};
                }}
            """)

            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.verticalHeader().setVisible(False)
            table.setShowGrid(True)
            table.setContentsMargins(0, 0, 0, 0)

            for row, entry in enumerate(files):
                # File name
                file_name = entry['file_name']
                name_item = QTableWidgetItem(file_name)
                name_item.setToolTip(file_name)
                table.setItem(row, 0, name_item)

                # Size with formatting
                size_bytes = entry['file_size']
                size_str = format_file_size(size_bytes)
                size_item = QTableWidgetItem(size_str)
                size_item.setData(Qt.ItemDataRole.UserRole, size_bytes)  # For sorting
                table.setItem(row, 1, size_item)

                # Path
                path = entry['file_path']
                path_item = QTableWidgetItem(path)
                path_item.setToolTip(path)
                table.setItem(row, 2, path_item)

                # File type/extension
                extension = entry.get('file_extension', '').upper()
                if extension:
                    type_item = QTableWidgetItem(f".{extension}")
                else:
                    type_item = QTableWidgetItem("[no extension]")
                table.setItem(row, 3, type_item)

            # Enable sorting
            table.setSortingEnabled(True)

            # Add table to a frame for better separation
            table_frame = QFrame()
            table_frame.setStyleSheet(f"""
                QFrame {{
                    background: {self.colors['panel_bg']};
                    border: 1px solid {self.colors['panel_border']};
                    border-radius: 6px;
                    padding: 2px 4px;
                    margin-bottom: 2px;
                }}
            """)
            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(2, 2, 2, 2)
            table_layout.setSpacing(2)
            table_layout.addWidget(table)
            layout.addWidget(table_frame)

            # Improved summary statistics
            summary_frame = self._create_files_summary()
            layout.addWidget(summary_frame)

        else:
            no_data_label = QLabel(_("📄 No file data available for this drive."))
            no_data_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.colors['text_secondary']};
                    font-size: 14px;
                    text-align: center;
                    padding: 40px;
                }}
            """)
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_data_label)

        db.close()
        self.tabs.addTab(tab, _("📄 Largest Files"))

    def _create_files_summary(self):
        """Create a summary of file statistics for the entire drive"""
        summary_frame = QFrame()
        summary_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['panel_bg']};
                border: 1px solid {self.colors['panel_border']};
                border-radius: 8px;
                padding: 8px 8px 8px 8px;
                min-height: 40px;
                margin-top: 4px;
            }}
        """)

        summary_layout = QGridLayout(summary_frame)
        summary_layout.setContentsMargins(4, 4, 4, 4)
        summary_layout.setSpacing(6)

        # Title
        summary_title = QLabel("📊" + _("Drive File Statistics"))
        summary_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 6px;")
        summary_layout.addWidget(summary_title, 0, 0, 1, 2)

        # Query total statistics from database
        db = DatabaseManager()
        total_files = 0
        total_size = 0
        avg_file_size = 0
        largest_file = None
        most_common_ext = None

        if db.cursor:
            # Get total file count and size
            db.cursor.execute("""
                SELECT COUNT(*) as total_files, SUM(file_size) as total_size
                FROM files WHERE drive_id = ?
            """, (self.drive_id,))
            result = db.cursor.fetchone()
            if result:
                total_files = result['total_files'] or 0
                total_size = result['total_size'] or 0
                avg_file_size = total_size / total_files if total_files > 0 else 0

            # Get largest file
            db.cursor.execute("""
                SELECT file_name, file_size FROM files WHERE drive_id = ? ORDER BY file_size DESC LIMIT 1
            """, (self.drive_id,))
            largest_result = db.cursor.fetchone()
            if largest_result:
                largest_file = dict(largest_result)

            # Get most common extension
            db.cursor.execute("""
                SELECT file_extension, COUNT(*) as count
                FROM files WHERE drive_id = ?
                GROUP BY file_extension
                ORDER BY count DESC LIMIT 1
            """, (self.drive_id,))
            ext_result = db.cursor.fetchone()
            if ext_result:
                most_common_ext = (ext_result['file_extension'], ext_result['count'])

        db.close()

        # Summary items
        summary_layout.addWidget(QLabel(_("<b>Total Files:</b>")), 1, 0)
        summary_layout.addWidget(QLabel(f"{total_files:,}"), 1, 1)

        summary_layout.addWidget(QLabel(_("<b>Total Size:</b>")), 2, 0)
        summary_layout.addWidget(QLabel(format_file_size(total_size)), 2, 1)

        summary_layout.addWidget(QLabel(_("<b>Average Size:</b>")), 3, 0)
        summary_layout.addWidget(QLabel(format_file_size(avg_file_size)), 3, 1)

        if largest_file:
            summary_layout.addWidget(QLabel(_("<b>Largest File:</b>")), 4, 0)
            summary_layout.addWidget(QLabel(_("{name} ({size})").format(name=largest_file['file_name'], size=format_file_size(largest_file['file_size']))), 4, 1)

        if most_common_ext:
            ext, count = most_common_ext
            ext_display = f".{ext.upper()}" if ext else _("[no extension]")
            summary_layout.addWidget(QLabel(_("<b>Most Common Type:</b>")), 5, 0)
            summary_layout.addWidget(QLabel(_("{ext} ({count:,} files)").format(ext=ext_display, count=count)), 5, 1)

        return summary_frame

    def _init_folder_analysis_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(_("📁 Folder Analysis"))
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        # Description
        desc = QLabel(_("Detailed analysis of folder sizes and file counts."))
        desc.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 15px;")
        layout.addWidget(desc)

        # Get folder data
        db = DatabaseManager()
        folders = db.get_folders_by_drive(self.drive_id, max_level=2, limit=50)  # Limit to top 50 folders, max 2 levels deep

        if folders:
            from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

            table = QTableWidget(len(folders), 5)
            table.setHorizontalHeaderLabels([_("📁 Folder"), _("📊 Size"), _("📄 Files"), _("📂 Subfolders"), _("📈 % of Total")])

            # Style the table
            table.setAlternatingRowColors(True)
            table.setStyleSheet(f"""
                QTableWidget {{
                    gridline-color: {self.colors['panel_border']};
                    selection-background-color: {self.colors['selection']};
                    background-color: {self.colors['panel_bg']};
                    color: {self.colors['text_primary']};
                }}
                QHeaderView::section {{
                    background-color: {self.colors['button']};
                    color: {self.colors['text_primary']};
                    padding: 8px;
                    border: 1px solid {self.colors['panel_border']};
                    font-weight: bold;
                }}
            """)

            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            # Calculate total size for percentages
            total_size = sum(folder.get('total_size', 0) for folder in folders)

            for row, folder in enumerate(folders):
                # Folder path
                folder_path = folder.get('folder_path', '') + folder.get('folder_name', '')
                path_item = QTableWidgetItem(folder_path)
                table.setItem(row, 0, path_item)

                # Size with formatting
                size_bytes = folder.get('total_size', 0)
                size_str = format_file_size(size_bytes)
                size_item = QTableWidgetItem(size_str)
                size_item.setData(Qt.ItemDataRole.UserRole, size_bytes)  # For sorting
                table.setItem(row, 1, size_item)

                # File count
                file_count = folder.get('file_count', 0)
                file_item = QTableWidgetItem(f"{file_count:,}")
                file_item.setData(Qt.ItemDataRole.UserRole, file_count)  # For sorting
                table.setItem(row, 2, file_item)

                # Subfolder count
                subfolder_count = folder.get('subfolder_count', 0)
                subfolder_item = QTableWidgetItem(f"{subfolder_count:,}")
                subfolder_item.setData(Qt.ItemDataRole.UserRole, subfolder_count)  # For sorting
                table.setItem(row, 3, subfolder_item)

                # Percentage
                if total_size > 0:
                    percentage = (size_bytes / total_size) * 100
                    percentage_item = QTableWidgetItem(f"{percentage:.1f}%")
                    percentage_item.setData(Qt.ItemDataRole.UserRole, percentage)  # For sorting
                else:
                    percentage_item = QTableWidgetItem("0.0%")
                    percentage_item.setData(Qt.ItemDataRole.UserRole, 0.0)
                table.setItem(row, 4, percentage_item)

            # Enable sorting
            table.setSortingEnabled(True)

            layout.addWidget(table)

            # Summary statistics
            summary_frame = self._create_folder_summary()
            layout.addWidget(summary_frame)

        else:
            no_data_label = QLabel(_("📁 No folder data available for this drive."))
            no_data_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.colors['text_secondary']};
                    font-size: 14px;
                    text-align: center;
                    padding: 40px;
                }}
            """)
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_data_label)

        db.close()
        self.tabs.addTab(tab, _("📁 Folders"))

    def _create_folder_summary(self):
        """Create a summary of folder statistics for the entire drive"""
        summary_frame = QFrame()
        summary_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['panel_bg']};
                border: 1px solid {self.colors['panel_border']};
                border-radius: 12px;
                padding: 24px 20px 24px 20px;
                min-height: 70px;
            }}
        """)

        summary_layout = QGridLayout(summary_frame)

        # Title
        summary_title = QLabel(_("📊 Drive Folder Statistics"))
        summary_title.setStyleSheet("font-size: 15px; font-weight: bold; margin-bottom: 10px;")
        summary_layout.addWidget(summary_title, 0, 0, 1, 2)

        # Query total statistics from database
        db = DatabaseManager()
        total_folders = 0
        total_files_in_folders = 0
        total_subfolders = 0
        total_size = 0
        avg_folder_size = 0
        largest_folder = None

        if db.cursor:
            # Get total folder count and aggregated stats
            db.cursor.execute("""
                SELECT COUNT(*) as total_folders,
                       SUM(file_count) as total_files,
                       SUM(subfolder_count) as total_subfolders,
                       SUM(total_size) as total_size
                FROM folders WHERE drive_id = ?
            """, (self.drive_id,))
            result = db.cursor.fetchone()
            if result:
                total_folders = result['total_folders'] or 0
                total_files_in_folders = result['total_files'] or 0
                total_subfolders = result['total_subfolders'] or 0
                total_size = result['total_size'] or 0
                avg_folder_size = total_size / total_folders if total_folders > 0 else 0

            # Get largest folder
            db.cursor.execute("""
                SELECT folder_path, folder_name, total_size FROM folders WHERE drive_id = ? ORDER BY total_size DESC LIMIT 1
            """, (self.drive_id,))
            largest_result = db.cursor.fetchone()
            if largest_result:
                largest_folder = dict(largest_result)

        db.close()

        # Summary items
        summary_layout.addWidget(QLabel(_("<b>Total Folders:</b>")), 1, 0)
        summary_layout.addWidget(QLabel(_("{count:,}").format(count=total_folders)), 1, 1)

        summary_layout.addWidget(QLabel(_("<b>Total Files in Folders:</b>")), 2, 0)
        summary_layout.addWidget(QLabel(_("{count:,}").format(count=total_files_in_folders)), 2, 1)

        summary_layout.addWidget(QLabel(_("<b>Total Subfolders:</b>")), 3, 0)
        summary_layout.addWidget(QLabel(_("{count:,}").format(count=total_subfolders)), 3, 1)

        summary_layout.addWidget(QLabel(_("<b>Average Folder Size:</b>")), 4, 0)
        summary_layout.addWidget(QLabel(format_file_size(avg_folder_size)), 4, 1)

        if largest_folder:
            folder_path = largest_folder.get('folder_path', '') + largest_folder.get('folder_name', '')
            summary_layout.addWidget(QLabel(_("<b>Largest Folder:</b>")), 5, 0)
            summary_layout.addWidget(QLabel(_("{path} ({size})").format(path=folder_path, size=format_file_size(largest_folder.get('total_size', 0)))), 5, 1)

        return summary_frame
