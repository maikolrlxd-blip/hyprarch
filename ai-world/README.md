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

## App Android

El APK tiene un menu de inicio con dos modos:

**Jugar en el celular (independiente).** El mundo 3D y las IAs corren en el telefono; no necesitas la PC. Pulsa **Ajustes** para elegir proveedor, modelo y API key de cada IA (se guardan en el almacenamiento privado de la app). Sin API key funciona con el proveedor "Simulado". Las llamadas a los modelos salen del telefono directamente (necesita internet). Ollama local solo sirve si pones en "URL base" la IP de tu PC en la red.

**Conectar con mi PC.** La PC corre las IAs y el celular ve el mismo mundo en tiempo real y puede chatear:

1. En la app de PC pulsa **Celular**: se levanta un servidor en tu red local y aparece un QR.
2. En el menu del telefono (misma Wi-Fi) pulsa **Conectar con mi PC -> Escanear QR** (o pega el enlace).
3. "Continuar con mi ultima PC" reconecta sin escanear. "Atras" vuelve al menu.

- Seguridad: el enlace de la PC lleva un token secreto generado en cada sesion; sin el, el servidor rechaza la conexion. "Desactivar acceso" lo apaga. No compartas el enlace.
- Fuera de casa: usa una VPN de malla como Tailscale en ambos equipos y conecta con la IP de Tailscale de la PC.
- Internamente hay dos WebView: el local (menu + modo independiente, con puente nativo para las llamadas HTTP y el QR) y el remoto (la pagina que sirve la PC, sin puente).
- Compilar el APK a mano: `npm ci` en `ai-world/`, luego `cd android && ./gradlew assembleRelease` (JDK 17 y Android SDK 34). El mundo 3D se copia dentro del APK automaticamente.

## Proveedores soportados

Anthropic (Claude), OpenAI, Google Gemini, OpenRouter, Ollama (local), cualquier API compatible con OpenAI (URL propia) y Simulado.
Cada IA puede usar un proveedor distinto en la misma sala.

## Como funciona

- Cada turno (cada N segundos, rotando entre IAs) el proceso principal le entrega a una IA lo que percibe: su posicion, quien esta cerca y la conversacion reciente.
- El modelo responde con JSON `{say, action, target}`; el mundo lo convierte en voz + movimiento.
- Las API keys viven en el proceso principal (`userData/ai-world.json`, permisos 600); la interfaz nunca las ve.

## Estructura

- `src/shared/` — el "cerebro" de las IAs (proveedores, prompts, parseo): ES modules que usan tanto la PC como el celular
- `src/main/` — ventana de Electron, almacenamiento, servidor LAN + WebSocket (`netserver.js`)
- `android/` — app Android (menu animado en `web/`, puente nativo en `MainActivity.java`)
- `src/renderer/` (`standalone.js` = modo independiente del celular) — escena 3D (`world.js`), cuerpos y animaciones (`avatar.js`), UI y bucle de turnos (`app.js`: mismo codigo en modo anfitrion dentro de Electron y modo cliente en el navegador del celular)

## Ideas siguientes

Voz (TTS) por personaje, memoria a largo plazo, objetos con los que interactuar, modelos 3D importables (glTF), mas salas.
