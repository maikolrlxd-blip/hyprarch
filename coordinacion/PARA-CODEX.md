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

## 3. GIRO DE DISEÑO (léelo): Slime Rush v2
El usuario cambió de idea: **mapa grande generado por semilla**, distinto en cada partida (como Minecraft). Se explora, se recolectan recursos, hay **cofres ocultos**, **slimes y accesorios raros**, **robo** entre jugadores (incluido acampar en la meta) y una **carrera final a la meta** con bonos de llegada. Lo lees completo en `slime-rush-juego/DISENO-v2.md` (propuesta, pendiente de que el usuario responda 5 decisiones). El mapa fijo y la lava anteriores quedan en pausa.

**Antes de programar nada que dependa del diseño, espera a que esté aprobado** (tarea del humano en el Taller).

## 4. Tus tareas (rol: ingeniero) — plan `taller-ia/planes/slime-rush-v2.json`
1. **Terreno por voxels desde la semilla** en Studio (rendimiento y Streaming): ya se puede preparar; mide tiempo de generación y FPS.
2. **Robo y depósito en la meta** y **cofres/nodos de recurso**: *después* de la aprobación del diseño y del kit de arte.
3. **Rayo y Miga: correcciones de forma** (Blender).
4. **Prueba con DOS clientes** al final (aquí sí 2 Studio/clientes; ciérralos al terminar).

## 5. Qué hacen los demás (no lo repitas)
Lee `coordinacion/BITACORA.md`: ahí está quién hizo qué. Resumen: **Opus** (Blender) hace árboles, kit modular, biomas, slimes/accesorios raros; **Claude** (director) hace el diseño, el generador de mundo y las reglas de partida como módulos puros con pruebas. **Yo no he hecho ninguna de tus tareas.**
Los archivos originales se perdieron con el reinicio del PC; si el usuario recupera copias, úsalas.

## 6. Reglas de siempre
Español, directo y corto. Verifica en el motor, no supongas ("no probado" si no lo probaste). Nada de claves en chat. No publicar ni tocar datos de producción sin permiso. Si te bloqueas, no esquives: pregunta. Si llegas a tu límite de uso, deja en la tarea hasta dónde llegaste.
