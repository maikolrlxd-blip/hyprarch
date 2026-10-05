'use strict';
const test = require('node:test');
const assert = require('node:assert');
const WebSocket = require('ws');
const { NetServer } = require('../src/main/netserver');

const open = url => new Promise((resolve, reject) => {
  const ws = new WebSocket(url);
  const queue = []; let waiter = null;
  ws.on('message', d => { const m = JSON.parse(d); if (waiter) { const w = waiter; waiter = null; w(m); } else queue.push(m); });
  ws.next = () => new Promise(r => queue.length ? r(queue.shift()) : (waiter = r));
  ws.once('open', () => resolve(ws)); ws.once('error', reject); ws.once('unexpected-response', (_q, r) => reject(new Error('HTTP ' + r.statusCode)));
});

test('NetServer: token, hello, broadcast, chat y archivos publicos', async () => {
  const chats = []; const counts = [];
  const net = new NetServer({ onChat: c => chats.push(c), onClients: n => counts.push(n) });
  net.setState({ agents: [{ id: 'a', name: 'A', color: '#fff' }], pos: { a: [1, 2] } });
  const { port, token } = await net.start({ port: 0, host: '127.0.0.1' });
  try {
    await assert.rejects(open(`ws://127.0.0.1:${port}/ws?t=malo`), /401/);
    await assert.rejects(open(`ws://127.0.0.1:${port}/ws`), /401/);

    const ws = await open(`ws://127.0.0.1:${port}/ws?t=${token}`);
    const hello = await ws.next();
    assert.strictEqual(hello.type, 'hello');
    assert.deepStrictEqual(hello.pos, { a: [1, 2] });

    net.event({ type: 'say', id: 'a', name: 'A', text: 'hola' });
    assert.deepStrictEqual(await ws.next(), { type: 'say', id: 'a', name: 'A', text: 'hola' });

    ws.send(JSON.stringify({ type: 'chat', text: '  hey  ' }));
    ws.send(JSON.stringify({ type: 'chat', text: 'spam' })); // dentro de 1 s: se descarta
    await new Promise(r => setTimeout(r, 100));
    assert.deepStrictEqual(chats, [{ from: 'Movil', text: 'hey' }]);

    // un cliente tardio recibe el historial
    const ws2 = await open(`ws://127.0.0.1:${port}/ws?t=${token}`);
    assert.strictEqual((await ws2.next()).log.length, 1);

    const base = `http://127.0.0.1:${port}`;
    const root = await fetch(base + '/?t=abc', { redirect: 'manual' });
    assert.strictEqual(root.status, 302);
    assert.strictEqual(root.headers.get('location'), '/src/renderer/index.html?t=abc');
    for (const p of ['/src/renderer/index.html', '/src/renderer/style.css', '/src/renderer/app.js', '/src/renderer/manifest.webmanifest', '/src/renderer/icon.svg'])
      assert.strictEqual((await fetch(base + p)).status, 200, p);
    assert.strictEqual((await fetch(base + '/node_modules/three/build/three.module.js')).status, 200);
    for (const p of ['/package.json', '/src/main/store.js', '/..%2fpackage.json', '/node_modules/ws/package.json'])
      assert.strictEqual((await fetch(base + p)).status, 404, p);
    ws.close(); ws2.close();
  } finally { await net.stop(); }
  assert.strictEqual(counts.at(-1), 0);
});
