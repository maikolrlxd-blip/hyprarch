# Ensambla el mapa apocalíptico (300 x 300 studs) con las piezas de calles, edificios, vehiculos, props y natura.
# Lee los .blend de cada categoria, coloca copias enlazadas, renderiza vistas y exporta el layout (JSON) y el FBX completo.
# blender -b --factory-startup -P build_mapa_ensamble.py
import sys, os, math, json
sys.path.insert(0, os.path.dirname(__file__))
import importlib
import ap_lib as A
import ap_armas as W
importlib.reload(A); importlib.reload(W)
import bpy
import numpy as np
from mathutils import Vector, Matrix, Euler

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MAPA = os.path.join(ROOT, 'mapa')
OUT = os.path.join(MAPA, 'ensamble')
os.makedirs(os.path.join(OUT, 'previews'), exist_ok=True)
CATS = {'Calles': 'calles', 'Edificios': 'edificios', 'Vehiculos': 'vehiculos', 'Props': 'props', 'Natura': 'natura'}

A.clean_scene()
LIB = A.collection('Biblioteca')
LIB.hide_render = True
SRC = {}
for cat, folder in CATS.items():
    path = os.path.join(MAPA, folder, cat + '.blend')
    if not os.path.exists(path):
        A.log('falta', path)
        continue
    try:
        with bpy.data.libraries.load(path, link=False) as (dfrom, dto):
            dto.objects = [n for n in dfrom.objects if not n.startswith(('Ref_', 'Regla_', 'Suelo_Ref', 'Cam', 'Sol', 'Relleno', 'RefPos'))]
    except OSError as e:                     # .blend roto (p. ej. un guardado cortado): se sigue con el resto y se avisa
        A.log('no se pudo abrir', path, e)
        continue
    for o in dto.objects:
        if o is None or o.type != 'MESH':
            continue
        LIB.objects.link(o)
        o.location = (0, 0, 0)
        SRC[o.name] = (o, folder)
A.log('piezas cargadas', len(SRC), sorted(SRC))

C = A.collection('Mapa')
inst = []
CUENTA = {}


def put(name, x, y, rz=0.0, z=0.0):
    if name not in SRC:
        A.log('pieza no encontrada', name)
        return None
    src, folder = SRC[name]
    o = src.copy()
    o.data = src.data
    CUENTA[name] = CUENTA.get(name, 0) + 1
    o.name = '%s_%02d' % (name, CUENTA[name])             # nombre fijo: es el nombre del MeshPart al importar en Studio
    o.location = (x, y, z)
    o.rotation_euler = (0, 0, math.radians(rz))
    C.objects.link(o)
    inst.append({'nombre': o.name, 'pieza': name, 'fbx': 'mapa/%s/fbx/%s.fbx' % (folder, name),
                 'pos_studs': [round(x, 2), round(y, 2), round(z, 2)], 'giro_z_grados': rz})
    return o


# ------------------------------------------------------------------ calles en cruz (300 x 300)
for x in (-120, -60, 60, 120):
    put('Calle_Recto_60', x, 0)
put('Calle_Cruce_60', 0, 0)
put('Calle_Rota_60', 0, 60, 90)
for y in (120, -60, -120):
    put('Calle_Recto_60', 0, y, 90)
