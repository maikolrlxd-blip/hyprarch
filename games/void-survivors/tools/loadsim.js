// Carga los módulos del juego (sin DOM) en un contexto de Node para pruebas y balance.
const fs = require('fs'), path = require('path'), vm = require('vm');
module.exports = function load() {
  const ctx = vm.createContext({ Math, console, Date });
  ctx.globalThis = ctx;
  for (const f of ['util', 'data', 'save', 'meta', 'sim']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname, '../js', f + '.js'), 'utf8'), ctx, { filename: f + '.js' });
  }
  return ctx.VS;
};
