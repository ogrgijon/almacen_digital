# Sistema de Internacionalización (i18n)

Almacén Digital ahora incluye soporte completo para múltiples idiomas usando archivos .po de gettext.

## Idiomas Disponibles

- **Español (es)** - Idioma por defecto
- **English (en)** - Inglés

## Cambiar el Idioma

1. Abre la aplicación
2. Ve a **Configuración** (icono de engranaje en la barra superior)
3. Selecciona la pestaña **🌐 Idioma**
4. Elige tu idioma preferido del menú desplegable
5. Haz clic en **Guardar**
6. **Reinicia la aplicación** para que los cambios surtan efecto

## Estructura de Archivos

```
locales/
├── es/
│   └── LC_MESSAGES/
│       ├── almacen.po    # Traducciones en español (editable)
│       └── almacen.mo    # Compilado (generado automáticamente)
└── en/
    └── LC_MESSAGES/
        ├── almacen.po    # Traducciones en inglés (editable)
        └── almacen.mo    # Compilado (generado automáticamente)
```

## Para Desarrolladores

### Agregar Nuevas Traducciones

1. Edita los archivos `.po` en `locales/[idioma]/LC_MESSAGES/almacen.po`
2. Agrega nuevas entradas siguiendo este formato:

```po
msgid "Original text in code"
msgstr "Texto traducido"
```

3. Compila las traducciones ejecutando:

```bash
python compile_translations.py
```

### Usar Traducciones en el Código

```python
from i18n import _

# Traducir un texto
translated_text = _("Text to translate")

# O usar directamente en PyQt
label = QLabel(_("Hello World"))
```

### Agregar un Nuevo Idioma

1. Crea una nueva carpeta en `locales/` con el código del idioma (ej: `fr` para francés)
2. Crea la subcarpeta `LC_MESSAGES`
3. Copia `locales/en/LC_MESSAGES/almacen.po` a la nueva carpeta
4. Traduce todos los `msgstr` al nuevo idioma
5. Ejecuta `python compile_translations.py`
6. Actualiza `i18n.py` para incluir el nuevo idioma en `get_available_languages()`
7. Actualiza `ui/settings_dialog.py` para agregar el nuevo idioma al combo box

## Archivos Principales

- **`i18n.py`** - Módulo principal de internacionalización
- **`compile_translations.py`** - Script para compilar archivos .po a .mo
- **`locales/`** - Directorio con todas las traducciones
- **`config.py`** - Incluye la configuración `LANGUAGE`
- **`utils/settings.py`** - Maneja la persistencia del idioma seleccionado
- **`ui/settings_dialog.py`** - Interfaz para cambiar el idioma

## Notas Técnicas

- El sistema usa **gettext** de Python para manejar las traducciones
- Los archivos `.mo` son binarios y deben recompilarse después de editar los `.po`
- El cambio de idioma requiere reiniciar la aplicación
- El idioma seleccionado se guarda en `data/settings.json`
- Por defecto, la aplicación inicia en español

## Troubleshooting

### Las traducciones no se aplican

1. Verifica que los archivos `.mo` existan en `locales/[idioma]/LC_MESSAGES/`
2. Ejecuta `python compile_translations.py` para recompilarlos
3. Reinicia la aplicación

### El idioma no cambia después de guardarlo

- **Importante:** Debes reiniciar completamente la aplicación para que el cambio de idioma surta efecto

### Error al compilar traducciones

Asegúrate de tener instalado `polib`:

```bash
pip install polib
```
