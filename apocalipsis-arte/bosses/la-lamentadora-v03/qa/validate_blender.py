"""Verifica entrega Blender/FBX en proceso independiente. No prueba Roblox."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent.parent
report={'scope':'Blender y reimportacion FBX; no Roblox Studio ni comportamiento jugable','errors':[],'warnings':[]}
def require(cond,message):
    if not cond:report['errors'].append(message)
def bounds(obs):
    points=[ob.matrix_world@v.co for ob in obs for v in ob.data.vertices]
    mn=[min(v[i] for v in points) for i in range(3)]
    mx=[max(v[i] for v in points) for i in range(3)]
    return {'min':mn,'max':mx,'size':[mx[i]-mn[i] for i in range(3)]}
def metrics(obs):
    result=[]
    for ob in obs:
        me=ob.data; me.calc_loop_triangles()
        used={vi for poly in me.polygons for vi in poly.vertices}
        deg=sum(1 for t in me.loop_triangles if t.area<1e-12)
        uv=me.uv_layers.active
        uvbad=sum(1 for it in uv.data if any(not math.isfinite(x) or x<-.0001 or x>1.0001 for x in it.uv)) if uv else -1
        badpos=sum(1 for v in me.vertices if not all(math.isfinite(x) for x in v.co))
        require(len(used)==len(me.vertices),ob.name+': vertices sueltos')
        require(deg==0,ob.name+': triangulos degenerados')
        require(uvbad==0,ob.name+': UV no finitas/fuera de rango/ausentes')
        require(badpos==0,ob.name+': coordenadas no finitas')
        result.append({'name':ob.name,'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'loose':len(me.vertices)-len(used),'degenerate':deg,'uv_bad':uvbad})
    return result

bpy.ops.wm.open_mainfile(filepath=str(ROOT/'LaLamentadora.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
obs=[o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
require(len(obs)==15,'Se esperaban las 15 piezas del rig')
require(rig.animation_data.action is None,'Archivo guardado con accion activa')
require(all(pb.location.length<1e-6 and sum(abs(x) for x in pb.rotation_euler)<1e-6 and (pb.scale-Vector((1,1,1))).length<1e-6 for pb in rig.pose.bones),'Archivo no guardado en pose neutral')
report['blender']={'meshes':metrics(obs),'bones':len(rig.data.bones),'bounds':bounds(obs)}
tri=sum(m['triangles'] for m in report['blender']['meshes'])
require(tri<=3000,'Presupuesto de 3000 triangulos excedido')
report['blender']['triangles_total']=tri
badweights=[]
for ob in obs:
    for v in ob.data.vertices:
        gs=[g for g in v.groups if g.weight>0]
        if abs(sum(g.weight for g in gs)-1)>1e-5 or any(ob.vertex_groups[g.group].name not in rig.data.bones for g in gs):badweights.append((ob.name,v.index))
require(not badweights,'Pesos incorrectos')
report['blender']['bad_weights']=badweights
report['actions']={a.name:{'frame_range':list(a.frame_range),'seconds':(a.frame_range[1]-a.frame_range[0])/bpy.context.scene.render.fps} for a in bpy.data.actions}
require(all(n in report['actions'] for n in ['Reposo','Caminar','Atacar','Caer']),'Faltan clips')
textures=[i for i in bpy.data.images if i.type=='IMAGE' and '_Color' in i.name]
report['textures']=[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in textures]
require(len(textures)==4 and all(i.packed_file for i in textures),'Texturas no empacadas')
contact=json.loads((ROOT/'qa'/'CONTACTO-CAIDA.json').read_text())
require(contact['passed'],'Caer atraviesa suelo en muestreo')
report['fall_contact']={k:contact[k] for k in ['passed','before_min_z','after_min_z','verification_step_frames']}

basebounds=report['blender']['bounds']['size']
report['fbx_reimport']=[]
for fn in ['LaLamentadora_Estatico.fbx','LaLamentadora.fbx','clips/LaLamentadora_Caer.fbx']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(ROOT/fn),use_anim=True)
    ms=[o for o in bpy.data.objects if o.type=='MESH']
    rigs=[o for o in bpy.data.objects if o.type=='ARMATURE']
    for r in rigs:
        r.animation_data_clear(); r.data.pose_position='REST'
    bpy.context.view_layer.update()
    data={'file':fn,'meshes':metrics(ms),'bounds':bounds(ms),'bones':sum(len(r.data.bones) for r in rigs),'actions':[a.name for a in bpy.data.actions]}
    require(len(ms)==15,fn+': faltan piezas')
    require(sum(m['triangles'] for m in data['meshes'])==tri,fn+': difiere geometria')
    expected=[x*.01 for x in basebounds]
    require(all(abs(a-b)<.0001 for a,b in zip(data['bounds']['size'],expected)),fn+': dimensiones distintas a conversion .01 esperada en Blender')
    report['fbx_reimport'].append(data)
report['warnings'].append('El cabello esta unido a Head; aun no tiene movimiento independiente.')
report['warnings'].append('Contacto Caer valida ausencia de penetracion muestreada, no la calidad visual de la caida ni fisica Roblox.')
report['passed']=not report['errors']
(ROOT/'qa'/'VALIDACION-BLENDER.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('BOSS_VALIDATION',json.dumps({'passed':report['passed'],'errors':report['errors'],'triangles':tri}))
if report['errors']:raise RuntimeError('Fallo validacion Blender, ver JSON')
