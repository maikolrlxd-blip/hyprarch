-- Identificadores de animaciones publicadas en Roblox (Animation Editor, cuenta de Maikol). VACIOS hasta que se publiquen:
-- con id "" el juego funciona igual (los zombis se deslizan y las armas no animan). Rellenar con "rbxassetid://NUMERO".
local A = {}

A.zombi = { Reposo = "", Caminar = "", Atacar = "", Caer = "" }
A.jefe_lamentadora = { Reposo = "", Caminar = "", Atacar = "", Caer = "" }
A.jefe_alta = { Reposo = "", Caminar = "", Atacar = "", Caer = "" }

-- Armas (para cuando se cuelguen como Tool): clips del mundo y del viewmodel
A.pistola = { Equipar = "", Disparo = "", Recargar = "", Reposo = "", Inspeccionar = "" }
A.escopeta = { Equipar = "", Disparo = "", Bombear = "", Recargar_Inicio = "", Recargar_Cartucho = "", Recargar_Fin = "", Reposo = "", Inspeccionar = "" }
A.subfusil = { Equipar = "", Disparo = "", Recargar = "", Amartillar = "", Reposo = "", Inspeccionar = "" }

return A
