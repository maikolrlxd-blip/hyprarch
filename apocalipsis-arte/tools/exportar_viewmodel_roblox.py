# Viewmodel de primera persona de un arma para Luto (Roblox): piezas, montaje con Motor6D y clips como KeyframeSequence.
# El rig _VM de cada arma tiene un hueso raiz "Camara" en el origen (la camara), "Arma" y los brazos R15, y cada malla va
# rigida a un solo hueso. En Roblox: una pieza por hueso con el nombre del hueso, una pieza invisible "Raiz" en la camara
# (PrimaryPart: el script del juego hace PivotTo(cam.CFrame)) y un Motor6D por hueso cuyo marco de union es el hueso en
# reposo pasado a ejes de Roblox (J = M * reposo). Con ese marco, la pose de cada clave es directamente matrix_basis.
# blender -b <Arma>.blend --python-exit-code 1 -P exportar_viewmodel_roblox.py -- <carpeta_salida> <id>   (id: pistola, escopeta, subfusil)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Matrix, Vector
import ap_lib as A
import ap_armas as W

args = sys.argv[sys.argv.index('--') + 1:]
OUT, ID = args[0], args[1]
os.makedirs(os.path.join(OUT, 'integracion'), exist_ok=True)
PASO = 2                                   # claves cada 2 fotogramas de 60 fps (30 fps)
M = Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0)))
M4 = M.to_4x4()
# Reposo puede seguir sonando debajo del resto; el script del juego tambien fija estas prioridades al cargar
PRIORIDAD = {'Reposo': 0}                  # Idle; el resto Action (2)

vm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o.name.endswith('_VM')][0]
NOMBRE = vm.name[:-3]                      # Pistola9mm, Escopeta, Subfusil
fps = bpy.context.scene.render.fps
huesos = [b.name for b in vm.data.bones]
padre = {b.name: (b.parent.name if b.parent else None) for b in vm.data.bones}

# ------------------------------------------------------------------ piezas en reposo, una por hueso
vm.data.pose_position = 'REST'
mallas = [o for o in bpy.data.objects if o.type == 'MESH' and any(m.type == 'ARMATURE' and m.object == vm for m in o.modifiers)]
por_hueso = {}
for o in mallas:
    assert len(o.vertex_groups) == 1, o.name
    por_hueso.setdefault(o.vertex_groups[0].name, []).append(o)
dup = [h for h, os_ in por_hueso.items() if len(os_) > 1]
assert not dup, 'huesos con varias mallas: %s' % dup
for o in list(bpy.data.objects):           # libera los nombres de hueso (brazos LeftHand..., piezas del modelo de mundo) para que las copias no salgan con ".001"
    if o in mallas or o.name in por_hueso:
        o.name = o.name + '__orig'
renombre = {os_[0].name: h for h, os_ in por_hueso.items()}
coll, piezas = W.static_copies(mallas, 'TMP_VM_Roblox', rename=renombre)
assert sorted(p.name for p in piezas) == sorted(por_hueso), [p.name for p in piezas]
fbx = os.path.join(OUT, '%s_VM_Roblox.fbx' % NOMBRE)
A.export_fbx(fbx, piezas)
centros = {}
for p in piezas:                           # centro de la caja de cada pieza en ejes de Roblox (donde el importador pone el MeshPart)
    mn, mx = W.bounds([p])
    centros[p.name] = M @ ((mn + mx) / 2)
W.remove_collection(coll)

# ------------------------------------------------------------------ montaje en Studio (barra de comandos)
def cf(mat):                               # Matrix 4x4 de Roblox -> CFrame.new(x,y,z, r00..r22)
    t = mat.to_translation(); r = mat.to_3x3()
    vals = [t.x, t.y, t.z] + [r[i][j] for i in range(3) for j in range(3)]
    return 'CFrame.new(%s)' % ', '.join('%.5f' % v for v in vals)