# solares en los cuatro cuadrantes
for sx in (-1, 1):
    for sy in (-1, 1):
        for a in (60, 120):
            for b in (60, 120):
                put('Suelo_Solar_60', sx * a, sy * b, ((a + b) // 60 % 4) * 90)

# ------------------------------------------------------------------ edificios
put('Edificio_Tienda', -78, 45)
put('Edificio_Bloque', 78, 47)
put('Edificio_Almacen', 82, -52, 180)
put('Edificio_Tienda', -120, -46, 180)

# ------------------------------------------------------------------ vehiculos
put('Coche_Sedan_Oxidado', -96, 8, 98)
put('Coche_Sedan_Volcado', 34, -7, 160)
put('Coche_Sedan_Quemado', 112, 9, -84)
put('Pickup_Abandonada', -42, -9, 272)
put('Furgoneta_Blanca', 7, 102, 4)
put('Coche_Sedan_Oxidado', -6, -128, 12)

# ------------------------------------------------------------------ barricadas y props
put('Barricada_Sacos', -1, -96, 0)
put('Barricada_Sacos', 11, -98, 12)
for y in (-12, 0, 12):
    put('Barrera_Hormigon', 136, y, 90)
put('Barricada_Madera', -60, 20, 0)
put('Barricada_Madera', 0, 140, 0)
for x in (-60, -80, -100):
    put('Valla_Chapa', x, -33, 0)
for (x, y, r) in ((-130, 23, 180), (-70, 23, 180), (100, 23, 180), (40, -23, 0), (-100, -23, 0), (23, 70, 270), (-23, -80, 90)):
    put('Farola_Doblada', x, y, r)
put('Hidrante', -45, 21)
put('Hidrante', 55, -21)
put('Contenedor_Basura', -56, 40, 90)
put('Contenedor_Basura', 104, -30, 0)
put('Barriles', 96, -31)
put('Senal_Alto', 22, 22, 180)
put('Semaforo_Torcido', -22, -22, 0)
put('Cajas_Madera', -62, 33)
put('Neumaticos', -110, -64)

# ------------------------------------------------------------------ natura y escombros
put('Escombros_Grande', 92, 30)
put('Escombros_Pequeno', -20, 40)
put('Escombros_Ladrillos', 60, 28)
put('Escombros_Pequeno', 40, -100)
put('Arbol_Muerto', -88, -92)
put('Arbol_Invasor', -60, -72)
put('Arbol_Invasor', 120, 110)
put('Arbol_Muerto', 60, 120)
for i, (x, y) in enumerate(((-75, -55), (-95, -70), (-120, -100), (-45, -110), (-130, 70), (40, 130), (130, -120), (60, -130))):
    put('Arbusto', x, y, i * 47)
rng = np.random.default_rng(3)
for i in range(26):
    side = rng.choice([-1, 1])
    if i % 2:
        x, y = rng.uniform(-145, 145), side * rng.uniform(29.0, 31.0)
    else:
        x, y = side * rng.uniform(29.0, 31.0), rng.uniform(-145, 145)
    put('Hierba_Alta', float(x), float(y), float(rng.uniform(0, 360)), 0.55)
for i in range(16):
    put('Maleza', float(rng.uniform(-140, 140)), float(rng.choice([-1, 1]) * rng.uniform(17.2, 17.8)), float(rng.uniform(0, 360)), 0.0)
put('Enredadera_Muro', 66, 35.0, 0)               # sobre la fachada del bloque (frente en y = 35)
put('Enredadera_Muro', -96.4, 45, 270)             # lateral de la tienda
A.log('instancias', len(inst))

# ------------------------------------------------------------------ colisiones simples y marcadores para el juego (Luto)
# Las mallas visuales van sin colision; las colisiones son cajas orientadas invisibles (*_Colision) y los marcadores son Parts.
# No se exportan como mallas (serian ~100 cajas subidas a la cuenta): salen como datos (JSON) y como un script para la barra
# de comandos de Studio que crea las Parts dentro de ServerStorage.LUTO_Plantillas.Mapa (ver apocalipsis-juego/INTEGRACION.md).
SIN_COLISION = ('Arbusto', 'Hierba_Alta', 'Maleza', 'Enredadera_Muro')
POSTES = {'Farola_Doblada': ((0, 0, 3.5), (0.6, 0.6, 7.0)), 'Semaforo_Torcido': ((0, 0, 7.25), (0.55, 0.55, 14.5)),
          'Senal_Alto': ((0, 0, 3.15), (0.3, 0.3, 6.3)), 'Arbol_Muerto': ((0, 0, 3.0), (1.4, 1.4, 6.0)),
          'Arbol_Invasor': ((0, 0, 3.0), (1.4, 1.4, 6.0))}
ACERAS = [((0, 24, -0.225), (60, 12, 1.55)), ((0, -24, -0.225), (60, 12, 1.55))]
SUELOS = {
    'Calle_Recto_60': [((0, 0, -0.5), (60, 36, 1.0))] + ACERAS,
    'Calle_Cruce_60': [((0, 0, -0.5), (60, 60, 1.0))] + [((sx * 24, sy * 24, 0.05), (12, 12, 1.2)) for sx in (-1, 1) for sy in (-1, 1)],
    'Calle_Rota_60': [((-19.5, 0, -0.5), (21, 36, 1)), ((19.5, 0, -0.5), (21, 36, 1)), ((0, 13.5, -0.5), (18, 9, 1)),
                      ((0, -13.5, -0.5), (18, 9, 1)), ((0, 0, -2.2), (18.4, 18.4, 0.6))] + ACERAS,
    'Suelo_Solar_60': [((0, 0, 0.05), (60, 60, 1.0))],
}


def cajas_pieza(name):
    if name in SIN_COLISION:
        return []
    if name in SUELOS:
        return SUELOS[name]
    if name in POSTES:
        return [POSTES[name]]
    bb = [Vector(c) for c in SRC[name][0].bound_box]
    mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    if name.startswith('Escombros'):
        mx.z = mn.z + (mx.z - mn.z) * 0.7            # el escombro se pisa por encima, no se trepa a sus picos
    return [(tuple((mn + mx) / 2), tuple(mx - mn))]


COL = []
for o in C.objects:
    piece = o.name[:-3]
    Rz = Matrix.Rotation(o.rotation_euler.z, 3, 'Z')
    for i, (c, s) in enumerate(cajas_pieza(piece)):
        w = Vector(o.location) + Rz @ Vector(c)
        COL.append({'nombre': '%s_Colision%s' % (o.name, '' if i == 0 else '_%d' % (i + 1)), 'centro': [round(v, 3) for v in w],
                    'tamano': [round(v, 3) for v in s], 'giro_z_grados': round(math.degrees(o.rotation_euler.z), 2)})
for (n, c, s) in (('Borde_N', (0, 152, 10), (312, 4, 20)), ('Borde_S', (0, -152, 10), (312, 4, 20)),
                  ('Borde_E', (152, 0, 10), (4, 312, 20)), ('Borde_O', (-152, 0, 10), (4, 312, 20))):
    COL.append({'nombre': n + '_Colision', 'centro': list(c), 'tamano': list(s), 'giro_z_grados': 0.0})
MARCAS = {'SpawnJugadores': [(0, -4, 0.0)],
          'SpawnZombis': [(-145, 6, 0.0), (145, -6, 0.0), (6, 145, 0.0), (-6, -145, 0.0),
                          (-135, -135, 0.55), (135, 135, 0.55), (-135, 135, 0.55), (135, -135, 0.55),
                          (-145, 80, 0.55), (145, -80, 0.55), (80, 145, 0.55), (-80, -145, 0.55)],
          'Tienda_municion': [(-26, -28, 0.65)], 'Tienda_curar': [(27, 26, 0.65)]}
A.log('colisiones', len(COL), 'marcadores', sum(len(v) for v in MARCAS.values()))

# ------------------------------------------------------------------ ambiente apocaliptico (solo apariencia)
# Tarde baja con polvo en suspension: sol calido y rasante, cielo de bruma marron grisacea, colores apagados. Los renders
# imitan los ajustes de Roblox de ambiente-roblox.lua (Atmosphere + ColorCorrection): bruma por distancia y desaturacion.
SKY = (0.62, 0.56, 0.48)
CC = A.collection('Camaras')
A.setup_world(SKY, 0.85)
for L in A.add_lights(CC):
    if L.name.startswith('Sol'):
        L.data.energy = 3.4
        L.data.color = (1.0, 0.80, 0.60)
        L.rotation_euler = Euler((math.radians(66), math.radians(4), math.radians(-38)))
    else:
        L.data.energy = 0.55
        L.data.color = (0.70, 0.74, 0.82)


def fog_mask_mat(d0, d1):
    m = bpy.data.materials.new('Niebla_Mascara')
    nt = A._nodes_clear(m)
    cd = nt.nodes.new('ShaderNodeCameraData')
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.clamp = True
    mr.inputs['From Min'].default_value = d0
    mr.inputs['From Max'].default_value = d1
    em = nt.nodes.new('ShaderNodeEmission')
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(cd.outputs['View Distance'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], em.inputs['Color'])
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return m


def render_ambiente(path, cam, d0, d1, dens):
    """Render normal + mascara de distancia (material forzado) y mezcla en numpy: bruma del color del cielo, desaturacion,
    algo de contraste y tinte calido."""
    A.render(path, cam)
    sc, vl = bpy.context.scene, bpy.context.view_layer
    bg = [n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND'][0]
    st, smp = bg.inputs['Strength'].default_value, sc.cycles.samples
    bg.inputs['Strength'].default_value = 0.0
    sc.cycles.samples = 4
    vl.material_override = fog_mask_mat(d0, d1)
    mp = path[:-4] + '_mascara.png'
    A.render(mp, cam)
    vl.material_override = None
    bg.inputs['Strength'].default_value, sc.cycles.samples = st, smp
    col = W.load_png(path)
    m = np.clip(W.load_png(mp)[:, :, 0], 0, 1) ** 2.2
    os.remove(mp)
    sky = col[m < 1e-4]
    fogc = np.median(sky, axis=0) if len(sky) > col.shape[0] * col.shape[1] * 0.02 else np.array([0.74, 0.69, 0.62], np.float32)
    f = (dens * m)[:, :, None]
    col = col * (1 - f) + fogc * f
    lum = (col * np.array([0.299, 0.587, 0.114], np.float32)).sum(2, keepdims=True)
    col = lum + (col - lum) * 0.74
    col = ((col - 0.5) * 1.08 + 0.5) * np.array([1.0, 0.97, 0.92], np.float32)
    W.save_png(col, path)


W.hide_only({'Mapa', 'Camaras', 'Ref'})
CR = A.collection('Ref')
for (x, y) in ((-60, 12), (10, 30), (0, -80)):
    for o in A.reference_figure(CR, x, y, 5.2):
        pass
A.setup_render((1600, 1600), 'CYCLES', 24)
top = W.look_cam(CC, 'CTop', Vector((0, 0, 0)), (0, 0, 1), 400, 50, ortho=310)
top.rotation_euler = (0, 0, 0)
render_ambiente(os.path.join(OUT, 'previews', 'Mapa_vista_cenital.png'), top, 380.0, 900.0, 0.0)
A.setup_render((1600, 900), 'CYCLES', 32)
views = {   # nombre: (objetivo, direccion desde el objetivo, distancia, objetivo de camara mm, bruma desde, hasta, densidad)
    'Mapa_aerea_3_4': (Vector((0, 0, 0)), (-0.75, -1.0, 0.85), 360, 35, 260.0, 700.0, 0.55),
    'Mapa_calle_principal': (Vector((-40, 4, 4.0)), (-1.0, -0.12, 0.06), 70, 35, 25.0, 260.0, 0.80),
    'Mapa_cruce_y_bloque': (Vector((35, 25, 6.0)), (-1.0, -0.9, 0.18), 60, 35, 25.0, 260.0, 0.80),
    'Mapa_solar_sur_oeste': (Vector((-80, -75, 4.0)), (0.9, 0.6, 0.12), 55, 35, 25.0, 260.0, 0.80),
}
for n, (tgt, d, dist, lens, d0, d1, dens) in views.items():
    cam = W.look_cam(CC, 'C_' + n, tgt, d, dist, lens)
    render_ambiente(os.path.join(OUT, 'previews', n + '.png'), cam, d0, d1, dens)

# ajustes de Roblox con el mismo ambiente (solo apariencia: Lighting y efectos de postproceso)
LUA = '''-- Ambiente apocaliptico del mapa (solo apariencia). Generado por tools/build_mapa_ensamble.py.
-- Uso: ModuleScript en ReplicatedStorage; desde un Script del servidor: require(ruta).aplicar()
local Lighting = game:GetService("Lighting")
local Ambiente = {}

Ambiente.Lighting = {
	ClockTime = 17.4,                 -- tarde baja: sombras largas y luz calida
	GeographicLatitude = 38,
	Brightness = 2.3,
	Ambient = Color3.fromRGB(70, 62, 55),
	OutdoorAmbient = Color3.fromRGB(124, 113, 101),
	ColorShift_Top = Color3.fromRGB(255, 208, 160),
	ColorShift_Bottom = Color3.fromRGB(58, 49, 43),
	EnvironmentDiffuseScale = 0.45,
	EnvironmentSpecularScale = 0.15,
	ExposureCompensation = -0.1,
	GlobalShadows = true,
}
-- bruma de polvo: el horizonte se pierde en marron grisaceo
Ambiente.Atmosphere = {Density = 0.38, Offset = 0.15, Color = Color3.fromRGB(199, 180, 154), Decay = Color3.fromRGB(112, 84, 62), Glare = 0.12, Haze = 2.4}
-- colores apagados y algo de contraste (estilo Poli Pintado: paleta sucia y mate)
Ambiente.ColorCorrection = {Brightness = -0.02, Contrast = 0.10, Saturation = -0.28, TintColor = Color3.fromRGB(255, 244, 228)}
Ambiente.Bloom = {Intensity = 0.3, Size = 26, Threshold = 1.7}
Ambiente.SunRays = {Intensity = 0.05, Spread = 0.55}

local function efecto(clase, nombre, props)
	local e = Lighting:FindFirstChild(nombre) or Instance.new(clase)
	e.Name = nombre
	for k, v in pairs(props) do
		e[k] = v
	end
	e.Parent = Lighting
end

function Ambiente.aplicar()
	for k, v in pairs(Ambiente.Lighting) do
		Lighting[k] = v
	end
	efecto("Atmosphere", "AtmosferaApocalipsis", Ambiente.Atmosphere)
	efecto("ColorCorrectionEffect", "ColorApocalipsis", Ambiente.ColorCorrection)
	efecto("BloomEffect", "BrilloApocalipsis", Ambiente.Bloom)
	efecto("SunRaysEffect", "RayosApocalipsis", Ambiente.SunRays)
end

return Ambiente
'''
with open(os.path.join(MAPA, 'ambiente-roblox.lua'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(LUA)

# ------------------------------------------------------------------ export
for o in list(CR.objects):
    bpy.data.objects.remove(o, do_unlink=True)
tri_total = A.tris([o for o in C.objects if o.type == 'MESH'])
A.write_json(os.path.join(OUT, 'mapa-layout.json'), {
    'descripcion': 'Mapa apocaliptico 300x300 studs: calle principal (eje X) y calle lateral (eje Y) en cruz, 4 edificios, 6 vehiculos, '
                   'barricadas, props y vegetacion. Posiciones en studs (Roblox: x = x, y_roblox = z, z_roblox = -y), giro alrededor de la vertical.',
    'unidades': '1 stud; superficie de la calzada en z = 0, aceras y solares en z = 0.55',
    'triangulos_totales': tri_total, 'instancias': inst, 'colisiones': COL,
    'marcadores': {k: [list(p) for p in v] for k, v in MARCAS.items()}})

# script para la barra de comandos de Studio: crea colisiones y marcadores dentro del Mapa importado (alineados con el cruce)
rb = lambda v: 'Vector3.new(%.3f, %.3f, %.3f)' % (v[0], v[2], -v[1])
rs = lambda s: 'Vector3.new(%.3f, %.3f, %.3f)' % (s[0], s[2], s[1])
ref = [o for o in C.objects if o.name == 'Calle_Cruce_60_01']
if ref:
    bb = [ref[0].matrix_world @ Vector(c) for c in ref[0].bound_box]
    rc = [(min(v[i] for v in bb) + max(v[i] for v in bb)) / 2 for i in range(3)]
else:
    rc = [0.0, 0.0, 0.0]
L = ['-- Ejecutar UNA vez en la barra de comandos de Studio, con el Mapa importado en ServerStorage.LUTO_Plantillas.Mapa.',
     '-- Crea las cajas de colision invisibles (*_Colision), los marcadores SpawnJugadores, SpawnZombis, Tienda_municion y',
     '-- Tienda_curar, y deja las mallas visuales ancladas y sin colision. Generado por tools/build_mapa_ensamble.py.',
     'local mapa = game:GetService("ServerStorage"):WaitForChild("LUTO_Plantillas"):WaitForChild("Mapa")',
     'local ref = mapa:FindFirstChild("Calle_Cruce_60_01", true)',
     'local off = ref and (ref.Position - %s) or Vector3.zero  -- el importador puede mover el modelo: se alinea con el cruce' % rb(rc),
     'for _, d in ipairs(mapa:GetDescendants()) do',
     '\tif d:IsA("BasePart") then d.Anchored = true; d.CanCollide = false end',
     'end',
     'local function caja(nombre, padre, c, s, giro, colision)',
     '\tlocal p = Instance.new("Part")',
     '\tp.Name = nombre; p.Anchored = true; p.Size = s; p.Transparency = 1',
     '\tp.CFrame = CFrame.new(c + off) * CFrame.Angles(0, math.rad(giro), 0)',
     '\tp.CanCollide = colision; p.CanQuery = false; p.CanTouch = false',
     '\tp.Parent = padre',
     '\treturn p',
     'end',
     'local col = Instance.new("Folder"); col.Name = "Colisiones"; col.Parent = mapa']
for k in COL:
    L.append('caja("%s", col, %s, %s, %.2f, true)' % (k['nombre'], rb(k['centro']), rs(k['tamano']), k['giro_z_grados']))
L.append('caja("SpawnJugadores", mapa, %s, Vector3.new(6, 1, 6), 0, false)' % rb((MARCAS['SpawnJugadores'][0][0], MARCAS['SpawnJugadores'][0][1],
                                                                               MARCAS['SpawnJugadores'][0][2] + 0.5)))
L.append('local sz = Instance.new("Folder"); sz.Name = "SpawnZombis"; sz.Parent = mapa')
for i, p in enumerate(MARCAS['SpawnZombis']):
    L.append('caja("SpawnZombi_%02d", sz, %s, Vector3.new(4, 1, 4), 0, false)' % (i + 1, rb((p[0], p[1], p[2] + 0.5))))
for n in ('Tienda_municion', 'Tienda_curar'):
    p = MARCAS[n][0]
    L.append('caja("%s", mapa, %s, Vector3.new(4, 4, 4), 0, false)' % (n, rb((p[0], p[1], p[2] + 2.0))))
# el servidor usa estas Parts como el bloque de la tienda: visibles y solidas (las otras marcas son invisibles)
L.append('for _, n in ipairs({"Tienda_municion", "Tienda_curar"}) do local t = mapa[n]; t.Transparency = 0; t.CanCollide = true; '
         't.Material = Enum.Material.WoodPlanks; t.Color = (n == "Tienda_municion") and Color3.fromRGB(150, 120, 70) or Color3.fromRGB(80, 140, 90) end')
L.append('print("Mapa listo:", #col:GetChildren(), "colisiones,", #sz:GetChildren(), "spawns de zombis")')
os.makedirs(os.path.join(MAPA, 'integracion'), exist_ok=True)
with open(os.path.join(MAPA, 'integracion', 'MapaColisionesMarcadores.lua'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(L) + '\n')
A.export_fbx(os.path.join(OUT, 'Mapa_Completo.fbx'), [o for o in C.objects if o.type == 'MESH'])
A.save_blend(os.path.join(OUT, 'Mapa_Completo.blend'))
A.log('mapa listo', len(inst), 'instancias', tri_total, 'triangulos')
