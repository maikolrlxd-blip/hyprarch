# Icono y miniaturas v01 — estado (30/10/2026, Coordinador)
Son el icono (512 × 512) y dos miniaturas (1920 × 1080) del juego, montados en Blender con el arte del proyecto:
- un avatar de bloques con las alas avanzadas v0.2;
- el mapa v01 y la Pradera de Codex detrás (solo se lee su archivo);
- los huevos alados v03 y mascotas (nube, meteorito, grifo).

El título va en Arial Black, amarillo con sombra oscura. **Son PROVISIONALES y no se han subido a Roblox.**

## Fallos y límites (primero)
- **El avatar no luce**: las alas avanzadas se ven de canto y salen como una mancha oscura, y no se le ve la cara. Hace falta otra pose o cámara: de frente, con las alas abiertas hacia la cámara.
- **El «+1» del icono es pequeño**: para un icono de Roblox debería ocupar casi media imagen.
- **El avatar es un muñeco de bloques genérico**, no un avatar de Roblox de verdad.
- **Arial Black es una fuente del sistema (Windows)**: sirve para una imagen, pero si se quiere un estilo propio habrá que elegir fuente.
- Son renders de Blender: la luz y los materiales no son los de Roblox.

## Qué hay
| Archivo | Tamaño | Qué muestra |
|---|---|---|
| `Icono-512.jpg` | 512 × 512 | el avatar volando sobre la Pradera, con mascotas, un aro y «+1» |
| `Miniatura-1-vuelo.jpg` | 1920 × 1080 | el vuelo sobre la Pradera hacia el Mar de Nubes, con el título «+1 DE LANZAMIENTO / POR SEGUNDO» |
| `Miniatura-2-huevos.jpg` | 1920 × 1080 | los huevos alados v03 en el Mar de Nubes, con «HUEVOS ALADOS / MASCOTAS MÍTICAS» |

## Cómo regenerar
`blender -b --factory-startup --python-exit-code 1 -P tools/icono_miniaturas.py`
