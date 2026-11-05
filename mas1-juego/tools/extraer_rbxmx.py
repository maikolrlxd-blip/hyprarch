# Saca una instancia (con todo lo que cuelga de ella) de una place .rbxlx guardada por Studio a un modelo .rbxmx, con las SharedStrings
# que cita (datos de malla). Sirve para guardar en assets/ lo que se importa en Studio sin el menú «Guardar en un archivo»: se importa,
# se coloca, Ctrl+S y esto. Las referencias (Ref) que apuntan fuera de la instancia quedan en null.
#   python tools/extraer_rbxmx.py build/Mas1-prueba.rbxlx ReplicatedStorage/MAS1_Equipo assets/MAS1_Equipo.rbxmx
import sys
import xml.etree.ElementTree as ET


def nombre(it):
    props = it.find('Properties')
    for c in props if props is not None else ():
        if c.get('name') == 'Name':
            return c.text
    return None


def buscar(raiz, ruta):
    actual = None
    for i, paso in enumerate(ruta.split('/')):
        hijos = (raiz if actual is None else actual).findall('Item')
        actual = next((h for h in hijos if nombre(h) == paso or (i == 0 and h.get('class') == paso)), None)
        assert actual is not None, 'no está ' + ruta
    return actual


def extraer(place, ruta, salida):
    raiz = ET.parse(place).getroot()
    it = buscar(raiz, ruta)
    propios = {x.get('referent') for x in it.iter('Item')}
    for r in it.iter('Ref'):
        if r.text not in propios:
            r.text = 'null'
    usados = {s.text for s in it.iter('SharedString') if s.get('name')}
    todas = raiz.find('SharedStrings')
    compartidas = [s for s in (todas if todas is not None else ()) if s.get('md5') in usados]
    faltan = usados - {s.get('md5') for s in compartidas}
    assert not faltan, ('SharedStrings que no están en la place', faltan)
    partes = ['<roblox xmlns:xmime="http://www.w3.org/2005/05/xmlmime" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
              'xsi:noNamespaceSchemaLocation="http://www.roblox.com/roblox.xsd" version="4">',
              '<External>null</External>', '<External>nil</External>', ET.tostring(it, encoding='unicode')]
    if compartidas:
        partes += ['<SharedStrings>'] + [ET.tostring(s, encoding='unicode') for s in compartidas] + ['</SharedStrings>']
    partes.append('</roblox>')
    open(salida, 'w', encoding='utf-8', newline='\n').write('\n'.join(partes) + '\n')
    clases = {}
    for x in it.iter('Item'):
        clases[x.get('class')] = clases.get(x.get('class'), 0) + 1
    print('rbxmx:', salida, clases, 'SharedStrings', len(compartidas))


if __name__ == '__main__':
    extraer(*sys.argv[1:4])
