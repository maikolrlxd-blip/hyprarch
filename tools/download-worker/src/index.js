// Entrega la ISO de hyprarch como UN solo archivo uniendo, al vuelo, las partes de la release de GitHub
// (GitHub limita cada archivo a 2 GB). No guarda nada: solo reenvía lo que GitHub sirve. Admite descargas reanudables (Range).
// Al publicar una versión nueva: cambia VERSION, FILE y los tamaños de PARTS (ver LEEME.md) y ejecuta `npx wrangler deploy`.
const REPO = "maikolrlxd-blip/hyprarch";
const VERSION = "v0.1.0-beta";
const FILE = "hyprarch-public-2026.10.09-x86_64.iso";
const PARTS = [
  { name: FILE + ".part00", size: 1992294400 },
  { name: FILE + ".part01", size: 685015040 },
];
const TOTAL = PARTS.reduce((a, p) => a + p.size, 0);
const SHA256 = "f6576aff5a56e53efe1b06a4ffcfad743e582ecc742d837d1c14c8b9cf7fbd71";
const url = (p) => `https://github.com/${REPO}/releases/download/${VERSION}/${p.name}`;

function parseRange(h) {
  const m = /^bytes=(\d*)-(\d*)$/.exec(h || "");
  if (!m || (m[1] === "" && m[2] === "")) return null;
  let s, e;
  if (m[1] === "") { s = Math.max(0, TOTAL - parseInt(m[2], 10)); e = TOTAL - 1; }
  else { s = parseInt(m[1], 10); e = m[2] === "" ? TOTAL - 1 : Math.min(parseInt(m[2], 10), TOTAL - 1); }
  return s <= e && s < TOTAL ? [s, e] : "bad";
}

export default {
  async fetch(req, env, ctx) {
    const u = new URL(req.url);
    if (u.pathname === "/sha256") return new Response(`${SHA256}  ${FILE}\n`, { headers: { "content-type": "text/plain; charset=utf-8" } });
    if (u.pathname !== "/" && u.pathname !== "/hyprarch.iso" && u.pathname !== "/" + FILE) return new Response("No encontrado", { status: 404 });
    if (req.method !== "GET" && req.method !== "HEAD") return new Response("Método no permitido", { status: 405 });
    const r = parseRange(req.headers.get("range"));
    if (r === "bad") return new Response("Rango no válido", { status: 416, headers: { "content-range": `bytes */${TOTAL}` } });
    const [s, e] = r || [0, TOTAL - 1];
    const h = {
      "content-type": "application/octet-stream",
      "content-disposition": `attachment; filename="${FILE}"`,
      "accept-ranges": "bytes",
      "content-length": String(e - s + 1),
      "cache-control": "public, max-age=300",
    };
    if (r) h["content-range"] = `bytes ${s}-${e}/${TOTAL}`;
    if (req.method === "HEAD") return new Response(null, { status: r ? 206 : 200, headers: h });
    const { readable, writable } = new TransformStream();
    ctx.waitUntil((async () => {
      try {
        let off = 0;
        for (const p of PARTS) {
          const ps = off, pe = off + p.size - 1;
          off += p.size;
          if (pe < s || ps > e) continue;
          const a = Math.max(s, ps) - ps, b = Math.min(e, pe) - ps;
          const up = await fetch(url(p), { headers: { range: `bytes=${a}-${b}` }, redirect: "follow" });
          if (!up.ok && up.status !== 206) throw new Error("origen " + up.status);
          await up.body.pipeTo(writable, { preventClose: true });
        }
        await writable.close();
      } catch (err) {
        await writable.abort(err);
      }
    })());
    return new Response(readable, { status: r ? 206 : 200, headers: h });
  },
};
