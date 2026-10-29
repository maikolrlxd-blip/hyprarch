# Exporta los clips de un personaje R15 (zombi o jefe) a un script de Studio que crea KeyframeSequences listas para publicar.
# Los huesos del rig apuntan a +Y con giro 0 (ejes del hueso = ejes del armature) y los Motor6D de ArmarZombi.lua tienen
# C0/C1 sin giro, asi que Pose.CFrame = cambio de ejes (Blender -> Roblox) de la pose local de cada hueso.
# blender -b <personaje>.blend --python-exit-code 1 -P exportar_animaciones_roblox.py -- <salida.lua> <prefijo>
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Matrix
import ap_lib as A                     # set_action: asigna la accion con su ranura (Blender 5)

args = sys.argv[sys.argv.index('--') + 1:]
OUT_LUA, PREFIJO = args[0], args[1]
PASO = 2                               # muestrea cada 2 fotogramas de 60 fps (30 fps, lo que usa el Animation Editor)
# prioridad de cada clip (Enum.AnimationPriority): Reposo puede seguir sonando debajo de Caminar y Atacar sin mezclarse con ellos.
# Los 12 clips publicados el 2026-10-23 salieron todos con Action (2); el servidor les fija la prioridad al cargarlos.
PRIORIDAD = {'Reposo': ('Idle', 0), 'Caminar': ('Movement', 1), 'Atacar': ('Action', 2), 'Caer': ('Action2', 3)}
# Blender (x derecha, y delante, z arriba) -> Roblox (x derecha, y arriba, -z delante)
M = Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0)))

rig = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
PARENT = {b.name: (b.parent.name if b.parent else None) for b in rig.data.bones}
fps = bpy.context.scene.render.fps


def fmt(v):
    return ('%.4f' % v).rstrip('0').rstrip('.') if abs(v) > 1e-6 else '0'


L = ['-- Generado por tools/exportar_animaciones_roblox.py. Ejecutar en la barra de comandos de Studio:',
     '-- crea ServerStorage.LUTO_Animaciones.%s_<Clip> (KeyframeSequence). Publicar cada una: clic derecho > Guardar en Roblox.' % PREFIJO,
     'local SS = game:GetService("ServerStorage")',
     'local carpeta = SS:FindFirstChild("LUTO_Animaciones") or Instance.new("Folder"); carpeta.Name = "LUTO_Animaciones"; carpeta.Parent = SS',
     'local function cf(x, y, z, r00, r01, r02, r10, r11, r12, r20, r21, r22) return CFrame.new(x, y, z, r00, r01, r02, r10, r11, r12, r20, r21, r22) end',
     'local function clip(nombre, bucle, prioridad, frames)',
     '\tlocal old = carpeta:FindFirstChild(nombre); if old then old:Destroy() end',
     '\tlocal ks = Instance.new("KeyframeSequence"); ks.Name = nombre; ks.Loop = bucle; ks.Priority = Enum.AnimationPriority[prioridad]',
     '\tfor _, f in ipairs(frames) do',
     '\t\tlocal kf = Instance.new("Keyframe"); kf.Time = f[1]',
     '\t\tlocal raiz = Instance.new("Pose"); raiz.Name = "HumanoidRootPart"; raiz.Weight = 0; raiz.Parent = kf',
     '\t\tlocal poses = {HumanoidRootPart = raiz}',
     '\t\tfor _, p in ipairs(f[2]) do',
     '\t\t\tlocal ps = Instance.new("Pose"); ps.Name = p[1]; ps.CFrame = p[3]; ps.EasingStyle = Enum.PoseEasingStyle.Linear',
     '\t\t\tps.Parent = poses[p[2]]; poses[p[1]] = ps',
     '\t\tend',
     '\t\tkf.Parent = ks',
     '\tend',
     '\tks.Parent = carpeta',
     '\treturn ks',
     'end']
# orden de padres antes que hijos (para colgar cada Pose de la de su padre)
orden = []
def visit(n):
    for b in rig.data.bones:
        if (b.parent.name if b.parent else None) == n and b.name != 'HumanoidRootPart':
            orden.append(b.name); visit(b.name)
