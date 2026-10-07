# Internationalization System (i18n)

Almacén Digital now includes full support for multiple languages using gettext .po files.

## Available Languages

- **Spanish (es)** - Default language
- **English (en)** - English

## Changing the Language

1. Open the application
2. Go to **Settings** (gear icon in the top bar)
3. Select the **🌐 Language** tab
4. Choose your preferred language from the dropdown menu
5. Click **Save**
6. **Restart the application** for changes to take effect

## File Structure

```
locales/
├── es/
│   └── LC_MESSAGES/
│       ├── almacen.po    # Spanish translations (editable)
│       └── almacen.mo    # Compiled (generated automatically)
└── en/
    └── LC_MESSAGES/
        ├── almacen.po    # English translations (editable)
        └── almacen.mo    # Compiled (generated automatically)
```

## For Developers

### Adding New Translations

1. Edit the `.po` files in `locales/[language]/LC_MESSAGES/almacen.po`
2. Add new entries following this format:

```po
msgid "Original text in code"
msgstr "Translated text"
```

3. Compile the translations by running:

```bash
python compile_translations.py
```

### Using Translations in Code

```python
from i18n import _

# Translate a text
translated_text = _("Text to translate")

# Or use directly in PyQt
label = QLabel(_("Hello World"))
```

### Adding a New Language

1. Create a new folder in `locales/` with the language code (e.g., `fr` for French)
2. Create the `LC_MESSAGES` subfolder
3. Copy `locales/en/LC_MESSAGES/almacen.po` to the new folder
4. Translate all `msgstr` entries to the new language
5. Run `python compile_translations.py`
6. Update `i18n.py` to include the new language in `get_available_languages()`
7. Update `ui/settings_dialog.py` to add the new language to the combo box

## Main Files

- **`i18n.py`** - Main internationalization module
- **`compile_translations.py`** - Script to compile .po files to .mo
- **`locales/`** - Directory with all translations
- **`config.py`** - Includes the `LANGUAGE` configuration
- **`utils/settings.py`** - Handles persistence of selected language
- **`ui/settings_dialog.py`** - Interface for changing language

## Technical Notes

- The system uses Python's **gettext** to handle translations
- `.mo` files are binary and must be recompiled after editing `.po` files
- Language change requires application restart
- Selected language is saved in `data/settings.json`
- By default, the application starts in Spanish

## Troubleshooting

### Translations are not applied

1. Verify that `.mo` files exist in `locales/[language]/LC_MESSAGES/`
2. Run `python compile_translations.py` to recompile them
3. Restart the application

### Language doesn't change after saving

- **Important:** You must completely restart the application for the language change to take effect

### Error compiling translations

Make sure `polib` is installed:

```bash
pip install polib
```</content>
<parameter name="filePath">c:\DOCS\PROYECTOS\HDDINVENTORY\docs\en\I18N_GUIDE.md