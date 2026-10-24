-- Generado por tools/build_*.py: no editar a mano.
-- Clips a 60 fps con su duracion exacta y sus eventos (segundos); puntos del arma en studs (ejes Roblox).
return {
	Arma = "Lanzallamas",
	Fps = 60,
	HandleCentroDesdeOrigen = Vector3.new(-0.1187, 0.1387, -1.16),
	Puntos = {
		Boca = {DesdeOrigen = Vector3.new(0.0, 0.32, -2.75), DesdeCentroHandle = Vector3.new(0.1187, 0.1813, -1.59)},
	},
	Clips = {
		Equipar = {Duracion = 0.85, Bucle = false, Hueco = false, Eventos = {{T = 0.56, Nombre = "agarre"}}},
		Guardar = {Duracion = 0.65, Bucle = false, Hueco = false, Eventos = {{T = 0, Nombre = "fuego_apagar"}, {T = 0.6, Nombre = "ocultar_arma"}}},
		Reposo = {Duracion = 2, Bucle = true, Hueco = false, Eventos = {}},
		Disparo = {Duracion = 0.6, Bucle = true, Hueco = false, Eventos = {{T = 0, Nombre = "fuego_sostener"}}},
		Recargar = {Duracion = 2.8, Bucle = false, Hueco = false, Eventos = {{T = 0, Nombre = "fuego_apagar"}, {T = 0.34, Nombre = "cierre_abrir"}, {T = 0.88, Nombre = "cartucho_fuera"}, {T = 1.36, Nombre = "cartucho_nuevo"}, {T = 2.12, Nombre = "cartucho_insertar"}, {T = 2.42, Nombre = "recarga_confirmar"}}},
		Inspeccionar = {Duracion = 3.2, Bucle = false, Hueco = false, Eventos = {{T = 0, Nombre = "fuego_apagar"}}},
	},
}
