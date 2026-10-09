// hyprarch — servidor de reportes (Cloudflare Worker + base de datos D1).
//   POST /api/report            recibe un reporte de hyprarch-report (con permiso de la persona)
//   GET  /api/reports           lista (necesita el token de administración)
//   GET  /api/reports/:id       detalle
//   PATCH /api/reports/:id      cambia estado/nota
//   GET  /admin                 visor web (pide el token; no se guarda en el servidor)
// Privacidad: no se guarda la IP (solo un hash con sal para limitar abusos); el texto se muestra siempre escapado.

const MAX_BODY = 900_000;
const LIMITS = { description: 2000, report: 250_000, screenshot: 600_000, version: 200, mode: 20, lang: 40, client: 64 };
const PER_HOUR = 5;
const PER_DAY_GLOBAL = 400;
const STATUSES = ["nuevo", "visto", "en curso", "arreglado", "descartado"];

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

async function sha256(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf)).map((b) => b.toString(16).padStart(2, "0")).join("");
}
function timingSafeEqual(a, b) {
  const x = new TextEncoder().encode(a), y = new TextEncoder().encode(b);
  if (x.length !== y.length) return false;
  let r = 0;
  for (let i = 0; i < x.length; i++) r |= x[i] ^ y[i];
  return r === 0;
}
function isAdmin(request, env) {
  const h = request.headers.get("authorization") || "";
  const tok = h.startsWith("Bearer ") ? h.slice(7) : "";
  return !!env.ADMIN_TOKEN && tok.length > 0 && timingSafeEqual(tok, env.ADMIN_TOKEN);
}
function clean(v, max) {
  return typeof v === "string" ? v.slice(0, max) : "";
}

async function handleReport(request, env) {
  const len = Number(request.headers.get("content-length") || 0);
  if (len > MAX_BODY) return json({ ok: false, error: "demasiado grande" }, 413);
  const raw = await request.text();
  if (raw.length > MAX_BODY) return json({ ok: false, error: "demasiado grande" }, 413);
  let b;
  try { b = JSON.parse(raw); } catch (e) { return json({ ok: false, error: "json inválido" }, 400); }
  const description = clean(b.description, LIMITS.description).trim();
  const report = clean(b.report, LIMITS.report);
  if (!description && !report) return json({ ok: false, error: "vacío" }, 400);
  let screenshot = clean(b.screenshot, LIMITS.screenshot);
  if (screenshot && !/^[A-Za-z0-9+/=]+$/.test(screenshot)) screenshot = "";       // solo base64 de una imagen
  const ip = request.headers.get("cf-connecting-ip") || "local";
  const ipHash = (await sha256((env.SALT || "hyprarch") + ip)).slice(0, 24);
  const now = Math.floor(Date.now() / 1000);
  await env.DB.prepare("DELETE FROM rate WHERE ts < ?").bind(now - 86400).run();
  const hour = await env.DB.prepare("SELECT COUNT(*) AS n FROM rate WHERE ip_hash = ? AND ts > ?").bind(ipHash, now - 3600).first();
  if (hour && hour.n >= PER_HOUR) return json({ ok: false, error: "demasiados reportes seguidos; prueba más tarde" }, 429);
  const day = await env.DB.prepare("SELECT COUNT(*) AS n FROM rate WHERE ts > ?").bind(now - 86400).first();
  if (day && day.n >= PER_DAY_GLOBAL) return json({ ok: false, error: "servidor ocupado; prueba más tarde" }, 429);
  await env.DB.prepare("INSERT INTO rate (ip_hash, ts) VALUES (?, ?)").bind(ipHash, now).run();
  const res = await env.DB.prepare(
    "INSERT INTO reports (created, description, report, screenshot, version, mode, lang, client, ip_hash) VALUES (?,?,?,?,?,?,?,?,?)"
  ).bind(now, description, report, screenshot, clean(b.version, LIMITS.version), clean(b.mode, LIMITS.mode), clean(b.lang, LIMITS.lang), clean(b.client, LIMITS.client), ipHash).run();
  return json({ ok: true, id: res.meta.last_row_id });
}

