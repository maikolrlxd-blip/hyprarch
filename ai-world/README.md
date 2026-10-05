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

## Proveedores soportados

Anthropic (Claude), OpenAI, Google Gemini, OpenRouter, Ollama (local), cualquier API compatible con OpenAI (URL propia) y Simulado.
Cada IA puede usar un proveedor distinto en la misma sala.

## Como funciona

- Cada turno (cada N segundos, rotando entre IAs) el proceso principal le entrega a una IA lo que percibe: su posicion, quien esta cerca y la conversacion reciente.
- El modelo responde con JSON `{say, action, target}`; el mundo lo convierte en voz + movimiento.
- Las API keys viven en el proceso principal (`userData/ai-world.json`, permisos 600); la interfaz nunca las ve.

## Estructura

- `src/main/` — ventana, almacenamiento, proveedores (`providers.js`), prompts y parseo (`brain.js`)
- `src/renderer/` — escena 3D (`world.js`), cuerpos y animaciones (`avatar.js`), UI y bucle de turnos (`app.js`)

## Ideas siguientes

Voz (TTS) por personaje, memoria a largo plazo, objetos con los que interactuar, modelos 3D importables (glTF), mas salas.
