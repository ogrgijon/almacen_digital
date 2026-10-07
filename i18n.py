"""
Módulo de internacionalización para Almacén Digital.
Gestiona la carga y cambio de idiomas usando gettext.
"""

import gettext
import locale
from pathlib import Path
from typing import Callable

# Dominio de traducción
DOMAIN = 'almacen'

# Directorio de locales
LOCALE_DIR = Path(__file__).parent / 'locales'

# Idioma actual
_current_language = 'es'

# Traductor actual
_translator = None


def get_available_languages():
    """Retorna lista de idiomas disponibles"""
    return {
        'es': 'Español',
        'en': 'English'
    }


def set_language(lang_code: str) -> bool:
    """
    Establece el idioma de la aplicación.
    
    Args:
        lang_code: Código de idioma ('es' o 'en')
        
    Returns:
        True si el idioma se estableció correctamente
    """
    global _current_language, _translator
    
    try:
        if lang_code not in get_available_languages():
            lang_code = 'es'  # Fallback a español
        
        _current_language = lang_code
        
        # Cargar traductor
        _translator = gettext.translation(
            DOMAIN,
            localedir=LOCALE_DIR,
            languages=[lang_code],
            fallback=True
        )
        
        # Instalar globalmente
        _translator.install()
        
        return True
    except Exception as e:
        print(f"Error setting language to {lang_code}: {e}")
        # Fallback a gettext sin traducción
        _translator = gettext.NullTranslations()
        _translator.install()
        return False


def get_current_language() -> str:
    """Retorna el código del idioma actual"""
    return _current_language


def translate(message: str) -> str:
    """
    Traduce un mensaje.
    
    Args:
        message: Mensaje a traducir
        
    Returns:
        Mensaje traducido
    """
    if _translator is None:
        return message
    return _translator.gettext(message)


def translate_plural(singular: str, plural: str, n: int) -> str:
    """
    Traduce un mensaje con plural.
    
    Args:
        singular: Forma singular
        plural: Forma plural
        n: Cantidad
        
    Returns:
        Mensaje traducido en forma correcta
    """
    if _translator is None:
        return singular if n == 1 else plural
    return _translator.ngettext(singular, plural, n)


# Alias corto para traducción
_ = translate

# Inicializar con idioma por defecto
set_language('es')
