# Verificación de hallazgos de hyprarch

Fecha: 2026-10-12. Revisión del código de esta copia, documentación versionada de Hyprland 0.56 y fuente upstream v0.56.2; paquetes y documentación actuales de Arch. No se usó Git.

Resultado: **14 REAL, 11 FALSO, 5 DUDOSO**. Se corrigieron los defectos reales identificados, incluida la documentación de baja prioridad. “REAL” puede ser parcial: la evidencia y las exageraciones del informe se distinguen en cada fila. DUDOSO significa que el código permite la hipótesis, pero falta una medición o reproducción.

Las referencias archivo:línea corresponden a los archivos finales. La comparación con el informe describe el estado anterior a estas correcciones. Los enlaces de Hyprland fijan la versión cuando es relevante.

| Nº | Clasificación | Impacto verificado | Verificación | Evidencia | Corrección |
|---|---|---|---|---|---|
| 1 | **REAL** | Alta | No se copiaban las configuraciones de zRAM/sysctl; el valor real de swappiness es 100, no 180. La congelación/OOM descrita no está medida. | `airootfs/usr/local/bin/hyprarch-install:290`; `airootfs/etc/sysctl.d/99-hyprarch.conf:2` | Sí: copia obligatoria y comprobación de los archivos antes de tocar el disco. |
| 2 | **FALSO** | — | eval existe con configuración Lua. float, move, resize y fullscreen están implementados. El campo sobrante exact no rompe resize: relative omiso vale false en 0.56.2. | `airootfs/usr/local/bin/hyprarch-win:21`; `airootfs/usr/local/bin/hyprarch-win:54`; [hyprctl 0.56](https://wiki.hypr.land/0.56.0/Configuring/Advanced-and-Cool/Using-hyprctl/); [bindings v0.56.2](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/config/lua/bindings/LuaBindingsDispatchers.cpp) (hlWindowResize, línea 1085). | No; se conserva la API Lua. |
| 3 | **FALSO** | — | Los botones usan eval y window.close válidos; la premisa de que eval no existe es incorrecta. | `tools/wbar/wbar.c:165`; `airootfs/usr/local/bin/hyprarch-wbar-py:132`; [hyprctl 0.56](https://wiki.hypr.land/0.56.0/Configuring/Advanced-and-Cool/Using-hyprctl/); [dispatchers 0.56](https://wiki.hypr.land/0.56.0/Configuring/Basics/Dispatchers/) | No. |
| 4 | **DUDOSO** | Sin medir | La detección combina criterios con OR, no RAM y CPU con AND. El umbral de 4 GB es explícito; no hay datos que prueben <15 FPS ni que toda iGPU/8 GB deba usar lite. | `airootfs/usr/local/bin/hyprarch-perf:21`; `airootfs/usr/local/bin/hyprarch-perf:22`; `airootfs/usr/local/bin/hyprarch-perf:31` | No: se conserva la heurística y la elección manual lite/full. |
| 5 | **REAL** | Media | Se iniciaban dos procesos GTK; la presencia ya se ocultaba y dibujaba menos, así que no eran dos avatares visibles. Los 170 MB indicados no están medidos. | `airootfs/etc/skel/.config/hypr/hyprland.lua:134`; `airootfs/etc/skel/.config/hypr/hyprland.lua:140`; `airootfs/usr/local/bin/claude-presence:1110` | Sí: la presencia gráfica solo arranca si falta el ejecutable de la isla. Los comandos de estado siguen funcionando. |
| 6 | **REAL** | Media | La guarda impedía otra ventana de la misma app durante 15 s. | `airootfs/usr/local/bin/hyprarch-start:170`; `airootfs/usr/local/bin/hyprarch-start:188` | Sí: 2 s para filtrar el doble clic. |
| 7 | **FALSO** | — | dispatch recibe una expresión Lua válida; focus acepta el ID de workspace. | `airootfs/etc/skel/.config/waybar/hyprarch-workspaces:57`; [hyprctl 0.56](https://wiki.hypr.land/0.56.0/Configuring/Advanced-and-Cool/Using-hyprctl/); [dispatchers 0.56](https://wiki.hypr.land/0.56.0/Configuring/Basics/Dispatchers/); [bindings v0.56.2](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/config/lua/bindings/LuaBindingsDispatchers.cpp) (hlFocus). | No; workspace N sería la sintaxis equivocada para este modo Lua. |
| 8 | **FALSO** | — | dispatch hl.dsp.exit() es válido en modo Lua. | `airootfs/etc/skel/.config/hypr/scripts/powermenu.sh:20`; [hyprctl 0.56](https://wiki.hypr.land/0.56.0/Configuring/Advanced-and-Cool/Using-hyprctl/); [dispatchers 0.56](https://wiki.hypr.land/0.56.0/Configuring/Basics/Dispatchers/) | No. |
| 9 | **FALSO** | — | hl.exec_cmd con reglas y window.close existen. Además, normal conserva las apps por decisión explícita: no es un fallo de IPC. | `airootfs/usr/local/bin/hyprarch-mode:79`; `airootfs/usr/local/bin/hyprarch-mode:118`; `airootfs/usr/local/bin/hyprarch-mode:183`; [hyprctl 0.56](https://wiki.hypr.land/0.56.0/Configuring/Advanced-and-Cool/Using-hyprctl/); [dispatchers 0.56](https://wiki.hypr.land/0.56.0/Configuring/Basics/Dispatchers/) | No en el despacho; solo tuteo y una condición equivalente para ShellCheck. |
| 10 | **REAL** | Media | Faltaban i965 y glxinfo. intel-media-driver también soporta Broadwell: no es solo Skylake+ como afirma el informe. | `packages.extra:34`; [i965 en Arch](https://archlinux.org/packages/extra/x86_64/libva-intel-driver/); [iHD en Arch](https://archlinux.org/packages/extra/x86_64/intel-media-driver/); [glxinfo](https://archlinux.org/packages/extra/x86_64/mesa-utils/files/). | Sí: libva-intel-driver y mesa-utils; no se fuerza un driver VA-API ni se cambia hyprarch-gpu. |
| 11 | **DUDOSO** | Sin medir | Hay intro de 6,4 s y arranque concurrente, pero admite tecla/clic y preferencia off. No se demuestra que bloquee el compositor o congele el bus de disco. | `airootfs/usr/local/bin/hyprarch-intro:22`; `airootfs/usr/local/bin/hyprarch-intro:440`; `airootfs/etc/skel/.config/hypr/hyprland.lua:116` | No: requiere medir arranque en el hardware afectado. |
| 12 | **REAL** | Media | La copia de /usr/share/hyprarch no incluía los .desktop de /usr/share/applications. | `airootfs/usr/local/bin/hyprarch-install:285`; `airootfs/usr/share/applications/hyprarch-settings.desktop:6` | Sí: se copian solo hyprarch-*.desktop al destino. |
| 13 | **FALSO** | — | eval hl.config actualiza opciones en caliente. Las opciones input.kb_layout/kb_variant son válidas. | `airootfs/usr/local/bin/hyprarch-lang:49`; [hyprctl 0.56](https://wiki.hypr.land/0.56.0/Configuring/Advanced-and-Cool/Using-hyprctl/); [opciones](https://wiki.hypr.land/configuring/core/config-options/); [teclado](https://wiki.hypr.land/configuring/core/binds/keyboard-layouts/). | No en teclado; únicamente tuteo en textos fallback. |
| 14 | **REAL** | Media | Se suprimía la misma URL o una petición sin URL durante 15 s. Dos URLs distintas tienen hashes distintos: no se pierde cualquier segundo enlace. | `airootfs/usr/local/bin/hyprarch-browser:107`; `airootfs/usr/local/bin/hyprarch-browser:108` | Sí: guarda de 2 s; argumentos y elección de navegador intactos. |
| 15 | **REAL** | Alta | pacman -Q incluye epoch y el nombre de archivo de caché no; el glob anterior no encontraba esa versión. | `airootfs/usr/local/bin/hyprarch-update:62`; `airootfs/usr/local/bin/hyprarch-update:63`; [versiones de pacman](https://man.archlinux.org/man/pacman.8.en). | Sí: solo se elimina epoch del glob; comparación completa y rechazo de rollback parcial se conservan. |
| 16 | **FALSO** | — | mon_json selecciona .[0] antes de leer availableModes. Hyprland 0.56.2 publica ese campo en cada monitor (puede estar vacío según backend). | `airootfs/usr/local/bin/hyprarch-display:15`; `airootfs/usr/local/bin/hyprarch-display:19`; [HyprCtl.cpp v0.56.2](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/debug/HyprCtl.cpp) (líneas 123 y 268). | No: no se mezclan modos de otros conectores ni resoluciones inventadas. |
| 17 | **FALSO** | — | La omisión de input es intencional. Una sesión local activa con PAM/logind recibe dispositivos mediante libseat; no necesita acceso permanente a /dev/input. | `airootfs/usr/local/bin/hyprarch-install:329`; [Aquamarine/libseat en Arch](https://archlinux.org/packages/extra/x86_64/aquamarine/); [backend logind](https://github.com/kennylevinsen/seatd/blob/master/libseat/backend/logind.c); [TakeDevice](https://wiki.freedesktop.org/www/Software/systemd/logind/). | No: se mantiene sin input. Confirmación documental, no prueba de una sesión gráfica desde Windows. |
| 18 | **REAL** | Media | Si falta el proveedor se intenta instalar sin comprobar red; las esperas/reintentos de npm/pipx pueden parecer un cuelgue. No es un bloqueo infinito demostrado. | `airootfs/usr/local/bin/hyprarch-ai:143`; `airootfs/usr/local/bin/hyprarch-ai:147`; `airootfs/usr/local/bin/hyprarch-ai:95` | Sí: estado de NetworkManager (también Ethernet) y prueba TCP con timeout de 3 s; mensaje y salida antes de instalar si falla. |
| 19 | **REAL** | Media | status solo consultaba SSID/radio Wi-Fi; no reflejaba Ethernet. El panel no distinguía una máquina sin adaptador Wi-Fi. | `airootfs/usr/local/bin/hyprarch-wifi:53`; `airootfs/usr/local/bin/hyprarch-wifi:90` | Sí: status informa Ethernet; sin Wi-Fi muestra estado y abre ajustes de red, sin pedir encender una radio inexistente. |
| 20 | **REAL** | Media | El callback del brillo ejecutaba subprocess.run en GLib; podía detener la UI hasta el timeout de 1,5 s. | `airootfs/usr/local/bin/hyprarch-control:60`; `airootfs/usr/local/bin/hyprarch-control:295`; `airootfs/usr/local/bin/hyprarch-control:416` | Sí: run_async, igual que las otras acciones del panel. |
| 21 | **REAL** | Baja | La mención SUPER+D era incorrecta; no hay ese bind. El lanzador alternativo se puede ejecutar manualmente y no recorre iconos por estar instalado. | `airootfs/usr/local/bin/hyprarch-launcher:2`; `airootfs/etc/skel/.config/hypr/hyprland.lua:106` | Sí: se corrige la docstring; no se añade un atajo ni se elimina el comando. |
| 22 | **DUDOSO** | Sin medir | Hay polling cada 3 s, pero lee carga/media, alarmas y estado de IA; no equivale a los módulos cpu/memory. No hay medición de consumo y 3 s no impide por sí solo los C-states. | `airootfs/etc/skel/.config/waybar/config.jsonc:63`; `airootfs/usr/local/bin/hyprarch-sysstate:8`; `airootfs/usr/local/bin/hyprarch-sysstate:14` | No: cambiar el intervalo también retrasa alarmas; falta evidencia de impacto. |
| 23 | **DUDOSO** | Sin reproducir | El sonido se lanza con Popen, sin esperar desde GTK. No hay sincronización ni límite del reproductor, pero el informe no aporta una reproducción de espera/zombis. | `airootfs/usr/local/bin/hyprarch-start:76`; `airootfs/usr/local/bin/hyprarch-control:79` | No: requiere logs de PipeWire/procesos en un arranque afectado. |
| 24 | **FALSO** | — | El tema llama reload_all, sin sleep 3. reload recarga configuración; no equivale a reiniciar Hyprland ni a force_renderer_reload. El parpadeo/GPU congelada no se demuestra. | `airootfs/usr/local/bin/hyprarch-theme:307`; [HyprCtl.cpp v0.56.2](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/debug/HyprCtl.cpp) (reloadRequest, línea 1260). | No en la recarga; solo tuteo y limpieza de avisos de ShellCheck. |
| 25 | **REAL** | Media | La columna es mezclaba voseo/tuteo y faltaban claves usadas. No se amplía el trabajo a traducir todos los textos hardcodeados. | `airootfs/usr/share/hyprarch/i18n/strings.txt:9`; `airootfs/usr/share/hyprarch/i18n/strings.txt:40`; `airootfs/usr/local/bin/hyprarch-ai:71`; `airootfs/etc/skel/.config/hypr/scripts/keybinds.sh:4` | Sí: tuteo neutro en catálogo y textos UI afectados; 157 claves con defaults reales en español, demás columnas vacías. |
| 26 | **FALSO** | — | La cancelación ya termina con éxito antes de crear el PNG y llamar a grim. | `airootfs/etc/skel/.config/hypr/scripts/screenshot.sh:8` | No; ya estaba corregido en esta copia. |
| 27 | **FALSO** | — | El socket y las líneas 40–65 son inventados: el script solo tiene 14 líneas, encuentra una sesión y hace exec con los argumentos recibidos. | `airootfs/usr/local/bin/hyprarch-ctl:5`; `airootfs/usr/local/bin/hyprarch-ctl:14` | No; no se añade servidor ni autenticación ficticia. |
| 28 | **DUDOSO** | Sin reproducir | No existe alternativa en el wrapper. Falta demostrar el fallo antes de adquirir el lock; si el cliente muere después, el compositor debe conservar el bloqueo. DPMS off no autentica ni bloquea la sesión. | `airootfs/usr/local/bin/hyprarch-lock:7`; [protocolo session-lock](https://wayland.app/protocols/ext-session-lock-v1). | No: no se introduce una falsa alternativa de seguridad ni se termina la sesión perdiendo trabajo. |
| 29 | **REAL** | Media | Parcial: los archivos ya usan tail y no hay dmesg ni volcado completo de paquetes. journalctl | tail recorría todos los avisos del arranque aunque entregara solo 60 líneas. | `airootfs/usr/local/bin/hyprarch-report:69`; `airootfs/usr/local/bin/hyprarch-report:120` | Sí: journalctl -n 60 y timeout 3 s. Sanitización, consentimiento, ZIP/web e inclusión opt-in intactos. |
| 30 | **REAL** | Media | No había resolución previa de la lista del perfil. Puede descubrirse demasiado tarde un paquete retirado; una caché corrupta no la detecta una consulta -Sp. | `build.sh:90`; `build.sh:239`; [pacman -p](https://man.archlinux.org/man/pacman.8.en). | Sí: preflight de toda packages.x86_64 con la configuración real del perfil y bases ya sincronizadas; no instala ni descarga. |

## Alcance y decisiones

- Se conserva la configuración Lua: no se sustituyen eval ni expresiones de dispatch por comandos legacy. También se contrastó el código upstream: dispatchRequest envuelve la expresión en hl.dispatch y availableModes existe por monitor.
- El grupo input permanece excluido. logind entrega descriptores solo al controlador de la sesión activa; herramientas que quieran leer dispositivos por fuera del compositor pueden requerir permisos propios, sin justificar acceso global al grupo.
- No se tocaron hyprarch-island, hyprarch-island-policy, hyprarch-approve, hooks/settings de Claude, hyprarch-api, hyprarch-mcp ni hyprarch-report-sanitize. La importación, validación y copia privada de --ssh-key tampoco cambiaron. Los hashes de estos archivos se compararon con una instantánea previa; las pruebas de seguridad se conservan sin editar.
- El cambio del reporte afecta exclusivamente la lectura de journalctl. Las nuevas claves rep.* conservan los avisos reales actuales, incluido el consentimiento y el texto sobre --include-logs; no se copiaron las versiones desactualizadas del informe de i18n.
- El preflight de paquetes detecta errores de resolución, no corrupción de archivos de caché ni cambios de repositorio posteriores. La comprobación de red de IA tampoco garantiza que el registro npm/PyPI permanezca accesible después.

## i18n

Se normalizó únicamente el español al tuteo neutro: catálogo, selector de idiomas, menú de atajos, lanzador, selector animado, IA, editor de modos, tema e instalador. Se añadieron **157 claves ausentes**, extraídas de llamadas reales T/hyprarch-i18n/tr y usando sus defaults españoles. No se generaron traducciones para los otros once idiomas ni se alteraron las existentes. El fallback actual idioma solicitado → en → es permite resolver estas claves en idiomas sin traducción.

El análisis estático actual identifica **190 claves literales usadas** frente a las 186 del informe y un catálogo final de **191 claves**. Se comprobaron las 13 columnas de cada fila, ausencia de duplicados y resolución del fallback en es, en, pt-BR y un idioma desconocido. Los textos traducidos del bloque sugerido por Antigravity no se reutilizaron: varias claves describen funciones distintas a las del código actual.

## Validación

- **11 scripts de shell modificados:** bash -n y ./shellcheck.exe -x, todos con salida 0 y sin avisos. Se usó bash de Git para Windows con --noprofile --norc; son las mismas comprobaciones de sintaxis.
- **4 ejecutables Python modificados:** python -c con ast.parse del archivo real, todos correctos. También pasan ast.parse los 5 Python auxiliares conservados en .audit-work. Los heredocs del instalador/reporte se analizan en test_security.py.
- **bash tests/test_hyprarch_gpu.sh airootfs/usr/local/bin/hyprarch-gpu:** 72 OK, 0 FAIL, salida 0.
- **python tests/test_security.py:** 7 casos, OK, salida 0; 6 ejecutados y 1 omitido por el decorador existente en Windows (test_symlink_escape). Ese caso debe ejecutarse en Linux para confirmar protección ante enlaces simbólicos; no se eliminó ni se cambió la prueba.
- **python tests/test_mcp.py:** OK en initialize, tools/list, llamadas, validación, timeout y modo de solo lectura; salida 0.
- Comprobaciones adicionales con datos sintéticos, sin GTK/red/discos reales: guarda del menú rechaza doble clic y permite segunda ventana tras 3 s; status informa Ethernet sin Wi-Fi; el glob encuentra la versión con epoch y excluye .sig; catálogo/fallback y aviso de privacidad correctos.
- Python 3.13.7 embebido oficial, descargado temporalmente dentro del workspace porque este Windows no tenía un runtime Python instalado; no se instaló globalmente.

Límites: este entorno Windows no tiene una sesión Arch/Hyprland, pacman ni mkarchiso. No se ejecutó una instalación real, compilación de ISO, cambio de brillo físico ni prueba visual del compositor. Los resultados de FPS, RAM, C-states, arranque lento, PipeWire e inicialización de hyprlock no se dan por medidos. Queda recomendada la prueba de integración en Arch con Hyprland 0.56, especialmente la sesión sin input y el caso de symlinks omitido.

## Archivos modificados

- `build.sh`
- `packages.extra`
- `airootfs/usr/share/hyprarch/i18n/strings.txt`
- `airootfs/usr/local/bin/hyprarch-ai`
- `airootfs/usr/local/bin/hyprarch-browser`
- `airootfs/usr/local/bin/hyprarch-control`
- `airootfs/usr/local/bin/hyprarch-install`
- `airootfs/usr/local/bin/hyprarch-lang`
- `airootfs/usr/local/bin/hyprarch-launcher`
- `airootfs/usr/local/bin/hyprarch-mode`
- `airootfs/usr/local/bin/hyprarch-pick`
- `airootfs/usr/local/bin/hyprarch-report`
- `airootfs/usr/local/bin/hyprarch-start`
- `airootfs/usr/local/bin/hyprarch-theme`
- `airootfs/usr/local/bin/hyprarch-update`
- `airootfs/usr/local/bin/hyprarch-wifi`
- `airootfs/etc/skel/.config/hypr/hyprland.lua`
- `airootfs/etc/skel/.config/hypr/scripts/keybinds.sh`
- `_ref/RESUMEN.md`

La lista anterior identifica los 19 archivos entregables de código/configuración/informe. `_ref/codex.log` puede crecer por el registro automático de la sesión; no se editó como parte de la solución. Los dos informes de Antigravity, los tests y shellcheck.exe se conservan.

## Auxiliares de auditoría conservados

La revisión automática del entorno rechazó eliminar `.audit-work/`, incluso con una limpieza por archivos, con el motivo literal «blocked by policy». No se solicitaron permisos ni se intentó eludir esa política. Estos archivos nuevos son auxiliares, no forman parte de la ISO y pueden descartarse por el dueño:

- `.audit-work/baseline.json`: hashes originales para comprobar el alcance.
- `.audit-work/changed.json`: lista de archivos funcionales modificados.
- `.audit-work/fetch.cjs`: descarga de fuentes/documentación y Python oficial.
- `.audit-work/inspect.py`, `.audit-work/i18n.py`: análisis del español y registro de claves faltantes. `i18n.py` es una herramienta de esta ejecución, no debe volver a aplicarse al catálogo final.
- `.audit-work/validate.py`, `.audit-work/regressions.py`, `.audit-work/report.py`: comprobaciones y generación inicial del resumen. No volver a generar el resumen: el entregable contiene notas finales añadidas después.
- `.audit-work/versions.html`, `.audit-work/wiki56.html`, `.audit-work/ipc.html`, `.audit-work/ipc56.html`, `.audit-work/dispatch.html`, `.audit-work/dispatch56.html`: documentación consultada.
- `.audit-work/hyprland.tar.gz`, `.audit-work/HyprCtl.cpp`, `.audit-work/Check.cpp`, `.audit-work/LuaBindingsConfigRules.cpp`, `.audit-work/LuaBindingsDispatchers.cpp`, `.audit-work/LuaBindingsDispatcherUtils.cpp`: fuentes upstream v0.56.2 consultadas.
- `.audit-work/python.zip` y los archivos del runtime oficial expandido en `.audit-work/python/`: Python 3.13.7, biblioteca estándar, extensiones, DLL y licencia. Se conserva exclusivamente dentro del workspace, sin instalación global.
