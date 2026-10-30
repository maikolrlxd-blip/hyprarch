# Gorro Nubecita: accesorio UGC de prueba (v01)

Encargo de Maikol (30/10): «Solo para probar, crea un accesorio nuevo, lo que más creas que va a vender». Después: «piensa en qué tan bien se ve el tamaño».

## Lo que falta o puede fallar

- **No está subido ni publicado.** Publicar en el Marketplace lo tiene que hacer Maikol desde su cuenta, porque se paga con Robux y pide verificaciones (ver abajo).
- **Prueba en Studio pendiente.** Falta comprobarlo con la herramienta de ajuste de accesorios (Accessory Fitting Tool) en varios tipos de cuerpo.
- **Solo tipo de cuerpo Classic** (AvatarPartScaleType = Classic, caja máxima 3 × 4 × 3). Mide 2,0 de ancho, así que no entra en las cajas Rthro (Normal 1,87 y Slender 1,78). Puesto en un cuerpo Rthro, Roblox lo escala solo.
- **14 islas** (piezas cerradas dentro de una sola malla, de los vóxeles). Una malla es lo que pide Roblox. Si el validador se queja, habría que unirlas.
- Había **2 aristas no-manifold**: dos vóxeles que se tocaban solo por una arista. El script las separa y ahora no queda ninguna arista abierta ni no-manifold.

## Qué es

- La **mascota nube amable del juego** (`mascotas-enemigos-v01/nube`), fija en la pose neutra y sentada en la cabeza como un gorro. Lo kawaii y lo de cabeza es lo que más se vende, y además anuncia el juego.
- **Tamaño 2,0 × 1,05 × 1,11 studs** (ancho × alto × fondo).
  - En `GorroNubecita-tamanos.jpg` se compara 1,6 / 2,0 / 2,4 / 2,8 sobre un avatar R15 de bloques: cabeza 1,2, torso 2 × 2 × 1, brazos y piernas 1 × 2 × 1.
  - Elegido **2,0, el ancho del torso (1,67 cabezas)**.
  - La v1 medía 2,8, es decir 2,3 cabezas: parecía un paraguas y en la foto de perfil la cara del avatar quedaba diminuta.
  - Con 1,6 la cara de la nube casi no se lee.
- **1.250 triángulos** (el límite de un Hat es 4.000), **textura de 1024 × 1024** y una sola malla.
- **HatAttachment** en el centro de la base. El gorro se hunde 0,1 studs en la cabeza para que no quede una rendija.

## Archivos

| Archivo | Qué es |
|---|---|
| `GorroNubecita.fbx` | Malla con la textura incrustada. Escala 0.01 y `axis_forward` Z, así la cara mira al frente del avatar. |
| `GorroNubecita_textura_1024.png` | Textura (la misma que la de la mascota). |
| `GorroNubecita.blend` | Fuente. |
| `GorroNubecita-tamanos.jpg` | Comparativa de tamaños. |
| `GorroNubecita-avatar.jpg` | Avatar de 3/4. |
| `GorroNubecita-cabeza.jpg` | Encuadre de foto de perfil. |
| `GorroNubecita-34.jpg` | Foto tipo catálogo. |
| `datos.json` | Medidas y comprobaciones. |

Script: `tools/build_ugc_gorro_nube.py`. Para cambiar el ancho, `GORRO_ANCHO=2.4 blender -b --factory-startup --python-exit-code 1 -P build_ugc_gorro_nube.py`.

## Cómo se publica (lo hace Maikol)

1. **Requisitos de la cuenta:**
   - verificación de identidad (o cuenta de padre o madre vinculada);
   - verificación en 2 pasos;
   - según Roblox, puede pedir Premium.
2. **En Studio:**
   - Avatar → Importar 3D → `GorroNubecita.fbx`;
   - Avatar → Accessory Fitting Tool → tipo **Hat**, tipo de cuerpo Classic;
   - comprobar que la cara mira al frente y que queda apoyado en la cabeza;
   - material Plastic.
3. **Subir:** clic derecho en el accesorio → «Guardar en Roblox» / subir como accesorio. Se paga una **cuota de subida** en Robux y se pasa moderación.
4. **Publicar a la venta** desde el Creator Hub. Se paga un **adelanto de publicación** en Robux y se fija el precio.

Los importes cambian, así que hay que mirarlos en el Creator Hub antes de pagar.
