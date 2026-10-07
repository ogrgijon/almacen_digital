# Sincronización de Base de Datos HDDInventory

## Descripción General

HDDInventory incluye capacidad de sincronización de base de datos que permite compartir el inventario entre múltiples computadoras usando una carpeta sincronizada con servicio externo de almacenamiento en la nube.

## Características

- **Sincronización Automática**: La aplicación puede sincronizar automáticamente al iniciar y/o cerrar
- **Control de Versiones**: Cada cambio incrementa un número de versión para determinar qué base de datos está más actualizada
- **ID Único**: Cada inventario tiene un ID único para evitar sincronizar bases de datos incorrectas
- **Tres Modos de Sincronización**:
  - **Bidireccional**: Sincroniza automáticamente usando la versión más reciente
  - **Solo desde respaldo**: Solo lee del respaldo, nunca escribe (útil para acceso de solo lectura)
  - **Solo hacia respaldo**: Solo escribe al respaldo, nunca lee (útil para computadora principal)

## Configuración Inicial

### 1. Configurar Carpeta Sincronizada

Primero, asegúrese de tener una carpeta sincronizada con su servicio externo de almacenamiento en la nube:

- Configure una carpeta dedicada para HDDInventory en su servicio de sincronización
- Ejemplo: `C:\Users\Usuario\Sincronizacion\HDDInventory\`

### 2. Abrir Configuración de Sincronización

En HDDInventory, vaya a:
- Menú → Configuración → Sincronización
- O use el acceso rápido desde la barra de herramientas

### 3. Configurar Parámetros

1. **Habilitar sincronización automática**: Marque esta casilla

2. **Ubicación del Respaldo**: Especifique la ruta completa al archivo de respaldo
   - Ejemplo: `C:\Users\Usuario\Sincronizacion\HDDInventory\inventory_backup.db`
   - Use el botón "Examinar..." para seleccionar la ubicación
   - El archivo se creará automáticamente si no existe

3. **Dirección de Sincronización**: Seleccione el modo apropiado
   - **Bidireccional** (recomendado): Para uso normal en múltiples computadoras
   - **Solo desde respaldo**: Para computadoras donde solo quiere ver el inventario
   - **Solo hacia respaldo**: Para la computadora principal que siempre tiene los datos más actualizados

4. **Momento de Sincronización**: Seleccione cuándo sincronizar
   - **Al iniciar**: Sincroniza cuando abre la aplicación
   - **Al cerrar**: Sincroniza cuando cierra la aplicación
   - Puede seleccionar ambos (recomendado)

5. **Probar Conexión**: Haga clic para verificar que la ruta es accesible

6. **Guardar**: Guarde la configuración

## Uso en Múltiples Computadoras

### Configuración del Primer Equipo (Computadora A)

1. Configure HDDInventory normalmente y agregue sus unidades
2. Configure la sincronización apuntando a una carpeta en la nube
3. Cierre la aplicación (esto creará el archivo de respaldo)
4. Espere a que el archivo se sincronice con la nube

### Configuración de Equipos Adicionales (Computadora B, C, etc.)

1. Instale HDDInventory
2. **NO agregue unidades todavía**
3. Configure la sincronización apuntando al mismo archivo de respaldo
4. Cierre y vuelva a abrir la aplicación
5. La base de datos se sincronizará automáticamente desde el respaldo
6. Ahora puede ver y agregar sus propias unidades

## Cómo Funciona

### Sistema de Versiones

Cada vez que se realizan cambios en la base de datos:
- El número de versión se incrementa automáticamente
- Se registra la fecha/hora de modificación
- Al sincronizar, se compara la versión local con la del respaldo
- Se usa la versión más alta (más reciente)

### Proceso de Sincronización

#### Sincronización Bidireccional

1. Al iniciar o cerrar la aplicación
2. Compara versión local vs. versión del respaldo
3. Si el respaldo es más nuevo: Actualiza la base de datos local
4. Si local es más nuevo: Actualiza el archivo de respaldo
5. Si son iguales: No hace nada

#### Solo desde Respaldo

1. Al iniciar la aplicación
2. Si el respaldo es más nuevo: Actualiza la base de datos local
3. Nunca escribe al respaldo

#### Solo hacia Respaldo

1. Al cerrar la aplicación
2. Siempre actualiza el archivo de respaldo con la base de datos local
3. Nunca lee del respaldo

## Resolución de Problemas

### El archivo de respaldo no se encuentra

**Problema**: La aplicación no puede encontrar el archivo de respaldo

**Soluciones**:
- Verifique que la carpeta sincronizada esté conectada y actualizada
- Asegúrese de que el cliente de sincronización esté en ejecución
- Verifique los permisos de la carpeta
- Use "Probar Conexión" en la configuración de sincronización

### IDs de inventario diferentes

**Problema**: "Different inventory IDs" en el log

**Explicación**: Esto significa que está intentando sincronizar con una base de datos de un inventario completamente diferente

**Solución**: 
- Asegúrese de que todas las computadoras usen el mismo archivo de respaldo
- Si intencionalmente quiere usar una base de datos diferente, cree una nueva carpeta de respaldo

### Conflictos de sincronización

**Problema**: Cambios realizados en múltiples computadoras simultáneamente

**Explicación**: El sistema de versiones maneja esto automáticamente

**Comportamiento**:
- En modo bidireccional: Gana la versión más alta
- Los cambios de la versión más baja se perderán
- Se recomienda trabajar en una sola computadora a la vez

### Sincronización muy lenta

**Problema**: La sincronización tarda mucho tiempo

**Soluciones**:
- La primera sincronización puede tardar debido al tamaño del archivo
- Sincronizaciones posteriores son más rápidas (solo se copia el archivo completo)
- Considere usar solo sincronización al cerrar si tiene una base de datos grande
- Verifique la velocidad de su conexión a internet

## Mejores Prácticas

1. **Haga respaldos regulares**: El archivo de respaldo ES un respaldo, pero también haga copias periódicas

2. **Use modo bidireccional**: A menos que tenga una razón específica, use el modo bidireccional

3. **Sincronice al inicio y al cierre**: Esto asegura que siempre tenga la versión más reciente

4. **Verifique el estado de sincronización**: Revise los logs en `data/hddinventory.log` para ver el estado de la sincronización

5. **Trabajo en equipo**: Si múltiples personas usan el inventario:
   - Coordinen quién hace cambios cuándo
   - Cierre la aplicación antes de que otra persona la abra
   - Espere a que la sincronización se complete

6. **Carpeta dedicada**: Use una carpeta dedicada para el archivo de respaldo
   - No mezcle con otros archivos
   - Facilita el mantenimiento y respaldo

## Estructura de Metadatos

El sistema de sincronización agrega una tabla `sync_metadata` a la base de datos:

```sql
CREATE TABLE sync_metadata (
    id INTEGER PRIMARY KEY,
    unique_id TEXT NOT NULL,          -- UUID único del inventario
    version INTEGER DEFAULT 1,        -- Número de versión incremental
    last_modified TEXT                -- Timestamp ISO de última modificación
)
```

Esta información permite:
- Identificar inventarios únicos
- Determinar qué versión es más reciente
- Rastrear cuándo se realizaron cambios

## Seguridad y Privacidad

- **Datos locales**: Su base de datos local siempre se mantiene
- **Respaldo automático**: Se crea un `.db.bak` antes de sobrescribir
- **Sin conexión a servidores**: Todo funciona mediante archivos compartidos
- **Control total**: Usted controla dónde se almacena el respaldo
- **Privacidad**: Los datos solo se comparten a través de su propia configuración de sincronización

## Limitaciones

- No es sincronización en tiempo real (solo al iniciar/cerrar)
- No maneja fusión de cambios conflictivos (usa la versión más alta)
- Requiere configuración manual de carpeta sincronizada
- El archivo completo se copia cada vez (no delta sync)

## Soporte

Para problemas o preguntas:
1. Revise el archivo de log: `data/hddinventory.log`
2. Verifique que el servicio de sincronización esté funcionando
3. Use "Probar Conexión" en la configuración
4. Reporte problemas con información del log
