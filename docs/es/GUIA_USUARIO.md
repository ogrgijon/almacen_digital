# Almacén Digital - Guía del Usuario

## Información General
Almacen Digital es una aplicación profesional para inventariar discos externos con una interfaz de tema oscuro. Te permite escanear, catalogar y buscar archivos en todos tus discos externos (HDDs, pendrives USB, etc.).

## Características

### ✨ Características Principales
- **Escaneo manual de discos** - Tú eliges qué discos escanear
- **Base de datos SQLite** - Base de datos local rápida y searchable
- **Búsqueda y filtrado avanzados** - Encuentra archivos rápidamente con múltiples filtros
- **Importación/exportación Excel** - Comparte y respalda tu inventario
- **Sincronización de metadatos XML** - Rastrea cambios entre escaneos
- **Tema oscuro profesional** - Interfaz moderna
- **Múltiples modos de vista** - Vistas de tabla, cuadrícula y árbol

## Primeros Pasos

### Instalación
1. Instala Python 3.10 o superior
2. Ejecuta `install.bat` o manualmente: `pip install -r requirements.txt`
3. Ejecuta `run.bat` o manualmente: `python main.py`

## Interfaz de Usuario

### Diseño General
La interfaz consta de cuatro áreas principales:

```
┌──────────────────────────────────────────────────┐
│  📋 Inventario | 🔍 Búsqueda | 💾 Gestionar | 📊 Estadísticas │  ← Selector de Modo
├─────────┬───────────────────────────┬────────────┤
│         │                           │            │
│  PANEL  │        CONTENIDO          │   PANEL    │
│ IZQUIERDO│        PRINCIPAL         │ DERECHO    │
│         │                           │            │
│Colecciones     Vista de Resultados  Filtros      │
│         │                           │            │
└─────────┴───────────────────────────┴────────────┘
│  Estado: 1,234 archivos | 3 discos | 25 GB      │  ← Barra de Estado
└──────────────────────────────────────────────────┘
```

### Modos

#### 📋 Modo Inventario (Predeterminado)
Navega todos los archivos indexados en una vista de tabla con detalles completos.

**Características:**
- Barra de búsqueda rápida en la parte superior
- Columnas ordenables (Nombre, Tamaño, Tipo, Fecha, Disco)
- Selector de vista: Tabla (≡), Cuadrícula (⊞), Árbol (⋮)
- Íconos de archivos y detalles

**Uso:**
1. Usa la búsqueda rápida para encontrar archivos por nombre
2. Haz clic en los encabezados de columna para ordenar
3. Selecciona archivos para ver detalles
4. Cambia entre modos de vista

#### 🔍 Modo Búsqueda
Búsqueda avanzada con múltiples filtros (actualmente usa la misma vista que Inventario).

**Nota:** Los filtros de búsqueda avanzada están integrados en el panel derecho en el modo Inventario.

#### 💾 Modo Gestionar
Agrega, escanea y administra tus discos.

**Características:**
- Agregar nuevos discos al inventario
- Escanear/rescanean discos
- Exportar datos de discos a Excel
- Remover discos del inventario
- Ver estadísticas de discos

**Agregar un Disco:**
1. Haz clic en "💾 Gestionar" en la barra superior
2. Haz clic en "+ Agregar Nuevo Disco"
3. Selecciona disco del menú desplegable
4. Ingresa nombre descriptivo (opcional)
5. Haz clic en "Iniciar Escaneo"
6. Espera a que se complete el escaneo (se muestra progreso)
7. ¡Listo! Los archivos ahora son buscables

**Las Tarjetas de Disco Muestran:**
- Nombre y etiqueta del disco
- Estado de conexión (⚫ desconectado / 🟢 conectado)
- Capacidad y conteos de archivos
- Fecha del último escaneo
- Botones de acción: Rescanear, Exportar, Remover

#### 📊 Modo Estadísticas
Ve análisis y visualizaciones (próximamente).

### Panel Izquierdo - Colecciones

**Todos los Discos:**
- Lista de todos los discos indexados
- Haz clic para filtrar por disco
- Muestra conteos de archivos

**Escaneos Recientes:**
- Hoy
- Esta Semana
- Este Mes

