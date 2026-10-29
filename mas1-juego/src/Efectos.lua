-- Efectos visuales de «+1 de lanzamiento por segundo»: especificaciones de ParticleEmitter (datos puros, sin API de Roblox) para
-- lanzamiento, estela de vuelo, aleteo, recoger aro, golpe, rebirth y fuego del fenix. Valores PROVISIONALES: se ajustan viendolos.
-- Colores vivos (estilo Steal a Brainrot). Cada efecto: count (rafaga) o rate (continuo), vida, velocidad, tamano, colores, aceleracion.
local E = {}

E.TIPOS = {
	lanzamiento = { count = 60, life = { 0.5, 1.0 }, speed = { 25, 55 }, size = { 2.5, 0 }, spread = 180, accel = { 0, -30, 0 }, colors = { "#fff3b0", "#ffb347", "#ff5d8f" }, light = 0.4 },
	estela = { rate = 40, life = { 0.5, 0.9 }, speed = { 0, 2 }, size = { 1.6, 0 }, spread = 20, accel = { 0, 0, 0 }, colors = { "#ffffff", "#bdeaff" }, light = 0.3 },
	aleteo = { count = 8, life = { 0.4, 0.7 }, speed = { 4, 9 }, size = { 0.9, 0 }, spread = 60, accel = { 0, -8, 0 }, colors = { "#ffffff", "#d8f1ff" }, light = 0.2 },
	aro = { count = 36, life = { 0.5, 0.9 }, speed = { 14, 28 }, size = { 1.6, 0 }, spread = 180, accel = { 0, -4, 0 }, colors = { "#ffd23f", "#fff7e0", "#3ddc97" }, light = 0.6 },
	golpe = { count = 14, life = { 0.25, 0.45 }, speed = { 12, 22 }, size = { 1.4, 0 }, spread = 180, accel = { 0, 0, 0 }, colors = { "#ffffff", "#ff5d8f" }, light = 0.5 },
	rebirth = { count = 120, life = { 0.8, 1.6 }, speed = { 10, 30 }, size = { 3, 0 }, spread = 180, accel = { 0, 6, 0 }, colors = { "#7c5cff", "#3ddc97", "#ffd23f" }, light = 0.7 },
	fuego_fenix = { rate = 70, life = { 0.4, 0.8 }, speed = { 3, 8 }, size = { 2.2, 0 }, spread = 25, accel = { 0, 10, 0 }, colors = { "#fff3b0", "#ff9d00", "#ff3d00" }, light = 0.8 },
}

-- Orden fijo para las pruebas (sin depender de pairs)
E.ORDEN = { "lanzamiento", "estela", "aleteo", "aro", "golpe", "rebirth", "fuego_fenix" }

return E
