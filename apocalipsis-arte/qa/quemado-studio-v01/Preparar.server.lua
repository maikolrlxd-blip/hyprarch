-- Isolated copy only. Existing LUTO meshes, no upload and no combat scripts.
game:GetService('Players').CharacterAutoLoads = false
local storage = game:GetService('ServerStorage')
local rs = game:GetService('ReplicatedStorage')
local source = storage.LUTO_Plantillas
local map = source.Mapa:Clone()
map.Name = 'QA_MapaExistente'
map.Parent = workspace
local template = source.Zombi_Mujer:Clone()
template.Name = 'QA_ZombiOriginal'
template.Parent = rs
print('LUTO_FIRE_QA SERVER_READY existing_meshes=true combat=false')
