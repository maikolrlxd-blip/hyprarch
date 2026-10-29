# Hoja de contacto con las tres mascotas altas v02 juntas (3/4, cara, lateral y aleteo recogiendo de cada una), para compararlas.
# blender -b --factory-startup -P hoja_mascotas_altas.py
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mas1_lib import *

D = os.path.abspath(os.path.join(HERE, '..', 'mascotas-altas-v02'))
PIEZAS = (('aguila-legendaria', 'Aguila-legendaria', 'AGUILA'), ('grifo-mitico', 'Grifo-mitico', 'GRIFO'), ('fenix', 'Fenix', 'FENIX'))
items = []
for vista, etiqueta in (('tres-cuartos', '3/4'), ('cara', 'CARA'), ('lateral', 'LATERAL'), ('aleteo-recogida', 'ALETEO RECOGIENDO')):
    for sub, pref, nombre in PIEZAS:
        ruta = os.path.join(D, sub, 'previews', '%s-%s.jpg' % (pref, vista))
        if os.path.exists(ruta):
            items.append((ruta, '%s %s' % (nombre, etiqueta)))
W.contact_sheet(items, 3, os.path.join(D, '_fam.png'), title='MASCOTAS ALTAS V02 - AGUILA, GRIFO Y FENIX (RENDERS DE BLENDER)')
a_jpg(os.path.join(D, '_fam.png'), os.path.join(D, 'Mascotas-altas-v02-hoja.jpg'), 0.5)
print('HOJA LISTA')
