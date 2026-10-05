'use strict';
const test = require('node:test');
const assert = require('node:assert');
const shared = Promise.all([import('../src/shared/brain.mjs'), import('../src/shared/providers.mjs')]);
const brainP = shared.then(([b]) => b), provP = shared.then(([, p]) => p);

test('parseDecision extrae JSON envuelto en markdown', async () => {
  const { parseDecision } = await brainP;
  const d = parseDecision('```json\n{"say":"hola","action":"wave","target":"Rex"}\n```');
  assert.deepStrictEqual(d, { say: 'hola', action: 'wave', target: 'Rex' });
});
test('parseDecision tolera acciones invalidas y texto plano', async () => {
  const { parseDecision } = await brainP;
  assert.strictEqual(parseDecision('{"say":"x","action":"fly"}').action, 'idle');
  assert.strictEqual(parseDecision('solo texto').say, 'solo texto');
});
test('toMessages alterna roles y empieza con user', async () => {
  const { toMessages } = await brainP;
  const m = toMessages([{ role: 'assistant', content: 'a' }, { role: 'assistant', content: 'b' }], 'P');
  assert.strictEqual(m[0].role, 'user');
  assert.deepStrictEqual(m.map(x => x.role), ['user', 'assistant', 'user']);
});
test('buildSystem incluye nombre y personalidad', async () => {
  const { buildSystem } = await brainP;
  assert.match(buildSystem({ name: 'Luna', personality: 'soniadora' }), /Luna[\s\S]*soniadora/);
});
test('proveedor mock devuelve una decision parseable', async () => {
  const { chat } = await provP; const { parseDecision } = await brainP;
  const raw = await chat({ agent: { provider: 'mock' }, system: '', messages: [{ role: 'user', content: 'x' }] });
  assert.ok(['idle', 'walk_to', 'wave', 'dance', 'jump'].includes(parseDecision(raw).action));
});
test('proveedor con key requerida falla sin key', async () => {
  const { chat } = await provP;
  await assert.rejects(chat({ agent: { provider: 'anthropic' }, system: '', messages: [] }), /API key/);
});

test('el hash CSP del importmap coincide con el HTML', () => {
  const crypto = require('node:crypto');
  const html = require('node:fs').readFileSync(require('node:path').join(__dirname, '../src/renderer/index.html'), 'utf8');
  const body = html.match(/<script type="importmap">([\s\S]*?)<\/script>/)[1];
  const hash = crypto.createHash('sha256').update(body).digest('base64');
  assert.ok(html.includes(`'sha256-${hash}'`));
});

test('los imports del renderer existen y no dependen de carpetas que el empaquetador elimina', () => {
  const fs = require('node:fs'), path = require('node:path');
  const dir = path.join(__dirname, '../src/renderer');
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.js')).concat(fs.readdirSync(path.join(dir, 'vendor')).filter(f => f.endsWith('.js')).map(f => 'vendor/' + f));
  for (const f of files) {
    const src = fs.readFileSync(path.join(dir, f), 'utf8');
    for (const m of src.matchAll(/from\s+'([^']+)'/g)) {
      const spec = m[1];
      if (spec === 'three') continue;
      assert.ok(spec.startsWith('.'), `${f}: import "${spec}" no resoluble (solo 'three' y relativos)`);
      assert.ok(fs.existsSync(path.join(dir, path.dirname(f), spec)), `${f}: falta ${spec}`);
    }
  }
});

test('think() corre un turno completo con transporte HTTP inyectado (como en Android)', async () => {
  const { think } = await brainP; const { chat } = await provP;
  const calls = [];
  const http = async (url, headers, body) => { calls.push({ url, headers, body }); return { choices: [{ message: { content: '{"say":"hola desde el celular","action":"wave","target":""}' } }] }; };
  const agent = { id: 'a', name: 'A', personality: 'x', provider: 'custom', baseUrl: 'http://mock/v1', apiKey: 'k', model: 'm' };
  const world = { self: { x: 0, z: 0 }, size: 12, others: [], log: [] };
  const r1 = await think({ agent, world, history: [], chat, http });
  assert.strictEqual(r1.decision.say, 'hola desde el celular');
  assert.strictEqual(calls[0].url, 'http://mock/v1/chat/completions');
  assert.strictEqual(calls[0].headers.authorization, 'Bearer k');
  assert.strictEqual(r1.history.length, 2);
  const r2 = await think({ agent, world, history: r1.history, chat, http });
  assert.strictEqual(r2.history.length, 4);
});

test('el transporte nativo recibe cabeceras de Anthropic y Gemini correctas', async () => {
  const { chat } = await provP; const seen = [];
  const http = async (url, headers) => { seen.push({ url, headers }); return { content: [{ type: 'text', text: 'ok' }], candidates: [{ content: { parts: [{ text: 'ok' }] } }] }; };
  await chat({ agent: { provider: 'anthropic', apiKey: 'sk', model: 'm' }, system: 's', messages: [{ role: 'user', content: 'x' }] }, http);
  await chat({ agent: { provider: 'gemini', apiKey: 'gk', model: 'g' }, system: 's', messages: [{ role: 'user', content: 'x' }] }, http);
  assert.strictEqual(seen[0].headers['x-api-key'], 'sk');
  assert.strictEqual(seen[1].headers['x-goog-api-key'], 'gk');
});
