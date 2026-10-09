# Servidor de reportes de hyprarch

Recibe los reportes que la gente envía con **«Reportar un problema» → «Enviar a los desarrolladores»** y los guarda en una base de datos
(Cloudflare D1) para verlos y arreglarlos. Gratis en el plan básico de Cloudflare.

- `src/index.js` — el Worker: `POST /api/report` (público, con límite de 5 por hora y persona, tamaño máximo, sin guardar la IP),
  `GET/PATCH /api/reports…` (solo con el token de administración) y `/admin` (visor web: lista, filtros por estado, capturas, notas).
- `schema.sql` — tablas `reports` y `rate`.
- `wrangler.toml` — configuración (falta el `database_id` real).

## Poner en marcha (una sola vez; necesita una cuenta gratuita de Cloudflare)
```
cd tools/report-server
npm install wrangler@4
npx wrangler login                              # abre el navegador: inicias sesión TÚ
npx wrangler d1 create hyprarch-reports         # imprime un database_id → pegarlo en wrangler.toml
npx wrangler d1 execute hyprarch-reports --remote --file schema.sql
npx wrangler secret put ADMIN_TOKEN             # una clave larga que solo conocéis tú y quien administre
npx wrangler secret put SALT                    # texto al azar (para el hash de la IP)
npx wrangler deploy                             # imprime https://hyprarch-reports.<tu-cuenta>.workers.dev
```
Después se escribe esa dirección en `airootfs/usr/share/hyprarch/report-endpoint` (una línea) y se recompila la ISO:
con el archivo vacío, la opción «Enviar» no aparece.

## Ver y corregir los reportes
- Navegador: `https://…workers.dev/admin` (pide el token).
- Por comandos (yo/Claude): `curl -H "authorization: Bearer $TOKEN" https://…/api/reports?status=nuevo` y `/api/reports/<id>`;
  cambiar estado: `curl -X PATCH … -d '{"status":"arreglado","note":"qué se hizo"}'`.

## Privacidad
Antes de enviar, el cliente quita usuario, nombre del equipo, direcciones MAC e IP, y pide permiso con la lista de lo que se manda.
La captura de pantalla solo va si la persona la aceptó. Sin Internet, el reporte espera en cola y se reenvía después.
