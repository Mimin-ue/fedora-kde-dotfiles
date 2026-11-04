# Mi escritorio Fedora KDE

Copia del **estado final del 4 de noviembre de 2026**, para recrearlo en otro computador. Incluye únicamente la apariencia y sus componentes: no hay sesiones del navegador, contraseñas, documentos, historiales, claves ni respaldos personales. Este repositorio es privado.

## Qué recupera

- Fondo minimalista de dunas azul grisáceo, colores oscuros, tema de Plasma y aplicaciones, iconos **Gruvbox Plus Dark** y cursor Sweet.
- Una sola barra superior de 32 px: lanzador, cinco escritorios circulares, accesos a aplicaciones, nombre de ventana, música, controles del sistema, hora y días con Fedora. Sin dock inferior.
- Bordes finos por módulos, separación corta entre escritorios y aplicaciones, reloj **JetBrains Mono 8 pt** dentro de su recuadro, iconos pequeños y micrófono ajustado.
- Canción y artista reales mediante MPRIS, título largo que se desplaza en bucle y visualizador de cinco bandas de audio reales mediante CAVA. Clic: reproducir/pausar; rueda: siguiente/anterior; clic central: abrir reproductor.
- **Terminal Venom**: Kitty 0.50.0, Fish, Fastfetch y la ilustración morada de Venom, fondo al 84 % de opacidad, desenfoque, borde claro de 1,5 px y esquinas de 6 px; cierre sin confirmación.
- Desvanecimiento al abrir/cerrar y minimizar/restaurar. Meta + arrastre izquierdo para mover; Meta + arrastre derecho para redimensionar. Alt+F4 para cerrar; Meta+Av Pág para minimizar; Meta+D para minimizar/restaurar todas.
- Pantalla de bloqueo con el fondo de dunas, reloj y controles multimedia. La apariencia del inicio de sesión está incluida como paso opcional separado.

Los días junto al corazón se cuentan desde **3 de noviembre de 2026**, preservando la fecha de este escritorio. No se modifica la shell de inicio de sesión de la cuenta: Fish se utiliza sólo dentro de Terminal Venom.

## Preparar otro computador

Usar **Fedora KDE con Plasma 6.8.x y Wayland, arquitectura x86_64**. La configuración usa funciones de KDE; no instala Hyprland ni controladores de GPU. La resolución original era 1920×1200, pero no se copian resoluciones, números de serie de pantallas ni identificadores de dispositivos.

1. Iniciar sesión en GitHub con tu cuenta y descargar este repositorio con **Code → Download ZIP**, o clonarlo con tu método de autenticación habitual. Extraer el ZIP y abrir una terminal dentro de la carpeta.
2. Instalar las dependencias desde los repositorios de Fedora:

```bash
sudo dnf install fish fastfetch cava btop cmatrix kvantum python3-pyside6 google-noto-sans-mono-fonts
```

La edición KDE ya proporciona Plasma, KWin, `qdbus-qt6`, `kwriteconfig6`, `kbuildsycoca6` y las fuentes de símbolos de Noto. Si la comprobación siguiente indica que falta alguno, instalar el paquete correspondiente de Fedora antes de aplicar.

3. Revisar los archivos y comprobar dependencias e integridad:

```bash
python3 install.py --check
```

Este paso no cambia el escritorio. Para inspeccionar una prueba completa de los archivos sin modificar KDE:

```bash
python3 install.py --stage-only /tmp/prueba-escritorio-kde
```

La carpeta de prueba debe estar vacía. Este modo no descarga Kitty ni inicia servicios ni altera el panel.

4. Desde una terminal de la sesión KDE, aplicar **sin sudo**:

```bash
python3 install.py --apply
```

Esto respalda los archivos que va a cambiar, instala los recursos incluidos y sustituye los paneles existentes por el panel superior guardado. No cierra tus aplicaciones. Descarga la versión oficial de Kitty 0.50.0 y comprueba la suma SHA256 registrada antes de extraerla; no ejecuta instaladores externos. Mantiene el Kitty del sistema separado. Necesita Internet para esa descarga.

Al terminar, cerrar e iniciar sesión para que las aplicaciones abiertas adopten todos los estilos y atajos. Abrir **Terminal Venom** desde la barra o el menú de aplicaciones. Se renueva la caché de KDE tanto en español como en inglés para evitar que el acceso abra el Kitty antiguo sin redondeo.

### Ajustes dependientes del equipo

