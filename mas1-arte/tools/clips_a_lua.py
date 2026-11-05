# Los clips de Blender de las mascotas y alas del juego, fotograma a fotograma, en un módulo Lua (mas1-juego/src/ClipsHuesos.lua) que
# client/AnimaSeguidores.client.lua reproduce con Bone.Transform. Así se ven las animaciones de verdad (Flap: recoger -> extender ->
# impulsar; Fly; Glide) sin publicar una Animation por clip en la cuenta de Maikol. Lee los .blend (los de Codex sin tocarlos) y los
# huesos tal como quedaron en Roblox (mas1-juego/assets/MAS1_Modelos.rbxmx).
#
# Ojo (01/11): los huesos importados en Studio NO tienen los ejes locales de Blender. En los rigs exportados con bake_space_transform
# todos los huesos salen con giro identidad respecto a su padre (alineados con Root), y en los de Codex con otros ejes. Copiar la
# pose local de Blender (matrix_basis) a Bone.Transform giraba cada hueso sobre ejes equivocados: las alas se cerraban sobre el
# jugador. Por eso aquí se pasa el movimiento por el espacio del modelo, que sí es el mismo en los dos lados:
#   1. C = semejanza (giro, escala y traslación) que lleva el espacio de la armadura de Blender al de la pieza que lleva los huesos en
#      Roblox, ajustada con las posiciones de reposo de los huesos (cabezas en Blender, CFrame encadenado en Roblox);
#   2. por fotograma, D = pose @ reposo⁻¹ de cada hueso en Blender (lo que mueve la piel) y su versión en Roblox, C·D·C⁻¹;
#   3. pose del hueso en Roblox = C·D·C⁻¹ · reposo_roblox, y Transform = (pose_padre · Bone.CFrame)⁻¹ · pose del hueso.
# Así la piel se deforma igual que en Blender sean cuales sean los ejes de cada hueso. Se guarda Transform (posición en studs a escala
# 1 y cuaternión) a 15 fotogramas por segundo.
#   blender -b --factory-startup --python-exit-code 1 -P clips_a_lua.py   ->   mas1-juego/src/ClipsHuesos.lua
import bpy, os, json, math
import xml.etree.ElementTree as ET
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ARTE = os.path.abspath(os.path.join(HERE, '..'))
CODEX = r'C:\Users\maiko\Documents\Codex\2026-10-21\c\outputs\mas-1-lanzamiento\art'
JUEGO = os.path.abspath(os.path.join(ARTE, '..', 'mas1-juego'))
SALIDA = os.path.join(JUEGO, 'src', 'ClipsHuesos.lua')
MODELOS = os.path.join(JUEGO, 'assets', 'MAS1_Modelos.rbxmx')
FPS = 15
PIEZAS = {   # id del juego: (.blend, clips que se usan)
    'gorrion': (os.path.join(CODEX, 'mascotas-comunes-v06', 'GorrionMiga_v06', 'GorrionMiga_v06.blend'), ('Fly',)),
    'golondrina': (os.path.join(CODEX, 'mascotas-comunes-v06', 'GolondrinaBrisa_v06', 'GolondrinaBrisa_v06.blend'), ('Fly',)),
    'nube': (os.path.join(ARTE, 'mascotas-enemigos-v01', 'nube', 'MascotaNube.blend'), ('Fly',)),
    'globo': (os.path.join(ARTE, 'mascotas-enemigos-v01', 'globo', 'MascotaGlobo.blend'), ('Fly',)),
    'nubarron': (os.path.join(ARTE, 'mascotas-enemigos-v01', 'nubarron', 'MascotaNubarron.blend'), ('Fly',)),
    'ovni': (os.path.join(ARTE, 'mascotas-enemigos-v01', 'ovni', 'MascotaOvni.blend'), ('Fly',)),
    'meteorito': (os.path.join(ARTE, 'mascotas-enemigos-v01', 'meteorito', 'MascotaMeteorito.blend'), ('Fly',)),
    'cometa': (os.path.join(ARTE, 'mascotas-enemigos-v01', 'cometa', 'MascotaCometa.blend'), ('Fly',)),
    'aguila': (os.path.join(ARTE, 'mascotas-altas-v02', 'aguila-legendaria', 'AguilaLegendaria.blend'), ('Fly',)),
    'grifo': (os.path.join(ARTE, 'mascotas-altas-v02', 'grifo-mitico', 'GrifoMitico.blend'), ('Fly',)),
    'fenix': (os.path.join(ARTE, 'mascotas-altas-v02', 'fenix', 'FenixDeFuego.blend'), ('Fly',)),
    'iniciales': (os.path.join(CODEX, 'alas-iniciales-v02', 'Alas-ave-iniciales-v02.blend'), ('Flap', 'Glide')),
    'roboticas': (os.path.join(CODEX, 'alas-roboticas-v02', 'Alas-Roboticas-v02.blend'), ('Flap', 'Glide', 'Deploy')),
    'avanzadas': (os.path.join(ARTE, 'alas-avanzadas-v02', 'AlasAvanzadas_v02.blend'), ('Flap', 'Glide', 'Deploy')),
}


