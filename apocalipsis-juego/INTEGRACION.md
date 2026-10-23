# Cómo entran a Luto el mapa y los zombis hechos en Blender
Estado (2026-10-23): el servidor `server/Partida.server.lua` **ya usa** lo que encuentre en `ServerStorage.LUTO_Plantillas` y, si falta algo, cae a sustitutos provisionales (arena de bloques, rigs R15 verdes). Falta que el mapa y el zombi terminen y se importen.

## Qué hay que dejar en `ServerStorage > LUTO_Plantillas` (Folder)
| Nombre | Qué es | Reglas |
|---|---|---|
| `Mapa` | Model con todas las piezas del mapa (MeshParts de Blender) | `Anchored = true`; suelo, muros y edificios con `CanCollide = true` (si la malla es compleja, añadir cajas de colisión simples e invisibles: `CollisionFidelity = Box`); sin scripts. Marcadores (Parts invisibles, `CanCollide=false`): `SpawnJugadores` (1 Part), carpeta `SpawnZombis` (N Parts repartidas por el borde y las calles), `Tienda_municion` y `Tienda_curar` (Parts donde irá cada tienda) |
| `Zombi_Mujer` | Model R15 de la mujer zombi | Piezas con nombres R15 (`Head`, `UpperTorso`, `LowerTorso`, `LeftUpperArm`…, `HumanoidRootPart`) y `Humanoid` (si no lo trae, el servidor lo añade); texturas pintadas por pieza |
| `Jefe_lamentadora` | Model R15 de La Lamentadora (larga, deformada, sin gore) | igual que el zombi; se escala sola solo si no hay plantilla |
| `Jefe_alta` | Segundo tipo de jefe | igual |
El servidor clona la plantilla, **respeta su textura pintada** (no la recolorea), pone vida/velocidad/daño de la ronda y la mueve a un punto de `SpawnZombis`.

## Cómo se importa (los FBX de `apocalipsis-arte/`)
**Opción A (recomendada): Studio, 3D Importer** (Inicio > Importar 3D, o Asset Manager > Bulk Import). Los FBX de Blender ya salen a escala 1 stud (`global_scale=0.01`, comprobada con la roca de Codex). Importa con tu sesión de Roblox iniciada: **las mallas y texturas se suben a TU cuenta** (queda en tu inventario/Creaciones; es gratis). Luego se arrastra el resultado a `LUTO_Plantillas`, se marcan los marcadores y se guarda el place (.rbxl) en una copia. Requiere a alguien frente a Studio (la sesión del PC con el permiso de pantalla, o tú).
**Opción B: Open Cloud** (subida por API sin abrir Studio): hace falta una clave de API creada por Maikol en create.roblox.com (permiso de escritura de activos). La clave NUNCA se pega en un chat: se guarda en una variable de entorno del PC. Más trabajo inicial; permite automatizarlo todo.
Ninguna de las dos se ha probado todavía con nuestros FBX (el estado de `apocalipsis-arte/ESTADO.md` lo dice: "nada probado en Studio con estos FBX").

## Orden de trabajo
1. Terminar el **mapa** (apariencia) y la **mujer zombi** (crítica incluida) en Blender → quien lo hace: Coordinador.
2. Importar ambos en un place de prueba, armar `LUTO_Plantillas` y los marcadores → sesión del PC en Studio.
3. Play con Rojo (`apocalipsis-juego/default.project.json`) y ajustar escala, colisiones y puntos de aparición.
4. Después: armas como `Tool` con sus clips (requiere importar las animaciones: otra tarea de Studio).
