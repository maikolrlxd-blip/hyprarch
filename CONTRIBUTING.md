# Contribuir a hyprarch

Ahora mismo lo más útil es **probarlo y contarlo**.

1. Sigue [`docs/GUIA-PROBADORES.md`](docs/GUIA-PROBADORES.md) (USB en modo «en vivo» o máquina virtual).
2. Si algo falla: SUPER → **«Reportar un problema»** (o `hyprarch-report`), o abre una *issue* con la plantilla.
3. Cuéntanos tu equipo (marca, modelo, gráficos, Wi-Fi, audio) y qué hacías.

## Código
- Los scripts están en `airootfs/usr/local/bin/` (bash y Python/GTK4). Antes de proponer cambios: `shellcheck` para bash y `python -m py_compile` para Python.
- Prueba en una VM antes de abrir un *pull request* (el instalador y la sesión gráfica no se prueban solo leyendo código).
- Al contribuir aceptas que tu aportación se distribuya bajo la licencia del proyecto ([PolyForm Noncommercial](LICENSE)).
- Para uso comercial o derivados de pago: abre una *issue* «Licencia comercial» (ver [`LICENSING.md`](LICENSING.md)).
