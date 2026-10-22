# Encargo de arte — juego "apocalipsis" (nombre provisional), todo en Blender
Pedido de Maikol (2026-10-22). Quien lo ejecuta: la sesión **Coordinador de Codex** (Claude en el PC con Blender 5.2.2). Claude de la nube NO hace modelos. Todo en Blender, nada de Parts/Toolbox/Terrain de fábrica.

## Entregables (en este orden)
1. **Pistola 9 mm** (estilo Glock, nombre genérico "Pistola 9mm")
2. **Escopeta** (de corredera)
3. **Subfusil** (estilo MP5, nombre genérico "Subfusil")
4. **Mujer zombi estilo Roblox** (proporciones tipo R15, fácilmente reconocible como Roblox; piel pálida/verdosa, ropa rota, heridas **estilizadas sin gore**; "claro" = claramente estilo Roblox — confirmar con Maikol si se refería a otra cosa, p. ej. piel/tono claro)
5. **Mapa pequeño apocalíptico** modular (calle en ruinas, 2–3 edificios, coches, barricadas, escombros, vegetación invasora; ≤ 300×300 studs jugables)

## Reglas técnicas (aprendidas en Slime Rush)
- **Escala Roblox:** 1 stud ≈ 0,28 m; una persona R15 mide ~5,2 studs. Revisar al exportar: Studio importó una roca ~100 veces más grande por la escala del FBX; fijar unidades/escala de exportación y comprobar en una copia de Studio.
- Estilo: formas facetadas limpias + texturas **pintadas a mano** (nada de color liso ni "plastilina"), mate, sin brillos. Referencia de aspecto: árboles v04 de Slime Rush.
- Presupuesto: armas 300–800 tris cada una; zombi ≤ 3.000; piezas del mapa ≤ 1.500 cada una (cada MeshPart < 20.000 tris).
- Armas: origen en la empuñadura, ejes de Roblox, partes móviles separadas (corredera, cargador, bomba de la escopeta) + clips opcionales: Reposo, Disparo (retroceso), Recarga.
- Zombi: rig compatible con R15 si es posible (si no, esqueleto simple con nombres claros) + clips Reposo, Caminar, Atacar, Caer.
- Exportar GLB/FBX + .blend + render de comprobación junto a una figura de 6 studs. Autocrítica sin adornos en un ESTADO.md por entrega ("qué falla" primero).
- Carpeta de trabajo: `apocalipsis-arte\` (sesión del PC); commit local pequeño por entrega; el push lo decide Maikol.
- Contenido: todo apto para Roblox (sin gore, armas genéricas, sin marcas ni logos).
