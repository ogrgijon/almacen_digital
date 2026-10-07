# --- Comentarios de desarrollo ---
# Este archivo implementa la barra lateral izquierda de la aplicación HDDInventory.
# Muestra las colecciones, unidades y filtros rápidos.
# Utiliza PyQt6 para la interfaz gráfica.
# Señales principales: drive_selected, collection_selected, quick_filter_selected.
# Métodos clave: init_ui, create_drives_section, create_recent_section, create_quick_filters_section, load_drives.
# Para mantenimiento:
# - Actualizar los textos y filtros según la evolución de la UI.
# - Mantener la compatibilidad con main_window.py y otros módulos que usen la barra lateral.
# - Revisar la estructura de los árboles y la gestión de señales al modificar la lógica.
# - Los nombres de métodos y clases se mantienen en inglés para compatibilidad global.
#
# Traducido y comentado para facilitar el desarrollo y mantenimiento.
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTreeWidget, 
							  QTreeWidgetItem, QPushButton, QHBoxLayout,
							  QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QColor
import config
from utils.helpers import format_file_size
from i18n import _


def create_left_sidebar() -> QWidget:
		# Devuelve la instancia principal de la barra lateral izquierda.
	# For compatibility with refactored main_window.py
	return CollectionsSidebar()


class CollectionsSidebar(QWidget):
		# Clase principal de la barra lateral izquierda.
		# Gestiona la visualización de colecciones, unidades y filtros rápidos.
	"""Left sidebar showing collections and drives"""
	drive_selected = pyqtSignal(int)  # drive_id
	collection_selected = pyqtSignal(str)  # collection name
	quick_filter_selected = pyqtSignal(str)  # filter type

	def __init__(self):
			# Inicializa la barra lateral y construye la interfaz.
		super().__init__()
		self.init_ui()

	def init_ui(self):
			# Construye la interfaz gráfica y organiza los bloques principales.
		layout = QVBoxLayout(self)
		layout.setContentsMargins(5, 5, 5, 5)
		layout.setSpacing(10)
		header = QLabel(_("🗂️ Storage"))
		header.setObjectName('sectionHeader')
		header.setAlignment(Qt.AlignmentFlag.AlignCenter)
		layout.addWidget(header)
		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		scroll.setFrameShape(QFrame.Shape.NoFrame)
		scroll_content = QWidget()
		scroll_layout = QVBoxLayout(scroll_content)
		scroll_layout.setContentsMargins(0, 0, 0, 0)
		scroll_layout.setSpacing(15)
		self.drives_tree = self.create_drives_section()
		# Habilitar menú contextual para unidades
		self.drives_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.drives_tree.customContextMenuRequested.connect(self.show_drive_context_menu)
		scroll_layout.addWidget(self.drives_tree)
		self.recent_tree = self.create_recent_section()
		scroll_layout.addWidget(self.recent_tree)
		self.filters_tree = self.create_quick_filters_section()
		scroll_layout.addWidget(self.filters_tree)
		scroll_layout.addStretch()
		scroll.setWidget(scroll_content)
		layout.addWidget(scroll)

		# Activar el filtro por defecto 'Root Folder'
		root = self.filters_tree.topLevelItem(0)
		if root:
			for i in range(root.childCount()):
				item = root.child(i)
				if item is not None and item.text(0) == _("🔌 USB Root Folder"):
					self.filters_tree.setCurrentItem(item)
					if item is not None:
						self.on_filter_item_clicked(item, 0)
					break

    
	def create_drives_section(self) -> QTreeWidget:
			# Crea el árbol de unidades registradas.
		"""Create All Drives tree widget"""
		tree = QTreeWidget()
		tree.setHeaderHidden(True)
		tree.setIndentation(15)
		tree.setStyleSheet(f"""
			QTreeWidget {{
				background-color: {config.COLORS['panel_bg']};
				border: 1px solid {config.COLORS['panel_border']};
				border-radius: 3px;
			}}
		""")
        
		# Root item
		root = QTreeWidgetItem(tree, [_("▼ Registered Drives")])
		root.setExpanded(True)
		font = root.font(0)
		font.setBold(True)
		root.setFont(0, font)
        
		tree.itemClicked.connect(self.on_tree_item_clicked)
        
		return tree
    
	def create_recent_section(self) -> QTreeWidget:
			# Crea el árbol de escaneos recientes.
		"""Create Recent Scans tree widget"""
		tree = QTreeWidget()
		tree.setHeaderHidden(True)
		tree.setIndentation(15)
		tree.setStyleSheet(f"""
			QTreeWidget {{
				background-color: {config.COLORS['panel_bg']};
				border: 1px solid {config.COLORS['panel_border']};
				border-radius: 3px;
			}}
		""")
        
		# Root item
		root = QTreeWidgetItem(tree, [_("▼ Recent Scans")])
		root.setExpanded(True)
		font = root.font(0)
		font.setBold(True)
		root.setFont(0, font)
        
		# Add recent items
		QTreeWidgetItem(root, [_("├─ Today")])
		QTreeWidgetItem(root, [_("├─ This week")])
		QTreeWidgetItem(root, [_("└─ This month")])
        
		tree.itemClicked.connect(self.on_recent_item_clicked)
        
		return tree
    
	def create_quick_filters_section(self) -> QTreeWidget:
			# Crea el árbol de filtros rápidos.
		"""Create Quick Filters tree widget"""
		tree = QTreeWidget()
		tree.setHeaderHidden(True)
		tree.setIndentation(15)
		tree.setStyleSheet(f"""
			QTreeWidget {{
				background-color: {config.COLORS['panel_bg']};
				border: 1px solid {config.COLORS['panel_border']};
				border-radius: 3px;
			}}
		""")
        
		# Root item
		root = QTreeWidgetItem(tree, [_("▼ Quick Filters")])
		root.setExpanded(True)
		font = root.font(0)
		font.setBold(True)
		root.setFont(0, font)
        
		# Add filter items with icons
		QTreeWidgetItem(root, [_("🔌 USB Root Folder")])
		QTreeWidgetItem(root, [_("📁 Folders")])
		QTreeWidgetItem(root, [_("📄 Documents")])
		QTreeWidgetItem(root, [_("🖼️ Images")])
		QTreeWidgetItem(root, [_("🎵 Audio")])
		QTreeWidgetItem(root, [_("🎬 Videos")])
		QTreeWidgetItem(root, [_("📦 Compressed")])
		QTreeWidgetItem(root, [_("🔷 Large Files")])
        
		tree.itemClicked.connect(self.on_filter_item_clicked)
        
		return tree
    
	def load_drives(self, drives: list):
			# Carga las unidades en el árbol de unidades.
		"""Load drives into the tree. Safe against missing drives_tree."""
		if not hasattr(self, 'drives_tree') or self.drives_tree is None:
			import logging
			logging.warning("CollectionsSidebar: drives_tree not initialized.")
			return
		root = self.drives_tree.topLevelItem(0)
		if root is None:
			import logging
			logging.warning("CollectionsSidebar: drives_tree root not found.")
			return
		while root.childCount() > 0:
			root.removeChild(root.child(0))
		self._last_loaded_drives = drives  # Guardar referencia para el menú contextual
		for drive in drives:
			drive_label = drive.get('drive_label', _("Unknown"))
			file_count = drive.get('file_count', 0)
			capacity = drive.get('capacity_bytes', 0)
			item_text = f"💾 {drive_label}"
			item = QTreeWidgetItem(root, [item_text])
			item.setData(0, Qt.ItemDataRole.UserRole, drive['id'])
			if 'drive_letter' in drive:
				item.setData(0, Qt.ItemDataRole.UserRole + 1, drive['drive_letter'])
			texto_info = f"   {file_count:,} {_('files')} | {format_file_size(capacity)}"
			info_item = QTreeWidgetItem(item, [texto_info])
			info_item.setForeground(0, QColor(config.COLORS['text_secondary']))
		root.setExpanded(True)
    
	def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
			# Maneja el clic en una unidad y emite la señal correspondiente.
		"""Handle drive item click"""
		drive_id = item.data(0, Qt.ItemDataRole.UserRole)
		if drive_id:
			self.drive_selected.emit(drive_id)
    
	def on_recent_item_clicked(self, item: QTreeWidgetItem, column: int):
			# Maneja el clic en un elemento reciente y emite la señal correspondiente.
		"""Handle recent item click"""
		text = item.text(0)
		if _("Today") in text:
			self.collection_selected.emit('hoy')
		elif _("This week") in text:
			self.collection_selected.emit('esta_semana')
		elif _("This month") in text:
			self.collection_selected.emit('este_mes')
    
	def on_filter_item_clicked(self, item: QTreeWidgetItem, column: int):
			# Maneja el clic en un filtro rápido y emite la señal correspondiente.
		"""Handle quick filter click"""
		text = item.text(0)
        
		filter_map = {
			_("🔌 USB Root Folder"): 'root_folders',
			_("📁 Folders"): 'folders',
			_("📄 Documents"): 'documentos',
			_("🖼️ Images"): 'imagenes',
			_("🎵 Audio"): 'audio',
			_("🎬 Videos"): 'videos',
			_("📦 Compressed"): 'comprimidos',
			_("🔷 Large Files"): 'archivos_grandes'
		}
		filter_type = filter_map.get(text)
		if filter_type:
			self.quick_filter_selected.emit(filter_type)
    
	def show_drive_context_menu(self, pos):
		# Muestra un menú contextual al hacer clic derecho sobre una unidad conectada
		item = self.drives_tree.itemAt(pos)
		if not item or not item.parent():
			return
		drive_id = item.data(0, Qt.ItemDataRole.UserRole)
		if not drive_id:
			return
		from PyQt6.QtWidgets import QMenu, QMessageBox
		menu = QMenu(self)
		action_explorer = menu.addAction(_("View in File Explorer"))
		viewport = self.drives_tree.viewport() if self.drives_tree else None
		global_pos = viewport.mapToGlobal(pos) if viewport is not None else pos
		action = menu.exec(global_pos)
		if action == action_explorer:
			# Emitir señal o abrir el explorador
			# Aquí se asume que el objeto drive tiene la letra de unidad
			# Buscar la letra de la unidad a partir del drive_id
			drive = self.find_drive_by_id(drive_id)
			if drive and 'drive_letter' in drive:
				import os
				import subprocess
				path = f"{drive['drive_letter']}\\"
				try:
					os.startfile(path)
				except Exception as e:
					QMessageBox.warning(self, _("Error"), f"{_('Could not open explorer')}: {e}")
			else:
				QMessageBox.warning(self, _("Error"), _("Could not determine drive letter."))

	def find_drive_by_id(self, drive_id):
		# Buscar la unidad en el árbol por id y devolver el dict asociado si está disponible
		# Este método debe ser adaptado según cómo se almacenen los datos de unidades en la app
		# Aquí se asume que se guarda una lista self._last_loaded_drives
		if hasattr(self, '_last_loaded_drives'):
			for d in self._last_loaded_drives:
				if d.get('id') == drive_id:
					return d
		return None