union = {}                                 # marco de union de cada hueso en reposo, en ejes de Roblox
for b in vm.data.bones:
    union[b.name] = M4 @ vm.matrix_world @ b.matrix_local
orden = []
def visitar(n):
    for h in huesos:
        if padre[h] == n:
            orden.append(h); visitar(h)
visitar(None)
ref = 'Arma'
L = ['-- Generado por tools/exportar_viewmodel_roblox.py: no editar a mano.',
     '-- Barra de comandos de Studio, con el Model importado de %s_VM_Roblox.fbx SELECCIONADO.' % NOMBRE,
     '-- Lo deja como plantilla del viewmodel en ReplicatedStorage.LUTO_VM.%s: PrimaryPart "Raiz" en la camara (origen),' % ID,
     '-- una pieza invisible "Camara" y un Motor6D por hueso (los clips son KeyframeSequence con esos mismos nombres).',
     'local m = game:GetService("Selection"):Get()[1]',
     'assert(m and m:IsA("Model"), "Selecciona el Model importado del viewmodel")',
     'for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Name = d.Name:gsub("^%s+", ""):gsub("%s+$", "") end end',
     'm.Name = "%s"' % ID,
     'local function pieza(n) local p = m:FindFirstChild(n, true); assert(p, "falta la pieza " .. n); return p end',
     '-- el importador 3D de Studio deja las mallas giradas 180 grados en Y respecto a Blender (comprobado el 2026-10-23 con el mapa,',
     '-- la zombi y estos viewmodels): se deshace girando las piezas alrededor del eje vertical de "%s"' % ref,
     'do local c = pieza("%s").Position; local rot = CFrame.new(c.X, 0, c.Z) * CFrame.Angles(0, math.pi, 0) * CFrame.new(-c.X, 0, -c.Z)' % ref,
     '\tfor _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.CFrame = rot * d.CFrame end end end',
     '-- el importador puede mover el modelo: se alinea con el centro esperado de "%s"' % ref,
     'local off = pieza("%s").Position - Vector3.new(%.5f, %.5f, %.5f)' % ((ref,) + tuple(centros[ref])),
     'local U = {']
for h in huesos:
    L.append('\t%s = %s,' % (h, cf(union[h])))
L += ['}',
      'for _, d in ipairs(m:GetDescendants()) do',
      '\tif d:IsA("BasePart") then d.Anchored = false; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false; d.Massless = true; d.CastShadow = false end',
      'end',
      'local function aux(nombre, marco) local p = Instance.new("Part"); p.Name = nombre; p.Size = Vector3.new(0.2, 0.2, 0.2); p.Transparency = 1',
      '\tp.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.Massless = true; p.CastShadow = false; p.CFrame = marco; p.Parent = m; return p end',
      'local raiz = aux("Raiz", CFrame.new(off))           -- la camara: ejes de Roblox sin giro (mira a -Z)',
      'aux("Camara", U.Camara + off)',
      'local function motor(hijo, padre_)',
      '\tlocal a, b = (padre_ and pieza(padre_) or raiz), pieza(hijo)',
      '\tlocal j = U[hijo] + off',
      '\tlocal mt = Instance.new("Motor6D"); mt.Name = hijo; mt.Part0 = a; mt.Part1 = b',
      '\tmt.C0 = a.CFrame:Inverse() * j; mt.C1 = b.CFrame:Inverse() * j; mt.Parent = b',
      'end']
for h in orden:
    L.append('motor("%s", %s)' % (h, ('"%s"' % padre[h]) if padre[h] else 'nil'))
