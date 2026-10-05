'use strict';
const fs = require('fs');
const path = require('path');

const DEFAULT_AGENTS = [
  { id: 'luna', name: 'Luna', color: '#ff7ab8', provider: 'mock', model: '', baseUrl: '', apiKey: '',
    personality: 'Curiosa y soniadora. Le fascinan las estrellas y hace preguntas raras.' },
  { id: 'rex', name: 'Rex', color: '#5ec8ff', provider: 'mock', model: '', baseUrl: '', apiKey: '',
    personality: 'Bromista y sarcastico pero buena onda. Siempre tiene un chiste.' },
  { id: 'sage', name: 'Sage', color: '#8dff9a', provider: 'mock', model: '', baseUrl: '', apiKey: '',
    personality: 'Calmado y filosofo. Habla poco y dice cosas profundas.' },
  { id: 'nova', name: 'Nova', color: '#ffd85e', provider: 'mock', model: '', baseUrl: '', apiKey: '',
    personality: 'Energica y competitiva. Propone juegos y retos a los demas.' },
];

class Store {
  constructor(dir) {
    this.file = path.join(dir, 'ai-world.json');
  }
  load() {
    try {
      const data = JSON.parse(fs.readFileSync(this.file, 'utf8'));
      if (Array.isArray(data.agents) && data.agents.length) return data;
    } catch { /* primer arranque */ }
    return { agents: DEFAULT_AGENTS, turnSeconds: 6 };
  }
  save(data) {
    fs.mkdirSync(path.dirname(this.file), { recursive: true });
    fs.writeFileSync(this.file, JSON.stringify(data, null, 2), { mode: 0o600 });
  }
}

module.exports = { Store, DEFAULT_AGENTS };
