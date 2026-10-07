"""
Utilidades para gestionar la configuración de la aplicación.
"""

import json
import logging
from pathlib import Path
import config


def load_sync_settings():
    """
    Carga la configuración de sincronización desde el archivo de settings.
    También carga otras configuraciones de la aplicación.
    """
    try:
        if not config.SETTINGS_PATH.exists():
            return
        
        with open(config.SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
        
        # Sync settings
        if 'sync' in settings:
            sync_settings = settings['sync']
            config.SYNC_ENABLED = sync_settings.get('enabled', False)
            config.SYNC_BACKUP_PATH = sync_settings.get('backup_path', None)
            config.SYNC_DIRECTION = sync_settings.get('direction', 'bidirectional')
            config.SYNC_ON_STARTUP = sync_settings.get('on_startup', True)
            config.SYNC_ON_SHUTDOWN = sync_settings.get('on_shutdown', True)
            
            logging.info(f"Loaded sync settings: enabled={config.SYNC_ENABLED}")
        
        # UI settings
        if 'ui' in settings:
            ui_settings = settings['ui']
            config.WINDOW_DEFAULT_WIDTH = ui_settings.get('window_width', config.WINDOW_DEFAULT_WIDTH)
            config.WINDOW_DEFAULT_HEIGHT = ui_settings.get('window_height', config.WINDOW_DEFAULT_HEIGHT)
            
            logging.info(f"Loaded UI settings: {config.WINDOW_DEFAULT_WIDTH}x{config.WINDOW_DEFAULT_HEIGHT}")
        
        # Scan settings
        if 'scan' in settings:
            scan_settings = settings['scan']
            config.DEFAULT_SCAN_DEPTH = scan_settings.get('default_depth', config.DEFAULT_SCAN_DEPTH)
            config.EXCLUDED_FOLDERS = scan_settings.get('excluded_folders', config.EXCLUDED_FOLDERS)
            
            logging.info(f"Loaded scan settings: depth={config.DEFAULT_SCAN_DEPTH}")
        
        # Search settings
        if 'search' in settings:
            search_settings = settings['search']
            config.SEARCH_DEBOUNCE_MS = search_settings.get('debounce_ms', config.SEARCH_DEBOUNCE_MS)
            config.MAX_SEARCH_RESULTS = search_settings.get('max_results', config.MAX_SEARCH_RESULTS)
            
            logging.info(f"Loaded search settings: max_results={config.MAX_SEARCH_RESULTS}")        
        
        # Language settings
        if 'language' in settings:
            config.LANGUAGE = settings.get('language', config.LANGUAGE)
            logging.info(f"Loaded language setting: {config.LANGUAGE}")
        
        # Legal settings
        if 'legal' in settings:
            legal_settings = settings['legal']
            config.FIRST_RUN_ACKNOWLEDGED = legal_settings.get('first_run_acknowledged', False)
            
            logging.info(f"Loaded legal settings: first_run_acknowledged={config.FIRST_RUN_ACKNOWLEDGED}")    
    except Exception as e:
        logging.error(f"Error loading settings: {e}")


def save_sync_settings():
    """
    Guarda la configuración de sincronización en el archivo de settings.
    """
    try:
        settings = {}
        if config.SETTINGS_PATH.exists():
            with open(config.SETTINGS_PATH, 'r') as f:
                settings = json.load(f)
        
        settings['sync'] = {
            'enabled': config.SYNC_ENABLED,
            'backup_path': config.SYNC_BACKUP_PATH,
            'direction': config.SYNC_DIRECTION,
            'on_startup': config.SYNC_ON_STARTUP,
            'on_shutdown': config.SYNC_ON_SHUTDOWN
        }
        
        with open(config.SETTINGS_PATH, 'w') as f:
            json.dump(settings, f, indent=2)
        
        logging.info("Saved sync settings")
    
    except Exception as e:
        logging.error(f"Error saving sync settings: {e}")


def save_legal_settings():
    """
    Guarda la configuración legal (aviso de primera ejecución).
    """
    try:
        settings = {}
        if config.SETTINGS_PATH.exists():
            with open(config.SETTINGS_PATH, 'r') as f:
                settings = json.load(f)
        
        # Legal settings
        settings['legal'] = {
            'first_run_acknowledged': config.FIRST_RUN_ACKNOWLEDGED
        }
        
        with open(config.SETTINGS_PATH, 'w') as f:
            json.dump(settings, f, indent=2)
        
        logging.info("Saved legal settings")
    
    except Exception as e:
        logging.error(f"Error saving legal settings: {e}")
