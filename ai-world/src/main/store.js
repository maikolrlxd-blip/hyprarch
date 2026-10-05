'use strict';
const fs = require('fs');
const path = require('path');



class Store {
  constructor(dir, defaults) {
    this.file = path.join(dir, 'ai-world.json');
    this.defaults = defaults; // { agents, turnSeconds } (viene de src/shared/defaults.mjs)
  }
  load() {
    try {
      const data = JSON.parse(fs.readFileSync(this.file, 'utf8'));
      if (Array.isArray(data.agents) && data.agents.length) return data;
    } catch { /* primer arranque */ }
    return structuredClone(this.defaults);
  }
  save(data) {
    fs.mkdirSync(path.dirname(this.file), { recursive: true });
    fs.writeFileSync(this.file, JSON.stringify(data, null, 2), { mode: 0o600 });
  }
}

module.exports = { Store };
