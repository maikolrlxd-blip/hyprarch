"""Cabeza propia de La Lamentadora v04, coordenadas de la base humana v02.

No ejecuta escena, exportacion ni renders al importarse. Frente +Y, arriba +Z.
build_head(A, collection) devuelve una sola malla Head con pelo incluido.
Regiones: piel/cara/pelo y labio/boca/ojo/diente. La boca y las orbitas
son aberturas de la superficie facial, con paredes internas; no decals negros.
Desactivar en face_x la boca y los ojos pintados antiguos para esta cabeza.
"""
import math
import bmesh
from mathutils import Vector


def build_head(A, CM):
    mb = A.MB('Head')
    tau = math.tau

    def vert(p):
        return mb.bm.verts.new(p)

    def loft(points, sections, material, sides=5, cap=True):
        pts = [Vector(p) for p in points]
        rings = []
        for k, (c, sec) in enumerate(zip(pts, sections)):
            direction = (pts[min(k + 1, len(pts) - 1)] - pts[max(k - 1, 0)]).normalized()
            front = Vector((0, 1, 0))
            front = (front - direction * front.dot(direction)).normalized()
            side = front.cross(direction)
            turn=.20*math.sin(k*1.3)
            rings.append([vert(c + side * (sec[0] * math.cos(tau * j / sides+turn)) +
                               front * (sec[1] * math.sin(tau * j / sides+turn)))
                          for j in range(sides)])
        for ra, rb in zip(rings[:-1], rings[1:]):
            for j in range(sides):
                mb.face((ra[j], ra[(j + 1) % sides], rb[(j + 1) % sides], rb[j]), material)
        if cap:
            mb.face(rings[0][::-1], material)
            mb.face(rings[-1], material)
        return rings

    # Secciones del craneo: mandibula afinada y torcida, pomulos y frente humanos.
    # Trece columnas frontales permitirian mas detalle, pero once dan una base
    # mas economica; los huecos se redondean en sus propios perimetros.
    specs = [
        (4.855, .100, .080, .130), (4.920, .180, .170, .090),
        (4.980, .225, .205, .060), (5.040, .252, .230, .040),
        (5.100, .268, .253, .025), (5.150, .280, .270, .015),
        (5.180, .285, .280, .008), (5.214, .289, .287, .003),
        (5.250, .292, .294, .000), (5.310, .294, .300, -.006),
        (5.400, .280, .298, -.012), (5.510, .230, .252, -.018),
        (5.600, .125, .140, -.020), (5.635, .035, .036, -.020)]
    fractions = [-1, -.77, -.56, -.42, -.23, 0, .23, .42, .56, .77, 1]
    rings = []

    def g(x, z, cx, cz, wx, wz):
        return math.exp(-((x - cx) / wx) ** 2 - ((z - cz) / wz) ** 2)

    def surface_y(x, z):
        low = specs[0]
        high = specs[-1]
        for a, b in zip(specs[:-1], specs[1:]):
            if a[0] <= z <= b[0]:
                low, high = a, b
                break
        t = max(0, min(1, (z - low[0]) / max(1e-8, high[0] - low[0])))
        rx, ry, yc = [low[j] * (1 - t) + high[j] * t for j in (1, 2, 3)]
        shift = .028 * max(0, min(1, (5.13 - z) / .24))
        xx = x - shift
        y = yc + ry * math.sqrt(max(0, 1 - (xx / rx) ** 2))
        # Puente/tip nasal real, reborde supraorbital, pomulos y mejillas hundidas.
        y += .103 * g(xx, z, 0, 5.155, .043, .092)
        for s in (-1, 1):
            y += .024 * g(xx, z, s * .120, 5.286 + s * .008, .075, .038)
            y += .029 * g(xx, z, s * .184, 5.155, .071, .060)
            y -= .026 * g(xx, z, s * .178, 5.063, .062, .064)
        return y

    for z, rx, ry, yc in specs:
        shift = .028 * max(0, min(1, (5.13 - z) / .24))
        rr = []
        for f in fractions:
            x = rx * f + shift
            rr.append(vert((x, surface_y(x, z), z)))
        # Back arc from right temple to left, endpoints already belong to front.
        for j in range(1, 8):
            th = -math.pi * j / 8
            rr.append(vert((rx * math.cos(th) + shift, yc + ry * math.sin(th), z)))
        rings.append(rr)

    # (low row, high row, left column, right column), inclusive perimeter.
    holes = [(1, 4, 4, 6, 'mouth'), (6, 8, 2, 4, 'left'), (6, 8, 6, 8, 'right')]
    for k in range(len(rings) - 1):
        for j in range(len(rings[k])):
            omit = any(r0 <= k < r1 and c0 <= j < c1 for r0, r1, c0, c1, _ in holes)
            if not omit:
                jn = (j + 1) % len(rings[k])
                region = 'cara' if j < 10 and k < 10 else 'piel'
                mb.face((rings[k][j], rings[k][jn], rings[k + 1][jn], rings[k + 1][j]), region)
    mb.face(rings[0][::-1], 'piel')
    mb.face(rings[-1], 'piel')

    def perimeter(r0, r1, c0, c1):
        return ([(r0, j) for j in range(c0, c1 + 1)] +
                [(k, c1) for k in range(r0 + 1, r1 + 1)] +
                [(r1, j) for j in range(c1 - 1, c0 - 1, -1)] +
                [(k, c0) for k in range(r1 - 1, r0, -1)])

    for r0, r1, c0, c1, kind in holes:
        indices = perimeter(r0, r1, c0, c1)
        border, angles = [], []
        cx = .027 if kind == 'mouth' else (-.113 if kind == 'left' else .113)
        cz = 5.005 if kind == 'mouth' else (5.214 + (-.004 if kind == 'left' else .006))
        rx, rz = (.082, .080) if kind == 'mouth' else (.068, .040 if kind=='left' else .026)
        for row, col in indices:
            th = math.atan2(2 * (row - r0) / (r1 - r0) - 1,
                            2 * (col - c0) / (c1 - c0) - 1)
            irregular = 1 + (.14 * math.sin(3 * th + .6) if kind == 'mouth' else .035 * math.sin(3 * th))
            x = cx + rx * math.cos(th) * irregular
            z = cz + rz * math.sin(th) * irregular + (x - cx) * (.30 if kind == 'mouth' else .07)
            v = rings[row][col]
            v.co = (x, surface_y(x, z) + .002, z)
            border.append(v)
            angles.append(th)
        rim, back = [], []
        for v, th in zip(border, angles):
            if kind == 'mouth':
                rim.append(vert((cx + (v.co.x - cx) * .85, v.co.y - .022, cz + (v.co.z - cz) * .88)))
                back.append(vert((cx + (v.co.x - cx) * .63, .115, cz + (v.co.z - cz) * .66)))
            else:
                rim.append(vert((cx + (v.co.x - cx) * .83, v.co.y - .028, cz + (v.co.z - cz) * .76)))
                back.append(vert((cx + (v.co.x - cx) * .58, v.co.y - .063, cz + (v.co.z - cz) * .54)))
        for j in range(len(border)):
            jn = (j + 1) % len(border)
            mb.face((border[j], border[jn], rim[jn], rim[j]), 'labio' if kind == 'mouth' else 'cara')
            mb.face((rim[j], rim[jn], back[jn], back[j]), 'boca')
        mb.face(back, 'boca')
        if kind != 'mouth':
            # Tiny clouded human eye lies INSIDE socket; right eye more occluded.
            eye_x = cx + (.008 if kind == 'left' else -.006)
            eye_z = cz - .006
            ey = surface_y(cx, cz) - .041
            ex = .033 if kind == 'left' else .021
            ez = .014 if kind == 'left' else .008
            ev = [vert((eye_x + ex * math.cos(tau * j / 8), ey + .005 * math.sin(math.pi * j / 8),
                        eye_z + ez * math.sin(tau * j / 8))) for j in range(8)]
            mb.face(ev[::-1], 'ojo')
            # Pupila e iris dentro del ojo, sin esfera saliente ni brillo plastico.
            ix = eye_x + (.004 if kind == 'left' else -.004)
            iz = eye_z + .001
            irx, irz = (.010, .012) if kind == 'left' else (.007, .006)
            for material, width, height, depth, sides, dx, dz in (
                ('iris', irx, irz, .008, 8, 0, 0),
                ('pupila', irx*.39, irz*.43, .010, 6, 0, 0),
                ('reflejo', .0017, .0020, .012, 4, -.0025, .0030)):
                vv=[vert((ix+dx+width*math.cos(tau*j/sides),ey+depth,
                          iz+dz+height*math.sin(tau*j/sides))) for j in range(sides)]
                mb.face(vv[::-1],material)

    # Discrete nose alae and nostrils, below the mesh's sculpted central bridge.
    for s in (-1, 1):
        x, z = s * .026, 5.119
        y = surface_y(x, z) + .002
        ev = [vert((x + .008 * math.cos(tau * j / 6), y,
                    z + .005 * math.sin(tau * j / 6))) for j in range(6)]
        mb.face(ev[::-1], 'boca')

    # Dientes pequenos con profundidad, desiguales; todos dentro de la cavidad.
    for j,x in enumerate((-.023,-.002,.020,.041,.060)):
        ztop=5.063-.004*j
        length=(.021,.029,.025,.019,.015)[j]
        loft([(x,.211,ztop),(x+.002,.218,ztop-length)],
             [(.008,.006),(.006,.005)],'diente',sides=4)
    for x in (.009,.033):
        loft([(x,.192,4.952),(x-.002,.201,4.963)],
             [(.007,.005),(.005,.004)],'diente',sides=4)

    # Ears with an inset inner concha, tucked in silhouette beneath the hair.
    for s in (-1, 1):
        ex, ey, ez = s * .280, -.006, 5.175
        outer = [vert((ex + s * .034 * math.cos(tau * j / 8), ey + .032 * math.cos(tau * j / 8),
                       ez + .076 * math.sin(tau * j / 8))) for j in range(8)]
        inn = [vert((ex + s * .012 * math.cos(tau * j / 8), ey + .006,
                     ez + .047 * math.sin(tau * j / 8))) for j in range(8)]
        for j in range(8):
            mb.face((outer[j], outer[(j + 1) % 8], inn[(j + 1) % 8], inn[j]), 'piel')
        mb.face(inn, 'labio')

    # Broken hairline and rounded locks. No sheet/helmet over the actual face.
    hr = []
    for k, (z, rx, ry) in enumerate(((5.695, .045, .055), (5.655, .180, .200),
                                    (5.550, .280, .310), (5.420, .309, .331))):
        ring = []
        for j in range(14):
            th = tau * j / 14
            zz = z
            if k == 3:
                zz += .045 * max(0, math.sin(th)) - .035 * max(0, -math.sin(th))
                zz += .013 * math.cos(3 * th)
            ring.append(vert((rx * math.cos(th), -.025 + ry * math.sin(th), zz)))
        hr.append(ring)
    for ra, rb in zip(hr[:-1], hr[1:]):
        for j in range(14):
            mb.face((ra[j], ra[(j + 1) % 14], rb[(j + 1) % 14], rb[j]), 'pelo')
    mb.face(hr[0][::-1], 'pelo')

    # Six back locks overlap slightly at roots, separate into pointed irregular ends.
    for i in range(6):
        th = math.pi + math.pi * (i + .5) / 6
        x, y = .265 * math.cos(th), -.025 + .285 * math.sin(th)
        length = 1.45 + .13 * math.sin(1.7 * i)
        points, secs = [], []
        for k in range(6):
            t = k / 5
            points.append((x * (1 + .34 * t) + .074 * math.sin(5 * t + i),
                           y - .11 * t + .070 * math.sin(6 * t + .7 * i),
                           5.54 - length * t))
            width = (.083 * (1 - .58 * t) + .014 * math.sin(math.pi * t)) if k < 5 else .008
            secs.append((width, width * .62))
        loft(points, secs, 'pelo', sides=5)

    # Side locks expose the cheekbones and upper jaw rather than forming straight boards.
    for s in (-1, 1):
        for i in range(2):
            points, secs = [], []
            for k in range(6):
                t = k / 5
                points.append((s * (.258 + .075 * t + .070 * math.sin(5 * t + i)),
                               .065 + .155 * t - i * .13 + .060 * math.sin(5.6 * t + i),
                               5.52 - (1.25 + .22 * i + .05 * s) * t))
                w = .061 * (1 - .47 * t) if k < 5 else .006
                secs.append((w, w * .72))
            loft(points, secs, 'pelo', sides=5)
    # An oblique fringe falls near the right eye, not over both facial landmarks.
    loft([(.080, .205, 5.602), (.152, .285, 5.483), (.193, .299, 5.350),
          (.211, .280, 5.215), (.225, .245, 5.108)],
         [(.053, .027), (.057, .026), (.044, .022), (.028, .016), (.004, .004)], 'pelo', sides=5)

    # Vertices inside omitted grid cells are not used; remove them before validation.
    unused = [v for v in mb.bm.verts if not v.link_faces]
    if unused:
        bmesh.ops.delete(mb.bm, geom=unused, context='VERTS')
    ob = mb.finish(CM, recalc=True)
    # Large silhouette remains faceted, surface shading soft enough for skin/hair.
    for p in ob.data.polygons:
        p.use_smooth = True
    ob['head_design'] = 'Human anatomy; recessed eye sockets and twisted internal mouth; non-gory'
    ob['head_landmarks'] = 'eyes x+-0.113 z5.214; nose z5.155; mouth x0.020 z5.005; jaw x+0.028'
    ob['head_regions_new'] = 'labio,boca,ojo,diente,iris,pupila,reflejo'
    return ob
