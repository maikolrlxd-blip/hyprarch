// Empaqueta el juego en UN solo HTML (CSS y JS incrustados): dist/void-survivors.html
// Se puede abrir con doble clic, subir a cualquier hosting estático o pasar por el móvil.
// Uso: node tools/make-singlefile.js [--fragment ruta]   (--fragment escribe solo el contenido, sin <html>/<head>)
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const css = fs.readFileSync(path.join(root, 'css/style.css'), 'utf8');
const scripts = [...html.matchAll(/<script src="([^"]+)"><\/script>/g)].map((m) => {
  const code = fs.readFileSync(path.join(root, m[1]), 'utf8');
  if (/<\/script/i.test(code)) throw new Error('</script> dentro de ' + m[1]);
  return `<script>\n/* ${m[1]} */\n${code}\n</script>`;
});
const body = html.slice(html.indexOf('<body>') + 6, html.indexOf('<script src')).trim();
const title = '<title>Void Survivors</title>';
const style = `<style>\n${css}\n:root{color-scheme:dark}\n</style>`;
const full = `<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">\n<meta name="theme-color" content="#05060f">\n${title}\n${style}\n</head>\n<body>\n${body}\n${scripts.join('\n')}\n</body>\n</html>\n`;
fs.mkdirSync(path.join(root, 'dist'), { recursive: true });
fs.writeFileSync(path.join(root, 'dist/void-survivors.html'), full);
const i = process.argv.indexOf('--fragment');
if (i > 0) fs.writeFileSync(process.argv[i + 1], `${title}\n${style}\n${body}\n${scripts.join('\n')}\n`);
console.log('dist/void-survivors.html', (full.length / 1024).toFixed(0) + ' KB');
