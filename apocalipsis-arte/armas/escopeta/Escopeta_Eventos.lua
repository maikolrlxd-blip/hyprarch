-- Generado por tools/build_*.py: no editar a mano.
-- Clips a 60 fps con su duracion exacta y sus eventos (segundos); puntos del arma en studs (ejes Roblox).
return {
	Arma = "Escopeta",
	Fps = 60,
	HandleCentroDesdeOrigen = Vector3.new(0.0, -0.1, -0.7596),
	Puntos = {
		Boca = {DesdeOrigen = Vector3.new(0.0, 0.097, -2.7879), DesdeCentroHandle = Vector3.new(0.0, 0.197, -2.0283)},
		Expulsion = {DesdeOrigen = Vector3.new(0.1103, 0.097, -0.5657), DesdeCentroHandle = Vector3.new(0.1103, 0.197, 0.1939)},
		PuertoCarga = {DesdeOrigen = Vector3.new(0.0, -0.101, -0.7273), DesdeCentroHandle = Vector3.new(0.0, -0.001, 0.0323)},
		MiraTrasera = {DesdeOrigen = Vector3.new(0.0, 0.1818, -0.1818), DesdeCentroHandle = Vector3.new(0.0, 0.2818, 0.5778)},
		MiraDelantera = {DesdeOrigen = Vector3.new(0.0, 0.1919, -2.7273), DesdeCentroHandle = Vector3.new(0.0, 0.2919, -1.9677)},
	},
	Clips = {
		Equipar = {Duracion = 0.9, Bucle = false, Hueco = false, Eventos = {{T = 0.58, Nombre = "bomba_atras"}, {T = 0.77, Nombre = "bomba_adelante"}}},
		Disparo = {Duracion = 0.45, Bucle = false, Hueco = false, Eventos = {{T = 0.0, Nombre = "disparo"}}},
		Bombear = {Duracion = 0.6, Bucle = false, Hueco = false, Eventos = {{T = 0.16, Nombre = "bomba_atras"}, {T = 0.18, Nombre = "casquillo_sale"}, {T = 0.4, Nombre = "bomba_adelante"}}},
		Recargar_Inicio = {Duracion = 0.45, Bucle = false, Hueco = false, Eventos = {}},
		Recargar_Cartucho = {Duracion = 0.5, Bucle = false, Hueco = false, Eventos = {{T = 0.34, Nombre = "cartucho_dentro"}}},
		Recargar_Fin = {Duracion = 0.55, Bucle = false, Hueco = false, Eventos = {{T = 0.28, Nombre = "bomba_atras"}, {T = 0.46, Nombre = "bomba_adelante"}}},
		Recargar = {Duracion = 2.5, Bucle = false, Hueco = false, Eventos = {{T = 0.79, Nombre = "cartucho_dentro"}, {T = 1.29, Nombre = "cartucho_dentro"}, {T = 1.79, Nombre = "cartucho_dentro"}, {T = 2.23, Nombre = "bomba_atras"}, {T = 2.41, Nombre = "bomba_adelante"}}},
		Reposo = {Duracion = 2.0, Bucle = true, Hueco = false, Eventos = {}},
		Inspeccionar = {Duracion = 3.0, Bucle = false, Hueco = false, Eventos = {{T = 0.92, Nombre = "bomba_atras"}, {T = 1.25, Nombre = "bomba_adelante"}}},
	},
}
