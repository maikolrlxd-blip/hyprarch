-- Generado por tools/build_*.py: no editar a mano.
-- Clips a 60 fps con su duracion exacta y sus eventos (segundos); puntos del arma en studs (ejes Roblox).
return {
	Arma = "Subfusil",
	Fps = 60,
	HandleCentroDesdeOrigen = Vector3.new(0.0, 0.2142, -0.3012),
	Puntos = {
		Boca = {DesdeOrigen = Vector3.new(0.0, 0.4372, -1.7846), DesdeCentroHandle = Vector3.new(0.0, 0.2231, -1.4835)},
		Expulsion = {DesdeOrigen = Vector3.new(0.1383, 0.4863, -0.4595), DesdeCentroHandle = Vector3.new(0.1383, 0.2722, -0.1584)},
		MiraTrasera = {DesdeOrigen = Vector3.new(0.0, 0.6335, 0.2052), DesdeCentroHandle = Vector3.new(0.0, 0.4194, 0.5064)},
		MiraDelantera = {DesdeOrigen = Vector3.new(0.0, 0.6135, -1.6195), DesdeCentroHandle = Vector3.new(0.0, 0.3993, -1.3184)},
	},
	Clips = {
		Equipar = {Duracion = 0.8, Bucle = false, Hueco = false, Eventos = {{T = 0.52, Nombre = "palanca_atras"}, {T = 0.59, Nombre = "palanca_suelta"}}},
		Disparo = {Duracion = 0.16, Bucle = false, Hueco = false, Eventos = {{T = 0.0, Nombre = "disparo"}, {T = 0.02, Nombre = "casquillo_sale"}}},
		Recargar = {Duracion = 1.95, Bucle = false, Hueco = false, Eventos = {{T = 0.3, Nombre = "cargador_suelta"}, {T = 0.36, Nombre = "cargador_fuera"}, {T = 0.84, Nombre = "cargador_nuevo"}, {T = 1.16, Nombre = "cargador_dentro"}, {T = 1.44, Nombre = "palanca_atras"}, {T = 1.51, Nombre = "palanca_suelta"}}},
		Amartillar = {Duracion = 0.4, Bucle = false, Hueco = false, Eventos = {{T = 0.1, Nombre = "palanca_atras"}, {T = 0.17, Nombre = "palanca_suelta"}}},
		Reposo = {Duracion = 2.0, Bucle = true, Hueco = false, Eventos = {}},
		Inspeccionar = {Duracion = 3.0, Bucle = false, Hueco = false, Eventos = {{T = 0.72, Nombre = "cargador_fuera"}, {T = 1.2, Nombre = "cargador_dentro"}}},
	},
}
