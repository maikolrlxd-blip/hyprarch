#!/usr/bin/env python3
"""Taller IA: espacio compartido para que varias IAs (Claude, ChatGPT/Codex, Antigravity...)
se pasen modelos, animaciones y renders y se corrijan entre ellas en tiempo real.

  python3 taller.py serve            # visor web (127.0.0.1:8770) donde TU ves y apruebas
  python3 taller.py mcp --as claude  # servidor MCP (stdio) para una IA; --as = su nombre

Solo biblioteca estandar. Datos en ~/.taller-ia (o TALLER_DIR).
"""
import argparse
import base64
import contextlib
import hashlib
import json
import mimetypes
import os
import re
import secrets
import shutil
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

HERE = Path(getattr(sys, "_MEIPASS", None) or Path(__file__).resolve().parent)  # _MEIPASS = recursos dentro del .exe
DIR = Path(os.environ.get("TALLER_DIR", Path.home() / ".taller-ia"))
MAX_ROUNDS = int(os.environ.get("TALLER_MAX_ROUNDS", "6"))
MAX_BYTES = 200 * 1024 * 1024
KINDS = {".glb": "model", ".gltf": "model", ".fbx": "model", ".png": "image", ".jpg": "image",
         ".jpeg": "image", ".webp": "image", ".gif": "image", ".json": "note", ".md": "note", ".txt": "note"}
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._ -]{0,63}$")
AUTHOR_RE = re.compile(r"^[a-z0-9_-]{1,24}$")


# ---------------- almacen (carpeta + registro de eventos) ----------------

@contextlib.contextmanager
def lock():
    DIR.mkdir(parents=True, exist_ok=True)
    path = DIR / ".lock"
    end = time.time() + 15
    while True:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            with contextlib.suppress(OSError):
                if time.time() - path.stat().st_mtime > 10:  # cerradura huerfana
                    path.unlink()
            if time.time() > end:
                raise RuntimeError("almacen ocupado")
            time.sleep(0.03)
    try:
        yield
    finally:
        os.close(fd)
        with contextlib.suppress(OSError):
            path.unlink()


def meta_path(name): return DIR / "assets" / name / "meta.json"


def load(name):
    p = meta_path(name)
    if not p.exists():
        raise KeyError(f"no existe el recurso '{name}'")
    return json.loads(p.read_text("utf-8"))


def save(meta):
    p = meta_path(meta["name"])
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=1), "utf-8")
    os.replace(tmp, p)


def events(since=0):
    p = DIR / "events.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text("utf-8").splitlines():
        with contextlib.suppress(ValueError):
            e = json.loads(line)
            if e["id"] > since:
                out.append(e)
    return out


def last_id():
    ev = events(0)
    return ev[-1]["id"] if ev else 0


