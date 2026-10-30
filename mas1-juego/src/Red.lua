-- RemoteEvents de «+1 de lanzamiento por segundo» en ReplicatedStorage (adaptador de Roblox, no es Lua puro): en el servidor se
-- crean la primera vez que se piden (asi dos scripts no los duplican) y en el cliente se esperan. Nombres en CONTRATO.md.
-- SIN PROBAR EN STUDIO.
local RS, RunService = game:GetService("ReplicatedStorage"), game:GetService("RunService")
local R = {}

function R.evento(nombre)
	local e = RS:FindFirstChild(nombre)
	if e then return e end
	if RunService:IsServer() then
		e = Instance.new("RemoteEvent")
		e.Name = nombre
		e.Parent = RS
		return e
	end
	return RS:WaitForChild(nombre)
end

return R
