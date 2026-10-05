import { World, ROOM } from './world.js';

const $ = id => document.getElementById(id);
const world = new World($('scene'));
let config = null;
let paused = false;
let turnIndex = 0;
const thinking = new Set();
const log = []; // { from, text }
const LOG_WINDOW = 12;

function addLine(from, text, cls = '', color = '') {
  const el = document.createElement('div');
  el.className = 'line ' + cls;
  const b = document.createElement('b'); b.textContent = from; if (color) b.style.color = color;
  el.append(b, document.createTextNode(text));
  const box = $('log'); box.append(el); box.scrollTop = box.scrollHeight;
  while (box.children.length > 300) box.firstChild.remove();
}

function renderRoster() {
  $('roster').replaceChildren(...config.agents.map(a => {
    const li = document.createElement('li');
    li.dataset.id = a.id; if (thinking.has(a.id)) li.className = 'thinking';
    const dot = document.createElement('span'); dot.className = 'dot'; dot.style.background = a.color;
    li.append(dot, `${a.name} · ${a.provider}`);
    return li;
  }));
}

function perceive(agent) {
  const self = world.avatars.get(agent.id);
  const others = [...world.avatars.values()].filter(o => o !== self).map(o => ({
    name: o.name, kind: 'IA', distance: o.position.distanceTo(self.position), doing: o.describe(),
  }));
  return {
    self: { x: self.position.x, z: self.position.z }, size: ROOM, others,
    log: log.slice(-LOG_WINDOW),
  };
}

async function takeTurn(agent) {
  const av = world.avatars.get(agent.id);
  if (!av || thinking.has(agent.id)) return;
  thinking.add(agent.id); renderRoster();
  try {
    const res = await window.aiWorld.think({ agentId: agent.id, world: perceive(agent) });
    if (res.error) { addLine(agent.name, res.error, 'err'); return; }
    const { say, action, target } = res.decision;
    if (action === 'walk_to') {
      const t = world.resolveTarget(av, target);
      av.walkTo(t.x, t.z, t.stop);
    } else av.perform(action);
    if (say) {
      av.say(say);
      log.push({ from: agent.name, text: say });
      addLine(agent.name, say, '', agent.color);
    }
  } finally { thinking.delete(agent.id); renderRoster(); }
}

// Un turno cada turnSeconds, rotando entre IAs: limita el gasto de API y evita que hablen todas a la vez.
let sinceTurn = 0;
setInterval(() => {
  if (paused || !config?.agents.length) return;
  if (++sinceTurn < config.turnSeconds) return;
  sinceTurn = 0;
  takeTurn(config.agents[turnIndex++ % config.agents.length]);
}, 1000);

$('chat').addEventListener('submit', e => {
  e.preventDefault();
  const text = $('msg').value.trim(); if (!text) return;
  $('msg').value = '';
  log.push({ from: 'Humano', text });
  addLine('Tu', text, 'me');
  // el humano interrumpe: la siguiente IA responde de inmediato
  if (!paused && config.agents.length) { sinceTurn = 0; takeTurn(config.agents[turnIndex++ % config.agents.length]); }
});

$('pause').addEventListener('click', () => { paused = !paused; $('pause').textContent = paused ? 'Reanudar' : 'Pausar'; });

// ---------- Ajustes ----------
function agentCard(a) {
  const el = document.createElement('div'); el.className = 'agent'; el.dataset.id = a.id;
  const provOpts = Object.entries(config.providers).map(([k, v]) => `<option value="${k}" ${k === a.provider ? 'selected' : ''}>${v.label}</option>`).join('');
  el.innerHTML = `
    <label>Nombre <input data-f="name"></label>
    <label>Color <input data-f="color" type="color"></label>
    <label>Proveedor <select data-f="provider">${provOpts}</select></label>
    <label>Modelo <input data-f="model" placeholder="(por defecto)"></label>
    <label>API key <input data-f="apiKey" type="password" autocomplete="off"></label>
    <label>URL base <input data-f="baseUrl" placeholder="(por defecto)"></label>
    <label class="full">Personalidad <textarea data-f="personality" rows="2"></textarea></label>
    <button type="button" class="full" data-del>Eliminar esta IA</button>`;
  for (const f of el.querySelectorAll('[data-f]')) if (f.tagName !== 'SELECT') f.value = a[f.dataset.f] ?? '';
  el.querySelector('[data-del]').onclick = () => el.remove();
  return el;
}

function openSettings() {
  $('turn').value = config.turnSeconds;
  $('agentList').replaceChildren(...config.agents.map(agentCard));
  $('dlg').showModal();
}
$('settings').onclick = openSettings;
$('cancel').onclick = () => $('dlg').close();
$('addAgent').onclick = () => $('agentList').append(agentCard({
  id: 'ia-' + Date.now().toString(36), name: 'Nueva IA', color: '#c58bff', provider: 'mock', model: '', baseUrl: '', apiKey: '', personality: 'Amistosa y curiosa.',
}));
$('dlgForm').addEventListener('submit', async () => {
  const agents = [...$('agentList').children].map(el => {
    const a = { id: el.dataset.id };
    for (const f of el.querySelectorAll('[data-f]')) a[f.dataset.f] = f.value.trim();
    return a;
  }).filter(a => a.name);
  config.agents = agents; config.turnSeconds = Math.max(2, +$('turn').value || 6);
  await window.aiWorld.saveConfig({ agents: config.agents, turnSeconds: config.turnSeconds });
  world.setAgents(config.agents); renderRoster();
});

// ---------- Arranque ----------
config = await window.aiWorld.getConfig();
world.setAgents(config.agents); renderRoster();
addLine('Sistema', 'Bienvenido. Las IAs usan el proveedor "Simulado" hasta que configures una API key en Ajustes.', 'err');
