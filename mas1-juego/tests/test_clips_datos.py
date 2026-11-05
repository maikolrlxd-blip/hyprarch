# Los datos generados por mas1-arte/tools/clips_a_lua.py (src/ClipsHuesos.lua y, cuando existan, ClipsEnemigos.lua y ClipsEquipo.lua)
# tienen que encajar con los modelos de Roblox guardados en assets/*.rbxmx: cada hueso que anima un clip existe en su modelo, cada
# hueso trae exactamente 7 numeros por fotograma, los cuaterniones estan normalizados y los clips duran algo. Si se reimporta un
# modelo y no se vuelve a pasar clips_a_lua.py, esta prueba lo avisa antes de verlo en Studio (un hueso que no existe se queda sin
# animar en silencio). Ejecutar desde mas1-juego: python tests/test_clips_datos.py
import math
import os
import xml.etree.ElementTree as ET
import lupa

l = lupa.LuaRuntime()


def huesos_y_piezas(ruta):
    """{modelo: ({huesos}, {mallas})} de un .rbxmx guardado desde Studio."""
    def nombre(it):
        return next(c.text for c in it.find('Properties') if c.get('name') == 'Name')
    r = {}
    for m in ET.parse(ruta).getroot().iter('Item'):
        if m.get('class') == 'Model':
            r[nombre(m)] = ({nombre(b) for b in m.iter('Item') if b.get('class') == 'Bone'},
                            {nombre(p) for p in m.iter('Item') if p.get('class') in ('MeshPart', 'Part')})
    return r


def revisar(modulo, rbxmx, motor=False):
    if not (os.path.exists(modulo) and os.path.exists(rbxmx)):
        print('salto', os.path.basename(modulo), '(aun no existe)')
        return 0
    datos = l.execute(open(modulo, encoding='utf-8').read())
    clips = datos.clips if motor else datos
    modelos = huesos_y_piezas(rbxmx)
    n_clips = 0
    for id_, por_clip in clips.items():
        assert id_ in modelos, (modulo, 'sin modelo', id_)
        huesos, piezas = modelos[id_]
        assert len(list(por_clip.items())) > 0, (id_, 'sin clips')
        for nombre, clip in por_clip.items():
            n, dur = clip.n, clip.dur
            assert n >= 2 and 0.05 < dur < 20, (id_, nombre, n, dur)
            assert len(list(clip.huesos.items())) > 0, (id_, nombre, 'ningun hueso animado')
            for hueso, v in clip.huesos.items():
                assert hueso in huesos, (id_, nombre, 'el modelo no tiene el hueso', hueso, sorted(huesos))
                nums = [x for _, x in v.items()]
                assert len(nums) == n * 7, (id_, nombre, hueso, len(nums), n * 7)
                for i in range(n):
                    q = nums[i * 7 + 3:i * 7 + 7]
                    assert abs(math.sqrt(sum(c * c for c in q)) - 1) < 2e-3, (id_, nombre, hueso, i, q)
                    assert all(abs(c) < 50 for c in nums[i * 7:i * 7 + 3]), (id_, nombre, hueso, i, 'desplazamiento enorme')
            n_clips += 1
        if motor:   # cada pieza que se mueve va con un hueso que existe y que el clip anima o es la raiz
            for pieza, hueso in datos.piezas[id_].items():
                assert pieza in piezas, (id_, 'el modelo no tiene la pieza', pieza)
                assert hueso in huesos, (id_, pieza, 'va con un hueso que no existe', hueso)
    return n_clips


total = revisar('src/ClipsHuesos.lua', 'assets/MAS1_Modelos.rbxmx')
total += revisar('src/ClipsEnemigos.lua', 'assets/MAS1_Enemigos.rbxmx')
total += revisar('src/ClipsEquipo.lua', 'assets/MAS1_Equipo.rbxmx', motor=True)
assert total >= 14
# lo que usan los scripts: cada pieza con alas tiene Flap y Glide; cada mascota, Fly; cada enemigo, Idle, Hit, Defeat y Blink
H = l.execute(open('src/ClipsHuesos.lua', encoding='utf-8').read())
for alas in ('iniciales', 'roboticas', 'avanzadas'):
    assert H[alas].Flap is not None and H[alas].Glide is not None, alas
for m in ('gorrion', 'golondrina', 'nube', 'globo', 'nubarron', 'ovni', 'meteorito', 'cometa', 'aguila', 'grifo', 'fenix'):
    assert H[m].Fly is not None, m
if os.path.exists('src/ClipsEnemigos.lua'):
    E = l.execute(open('src/ClipsEnemigos.lua', encoding='utf-8').read())
    for t in ('globo', 'nube', 'nubarron', 'cometa', 'ovni', 'meteorito'):
        for c in ('Idle', 'Hit', 'Defeat', 'Blink'):
            assert E[t][c] is not None, (t, c)
print('ok (%d clips revisados)' % total)
