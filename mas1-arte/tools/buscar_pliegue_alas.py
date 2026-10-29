# Busca poses plegadas compactas para las alas avanzadas v0.2 con una cinematica directa en numpy (cada vertice sigue un solo hueso).
# blender -b --factory-startup -P buscar_pliegue_alas.py   (lee AlasAvanzadas_v02.blend; solo escribe en la salida estandar)
import bpy, math, json, random
import numpy as np

OUT = r"C:\Users\maiko\slime-rush\hyprarch\mas1-arte\alas-avanzadas-v02\AlasAvanzadas_v02.blend"
bpy.ops.wm.open_mainfile(filepath=OUT)
ob = bpy.data.objects['AlasAvanzadas']
rig = bpy.data.objects['AlasAvanzadas_Rig']
V = np.array([v.co[:] for v in ob.data.vertices], dtype=np.float64)
gi = {g.index: g.name for g in ob.vertex_groups}
grp = np.array([gi[v.groups[0].group] for v in ob.data.vertices])
head = {b.name: np.array(b.head_local[:], dtype=np.float64) for b in rig.data.bones}
par = {b.name: (b.parent.name if b.parent else None) for b in rig.data.bones}


def Rxyz(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def M4(R, h):
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3] = h - R @ h
    return M


def evaluar(p):
    """p = (wr, wy, wp, mr, my, mp, tr, ty, tp) en grados, convenio de pose(): aleteo, barrido, cabeceo del ala derecha."""
    wr, wy, wp, mr, my, mp, tr, ty, tp = [math.radians(a) for a in p]
    pts = []
    for s, suf in ((1, 'R'), (-1, 'L')):
        mats = {}
        for nm, (rr, yy, pp) in (('Wing', (wr, wy, wp)), ('Mid', (mr, my, mp)), ('Tip', (tr, ty, tp))):
            b = '%s_%s' % (nm, suf)
            Rb = Rxyz(pp, s * rr, -s * yy)
            mats[b] = M4(Rb, head[b])
        chain = {}
        for nm in ('Wing', 'Mid', 'Tip'):
            b = '%s_%s' % (nm, suf)
            M = mats[b]
            q = par[b]
            while q and q in mats:
                M = mats[q] @ M
                q = par[q]
            chain[b] = M
        for b, M in chain.items():
            sel = V[grp == b]
            if len(sel):
                pts.append((sel @ M[:3, :3].T) + M[:3, 3])
    return np.vstack(pts + [V[grp == 'Root']])


def metricas(p):
    P = evaluar(p)
    return dict(x=float(np.abs(P[:, 0]).max()), ymin=float(P[:, 1].min()), ymax=float(P[:, 1].max()), zmin=float(P[:, 2].min()),
                zmax=float(P[:, 2].max()))


def coste(m):
    c = 0.0
    c += max(0.0, -m['ymin'] - 2.2) * 3.0                      # que no sobresalga mas de 2,2 studs por detras
    c += max(0.0, m['ymax'] - 0.0) * 6.0                       # nada por delante de la espalda
    c += max(0.0, -3.55 - m['zmin']) * 6.0                     # que no baje del suelo (el maniqui esta en -3,8)
    c += max(0.0, m['x'] - 1.5) * 3.0                          # estrecho
    c += max(0.0, m['zmax'] - 2.6) * 1.0
    return c


print('reposo', metricas((0,) * 9))
print('F1 actual', metricas((22, 70, 0, 28, 8, 0, 34, 10, 0)))
random.seed(7)
rng = [(0, 70), (0, 100), (-40, 40), (0, 100), (-30, 60), (-30, 40), (0, 110), (-30, 80), (-40, 60)]
mejores = []
for i in range(60000):
    p = tuple(random.uniform(a, b) for a, b in rng)
    m = metricas(p)
    mejores.append((coste(m), p, m))
    if len(mejores) > 400:
        mejores.sort(key=lambda t: t[0])
        mejores = mejores[:100]
mejores.sort(key=lambda t: t[0])
for c, p, m in mejores[:3]:
    print('COSTE %.3f' % c, tuple(round(a, 1) for a in p), {k: round(v, 2) for k, v in m.items()})


def coste2(p):
    m = metricas(p)
    v = max(0.0, -m['ymin'] - 2.6) + max(0.0, m['ymax'] + 0.02) * 2 + max(0.0, -3.7 - m['zmin']) + max(0.0, m['x'] - 1.5) + max(0.0, m['zmax'] - 2.7)
    return v * 10 + 0.004 * sum(abs(a) for a in p), m


finales = []
for c, p, m in mejores[:40]:
    cur = list(p)
    cc, mm = coste2(cur)
    paso = 8.0
    while paso > 0.5:
        mejoro = False
        for _ in range(60):
            q = [a + random.uniform(-paso, paso) * (random.random() < 0.5) for a in cur]
            q = [min(max(a, lo), hi) for a, (lo, hi) in zip(q, rng)]
            c2, m2 = coste2(q)
            if c2 < cc:
                cur, cc, mm, mejoro = q, c2, m2, True
        if not mejoro:
            paso *= 0.5
    finales.append((cc, cur, mm))
finales.sort(key=lambda t: t[0])
vistos = []
for cc, p, m in finales:
    if any(max(abs(a - b) for a, b in zip(p, q)) < 6 for q in vistos):
        continue
    vistos.append(p)
    print('FINAL %.3f' % cc, tuple(round(a, 1) for a in p), {k: round(v, 2) for k, v in m.items()})
    if len(vistos) >= 6:
        break
