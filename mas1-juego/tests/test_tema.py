# Guarda de client/Tema.lua: T.panel crea la sombra como HERMANA del panel (no hija), asi que tiene que seguir su visibilidad; si no,
# al ocultar un panel queda un recuadro oscuro vacio (lo que se vio en Studio el 05/11: el panel de misiones en vuelo, el contador de
# combo y los consejos). Comprueba ademas que todos los paneles que alguna vez se ocultan pasan por T.panel (y no se ocultan a mano
# junto a una sombra propia). Ejecutar desde mas1-juego: python tests/test_tema.py
import glob
import re

tema = open('client/Tema.lua', encoding='utf-8').read()
cuerpo = tema[tema.index('function T.panel'):]
cuerpo = cuerpo[:cuerpo.index('\nend\n')]
assert 'sombra.Visible = p.Visible' in cuerpo, 'T.panel: la sombra tiene que empezar con la visibilidad del panel'
assert re.search(r'p:GetPropertyChangedSignal\("Visible"\):Connect\(function\(\)\s*sombra\.Visible = p\.Visible', cuerpo), \
    'T.panel: la sombra tiene que seguir la visibilidad del panel'
assert 'return p, sombra' in cuerpo

ocultos = []
for ruta in sorted(glob.glob('client/*.lua')):
    s = open(ruta, encoding='utf-8').read()
    for m in re.finditer(r'local (\w+)(?:, \w+)? = T\.panel\([^\n]*Visible = false', s):
        ocultos.append((ruta, m.group(1)))
    assert 'sombra' not in s or ruta.endswith('Tema.lua'), (ruta, 'usa su propia sombra: que pase por T.panel')
print('ok: la sombra de T.panel sigue al panel; paneles que empiezan ocultos:', ', '.join(n for _, n in ocultos))
