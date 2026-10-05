# phone-mcp — controlar tu celular Android con Claude

Hay dos modos:

| Modo | Necesita | Para quién |
|---|---|---|
| **App Android + relay** (nuevo) | Instalar la app en el celular y un servidor relay | Cualquier persona, sin cable ni ADB |
| **ADB** | Cable/Wi-Fi debug + `adb` en la PC | Desarrolladores |

## Sin PC (solo el celular)

1. Instalá el APK (GitHub → Actions → *Build Android APK* → `phone-mcp-apk`).
2. Abrila, activá la accesibilidad y pegá tu API key de Anthropic.
3. Escribí qué querés ("abre Spotify y pon música tranquila") y tocá **Ejecutar**.

El asistente corre en el propio celular: ve la pantalla, toca y escribe en bucle (máx. 40 pasos por tarea), pide confirmación antes de enviar/pagar/borrar y se corta con **DETENER**. Cada paso envía capturas/texto de pantalla a la API de Anthropic y consume tu saldo. La API key se guarda en el almacenamiento privado de la app (sin cifrado adicional).

## Con PC (opcional, para usar Claude Code)


**Una vez:**
1. Instalá el APK (GitHub → Actions → *Build Android APK* → `phone-mcp-apk`) y activá su permiso de accesibilidad.

**Cada vez:**
1. En la PC: `python3 phone/start.py` → muestra un QR (y registra la herramienta en Claude Code por vos).
2. En el celular: escaneá el QR con la cámara, tocá el enlace. Listo, queda conectado.
3. Pedile cosas a Claude Code.

Alcance: con [`cloudflared`](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) instalado funciona desde cualquier red (HTTPS gratis; el QR cambia en cada inicio). Sin él, funciona solo con la PC y el celular en el mismo Wi-Fi (tráfico sin cifrar dentro de tu red).

Seguridad: la clave se guarda en `~/.phone-mcp.json` (solo tu usuario); mientras está activo hay una notificación permanente con botón **DETENER**; borrar ese archivo revoca el acceso. Requiere Android 11+. `phone_text` acepta tildes y emojis.

> Estado: la app compila en CI, pero aún no se probó en un celular real.

## Modo ADB

Servidor MCP (sin dependencias, solo Python 3 + `adb`) que le da a Claude Code los mismos "ojos y manos" sobre tu celular que tiene sobre la PC: ver la pantalla, tocar, deslizar, escribir y abrir apps.

## Requisitos
- PC con Claude Code, `python3` y `adb` (`sudo pacman -S android-tools`). Opcional: `python-pillow` para capturas más livianas.
- Celular **Android** con *Opciones de desarrollador → Depuración USB* activada. (iPhone no permite esto.)

## Conectar
USB: enchufá el cable y aceptá la huella RSA en el celular. `adb devices` debe mostrarlo.

Wi-Fi (sin cable, Android 11+): *Depuración inalámbrica* → "Vincular con código":
```
adb pair IP:PUERTO_PAIRING     # pide el código de 6 dígitos
adb connect IP:PUERTO
```

## Registrar en Claude Code
```
claude mcp add phone -- python3 /ruta/a/hyprarch/phone/phone_mcp.py
```
Con varios dispositivos: `ANDROID_SERIAL=<serial>` o el parámetro `serial` de cada herramienta.

## Herramientas
`phone_devices` · `phone_screenshot` · `phone_ui` (elementos + coordenadas, más barato que una captura) · `phone_tap` · `phone_tap_text` · `phone_swipe` · `phone_scroll` · `phone_text` · `phone_key` · `phone_launch` · `phone_packages` · `phone_open_url`

## Límites y seguridad
- `phone_text` solo envía ASCII (limitación de `adb input text`).
- Apps con `FLAG_SECURE` (bancos, etc.) devuelven captura negra; `phone_ui` puede seguir funcionando.
- Quien controla el MCP controla el celular: usá solo dispositivos propios y desactivá la depuración al terminar.
