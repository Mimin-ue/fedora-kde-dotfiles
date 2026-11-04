# Comprobaciones

Fecha del respaldo: 4 de noviembre de 2026.

- Se exportaron los archivos activos del resultado final, después de los últimos cambios del micrófono y del texto móvil de música.
- Los recursos comprimidos se verifican con SHA256; el inventario contiene 576 archivos de contenido. El tema de iconos completo tiene su propio archivo interno, sin caché generada.
- El archivo comprimido se extrajo con el filtro seguro `data` de Python; también se extrajo así el archivo interno de iconos, incluidos sus enlaces relativos.
- La instalación se ejecutó en una carpeta de usuario de prueba vacía mediante `--stage-only`. Se verificaron rutas adaptadas, archivos de apariencia, componentes y lanzador, sin llamar a los servicios de KDE ni descargar software.
- La restauración de esa prueba retiró correctamente los archivos y directorios creados y el lanzador. Los respaldos quedan fuera del repositorio.
- Se comprobó la sintaxis de los scripts Python y se ejecutó el constructor del panel en una simulación de la API de Plasma: los 22 módulos reciben identificadores nuevos y se conserva el orden.
- Se revisó que el perfil incluya cierre directo, borde redondeado, nueva imagen, tamaño del micrófono y título de música en movimiento.
- Se buscaron rutas del usuario original, nombre del equipo, identificadores del monitor y de escritorios, claves privadas y patrones de credenciales en los recursos de texto y ajustes exportados. No se encontraron datos privados de ese tipo. No se exportaron historiales, cookies, credenciales, conexiones WiFi ni documentos.
- Los componentes visuales y las animaciones están comprobados en el escritorio original. El acceso de Terminal Venom se probó mediante el lanzador de KDE en español y abrió la versión local correcta de Kitty.

## Límites

No se reinstaló el computador original para probar este repositorio ni se aplicó de nuevo el panel mientras el usuario lo estaba usando. No se realizó una prueba completa desde cero en una máquina virtual nueva. La prueba aislada valida archivos, integridad y restauración; no sustituye la comprobación visual tras iniciar sesión en el otro equipo.

La distribución de mosaicos se ajusta por monitor mediante Meta+T. La apariencia administrativa de Plasma Login Manager se incluye como paso opcional y separado; debe comprobarse entrando realmente en la sesión. Otras versiones de Plasma pueden requerir adaptaciones.

## Capturas públicas

Se añadieron cuatro capturas reales: escritorio, Terminal Venom, conjunto con btop/Cmatrix y detalle del panel. Se tomaron en un escritorio vacío y se revisaron antes de subirlas. Las ventanas de vista previa usaron `usuario@fedora` y no muestran procesos, documentos, mensajes ni ventanas personales. Las configuraciones de vista previa no sustituyeron las del usuario.