**Filtros Rápidos:**
- 📄 Documentos (PDF, DOC, TXT, etc.)
- 🖼️ Imágenes (JPG, PNG, etc.)
- 🎵 Audio (MP3, WAV, etc.)
- 🎬 Videos (MP4, AVI, etc.)
- 📦 Archivos (ZIP, RAR, etc.)
- 🔷 Archivos Grandes (>100MB)

### Panel Derecho - Filtros

**Búsqueda de Texto:**
- **Búsqueda Universal:** Busca en nombres de archivo, rutas, comentarios, metadatos y etiquetas
- **Opción Sensible a Mayúsculas:** Casilla para activar/desactivar búsqueda sensible a mayúsculas
- **Alcance de Búsqueda:** Casillas para controlar dónde buscar (nombre, ruta, comentarios, metadatos, etiquetas)
- **Búsqueda Simple:** Búsqueda heredada solo por nombre de archivo
- Opción de coincidir mayúsculas
- Soporte para expresiones regulares

**Atributos de Archivo:**
- Menú desplegable de tipo de archivo
- Rango de tamaño (mín/máx bytes)
- Preajustes rápidos de tamaño

**Rango de Fechas:**
- Preajustes: Hoy, Últimos 7 días, Últimos 30 días, etc.
- Selector de rango de fechas personalizado

**Ubicación:**
- Filtrar por disco específico
- Ruta contiene texto

**Metadatos:**
- Filtro de calificación mínima
- Archivos con/sin comentarios
- Filtrado por etiquetas

**Botones de Acción:**
- "Aplicar Filtros" - Ejecutar búsqueda (muestra barra de progreso)
- "Reiniciar" - Limpiar todos los filtros
- Casilla de auto-aplicar para filtrado instantáneo

**Progreso de Búsqueda:**
- Barra de progreso aparece en la barra de estado durante operaciones de búsqueda
- Muestra mensajes "Buscando..." o "Aplicando filtros..."
- Se oculta automáticamente cuando se completa la búsqueda

## Flujos de Trabajo

### Uso por Primera Vez

1. **Inicia la aplicación**
   ```
   python main.py
   ```

2. **Cambia al modo Gestionar**
   - Haz clic en "💾 Gestionar" en la barra superior

3. **Agrega tu primer disco**
   - Haz clic en "+ Agregar Nuevo Disco"
   - Selecciona disco (ej. E:\)
   - Ingresa nombre: "USB Trabajo"
   - Haz clic en "Iniciar Escaneo"
   - Espera a que se complete

4. **Navega archivos**
   - Cambia al modo "📋 Inventario"
   - ¡Todos los archivos ahora son buscables!

### Flujo de Búsqueda Diario

1. **Abre la aplicación**
2. **Busca archivos:**
   - **Búsqueda rápida:** Escribe en la caja de búsqueda, presiona Enter
   - **Avanzada:** Usa filtros del panel derecho en modo Inventario, los filtros se aplican automáticamente o haz clic en "Aplicar Filtros"
3. **Filtra resultados:**
   - Haz clic en filtros rápidos del panel izquierdo
   - Ajusta filtros en el panel derecho (expande/colapsa secciones según necesites)
4. **Ve detalles:**
   - Haz clic en fila de archivo para ver detalles
   - Ordena por cualquier columna

### Agregar Más Discos

1. Conecta nuevo disco
2. Ve al modo Gestionar
3. Haz clic en "+ Agregar Nuevo Disco"
4. Selecciona y escanea
5. ¡Los archivos de todos los discos ahora son buscables juntos!

### Rescaneando un Disco

Cuando reconectas un disco que has escaneado antes:

1. Ve al modo Gestionar
2. Encuentra la tarjeta del disco
3. Haz clic en "🔄 Rescanear"
4. Elige "Actualización Rápida" (usa metadatos XML) o "Escaneo Completo"
5. Solo se actualizan los cambios

### Exportando Datos

**Exportar a Excel:**
1. Ve al modo Gestionar
2. Haz clic en "📤 Exportar" en la tarjeta del disco
3. Elige ubicación para guardar
4. Se crea archivo Excel con:
   - Hoja índice (todos los discos)
   - Una hoja por disco con archivos

