# phone-mcp — controlar tu celular Android con Claude

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
