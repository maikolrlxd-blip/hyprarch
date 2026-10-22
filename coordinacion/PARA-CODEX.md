# Mensaje para Codex (de Claude, el director del equipo)

> Léelo al empezar. Lo escribió el director desde la nube: **no puedo ver tu pantalla ni tu PC**, así que este archivo y el Taller IA son nuestro canal. Responde en `coordinacion/DE-CODEX.md` (o por el Taller, tarea por tarea).

## 1. Regla del usuario sobre Roblox Studio (importante)
**No abras tantos Roblox Studio.** Quédate con **el o los que de verdad te hagan falta** (normalmente 1; 2 solo si pruebas dos clientes a la vez).
- Antes de abrir uno nuevo, llama a `list_roblox_studios` y **reutiliza** el que ya tengas.
- Un Studio por lugar/archivo de trabajo. No abras otro "por si acaso" ni uno por cada prueba.
- Si dejaste Studios sobrantes **tuyos** y sin cambios, ciérralos. Si tienen cambios sin guardar o son del usuario: guarda copia y **pregunta**, no cierres a ciegas.
- Registra en la nota de tu tarea cuántos Studio usas y por qué.

## 2. Modelos: todo por Blender
Todos los modelos (slimes, árboles, mapa) se hacen y exportan **con Blender**. Si tocas un modelo, trabájalo en Blender y entrega .blend + .glb/.fbx.

## 3. Tus tareas (rol: ingeniero; mira `taller-ia/planes/slime-rush.json`)
1. **Rayo y Miga: correcciones de forma** (Blender). Rayo más alto y alas más grandes y pegadas; Miga: bajar la masa frontal que tapa la boca. Render antes/después.
2. **Integrar UN árbol en Studio y probar** (cuando llegue `slime-rush-arte/arboles-v05/`): escala vs figura de 6 studs, colisión simple solo en el tronco, follaje sin colisión, densidad menor, pasos despejados. Captura real del motor.
3. **Cámara del lobby / Results** (superficie azul): encuentra la causa, no la supongas.
4. **Prueba con DOS clientes** (disputa de cristal, monedas independientes, entrada tardía). Aquí sí 2 Studio/clientes; ciérralos al terminar.

## 4. Qué está pasando mientras no tienes uso
- Dos trabajadores Opus (con Blender) entregan en el repo: **árboles 0.5.0** en `slime-rush-arte/arboles-v05/` y **el mapa nuevo** (el anterior era "feísimo") en `slime-rush-arte/mapa-v02/`. Revísalos antes de integrarlos.
- Los archivos originales (.rbxl, .blend) se perdieron con el reinicio del PC. Si el usuario recupera copias, úsalas.

## 5. Reglas de siempre
Español, directo y corto. Verifica en el motor, no supongas ("no probado" si no lo probaste). Nada de claves en chat. No publicar ni tocar datos de producción sin permiso. Si te bloqueas, no esquives: pregunta. Si llegas a tu límite de uso, deja en la tarea hasta dónde llegaste.
