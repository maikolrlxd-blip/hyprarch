-- Isolated motor/ParticleEmitter preview. Not AI, combat, replication or mobile QA.
local RS = game:GetService('ReplicatedStorage')
local Run = game:GetService('RunService')
local Http = game:GetService('HttpService')
local player = game:GetService('Players').LocalPlayer
local FX = require(RS:WaitForChild('QA_QuemadoFX'))
local folder = RS:WaitForChild('QuemadoClips')
local template = RS:WaitForChild('QA_ZombiOriginal')
local camera = workspace.CurrentCamera
camera.CameraType = Enum.CameraType.Scriptable
camera.CFrame = CFrame.lookAt(Vector3.new(7,4.5,-14), Vector3.new(0,2.6,0))
camera.FieldOfView = 48
local models, animators, tracks = {}, {}, {}
local function log(name, data)
    print('LUTO_FIRE_QA '..name..' '..Http:JSONEncode(data or {}))
end
local function count(model, class)
    local n=0
    for _,o in model:GetDescendants() do if o:IsA(class) then n+=1 end end
    return n
end
local gui=Instance.new('ScreenGui');gui.Name='QA_Quemado';gui.IgnoreGuiInset=false;gui.ResetOnSpawn=false;gui.Parent=player.PlayerGui
pcall(function() game:GetService('StarterGui'):SetCoreGuiEnabled(Enum.CoreGuiType.PlayerList,false) end)
local panel=Instance.new('Frame');panel.Size=UDim2.new(1,-32,0,62);panel.Position=UDim2.fromOffset(16,4);panel.BackgroundColor3=Color3.fromRGB(18,22,25);panel.BackgroundTransparency=.12;panel.Parent=gui
local title=Instance.new('TextLabel');title.Size=UDim2.new(1,-24,0,32);title.Position=UDim2.fromOffset(12,4);title.BackgroundTransparency=1;title.Text='LUTO / QUEMADO — PRUEBA LOCAL';title.Font=Enum.Font.GothamBold;title.TextSize=21;title.TextColor3=Color3.fromRGB(237,219,189);title.TextXAlignment=Enum.TextXAlignment.Left;title.Parent=panel
local status=title:Clone();status.Position=UDim2.fromOffset(12,33);status.Size=UDim2.new(1,-24,0,25);status.Font=Enum.Font.Gotham;status.TextSize=13;status.TextWrapped=true;status.Text='Preparando tres clips locales y comprobaciones...';status.Parent=panel
for i=1,3 do
    local model=template:Clone();model.Name='QA_Zombi_'..i
    for _,o in model:GetDescendants() do
        if o:IsA('BasePart') then o.CanCollide=false;o.Anchored=false end
        if o:IsA('BaseScript') then o.Enabled=false end
    end
    local root=model.HumanoidRootPart;root.Anchored=true
    local hum=model:FindFirstChildOfClass('Humanoid');hum.AutoRotate=false;hum.BreakJointsOnDeath=false;hum.DisplayDistanceType=Enum.HumanoidDisplayDistanceType.None
    local minY=math.huge
    for _,o in model:GetDescendants() do
        if o:IsA('MeshPart') then minY=math.min(minY,o.Position.Y-o.Size.Y/2) end
    end
    local x=(i-2)*3.8
    local params=RaycastParams.new();params.FilterType=Enum.RaycastFilterType.Include;params.FilterDescendantsInstances={workspace:WaitForChild('QA_MapaExistente')}
    local ground=workspace:Raycast(Vector3.new(x,10,0),Vector3.new(0,-30,0),params)
    assert(ground,'QA needs existing ground')
    local target=Vector3.new(x,root.Position.Y-minY+ground.Position.Y+.025,0)
    log('GROUND',{index=i,y=ground.Position.Y,part=ground.Instance.Name})
    model:PivotTo(model:GetPivot()+target-root.Position)
    model.Parent=workspace
    models[i]=model
    animators[i]=Instance.new('Animator');animators[i].Parent=hum
    tracks[i]={}
end
local assets={}
for _,seq in folder:GetChildren() do
    local id=game:GetService('KeyframeSequenceProvider'):RegisterKeyframeSequence(seq)
    local a=Instance.new('Animation');a.Name=seq.Name;a.AnimationId=id;assets[seq.Name]=a
    for i,animator in animators do
        local t=animator:LoadAnimation(a);t.Priority=Enum.AnimationPriority.Action2;t.Looped=seq.Loop
        tracks[i][seq.Name]=t
    end
end
local function play(i,name,hold)
    for key,t in tracks[i] do if key~=name then t:Stop(0) end end
    local t=tracks[i][name];t:Play(0,1,1)
    t.TimePosition=hold or 0
    if hold then
        t:AdjustSpeed(0)
    end
    return t
end
local emitter=Instance.new('Attachment');emitter.Name='QA_MuzzleSinArma';emitter.CFrame=CFrame.lookAt(Vector3.new(2.8,1.7,-7),Vector3.new(0,2.5,0));emitter.Parent=workspace.Terrain
local muzzle=FX.Muzzle(emitter)
local failures=0
local function check(name,fn)
    local ok,result=pcall(fn)
    if not ok then failures+=1 end
    log(name,{pass=ok,detail=ok and result or tostring(result)})
