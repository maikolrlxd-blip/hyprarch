# Place de prueba de «+1 de lanzamiento por segundo» sin Rojo: la place del mapa v01 en piezas (mas1-arte/mapa-v01/roblox) con los
# scripts del juego colocados como los pondria Rojo segun default.project.json (src -> ReplicatedStorage.Mas1, server ->
# ServerScriptService.Mas1Servidor, client -> StarterPlayer.StarterPlayerScripts.Mas1Cliente; .server.lua = Script,
# .client.lua = LocalScript, .lua = ModuleScript). Se abre en Studio con File > Open from File: es un archivo local, no sube nada.
# Uso (desde mas1-juego): python tools/construir_place.py   ->   build/Mas1-prueba.rbxlx
import json
import os
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

JUEGO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPA = os.path.join(JUEGO, '..', 'mas1-arte', 'mapa-v01', 'roblox', 'Mapa-v01-prueba.rbxlx')
SALIDA = os.path.join(JUEGO, 'build', 'Mas1-prueba.rbxlx')
SUFIJOS = (('.server.lua', 'Script'), ('.client.lua', 'LocalScript'), ('.lua', 'ModuleScript'))
n = [0]


def ref():
    n[0] += 1
    return 'RBXJ%07X' % n[0]  # prefijo propio: no choca con los referentes del mapa


def cdata(s):
    return '<![CDATA[' + s.replace(']]>', ']]]]><![CDATA[>') + ']]>'


def item(clase, nombre, hijos=(), fuente=None):
    props = ['<string name="Name">%s</string>' % escape(nombre)]
    if fuente is not None:
        props.append('<ProtectedString name="Source">%s</ProtectedString>' % cdata(fuente))
    return ['<Item class="%s" referent="%s">' % (clase, ref()), '<Properties>'] + props + ['</Properties>'] + \
        [linea for h in hijos for linea in h] + ['</Item>']


def carpeta(ruta, nombre):
    hijos = []
    for f in sorted(os.listdir(ruta)):
        p = os.path.join(ruta, f)
        if os.path.isdir(p):
            hijos.append(carpeta(p, f))
            continue
        for sufijo, clase in SUFIJOS:
            if f.endswith(sufijo):
                hijos.append(item(clase, f[:-len(sufijo)], fuente=open(p, encoding='utf-8').read()))
                break
    return item('Folder', nombre, hijos)


def nodo(nombre, d):
    if '$path' in d:
        return carpeta(os.path.join(JUEGO, d['$path']), nombre)
    return item(d['$className'], nombre, [nodo(k, v) for k, v in d.items() if not k.startswith('$')])


arbol = json.load(open(os.path.join(JUEGO, 'default.project.json'), encoding='utf-8'))['tree']
servicios = [linea for k, v in arbol.items() if not k.startswith('$') for linea in nodo(k, v)]
texto = open(MAPA, encoding='utf-8').read()
assert texto.rstrip().endswith('</roblox>')
texto = texto.rstrip()[:-len('</roblox>')] + '\n'.join(servicios) + '\n</roblox>\n'
os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
with open(SALIDA, 'w', encoding='utf-8', newline='\n') as f:
    f.write(texto)
raiz = ET.parse(SALIDA).getroot()  # comprobacion: XML bien formado y cuantos scripts hay de cada clase
cuenta = {}
for it in raiz.iter('Item'):
    if it.get('class') in ('Script', 'LocalScript', 'ModuleScript'):
        cuenta[it.get('class')] = cuenta.get(it.get('class'), 0) + 1
print('place:', os.path.relpath(SALIDA, JUEGO), '%.1f MB' % (os.path.getsize(SALIDA) / 1e6), cuenta)
