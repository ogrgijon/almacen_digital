# Panel de Estadísticas - Rediseño - Descripción General

## Características
- Vista general del disco: total de archivos, carpetas, discos, tamaño total
- Gráfico circular: Espacio usado vs libre por disco (con advertencia si está bajo)
- Estado de salud S.M.A.R.T. (OK, Precaución, Fallando) con ícono
- Treemap de tamaño de archivos: carpetas/archivos más grandes, interactivo
- Distribución de tipos de archivo: gráfico circular/de barras
- Traza/historial S.M.A.R.T.: tabla y gráfico de tendencias
- Recomendación de reemplazo si S.M.A.R.T. está "FALLANDO" o es crítico
- Tabla: archivos/carpetas más grandes por disco
- (Opcional) Análisis de archivos duplicados

## Estructura de Archivos
- `ui/statistics_panel.py`: Widget principal del panel
- `core/smart/smart_reader.py`: Utilidad de obtención S.M.A.R.T.
- `core/smart/smart_db.py`: Base de datos de historial S.M.A.R.T.
- `ui/README_statistics_panel.md`: Documentación del módulo
- `core/smart/README.md`: Documentos de integración S.M.A.R.T.

## Extensibilidad
- Agregar nuevas pestañas/secciones extendiendo `StatisticsPanel`
- Agregar nuevos atributos S.M.A.R.T. en BD y UI según sea necesario

## Puntos de Integración
- Llamar obtención/registro S.M.A.R.T. en rutinas de escaneo/actualización
- Mostrar panel en modo estadísticas (reemplazar statistics_view anterior)

## Requisitos
- PyQt6, matplotlib, squarify, smartctl (Windows)

## Próximos Pasos
- Integrar panel en ventana principal
- Conectar registro S.M.A.R.T. a escaneo/actualización
- Agregar más visualizaciones según sea necesario