L += ['raiz.Anchored = true                                 -- en la plantilla; el script del juego lo desancla y lo pega a la camara',
      'm.PrimaryPart = raiz; m.WorldPivot = raiz.CFrame',
      'local ctl = m:FindFirstChildOfClass("AnimationController") or Instance.new("AnimationController", m)',
      'if not ctl:FindFirstChildOfClass("Animator") then Instance.new("Animator", ctl) end',
      'local RS = game:GetService("ReplicatedStorage")',
      'local carpeta = RS:FindFirstChild("LUTO_VM") or Instance.new("Folder"); carpeta.Name = "LUTO_VM"; carpeta.Parent = RS',
      'local viejo = carpeta:FindFirstChild("%s"); if viejo and viejo ~= m then viejo.Parent = game:GetService("ServerStorage") end' % ID,
      'm.Parent = carpeta',
      'print("LUTO_VM.%s listo:", #m:GetDescendants(), "descendientes")' % ID]
lua = os.path.join(OUT, 'integracion', 'ArmarVM_%s.lua' % ID)
with open(lua, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(L) + '\n')

# ------------------------------------------------------------------ clips del viewmodel como KeyframeSequence (.rbxmx)
vm.data.pose_position = 'POSE'
ref_id = [0]
def item(cls, props, hijos=()):
    ref_id[0] += 1
    return '<Item class="%s" referent="RBX%d"><Properties>%s</Properties>%s</Item>' % (cls, ref_id[0], ''.join(props), ''.join(hijos))
def num(v):
    return ('%.5f' % v).rstrip('0').rstrip('.') if abs(v) > 1e-7 else '0'
def cfxml(mat):
    t = mat.to_translation(); r = mat.to_3x3()
    vals = [t.x, t.y, t.z] + [r[i][j] for i in range(3) for j in range(3)]
    keys = ['X', 'Y', 'Z', 'R00', 'R01', 'R02', 'R10', 'R11', 'R12', 'R20', 'R21', 'R22']
    return '<CoordinateFrame name="CFrame">%s</CoordinateFrame>' % ''.join('<%s>%s</%s>' % (k, num(v), k) for k, v in zip(keys, vals))
hijos_de = {h: [c for c in huesos if padre[c] == h] for h in huesos}
seqs, resumen = [], []
for act in sorted(bpy.data.actions, key=lambda a: a.name):
    if not act.name.startswith('VM_'):
        continue
    clip = act.name[3:]
    A.set_action(vm, act)
    f0, f1 = (int(round(v)) for v in act.frame_range)
    marcos = list(range(f0, f1 + 1, PASO))
    if marcos[-1] != f1:
        marcos.append(f1)
    kfs = []
    for fr in marcos:
        bpy.context.scene.frame_set(fr)
        def pose(h):
            mb = vm.pose.bones[h].matrix_basis
            return item('Pose', ['<string name="Name">%s</string>' % h, cfxml(mb), '<float name="Weight">1</float>',
                                 '<token name="EasingStyle">0</token>', '<token name="EasingDirection">0</token>'],
                        [pose(c) for c in hijos_de[h]])
        raiz = item('Pose', ['<string name="Name">Raiz</string>', cfxml(Matrix.Identity(4)), '<float name="Weight">0</float>',
                             '<token name="EasingStyle">0</token>', '<token name="EasingDirection">0</token>'],
                    [pose(h) for h in huesos if padre[h] is None])
        kfs.append(item('Keyframe', ['<string name="Name">Keyframe</string>', '<float name="Time">%s</float>' % num((fr - f0) / fps)], [raiz]))
    nombre = '%s_VM_%s' % (ID.capitalize(), clip)
    seqs.append(item('KeyframeSequence', ['<string name="Name">%s</string>' % nombre,
                                          '<bool name="Loop">%s</bool>' % ('true' if clip == 'Reposo' else 'false'),
                                          '<token name="Priority">%d</token>' % PRIORIDAD.get(clip, 2)], kfs))
    resumen.append('%s %d claves %.2f s' % (nombre, len(kfs), (f1 - f0) / fps))
xml = ('<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" version="4">' +
       item('Folder', ['<string name="Name">LUTO_Animaciones_VM_%s</string>' % ID], seqs) + '</roblox>')
