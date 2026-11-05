# Todos los scripts del juego tienen que compilar. Studio solo los lee al abrir la place y un error de sintaxis deja un cliente o el
# servidor sin arrancar; esto lo pilla antes con el analizador de Lua de lupa. Los scripts son Luau, que añade `x += y` y `continue`
# (los dos se aplican antes de compilar, solo para comprobar la sintaxis); lo demas de Luau (tipos, `if` como expresion, cadenas con
# comillas invertidas, `::`) no se usa en el juego, y si alguien lo mete esta prueba lo avisa para decidir si se amplía.
# Ejecutar desde mas1-juego: python tests/test_sintaxis.py
import glob
import re
import lupa

l = lupa.LuaRuntime()
carga = l.eval('function(c, n) local f, e = load(c, n) return f ~= nil, e end')
NO_SOPORTADO = [(re.compile(r'`'), 'cadena con comillas invertidas'), (re.compile(r'::\s*[A-Za-z_]'), 'conversion de tipo (::)'),
                (re.compile(r'\)\s*:\s*[A-Za-z_]+\s*\n'), 'tipo de retorno'), (re.compile(r'\bexport\s+type\b|\btype\s+[A-Z]\w*\s*='), 'declaracion de tipo')]


def sin_comentarios(c):
    c = re.sub(r'--\[\[.*?\]\]', '', c, flags=re.S)
    return re.sub(r'--[^\n]*', '', c)


n = 0
for ruta in sorted(glob.glob('src/*.lua') + glob.glob('client/*.lua') + glob.glob('server/*.lua')):
    c = open(ruta, encoding='utf-8').read()
    limpio = sin_comentarios(re.sub(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'', '""', c))   # las cadenas y comentarios no cuentan
    for patron, que in NO_SOPORTADO:
        assert not patron.search(limpio), (ruta, 'usa Luau que esta prueba no sabe comprobar:', que)
    c = re.sub(r'([\w\.\[\]"]+)\s*([+\-*/])=\s*', r'\1 = \1 \2 ', c)   # x += y  ->  x = x + y
    c = re.sub(r'\bcontinue\b', 'do end', c)
    ok, err = carga(c, ruta)
    assert ok, (ruta, err)
    n += 1
assert n >= 30, n
print('ok (%d scripts compilan)' % n)
