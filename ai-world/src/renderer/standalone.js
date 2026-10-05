// Modo independiente (app Android): la misma API que expone Electron (`window.aiWorld`),
// pero las IAs corren aqui, en el telefono, sin necesidad de la PC.
// - La configuracion (incluidas las API keys) se guarda en el almacenamiento privado de la app.
// - Las llamadas HTTP a los modelos pasan por el puente nativo (`native.http`), que no tiene CORS.
import { PROVIDERS, chat } from '../shared/providers.mjs';
import { think } from '../shared/brain.mjs';
import { DEFAULT_AGENTS, DEFAULT_TURN_SECONDS } from '../shared/defaults.mjs';

const STORAGE_KEY = 'aiworld-config-v1';
const HTTP_TIMEOUT_MS = 100000;

export function createStandaloneApi(native) {
  const pending = new Map();
  let seq = 0;

  const settle = (id, fn) => { const p = pending.get(id); if (!p) return; pending.delete(id); clearTimeout(p.timer); fn(p); };
  // Los llama Java con el resultado de la peticion.
  window.__aiHttp = (id, status, text) => settle(id, p => {
    if (status < 200 || status >= 300) return p.reject(new Error(`HTTP ${status}: ${String(text).slice(0, 300)}`));
    try { p.resolve(JSON.parse(text)); } catch { p.reject(new Error('Respuesta no JSON: ' + String(text).slice(0, 200))); }
  });
  window.__aiHttpErr = (id, message) => settle(id, p => p.reject(new Error(message)));

  const http = (url, headers, body) => new Promise((resolve, reject) => {
    const id = 'h' + (++seq);
    const timer = setTimeout(() => settle(id, p => p.reject(new Error('Tiempo de espera agotado'))), HTTP_TIMEOUT_MS);
    pending.set(id, { resolve, reject, timer });
    native.http(id, url, JSON.stringify(headers || {}), JSON.stringify(body));
  });

  const load = () => {
    try {
      const d = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (Array.isArray(d?.agents) && d.agents.length) return d;
    } catch { /* primer arranque o almacenamiento vacio */ }
    return { agents: structuredClone(DEFAULT_AGENTS), turnSeconds: DEFAULT_TURN_SECONDS };
  };
  const histories = new Map();

  return {
    standalone: true,
    getConfig: async () => ({ ...load(), providers: PROVIDERS }),
    saveConfig: async cfg => {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ agents: cfg.agents, turnSeconds: cfg.turnSeconds }));
      for (const id of [...histories.keys()]) if (!cfg.agents.some(a => a.id === id)) histories.delete(id);
      return true;
    },
    think: async ({ agentId, world }) => {
      const agent = load().agents.find(a => a.id === agentId);
      if (!agent) return { error: 'Agente no encontrado' };
      try {
        const { decision, history } = await think({ agent, world, history: histories.get(agentId) || [], chat, http });
        histories.set(agentId, history);
        return { decision };
      } catch (err) {
        return { error: String(err.message || err) };
      }
    },
    // Sin PC no hay servidor para otros dispositivos: estas funciones no hacen nada.
    netStart: async () => ({ urls: [], url: '', qr: '' }),
    netStop: async () => {},
    netEvent: () => {},
    netState: () => {},
    onNetChat: () => {},
    onNetClients: () => {},
    exit: () => native.exit(),
  };
}
