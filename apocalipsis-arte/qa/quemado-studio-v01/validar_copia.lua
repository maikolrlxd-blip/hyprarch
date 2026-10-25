-- Offline structure check; does not claim Play.
local root='C:/Users/maiko/slime-rush/hyprarch/'
local qa=root..'apocalipsis-arte/qa/quemado-studio-v01/'
local dm=fs.read('work/luto-fire-engine-qa/LUTO-Quemado-QA-03.rbxl')
local rs=dm:FindFirstChild('ReplicatedStorage')
assert(rs:FindFirstChild('QA_QuemadoFX').Source==fs.read(root..'apocalipsis-arte/armas/lanzallamas-fx-v02/QuemadoFX.lua','txt'))
assert(dm:Descend('ServerScriptService','QA_FuegoServidor').Source==fs.read(qa..'Preparar.server.lua','txt'))
assert(dm:Descend('StarterPlayer','StarterPlayerScripts','QA_FuegoCliente').Source==fs.read(qa..'Prueba.client.lua','txt'))
local active,disabled=0,0
for _,o in ipairs(dm:GetDescendants()) do
    if o.ClassName=='Script' or o.ClassName=='LocalScript' then
        if o.Disabled then disabled=disabled+1 else
            assert(o.Name=='QA_FuegoCliente' or o.Name=='QA_FuegoServidor')
            active=active+1
        end
    end
end
assert(active==2 and disabled==6)
local count={QuemadoInicio=27,QuemadoBucle=37,QuemadoCaer=55}
local sequences=rs:FindFirstChild('QuemadoClips'):GetChildren()
assert(#sequences==3)
for _,seq in ipairs(sequences) do
    assert(seq.ClassName=='KeyframeSequence')
    assert(#seq:GetChildren()==count[seq.Name])
    assert(seq.Loop==(seq.Name=='QuemadoBucle'))
end
local native=fs.read('work/luto-fire-engine-qa/Luto-audit-uncompressed.rbxl')
local original=native:Descend('ServerStorage','LUTO_Plantillas','Zombi_Mujer')
local copy=dm:Descend('ServerStorage','LUTO_Plantillas','Zombi_Mujer')
local meshes=0
for _,p in ipairs(original:GetDescendants()) do
    if p.ClassName=='MeshPart' then
        local c=copy:FindFirstChild(p.Name,true)
        assert(c and c.MeshId==p.MeshId and c.TextureID==p.TextureID and c.Size==p.Size)
        meshes=meshes+1
    end
end
assert(meshes==15)
print('STRUCTURE_PASS scripts=2_active_6_disabled clips=3 keyframes=119 source_match=3 original_meshes=15')
