# Void Survivors

Roguelite de supervivencia espacial (estilo "survivor") hecho en HTML5/Canvas, sin dependencias ni assets externos. Se empaqueta como app Android con un WebView (ver `../build-android.sh`).

## Qué incluye

- **Partida:** movimiento con joystick flotante, disparo automático, hordas con un director de dificultad, élites, enjambres, 3 jefes con patrones distintos, cofres, imanes y botiquines.
- **Build por partida:** 6 armas × 6 niveles y 10 pasivos × 5 niveles; al subir de nivel eliges 1 de 3 mejoras (con cambios y opción de 4ª carta).
- **Meta-progresión:** monedas → 11 mejoras permanentes, 5 naves (compra o desbloqueo), 3 fases (se desbloquean al ganar la anterior).
- **Retención:** misiones diarias deterministas, racha de login de 7 días, 15 logros.
- **Extras:** español/inglés, música y efectos procedurales (WebAudio), vibración, tutorial en la primera partida, pausa automática al salir de la app, guardado local versionado.
- **Anuncios:** capa `js/ads.js` lista para AdMob (revivir y duplicar monedas). Sin proveedor, los botones no se muestran.

## Estructura

```
index.html  css/style.css
js/util.js data.js i18n.js     utilidades, balance y textos
js/save.js meta.js             guardado y meta-progresión (sin DOM)
js/sim.js                      simulación de la partida (sin DOM, determinista con rand inyectado)
js/render.js audio.js input.js icons.js ui.js main.js   presentación y flujo
tools/                         bots y barridos de balance en Node
store/                         textos de la ficha, política de privacidad, gráficos
```

## Probar

```bash
cd games/void-survivors && python3 -m http.server 8000   # abrir http://localhost:8000/?dev=1
```
`?dev=1` simula anuncios recompensados para probar esos botones.

## Balance

Todo el balance está en `js/data.js` (`D.tune`, `D.stages`, `D.weapons`...). La simulación no toca el DOM, así que se puede simular en Node:

```bash
cd tools
node bot.js 6 s1 falcon                 # 6 partidas de un bot en la fase 1
node sweep.js s2 '{"rate0":1.8}' 8      # barrido de parámetros (fase 2) con 8 semillas
node test.js                            # pruebas de lógica (meta-progresión, misiones, guardado)
```
