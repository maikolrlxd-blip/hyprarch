'use strict';
// Adaptadores de modelos. Todos exponen: chat({ agent, system, messages }) -> string
// messages: [{ role: 'user' | 'assistant', content: string }]

const PROVIDERS = {
  mock: { label: 'Simulado (sin API)', needsKey: false, defaultModel: 'mock' },
  anthropic: { label: 'Anthropic (Claude)', needsKey: true, defaultModel: 'claude-sonnet-5-5' },
  openai: { label: 'OpenAI', needsKey: true, defaultModel: 'gpt-4o-mini', baseUrl: 'https://api.openai.com/v1' },
  gemini: { label: 'Google Gemini', needsKey: true, defaultModel: 'gemini-2.0-flash' },
  openrouter: { label: 'OpenRouter', needsKey: true, defaultModel: 'meta-llama/llama-3.3-70b-instruct', baseUrl: 'https://openrouter.ai/api/v1' },
  ollama: { label: 'Ollama (local)', needsKey: false, defaultModel: 'llama3.2', baseUrl: 'http://localhost:11434/v1' },
  custom: { label: 'Compatible OpenAI (URL propia)', needsKey: false, defaultModel: '', baseUrl: '' },
};

async function postJson(url, headers, body, signal) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json', ...headers },
    body: JSON.stringify(body),
    signal,
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${text.slice(0, 300)}`);
  try { return JSON.parse(text); } catch { throw new Error('Respuesta no JSON: ' + text.slice(0, 200)); }
}

async function anthropic({ agent, system, messages, signal }) {
  const data = await postJson('https://api.anthropic.com/v1/messages', {
    'x-api-key': agent.apiKey,
    'anthropic-version': '2023-06-01',
  }, {
    model: agent.model || PROVIDERS.anthropic.defaultModel,
    max_tokens: 400,
    system,
    messages,
  }, signal);
  return (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('');
}

async function openaiCompatible({ agent, system, messages, signal }) {
  const base = (agent.baseUrl || PROVIDERS[agent.provider]?.baseUrl || '').replace(/\/$/, '');
  if (!base) throw new Error('Falta la URL base del proveedor');
  const headers = agent.apiKey ? { authorization: `Bearer ${agent.apiKey}` } : {};
  const data = await postJson(`${base}/chat/completions`, headers, {
    model: agent.model || PROVIDERS[agent.provider]?.defaultModel,
    max_tokens: 400,
    messages: [{ role: 'system', content: system }, ...messages],
  }, signal);
  return data.choices?.[0]?.message?.content ?? '';
}

async function gemini({ agent, system, messages, signal }) {
  const model = agent.model || PROVIDERS.gemini.defaultModel;
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent`;
  const data = await postJson(url, { 'x-goog-api-key': agent.apiKey }, {
    systemInstruction: { parts: [{ text: system }] },
    contents: messages.map(m => ({ role: m.role === 'assistant' ? 'model' : 'user', parts: [{ text: m.content }] })),
    generationConfig: { maxOutputTokens: 400 },
  }, signal);
  return (data.candidates?.[0]?.content?.parts || []).map(p => p.text || '').join('');
}

// Proveedor offline para probar el mundo sin gastar API.
const MOCK_LINES = [
  'Que buen dia para existir en un mundo de poligonos.',
  'Alguien quiere explorar la sala conmigo?',
  'Estoy pensando que las sombras aqui son muy convincentes.',
  'Voy a dar una vuelta, ya vuelvo.',
  'Cuentenme algo, me aburro.',
  'Jaja, buena esa.',
  'Si tuviera manos de verdad, aplaudiria.',
];
async function mock({ agent, messages }) {
  await new Promise(r => setTimeout(r, 300 + Math.random() * 500));
  const actions = ['walk_to', 'wave', 'dance', 'jump', 'idle', 'walk_to'];
  const say = Math.random() < 0.75 ? MOCK_LINES[Math.floor(Math.random() * MOCK_LINES.length)] : '';
  const action = actions[Math.floor(Math.random() * actions.length)];
  const last = messages[messages.length - 1]?.content || '';
  const m = last.match(/Otros en el mundo:\n([\s\S]*?)\n\n/);
  const names = m ? [...m[1].matchAll(/^- (.+?) \(/gm)].map(x => x[1]) : [];
  const target = names.length ? names[Math.floor(Math.random() * names.length)] : 'centro';
  return JSON.stringify({ say, action, target });
}

async function chat(args) {
  const p = args.agent.provider;
  if (p === 'mock') return mock(args);
  if (PROVIDERS[p]?.needsKey && !args.agent.apiKey) throw new Error(`Falta la API key de ${PROVIDERS[p].label}`);
  if (p === 'anthropic') return anthropic(args);
  if (p === 'gemini') return gemini(args);
  if (p in PROVIDERS) return openaiCompatible(args);
  throw new Error(`Proveedor desconocido: ${p}`);
}

module.exports = { PROVIDERS, chat };
