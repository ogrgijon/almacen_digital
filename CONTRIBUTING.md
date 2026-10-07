# Contributing to Almacén Digital / Contribuir a Almacén Digital

> **🇪🇸 [Versión en Español](#español) | 🇺🇸 [English Version](#english)**

---

## English

Thank you for your interest in contributing to Almacén Digital! This document provides guidelines and instructions for contributing.

### Code of Conduct

#### Our Pledge

We are committed to providing a friendly, safe, and welcoming environment for all contributors.

#### Expected Behavior

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the project
- Show empathy towards other contributors

#### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling or insulting remarks
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

### How to Contribute

#### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**Good Bug Reports Include:**
- Clear, descriptive title
- Steps to reproduce the problem
- Expected vs. actual behavior
- Screenshots (if applicable)
- System information (OS, Python version)
- Log files (`data/app.log`)

#### Suggesting Features

Feature suggestions are welcome! Please:
- Use a clear, descriptive title
- Explain the use case and benefits
- Provide examples or mockups if possible
- Consider implementation complexity

#### Pull Requests

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/almacen_digital.git
   cd almacen_digital
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow the code style guidelines
   - Add tests for new features
   - Update documentation
   - Test thoroughly

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

5. **Push to GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Provide clear description of changes
   - Reference related issues
   - Include screenshots for UI changes

### Development Setup

```bash
# Clone repository
git clone https://github.com/ogrgijon/almacen_digital.git
cd almacen_digital

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Unix:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise
- Write clear comments for complex logic

### Testing

```bash
# Run tests (when available)
python -m pytest tests/

# Test with dummy data
python scripts/populate_dummy_data.py
```

### Documentation

- Update relevant documentation files
- Add comments to complex code
- Update CHANGELOG.md for significant changes
- Include examples where appropriate

### Commit Messages

Use clear and descriptive commit messages:

```
Add feature: brief description

Detailed explanation of what was added and why.

Fixes #123
```

### Questions?

Feel free to:
- Open an issue for questions
- Contact via [GitHub Issues](https://github.com/ogrgijon/almacen_digital/issues)
- Reach out on [LinkedIn](https://www.linkedin.com/in/ogrgijon)

---

## Español

¡Gracias por tu interés en contribuir a Almacén Digital! Este documento proporciona pautas e instrucciones para contribuir.

### Código de Conducta

#### Nuestro Compromiso

Estamos comprometidos a proporcionar un entorno amigable, seguro y acogedor para todos los colaboradores.

#### Comportamiento Esperado

- Ser respetuoso e inclusivo
- Aceptar críticas constructivas con gracia
- Enfocarse en lo mejor para el proyecto
- Mostrar empatía hacia otros colaboradores

#### Comportamiento Inaceptable

- Acoso, discriminación o comentarios ofensivos
- Trolling o comentarios insultantes
- Publicar información privada de otros
- Cualquier conducta inapropiada en un entorno profesional

### Cómo Contribuir

#### Reportar Errores

Antes de crear reportes de errores, por favor verifica los issues existentes para evitar duplicados.

**Los Buenos Reportes de Errores Incluyen:**
- Título claro y descriptivo
- Pasos para reproducir el problema
- Comportamiento esperado vs. real
- Capturas de pantalla (si aplica)
- Información del sistema (SO, versión de Python)
- Archivos de log (`data/app.log`)

#### Sugerir Funcionalidades

¡Las sugerencias de funcionalidades son bienvenidas! Por favor:
- Usa un título claro y descriptivo
- Explica el caso de uso y beneficios
- Proporciona ejemplos o bocetos si es posible
- Considera la complejidad de implementación

#### Pull Requests

1. **Fork del Repositorio**
   ```bash
   git clone https://github.com/tuusuario/almacen_digital.git
   cd almacen_digital
   ```

2. **Crear una Rama**
   ```bash
   git checkout -b feature/nombre-de-tu-funcionalidad
   ```

3. **Hacer Cambios**
   - Sigue las pautas de estilo de código
   - Añade pruebas para nuevas funcionalidades
   - Actualiza la documentación
   - Prueba exhaustivamente

4. **Commit de Cambios**
   ```bash
   git add .
   git commit -m "Añade funcionalidad: descripción breve"
   ```

5. **Push a GitHub**
   ```bash
   git push origin feature/nombre-de-tu-funcionalidad
   ```

6. **Crear Pull Request**
   - Proporciona descripción clara de los cambios
   - Referencia issues relacionados
   - Incluye capturas de pantalla para cambios de UI

### Configuración de Desarrollo

```bash
# Clonar repositorio
git clone https://github.com/ogrgijon/almacen_digital.git
cd almacen_digital

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Unix:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

### Estilo de Código

- Sigue las pautas PEP 8
- Usa nombres significativos para variables y funciones
- Añade docstrings a funciones y clases
- Mantén las funciones enfocadas y concisas
- Escribe comentarios claros para lógica compleja

### Pruebas

```bash
# Ejecutar pruebas (cuando estén disponibles)
python -m pytest tests/

# Probar con datos de ejemplo
python scripts/populate_dummy_data.py
```

### Documentación

- Actualiza archivos de documentación relevantes
- Añade comentarios a código complejo
- Actualiza CHANGELOG.md para cambios significativos
- Incluye ejemplos donde sea apropiado

### Mensajes de Commit

Usa mensajes de commit claros y descriptivos:

```
Añade funcionalidad: descripción breve

Explicación detallada de qué se añadió y por qué.

Resuelve #123
```

### ¿Preguntas?

Siéntete libre de:
- Abrir un issue para preguntas
- Contactar vía [GitHub Issues](https://github.com/ogrgijon/almacen_digital/issues)
- Contactar en [LinkedIn](https://www.linkedin.com/in/ogrgijon)

---

**Thank you for contributing! / ¡Gracias por contribuir!**
