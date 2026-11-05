# La place de prueba que genera tools/construir_place.py (build/Mas1-prueba.rbxlx) tiene que ser algo que Studio abra y que traiga todo
# lo que el juego espera. Ya nos paso que Studio se negaba a abrirla porque dos modelos (.rbxmx) declaraban la misma SharedString
# («duplicate declared shared string»). Aqui: XML bien formado, SharedStrings declaradas una sola vez y todas las citadas existen,
# referentes unicos, los scripts de src/client/server dentro con su codigo, y los modelos de MAS1_Modelos, MAS1_Equipo (y
# MAS1_Enemigos si ya esta) con sus mallas y huesos. Ejecutar despues de tools/construir_place.py, desde mas1-juego:
# python tests/test_place.py
import glob
import os
import sys
import xml.etree.ElementTree as ET

RUTA = os.environ.get('PLACE', 'build/Mas1-prueba.rbxlx')
if not os.path.exists(RUTA):
    print('salto: no hay', RUTA, '(ejecuta tools/construir_place.py)')
    sys.exit(0)
raiz = ET.parse(RUTA).getroot()


def nombre(it):
    return next((c.text for c in it.find('Properties') if c.get('name') == 'Name'), None)


# SharedStrings: declaradas una vez cada una; las que citan las propiedades existen
declaradas = [s.get('md5') for s in (raiz.find('SharedStrings') if raiz.find('SharedStrings') is not None else [])]
assert len(declaradas) == len(set(declaradas)), ('SharedStrings declaradas dos veces', len(declaradas) - len(set(declaradas)))
citadas = {s.text.strip() for s in raiz.iter('SharedString') if s.get('name')}
assert citadas <= set(declaradas), ('SharedStrings citadas que no existen', list(citadas - set(declaradas))[:3])

# referentes unicos y referencias que apuntan a algo que existe
refs = [it.get('referent') for it in raiz.iter('Item')]
assert len(refs) == len(set(refs)), ('referentes repetidos', len(refs) - len(set(refs)))
existentes = set(refs)
for r in raiz.iter('Ref'):
    assert r.text.strip() in existentes or r.text.strip() == 'null', ('Ref a un referente que no existe', r.get('name'), r.text)


def hijos(ruta_servicio):
    """Los Items de un servicio por su nombre de clase, y dentro, por nombres."""
    s = next(it for it in raiz.findall('Item') if it.get('class') == ruta_servicio)
    return s


rs = hijos('ReplicatedStorage')
por_nombre = {nombre(it): it for it in rs.findall('Item')}
assert 'Mas1' in por_nombre and 'MAS1_Modelos' in por_nombre and 'MAS1_Equipo' in por_nombre, sorted(por_nombre)

# los modulos de src/*.lua estan dentro de Mas1 con su codigo
esperados = {os.path.basename(f)[:-4] for f in glob.glob('src/*.lua')}
dentro = {nombre(it): it for it in por_nombre['Mas1'].findall('Item')}
assert esperados <= set(dentro), ('faltan modulos en la place', sorted(esperados - set(dentro)))
for n in esperados:
    fuente = next(c.text for c in dentro[n].find('Properties') if c.get('name') == 'Source')
    assert fuente and len(fuente) > 100, ('modulo vacio', n)

# los scripts de client y server
for carpeta, servicio in (('client', 'StarterPlayer'), ('server', 'ServerScriptService')):
    scripts = [nombre(it) for it in hijos(servicio).iter('Item') if it.get('class') in ('LocalScript', 'Script', 'ModuleScript')]
    for f in glob.glob(carpeta + '/*.lua'):
        n = os.path.basename(f)[:-4].replace('.client', '').replace('.server', '')
        assert n in scripts, ('falta en la place', f, n)


def modelos(carpeta):
    out = {}
    for m in por_nombre[carpeta].iter('Item'):
        if m.get('class') == 'Model':
            piezas = [p for p in m.iter('Item') if p.get('class') == 'MeshPart']
            huesos = {nombre(b) for b in m.iter('Item') if b.get('class') == 'Bone'}
            for p in piezas:   # cada malla apunta a un recurso subido (o lleva su malla dentro)
                prop = {c.get('name'): c for c in p.find('Properties')}
                malla = prop.get('MeshId')
                assert malla is not None and (malla.findtext('url') or '').strip().startswith('rbxassetid://'), ('malla sin recurso', nombre(m), nombre(p))
            out[nombre(m)] = (len(piezas), huesos)
    return out


mod = modelos('MAS1_Modelos')
assert {'gorrion', 'golondrina', 'nube', 'globo', 'nubarron', 'ovni', 'meteorito', 'cometa', 'aguila', 'grifo', 'fenix',
        'iniciales', 'roboticas', 'avanzadas'} <= set(mod), sorted(mod)
assert 'Tip_R' in mod['avanzadas'][1] and 'Wing_L' in mod['iniciales'][1] and 'Lid_R' in mod['aguila'][1]
equipo = modelos('MAS1_Equipo')
assert equipo['Canon'][0] >= 20 and {'Root', 'Barrel', 'Lever'} <= equipo['Canon'][1], equipo
if 'MAS1_Enemigos' in por_nombre:   # cuando se importen los 6 enemigos
    en = modelos('MAS1_Enemigos')
    assert {'globo', 'nube', 'nubarron', 'cometa', 'ovni', 'meteorito'} <= set(en), sorted(en)
    for t, (n, huesos) in en.items():
        assert n >= 1 and {'Body', 'Lid_R', 'Lid_L'} <= huesos, (t, huesos)
print('ok (%d referentes, %d SharedStrings, %d modulos, %d modelos de mascotas y alas)' % (len(refs), len(declaradas), len(esperados), len(mod)))
