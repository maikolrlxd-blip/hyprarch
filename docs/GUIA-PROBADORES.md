# Guía para probar hyprarch (¡gracias por ayudar!)

**hyprarch** es un sistema operativo en desarrollo (Arch Linux + escritorio Hyprland) pensado como casa para IAs que ayudan en el
día a día, y también para jugar y usar el ordenador con comodidad, incluso en equipos modestos. Todavía está en **fase de prueba**:
buscamos fallos, cosas que confundan y cosas que no se vean o suenen bien.

## Antes de empezar (seguridad primero)
- **Usa el USB en modo «en vivo».** Arrancas desde el USB, pruebas, apagas, sacas el USB y tu ordenador queda como estaba.
- **No instales en tu disco principal.** El instalador borra el disco que elijas. Si quieres probar la instalación, hazlo en una
  **máquina virtual** o en un equipo/disco de pruebas.
- No metas contraseñas importantes, ni inicies sesión en tu banco ni en cuentas delicadas.

## Cómo arrancar
1. Conecta el USB, reinicia y pulsa la tecla del menú de arranque (suele ser **F12**, a veces F8, F11 o Esc).
2. Elige el USB en modo **UEFI** y, en el menú, «hyprarch - Hyprland live».
3. Espera la animación de entrada y sigue el asistente de primer inicio (elige tu idioma).

## Qué probar (marca lo que pruebes)
- [ ] ¿Arranca y llega al escritorio? ¿A qué resolución? ¿Se ve nítido?
- [ ] **Wi‑Fi:** clic en el icono de red de la barra (o **SUPER+N**; SUPER = tecla Windows). ¿Aparecen tus redes? ¿Te conecta?
- [ ] **Sonido:** ¿suena la animación de entrada y los menús? ¿Hay chasquidos o ruidos raros? ¿Funcionan las teclas de volumen y se ve el aviso?
- [ ] **Menús:** **SUPER+D** (aplicaciones), **SUPER+ESC** (apagar/bloquear), **SUPER+T** (colores), **SUPER+I** (instalar apps), **SUPER+F1** (todos los atajos). ¿Van fluidos?
- [ ] **Teclado y ratón/trackpad:** ¿funcionan bien? ¿Las teclas especiales (brillo, volumen)?
- [ ] **Modos** (gamer, cine, estudio, trabajo): desde el menú de Hyro (clic en el robot). ¿Cambian el fondo y abren sus apps?
- [ ] **Navegador y archivos:** abre Firefox y una web; abre la carpeta de archivos.
- [ ] **Rendimiento:** ¿se siente rápido o se arrastra? ¿Se calienta el equipo? ¿Cuánto dura la batería (portátiles)?
- [ ] **Suspender y bloquear** la pantalla, y volver.
- [ ] **Idiomas:** cambia el idioma (SUPER+L): ¿se ve bien tu idioma, también los textos especiales?
- [ ] Cualquier cosa que te confunda, te parezca fea, lenta o rara. **Las impresiones tuyas son tan valiosas como los errores.**

## Cómo reportar un problema (30 segundos)
1. Pulsa **SUPER+D** y busca **«Reportar un problema»** (o escribe `hyprarch-report` en una terminal).
2. Escribe en una frase qué pasó y elige si incluyes una captura.
3. Se crea un archivo `hyprarch-reporte-FECHA.txt` en tu carpeta personal (y, si quisiste, una imagen). **Léelo si quieres: no incluye contraseñas ni nombres de tus redes Wi‑Fi.**
4. Envíame ese archivo (y la foto/captura, si hay) con tu mensaje. Si el sistema no arranca, una **foto con el móvil** de la pantalla ya ayuda mucho.

## Qué datos son más útiles
- Qué equipo es (marca, modelo, año) y si es portátil o de escritorio.
- Qué estabas haciendo justo antes del fallo y si se puede repetir.
- Si algo te sorprendió **para bien** también cuéntalo.

¡Gracias! Cada fallo que encuentres hoy es uno que nadie más sufrirá mañana.
