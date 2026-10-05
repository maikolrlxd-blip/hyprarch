# phone-mcp — controlar tu celular Android con Claude

Hay dos modos:

| Modo | Necesita | Para quién |
|---|---|---|
| **App Android + relay** (nuevo) | Instalar la app en el celular y un servidor relay | Cualquier persona, sin cable ni ADB |
| **ADB** | Cable/Wi-Fi debug + `adb` en la PC | Desarrolladores |

## Modo app Android + relay

```
Claude (PC) → phone_mcp.py ──HTTPS──▶ relay.py ◀──WebSocket── App Android (accesibilidad)
```
El celular se conecta *hacia afuera*: no hay que abrir puertos ni usar cable.

1. **Relay** (un VPS o tu PC; detrás de HTTPS en producción): `pip install aiohttp && python3 phone/server/relay.py --port 8765`
2. **APK**: GitHub → Actions → *Build Android APK* → artefacto `phone-mcp-apk`. Instalarlo (permitir orígenes desconocidos).
3. En la app: activar el servicio de accesibilidad, escribir la URL del relay, **Conectar**.
4. **Copiar comando para Claude Code** y pegarlo en la PC (ajustá la ruta de `phone_mcp.py`).

Seguridad: la clave la genera el celular (256 bits) y el relay solo guarda su hash en memoria; mientras está activo hay una notificación permanente con botón **DETENER**; "Generar clave nueva" revoca el acceso anterior. Usá siempre HTTPS: sin él la clave viaja en claro.
Ventaja sobre ADB: `phone_text` acepta tildes y emojis. Requiere Android 11+.

> Estado: el relay y el puente están probados de punta a punta con un celular simulado. El código de la app **aún no se compiló ni probó en un dispositivo real**.

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
