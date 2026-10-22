"""Render comun (Cycles CPU): luz de hora dorada, cielo degradado, niebla
por material (solo para render; se quita antes de exportar)."""
import math
import bpy
from mathutils import Vector
from kit_base import srgb_a_lineal

CIELO_ARRIBA = "#86C6EE"
CIELO_HORIZONTE = "#FBE3BD"
SOL = "#FFE0AE"
NIEBLA = "#F4E2C4"


def preparar_escena(res=(1600, 900), muestras=32):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = muestras
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 1
    sc.cycles.transparent_max_bounces = 2
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.render.film_transparent = False
    # cielo: degradado vertical suave (no HDRI, no assets externos)
    w = bpy.data.worlds.get("SR_cielo") or bpy.data.worlds.new("SR_cielo")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs[0])
    ramp.color_ramp.elements[0].position = 0.48
    ramp.color_ramp.elements[0].color = srgb_a_lineal(CIELO_HORIZONTE) + (1,)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = srgb_a_lineal(CIELO_ARRIBA) + (1,)
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    nt.links.new(bg.outputs[0], out.inputs[0])
    return sc


def sol(elev_grados=24, azim_grados=215, fuerza=3.6):
    s = bpy.data.objects.get("SR_sol")
    if s is None:
        ld = bpy.data.lights.new("SR_sol", "SUN")
        s = bpy.data.objects.new("SR_sol", ld)
        bpy.context.scene.collection.objects.link(s)
    s.data.energy = fuerza
    s.data.color = srgb_a_lineal(SOL)
    s.data.angle = math.radians(3.0)  # sombras algo suaves
    e, a = math.radians(elev_grados), math.radians(azim_grados)
    d = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
    s.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    return s


def camara(pos, mirar, lente=35.0, orto=None, nombre="SR_cam"):
    c = bpy.data.objects.get(nombre)
    if c is None:
        c = bpy.data.objects.new(nombre, bpy.data.cameras.new(nombre))
        bpy.context.scene.collection.objects.link(c)
    c.location = pos
    d = Vector(mirar) - Vector(pos)
    c.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if orto:
        c.data.type = "ORTHO"
        c.data.ortho_scale = orto
    else:
        c.data.type = "PERSP"
        c.data.lens = lente
    c.data.clip_start = 0.5
    c.data.clip_end = 6000
    bpy.context.scene.camera = c
    return c


def activar_niebla(distancia=900.0, maximo=0.55):
    """Mezcla cada material SR_ con una emision color niebla segun la
    distancia a camara. Guarda el enlace original para poder quitarla."""
    col = srgb_a_lineal(NIEBLA) + (1,)
    for m in bpy.data.materials:
        if not m.name.startswith("SR_") or not m.use_nodes:
            continue
        nt = m.node_tree
        if nt.nodes.get("SR_niebla_mix"):
            continue
        out = nt.nodes.get("Material Output")
        p = nt.nodes.get("Principled BSDF")
        cam = nt.nodes.new("ShaderNodeCameraData")
        mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = -1.0 / distancia
        ex = nt.nodes.new("ShaderNodeMath"); ex.operation = "EXPONENT"
        sub = nt.nodes.new("ShaderNodeMath"); sub.operation = "SUBTRACT"; sub.inputs[0].default_value = 1.0
        esc = nt.nodes.new("ShaderNodeMath"); esc.operation = "MULTIPLY"; esc.inputs[1].default_value = maximo
        em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = col; em.inputs[1].default_value = 1.0
        mix = nt.nodes.new("ShaderNodeMixShader"); mix.name = "SR_niebla_mix"
        nt.links.new(cam.outputs["View Distance"], mul.inputs[0])
        nt.links.new(mul.outputs[0], ex.inputs[0])
        nt.links.new(ex.outputs[0], sub.inputs[1])
        nt.links.new(sub.outputs[0], esc.inputs[0])
        nt.links.new(esc.outputs[0], mix.inputs[0])
        nt.links.new(p.outputs[0], mix.inputs[1])
        nt.links.new(em.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])


def quitar_niebla():
    for m in bpy.data.materials:
        if not m.name.startswith("SR_") or not m.use_nodes:
            continue
        nt = m.node_tree
        mix = nt.nodes.get("SR_niebla_mix")
        if not mix:
            continue
        out = nt.nodes.get("Material Output")
        p = nt.nodes.get("Principled BSDF")
        for n in list(nt.nodes):
            if n.bl_idname in ("ShaderNodeCameraData", "ShaderNodeMath", "ShaderNodeEmission", "ShaderNodeMixShader"):
                nt.nodes.remove(n)
        nt.links.new(p.outputs[0], out.inputs["Surface"])


def render(ruta):
    bpy.context.scene.render.filepath = ruta
    bpy.ops.render.render(write_still=True)