visit('HumanoidRootPart')
resumen = []
for act in sorted(bpy.data.actions, key=lambda a: a.name):
    nombre = act.name.split('.')[0]
    if nombre not in ('Reposo', 'Caminar', 'Atacar', 'Caer'):
        continue
    A.set_action(rig, act)
    f0, f1 = (int(round(v)) for v in act.frame_range)
    bucle = nombre in ('Reposo', 'Caminar')
    frames = []
    for f in range(f0, f1 + 1, PASO) if (f1 - f0) % PASO == 0 else list(range(f0, f1, PASO)) + [f1]:
        bpy.context.scene.frame_set(f)
        poses = []
        for bn in orden:
            pb = rig.pose.bones[bn]
            mb = pb.matrix_basis                        # pose local del hueso (sus ejes = ejes del armature)
            r = M @ mb.to_3x3() @ M.transposed()
            t = M @ mb.to_translation()
            vals = [t.x, t.y, t.z] + [r[i][j] for i in range(3) for j in range(3)]
            poses.append('{"%s", "%s", cf(%s)}' % (bn, PARENT[bn], ', '.join(fmt(v) for v in vals)))
        frames.append('{%s, {%s}}' % (fmt((f - f0) / fps), ', '.join(poses)))
    L.append('clip("%s_%s", %s, "%s", {%s})' % (PREFIJO, nombre, 'true' if bucle else 'false', PRIORIDAD[nombre][0], ',\n\t'.join(frames)))
    resumen.append('%s_%s %d claves' % (PREFIJO, nombre, len(frames)))
L.append('print("Animaciones creadas en ServerStorage.LUTO_Animaciones: %s")' % ', '.join(resumen))
with open(OUT_LUA, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write('\n'.join(L) + '\n')
print('[AP] exportado', OUT_LUA, resumen)

# lo mismo como modelo de Roblox (.rbxmx) para insertarlo sin pegar nada: clic derecho > Insertar > Importar modelo Roblox
ref = [0]
def item(cls, props, hijos=()):
    ref[0] += 1
    return '<Item class="%s" referent="RBX%d"><Properties>%s</Properties>%s</Item>' % (cls, ref[0], ''.join(props), ''.join(hijos))
def cfxml(vals):
    keys = ['X', 'Y', 'Z', 'R00', 'R01', 'R02', 'R10', 'R11', 'R12', 'R20', 'R21', 'R22']
    return '<CoordinateFrame name="CFrame">%s</CoordinateFrame>' % ''.join('<%s>%s</%s>' % (k, fmt(v), k) for k, v in zip(keys, vals))
seqs = []
for act in sorted(bpy.data.actions, key=lambda a: a.name):
    nombre = act.name.split('.')[0]
    if nombre not in ('Reposo', 'Caminar', 'Atacar', 'Caer'):
        continue
    A.set_action(rig, act)
    f0, f1 = (int(round(v)) for v in act.frame_range)
    kfs = []
    for f in (range(f0, f1 + 1, PASO) if (f1 - f0) % PASO == 0 else list(range(f0, f1, PASO)) + [f1]):
        bpy.context.scene.frame_set(f)
        def pose(bn):
            hijos = [pose(c.name) for c in rig.data.bones[bn].children]
            if bn == 'HumanoidRootPart':
                vals, peso = [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1], '0'
            else:
                mb = rig.pose.bones[bn].matrix_basis
                r = M @ mb.to_3x3() @ M.transposed()
                t = M @ mb.to_translation()
                vals, peso = [t.x, t.y, t.z] + [r[i][j] for i in range(3) for j in range(3)], '1'
            return item('Pose', ['<string name="Name">%s</string>' % bn, cfxml(vals), '<float name="Weight">%s</float>' % peso,
                                 '<token name="EasingStyle">0</token>', '<token name="EasingDirection">0</token>'], hijos)
        kfs.append(item('Keyframe', ['<string name="Name">Keyframe</string>', '<float name="Time">%s</float>' % fmt((f - f0) / fps)],
                        [pose('HumanoidRootPart')]))
    seqs.append(item('KeyframeSequence', ['<string name="Name">%s_%s</string>' % (PREFIJO, nombre),
                                          '<bool name="Loop">%s</bool>' % ('true' if nombre in ('Reposo', 'Caminar') else 'false'),
                                          '<token name="Priority">%d</token>' % PRIORIDAD[nombre][1]], kfs))
xml = ('<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" version="4">' +
       item('Folder', ['<string name="Name">LUTO_Animaciones_%s</string>' % PREFIJO], seqs) + '</roblox>')
OUT_XML = os.path.splitext(OUT_LUA)[0] + '.rbxmx'
with open(OUT_XML, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(xml)
print('[AP] exportado', OUT_XML)
