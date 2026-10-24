-- Generado por tools/build_*.py: no editar a mano.
-- Clips a 60 fps con su duracion exacta y sus eventos (segundos); puntos del arma en studs (ejes Roblox).
return {
	Arma = "Pistola9mm",
	Fps = 60,
	HandleCentroDesdeOrigen = Vector3.new(-0.0004, -0.1024, -0.4488),
	Puntos = {
		Boca = {DesdeOrigen = Vector3.new(0.0, 0.3952, -1.35), DesdeCentroHandle = Vector3.new(0.0004, 0.4976, -0.9012)},
		Expulsion = {DesdeOrigen = Vector3.new(0.1028, 0.4355, -0.3016), DesdeCentroHandle = Vector3.new(0.1032, 0.5379, 0.1472)},
		MiraTrasera = {DesdeOrigen = Vector3.new(0.0, 0.5645, 0.0492), DesdeCentroHandle = Vector3.new(0.0004, 0.6669, 0.498)},
		MiraDelantera = {DesdeOrigen = Vector3.new(0.0, 0.5629, -1.2532), DesdeCentroHandle = Vector3.new(0.0004, 0.6653, -0.8044)},
	},
	Clips = {
		Equipar = {Duracion = 0.8, Bucle = false, Hueco = false, Eventos = {{T = 0.48, Nombre = "corredera_atras"}, {T = 0.53, Nombre = "corredera_adelante"}}},
		Disparo = {Duracion = 0.25, Bucle = false, Hueco = false, Eventos = {{T = 0.0, Nombre = "disparo"}, {T = 0.033, Nombre = "corredera_atras"}, {T = 0.05, Nombre = "casquillo_sale"}, {T = 0.11, Nombre = "corredera_adelante"}}},
		Recargar = {Duracion = 1.7, Bucle = false, Hueco = false, Eventos = {{T = 0.22, Nombre = "cargador_suelta"}, {T = 0.32, Nombre = "cargador_fuera"}, {T = 0.56, Nombre = "cargador_nuevo"}, {T = 1.04, Nombre = "cargador_dentro"}, {T = 1.18, Nombre = "corredera_atras"}, {T = 1.24, Nombre = "corredera_adelante"}}},
		Reposo = {Duracion = 2.0, Bucle = true, Hueco = false, Eventos = {}},
		Inspeccionar = {Duracion = 3.3, Bucle = false, Hueco = false, Eventos = {}},
	},
}
