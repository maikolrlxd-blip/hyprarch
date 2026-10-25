-- LUTO: solo presentacion local. No aplica dano, remotos, monedas ni estado de combate.
-- Revision visual v02: emisores en la superficie del rig y fuego legible.
local RunService = game:GetService("RunService")
local FX = {}
local active = setmetatable({}, {__mode = "k"})

local function emitter(parent, stream)
    local p = Instance.new("ParticleEmitter")
    p.Name = "LutoQuemadoVisual"
    p.Texture = "rbxasset://textures/particles/fire_main.dds"
    p.Color = ColorSequence.new({
        ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 222, 135)),
        ColorSequenceKeypoint.new(0.35, Color3.fromRGB(237, 117, 46)),
        ColorSequenceKeypoint.new(1, Color3.fromRGB(81, 50, 44)),
    })
    p.Transparency = NumberSequence.new({
        NumberSequenceKeypoint.new(0, 0.05), NumberSequenceKeypoint.new(0.65, 0.2),
        NumberSequenceKeypoint.new(1, 1),
    })
    p.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, stream and 0.45 or 1.0),
        NumberSequenceKeypoint.new(0.5, stream and 1.5 or 1.8), NumberSequenceKeypoint.new(1, 0.25)})
    p.Brightness = 3
    p.LightEmission = 1
    p.LightInfluence = 0
    p.Lifetime = stream and NumberRange.new(0.35, 0.55) or NumberRange.new(0.4, 0.7)
    p.Speed = stream and NumberRange.new(22, 26) or NumberRange.new(1.8, 3.5)
    p.SpreadAngle = stream and Vector2.new(7, 7) or Vector2.new(25, 25)
    p.Acceleration = Vector3.new(0, stream and 1 or 4, 0)
    p.EmissionDirection = stream and Enum.NormalId.Front or Enum.NormalId.Top
    p.Rate = stream and 60 or 18
    p.Enabled = false
    p.Parent = parent
    return p
end

function FX.Muzzle(attachment)
    assert(attachment and attachment:IsA("Attachment"), "Muzzle requiere un Attachment orientado al frente")
    local fire = emitter(attachment, true)
    local light = Instance.new("PointLight")
    light.Name = "LutoMuzzleLuz"; light.Color = Color3.fromRGB(255, 161, 73)
    light.Range = 9; light.Brightness = 0; light.Shadows = false; light.Parent = attachment
    local dead = false
    return {
        SetActive = function(on)
            if dead then return end
            fire.Enabled = on == true
            light.Brightness = on == true and 1.5 or 0
        end,
        Destroy = function()
            if dead then return end
            dead = true; fire:Destroy(); light:Destroy()
        end,
    }
end

function FX.StopBurn(model)
    local state = active[model]
    if not state then return end
    active[model] = nil
    if state.connection then state.connection:Disconnect() end
    for _, inst in ipairs(state.instances) do inst:Destroy() end
end

function FX.Burn(model, seconds)
    if not model or not model:IsA("Model") or not model.Parent then return false end
    local duration = tonumber(seconds) or 2.8
    if duration ~= duration then duration = 2.8 end
    duration = math.clamp(duration, 0.1, 8)
    local state = active[model]
    if state then state.untilTime = os.clock() + duration; return true end
    local instances = {}
    for _, name in ipairs({"UpperTorso", "LowerTorso", "LeftUpperArm"}) do
        local part = model:FindFirstChild(name, true)
        if part and part:IsA("BasePart") then
            local at = Instance.new("Attachment"); at.Name = "LutoQuemadoAttachment"; at.Parent = part
            local root = model:FindFirstChild("HumanoidRootPart")
            local front = root and root:IsA("BasePart") and root.CFrame.LookVector or part.CFrame.LookVector
            -- Place on the body surface instead of burying the emitter inside the mesh.
            at.CFrame = part.CFrame:ToObjectSpace(CFrame.new(part.Position + front * (part.Size.Z * 0.5 + 0.08)))
            local fire = emitter(at, false); fire.Enabled = true
            if name == "UpperTorso" then
                local glow = Instance.new("PointLight"); glow.Name = "LutoQuemadoLuz"
                glow.Color = Color3.fromRGB(255, 136, 52); glow.Range = 6
                glow.Brightness = 0.6; glow.Shadows = false; glow.Parent = at
            end
            table.insert(instances, at)
        end
    end
    if #instances == 0 then return false end
    state = {instances = instances, untilTime = os.clock() + duration}
    active[model] = state
    state.connection = RunService.Heartbeat:Connect(function()
        if not model.Parent or os.clock() >= state.untilTime then FX.StopBurn(model) end
    end)
    return true
end

function FX.Destroy()
    local models = {}
    for model in pairs(active) do table.insert(models, model) end
    for _, model in ipairs(models) do FX.StopBurn(model) end
end
return FX
