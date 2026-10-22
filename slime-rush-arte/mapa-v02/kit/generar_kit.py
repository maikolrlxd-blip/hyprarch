"""Slime Rush - genera el KIT MODULAR v0.2 en Blender (bpy 5.0.1).

Uso:
    python3 generar_kit.py            # construye, guarda kit_slime_v02.blend, exporta GLB/FBX y metricas
    python3 generar_kit.py --render   # ademas renderiza los catalogos con figura de 6 studs (Cycles CPU)

Salida en la misma carpeta. Reproducible: semillas fijas por pieza.
"""
import os
import sys
import json
import math
import bpy

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import kit_base as kb  # noqa: E402
import kit_piezas as kp  # noqa: E402
import render_comun as rc  # noqa: E402

VERSION = "0.2.0"
LOD_UMBRAL = 1500   # piezas con mas triangulos reciben un LOD1
LOD_RATIO = 0.4


def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def construir():
    kit = bpy.data.collections.new("KIT")
    bpy.context.scene.collection.children.link(kit)
    filas = {
        "naturaleza": [],
        "recursos_cofres": [],
        "estructuras": [],
    }
    N, RC, E = filas["naturaleza"], filas["recursos_cofres"], filas["estructuras"]
    for tam in ("peq", "med", "gran"):
        for v in (0, 1):
            N.append(kp.roca(kit, tam, v))
    for v in range(3):
        N.append(kp.arbusto(kit, v))
    for v in range(2):
        N.append(kp.hierba_parche(kit, v))
    for v in range(3):
        N.append(kp.flores(kit, v))
    for v in range(2):
        N.append(kp.tronco_caido(kit, v))
    for v in range(2):
        N.append(kp.hongo_grande(kit, v))
    for v in range(2):
        N.append(kp.cactus(kit, v))
    for v in range(2):
        N.append(kp.palmera(kit, v))
    for v in range(2):
        N.append(kp.duna(kit, v))
    for v in range(2):
        N.append(kp.rampa_natural(kit, v))
    for t in ("cristal", "ambar", "gema"):
        RC.append(kp.recurso(kit, t))
    for t in ("comun", "musgoso", "raro", "enterrado"):
        RC.append(kp.cofre(kit, t))
    for v in range(2):
        E.append(kp.puente_tramo(kit, v))
    for v in range(2):
        E.append(kp.ruina_arco(kit, v))
    E.append(kp.ruina_pilar(kit))
    for v in range(2):
        E.append(kp.valla(kit, v))
    E.append(kp.antorcha(kit))
    for v in range(2):
        E.append(kp.boca_cueva(kit, v))
    E.append(kp.portal_salida(kit))
    E.append(kp.meta_plataforma(kit))
    E.append(kp.meta_arco(kit))
    E.append(kp.meta_banco(kit))
    return kit, filas


def colocar(filas):
    """Distribuye las piezas en filas (solo para ver el catalogo)."""
    y = 0.0
    for nombre, objs in filas.items():
        x = 0.0
        prof = 0.0
        for o in objs:
            dx = max(o.dimensions.x, 4.0)
            o.location = (x + dx / 2, y, 0)
            x += dx + 6.0
            prof = max(prof, o.dimensions.y)
        y -= prof + 26.0


def lods(kit):
    col = bpy.data.collections.new("KIT_LOD1")
    bpy.context.scene.collection.children.link(col)
    for o in list(kit.objects):
        if kb.triangulos(o) > LOD_UMBRAL:
            c = o.copy()
            c.data = o.data.copy()
            c.name = o.name + "_lod1"
            c.data.name = c.name
            col.objects.link(c)
            kb.decimar(c, LOD_RATIO)
    return col


def metricas(kit, lod):
    datos = {"version": VERSION, "unidad": "1 unidad = 1 stud", "piezas": {}}
    total = 0
    for o in sorted(kit.objects, key=lambda o: o.name):
        t = kb.triangulos(o)
        total += t
        d = o.dimensions
        e = {"triangulos": t, "tam_studs": [round(d.x, 2), round(d.y, 2), round(d.z, 2)],
             "materiales": [m.name for m in o.data.materials]}
        l1 = bpy.data.objects.get(o.name + "_lod1")
        if l1:
            e["triangulos_lod1"] = kb.triangulos(l1)
        datos["piezas"][o.name] = e
    datos["total_lod0"] = total
    datos["total_lod1"] = sum(kb.triangulos(o) for o in lod.objects)
    datos["n_piezas"] = len(kit.objects)
    return datos


