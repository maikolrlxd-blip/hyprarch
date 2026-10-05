# AI World

App de escritorio (Electron + Three.js) con una sala 3D donde varias IAs conviven, cada una con su cuerpo: caminan, saludan, bailan, saltan y hablan con burbujas de dialogo. Tu tambien puedes hablarles desde el panel lateral.

## Uso

```bash
cd ai-world
npm install
npm start      # abre la app
npm test       # tests de la logica de los cerebros / proveedores
```

Al primer arranque hay 4 IAs con el proveedor **Simulado** (sin API), para ver el mundo funcionando. En **Ajustes** puedes cambiar proveedor, modelo, API key y personalidad de cada una, y agregar mas.

## Version Android (celular conectado a la PC)

La PC es el anfitrion: ahi viven las IAs y las API keys. El celular es un cliente que ve el mismo mundo 3D en tiempo real y puede chatear.

1. En la app de PC pulsa **Celular**: se levanta un servidor en tu red local y aparece un QR.
2. Con el celular en la **misma Wi-Fi**, escanea el QR (o abre la URL) en Chrome.
3. Opcional: menu de Chrome -> "Agregar a la pantalla de inicio" para abrirlo como app (pantalla completa).

- Seguridad: la URL lleva un token secreto generado en cada sesion; sin el, el servidor rechaza la conexion. "Desactivar acceso" lo apaga. No compartas el enlace.
- Fuera de casa: usa una VPN de malla como Tailscale en ambos equipos y abre la URL con la IP de Tailscale de la PC.
- Es una web app (PWA), no un APK nativo: no hace falta instalar nada en el celular. Si mas adelante quieres un APK, se puede envolver este mismo cliente con Capacitor.

## Proveedores soportados

Anthropic (Claude), OpenAI, Google Gemini, OpenRouter, Ollama (local), cualquier API compatible con OpenAI (URL propia) y Simulado.
Cada IA puede usar un proveedor distinto en la misma sala.

## Como funciona

- Cada turno (cada N segundos, rotando entre IAs) el proceso principal le entrega a una IA lo que percibe: su posicion, quien esta cerca y la conversacion reciente.
- El modelo responde con JSON `{say, action, target}`; el mundo lo convierte en voz + movimiento.
- Las API keys viven en el proceso principal (`userData/ai-world.json`, permisos 600); la interfaz nunca las ve.

## Estructura

- `src/main/` — ventana, almacenamiento, proveedores (`providers.js`), prompts y parseo (`brain.js`), servidor LAN + WebSocket (`netserver.js`)
- `src/renderer/` — escena 3D (`world.js`), cuerpos y animaciones (`avatar.js`), UI y bucle de turnos (`app.js`: mismo codigo en modo anfitrion dentro de Electron y modo cliente en el navegador del celular)

## Ideas siguientes

Voz (TTS) por personaje, memoria a largo plazo, objetos con los que interactuar, modelos 3D importables (glTF), mas salas.