def emit(type_, asset, author, summary, v=None):  # llamar dentro de lock()
    e = {"id": last_id() + 1, "ts": round(time.time(), 2), "type": type_, "asset": asset, "v": v,
         "author": author, "summary": summary[:300]}
    with open(DIR / "events.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return e


STATES = ("ok", "busy", "limit", "away")

ROLES = {
    "director": ("Director / planificador", ["planificar", "repartir tareas", "revisar y corregir", "integrar", "informar al humano"]),
    "modelador": ("Modelador 3D", ["modelado 3D dificil", "topologia", "correcciones de forma", "rigs"]),
    "animador": ("Animador", ["animaciones", "clips", "rigs", "movimiento y tiempos"]),
    "ingeniero": ("Ingeniero", ["Luau y codigo de Roblox", "Studio/Blender por MCP", "integracion y pruebas", "revision de codigo"]),
    "artista": ("Direccion de arte", ["critica visual", "referencias", "UI e imagenes", "investigacion de contexto largo"]),
}
COMMON = ["programar", "revisar codigo", "investigar", "escribir"]  # TODAS las IAs saben esto
DEFAULT_ROLE = {"claude": "director", "opus": "modelador", "chatgpt": "ingeniero", "codex": "ingeniero", "antigravity": "artista"}
TSTATUS = ("todo", "doing", "review", "done", "blocked")


def tasks_all():
    p = DIR / "tasks.json"
    return json.loads(p.read_text("utf-8")) if p.exists() else []


def _save_tasks(ts):
    tmp = DIR / "tasks.tmp"
    tmp.write_text(json.dumps(ts, ensure_ascii=False, indent=1), "utf-8")
    os.replace(tmp, DIR / "tasks.json")


def role_of(who):
    return presence_all().get(who, {}).get("role") or DEFAULT_ROLE.get(who, "")


def availability(who):
    c = presence_all().get(who)
    if not c:
        return False
    return c.get("state", "ok") == "ok" and time.time() - c.get("last_seen", 0) < 180


def skills_of(who):
    """Fortaleza del rol + habilidades comunes + las que el director/humano le haya anadido."""
    c = presence_all().get(who, {})
    r = c.get("role") or DEFAULT_ROLE.get(who, "")
    return sorted(set(ROLES.get(r, ("", []))[1]) | set(COMMON) | set(c.get("skills", [])))


def load_of(who):
    return sum(1 for t in tasks_all() if t["assignee"] == who and t["status"] in ("todo", "doing", "review", "blocked"))


def alternatives(assignee, needs=""):
    """Quien puede cubrir: cualquiera disponible que sepa lo que pide la tarea (todas saben programar),
    ordenado primero por afinidad con el rol del asignado y luego por menos carga."""
    want = {needs.lower()} if needs else set(skills_of(assignee))
    cands = []
    for w in presence_all():
        if w == assignee or not availability(w):
            continue
        ov = len({x.lower() for x in skills_of(w)} & want)
        if ov:
            cands.append((-ov, load_of(w), w))
    return [w for _, _, w in sorted(cands)]


def task_create(author, title, detail="", assignee="", asset="", needs=""):
    if not title.strip():
        raise ValueError("falta el titulo")
    if assignee and not AUTHOR_RE.match(assignee):
        raise ValueError("assignee invalido")
    if assignee and assignee != author and role_of(author) != "director" and author != "humano":
        raise ValueError("solo el director (o el humano) puede asignar tareas a otras IAs; deja assignee vacio o pon el tuyo")
    with lock():
        ts = tasks_all()
        t = {"id": (max([x["id"] for x in ts]) + 1) if ts else 1, "title": title[:120], "detail": detail[:2000],
             "assignee": assignee, "asset": asset, "needs": needs[:40], "status": "todo", "by": author, "notes": [],
             "created": time.strftime("%Y-%m-%dT%H:%M:%S"), "updated": time.strftime("%Y-%m-%dT%H:%M:%S")}
        ts.append(t)
        _save_tasks(ts)
        emit("task", asset, author, f"tarea #{t['id']} '{t['title']}'" + (f" -> {assignee}" if assignee else " (sin asignar)"))
    warn = ""
    if assignee and assignee != "humano" and not availability(assignee):
        alt = alternatives(assignee, needs)
        warn = f" AVISO: {assignee} no esta disponible ahora (limite, ocupada o sin senal)." + (f" Pueden cubrir (por afinidad y menos carga): {', '.join(alt)}." if alt else " No hay nadie mas disponible con esa habilidad.")
    return t, warn


def task_update(author, tid, status=None, note="", assignee=None):
    with lock():
        ts = tasks_all()
        t = next((x for x in ts if x["id"] == tid), None)
        if not t:
            raise ValueError(f"no existe la tarea #{tid}")
        is_dir = role_of(author) == "director" or author == "humano"
        if assignee is not None and assignee != t["assignee"]:
            if not is_dir:
                raise ValueError("solo el director (o el humano) puede reasignar")
            t["assignee"] = assignee
        elif not is_dir and t["assignee"] not in ("", author):
            raise ValueError(f"la tarea #{tid} es de {t['assignee']}")
        elif not is_dir and not t["assignee"]:
            t["assignee"] = author  # quien toma una tarea libre se la queda
        if status:
            if status not in TSTATUS:
                raise ValueError("status debe ser " + ", ".join(TSTATUS))
            t["status"] = status
        if note:
            t["notes"].append({"by": author, "text": note[:500], "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
        t["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        _save_tasks(ts)
        emit("task", t["asset"], author, f"tarea #{tid} '{t['title']}' -> {t['status']}" + (f" ({note})" if note else ""))
    return t


def presence_all():
    p = DIR / "presence.json"
    return json.loads(p.read_text("utf-8")) if p.exists() else {}


def touch(who, state=None, note=None, reset_at=None, by=None, role=None, skills=None):
    """Latido: cada llamada de una IA actualiza 'visto por ultima vez'. Si cambia el estado, emite un evento."""
    if state is not None and state not in STATES:
        raise ValueError("state debe ser ok, busy, limit o away")
    with lock():
        pr = presence_all()
        cur = pr.get(who, {"state": "ok", "note": "", "reset_at": ""})
        old = cur.get("state")
        cur["last_seen"] = round(time.time(), 1)
        if role:
            if role not in ROLES:
                raise ValueError("rol invalido: " + ", ".join(ROLES))
            cur["role"] = role
        if skills is not None:
            cur["skills"] = [str(x)[:30] for x in skills][:12]
        if not role and not cur.get("role") and who in DEFAULT_ROLE:
            cur["role"] = DEFAULT_ROLE[who]
        if state is not None:
            cur.update(state=state, note=(note or "")[:200], reset_at=(reset_at or "")[:60], by=by or who)
        pr[who] = cur
        tmp = DIR / "presence.tmp"
        tmp.write_text(json.dumps(pr, ensure_ascii=False), "utf-8")
        os.replace(tmp, DIR / "presence.json")
        if state is not None and state != old:
            emit("status", "", who, f"{who} ahora: {state}" + (f" ({note})" if note else "") + (f" — vuelve {reset_at}" if reset_at else ""))
    return cur


def check_name(name):
    if not NAME_RE.match(name or ""):
        raise ValueError("nombre invalido: usa letras, numeros, espacio . _ - (max 64)")


def assets_summary():
    out = []
    root = DIR / "assets"
    for d in sorted(root.iterdir()) if root.exists() else []:
        with contextlib.suppress(Exception):
            m = load(d.name)
            last = m["versions"][-1]
            out.append({"name": m["name"], "kind": m["kind"], "status": m["status"], "versions": len(m["versions"]),
                        "latest_author": last["author"], "updated": last["created"],
                        "open_changes": sum(1 for r in m["reviews"] if r["v"] == last["v"] and r["verdict"] == "changes")})
    return out


def _store_file(name, v, filename, data=None, src=None):
    d = DIR / "assets" / name / f"v{v}"
    d.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", filename)[:80] or "archivo"
    dst = d / safe
    if src is not None:
        shutil.copyfile(src, dst)
    else:
        dst.write_bytes(data)
    return safe


def publish(author, name, file_path=None, content_base64=None, filename=None, preview_path=None,
            preview_base64=None, description="", kind=None):
    check_name(name)
    if file_path:
        src = Path(file_path).expanduser()
        if not src.is_file():
            raise ValueError(f"no existe el archivo: {file_path}")
        if src.stat().st_size > MAX_BYTES:
            raise ValueError("archivo mayor de 200 MB")
        filename = src.name
        data = None
    elif content_base64 and filename:
        data = base64.b64decode(content_base64)
        if len(data) > MAX_BYTES:
            raise ValueError("archivo mayor de 200 MB")
        src = None
    else:
        raise ValueError("indica file_path, o content_base64 + filename")
    ext = Path(filename).suffix.lower()
    kind = kind or KINDS.get(ext)
    if kind not in ("model", "image", "note", "animation"):
        raise ValueError(f"tipo no soportado ({ext}). Usa .glb .gltf .fbx .png .jpg .json .md")
    with lock():
        try:
            meta = load(name)
        except KeyError:
            meta = {"name": name, "kind": kind, "status": "in_review", "versions": [], "reviews": [], "round_limit": MAX_ROUNDS}
            meta_path(name).parent.mkdir(parents=True, exist_ok=True)
        v = len(meta["versions"]) + 1
        if v > meta["round_limit"]:
            raise ValueError(f"limite de {meta['round_limit']} versiones alcanzado: el humano debe aprobar o ampliar rondas en el visor")
        stored = _store_file(name, v, filename, data=data, src=src)
        prev = None
        if preview_path or preview_base64:
            if preview_path:
                p = Path(preview_path).expanduser()
                if not p.is_file():
                    raise ValueError(f"no existe la vista previa: {preview_path}")
                prev = _store_file(name, v, "preview_" + p.name, src=p)
            else:
                prev = _store_file(name, v, "preview.png", data=base64.b64decode(preview_base64))
        meta["versions"].append({"v": v, "file": stored, "preview": prev, "author": author, "description": description[:1000],
                                 "created": time.strftime("%Y-%m-%dT%H:%M:%S"), "sha256": hashlib.sha256(
                                     (DIR / "assets" / name / f"v{v}" / stored).read_bytes()).hexdigest()[:16]})
        meta["status"] = "in_review"
        save(meta)
        e = emit("publish", name, author, f"v{v}: {description or stored}", v)
    return meta, e


def review(author, name, v, verdict, comment, point=None):
    if verdict not in ("approve", "changes", "comment"):
        raise ValueError("verdict debe ser approve, changes o comment")
    with lock():
        meta = load(name)
        v = v or meta["versions"][-1]["v"]
        if not any(x["v"] == v for x in meta["versions"]):
            raise ValueError(f"no existe la version {v}")
        r = {"id": len(meta["reviews"]) + 1, "v": v, "author": author, "verdict": verdict, "comment": comment[:4000],
             "point": point, "created": time.strftime("%Y-%m-%dT%H:%M:%S")}
        meta["reviews"].append(r)
        if v == meta["versions"][-1]["v"] and meta["status"] != "approved":
            if verdict == "changes":
                meta["status"] = "changes_requested"
            elif verdict == "approve":
                others = {x["author"] for x in meta["reviews"] if x["v"] == v and x["verdict"] == "approve"}
                meta["status"] = "ai_approved" if others else meta["status"]
        save(meta)
        e = emit("review", name, author, f"[{verdict}] {comment}", v)
    return meta, e


def human_set(name, action):
    with lock():
        meta = load(name)
        if action == "approve":
            meta["status"] = "approved"
        elif action == "reset":
            meta["round_limit"] = len(meta["versions"]) + MAX_ROUNDS
            if meta["status"] == "approved":
                meta["status"] = "in_review"
        else:
            raise ValueError("accion invalida")
        save(meta)
        emit("human_" + action, name, "humano", {"approve": "APROBADO por el humano", "reset": "Rondas ampliadas"}[action])
    return meta


# ---------------- herramientas MCP ----------------

def sch(props, req):
    return {"type": "object", "properties": props, "required": req}


S = lambda d: {"type": "string", "description": d}
N = lambda d: {"type": "number", "description": d}


def tools(me):
    def t_publish(a):
        m, e = publish(me, a["name"], a.get("file_path"), a.get("content_base64"), a.get("filename"),
                       a.get("preview_path"), a.get("preview_base64"), a.get("description", ""), a.get("kind"))
        return f"Publicada la version {m['versions'][-1]['v']} de '{m['name']}' (evento {e['id']}). Ahora toca a la otra IA o al humano: usa taller_wait."

    def t_list(a):
        return json.dumps(assets_summary(), ensure_ascii=False, indent=1)

    def t_get(a):
        m = load(a["name"])
        v = int(a.get("version") or m["versions"][-1]["v"])
        ver = next((x for x in m["versions"] if x["v"] == v), None)
        if not ver:
            raise ValueError(f"no existe la version {v}")
        base = DIR / "assets" / m["name"] / f"v{v}"
        info = {"name": m["name"], "kind": m["kind"], "status": m["status"], "version": ver,
                "archivo_local": str(base / ver["file"]),
                "revisiones": [r for r in m["reviews"] if r["v"] == v],
                "versiones_totales": len(m["versions"])}
        out = [{"type": "text", "text": json.dumps(info, ensure_ascii=False, indent=1)}]
        img = base / (ver["preview"] or "") if ver["preview"] else (base / ver["file"] if m["kind"] == "image" else None)
        if img and img.is_file() and img.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
            mime = mimetypes.guess_type(img.name)[0] or "image/png"
            out.append({"type": "image", "data": base64.b64encode(img.read_bytes()).decode(), "mimeType": mime})
        return out

    def t_review(a):
        m, e = review(me, a["name"], int(a["version"]) if a.get("version") else None, a["verdict"], a["comment"], a.get("point"))
        return f"Revision registrada (evento {e['id']}). Estado: {m['status']}."

    def t_wait(a):
        since = int(a.get("since", 0))
        end = time.time() + min(float(a.get("timeout_s", 50)), 55)
        beat = 0
        while True:
            beat += 1
            if beat % 25 == 0:
                touch(me)
            new = [e for e in events(since) if e["author"] != me]
            if new:
                return json.dumps({"eventos": new, "ultimo_id": new[-1]["id"],
                                   "nota": "Lee con taller_get y responde con taller_publish o taller_review."}, ensure_ascii=False, indent=1)
            if time.time() > end:
                return json.dumps({"eventos": [], "ultimo_id": max(since, last_id()), "nota": "Sin novedades; vuelve a llamar a taller_wait."})
            time.sleep(0.4)

    def t_status(a):
        c = touch(me, a["state"], a.get("note"), a.get("reset_at"))
        return f"Tu estado queda en '{c['state']}'. Las demas IAs y el humano lo ven en el panel."

    def t_team(a):
        now = time.time()
        out = {}
        for who, c in presence_all().items():
            ago = now - c.get("last_seen", 0)
            r = c.get("role", "")
            out[who] = {"rol_principal": r, "fortalezas": ROLES.get(r, ("", []))[1], "sabe_ademas": [x for x in skills_of(who) if x not in ROLES.get(r, ("", []))[1]],
                        "tareas_abiertas": load_of(who), "estado": c.get("state", "ok"), "nota": c.get("note", ""),
                        "vuelve": c.get("reset_at", ""), "visto_hace_s": int(ago), "disponible": c.get("state") == "ok" and ago < 180}
        return json.dumps(out, ensure_ascii=False, indent=1)

    def t_set_role(a):
        if role_of(me) != "director":
            raise ValueError("solo el director (o el humano, en el visor) cambia roles")
        touch(a["who"], by=me, role=a.get("role"), skills=a.get("skills"))
        return f"{a['who']}: rol {role_of(a['who']) or '-'}, sabe {', '.join(skills_of(a['who']))}."

    def t_task_create(a):
        t, warn = task_create(me, a["title"], a.get("detail", ""), a.get("assignee", ""), a.get("asset", ""), a.get("needs", ""))
        return f"Tarea #{t['id']} creada" + (f" y asignada a {t['assignee']}." if t["assignee"] else " (sin asignar).") + warn

    def t_task_update(a):
        t = task_update(me, int(a["id"]), a.get("status"), a.get("note", ""), a.get("assignee"))
        return f"Tarea #{t['id']}: {t['status']} (asignada a {t['assignee'] or 'nadie'})."

    def t_tasks(a):
        ts = [t for t in tasks_all() if (not a.get("assignee") or t["assignee"] == a["assignee"]) and (not a.get("status") or t["status"] == a["status"])]
        return json.dumps(ts, ensure_ascii=False, indent=1)

    return {
        "taller_status": (t_status, "Avisa tu estado al equipo: ok, busy (ocupada), limit (llegaste al limite de uso; pon reset_at si sabes cuando vuelve) o away. LLAMALO en cuanto veas un aviso de limite de uso o te quede poco.",
                          sch({"state": S("ok|busy|limit|away"), "note": S("detalle breve"), "reset_at": S("cuando vuelve, p. ej. 'hoy 01:00' (opcional)")}, ["state"])),
        "taller_team": (t_team, "Equipo: rol, que sabe hacer cada IA y si esta disponible, ocupada o con limite de uso. Consultalo antes de repartir trabajo.", sch({}, [])),
        "taller_set_role": (t_set_role, "(Director) Cambia el rol principal y/o anade habilidades a una IA. Los roles son fortalezas, no limites: todas pueden programar.",
                            sch({"who": S("nombre de la IA"), "role": S("director|modelador|animador|ingeniero|artista"), "skills": {"type": "array", "items": {"type": "string"}, "description": "habilidades extra"}}, ["who"])),
        "taller_task_create": (t_task_create, "Crea una tarea. Solo el DIRECTOR (o el humano) puede asignarla a otra IA; las demas solo a si mismas o sin asignar. Avisa si el asignado no esta disponible y sugiere reemplazos (cualquiera que sepa lo necesario; todas saben programar).",
                               sch({"title": S("titulo corto"), "detail": S("que hay que entregar y criterios de 'hecho'"), "assignee": S("nombre de la IA (opcional)"),
                                    "asset": S("recurso del taller relacionado (opcional)"),
                                    "needs": S("habilidad que exige, p. ej. 'programar' o 'modelado 3D dificil' (opcional; sirve para sugerir reemplazos)")}, ["title"])),
        "taller_task_update": (t_task_update, "Actualiza una tarea: status todo|doing|review|done|blocked, nota, o (solo director) reasignar con assignee.",
                               sch({"id": N("numero de tarea"), "status": S("todo|doing|review|done|blocked"), "note": S("nota"), "assignee": S("nueva IA (solo director)")}, ["id"])),
        "taller_tasks": (t_tasks, "Lista tareas; filtra por assignee o status. Mira las tuyas con assignee=<tu nombre>.", sch({"assignee": S("filtrar"), "status": S("filtrar")}, [])),
        "taller_publish": (t_publish, "Publica una NUEVA VERSION de un modelo (.glb/.gltf/.fbx), animacion, imagen o nota. Adjunta preview_path (un render PNG) para que las demas IAs puedan VERLO.",
                           sch({"name": S("nombre del recurso (misma name = nueva version)"), "file_path": S("ruta local del archivo"),
                                "content_base64": S("alternativa a file_path"), "filename": S("con content_base64"),
                                "preview_path": S("ruta de un render/captura PNG del modelo (recomendado)"),
                                "preview_base64": S("alternativa a preview_path"), "description": S("que cambia en esta version"),
                                "kind": S("model|animation|image|note (opcional)")}, ["name"])),
        "taller_list": (t_list, "Lista los recursos del taller con su estado.", sch({}, [])),
        "taller_get": (t_get, "Lee un recurso: metadatos, revisiones, ruta local y la vista previa como imagen.",
                       sch({"name": S("nombre"), "version": N("version (por defecto la ultima)")}, ["name"])),
        "taller_review": (t_review, "Revisa una version: verdict approve|changes|comment, con comentarios concretos y accionables (que, donde, como arreglarlo).",
                          sch({"name": S("nombre"), "version": N("version (por defecto la ultima)"), "verdict": S("approve|changes|comment"),
                               "comment": S("comentario"), "point": S("zona o coordenadas, opcional")}, ["name", "verdict", "comment"])),
        "taller_wait": (t_wait, "ESPERA (hasta 55 s) novedades de las otras IAs o del humano. Pasa since=ultimo_id de la llamada anterior (0 la primera vez).",
                        sch({"since": N("ultimo id de evento visto"), "timeout_s": N("segundos, max 55")}, [])),
    }


def mcp_handle(me, req):
    m, p = req.get("method"), req.get("params") or {}
    T = tools(me)
    if m == "initialize":
        return {"protocolVersion": p.get("protocolVersion", "2025-06-18"), "capabilities": {"tools": {}},
                "serverInfo": {"name": "taller-ia", "version": "0.1.0"},
                "instructions": f"Eres '{me}' en el Taller IA. Lee PROTOCOLO.md: publica con taller_publish, revisa con taller_review, espera con taller_wait."}
    if m == "ping":
        return {}
    if m == "tools/list":
        return {"tools": [{"name": n, "description": d, "inputSchema": s} for n, (_, d, s) in T.items()]}
    if m == "tools/call":
        name = p.get("name")
        if name not in T:
            raise KeyError(name)
        try:
            touch(me)
            out = T[name][0](p.get("arguments") or {})
            return {"content": out if isinstance(out, list) else [{"type": "text", "text": out}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}
    raise NotImplementedError(m)


AIS = [("claude", "Claude (director)"), ("opus", "Claude Opus (modelador / animador)"),
       ("chatgpt", "Codex / ChatGPT (ingeniero)"), ("antigravity", "Antigravity (direccion de arte)")]


def mcp_command(name):
    """Comando exacto para que una IA lance el servidor MCP del Taller (ruta real de ESTA instalacion)."""
    if getattr(sys, "frozen", False):
        return [str(Path(sys.executable).parent / ("taller-mcp.exe" if os.name == "nt" else "taller-mcp")), "mcp", "--as", name]
    return [sys.executable, str(Path(__file__).resolve()), "mcp", "--as", name]


def connect_info():
    out = []
    for name, label in AIS:
        cmd = mcp_command(name)
        if name in ("claude", "opus"):
            q = lambda x: '"' + x + '"' if " " in x else x
            kind, text = "Pega esto en la terminal, DENTRO de la carpeta del chat de esta IA:", "claude mcp add taller -- " + " ".join(q(x) for x in cmd)
        elif name == "chatgpt":
            kind, text = "Agrega esto al final de ~/.codex/config.toml (en Windows: C:\\Users\\TU_USUARIO\\.codex\\config.toml) y reinicia Codex:", \
                f"[mcp_servers.taller]\ncommand = {json.dumps(cmd[0])}\nargs = {json.dumps(cmd[1:])}"
        else:
            kind, text = "En Antigravity: servidores MCP > configuracion (mcp_config.json) y pega (el menu exacto puede variar):", \
                json.dumps({"mcpServers": {"taller": {"command": cmd[0], "args": cmd[1:]}}}, indent=1)
        out.append({"name": name, "label": label, "role": DEFAULT_ROLE.get(name, ""), "kind": kind, "text": text})
    return out


def prompt_text(role):
    if role not in ROLES:
        raise ValueError("rol invalido")
    name = next((n for n, r in DEFAULT_ROLE.items() if r == role), role)
    parts = [f"Tu nombre en el Taller IA es `{name}` y tu rol principal es **{ROLES[role][0]}**. "
             f"Es tu fortaleza, no tu limite: todas las IAs podemos programar.\n"]
    for f in ("PROTOCOLO.md", f"roles/{role}.md"):
        pth = HERE / f
        if pth.is_file():
            parts.append(pth.read_text("utf-8"))
    return "\n\n".join(parts)


def seed_file(path, quiet=True):
    data = json.loads(Path(path).read_text("utf-8"))
    made = 0
    for t in data["tasks"]:
        if any(x["title"] == t["title"] for x in tasks_all()):
            continue
        task, _ = task_create("claude", t["title"], t.get("detail", ""), t.get("assignee", ""), t.get("asset", ""), t.get("needs", ""))
        if t.get("status", "todo") != "todo":
            task_update("claude", task["id"], t["status"])
        made += 1
        if not quiet:
            print(f"#{task['id']:>2} {task['assignee'] or '(sin asignar)':<12} {task['title']}")
    return made


def run_seed(path):
    """Carga un plan de tareas (como director). No duplica: omite titulos ya existentes."""
    print(f"{seed_file(path, quiet=False)} tareas cargadas en {DIR}")


def run_mcp(me, role=None):
    if not AUTHOR_RE.match(me):
        sys.exit("--as debe ser corto: letras minusculas, numeros, - o _")
    if role or me in DEFAULT_ROLE:
        touch(me, role=role)
    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line)
        if "id" not in req:
            continue
        try:
            resp = {"jsonrpc": "2.0", "id": req["id"], "result": mcp_handle(me, req)}
        except Exception as e:
            resp = {"jsonrpc": "2.0", "id": req["id"], "error": {"code": -32601, "message": str(e)}}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


# ---------------- visor web (para el humano) ----------------

class Handler(BaseHTTPRequestHandler):
    key = ""
    mcp_http = ""
    port = 0

    def log_message(self, *a): pass

    def _ok_host(self):
        return self.headers.get("Host", "") in (f"127.0.0.1:{self.port}", f"localhost:{self.port}") or bool(self.mcp_http and self.path.startswith("/mcp"))

    def _send(self, code, body, ctype="application/json", extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        if isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _authed(self):
        auth = self.headers.get("Authorization", "")
        tok = auth[7:] if auth.startswith("Bearer ") else self.headers.get("X-Taller-Key", "")
        return secrets.compare_digest(tok, self.key)

    def do_GET(self):
        if not self._ok_host():
            return self._send(403, {"error": "host"})
        u = urlparse(self.path)
        try:
            if u.path == "/":
                return self._send(200, (HERE / "viewer.html").read_bytes(), "text/html; charset=utf-8")
            if u.path == "/api/assets":
                return self._send(200, assets_summary())
            if u.path.startswith("/api/assets/"):
                return self._send(200, load(unquote(u.path[12:])))
            if u.path == "/api/connect":
                return self._send(200, connect_info())
            if u.path == "/api/prompt":
                return self._send(200, {"text": prompt_text(parse_qs(u.query).get("role", [""])[0])})
            if u.path == "/api/presence":
                return self._send(200, presence_all())
            if u.path == "/api/tasks":
                return self._send(200, {"tasks": tasks_all(), "roles": {k: {"label": v[0], "skills": v[1]} for k, v in ROLES.items()}, "common": COMMON})
            if u.path == "/api/events":
                return self._send(200, events(int(parse_qs(u.query).get("since", ["0"])[0])))
            if u.path == "/api/stream":
                return self._stream(int(parse_qs(u.query).get("since", [str(last_id())])[0]))
            if u.path.startswith("/vendor/"):  # three.js incluido (sin CDN)
                f = (HERE / unquote(u.path[1:])).resolve()
                if not str(f).startswith(str(HERE / "vendor")) or not f.is_file():
                    return self._send(404, {"error": "no encontrado"})
                return self._send(200, f.read_bytes(), "text/javascript" if f.suffix == ".js" else "text/plain")
            if u.path.startswith("/files/"):
                parts = [unquote(x) for x in u.path[7:].split("/")]
                if len(parts) != 3 or not re.match(r"^v\d+$", parts[1]) or not NAME_RE.match(parts[0]) or "/" in parts[2] or parts[2].startswith("."):
                    return self._send(404, {"error": "no encontrado"})
                f = DIR / "assets" / parts[0] / parts[1] / parts[2]
                if not f.is_file():
                    return self._send(404, {"error": "no encontrado"})
                ctype = {".glb": "model/gltf-binary", ".gltf": "model/gltf+json", ".fbx": "application/octet-stream"}.get(
                    f.suffix.lower()) or mimetypes.guess_type(f.name)[0] or "application/octet-stream"
                return self._send(200, f.read_bytes(), ctype)
        except KeyError as e:
            return self._send(404, {"error": str(e)})
        except ValueError as e:
            return self._send(400, {"error": str(e)})
        self._send(404, {"error": "no encontrado"})

    def _stream(self, since):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            beat = 0
            while True:
                new = events(since)
                for e in new:
                    self.wfile.write(f"data: {json.dumps(e, ensure_ascii=False)}\n\n".encode())
                    since = e["id"]
                beat += 1
                if new or beat % 25 == 0:
                    self.wfile.write(b": ping\n\n")
                self.wfile.flush()
                time.sleep(0.4)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def do_POST(self):
        if not self._ok_host():
            return self._send(403, {"error": "host"})
        n = int(self.headers.get("Content-Length", "0"))
        if n > 8 * 1024 * 1024:
            return self._send(413, {"error": "muy grande"})
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return self._send(400, {"error": "json invalido"})
        if self.path.startswith("/mcp"):  # MCP por HTTP (ChatGPT web/escritorio): requiere --mcp-http y token
            if not self.mcp_http:
                return self._send(404, {"error": "mcp http desactivado"})
            if not self._authed():
                return self._send(401, {"error": "token"})
            who = parse_qs(urlparse(self.path).query).get("as", [self.mcp_http])[0]
            if not AUTHOR_RE.match(who):
                return self._send(400, {"error": "as invalido"})
            if "id" not in body:
                return self._send(202, b"")
            try:
                return self._send(200, {"jsonrpc": "2.0", "id": body["id"], "result": mcp_handle(who, body)})
            except Exception as e:
                return self._send(200, {"jsonrpc": "2.0", "id": body["id"], "error": {"code": -32601, "message": str(e)}})
        if not self._authed():
            return self._send(401, {"error": "token"})
        try:
            if self.path == "/api/comment":
                m, _ = review("humano", body["name"], body.get("version"), body.get("verdict", "comment"), body["comment"])
                return self._send(200, {"ok": True})
            if self.path == "/api/seed":
                plan = HERE / "planes" / (re.sub(r"[^a-z0-9-]", "", str(body.get("plan", "slime-rush"))) + ".json")
                if not plan.is_file():
                    raise ValueError("plan no encontrado")
                return self._send(200, {"ok": True, "tareas_nuevas": seed_file(plan)})
            if self.path == "/api/task":
                if body.get("id"):
                    task_update("humano", int(body["id"]), body.get("status"), body.get("note", ""), body.get("assignee"))
                else:
                    task_create("humano", body["title"], body.get("detail", ""), body.get("assignee", ""), body.get("asset", ""))
                return self._send(200, {"ok": True})
            if self.path == "/api/presence":
                who = str(body["name"])
                if not AUTHOR_RE.match(who):
                    raise ValueError("nombre invalido")
                touch(who, body.get("state"), body.get("note"), body.get("reset_at"), by="humano", role=body.get("role"), skills=body.get("skills"))
                return self._send(200, {"ok": True})
            if self.path in ("/api/approve", "/api/reset"):
                human_set(body["name"], self.path[5:])
                return self._send(200, {"ok": True})
        except (KeyError, ValueError) as e:
            return self._send(400, {"error": str(e)})
        self._send(404, {"error": "no encontrado"})


def make_server(port, mcp_http=False):
    DIR.mkdir(parents=True, exist_ok=True)
    kp = DIR / "key.txt"
    if not kp.exists():
        kp.write_text(secrets.token_urlsafe(24))
        with contextlib.suppress(OSError):
            kp.chmod(0o600)
    Handler.key, Handler.port = kp.read_text().strip(), port
    Handler.mcp_http = "chatgpt" if mcp_http else ""
    return ThreadingHTTPServer(("127.0.0.1", port), Handler), f"http://127.0.0.1:{port}/?k={Handler.key}"


def run_serve(port, mcp_http):
    srv, url = make_server(port, mcp_http)
    print(f"Taller IA: {url}\nDatos: {DIR}")
    if mcp_http:
        print("MCP por HTTP activo en /mcp (Authorization: Bearer <token>; ?as=nombre). NO lo expongas a internet sin que tu lo decidas.")
    with contextlib.suppress(KeyboardInterrupt):
        srv.serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve")
    s.add_argument("--port", type=int, default=8770)
    s.add_argument("--mcp-http", action="store_true", help="habilita /mcp por HTTP (para ChatGPT web/escritorio)")
    sd = sub.add_parser("seed")
    sd.add_argument("plan", help="archivo JSON con tareas, p. ej. planes/slime-rush.json")
    m = sub.add_parser("mcp")
    m.add_argument("--as", dest="me", required=True, help="nombre de esta IA: claude, chatgpt, antigravity...")
    m.add_argument("--role", choices=list(ROLES), help="rol (por defecto segun el nombre: claude=director, opus=modelador, chatgpt/codex=ingeniero, antigravity=artista)")
    a = ap.parse_args()
    if a.cmd == "seed":
        run_seed(a.plan)
    elif a.cmd == "mcp":
        run_mcp(a.me, a.role)
    else:
        run_serve(a.port, a.mcp_http)
