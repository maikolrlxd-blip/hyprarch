# La Lamentadora v0.1 — estado (trabajo de Codex, revisado por Claude)

Codex hizo este jefe el 2026-10-22 con su propio script, `fuentes/build_boss.py`, en Blender 5.2.2. Maikol pidió aprovecharlo como base del jefe "La Lamentadora": una mujer larga y deformada, sin gore. Codex ya no está disponible.

## Qué falla
- **La cara es de caricatura, no da miedo.** La boca es un rectángulo enorme abierto con pocos dientes sueltos y la nariz es una cuña plana. Solo se ve un ojo, una almendra blanca con un punto. Parece una máscara más que una cara.
- **El pelo son tablas:** mechones rectangulares rígidos, sin volumen.
- **Hombros raros:** las mangas son dos conchas cuadradas enormes que se leen como hombreras.
- **Clavículas y cuello:** se ven como un alambre blanco pegado al pecho.
- **Triángulos:** 3924, por encima de los 3000 del presupuesto del zombi. Hay un LOD1 de 2564.
- **No probado en Roblox Studio:**
  - el rig tiene nombres R15 más huesos auxiliares de tela y pelo (38 en total), y Codex no lo declaró compatible;
  - el GLB sale a otra escala.
- **Render de escala:** el maniquí R15 queda pegado a ella y tapa su brazo izquierdo.

## Qué está bien y se aprovecha
- **Silueta:** es alta (9,3 studs, casi el doble que un R15), con pelo largo negro, vestido azul verdoso con el bajo roto y manos con garras. Se lee como una mujer de terror sin gore.
- **Clips:** Reposo 3,0 s (bucle), Acechar 1,6 s (bucle), Zarpazo 1,13 s, Lamento 2,4 s, Impacto 0,67 s y Caer 2,0 s, a 30 fps.
- **Texturas pintadas:** rostro y cuerpo.
- **Exportación:**
  - FBX con `global_scale=0.01` y ejes -Z/Y, igual que el resto del encargo;
  - FBX estático y con rig;
  - un FBX por clip.

## Archivos
- En git:
  - FBX: `LaLamentadora_Rig.fbx`, `_Estatico.fbx`, `_LOD1_Estatico.fbx` y `clips/`;
  - GLB;
  - `texturas/`, `previews/`, `fuentes/`, `qa/build-01.log` y `datos.json`.
- **Fuera de git:** `LaLamentadora.blend`. La carpeta pasa de 50 MB, así que el .blend está guardado en `C:\Users\maiko\Backups\codex-respaldo\la-lamentadora-v01\`.

## Siguiente paso propuesto
Usarla como base y rehacer, con el mismo nivel de realismo que la mujer zombi:
1. la cara: boca entreabierta, ojos hundidos y piel con volumen;
2. el pelo en mechones con volumen;
3. los hombros.

También hay que bajar a unos 3000 triángulos. Va después del mapa y de la mujer zombi; antes conviene confirmarlo con Maikol.