def num(x, d):
    s = ('%.' + str(d) + 'f') % x
    s = s.rstrip('0').rstrip('.') if '.' in s else s
    return '0' if s in ('-0', '') else s


def huesos_roblox(ruta):
    """{modelo: {hueso: (padre o None, Bone.CFrame como Matrix)}}; padre None = cuelga de la pieza (MeshPart o RootPart)."""
    def prop(it, n):
        return next((c for c in it.find('Properties') if c.get('name') == n), None)

    def cframe(c):
        v = [float(c.find(k).text) for k in ('X', 'Y', 'Z', 'R00', 'R01', 'R02', 'R10', 'R11', 'R12', 'R20', 'R21', 'R22')]
        return Matrix(((v[3], v[4], v[5], v[0]), (v[6], v[7], v[8], v[1]), (v[9], v[10], v[11], v[2]), (0, 0, 0, 1)))

    modelos = {}
    for m in ET.parse(ruta).getroot().iter('Item'):
        if m.get('class') != 'Model':
            continue
        huesos = {}

        def bajar(it, padre):
            for k in it.findall('Item'):
                if k.get('class') == 'Bone':
                    n = prop(k, 'Name').text
                    huesos[n] = (padre, cframe(prop(k, 'CFrame')))
                    bajar(k, n)
                elif k.get('class') in ('MeshPart', 'Part'):
                    bajar(k, None)
        bajar(m, None)
        if huesos:
            modelos[prop(m, 'Name').text] = huesos
    return modelos


def semejanza(a, b):
    """s, R, t con b ≈ s·R·a + t (Umeyama; R siempre es un giro propio, d = -1 solo dice que hubo que corregir una
    reflexión, lo normal si los huesos están en un plano) y el error máximo en studs."""
    a, b = np.array(a), np.array(b)
    ma, mb = a.mean(0), b.mean(0)
    a0, b0 = a - ma, b - mb
    u, sv, vt = np.linalg.svd(b0.T @ a0 / len(a))
    d = 1.0 if np.linalg.det(u) * np.linalg.det(vt) > 0 else -1.0
    giro = u @ np.diag([1, 1, d]) @ vt
    s = (sv * np.array([1, 1, d])).sum() / (a0 ** 2).sum(1).mean()
    t = mb - s * giro @ ma
    err = float(np.sqrt(((b - (s * (giro @ a.T).T + t)) ** 2).sum(1)).max())
    return s, giro, t, d, err


ROBLOX = huesos_roblox(MODELOS)
lua = ['-- GENERADO por mas1-arte/tools/clips_a_lua.py: no editar a mano. Clips de Blender de mascotas y alas pasados a Bone.Transform',
       '-- de los huesos de MAS1_Modelos (studs a escala 1), %d fotogramas por segundo: por hueso, 7 numeros por fotograma' % FPS,
       '-- (x, y, z, qx, qy, qz, qw).',
       'return {']