end
task.wait(2)
check('clip_load_and_motion',function()
    local result={}
    for _,name in {'QuemadoInicio','QuemadoBucle','QuemadoCaer'} do
        local t=play(1,name)
        task.wait(.3)
        assert(t.Length>0,'clip length is zero: '..name)
        local moved=0
        for _,o in models[1]:GetDescendants() do
            if o:IsA('Motor6D') then
                local _,angle=o.Transform:ToAxisAngle()
                if math.abs(angle)>.01 or o.Transform.Position.Magnitude>.01 then moved+=1 end
            end
        end
        assert(moved>=4,'not enough moving joints: '..name)
        result[name]={length=t.Length,movingJoints=moved}
    end
    return result
end)
check('burn_refresh_no_stack',function()
    local m=models[1];assert(FX.Burn(m,.3));local first=m.UpperTorso:FindFirstChild('LutoQuemadoAttachment');assert(count(m,'ParticleEmitter')==3)
    task.wait(.12);assert(FX.Burn(m,.6));task.wait(.3)
    assert(first==m.UpperTorso:FindFirstChild('LutoQuemadoAttachment'),'refresh replaced attachment')
    assert(count(m,'ParticleEmitter')==3)
    task.wait(.4);assert(count(m,'ParticleEmitter')==0,'expired burn retained emitters')
    return 'three emitters, same attachments, expiry clean'
end)
check('stop_and_destroy',function()
    FX.Burn(models[1],8);FX.Burn(models[2],8);FX.StopBurn(models[1]);assert(count(models[1],'ParticleEmitter')==0)
    FX.Destroy();assert(count(models[2],'ParticleEmitter')==0)
    return 'all burn attachments cleaned'
end)
check('removed_model_cleanup',function()
    local m=template:Clone();m.Parent=workspace;FX.Burn(m,8);m.Parent=nil;task.wait(.1)
    assert(count(m,'ParticleEmitter')==0);m:Destroy();return 'detached model cleaned'
end)
check('muzzle_toggle_cleanup',function()
    muzzle.SetActive(true);assert(emitter.LutoQuemadoVisual.Enabled);assert(emitter.LutoMuzzleLuz.Brightness>0)
    muzzle.SetActive(false);assert(not emitter.LutoQuemadoVisual.Enabled)
    muzzle.Destroy();muzzle.Destroy();assert(#emitter:GetChildren()==0)
    muzzle=FX.Muzzle(emitter);return 'toggle and repeated Destroy passed'
end)
check('fall_root_translation',function()
    play(3,'QuemadoCaer',1.76);Run.RenderStepped:Wait();Run.RenderStepped:Wait()
    local rootJoint=models[3].LowerTorso:FindFirstChild('Root')
    assert(rootJoint.Transform.Position.Y < -1.5,'root lowering lost')
    local value=rootJoint.Transform.Position.Y
    log('FALL_POSITION',{loweringY=value,headY=models[3].Head.Position.Y,rootY=models[3].HumanoidRootPart.Position.Y})
    return value
end)
local function measure(seconds)
    local dtValues={};local started=os.clock()
    while os.clock()-started<seconds do table.insert(dtValues,Run.RenderStepped:Wait()) end
    local sum=0;for _,d in dtValues do sum+=d end;table.sort(dtValues)
    return {frames=#dtValues,seconds=sum,meanFPS=#dtValues/sum,p95FrameMs=dtValues[math.ceil(#dtValues*.95)]*1000,viewport={camera.ViewportSize.X,camera.ViewportSize.Y}}
end
for i=1,3 do play(i,'QuemadoBucle') end
status.Text='Midiendo: 3 zombis animadas, fuego apagado (5 s)...'
local baseline=measure(5)
for _,m in models do FX.Burn(m,8) end
status.Text='Midiendo: las mismas 3 zombis, fuego encendido (5 s)...'
local burning=measure(5)
log('PERFORMANCE',{baseline=baseline,burning=burning,npc=3,clients=1,combat=false})
FX.Destroy()
play(1,'QuemadoInicio',.45);play(2,'QuemadoBucle');play(3,'QuemadoCaer',1.76)
status.Text=string.format('Inicio / Bucle / Caída · %d fallos QA · %.1f FPS con 3 zombis · Sin IA ni daño',failures,burning.meanFPS)
local labels={'INICIO','BUCLE','CAÍDA'}
for i=1,3 do
    local b=Instance.new('TextButton');b.Size=UDim2.fromOffset(154,40);b.Position=UDim2.new(.5,(i-2)*166-77,1,-58);b.BackgroundColor3=Color3.fromRGB(51,46,41);b.TextColor3=Color3.fromRGB(255,235,200);b.TextSize=15;b.Font=Enum.Font.GothamBold;b.Text=labels[i];b.Parent=gui
    b.Activated:Connect(function()
        log('UI_CLICK',{button=labels[i]})
        local name=({'QuemadoInicio','QuemadoBucle','QuemadoCaer'})[i]
        local t=play(i,name);FX.Burn(models[i],8)
        -- QA pose hold only: do not race automatic track stop at low FPS.
        -- Loop temporarily, then seek to the last authored pose and freeze.
        if i~=2 then
            t.Looped=true
            task.delay(t.Length,function()
                t.TimePosition=t.Length-.02;t:AdjustSpeed(0)
                log('UI_HOLD',{clip=name,time=t.TimePosition,playing=t.IsPlaying,rootY=models[i].LowerTorso.Root.Transform.Position.Y})
            end)
        end
    end)
end
log('COMPLETE',{failures=failures,localPreview=true})
local jet=Instance.new('TextButton');jet.Size=UDim2.fromOffset(176,32);jet.Position=UDim2.fromOffset(24,74);jet.BackgroundColor3=Color3.fromRGB(51,46,41);jet.TextColor3=Color3.fromRGB(255,235,200);jet.TextSize=13;jet.Text='CHORRO VFX (sin arma)';jet.Parent=gui
local jetOn=false
jet.Activated:Connect(function() jetOn=not jetOn;muzzle.SetActive(jetOn);log('UI_MUZZLE',{active=jetOn}) end)
while gui.Parent do FX.Burn(models[2],8);task.wait(5) end
