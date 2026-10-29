#!/usr/bin/env python3
"""phone-relay: une el celular (WebSocket) con el puente MCP (HTTP).

El celular y el puente comparten un token secreto; el relay solo guarda su hash
en memoria. Ponelo detras de HTTPS (Caddy/nginx) en produccion.

  pip install aiohttp && python3 relay.py --port 8765
"""
import argparse
import asyncio
import hashlib
import hmac
import json
import uuid

from aiohttp import WSMsgType, web

MIN_TOKEN = 32
TIMEOUT = 30


def key_of(request):
    auth = request.headers.get("Authorization", "")
    token = auth[7:] if auth.startswith("Bearer ") else ""
    if len(token) < MIN_TOKEN:
        raise web.HTTPUnauthorized(text="token invalido")
    return hashlib.sha256(token.encode()).hexdigest()


async def ws_phone(request):
    key = key_of(request)
    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=32 * 1024 * 1024)
    await ws.prepare(request)
    old = request.app["phones"].get(key)
    if old is not None and not old.closed:
        await old.close()  # un token = un celular
    request.app["phones"][key] = ws
    pending = request.app["pending"]
    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                continue
            try:
                data = json.loads(msg.data)
            except ValueError:
                continue
            fut = pending.pop(data.get("id"), None)
            if fut and not fut.done():
                fut.set_result(data)
    finally:
        if request.app["phones"].get(key) is ws:
            del request.app["phones"][key]
    return ws


async def status(request):
    ws = request.app["phones"].get(key_of(request))
    return web.json_response({"online": ws is not None and not ws.closed})


async def command(request):
    ws = request.app["phones"].get(key_of(request))
    if ws is None or ws.closed:
        return web.json_response({"ok": False, "error": "El celular no esta conectado"}, status=503)
    try:
        body = await request.json()
        action = str(body["action"])
    except (ValueError, KeyError):
        return web.json_response({"ok": False, "error": "JSON invalido"}, status=400)
    cid = uuid.uuid4().hex
    fut = asyncio.get_running_loop().create_future()
    request.app["pending"][cid] = fut
    try:
        await ws.send_json({"id": cid, "action": action, "args": body.get("args") or {}})
        return web.json_response(await asyncio.wait_for(fut, TIMEOUT))
    except asyncio.TimeoutError:
        return web.json_response({"ok": False, "error": "El celular no respondio a tiempo"}, status=504)
    finally:
        request.app["pending"].pop(cid, None)


def make_app():
    app = web.Application(client_max_size=1024 * 1024)
    app["phones"], app["pending"] = {}, {}
    app.add_routes([web.get("/ws/phone", ws_phone), web.get("/api/status", status),
                    web.post("/api/cmd", command), web.get("/", lambda r: web.Response(text="phone-relay ok"))])
    return app


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    web.run_app(make_app(), host=a.host, port=a.port)