rbxmx = os.path.join(OUT, 'integracion', 'Animaciones_VM_%s.rbxmx' % ID)
with open(rbxmx, 'w', encoding='utf-8', newline='\n') as f:
    f.write(xml)

# ------------------------------------------------------------------ arma de tercera persona: Tool con el modelo de mundo
# <NOMBRE>_Mundo_Estatico.fbx trae "Handle" (cuerpo) y las piezas sueltas en su sitio. El origen del FBX es el punto de
# agarre; eventos.json da el centro del Handle desde ese origen (ejes de Roblox). El Grip es ese punto de agarre en el
# espacio del Handle, con los ejes del arma: el canon (-Z) mira adelante con el brazo extendido (RightGripAttachment R15).
import json
ev = json.load(open(os.path.join(OUT, 'eventos.json'), encoding='utf-8'))
hc = ev['handle_centro_desde_origen']
T = ['-- Generado por tools/exportar_viewmodel_roblox.py: no editar a mano.',
     '-- Barra de comandos de Studio, con el Model importado de %s_Mundo_Estatico.fbx SELECCIONADO.' % NOMBRE,
     '-- Lo deja como Tool "%s" en ReplicatedStorage.LUTO_Armas (Handle + piezas soldadas; Grip en el punto de agarre).' % ID,
     'local m = game:GetService("Selection"):Get()[1]',
     'assert(m and m:IsA("Model"), "Selecciona el Model importado del arma de mundo")',
     'for _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.Name = d.Name:gsub("^%s+", ""):gsub("%s+$", "") end end',
     'local h = m:FindFirstChild("Handle", true); assert(h, "falta Handle")',
     '-- el importador 3D deja las mallas giradas 180 grados en Y (ver ArmarVM): se deshace alrededor del eje vertical del Handle',
     'do local c = h.Position; local rot = CFrame.new(c.X, 0, c.Z) * CFrame.Angles(0, math.pi, 0) * CFrame.new(-c.X, 0, -c.Z)',
     '\tfor _, d in ipairs(m:GetDescendants()) do if d:IsA("BasePart") then d.CFrame = rot * d.CFrame end end end',
     'local origen = h.Position - Vector3.new(%s, %s, %s)   -- punto de agarre (origen del FBX), desde eventos.json' % tuple(repr(v) for v in hc),
     'local tool = Instance.new("Tool"); tool.Name = "%s"; tool.RequiresHandle = true; tool.CanBeDropped = false; tool.ToolTip = "%s"' % (ID, ev.get('arma', NOMBRE)),
     'for _, d in ipairs(m:GetDescendants()) do',
     '\tif d:IsA("BasePart") then',
     '\t\td.Anchored = false; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false; d.Massless = true',
     '\t\tlocal cf = d.CFrame; d.Parent = tool; d.CFrame = cf',
     '\t\tif d ~= h then local w = Instance.new("WeldConstraint"); w.Part0 = h; w.Part1 = d; w.Parent = d end',
     '\tend',
     'end',
     'tool.Grip = h.CFrame:ToObjectSpace(CFrame.new(origen))',
     'local RS = game:GetService("ReplicatedStorage")',
     'local carpeta = RS:FindFirstChild("LUTO_Armas") or Instance.new("Folder"); carpeta.Name = "LUTO_Armas"; carpeta.Parent = RS',
     'local viejo = carpeta:FindFirstChild("%s"); if viejo then viejo.Parent = game:GetService("ServerStorage") end' % ID,
     'tool.Parent = carpeta; m.Parent = nil',
     'print("LUTO_Armas.%s listo: piezas", #tool:GetChildren(), "Grip", tool.Grip)' % ID]
tlua = os.path.join(OUT, 'integracion', 'ArmarTool_%s.lua' % ID)
with open(tlua, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(T) + '\n')
print('[AP] viewmodel', ID, fbx, lua, rbxmx, tlua)
for r in resumen:
    print('[AP]   ', r)
