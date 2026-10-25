-- rbxmk run from workspace; never writes the user's native place.
local repo='C:/Users/maiko/slime-rush/hyprarch/'
local qa=repo..'apocalipsis-arte/qa/quemado-studio-v01/'
local dm=fs.read('work/luto-fire-engine-qa/Luto-audit-uncompressed.rbxl')
local disabled=0
for _,o in ipairs(dm:GetDescendants()) do
    if o.ClassName=='Script' or o.ClassName=='LocalScript' then o.Disabled=true;disabled=disabled+1 end
end
local rs=dm:FindFirstChild('ReplicatedStorage')
local module=Instance.new('ModuleScript');module.Name='QA_QuemadoFX';module.Source=fs.read(repo..'apocalipsis-arte/armas/lanzallamas-fx-v02/QuemadoFX.lua','txt');module.Parent=rs
local clips=fs.read(qa..'datos/Quemado-local.rbxmx');clips:GetChildren()[1].Parent=rs
local server=Instance.new('Script');server.Name='QA_FuegoServidor';server.Source=fs.read(qa..'Preparar.server.lua','txt');server.Parent=dm:FindFirstChild('ServerScriptService')
local client=Instance.new('LocalScript');client.Name='QA_FuegoCliente';client.Source=fs.read(qa..'Prueba.client.lua','txt');client.Parent=dm:Descend('StarterPlayer','StarterPlayerScripts')
fs.write('work/luto-fire-engine-qa/LUTO-Quemado-QA-03.rbxl',dm)
print('QA built; original scripts disabled only in copy',disabled)
