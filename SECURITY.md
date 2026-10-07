# Security Policy / Política de Seguridad

> **🇪🇸 [Versión en Español](#español) | 🇺🇸 [English Version](#english)**

---

## English

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :x:                |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability within Almacén Digital, please follow these steps:

### 1. Do Not Disclose Publicly

Please do not open a public issue or discussion about the vulnerability. This helps protect users who have not yet updated.

### 2. Contact Us Privately

Report the vulnerability privately through one of these channels:

- **GitHub Security Advisories**: Use the "Security" tab in the repository to report privately
- **Direct Contact**: Reach out via [LinkedIn](https://www.linkedin.com/in/ogrgijon) with details
- **Email**: Send details through LinkedIn messaging

### 3. Provide Details

When reporting, please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Any suggested fixes (if you have them)
- Your contact information

### 4. Response Timeline

- **Initial Response**: Within 48 hours
- **Assessment**: Within 1 week
- **Fix Development**: Depends on severity (1-4 weeks)
- **Public Disclosure**: After fix is released and users have time to update

## Security Best Practices for Users

### Data Protection

1. **Backup Regularly**: Always maintain backups of your catalog database
2. **Secure Storage**: Store sensitive catalog data on encrypted drives
3. **Access Control**: Limit access to the application and its database files
4. **Network Security**: When using sync features, ensure secure network connections

### Application Security

1. **Keep Updated**: Always use the latest version of Almacén Digital
2. **Verify Downloads**: Download only from official sources (GitHub releases)
3. **Check Integrity**: Verify file hashes when available
4. **Scan for Malware**: Use antivirus software on downloaded files

### Privacy Considerations

1. **Local Data**: All catalog data is stored locally by default
2. **Sync Feature**: Sync functionality uses your chosen cloud storage
3. **No Telemetry**: The application does not send usage data to external servers
4. **File Metadata**: Only file metadata is stored, not file contents

## Known Security Considerations

### File System Access

- The application requires read access to drives you choose to catalog
- Write access is only needed for creating the metadata file on drives
- Never grant unnecessary permissions

### Database Security

- The SQLite database is stored in the application's data folder
- Consider encrypting the data folder if storing sensitive file information
- The database is not encrypted by default

### S.M.A.R.T. Monitoring

- Requires system-level access to disk information
- Uses smartmontools which requires elevated permissions on some systems
- Review smartmontools documentation for security implications

## Vulnerability Disclosure Policy

When a vulnerability is confirmed:

1. We will develop and test a fix
2. We will prepare a security advisory
3. We will release a patched version
4. We will publish the security advisory with:
   - Description of the vulnerability
   - Affected versions
   - Fixed version
   - Mitigation steps for users who cannot update immediately
   - Credit to the reporter (if desired)

## Security Update Process

1. **Critical Updates**: Released as soon as possible (within days)
2. **High Priority**: Released within 1-2 weeks
3. **Medium Priority**: Included in next regular release
4. **Low Priority**: Scheduled for future releases

Users will be notified through:
- GitHub Security Advisories
- Release notes
- CHANGELOG.md updates

## Contact

For security concerns, contact:
- **Security Issues**: GitHub Security Advisories (preferred)
- **General Contact**: [LinkedIn - OGRGijon](https://www.linkedin.com/in/ogrgijon)
- **Repository**: [GitHub Issues](https://github.com/ogrgijon/almacen_digital/issues) (for non-security bugs)

---

## Español

## Versiones Soportadas

Liberamos parches para vulnerabilidades de seguridad. Qué versiones son elegibles para recibir tales parches depende de la Calificación CVSS v3.0:

| Versión | Soportada          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :x:                |
| < 1.0   | :x:                |

## Reportar una Vulnerabilidad

Si descubres una vulnerabilidad de seguridad en Almacén Digital, por favor sigue estos pasos:

### 1. No Divulgues Públicamente

Por favor no abras un issue público o discusión sobre la vulnerabilidad. Esto ayuda a proteger a usuarios que aún no han actualizado.

### 2. Contáctanos Privadamente

Reporta la vulnerabilidad privadamente a través de uno de estos canales:

- **GitHub Security Advisories**: Usa la pestaña "Security" en el repositorio para reportar privadamente
- **Contacto Directo**: Comunícate vía [LinkedIn](https://www.linkedin.com/in/ogrgijon) con detalles
- **Email**: Envía detalles a través de mensajería de LinkedIn

### 3. Proporciona Detalles

Al reportar, por favor incluye:

- Descripción de la vulnerabilidad
- Pasos para reproducir el problema
- Impacto potencial
- Cualquier corrección sugerida (si las tienes)
- Tu información de contacto

### 4. Cronograma de Respuesta

- **Respuesta Inicial**: Dentro de 48 horas
- **Evaluación**: Dentro de 1 semana
- **Desarrollo de Corrección**: Depende de la severidad (1-4 semanas)
- **Divulgación Pública**: Después de que la corrección se libere y los usuarios tengan tiempo de actualizar

## Mejores Prácticas de Seguridad para Usuarios

### Protección de Datos

1. **Respalda Regularmente**: Siempre mantén respaldos de tu base de datos de catálogo
2. **Almacenamiento Seguro**: Guarda datos sensibles del catálogo en discos encriptados
3. **Control de Acceso**: Limita el acceso a la aplicación y sus archivos de base de datos
4. **Seguridad de Red**: Al usar funciones de sincronización, asegura conexiones de red seguras

### Seguridad de la Aplicación

1. **Mantén Actualizado**: Siempre usa la última versión de Almacén Digital
2. **Verifica Descargas**: Descarga solo de fuentes oficiales (releases de GitHub)
3. **Verifica Integridad**: Verifica hashes de archivo cuando estén disponibles
4. **Escanea por Malware**: Usa software antivirus en archivos descargados

### Consideraciones de Privacidad

1. **Datos Locales**: Todos los datos del catálogo se almacenan localmente por defecto
2. **Función de Sincronización**: La funcionalidad de sincronización usa tu almacenamiento en la nube elegido
3. **Sin Telemetría**: La aplicación no envía datos de uso a servidores externos
4. **Metadatos de Archivo**: Solo se almacenan metadatos de archivo, no contenidos de archivo

## Consideraciones de Seguridad Conocidas

### Acceso al Sistema de Archivos

- La aplicación requiere acceso de lectura a discos que elijas catalogar
- El acceso de escritura solo se necesita para crear el archivo de metadatos en discos
- Nunca otorgues permisos innecesarios

### Seguridad de Base de Datos

- La base de datos SQLite se almacena en la carpeta de datos de la aplicación
- Considera encriptar la carpeta de datos si almacenas información de archivos sensibles
- La base de datos no está encriptada por defecto

### Monitoreo S.M.A.R.T.

- Requiere acceso a nivel de sistema a información de disco
- Usa smartmontools que requiere permisos elevados en algunos sistemas
- Revisa la documentación de smartmontools para implicaciones de seguridad

## Política de Divulgación de Vulnerabilidades

Cuando se confirma una vulnerabilidad:

1. Desarrollaremos y probaremos una corrección
2. Prepararemos un aviso de seguridad
3. Liberaremos una versión parcheada
4. Publicaremos el aviso de seguridad con:
   - Descripción de la vulnerabilidad
   - Versiones afectadas
   - Versión corregida
   - Pasos de mitigación para usuarios que no puedan actualizar inmediatamente
   - Crédito al reportero (si lo desea)

## Proceso de Actualización de Seguridad

1. **Actualizaciones Críticas**: Liberadas lo antes posible (dentro de días)
2. **Alta Prioridad**: Liberadas dentro de 1-2 semanas
3. **Prioridad Media**: Incluidas en el próximo lanzamiento regular
4. **Baja Prioridad**: Programadas para lanzamientos futuros

Los usuarios serán notificados a través de:
- GitHub Security Advisories
- Notas de lanzamiento
- Actualizaciones de CHANGELOG.md

## Contacto

Para preocupaciones de seguridad, contacta:
- **Problemas de Seguridad**: GitHub Security Advisories (preferido)
- **Contacto General**: [LinkedIn - OGRGijon](https://www.linkedin.com/in/ogrgijon)
- **Repositorio**: [GitHub Issues](https://github.com/ogrgijon/almacen_digital/issues) (para bugs no relacionados con seguridad)

---

**Thank you for helping keep Almacén Digital and its users safe!**

**¡Gracias por ayudar a mantener Almacén Digital y sus usuarios seguros!**
