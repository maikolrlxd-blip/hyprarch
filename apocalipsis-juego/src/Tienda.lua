-- Tienda del mapa de Luto: se compra con las monedas de la partida (por zombi). Modulo PURO. Precios PROVISIONALES.
local Tienda = {}

Tienda.ITEMS = {
	municion = { nombre = "Municion (+2 cargadores)", base = 50, crece = 0.04 },
	curar = { nombre = "Curarse del todo", base = 75, crece = 0.05 },
}

-- Precio segun la ronda (sube un poco con el avance).
function Tienda.precio(item, ronda)
	local it = Tienda.ITEMS[item]; if not it then return nil end
	return math.floor(it.base * (1 + it.crece * (ronda - 1)) + 0.5)
end

-- Compra: descuenta las monedas del jugador en la partida y devuelve (true, item) o (false, motivo).
function Tienda.comprar(partida, id, item, ronda)
	local precio = Tienda.precio(item, ronda); if not precio then return false, "articulo desconocido" end
	if partida.estado == "fin" or partida.estado == "esperando" then return false, "ahora no se puede comprar" end
	if not partida:gastar(id, precio) then return false, "monedas insuficientes (" .. precio .. ")" end
	return true, { item = item, precio = precio }
end

return Tienda