**Exportar Resultados de Búsqueda:**
1. Busca/filtra archivos deseados
2. Haz clic en "Exportar Resultados" (próximamente)
3. Solo se exportan archivos filtrados

## Consejos y Trucos

### Rendimiento
- Los resultados de escaneo se cachean en base de datos local
- Las búsquedas rápidas son instantáneas (no requieren acceso al disco)
- Los metadatos XML permiten detección rápida de actualizaciones

### Atajos de Teclado
- `Ctrl+F` - Enfocar caja de búsqueda
- `Ctrl+R` - Actualizar resultados
- `Escape` - Limpiar búsqueda

### Organización de Archivos
- Usa nombres descriptivos para discos ("USB Trabajo" no "Disco E:")
- Agrega notas a discos en modo Gestionar
- Usa etiquetas para organizar archivos (próximamente)

### Mejores Prácticas
- Rescanea discos periódicamente para mantener inventario actualizado
- Exporta a Excel para respaldo/compartir
- Los metadatos XML permanecen en el disco para sincronización rápida

## Solución de Problemas

### Disco No Detectado
- Asegúrate de que el disco esté conectado
- Verifica que el disco esté formateado (NTFS, FAT32, exFAT)
- Intenta desconectar y reconectar

### Errores de Escaneo
- "Permiso denegado" - Ejecuta como administrador para discos del sistema
- "No se puede acceder" - Verifica permisos de archivo/carpeta
- Cancela y reinicia escaneo si se congela

### Rendimiento Lento
- Discos grandes (>1TB) toman tiempo escanear inicialmente
- Usa Actualización Rápida para escaneos posteriores
- Cierra otras aplicaciones durante el escaneo

### Problemas de Base de Datos
- Ubicación de base de datos: `data/inventory.db`
- Respaldar este archivo para preservar inventario
- Eliminar para reiniciar desde cero

## Ubicaciones de Archivos

```
HDDINVENTORY/
├── data/
│   ├── inventory.db        ← Base de datos principal
│   └── settings.json       ← Configuración de aplicación
├── main.py                 ← Ejecuta esto para iniciar
├── requirements.txt        ← Dependencias
├── install.bat            ← Instalar dependencias
└── run.bat                ← Script de inicio rápido
```

## Metadatos XML

Cada disco escaneado recibe un archivo XML oculto:
- Ubicación: Raíz del disco (ej. `E:\.drive_inventory_meta.xml`)
- Propósito: Rastrear último escaneo, conteos de archivos, ID de disco
- Usado para: Detección de sincronización rápida, avisos de actualización

**¡No elimines este archivo!** - ¡Permite actualizaciones rápidas!

## Referencia de Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl+F` | Enfocar búsqueda |
| `Ctrl+R` | Actualizar |
| `Escape` | Limpiar búsqueda |
| `F11` | Pantalla completa (próximamente) |
| `Ctrl+1` | Modo Inventario |
| `Ctrl+2` | Modo Búsqueda |
| `Ctrl+3` | Modo Gestionar |
| `Ctrl+4` | Modo Estadísticas |

## Características Avanzadas (Próximamente)

- **Vista previa de archivos** - Previsualizar imágenes, documentos
- **Detección de duplicados** - Encontrar archivos duplicados por hash
- **Colecciones virtuales** - Crear grupos personalizados de archivos
- **Etiquetas** - Etiquetar y categorizar archivos
- **Estadísticas** - Gráficos y análisis
- **Vista de cuadrícula** - Cuadrícula de miniaturas como galería de fotos
- **Vista de árbol** - Estructura jerárquica de carpetas

## Soporte y Desarrollo

Este es un proyecto de código abierto. Para problemas, sugerencias o contribuciones:
- Consulta README.md para estructura del proyecto
- Esquema de base de datos en `core/database.py`
- Componentes de UI en carpeta `ui/`

## Historial de Versiones

**v1.0.0** (Actual)
- Lanzamiento inicial
- Escaneo manual de discos
- Base de datos SQLite
- Búsqueda y filtrado avanzados
- Importación/exportación Excel
- Sincronización de metadatos XML
- Tema oscuro profesional
- Interfaz de gestión de discos

---

**¡Feliz Organización! 📦🔍**
