# Place de prueba de «+1 de lanzamiento por segundo» sin Rojo: la place del mapa v01 en piezas (mas1-arte/mapa-v01/roblox) con los
# scripts del juego colocados como los pondria Rojo segun default.project.json (src -> ReplicatedStorage.Mas1, server ->
# ServerScriptService.Mas1Servidor, client -> StarterPlayer.StarterPlayerScripts.Mas1Cliente; .server.lua = Script,
# .client.lua = LocalScript, .lua = ModuleScript; un "$path" a un .rbxmx mete ese modelo, como Rojo: assets/MAS1_Modelos.rbxmx son
# las mallas de mascotas y alas que usa client/Seguidores.client.lua). Se abre en Studio con File > Open from File: es un archivo
# local, no sube nada (las mallas del .rbxmx ya estan subidas a la cuenta de Maikol).
# Uso (desde mas1-juego): python tools/construir_place.py   ->   build/Mas1-prueba.rbxlx
import json
import os
import re
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


COMPARTIDAS = []  # bloques <SharedStrings> de los .rbxmx (datos de malla que las piezas citan por su md5)


def modelo_rbxmx(ruta):
    """El modelo de un .rbxmx guardado desde Studio, con los referentes renombrados (M + el suyo) para que no choquen con los del
    mapa; sus SharedStrings se guardan aparte y van al final de la place."""
    texto = open(ruta, encoding='utf-8').read()
    m = re.search(r'<SharedStrings>(.*?)</SharedStrings>', texto, re.S)
    if m:
        COMPARTIDAS.append(m.group(1))
        texto = texto[:m.start()] + texto[m.end():]
    cuerpo = texto[texto.index('<Item '):texto.rindex('</roblox>')]
    cuerpo = re.sub(r'referent="(RBX[0-9A-Fa-f]+)"', r'referent="M\1"', cuerpo)
    cuerpo = re.sub(r'(<Ref name="[^"]*">)(RBX[0-9A-Fa-f]+)(</Ref>)', r'\1M\2\3', cuerpo)
    return [cuerpo]


def nodo(nombre, d):
    if '$path' in d and d['$path'].endswith('.rbxmx'):
        return modelo_rbxmx(os.path.join(JUEGO, d['$path']))
    if '$path' in d:
        return carpeta(os.path.join(JUEGO, d['$path']), nombre)
    return item(d['$className'], nombre, [nodo(k, v) for k, v in d.items() if not k.startswith('$')])


def placa(nombre, x, z, color):
    """Placa de 14 x 14 sobre el carril, junto al SpawnLocation (Z = -182): las zonas de entrenamiento que lee el servidor."""
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    props = ['<bool name="Anchored">true</bool>', '<token name="TopSurface">0</token>', '<token name="BottomSurface">0</token>',
             '<CoordinateFrame name="CFrame"><X>%g</X><Y>0.2</Y><Z>%g</Z><R00>1</R00><R01>0</R01><R02>0</R02><R10>0</R10><R11>1</R11>'
             '<R12>0</R12><R20>0</R20><R21>0</R21><R22>1</R22></CoordinateFrame>' % (x, z),
             '<Color3uint8 name="Color3uint8">%d</Color3uint8>' % ((0xFF << 24) | (r << 16) | (g << 8) | b),
             '<token name="Material">288</token>', '<string name="Name">%s</string>' % nombre,
             '<Vector3 name="size"><X>14</X><Y>0.4</Y><Z>14</Z></Vector3>', '<token name="shape">1</token>']
    return ['<Item class="Part" referent="%s">' % ref(), '<Properties>'] + props + ['</Properties>', '</Item>']


arbol = json.load(open(os.path.join(JUEGO, 'default.project.json'), encoding='utf-8'))['tree']
servicios = [linea for k, v in arbol.items() if not k.startswith('$') for linea in nodo(k, v)]
texto = open(MAPA, encoding='utf-8').read()
assert texto.rstrip().endswith('</roblox>')
# el SpawnLocation de la place del mapa (Z = -182, al principio del carril) sobra: el spawn es el del lobby (server/Lobby.server.lua)
# y aquel se quedaba como una losa blanca en mitad de la Pradera (prueba del 31/10)
sp = texto.find('<Item class="SpawnLocation"')
if sp >= 0:
    texto = texto[:sp] + texto[texto.index('</Item>', sp) + len('</Item>'):]
# zonas de entrenamiento de prueba (en el juego de verdad iran en la Pradera): dentro del Workspace, tras sus propiedades
ws = texto.index('<Item class="Workspace"')
fin = texto.index('</Properties>', ws) + len('</Properties>')
placas = []  # las zonas de entreno ahora las crea server/Lobby.server.lua
texto = texto[:fin] + '\n' + '\n'.join(placas) + texto[fin:]
texto = texto.rstrip()[:-len('</roblox>')] + '\n'.join(servicios) + '\n</roblox>\n'
if COMPARTIDAS:  # los datos de malla de los .rbxmx, en el bloque SharedStrings de la place (uno solo, al final)
    if '<SharedStrings>' in texto:
        texto = texto.replace('</SharedStrings>', ''.join(COMPARTIDAS) + '</SharedStrings>', 1)
    else:
        texto = texto.replace('\n</roblox>\n', '\n<SharedStrings>' + ''.join(COMPARTIDAS) + '</SharedStrings>\n</roblox>\n')
os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
with open(SALIDA, 'w', encoding='utf-8', newline='\n') as f:
    f.write(texto)
raiz = ET.parse(SALIDA).getroot()  # comprobacion: XML bien formado y cuantos scripts hay de cada clase
cuenta = {}
for it in raiz.iter('Item'):
    if it.get('class') in ('Script', 'LocalScript', 'ModuleScript'):
        cuenta[it.get('class')] = cuenta.get(it.get('class'), 0) + 1
print('place:', os.path.relpath(SALIDA, JUEGO), '%.1f MB' % (os.path.getsize(SALIDA) / 1e6), cuenta)
