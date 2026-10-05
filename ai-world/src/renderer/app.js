import { World, ROOM } from './world.js';

const $ = id => document.getElementById(id);
const world = new World($('scene'));
// Tres formas de ejecutarse:
//  - Electron (PC): `window.aiWorld` -> anfitrion; las IAs corren en el proceso principal.
//  - App Android independiente: `window.AiNative` -> anfitrion local; las IAs corren en el telefono.
//  - Navegador/WebView apuntando a la PC: sin ninguno -> cliente que solo muestra el mundo.
const api = window.aiWorld || (window.AiNative ? (await import('./standalone.js')).createStandaloneApi(window.AiNative) : null);
const isHost = !!api;
const isStandalone = !!api?.standalone;
document.body.classList.add(isHost ? 'host' : 'remote');
if (isStandalone) document.body.classList.add('standalone');

let agents = [];          // { id, name, color, provider, ... }
const thinking = new Set();
const log = [];           // { from, text } (solo anfitrion: lo que oyen las IAs)
const LOG_WINDOW = 12;

// ---------- UI comun ----------
function addLine(from, text, cls = '', color = '') {
  const el = document.createElement('div');
  el.className = 'line ' + cls;
  const b = document.createElement('b'); b.textContent = from; if (color) { b.style.color = color; el.style.setProperty('--c', color); }
  el.append(b, document.createTextNode(text));
  const box = $('log'); box.append(el); box.scrollTop = box.scrollHeight;
  while (box.children.length > 300) box.firstChild.remove();
}

function renderRoster() {
  world.setThinking(thinking);
  $('roster').replaceChildren(...agents.map(a => {
    const li = document.createElement('li');
    if (thinking.has(a.id)) li.className = 'thinking';
    const dot = document.createElement('span'); dot.className = 'dot'; dot.style.background = a.color;
    li.append(dot, `${a.name} · ${a.provider}`);
    return li;
  }));
}

function setAgents(list) {
  agents = list; world.setAgents(agents); renderRoster();
}

function doSay(id, text) {
  const a = agents.find(x => x.id === id); const av = world.avatars.get(id);
  if (!av) return;
  av.say(text); addLine(a.name, text, '', a.color);
}
function doAct(id, action, x, z, stop) {
  const av = world.avatars.get(id); if (!av) return;
  if (action === 'walk_to') av.walkTo(x, z, stop); else av.perform(action);
}
function publicAgents() { return agents.map(({ id, name, color, provider }) => ({ id, name, color, provider })); }

$('pause').addEventListener('click', () => togglePause());
let paused = false;
function togglePause() { paused = !paused; $('pause').textContent = paused ? 'Reanudar' : 'Pausar'; }

// =====================================================================
//  ANFITRION (PC): corre las IAs y retransmite todo a los celulares
// =====================================================================
async function startHost() {
  const config = await api.getConfig();
  let turnIndex = 0, sinceTurn = 0;

  const perceive = agent => {
    const self = world.avatars.get(agent.id);
    return {
      self: { x: self.position.x, z: self.position.z }, size: ROOM, log: log.slice(-LOG_WINDOW),
      others: [...world.avatars.values()].filter(o => o !== self).map(o => ({
        name: o.name, kind: 'IA', distance: o.position.distanceTo(self.position), doing: o.describe() })),
    };
  };
  const sendThinking = () => api.netEvent({ type: 'thinking', ids: [...thinking] });

  async function takeTurn(agent) {
    const av = world.avatars.get(agent.id);
    if (!av || thinking.has(agent.id)) return;
    thinking.add(agent.id); renderRoster(); sendThinking();
    try {
      const res = await api.think({ agentId: agent.id, world: perceive(agent) });
      if (res.error) { addLine(agent.name, res.error, 'err'); return; }
      const { say, action, target } = res.decision;
      let x = 0, z = 0, stop = 0;
      if (action === 'walk_to') { ({ x, z, stop } = world.resolveTarget(av, target)); }
      doAct(agent.id, action, x, z, stop);
      api.netEvent({ type: 'act', id: agent.id, action, x, z, stop });
      if (say) {
        doSay(agent.id, say); log.push({ from: agent.name, text: say });
        api.netEvent({ type: 'say', id: agent.id, name: agent.name, color: agent.color, text: say });
      }
    } finally { thinking.delete(agent.id); renderRoster(); sendThinking(); }
  }

  // Un turno cada turnSeconds, rotando entre IAs: limita el gasto de API y evita que hablen todas a la vez.
  setInterval(() => {
    if (paused || !agents.length) return;
    if (++sinceTurn < config.turnSeconds) return;
    sinceTurn = 0; takeTurn(agents[turnIndex++ % agents.length]);
  }, 1000);

  // Foto de posiciones para los celulares (corrige deriva y sirve a quien se conecta tarde).
  setInterval(() => {
    const pos = {};
    for (const [id, av] of world.avatars) pos[id] = [+av.position.x.toFixed(2), +av.position.z.toFixed(2)];
    api.netState({ agents: publicAgents(), pos });
  }, 500);

  // Un humano (PC o celular) habla: la siguiente IA responde de inmediato.
  function humanSays(from, text, mine) {
    log.push({ from: mine ? 'Humano' : `Humano (${from})`, text });
    addLine(mine ? 'Tu' : from, text, 'me');
    api.netEvent({ type: 'human', from: mine ? 'Anfitrion' : from, text });
    if (!paused && agents.length) { sinceTurn = 0; takeTurn(agents[turnIndex++ % agents.length]); }
  }
  $('chat').addEventListener('submit', e => {
    e.preventDefault(); const text = $('msg').value.trim(); if (!text) return;
    $('msg').value = ''; humanSays('', text, true);
  });
  api.onNetChat(c => humanSays(c.from, c.text, false));

  // ---- Ajustes ----
  const agentCard = a => {
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
  };
  $('settings').onclick = () => {
    $('turn').value = config.turnSeconds;
    $('agentList').replaceChildren(...agents.map(agentCard));
    $('dlg').showModal();
  };
  $('cancel').onclick = () => $('dlg').close();
  $('addAgent').onclick = () => $('agentList').append(agentCard({
    id: 'ia-' + Date.now().toString(36), name: 'Nueva IA', color: '#c58bff', provider: 'mock', model: '', baseUrl: '', apiKey: '', personality: 'Amistosa y curiosa.' }));
  $('dlgForm').addEventListener('submit', async () => {
    const list = [...$('agentList').children].map(el => {
      const a = { id: el.dataset.id };
      for (const f of el.querySelectorAll('[data-f]')) a[f.dataset.f] = f.value.trim();
      return a;
    }).filter(a => a.name);
    config.turnSeconds = Math.max(2, +$('turn').value || 6);
    await api.saveConfig({ agents: list, turnSeconds: config.turnSeconds });
    setAgents(list);
  });

  // ---- Conectar celular ----
  let mobileOn = false;
  $('mobile').onclick = async () => {
    $('mobileDlg').showModal();
    if (mobileOn) return;
    const info = await api.netStart(); mobileOn = true;
    $('qr').src = info.qr; $('mobileUrl').textContent = info.url;
    $('mobileOthers').textContent = info.urls.length > 1 ? 'Otras direcciones: ' + info.urls.slice(1).join('  ') : '';
    if (!info.urls.length) $('mobileUrl').textContent += '  (no se detecto red local: conectate a la misma Wi-Fi)';
  };
  $('mobileClose').onclick = () => $('mobileDlg').close();
  $('mobileStop').onclick = async () => {
    await api.netStop(); mobileOn = false; $('qr').removeAttribute('src'); $('mobileUrl').textContent = ''; $('mobileDlg').close();
    $('mobile').textContent = 'Celular';
  };
  api.onNetClients(n => { $('mobile').textContent = n ? `Celular (${n})` : 'Celular'; $('mobileCount').textContent = n; });

  setAgents(config.agents);
  if (isStandalone) {
    $('menuBtn').onclick = () => api.exit();
    addLine('Sistema', 'Modo independiente: las IAs viven en tu celular. Usan el proveedor "Simulado" hasta que agregues una API key en Ajustes (necesitas internet para los modelos reales).', 'err');
  } else {
    addLine('Sistema', 'Bienvenido. Las IAs usan el proveedor "Simulado" hasta que configures una API key en Ajustes. Pulsa "Celular" para conectar tu telefono.', 'err');
  }
}

