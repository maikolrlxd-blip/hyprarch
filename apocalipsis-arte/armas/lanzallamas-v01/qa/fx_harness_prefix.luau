-- Mock limitado de ciclo de vida: no renderiza ni emula la fisica de Roblox.
local now = 0
local os = {clock = function() return now end}
local signals = {}
local heartbeat = {}
function heartbeat:Connect(fn)
    local c = {live = true, fn = fn}
    function c:Disconnect() self.live = false end
    table.insert(signals, c)
    return c
end
local function pulse(t)
    now = t
    for _, c in ipairs(table.clone(signals)) do if c.live then c.fn() end end
end
local game = {GetService = function(_, name) assert(name == 'RunService'); return {Heartbeat = heartbeat} end}
local function constructor(...)
    return {...}
end
local ColorSequence = {new = constructor}
local ColorSequenceKeypoint = {new = constructor}
local Color3 = {fromRGB = constructor}
local NumberSequence = {new = constructor}
local NumberSequenceKeypoint = {new = constructor}
local NumberRange = {new = constructor}
local Vector2 = {new = constructor}
local Vector3 = {new = constructor}
local Enum = {NormalId = {Front = 'Front', Top = 'Top'}}
local methods = {}
local Instance = {}
function Instance.new(class)
    local data = {ClassName = class, Name = class, children = {}}
    local proxy = {}
    return setmetatable(proxy, {
        __index = function(_, key) return methods[key] or data[key] end,
        __newindex = function(_, key, value)
            if key == 'Parent' and data.Parent ~= value then
                if data.Parent then
                    local index = table.find(data.Parent.children, proxy)
                    if index then table.remove(data.Parent.children, index) end
                end
                if value then table.insert(value.children, proxy) end
            end
            data[key] = value
        end,
    })
end
function methods:IsA(class)
    return self.ClassName == class or (class == 'BasePart' and self.ClassName == 'Part')
end
function methods:FindFirstChild(name, recursive)
    for _, c in ipairs(self.children) do
        if c.Name == name then return c end
        if recursive then local found = c:FindFirstChild(name, true); if found then return found end end
    end
end
function methods:Destroy()
    if self.destroyed then return end
    self.destroyed = true
    for _, c in ipairs(table.clone(self.children)) do c:Destroy() end
    self.Parent = nil
end
local function count(object, class)
    local n = 0
    for _, c in ipairs(object.children) do n += c:IsA(class) and 1 or 0; n += count(c, class) end
    return n
end
local scene = Instance.new('Folder')
local function zombie(names)
    local model = Instance.new('Model'); model.Parent = scene
    for _, name in ipairs(names or {'UpperTorso','LowerTorso','LeftUpperArm'}) do
        local p = Instance.new('Part'); p.Name = name; p.Parent = model
    end
    return model
end
local FX = (function()
