import bpy,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'fuentes'))
import ap_lib as A
import ap_armas as W
data=json.loads((ROOT/'datos.json').read_text());errors=[];results=[]
def check(c,m):
    if not c:errors.append(m)
for name,info in data.items():
    for ext in ('fbx','glb'):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        if ext=='fbx':bpy.ops.import_scene.fbx(filepath=str(ROOT/'fbx'/f'{name}.fbx'))
        else:bpy.ops.import_scene.gltf(filepath=str(ROOT/'fbx'/f'{name}.glb'))
        obs=[o for o in bpy.data.objects if o.type=='MESH']
        check(len(obs)==1 and obs[0].name==name,f'{name}/{ext} objetos')
        tris=A.tris(obs);check(tris==info['triangles'] and tris<=1500,f'{name}/{ext} tris')
        for o in obs:
            me=o.data;me.calc_loop_triangles()
            check(len({i for p in me.polygons for i in p.vertices})==len(me.vertices),f'{name}/{ext} vertices sueltos')
            check(all(t.area>1e-12 for t in me.loop_triangles),f'{name}/{ext} degenerados')
            check(me.uv_layers.active is not None,f'{name}/{ext} UV')
            if me.uv_layers.active:check(all(math.isfinite(x) and -.0001<=x<=1.0001 for uv in me.uv_layers.active.data for x in uv.uv),f'{name}/{ext} UV invalidas')
        bbox=W.bounds(obs);dimensions=[bbox[1][i]-bbox[0][i] for i in range(3)]
        expected=[info['local_bounds'][1][i]-info['local_bounds'][0][i] for i in range(3)]
        # ap_lib exporta FBX con global_scale=.01. Medir ambas magnitudes;
        # normalizar no demuestra escala correcta en el importador de Roblox.
        scale=100 if ext=='fbx' else 1
        normalized=[d*scale for d in dimensions]
        check(max(abs(a-b) for a,b in zip(normalized,expected))<.002,f'{name}/{ext} orientacion/escala normalizada {normalized} vs {expected}')
        results.append({'asset':name,'format':ext,'triangles':tris,'raw_dimensions_blender':dimensions,'blender_roundtrip_normalization':scale,'dimensions_source_units':normalized})
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Hospital.blend'))
for name in data:
    ob=bpy.data.objects.get(name);check(ob is not None,'Falta pieza '+name)
    images={n.image for m in ob.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    check(len(images)==1 and all(i.packed_file and list(i.size)==[512,512] and len(i.pixels)>0 for i in images),'Atlas '+name)
report={'passed':not errors,'errors':errors,'scope':'Geometria/UV/texturas y reimportacion Blender. No colision/escala/FPS Roblox','imports':results}
(ROOT/'qa'/'VALIDACION.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('HOSPITAL_QA',json.dumps(report))
if errors:raise RuntimeError(errors)
