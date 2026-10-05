# AI World

App de escritorio (Electron + Three.js) con una sala 3D donde varias IAs conviven, cada una con su cuerpo: caminan, saludan, bailan, saltan y hablan con burbujas de dialogo. Tu tambien puedes hablarles desde el panel lateral.

## Instalar (apps listas)

Los instaladores se construyen en GitHub Actions (workflow **Build apps**). Al subir una etiqueta `v*` quedan en el Release; tambien puedes bajarlos de **Actions -> Build apps -> Artifacts**.

| Plataforma | Archivo | Como instalar |
|---|---|---|
| Windows | `AI-World-Setup-x.y.z.exe` | doble clic y seguir el instalador |
| Linux | `AI-World-x.y.z.AppImage` / `.deb` | `chmod +x` y ejecutar, o `sudo dpkg -i` |
| Android | `AI-World.apk` | abrir el APK en el telefono (permitir "instalar apps desconocidas") |

Windows puede mostrar "SmartScreen" y Android "app desconocida" porque las apps no estan firmadas con certificado de pago: es normal para apps propias.

## Uso desde el codigo

```bash
cd ai-world
npm install
npm start            # abre la app
npm test             # tests
npm run dist:linux   # genera AppImage + deb en dist/
npm run dist:win     # genera el instalador .exe (desde Windows)
```

Al primer arranque hay 4 IAs con el proveedor **Simulado** (sin API), para ver el mundo funcionando. En **Ajustes** puedes cambiar proveedor, modelo, API key y personalidad de cada una, y agregar mas.

## App Android (conectada a la PC)

La PC es el anfitrion: ahi viven las IAs y las API keys. El celular ve el mismo mundo 3D en tiempo real y puede chatear.

1. En la app de PC pulsa **Celular**: se levanta un servidor en tu red local y aparece un QR.
2. Abre la app **AI World** en el telefono (misma Wi-Fi) y pulsa **Escanear QR** (o pega el enlace).
3. La app recuerda la PC y reconecta sola. Con "Atras" puedes cambiar de PC.

- Seguridad: el enlace lleva un token secreto generado en cada sesion; sin el, el servidor rechaza la conexion. "Desactivar acceso" lo apaga. No compartas el enlace.
- Fuera de casa: usa una VPN de malla como Tailscale en ambos equipos y conecta con la IP de Tailscale de la PC.
- El APK es un WebView nativo (`android/`) que muestra el cliente que sirve la PC; tambien funciona abriendo el enlace directo en Chrome.
- Compilar el APK a mano: `cd android && ./gradlew assembleRelease` (necesita JDK 17 y Android SDK 34).

## Proveedores soportados

Anthropic (Claude), OpenAI, Google Gemini, OpenRouter, Ollama (local), cualquier API compatible con OpenAI (URL propia) y Simulado.
Cada IA puede usar un proveedor distinto en la misma sala.

## Como funciona

- Cada turno (cada N segundos, rotando entre IAs) el proceso principal le entrega a una IA lo que percibe: su posicion, quien esta cerca y la conversacion reciente.
- El modelo responde con JSON `{say, action, target}`; el mundo lo convierte en voz + movimiento.
- Las API keys viven en el proceso principal (`userData/ai-world.json`, permisos 600); la interfaz nunca las ve.

## Estructura

- `src/main/` — ventana, almacenamiento, proveedores (`providers.js`), prompts y parseo (`brain.js`), servidor LAN + WebSocket (`netserver.js`)
- `android/` — app nativa Android (WebView + escaner de QR)
- `src/renderer/` — escena 3D (`world.js`), cuerpos y animaciones (`avatar.js`), UI y bucle de turnos (`app.js`: mismo codigo en modo anfitrion dentro de Electron y modo cliente en el navegador del celular)

## Ideas siguientes

Voz (TTS) por personaje, memoria a largo plazo, objetos con los que interactuar, modelos 3D importables (glTF), mas salas.
