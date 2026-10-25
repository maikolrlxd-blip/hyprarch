"""Run in Blender background on Zombi_Quemado.blend; no asset upload.

The HRP is an anchored preview root. Fold its authored movement into the
LowerTorso pose so QuemadoCaer keeps its floor correction in Motor6D playback.
"""
import sys, json, math
from pathlib import Path
import bpy
from mathutils import Matrix

OUT = Path(sys.argv[sys.argv.index('--') + 1])
OUT.mkdir(parents=True, exist_ok=True)
rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
M = Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0)))
clips = {}
order = []
def visit(b):
    for c in b.children:
        order.append(c.name)
        visit(c)
visit(rig.data.bones['HumanoidRootPart'])

for act in sorted(bpy.data.actions, key=lambda a:a.name):
    if act.name not in ('QuemadoInicio','QuemadoBucle','QuemadoCaer'):
        continue
    rig.animation_data_clear()
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    rig.animation_data_create()
    rig.animation_data.action = act
    rig.animation_data.action_slot = act.slots[0]
    start, end = [round(x) for x in act.frame_range]
    frames = []
    for f in sorted(set(list(range(start, end + 1, 2)) + [end])):
        bpy.context.scene.frame_set(f)
        poses = []
        for n in order:
            pb = rig.pose.bones[n]
            mb = pb.matrix_basis.copy()
            if n == 'LowerTorso':
                mb = pb.bone.matrix_local.inverted() @ pb.matrix
            t = M @ mb.translation
            r = M @ mb.to_3x3() @ M.transposed()
            values = list(t) + [r[i][j] for i in range(3) for j in range(3)]
            assert all(math.isfinite(v) for v in values)
            poses.append([n, pb.parent.name, values])
        frames.append([(f-start)/bpy.context.scene.render.fps, poses])
    clips[act.name] = {'loop':act.name == 'QuemadoBucle','frames':frames}

assert len(clips)==3
(OUT/'clips.json').write_text(json.dumps(clips,indent=2),encoding='utf-8')
ref = 0
def item(cls,props,children=''):
    global ref
    ref += 1
    return f'<Item class="{cls}" referent="FIRE{ref}"><Properties>{props}</Properties>{children}</Item>'
def string(k,v):return f'<string name="{k}">{v}</string>'
seqs=[]
for name, clip in clips.items():
    keyframes=[]
    for time, poses in clip['frames']:
        data={n:(parent,values) for n,parent,values in poses}
        def pose(n):
            values=[0,0,0,1,0,0,0,1,0,0,0,1] if n=='HumanoidRootPart' else data[n][1]
            cf='<CoordinateFrame name="CFrame">'+''.join(f'<{k}>{v:.8g}</{k}>' for k,v in zip(['X','Y','Z','R00','R01','R02','R10','R11','R12','R20','R21','R22'],values))+'</CoordinateFrame>'
            children=''.join(pose(c) for c,(parent,_) in data.items() if parent==n)
            return item('Pose',string('Name',n)+cf+f'<float name="Weight">{0 if n=="HumanoidRootPart" else 1}</float><token name="EasingStyle">0</token>',children)
        keyframes.append(item('Keyframe',string('Name','Keyframe')+f'<float name="Time">{time:.8g}</float>',pose('HumanoidRootPart')))
    seqs.append(item('KeyframeSequence',string('Name',name)+f'<bool name="Loop">{str(clip["loop"]).lower()}</bool><token name="Priority">3</token>',''.join(keyframes)))
(OUT/'Quemado-local.rbxmx').write_text('<roblox version="4">'+item('Folder',string('Name','QuemadoClips'),''.join(seqs))+'</roblox>',encoding='utf-8')
print('LUTO_EXPORT', {n:len(v['frames']) for n,v in clips.items()})
print('ROOT_FOLDED', clips['QuemadoCaer']['frames'][-1][1][0])
