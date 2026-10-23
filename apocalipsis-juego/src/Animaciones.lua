-- Identificadores de animaciones publicadas en Roblox (cuenta de Maikol, fuera de venta). Con id "" el juego funciona igual
-- (los zombis se deslizan y las armas no animan). Rellenar con "rbxassetid://NUMERO".
-- Zombi y jefes: publicados el 2026-10-23 desde las KeyframeSequence de apocalipsis-arte/*/integracion/Animaciones_*.rbxmx
-- (tools/exportar_animaciones_roblox.py); comprobados en Studio contra las secuencias locales (claves y poses).
local A = {}

A.zombi = {
	Reposo = "rbxassetid://117323418394221",
	Caminar = "rbxassetid://128425423837041",
	Atacar = "rbxassetid://81918422160520",
	Caer = "rbxassetid://131892149953171",
}
A.jefe_lamentadora = {
	Reposo = "rbxassetid://90599448240055",
	Caminar = "rbxassetid://78378171595825",
	Atacar = "rbxassetid://117438706829596",
	Caer = "rbxassetid://117668623351499",
}
A.jefe_alta = {
	Reposo = "rbxassetid://73495974087699",
	Caminar = "rbxassetid://110159877146850",
	Atacar = "rbxassetid://139329540979905",
	Caer = "rbxassetid://124895291095508",
}

-- Armas (para cuando se cuelguen como Tool): clips del mundo y del viewmodel
A.pistola = { Equipar = "", Disparo = "", Recargar = "", Reposo = "", Inspeccionar = "" }
A.escopeta = { Equipar = "", Disparo = "", Bombear = "", Recargar_Inicio = "", Recargar_Cartucho = "", Recargar_Fin = "", Reposo = "", Inspeccionar = "" }
A.subfusil = { Equipar = "", Disparo = "", Recargar = "", Amartillar = "", Reposo = "", Inspeccionar = "" }

return A