- **Aplicaciones:** Firefox, Brave, KWrite y Dolphin conservan sus accesos si están instalados. Los accesos ausentes se omiten; no se instala Brave ni se copian sus datos. Puedes añadir las aplicaciones que uses al módulo de lanzamiento rápido.
- **Mosaicos:** las zonas pertenecen a cada monitor. Con **Meta+T**, ajustar tres columnas de **25 % / 50 % / 25 %** y separación de **4 px**, si quieres conservar esa distribución. No se reutilizan los identificadores del monitor anterior.
- **Música:** el reproductor o navegador debe exponer MPRIS; en silencio las bandas quedan bajas. CAVA toma el monitor de la salida de audio, no el micrófono. Servicio: `systemctl --user status local-mimin-spectrum.service`.
- **Avatar, cuenta y contraseña:** se conservan los del computador nuevo. No están en este respaldo.
- Otras versiones de Plasma o distribuciones pueden necesitar adaptar los componentes. No está probado como instalador universal ni en ARM.

## Volver atrás

El instalador muestra la carpeta del respaldo, dentro de:

```text
~/.local/state/fedora-kde-dotfiles/backups/
```

Cerrar Terminal Venom antes de restaurar y ejecutar, indicando la carpeta exacta que imprimió el instalador:

```bash
python3 restore.py /ruta/al/respaldo
```

Recupera los archivos y paneles anteriores, los servicios y los efectos. Sólo retira los escritorios añadidos por esa instalación. La restauración puede sustituir cambios posteriores en los mismos archivos. Los respaldos permanecen **locales** y no se suben a GitHub.

## Inicio de sesión al encender: opcional

El computador original usa **Plasma Login Manager**, no SDDM. Los recursos incluidos preservan su apariencia actual: reloj, paleta clara sobre fondo oscuro y el fondo que tenía el gestor de inicio de sesión. Este fondo es independiente del escritorio y del bloqueo.

Revisar `install-login.py` y, sólo si el nuevo computador utiliza Plasma Login Manager:

```bash
pkexec /usr/bin/python3 install-login.py
```

Fedora solicitará autorización de administrador. El script se detiene si falta la cuenta `plasmalogin`; no sirve para SDDM ni modifica la autenticación. El respaldo de este paso queda en `/var/lib/plasmalogin/mimin-appearance-backups/`. Para restaurarlo:

```bash
pkexec /usr/bin/python3 restore-login.py
```

La configuración administrativa original se aplicó correctamente; su apariencia completa debe comprobarse al iniciar sesión realmente. No se promete que la vista de prueba del greeter sustituya esa comprobación.

## Archivos y cómo se hizo

| Archivo | Contenido |
| --- | --- |
| `settings.json` | Ajustes visuales filtrados, módulos y distribución; usa `@HOME@` en lugar de un nombre de usuario fijo. |
| `panel.js` | Crea el panel mediante la API de Plasma y asigna identificadores nuevos a sus módulos. |
| `desktop-files.tar.gz` | Recursos finales: componentes QML, temas, iconos, fuentes, fondo, perfil Kitty/Fish/Fastfetch, Venom, servicio CAVA y apariencia del login. |
| `desktop-files.sha256` | Suma de integridad del archivo comprimido. |
| `files-manifest.json` | Inventario con SHA256 de cada archivo de recursos. |
| `install.py` / `restore.py` | Aplicación con respaldos y restauración de la sesión del usuario. |
| `install-login.py` / `restore-login.py` | Paso administrativo opcional, separado. |
| `LICENSES.md` | Origen y licencias de los componentes. |
| `VALIDATION.md` | Alcance de las comprobaciones realizadas. |

La base es KDE y su tema Utterly Sweet; Panel Colorizer aporta los recuadros. Se ajustó localmente el color del título de ventana y el tamaño de las representaciones compactas, incluido el micrófono. Los círculos de escritorios, contador de días, módulo MPRIS con texto móvil y puente CAVA son componentes locales incluidos.

Las esquinas de la terminal se dibujan con un sombreado propio de Kitty (`rounded.slang`): recorta el contorno y añade un borde claro sin oscurecer el texto ni la imagen. Se usa porque el borde redondeado integrado de la versión probada producía una superposición sobre el contenido. Kitty está fijado a una versión y suma verificadas; la firma GPG de su descarga original se comprobó con la huella completa de Kovid Goyal, registrada dentro de los recursos.

Se conserva el resultado final, sin los estados intermedios de personalización ni la conversación. **No es una copia de seguridad de tus documentos ni de todo el sistema.**
