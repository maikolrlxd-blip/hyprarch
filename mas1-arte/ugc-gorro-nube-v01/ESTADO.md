# Gorro Nubecita: accesorio UGC de prueba (v01)

Encargo de Maikol (30/10): «Solo para probar, crea un accesorio nuevo, lo que más creas que va a vender». Después pidió: «piensa en qué tan bien se ve el tamaño». Y eligió: «el de 1,6 es el que mejor se ve».

## Lo que falta o puede fallar

- **No está publicado ni a la venta.** Publicarlo lo hace Maikol desde su cuenta: se paga en Robux y pide verificaciones (ver abajo).
- **El validador de UGC de Studio da 0 errores y 2 avisos** (31/10, tras el arreglo que pidió Maikol). Los avisos no bloquean la subida:
  1. Textura «poco compleja». Es el estilo vóxel de colores planos. Ya lleva una oclusión suave horneada; meterle ruido la afearía.
  2. Textura «baja, de 1024». Se subió una de 2048, pero Roblox la deja en 1024 al subirla, así que con TextureID no se puede quitar.
- **Arreglados el 31/10 los avisos de geometría** (triángulos degenerados y no-manifold):
  - La malla era 14 piezas que se cortaban: cuerpo, nubecitas laterales y cajitas de la cara.
  - Ahora es **una sola piel de vóxeles cerrada**: 1.796 triángulos, 0 aristas o vértices no-manifold y ningún triángulo de área cero.
  - La cara (ojos con brillo, mejillas y boca) va **horneada en la textura**, que ahora tiene UV propias. Antes eran cajitas que sobresalían 0,05 studs; se nota muy poco.
- **Solo se ha probado con el avatar R15 de bloques por defecto** (cabeza de 1,16). Roblox escala el gorro según la cabeza, así que 1,6 queda en 1,55 de ancho. Falta probarlo con cuerpos Rthro y cabezas dinámicas.
- **La luz de cada juego cambia mucho cómo se ve.** En la place de prueba, sin el sol de frente, la nube salía gris, y un cubo blanco de referencia también. Por eso se aclaró la textura.

## Qué es

- La **mascota nube amable del juego** (`mascotas-enemigos-v01/nube`), fija y sentada en la cabeza como un gorro.
- **Mide 1,6 × 0,84 × 0,84 studs** (ancho × alto × fondo; el fondo bajó de 0,89 al hornear la cara en la textura).
  - Es el tamaño que eligió Maikol de la comparativa `GorroNubecita-tamanos.jpg` (1,6 / 2,0 / 2,4 / 2,8).
  - Cabe en la caja Hat de todos los tipos de cuerpo: Classic 3 × 4 × 3, Normal 1,87 × 2,5 × 1,87 y Slender 1,78 × 2,5 × 1,78.
- **Malla:** 1.796 triángulos (el límite es 4.000), una sola piel cerrada.
- **HatAttachment** centrada en la base. El gorro se hunde 0,1 studs en la cabeza para que no quede una rendija.
- **Textura (`GorroNubecita_textura_2048.png`):** el color de la mascota con los blancos y lavandas aclarados un 40 % (la cara no), horneado sobre la piel nueva y con una oclusión suave en los huecos.

## Probado en Studio (30/10)

- **Fallo encontrado y arreglado: el FBX entraba con la cara mirando a la nuca.**
  - Con `axis_forward='Z'`, el 3D Importer pone el +Y de Blender en el +Z de Roblox, y los personajes miran a −Z.
  - El script ahora gira el FBX 180° antes de exportar. El `.blend` no cambia.
  - Comprobado después: en una malla **sin huesos** el `axis_forward` no cambia nada, ni con `bake_space_transform`. Solo funciona girar la malla.
  - Las piezas **con huesos** tenían otro problema (esqueleto girado 90°) y otra regla. Está todo en `pruebas-studio/2026-10-30-ejes/LEEME.md`.
- **La escala es correcta.** Lo que mide 1,6 en Blender entra como 1,6 studs.
- **Puesto en un avatar R15** con `Humanoid:AddAccessory`: queda asentado en la cabeza y la cara mira al frente (`GorroNubecita-studio.jpg`).
- **Validación de UGC como Hat:**
  - al principio dio 1 error: `Massless` tenía que ser `false`;
  - arreglado, ahora da 0 errores y los 4 avisos de arriba.

## Archivos

| Archivo | Qué es |
|---|---|
| `GorroNubecita-accesorio.rbxm` | **El accesorio listo para subir.** Es un Accessory «GorroNubecita» de tipo Hat. Su Handle es un MeshPart con la HatAttachment, material Plastic y `Massless = false`. Usa la malla y la textura ya subidas. |
| `GorroNubecita.fbx` | Malla con la textura incrustada. Escala 0.01, `axis_forward` Z y girada 180°. |
| `GorroNubecita_textura_2048.png` | Textura horneada (color aclarado, cara y oclusión suave). |
| `GorroNubecita.blend` | Fuente, con la cara hacia +Y como el resto del arte. |
| `GorroNubecita-tamanos.jpg` | Comparativa de tamaños; el elegido va en azul. |
| `GorroNubecita-avatar.jpg` | Avatar de 3/4. |
| `GorroNubecita-cabeza.jpg` | Encuadre de foto de perfil. |
| `GorroNubecita-34.jpg` | Foto tipo catálogo. |
| `GorroNubecita-studio.jpg` | Captura en Studio. |
| `datos.json` | Medidas y comprobaciones. |

Script: `tools/build_ugc_gorro_nube.py`.

- Para cambiar el ancho: `GORRO_ANCHO=1.6`.
- Para cambiar cuánto se aclara la textura: `GORRO_ACLARAR=0.4`.

## Recursos subidos a la cuenta de Maikol

Son privados y no están publicados.

- **Finales (31/10, piel de una pieza):**
  - malla `rbxassetid://105089157766338`;
  - textura horneada `rbxassetid://91926435167786`.
- **Pruebas descartadas:**
  - malla de 14 piezas `rbxassetid://108856740245372` y su textura aclarada `rbxassetid://131716664749821`;
  - malla de 2,0 con la cara hacia atrás `rbxassetid://120611883318936`;
  - textura sin aclarar `rbxassetid://101145254390945`;
  - malla de 1,6 sin girar.

## Cómo se publica (lo hace Maikol)

1. **Requisitos de la cuenta:**
   - verificación de identidad (o cuenta de padre o madre vinculada);
   - verificación en 2 pasos;
   - según Roblox, puede pedir Premium.
2. **En Studio:**
   - arrastrar `GorroNubecita-accesorio.rbxm` a la ventana para insertarlo;
   - seleccionar el accesorio → pestaña Avatar → **Validación…** → Hat → «Ejecutar validación»;
   - comprobar que da 0 errores.
3. **Subir:** clic derecho en el accesorio → Guardar / Exportar → **Guardar en Roblox…** → tipo Hat, nombre y descripción. Se paga la **cuota de subida** en Robux y pasa moderación.
4. **Ponerlo a la venta** desde el Creator Hub. Se paga el **adelanto de publicación** en Robux y se fija el precio.

Los importes cambian, así que hay que mirarlos en el Creator Hub antes de pagar.
