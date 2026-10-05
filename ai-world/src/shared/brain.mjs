// "Cerebro" de cada IA: arma el prompt a partir de lo que percibe y
// convierte la respuesta del modelo en una decision (hablar + accion).

export const ACTIONS = ['idle', 'walk_to', 'wave', 'dance', 'jump'];

export function buildSystem(agent) {
  return [
    `Eres ${agent.name}, un personaje con cuerpo fisico dentro de una isla flotante bioluminiscente (un mundo virtual 3D) compartida con otras IAs y con un humano.`,
    `Personalidad: ${agent.personality}`,
    'Hablas en espanol, en frases cortas (maximo 2) como en una charla casual. No narres tus acciones en el texto, para eso esta el campo "action".',
    'Respondes SIEMPRE y SOLO con un objeto JSON, sin texto extra ni markdown:',
    '{"say": "<lo que dices en voz alta, o cadena vacia para callar>", "action": "<idle|walk_to|wave|dance|jump>", "target": "<nombre de otro personaje, o \'centro\', o \'x,z\' si action es walk_to>"}',
    'Callar esta bien: no hables en todos los turnos. Reacciona a lo que oyes y a quien tienes cerca.',
  ].join('\n');
}

export function buildPerception(agent, world) {
  const others = world.others
    .map(o => `- ${o.name} (${o.kind}) a ${o.distance.toFixed(1)} m, ${o.doing}`)
    .join('\n') || '- nadie';
  const log = world.log.length
    ? world.log.map(l => `${l.from}: ${l.text}`).join('\n')
    : '(todavia nadie ha dicho nada)';
  return `Estas en x=${world.self.x.toFixed(1)}, z=${world.self.z.toFixed(1)}. Estas en una isla flotante circular de ${(world.size / 2).toFixed(0)} m de radio; el centro (0,0) es un cristal brillante.\n` +
    `Otros en el mundo:\n${others}\n\nConversacion reciente:\n${log}\n\nTu turno. Responde con el JSON.`;
}

// Los modelos a veces envuelven el JSON en ```; extraemos el primer objeto valido.
export function parseDecision(raw) {
  const fallback = { say: '', action: 'idle', target: '' };
  if (typeof raw !== 'string') return fallback;
  const start = raw.indexOf('{');
  const end = raw.lastIndexOf('}');
  if (start === -1 || end <= start) return { ...fallback, say: raw.trim().slice(0, 200) };
  try {
    const o = JSON.parse(raw.slice(start, end + 1));
    return {
      say: typeof o.say === 'string' ? o.say.trim().slice(0, 240) : '',
      action: ACTIONS.includes(o.action) ? o.action : 'idle',
      target: o.target == null ? '' : String(o.target),
    };
  } catch {
    return { ...fallback, say: raw.slice(0, 200).trim() };
  }
}

// Convierte el historial en mensajes user/assistant alternados (requisito de Anthropic/Gemini).
export function toMessages(history, perception) {
  const msgs = [];
  for (const h of history) {
    const last = msgs[msgs.length - 1];
    if (last && last.role === h.role) last.content += '\n' + h.content;
    else msgs.push({ ...h });
  }
  if (msgs.length && msgs[msgs.length - 1].role === 'user') msgs[msgs.length - 1].content += '\n\n' + perception;
  else msgs.push({ role: 'user', content: perception });
  if (msgs[0].role !== 'user') msgs.unshift({ role: 'user', content: '(inicio)' });
  return msgs;
}


const MAX_HISTORY = 10;

// Un turno completo de una IA: percibe -> consulta al modelo -> decision. Lo usan la PC y el celular.
export async function think({ agent, world, history = [], chat, http }) {
  const perception = buildPerception(agent, world);
  const raw = await chat({ agent, system: buildSystem(agent), messages: toMessages(history, perception) }, http);
  const decision = parseDecision(raw);
  const next = [...history, { role: 'user', content: perception }, { role: 'assistant', content: JSON.stringify(decision) }].slice(-MAX_HISTORY);
  return { decision, history: next };
}
