# hyprarch

**Un sistema operativo (Arch Linux + Hyprland) pensado como casa para tu IA.**
Tu IA conoce el sistema, lo controla con permisos claros y tú sigues al mando. También es cómodo para jugar,
trabajar y funcionar en equipos modestos.

> **Estado: beta.** Se prueba en VM y en algún equipo real; faltan pruebas en más hardware. Úsalo en modo «en vivo»
> (USB) o en una máquina virtual antes de instalarlo en un disco que te importe: el instalador **borra el disco que elijas**.

## Qué trae
- **La isla de Hyro** (arriba al centro): una pastilla que se abre en un chat con la IA que elijas (Claude, Codex, Gemini
  u Ollama). Si la IA necesita permiso para ejecutar algo, sale una tarjeta con el comando completo y **solo se ejecuta si pulsas «Permitir»**.
- **`hyprarch-api`**: acciones acotadas y seguras con respuesta JSON para que una IA controle el escritorio
  (ventanas, apps, modos, temas, volumen, Wi-Fi, capturas…). Funciona también por SSH. Guía para IAs: [`AGENTS.md`](airootfs/etc/skel/AGENTS.md).
- **Modos** (gamer, cine, estudio, trabajo, normal) con efectos reales: rendimiento, avisos, tema, fondo y apps propias, configurables en una ventana.
- **Escritorio propio**: barra, menú de inicio, centro de control, selector animado, sonidos, tema de colores con un solo acento.
- **Pensado para equipos modestos**: perfil ligero automático, menús que se adaptan a la potencia disponible.
- **Todos los idiomas** y asistente de primer arranque; instalador guiado **UEFI y BIOS clásico**, con cifrado de disco (LUKS) opcional.
- **Reportar un problema** (SUPER → «Reportar un problema»): crea un informe sin contraseñas ni nombres de Wi-Fi y, **solo si tú lo aceptas**, lo envía a los desarrolladores.

## Descargar y probar
Descarga la última versión en [**Releases**](https://github.com/maikolrlxd-blip/hyprarch/releases) (la ISO va en 2 partes por el límite de 2 GB de GitHub; las instrucciones para juntarlas y el `SHA256SUMS.txt` están ahí).
También puedes compilarla tú mismo (abajo) o bajar el artefacto `hyprarch-iso-public` de **Actions → Build ISO**. Grábala en un USB con [Rufus](https://rufus.ie), [Ventoy](https://www.ventoy.net)
o USBImager (se borra el USB) y arranca en modo UEFI. Guía paso a paso: [`docs/GUIA-PROBADORES.md`](docs/GUIA-PROBADORES.md).

La edición pública **no incluye ninguna IA**: al primer uso, `hyprarch-ai` instala la que elijas (con tu cuenta; hyprarch no guarda credenciales).

## Compilar
```bash
sudo ./build.sh                      # edición pública (por defecto)
HYPRARCH_EDITION=personal sudo ./build.sh   # incluye Claude Code: solo para uso propio, no se redistribuye
```
La ISO queda en `out/`. Con GitHub Actions: sube el repo, ejecuta **Build ISO** y baja el artefacto.

## Privacidad
- No hay telemetría. Lo único que sale del equipo es un informe **si lo envías tú**, tras pedirte permiso: descripción, datos del equipo
  (sin nombre de usuario, equipo, MAC ni IP; sin redes Wi-Fi ni contraseñas), registros y una captura **solo si la incluyes**.
- Puedes leer el informe antes de enviarlo o copiarlo a un USB en su lugar.

## Contribuir y seguridad
- Probar y reportar fallos es lo más valioso ahora: [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Vulnerabilidades: [`SECURITY.md`](SECURITY.md) (no las publiques en una *issue*).

## Licencia
**Código visible, uso no comercial** ([PolyForm Noncommercial 1.0.0](LICENSE)): puedes usarlo, estudiarlo, modificarlo y compartirlo
sin ánimo de lucro; el uso comercial requiere un acuerdo con el autor. No es «código abierto» en el sentido estricto de la OSI.
El software de terceros (Arch Linux, Hyprland, etc.) conserva su propia licencia. Detalles y marca («hyprarch», «Hyro»):
[`LICENSING.md`](LICENSING.md). hyprarch no está afiliado a Anthropic, OpenAI, Google ni a Arch Linux.

---

## English summary
**hyprarch** is an Arch Linux + Hyprland operating system built as a home for your AI: a chat "island" with the AI of your choice,
a safe JSON API (`hyprarch-api`) so an AI can control the desktop, real "modes" (gamer, cinema, study, work), a light profile for modest
PCs, a UEFI/BIOS installer with optional disk encryption, and a privacy-first bug reporter (sent only if you agree).
**Beta**: try it live from USB or in a VM first — the installer erases the disk you pick. The public edition ships no AI; you install
the one you want on first use. Source-available under **PolyForm Noncommercial 1.0.0** (free for non-commercial use; commercial use
needs an agreement). Not "open source" in the OSI sense. Build with `sudo ./build.sh` or the *Build ISO* GitHub Action.
