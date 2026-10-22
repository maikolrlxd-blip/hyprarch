# Sensación de juego (animación, efectos, sonido, impactos) — Slime Rush v2
Regla: cada acción importante lleva **anticipación → impacto → reacción**, con sonido y efecto en el mismo instante. Para la prueba jugable solo lo de la columna "P" (provisional, simple); el resto después.

| Acción | Animación | Efecto | Sonido | Impacto (juego) | P |
|---|---|---|---|---|---|
| Bongo: puñetazo | enrollar brazo → disparo | estela + onda al golpear | boing + golpe sordo | cámara tiembla, empuje, pausa de 0,05 s | ✔ |
| Bongo: rebote | giro del slime | chispas de gel en cada rebote | boing cada rebote | daño por golpe | |
| Rayo: montar/embestir | agacharse → salir | polvo/estela, líneas de velocidad | zumbido creciente, choque | arrastre y choque con aturdimiento | ✔ |
| Miga: lanzar partes | estirar y soltar | gotas de gel, partes regeneran con brillo | pop suave | contador de partes en el HUD | ✔ |
| Recibir golpe | encogerse | salpicón de gel (no sangre) | chof | parpadeo, retroceso | ✔ |
| Quedar inconsciente | desinflarse | charco de gel | suspiro largo | cuenta atrás visible | ✔ |
| Saquear / recoger / cofre | brazos al objeto | destellos, número flotante | clic de moneda / tapa | puntos suben | ✔ |
| Bote llegando | Atracar (ya existe) | espuma | motor + olas | — | |
| Volcán / lava / tornado / terremoto | por clip | humo, brasas, polvo | rugido grave | temblor de cámara | después |
| Colapso (se derrite) | derretirse | goteo | burbujeo | pantalla de fin | |
| HUD y menús | rebote suave | brillo | clics limpios | — | ✔ básico |

## Cómo se producen (sin tocar el arte principal)
- **Sonidos:** generados por código (Python/numpy → WAV: sintetizados, ruido filtrado, envolventes) y mezclados; cortos, limpios, sin chirridos (Maikol lo pidió). Luego revisar con oído de Maikol.
- **Efectos:** ParticleEmitter/Beam de Roblox con parámetros propios + sprites hechos por código; Codex los conecta.
- **Impactos:** reglas de "sensación" (hit-stop, temblor, retroceso) en Luau; valores en un solo módulo para ajustar rápido.
- **Animaciones de slime:** las hace quien modele a los slimes (Codex/Antigravity/otra sesión); Claude de la nube no hace modelos.
Prioridad: P primero, medir si la prueba jugable "se siente bien", luego el resto.
