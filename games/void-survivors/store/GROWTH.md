# Estrategia de crecimiento — Void Survivors

Resumen de la investigación de mercado (octubre 2026), qué se aplicó al juego y el plan para lanzarlo con criterio. **No hay garantía de éxito**: el propio mercado es un "cementerio del 95 %", y esto sirve para tomar decisiones con datos y no a ciegas.

## 1. Lo que dicen los datos

| Hallazgo | Fuente |
|---|---|
| Mediana de retención: **D1 ≈ 22 %, D7 < 4 %, D30 ≈ 0,7-0,8 %**. El 1 % superior llega a D1 64-68 % | [GameAnalytics 2026](https://www.gameanalytics.com/reports/2026-mobile-pc-gaming-benchmarks), [AppFollow](https://appfollow.io/blog/mobile-game-retention) |
| Cuartil superior en Android: **D1 25-27 %**. Objetivo antes de gastar en marketing: D1 ≥ 25-28 %, D7 ≥ 7-8 %, D30 ≥ 3 % | [Game Growth Advisor](https://gamegrowthadvisor.com/blog/2025-12-16-mobile-soft-launch-complete-guide/) |
| D1 < 25 % ⇒ rediseñar la primera experiencia; D1 > 40 % ⇒ 1-2 iteraciones de pulido | [Mobile Dev Memo](https://mdm.co/dear-indie-mobile-game-developer/) |
| D1 es el techo de todo lo demás: si el 80 % se va el primer día, D7 no puede pasar del 20 % | [Solsten](https://solsten.io/blog/d1-d7-d30-retention-in-gaming) |
| El descubrimiento orgánico "ha colapsado"; los indies sin presupuesto son invisibles por defecto | [CAS.ai](https://cas.ai/blog/the-mobile-game-publishing-reality-why-most-indies-fail-and-what-actually-works/), [Pixelpicked](https://pixelpicked.com/blogs/why-indie-mobile-games-keep-dying) |
| De cada 100 lanzamientos indie, ~1 llega a 10.000 USD/mes; con editor, ~1 de cada 10 | [CAS.ai](https://cas.ai/blog/the-mobile-game-publishing-reality-why-most-indies-fail-and-what-actually-works/) |
| Un soft launch serio cuesta 11.000-23.000 USD (4 semanas, un mercado) | [Game Growth Advisor](https://gamegrowthadvisor.com/blog/2025-12-16-mobile-soft-launch-complete-guide/) |
| Fórmula de Survivor.io (Habby): coger un juego probado, estética casual, pulir la UX y añadir meta de progresión. >500 M USD en IAP, pero **retención D30 baja y techo de progresión** | [PocketGamer.biz](https://pocketgamer.biz/feature/79592/how-innovation-and-iteration-has-transformed-survivorio), [Naavik](https://naavik.co/deep-dives/survivorio-archeros-footsteps/) |
| Fallo de diseño a evitar: trocear recompensas en piezas pequeñas aumenta la sensación de grind sin avance visible | [Naavik](https://naavik.co/deep-dives/survivorio-archeros-footsteps/) |
| Monetización "free-for-real" de Vampire Survivors: anuncios solo opcionales, nunca interrumpen | [PocketGamer.biz](https://pocketgamer.biz/news/80554/vampire-survivors-developer-takes-new-approach-to-monetisation) |
| Primera sesión: ir al juego en segundos, un momento de poder en los primeros 5 min, meta introducida en las 3-5 primeras sesiones | [Supersonic](https://supersonic.com/learn/blog/6-ways-to-boost-your-games-retention-from-d1-d7/), [Department of Play](https://departmentofplay.net/guide-harnessing-the-hybridcasual-opportunity/) |
| Cuentas personales nuevas de Play: **12 testers durante 14 días seguidos** (y Google comprueba que usen la app) antes de producción | [Play Console Help](https://support.google.com/googleplay/android-developer/answer/14151465?hl=en), [TestersCommunity](https://www.testerscommunity.com/blog/google-play-closed-testing-requirements-2026) |
| ASO en Play: las 3 primeras capturas y la descripción corta (80 car.) pesan más; los *Store Listing Experiments* permiten probar hasta 3 variantes | [AppTweak](https://www.apptweak.com/en/aso-blog/app-store-optimization-aso-checklist-for-google-play) |
| Sin presupuesto: 3-5 vídeos verticales por semana rinden más que un intento viral al mes; Reddit (r/IndieDev, r/IndieGaming, r/playmygame) y devlogs; el alcance orgánico de TikTok ha bajado desde 2025 | [Phantom Cave](https://phantomcave.com/blog/market-indie-game-2026/), [Presskit.gg](https://presskit.gg/field-guides/tiktok-indie-game-marketing) |

## 2. Qué se aplicó al juego a raíz de esto

| Palanca | Cambio |
|---|---|
| **D1 / primera sesión** | La primera vez se entra directo a jugar (sin menús). Primera partida con ayuda: XP ×1,8 durante 2,5 min, enemigos más blandos, cofre regalo a los 25 s (el primer "momento de poder"), consejos de 3 frases. |
| **Meta temprana (sesiones 1-5)** | Mínimo de 150 monedas en las 2 primeras partidas, botón "Mejorar nave" tras la partida, insignia en *Mejoras* cuando puedes comprar algo. |
| **Razones para volver** | Misiones diarias, racha de 7 días, logros, nave que se desbloquea al ganar la fase 1. |
| **Techo de progresión (lección Survivor.io)** | Evoluciones de armas, 3 dificultades por fase (más monedas), 5 naves, 11 mejoras. Todo está en `js/data.js` para añadir contenido rápido. |
| **Monetización ética** | Solo anuncios recompensados opcionales (revivir, duplicar monedas) y nunca interrumpen. Desactivados hasta integrar el SDK. |
| **ASO / conversión** | Capturas con gameplay real y las 3 primeras con lo más atractivo (menú, horda, jefe), gráfico de funciones e icono propios, descripción corta con la palabra clave. |
| **Marketing sin presupuesto** | 3 clips verticales de gameplay real en `store/video/` (horda, jefe, evolución) y plantilla de publicaciones (abajo). |
| **Valoraciones** | Petición única y no intrusiva de valoración tras ganar (o a la 4.ª partida). |

## 3. Plan con puertas de decisión

**Fase 0 — Listo (esto):** juego, tests, CI, material de tienda.

**Fase 1 — Prueba cerrada (semanas 1-3, coste ≈ 0 + 25 USD de cuenta)**
1. Publica el AAB firmado en *Prueba cerrada* y recluta ≥ 12 testers reales (amigos, comunidades como r/playmygame, Discord de indies). Pídeles que jueguen 3 días distintos: Google verifica el uso.
2. Observa en Play Console: *Android vitals* (cuelgues y ANR), retención de instaladores y comentarios.
3. **Puerta:** cuelgues/ANR por debajo de los umbrales de Play ("mal comportamiento") y ≥ 70 % de testers que completan la fase 1. Si no, arregla antes de seguir.

**Fase 2 — Lanzamiento limitado (semanas 4-8)**
1. Publica en producción solo en países baratos y con buen encaje (p. ej. México, Colombia, Argentina, Filipinas, Indonesia) y mide D1/D7.
2. Empieza el calendario de contenido (sección 4). Anuncios de pago opcionales con 5-10 USD/día solo para medir D1, **no** para escalar.
3. **Puerta:** D1 ≥ 25 % y D7 ≥ 7 % ⇒ ampliar países y activar anuncios recompensados. D1 < 25 % ⇒ iterar el tutorial/primera partida (las pruebas de `tools/bot.js` permiten recalibrar dificultad en minutos) antes de seguir.

**Fase 3 — Operación en vivo (mes 3+)**
- Un contenido nuevo cada 2 semanas (nave, arma, fase o evento temporal). Las iteraciones frecuentes son lo que separa a los juegos que crecen de los que mueren (CAS.ai estima 11-18 meses de actualizaciones bisemanales para ver crecimiento real).
- Localizar a pt-BR, id, fil/es-LATAM para los mercados con CPI bajo.
- Si el D1 es bueno pero falta alcance: buscar editor o programa de apoyo de Google Play.

## 4. Calendario de contenido (3-5 vídeos/semana)

Ganchos que funcionan en este género (números que suben, caos controlado, "momento de poder"):

1. **Horda** — `clip-horda.mp4`: "Esto es lo que pasa a los 2:30 con la build correcta".
2. **Jefe** — `clip-jefe.mp4`: "Derroté al Centinela sin recibir daño" (o "con la peor build").
3. **Evolución** — `clip-evolucion.mp4`: "Combina X + Y y mira lo que pasa".
4. Ideas siguientes: *build rota* de la semana, *antes/después* de una mejora permanente, *reto* "gana la fase 3 con la nave inicial".

Publicar como YouTube Shorts, TikTok, Instagram Reels y un *devlog* semanal en r/IndieDev / r/IndieGaming. Sigue sus normas de autopromoción: aporta algo (una lección, una gráfica de equilibrio) y no solo el enlace. Los clips se graban sin audio: añade música en el editor de tu elección.

**Plantilla de post (Reddit / devlog):**
> Estoy haciendo un survivor espacial para Android en solitario. Esta semana: **[cambio concreto]**. Me costó **[dato]** y aprendí **[lección]**. Busco testers para la prueba cerrada (cuesta 2 min, solo hay que jugar 3 días): [enlace].

## 5. Qué NO hacer (errores que describen las fuentes)
- Gastar 10-20 k en anuncios y parar antes de tener datos fiables.
- Escalar marketing con D1 < 25 %.
- Meter anuncios intrusivos: va contra la propuesta y la retención.
- Repartir esfuerzo entre muchos juegos pequeños (por eso hay un solo juego principal).
