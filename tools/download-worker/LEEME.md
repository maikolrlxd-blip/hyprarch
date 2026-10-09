# Descarga de la ISO en un solo clic

GitHub no admite archivos de más de 2 GB, y la ISO pesa ~2,7 GB, así que en la release va en 2 partes. Este Worker de Cloudflare las une al vuelo
y las entrega como **un solo archivo `.iso`** (con descargas reanudables). No guarda nada.

- URL: `https://hyprarch-download.maikolrlxd.workers.dev/hyprarch.iso` · suma de comprobación: `/sha256`
- Publicar: `cd tools/download-worker && npx wrangler deploy`
- Versión nueva: cambia `VERSION`, `FILE`, `SHA256` y los tamaños de `PARTS` en `src/index.js` (salen de `SHA256SUMS`/`ls -l` de la release) y vuelve a publicar.