resumen = {}
for id_, (ruta, clips) in PIEZAS.items():
    rob = ROBLOX[id_]
    bpy.ops.wm.open_mainfile(filepath=ruta, load_ui=False)
    rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    acciones = {tr.name: tr.strips[0].action for tr in rig.animation_data.nla_tracks if tr.strips} if rig.animation_data else {}
    rig.animation_data_clear()
    ad = rig.animation_data_create()
    sc = bpy.context.scene

    # reposo de cada hueso en el espacio de la pieza de Roblox, padres antes que hijos
    orden, reposo = [], {}

    def poner(n):
        if n in reposo:
            return
        padre, cf = rob[n]
        if padre:
            poner(padre)
        reposo[n] = reposo[padre] @ cf if padre else cf.copy()
        orden.append(n)
    for n in rob:
        poner(n)
    comunes = [n for n in orden if n in rig.data.bones]
    faltan = sorted(set(rob) - set(comunes))
    s, giro, t, d, err = semejanza([rig.data.bones[n].head_local[:] for n in comunes], [reposo[n].translation[:] for n in comunes])
    assert err < 0.02, (id_, 'el reposo de Blender no encaja con el de Roblox', d, err)
    C = Matrix([[*(s * giro[i]), t[i]] for i in range(3)] + [[0, 0, 0, 1]])
    Ci = C.inverted()
    # cuánto distan los ejes locales de Roblox de los de Blender (lo que estropeaba la copia directa de matrix_basis)
    giro_c = Matrix([list(giro[i]) for i in range(3)])

    def desfase_ejes(n):
        a = (giro_c @ rig.data.bones[n].matrix_local.to_3x3()).to_quaternion()
        g = a.rotation_difference(reposo[n].to_3x3().to_quaternion()).angle
        return math.degrees(min(g, 2 * math.pi - g))
    desfase = max(desfase_ejes(n) for n in comunes)
    print('PIEZA', id_, 'huesos', len(comunes), 'faltan', faltan, 'escala %.4f' % s, 'error %.4f studs' % err,
          'desfase de ejes %.0f grados' % desfase)

    partes = []
    for c in clips:
        act = acciones.get(c)
        if act is None:
            continue
        ad.action = act
        try:
            if act.slots and ad.action_slot is None:
                ad.action_slot = act.slots[0]
        except Exception:
            pass
        f0, f1 = act.frame_range
        paso = sc.render.fps / FPS
        cuadros = []
        f = f0
        while f <= f1 + 1e-6:
            cuadros.append(f)
            f += paso
        datos = {n: [] for n in orden}
        for f in cuadros:
            sc.frame_set(int(f), subframe=f - int(f))
            pose = {}
            for n in orden:
                padre, cf = rob[n]
                base = pose[padre] if padre else Matrix.Identity(4)
                pb = rig.pose.bones.get(n)
                if pb is None:
                    pose[n] = base @ cf
                    T = Matrix.Identity(4)
                else:
                    D = pb.matrix @ rig.data.bones[n].matrix_local.inverted()
                    pose[n] = C @ D @ Ci @ reposo[n]
                    T = (base @ cf).inverted() @ pose[n]
                q = T.to_quaternion().normalized()
                previo = datos[n][-1] if datos[n] else None
                if previo and q.x * previo[3] + q.y * previo[4] + q.z * previo[5] + q.w * previo[6] < 0:
                    q.negate()   # mismo giro, sin saltos de signo entre fotogramas
                p = T.translation
                datos[n].append((p.x, p.y, p.z, q.x, q.y, q.z, q.w))
        vivos = {n: v for n, v in datos.items()
                 if any(abs(a - b) > 1e-4 for fr in v for a, b in zip(fr, (0, 0, 0, 0, 0, 0, 1)))}
        cuerpo = ', '.join('%s = { %s }' % (n, ', '.join(num(x, 3 if k < 3 else 4) for fr in v for k, x in enumerate(fr)))
                           for n, v in sorted(vivos.items()))
        partes.append('%s = { n = %d, dur = %s, huesos = { %s } }' % (c, len(cuadros), num((f1 - f0) / sc.render.fps, 4), cuerpo))
        resumen.setdefault(id_, {})[c] = (len(cuadros), sorted(vivos))
    lua.append('\t%s = { %s },' % (id_, ', '.join(partes)))
lua.append('}')
open(SALIDA, 'w', encoding='utf-8', newline='\n').write('\n'.join(lua) + '\n')
print('CLIPS', os.path.getsize(SALIDA), json.dumps({k: {c: n for c, (n, _) in v.items()} for k, v in resumen.items()}))
for k, v in resumen.items():
    for c, (n, hs) in v.items():
        print('CLIP', k, c, n, 'huesos', hs)
