# Contorno negro grueso para mascotas (referencia: Steal an Egg / «Roba un huevo»): carcasa invertida dentro de la MISMA malla.
# La carcasa es una copia ligeramente inflada de toda la superficie con las normales hacia dentro; como Roblox no dibuja las caras traseras,
# desde fuera solo se ve el borde que asoma por detras de la mascota. Sigue a los mismos huesos (copia los pesos) y usa el mismo material:
# sus UV apuntan a un texel negro reservado en el atlas (hay que dejar libre la esquina superior derecha: ver reservar_esquina_negra).
# Solo depende de bpy (se puede usar desde cualquier script de Blender de este proyecto).
import bpy
import numpy as np


def reservar_esquina_negra(ob, escala=0.96):
    """Despues de desplegar las UV: las encoge hacia el origen para dejar libre una franja arriba y a la derecha del atlas."""
    uv = ob.data.uv_layers.active.data
    arr = np.empty(len(uv) * 2, np.float32)
    uv.foreach_get('uv', arr)
    uv.foreach_set('uv', arr * escala)


def pintar_esquina_negra(img_array, frac=0.025):
    """Pone en negro la esquina superior derecha de la imagen (fila 0 = abajo, como en Paint.img)."""
    h, w = img_array.shape[:2]
    img_array[int(h * (1 - frac)):, int(w * (1 - frac)):] = 0.0


def agregar_contorno(ob, grosor=0.12, uv=(0.992, 0.992)):
    """Aplica una carcasa invertida de `grosor` (studs) a ob y la asigna al texel negro `uv`. Devuelve los poligonos antes y despues."""
    me = ob.data
    n0 = len(me.polygons)
    while len(me.materials) < 2:
        me.materials.append(me.materials[0])
    mod = ob.modifiers.new('Contorno', 'SOLIDIFY')
    mod.thickness = grosor
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.use_rim = False
    mod.use_even_offset = False                  # con grosor uniforme los vertices de caras muy finas se disparaban (radio x1000)
    mod.nonmanifold_thickness_mode = 'FIXED'
    mod.nonmanifold_boundary_mode = 'NONE'
    mod.material_offset = 1
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=0)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    me = ob.data
    luv = me.uv_layers.active.data
    for p in me.polygons:
        if p.material_index == 1:
            for li in p.loop_indices:
                luv[li].uv = uv
            p.material_index = 0
    while len(me.materials) > 1:
        me.materials.pop(index=len(me.materials) - 1)
    return n0, len(me.polygons)


def material_contorno_vista(nombre='contorno_vista', color=(0.015, 0.015, 0.02)):
    """Material SOLO para los renders de Cycles de las caras de la carcasa: negro para la camara cuando se ve la cara delantera (la del
    fondo de la carcasa) y totalmente transparente para todo lo demas (cara trasera, sombras, luz indirecta). Asi se ve como el contorno
    en Roblox, que no dibuja las caras traseras. Aviso para Roblox: la carcasa cerrada si puede ensombrecer a la propia mascota; poner
    CastShadow = false en el MeshPart de la version con contorno."""
    mat = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    mix = nt.nodes.new('ShaderNodeMixShader')
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    lp = nt.nodes.new('ShaderNodeLightPath')
    resta = nt.nodes.new('ShaderNodeMath')
    maximo = nt.nodes.new('ShaderNodeMath')
    em = nt.nodes.new('ShaderNodeEmission')
    tra = nt.nodes.new('ShaderNodeBsdfTransparent')
    resta.operation = 'SUBTRACT'
    resta.inputs[0].default_value = 1.0
    maximo.operation = 'MAXIMUM'
    em.inputs['Color'].default_value = (*color, 1.0)
    nt.links.new(lp.outputs['Is Camera Ray'], resta.inputs[1])
    nt.links.new(geo.outputs['Backfacing'], maximo.inputs[0])
    nt.links.new(resta.outputs['Value'], maximo.inputs[1])
    nt.links.new(maximo.outputs['Value'], mix.inputs['Fac'])
    nt.links.new(em.outputs['Emission'], mix.inputs[1])
    nt.links.new(tra.outputs['BSDF'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return mat


def separar_carcasa_para_vista(ob, mat_carcasa, umbral=0.98):
    """En un objeto con carcasa (UV de la carcasa >= umbral): le da un segundo hueco de material con mat_carcasa para los renders."""
    me = ob.data
    luv = me.uv_layers.active.data
    me.materials.append(mat_carcasa)
    n = 0
    for p in me.polygons:
        if all(min(luv[li].uv) >= umbral for li in p.loop_indices):
            p.material_index = 1
            n += 1
    return n


def material_vista_recortada(nombre, img_path):
    """Material SOLO para los renders de Cycles: oculta las caras traseras (lo que hace Roblox) para que se vea el contorno.
    No usar en la exportacion: el FBX/GLB lleva el material sencillo de ap_lib.final_material."""
    mat = bpy.data.materials.get(nombre) or bpy.data.materials.new(nombre)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    mix = nt.nodes.new('ShaderNodeMixShader')
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    tra = nt.nodes.new('ShaderNodeBsdfTransparent')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    tex = nt.nodes.new('ShaderNodeTexImage')
    img = bpy.data.images.load(img_path, check_existing=True)
    img.colorspace_settings.name = 'sRGB'
    tex.image = img
    tex.interpolation = 'Linear'
    bsdf.inputs['Roughness'].default_value = 1.0
    for k in ('Specular IOR Level', 'Specular'):
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = 0.0
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(geo.outputs['Backfacing'], mix.inputs['Fac'])
    nt.links.new(bsdf.outputs['BSDF'], mix.inputs[1])
    nt.links.new(tra.outputs['BSDF'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return mat
