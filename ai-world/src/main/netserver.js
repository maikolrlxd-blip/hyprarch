'use strict';
// Servidor LAN: sirve el cliente web (para el celular) y retransmite el mundo por WebSocket.
// Solo acepta conexiones con el token de emparejamiento, para que nadie en la red
// pueda gastar tu API ni hablar por las IAs.
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const crypto = require('crypto');
const { WebSocketServer } = require('ws');

const ROOT = path.join(__dirname, '..', '..');
const ALLOWED = [ // solo estos directorios son publicos
  path.join(ROOT, 'src', 'renderer'),
  path.join(ROOT, 'node_modules', 'three', 'build'),
  path.join(ROOT, 'node_modules', 'three', 'examples', 'jsm'),
];
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.svg': 'image/svg+xml' };
const MAX_TEXT = 240;
const LOG_KEEP = 30;

function lanAddresses() {
  const out = [];
  for (const list of Object.values(os.networkInterfaces())) {
    for (const i of list || []) if (i.family === 'IPv4' && !i.internal) out.push(i.address);
  }
  const isPrivate = a => /^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)/.test(a);
  return out.sort((a, b) => isPrivate(b) - isPrivate(a));
}

class NetServer {
  constructor({ onChat, onClients } = {}) {
    this.onChat = onChat || (() => {});
    this.onClients = onClients || (() => {});
    this.token = null; this.server = null; this.wss = null;
    this.state = { agents: [], pos: {} };
    this.log = [];
  }

  get running() { return !!this.server; }

  async start({ port = 8787, host = '0.0.0.0' } = {}) {
    if (this.server) return this.info();
    this.token = crypto.randomBytes(12).toString('base64url');
    this.server = http.createServer((req, res) => this.#serve(req, res));
    this.wss = new WebSocketServer({ noServer: true, maxPayload: 4096 });
    this.server.on('upgrade', (req, socket, head) => {
      const u = new URL(req.url, 'http://x');
      const given = Buffer.from(u.searchParams.get('t') || '');
      const want = Buffer.from(this.token);
      if (u.pathname !== '/ws' || given.length !== want.length || !crypto.timingSafeEqual(given, want)) {
        socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n'); return socket.destroy();
      }
      this.wss.handleUpgrade(req, socket, head, ws => this.#onConnect(ws));
    });
    await new Promise((resolve, reject) => {
      this.server.once('error', reject);
      this.server.listen(port, host, resolve);
    });
    return this.info();
  }

  info() {
    const port = this.server.address().port;
    return { port, token: this.token, urls: lanAddresses().map(a => `http://${a}:${port}/?t=${this.token}`), localUrl: `http://127.0.0.1:${port}/?t=${this.token}` };
  }

  async stop() {
    if (!this.server) return;
    for (const c of this.wss.clients) c.terminate();
    this.wss.close();
    await new Promise(r => this.server.close(r));
    this.server = this.wss = this.token = null;
    this.onClients(0);
  }

  #onConnect(ws) {
    ws.lastChat = 0;
    ws.send(JSON.stringify({ type: 'hello', agents: this.state.agents, pos: this.state.pos, log: this.log }));
    this.onClients(this.wss.clients.size);
    ws.on('close', () => this.onClients(this.wss ? this.wss.clients.size : 0));
    ws.on('message', data => {
      let m; try { m = JSON.parse(data.toString()); } catch { return; }
      if (m?.type !== 'chat' || typeof m.text !== 'string') return;
      const text = m.text.trim().slice(0, MAX_TEXT);
      if (!text || Date.now() - ws.lastChat < 1000) return; // maximo 1 mensaje/s por cliente
      ws.lastChat = Date.now();
      this.onChat({ from: 'Movil', text });
    });
  }

  // Eventos del mundo (say / act / thinking / human) -> todos los clientes.
  event(ev) {
    if (ev.type === 'say' || ev.type === 'human') { this.log.push(ev); this.log = this.log.slice(-LOG_KEEP); }
    this.#broadcast(ev);
  }
  // Foto periodica de posiciones; tambien es lo que ve un cliente que se conecta tarde.
  setState(state) {
    this.state = state;
    this.#broadcast({ type: 'snap', agents: state.agents, pos: state.pos });
  }
  #broadcast(obj) {
    if (!this.wss) return;
    const s = JSON.stringify(obj);
    for (const c of this.wss.clients) if (c.readyState === 1) c.send(s);
  }

  #serve(req, res) {
    const u = new URL(req.url, 'http://x');
    let p = decodeURIComponent(u.pathname);
    // Redirigir (no servir directo) para que las rutas relativas del HTML resuelvan bien.
    if (p === '/') { res.writeHead(302, { location: '/src/renderer/index.html' + u.search }); return res.end(); }
    const file = path.normalize(path.join(ROOT, p));
    if (!ALLOWED.some(d => file.startsWith(d + path.sep)) || file.includes('\0')) { res.writeHead(404); return res.end('not found'); }
    fs.readFile(file, (err, data) => {
      if (err) { res.writeHead(404); return res.end('not found'); }
      res.writeHead(200, { 'content-type': MIME[path.extname(file)] || 'application/octet-stream', 'cache-control': 'no-cache' });
      res.end(data);
    });
  }
}

module.exports = { NetServer, lanAddresses };