// =====================================================================
//  CLIENTE (celular / navegador): solo muestra el mundo y chatea
// =====================================================================
function startRemote() {
  const token = new URLSearchParams(location.search).get('t') || '';
  let ws, retry = 0, hadHello = false;
  const status = msg => { $('status').textContent = msg; $('status').hidden = !msg; };

  function sig(list) { return list.map(a => a.id + a.name + a.color).join('|'); }
  function applyPositions(pos, soft) {
    for (const [id, [x, z]] of Object.entries(pos || {})) {
      const av = world.avatars.get(id); if (!av) continue;
      if (soft && av.position.distanceTo({ x, y: 0, z }) < 3) { av.position.x += (x - av.position.x) * 0.3; av.position.z += (z - av.position.z) * 0.3; }
      else { av.position.x = x; av.position.z = z; }
    }
  }
  function sync(m, soft) {
    if (sig(m.agents) !== sig(agents)) { setAgents(m.agents); applyPositions(m.pos, false); }
    else applyPositions(m.pos, soft);
  }

  function connect() {
    status(retry ? 'Reconectando...' : 'Conectando...');
    ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws?t=${encodeURIComponent(token)}`);
    ws.onopen = () => { retry = 0; status(''); };
    ws.onclose = () => { status('Sin conexion con la PC. Reintentando...'); setTimeout(connect, Math.min(1000 * 2 ** retry++, 8000)); };
    ws.onmessage = ev => {
      const m = JSON.parse(ev.data);
      if (m.type === 'hello') {
        sync(m, false); $('log').replaceChildren(); hadHello = true;
        for (const l of m.log) l.type === 'say' ? addLine(l.name, l.text, '', l.color) : addLine(l.from, l.text, 'me');
      } else if (!hadHello) return;
      else if (m.type === 'snap') sync(m, true);
      else if (m.type === 'act') doAct(m.id, m.action, m.x, m.z, m.stop);
      else if (m.type === 'say') doSay(m.id, m.text);
      else if (m.type === 'human') addLine(m.from, m.text, 'me');
      else if (m.type === 'thinking') { thinking.clear(); m.ids.forEach(i => thinking.add(i)); renderRoster(); }
    };
  }
  $('chat').addEventListener('submit', e => {
    e.preventDefault(); const text = $('msg').value.trim();
    if (!text || ws?.readyState !== 1) return;
    $('msg').value = ''; ws.send(JSON.stringify({ type: 'chat', text }));
    // el anfitrion devuelve el mensaje como evento 'human', no lo duplicamos aqui
  });
  $('pause').remove(); $('settings').remove(); $('mobile').remove();
  connect();
}

const hideSplash = () => setTimeout(() => $('splash').classList.add('hide'), 700);
(isHost ? startHost() : Promise.resolve(startRemote())).finally(hideSplash);