const ADMIN_HTML = `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reportes de hyprarch</title><style>
:root{--bg:#0b0f14;--p:#111922;--l:#1c2630;--f:#dfe9ee;--d:#7d909c;--a:#5ef2c8;--w:#ffb347}
@media (prefers-color-scheme: light){:root{--bg:#f4f6f8;--p:#fff;--l:#d9e0e6;--f:#16212b;--d:#5b6b78;--a:#0b8f6c;--w:#b4691f}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--f);font:14px/1.45 system-ui,Segoe UI,sans-serif;display:flex;height:100vh}
#side{width:380px;border-right:1px solid var(--l);display:flex;flex-direction:column}#main{flex:1;overflow:auto;padding:18px}
header{padding:12px;border-bottom:1px solid var(--l);display:flex;gap:8px;align-items:center}header b{flex:1}
input,select,button,textarea{background:var(--p);color:var(--f);border:1px solid var(--l);border-radius:8px;padding:6px 9px;font:inherit}
button{cursor:pointer}button:hover{border-color:var(--a)}
#list{overflow:auto;flex:1}.it{padding:10px 12px;border-bottom:1px solid var(--l);cursor:pointer}.it:hover,.it.on{background:var(--p)}
.it .t{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.it .m{color:var(--d);font-size:12px}
.tag{display:inline-block;border:1px solid var(--l);border-radius:9px;padding:0 8px;font-size:11px;margin-left:6px}.tag.nuevo{color:var(--w);border-color:var(--w)}.tag.arreglado{color:var(--a);border-color:var(--a)}
pre{background:var(--p);border:1px solid var(--l);border-radius:10px;padding:12px;white-space:pre-wrap;word-wrap:anywhere;max-height:60vh;overflow:auto;font:12px/1.4 ui-monospace,Consolas,monospace}
img{max-width:100%;border:1px solid var(--l);border-radius:10px}.row{display:flex;gap:8px;margin:10px 0;align-items:center;flex-wrap:wrap}
</style></head><body>
<div id="side"><header><b>Reportes</b><input id="tok" type="password" placeholder="token" size="10"><button id="go">Entrar</button></header>
<header><select id="st"><option value="">todos</option><option>nuevo</option><option>visto</option><option>en curso</option><option>arreglado</option><option>descartado</option></select><span id="cnt" style="color:var(--d)"></span></header>
<div id="list"></div></div><div id="main"><p style="color:var(--d)">Escribe el token de administración y pulsa Entrar.</p></div>
<script>
const $=id=>document.getElementById(id);let cur=null;
const H=()=>({authorization:'Bearer '+$('tok').value});
const dt=t=>new Date(t*1000).toLocaleString();
async function load(){const r=await fetch('/api/reports?status='+encodeURIComponent($('st').value),{headers:H()});if(!r.ok){$('list').textContent='Token incorrecto';return}
 const j=await r.json();sessionStorage.setItem('t',$('tok').value);$('cnt').textContent=j.reports.length+' reportes';$('list').textContent='';
 for(const x of j.reports){const d=document.createElement('div');d.className='it'+(cur===x.id?' on':'');
  const t=document.createElement('div');t.className='t';t.textContent='#'+x.id+'  '+(x.description||'(sin descripción)');
  const tg=document.createElement('span');tg.className='tag '+x.status.replace(' ','');tg.textContent=x.status;t.append(tg);
  const m=document.createElement('div');m.className='m';m.textContent=dt(x.created)+' · '+x.mode+' · '+x.version;d.append(t,m);d.onclick=()=>show(x.id);$('list').append(d)}}
async function show(id){cur=id;const r=await fetch('/api/reports/'+id,{headers:H()});const x=await r.json();const m=$('main');m.textContent='';
 const h=document.createElement('h2');h.textContent='#'+x.id+' · '+dt(x.created);m.append(h);
 const p=document.createElement('p');p.textContent=x.description||'(sin descripción)';m.append(p);
 const meta=document.createElement('p');meta.style.color='var(--d)';meta.textContent=[x.mode,x.version,x.lang,'equipo '+(x.client||'?').slice(0,8)].join(' · ');m.append(meta);
 const row=document.createElement('div');row.className='row';const sel=document.createElement('select');for(const s of ${JSON.stringify(STATUSES)}){const o=document.createElement('option');o.textContent=s;if(s===x.status)o.selected=true;sel.append(o)}
 const note=document.createElement('input');note.placeholder='nota (qué se hizo)';note.size=40;note.value=x.note||'';
 const b=document.createElement('button');b.textContent='Guardar';b.onclick=async()=>{await fetch('/api/reports/'+id,{method:'PATCH',headers:Object.assign({'content-type':'application/json'},H()),body:JSON.stringify({status:sel.value,note:note.value})});load()};
 row.append(sel,note,b);m.append(row);
 if(x.screenshot){const i=document.createElement('img');i.src='data:image/png;base64,'+x.screenshot;m.append(i)}
 const pre=document.createElement('pre');pre.textContent=x.report;m.append(pre);load()}
$('go').onclick=load;$('st').onchange=load;$('tok').value=sessionStorage.getItem('t')||'';if($('tok').value)load();
</script></body></html>`;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";
    try {
      if (path === "/api/report" && request.method === "POST") return await handleReport(request, env);
      if (path === "/admin") return new Response(ADMIN_HTML, { headers: { "content-type": "text/html; charset=utf-8", "content-security-policy": "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'self'", "cache-control": "no-store" } });
      if (path === "/") return new Response("hyprarch reportes: ok", { headers: { "content-type": "text/plain; charset=utf-8" } });
      if (path.startsWith("/api/reports")) {
        if (!isAdmin(request, env)) return json({ ok: false, error: "no autorizado" }, 401);
        const m = path.match(/^\/api\/reports(?:\/(\d+))?$/);
        if (!m) return json({ ok: false }, 404);
        if (!m[1] && request.method === "GET") {
          const st = url.searchParams.get("status") || "";
          const lim = Math.min(Number(url.searchParams.get("limit") || 200), 500);
          const q = st
            ? env.DB.prepare("SELECT id, created, description, version, mode, status FROM reports WHERE status = ? ORDER BY id DESC LIMIT ?").bind(st, lim)
            : env.DB.prepare("SELECT id, created, description, version, mode, status FROM reports ORDER BY id DESC LIMIT ?").bind(lim);
          const { results } = await q.all();
          return json({ ok: true, reports: results });
        }
        if (m[1] && request.method === "GET") {
          const row = await env.DB.prepare("SELECT id, created, description, report, screenshot, version, mode, lang, client, status, note FROM reports WHERE id = ?").bind(Number(m[1])).first();
          return row ? json(row) : json({ ok: false }, 404);
        }
        if (m[1] && request.method === "PATCH") {
          const b = await request.json();
          const status = STATUSES.includes(b.status) ? b.status : null;
          if (!status) return json({ ok: false, error: "estado no válido" }, 400);
          await env.DB.prepare("UPDATE reports SET status = ?, note = ? WHERE id = ?").bind(status, clean(b.note, 2000), Number(m[1])).run();
          return json({ ok: true });
        }
      }
      return json({ ok: false }, 404);
    } catch (e) {
      return json({ ok: false, error: "error interno" }, 500);
    }
  },
};
