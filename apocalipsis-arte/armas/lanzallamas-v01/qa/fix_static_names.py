"""Reexportacion puntual de nombres; no regenera geometria, atlas ni renders."""
import sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'fuentes'))
import ap_lib as A
import ap_armas as W
from clip_contacts import reset_pose
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Lanzallamas.blend'))
rig=bpy.data.objects['Lanzallamas_Mundo'];reset_pose(rig)
parts=[bpy.data.objects[n] for n in ('Handle','Cartucho','Cierre')]
cst,stat=W.static_copies(parts)
names=[o.name for o in parts]
for o in parts:o.name+='_rig'
for o,n in zip(stat,names):o.name=n
A.export_fbx(str(ROOT/'Lanzallamas_Estatico.fbx'),stat)
A.export_glb(str(ROOT/'Lanzallamas_Estatico.glb'),stat)
W.remove_collection(cst)
print('STATIC_NAMES_FIXED',names)
