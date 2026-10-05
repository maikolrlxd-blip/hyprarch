'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { parseDecision, toMessages, buildSystem } = require('../src/main/brain');
const { chat } = require('../src/main/providers');

test('parseDecision extrae JSON envuelto en markdown', () => {
  const d = parseDecision('```json\n{"say":"hola","action":"wave","target":"Rex"}\n```');
  assert.deepStrictEqual(d, { say: 'hola', action: 'wave', target: 'Rex' });
});
test('parseDecision tolera acciones invalidas y texto plano', () => {
  assert.strictEqual(parseDecision('{"say":"x","action":"fly"}').action, 'idle');
  assert.strictEqual(parseDecision('solo texto').say, 'solo texto');
});
test('toMessages alterna roles y empieza con user', () => {
  const m = toMessages([{ role: 'assistant', content: 'a' }, { role: 'assistant', content: 'b' }], 'P');
  assert.strictEqual(m[0].role, 'user');
  assert.deepStrictEqual(m.map(x => x.role), ['user', 'assistant', 'user']);
});
test('buildSystem incluye nombre y personalidad', () => {
  assert.match(buildSystem({ name: 'Luna', personality: 'soniadora' }), /Luna[\s\S]*soniadora/);
});
test('proveedor mock devuelve una decision parseable', async () => {
  const raw = await chat({ agent: { provider: 'mock' }, system: '', messages: [{ role: 'user', content: 'x' }] });
  assert.ok(['idle', 'walk_to', 'wave', 'dance', 'jump'].includes(parseDecision(raw).action));
});
test('proveedor con key requerida falla sin key', async () => {
  await assert.rejects(chat({ agent: { provider: 'anthropic' }, system: '', messages: [] }), /API key/);
});

test('el hash CSP del importmap coincide con el HTML', () => {
  const crypto = require('node:crypto');
  const html = require('node:fs').readFileSync(require('node:path').join(__dirname, '../src/renderer/index.html'), 'utf8');
  const body = html.match(/<script type="importmap">([\s\S]*?)<\/script>/)[1];
  const hash = crypto.createHash('sha256').update(body).digest('base64');
  assert.ok(html.includes(`'sha256-${hash}'`));
});