def exportar(kit, lod):
    # solo KIT y KIT_LOD1 (sin camara, luces ni figura)
    for o in bpy.data.objects:
        o.select_set(o.name in kit.objects or o.name in lod.objects)
    rc.quitar_niebla()
    bpy.ops.export_scene.gltf(filepath=os.path.join(AQUI, "kit_slime_v02.glb"), export_format="GLB",
                              use_selection=True, export_apply=True, export_yup=True)
    bpy.ops.export_scene.fbx(filepath=os.path.join(AQUI, "kit_slime_v02.fbx"), use_selection=True,
                             apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
                             mesh_smooth_type="FACE", use_mesh_modifiers=True)


def render_catalogos(filas):
    rc.preparar_escena((1800, 900), muestras=40)
    rc.sol(elev_grados=26, azim_grados=235)
    ayuda = bpy.data.collections.new("AYUDA_RENDER")
    bpy.context.scene.collection.children.link(ayuda)
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=600)
    suelo = kb.obj_temporal(bm, "suelo_catalogo")
    suelo.data.materials.append(kb.material("hierba"))
    bpy.context.scene.collection.objects.unlink(suelo)
    ayuda.objects.link(suelo)
    for nombre, objs in filas.items():
        # ocultar el resto de filas
        for n2, o2 in filas.items():
            for o in o2:
                o.hide_render = (n2 != nombre)
        xs = [o.location.x for o in objs]
        x0, x1 = min(xs) - 10, max(xs) + 10
        y = objs[0].location.y
        figs = []
        for o in objs:
            f = kb.figura_escala(ayuda, (o.location.x + o.dimensions.x / 2 + 2.5, y - o.dimensions.y / 2 - 2.0, 0), 0.3)
            figs.append(f)
        alto = max(o.dimensions.z for o in objs)
        cx = (x0 + x1) / 2
        ancho = x1 - x0
        if nombre == "naturaleza":
            # dos mitades para que se vean grandes
            mitad = len(objs) // 2
            for parte, sub in (("a", objs[:mitad]), ("b", objs[mitad:])):
                sx0 = min(o.location.x - o.dimensions.x / 2 for o in sub) - 4
                sx1 = max(o.location.x + o.dimensions.x / 2 for o in sub) + 6
                scx, sw = (sx0 + sx1) / 2, sx1 - sx0
                rc.camara((scx, y - sw * 0.55, sw * 0.32), (scx, y, 3.0), lente=40)
                rc.render(os.path.join(AQUI, "render_kit_v02_naturaleza_%s_con_figura.png" % parte))
        else:
            rc.camara((cx, y - ancho * 0.55, max(ancho * 0.3, alto * 0.9)), (cx, y, alto * 0.3), lente=40)
            rc.render(os.path.join(AQUI, "render_kit_v02_%s_con_figura.png" % nombre))
        for f in figs:
            kb.borrar_obj(f)
    for o2 in filas.values():
        for o in o2:
            o.hide_render = False


def main():
    limpiar()
    kit, filas = construir()
    bpy.context.view_layer.update()
    colocar(filas)
    lod = lods(kit)
    for o in lod.objects:  # LODs aparte, debajo del catalogo
        o.location.y -= 400
    m = metricas(kit, lod)
    with open(os.path.join(AQUI, "kit_metricas.json"), "w") as f:
        json.dump(m, f, indent=1, ensure_ascii=False)
    exportar(kit, lod)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, "kit_slime_v02.blend"), compress=True)
    print("KIT OK piezas=%d tris_lod0=%d tris_lod1=%d" % (m["n_piezas"], m["total_lod0"], m["total_lod1"]))
    if "--render" in sys.argv:
        lod.hide_render = True
        for o in lod.objects:
            o.hide_render = True
        render_catalogos(filas)


if __name__ == "__main__":
    main()
