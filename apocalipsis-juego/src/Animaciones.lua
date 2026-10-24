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

-- Armas: clips del viewmodel de primera persona (plantillas ReplicatedStorage.LUTO_VM). Publicados el 2026-10-23 desde
-- apocalipsis-arte/armas/<arma>/integracion/Animaciones_VM_<arma>.rbxmx (tools/exportar_viewmodel_roblox.py); los 19
-- comprobados en Studio contra las secuencias locales (claves y poses).
A.pistola = {
	Equipar = "rbxassetid://129870583652847",
	Disparo = "rbxassetid://85279522252663",
	Recargar = "rbxassetid://108148379809721",
	Reposo = "rbxassetid://124440958646390",
	Inspeccionar = "rbxassetid://87199766701294",
}
A.escopeta = {
	Equipar = "rbxassetid://99583907030660",
	Disparo = "rbxassetid://135578119667473",
	Bombear = "rbxassetid://134334099356367",
	Recargar_Inicio = "rbxassetid://128134985479278",
	Recargar_Cartucho = "rbxassetid://104910286100215",
	Recargar_Fin = "rbxassetid://107981003735021",
	Reposo = "rbxassetid://82737557713588",
	Inspeccionar = "rbxassetid://105619437087417",
}
A.subfusil = {
	Equipar = "rbxassetid://130294549646215",
	Disparo = "rbxassetid://94339497096074",
	Recargar = "rbxassetid://93791845167918",
	Amartillar = "rbxassetid://118133406020880",
	Reposo = "rbxassetid://116267547833340",
	Inspeccionar = "rbxassetid://109034628894916",
}

return A
