"""Build The Grave Yard using GRAB Tools format 25 and native GASM."""
import json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
import grab_pb2 as pb
from google.protobuf.json_format import ParseDict
V=lambda x=0,y=0,z=0:dict(x=x,y=y,z=z)
Q=lambda yaw=0:dict(x=0,y=math.sin(math.radians(yaw/2)),z=0,w=math.cos(math.radians(yaw/2)))
C=lambda r,g,b,a=1:dict(r=r,g=g,b=b,a=a)
N=[]; names={}; scripts={}; manifest={'status':'experimental-native-build','formatVersion':25,'targetPlayers':10,'revision':'grave-yard-1','monsterSpeed':4.1}
def add(name,kind,data):
    node={kind:data,'activeAnimation':-1};N.append(node); names[name]=node;return name
def box(name,p,s,c,**kw):
    return add(name,'levelNodeStatic',dict(shape=1000,material=8,position=V(*p),scale=V(*s),rotation=Q(),color1=C(*c),**kw))
def group(name,p,children=[]):return add(name,'levelNodeGroup',dict(name=name,position=V(*p),scale=V(1,1,1),rotation=Q(),childNodes=children))
def part(p,s,c,**kw):return {'levelNodeStatic':dict(shape=1000,material=8,position=V(*p),scale=V(*s),rotation=Q(),color1=C(*c),**kw),'activeAnimation':-1}
def sign(name,text,p,scale=.4,yaw=0,c=(.8,.9,.9)):
    return add(name,'levelNodeSign',dict(position=V(*p),rotation=Q(yaw),text=text,scale=scale,color=C(*c),hideModel=True,isNeon=True))
def trigger(name,p,s=(.3,.3,.3)):
    return add(name,'levelNodeTrigger',dict(shape=1000,position=V(*p),scale=V(*s),rotation=Q(),isShared=True,triggerSources=[{'triggerSourceBasic':{'type':0}}],triggerTargets=[]))
def state(name):return group(name,(0,0,0)) # empty groups, no visible or collidable geometry
def animation(name,title,position=(0,0,0),yaw=0,duration=.65):
    names[name]['animations']=[dict(name=title,frames=[dict(time=0,position=V(),rotation=Q()),dict(time=duration,position=V(*position),rotation=Q(yaw))],direction=0,speed=1,interpolation=0)]
def attach(parent,child,position):
    node=names[child];N.remove(node)
    node[next(k for k in node if k.startswith('levelNode'))]['position']=V(*position)
    names[parent]['levelNodeGroup']['childNodes'].append(node)

MAP={'SET':1,'ADD':3,'SUB':4,'MUL':5,'DIV':6,'EQUAL':7,'LESS':8,'GREATER':9,'AND':10,'OR':11,'NOT':12,'LABEL':13,'GOTO':14,'IF':15,'SLEEP':16,'END':17,'RAND':18,'FLOOR':19,'MOD':20,'SIN':21,'COS':22,'SQRT':23,'ATAN2':24,'ABS':26}
class G:
 def __init__(self,name):
    self.name=name;self.lines=[];self.reg={};self.con=[];self.program={k:[] for k in ['inputRegisters','outputRegisters','workingRegisters','inoutRegisters','labels','instructions']};self.seq=0
 def emit(self,s):self.lines.extend(x.strip() for x in s.strip().splitlines() if x.strip())
 def label(self,p='skip'):self.seq+=1;return f'{p}{self.seq}'
 def skip(self,op,a,b):
    end=self.label();self.emit(f'{op} R7 {a} {b}\nIF R7 {end}');return end
 def end(self,label):self.emit(f'LABEL {label}')
 def bind(self,name,prop='position',alias=None):
    alias=alias or name
    specs={'position':[(f'{alias}.Pos.{a}',7) for a in 'XYZ'],'rotation':[(f'{alias}.Rot.{a}',7) for a in 'XYZ'],'physics':[(f'{alias}.Physics.Enabled',7),(f'{alias}.Physics.State',0)],'triggerActive':[(f'{alias}.Trg.{a}',t) for a,t in [('Active',0),('PlayerId',0),('Force',7)]],
    'player':[(f'Player.{a}',t) for a,t in [('SelIndex',1),('SelId',1),('SelPart',1),('Control',1),('Count',0),('Valid',0),('Id',0),('Pos.X',0),('Pos.Y',0),('Pos.Z',0),('Rot.X',0),('Rot.Y',0),('Rot.Z',0),('Name',0),('Col.Sel',1),('Col.R',0),('Col.G',0),('Col.B',0),('LocalId',0),('Respawn',1),('Tel.Pos.X',1),('Tel.Pos.Y',1),('Tel.Pos.Z',1),('Tel.Rot.Y',1),('Tel.Apply',1),('Vel.X',7),('Vel.Y',7),('Vel.Z',7)]],
    'playerVariables':[(f'Player.Var{i}',7) for i in range(1,6)]}
    conn=next((c for c in self.con if c['target']==name),None)
    if conn is None:conn={'target':name,'name':alias,'type':1 if name=='@player' else 0,'properties':[]};self.con.append(conn)
    comps=[]
    for rn,t in specs[prop]:
       key={0:'inputRegisters',1:'outputRegisters',7:'inoutRegisters'}[t];idx=len(self.program[key]);self.program[key].append({'name':rn});self.reg[rn]=(t,idx)
       component={'inputRegisterIndex':-1,'outputRegisterIndex':-1,'inoutRegisterIndex':-1};component[{0:'inputRegisterIndex',1:'outputRegisterIndex',7:'inoutRegisterIndex'}[t]]=idx;comps.append(component)
    # GRAB-exported trigger properties contain SIX slots. Preserve the
    # unbound trailing slots, even though this game only uses the first three.
    if prop=='triggerActive':
       comps.extend({'inputRegisterIndex':-1,'outputRegisterIndex':-1,'inoutRegisterIndex':-1} for _ in range(3))
    conn['properties'].append({prop:{},'components':comps})
 def player(self):self.bind('@player','player');self.bind('@player','playerVariables');self.emit('SET Player.SelPart 0')
 def teleport(self,x,y,z):self.emit(f'SET Player.Tel.Pos.X {x}\nSET Player.Tel.Pos.Y {y}\nSET Player.Tel.Pos.Z {z}\nSET Player.Tel.Apply 1')
 def compile(self,ids):
    p=self.program;labs={}
    for line in self.lines:
       if line.startswith('LABEL '):
         name=line.split()[1]
         if name in labs:raise ValueError('duplicate label '+name)
         labs[name]=len(labs);p['labels'].append({'name':name})
    for i in range(8):p['workingRegisters'].append({'name':f'R{i}'})
    for line in self.lines:
       words=line.split();op=words[0];out=[]
       for j,w in enumerate(words[1:]):
         if op in ['IF','GOTO','LABEL'] and j==len(words)-2:out.append({'type':5,'index':labs[w]})
         elif w in self.reg:t,k=self.reg[w];out.append({'type':t,'index':k})
         elif w.startswith('R') and w[1:].isdigit():
           assert int(w[1:])<8;out.append({'type':2,'index':int(w[1:])})
         elif w=='DeltaTime':out.append({'type':3,'index':4})
         else:out.append({'type':4,'value':float(w)})
       p['instructions'].append({'type':MAP[op],'operands':out})
    cons=[]
    for c in self.con:
      d=dict(c);target=d.pop('target');d['objectID']=ids.get(target,0)
      for prop in d['properties']:prop['objectID']=d['objectID']
      cons.append(d)
    scripts[self.name]='; Generated native GRAB Assembly. Connections in level JSON.\n'+'\n'.join(self.lines)+'\n'
    return dict(position=V(0,-150,0),rotation=Q(),scale=V(1,1,1),program=p,connections=cons,startActive=True,isShared=self.name not in ['LocalMovement','LocalFog'])
allg=[]
def script(name):g=G(name);allg.append(g);return g

# Explicit game configuration, all shared native timing is in seconds.
CONFIG=dict(players=10,calmSeconds=60,huntSeconds=60,waves=5,monsterSpeed=4.1,resetSeconds=5)
import environment, zombie
ctx={k:globals()[k] for k in ['box','group','part','sign','trigger','animation','attach','names','V','Q','C','add','script','state','CONFIG']}
layout=environment.build(ctx);ctx['layout']=layout
manifest.update(config=CONFIG,layout=layout,creature=zombie.build(ctx))
HIDES=[];DOORS=[]
LOOT=[dict(position=pos) for pos in layout.get('gem_positions',[(x,3.95,z) for x,z in environment.TREE_POSITIONS[:3]])]
manifest['loot']=LOOT
for n in ['Clock','Round','KeyState','SkullState','Target','Waypoint','ExitState','LootA','LootB','LootC']:state(n)
# Floor and sealed native finish chamber south of the gate.
box('ExitRoomFloor',(0,-.15,-32),(6.6,.3,8.6),(.13,.17,.16))
box('ExitRoomRoof',(0,4,-32),(6.6,.25,8.6),(.15,.18,.18))
for side in [-1,1]:box(f'ExitRoomSide{side}',(side*3.15,2,-32),(.3,4,8.6),(.19,.21,.22))
box('ExitRoomBack',(0,2,-36.15),(6.6,4,.3),(.19,.21,.22))
group('ExitDoor',(0,0,-28),[part((0,1.75,0),(5.4,3.5,.22),(.23,.26,.25))])
animation('ExitDoor','GateLift',position=(0,4.5,0),duration=1.3)
for nm in ['ExitOpen','ResetAnimations']:
 trigger(nm,(0,-200,0));names[nm]['levelNodeTrigger']['triggerSources']=[]
trigger('Escape',(0,1.4,-34),(2,2.8,2));names['Escape']['levelNodeTrigger']['triggerSources']=[{'triggerSourceBasic':{'type':1}}]
add('Start','levelNodeStart',dict(position=V(0,.1,-22),rotation=Q(),radius=1,name='Graveyard Entry',isHidden=False))
add('Finish','levelNodeFinish',dict(position=V(0,-100,-34),radius=1))
manifest['exitRoom']=dict(gate=[0,0,-28],finish=[0,1.2,-34],socket=[4,2.15,-24],bounds=dict(xmin=-3,xmax=3,zmin=-36,zmax=-28))
# Isolated gallery: dead players cannot interfere with the live gems or skull.
box('SpectatorFloor',(28,-.1,0),(5,.2,52),(.15,.25,.28))
box('SpectatorRoof',(28,4,0),(5,.2,52),(.18,.25,.28))
for x in [25.5,30.5]:box(f'SpectatorSide{x}',(x,2,0),(.18,4,52),(.2,.45,.5),isTransparent=True)
for z in [-26,26]:box(f'SpectatorEnd{z}',(28,2,z),(5,4,.18),(.2,.45,.5))
sign('SpectatorLabel','SPECTATOR — ELIMINATED\nWatch the living survivors.',(28,2,-25),.38,180)
sign('Title','THE GRAVE YARD\nSURVIVE FIVE HUNTS — 10 PLAYERS',(0,3.8,-23),.6)
sign('Rules','60 seconds rest / 60 seconds hunt. Five hunts.\nHOLD a tree gem for immunity. Trees alone do not protect you.\nAfter hunt five, carry the golden skull to the exit pedestal.\nRelease it in the glowing socket; enter the gate and touch finish.',(0,2,-25.5),.36)
sign('ExitLabel','GOLDEN SKULL SOCKET',(4,3,-24),.35)
sign('FinishLabel','ESCAPED — TOUCH GREEN FINISH',(0,2.8,-36),.38)
for sec in range(1,6):sign(f'Restart{sec}',f'ALL PLAYERS ELIMINATED\nNEW ROUND IN {sec}',(28,-100,0),.7)
# Physical golden skull, held and released rather than inventory-only key.
skullpart=part((0,0,0),(.42,.46,.38),(.95,.72,.1),isNeon=True,isGrabbable=True);skullpart['levelNodeStatic']['shape']=1001
group('GoldenSkull',(0,-100,17),[skullpart,part((-.10,.055,-.183),(.08,.09,.03),(.05,.025,.01),isPassable=True),part((.10,.055,-.183),(.08,.09,.03),(.05,.025,.01),isPassable=True),part((0,-.14,-.1),(.28,.11,.25),(.95,.72,.1),isGrabbable=True)])
names['GoldenSkull']['levelNodeGroup'].update(physicsObject=True,localPhysicsObject=False,mass=.3)
box('SkullSocket',(4,1.86,-24),(.75,.10,.75),(.9,.65,.1),isNeon=True,isPassable=True)
box('SkullSpawnPedestal',(0,.65,17),(1,1.3,1),(.25,.28,.24))
for j,l in enumerate(LOOT,1):
 c=[(.1,1,.8),(.5,.4,1),(1,.3,.7)][j-1];p=part((0,0,0),(.22,.2,.22),c,isNeon=True,isGrabbable=True);p['levelNodeStatic']['shape']=1006
 group(f'Gem{j}',tuple(l['position']),[p]);names[f'Gem{j}']['levelNodeGroup'].update(physicsObject=True,localPhysicsObject=False,mass=.15);state(f'GemMemory{j}')
for nm,fog,brightness in [('FogOn',.68,.3),('FogOff',0,.65)]:
 color=(.3,.38,.4) if fog else (.06,.09,.12)
 add(nm,'levelNodeTrigger',dict(shape=1000,position=V(0,-200,0),scale=V(.1,.1,.1),rotation=Q(),isShared=False,triggerSources=[],triggerTargets=[{'mode':0,'triggerTargetAmbience':dict(skyColor0=C(*color),skyColor1=C(*color),sunAltitude=30,sunAzimuth=0,sunSize=0,fogDensity=fog,changeDuration=0,useAdvancedSunSettings=True,sunBrightness=.15,ambientColor=C(.7,.8,.85),ambientBrightness=brightness)}]))
names['FogOn']['levelNodeTrigger']['triggerTargets'].append(dict(mode=1,triggerTargetAmbience=dict(names['FogOff']['levelNodeTrigger']['triggerTargets'][0]['triggerTargetAmbience'])))
# Round shared authority. It stops permanently after five completed hunts.
g=script('RoundClock');g.player()
for n in ['Clock','Round','KeyState','SkullState','ExitState','Monster','Target','LootA','LootB','LootC']:g.bind(n)
g.bind('ResetAnimations','triggerActive')
for h in HIDES:g.bind(f"HideState{h['id']}")
for sec in range(1,6):g.bind(f'Restart{sec}')
g.emit('SET Round.Pos.Z 1\nGOTO initialize\nLABEL loop\nSET ResetAnimations.Trg.Force 0')
for sec in range(1,6):g.emit(f'SET Restart{sec}.Pos.Y -100')
g.emit('IF Round.Pos.X countdown\nSET R0 0\nSET R1 0\nSET R2 0\nLABEL scan\nSET Player.SelIndex R0\nNOT R7 Player.Valid\nIF R7 next\nADD R1 R1 1\nEQUAL R7 Player.Var1 1\nADD R2 R2 R7\nLABEL next\nADD R0 R0 1\nLESS R7 R0 Player.Count\nIF R7 scan\nNOT R7 R1\nIF R7 advance\nEQUAL R7 R1 R2\nNOT R7 R7\nIF R7 advance\nSET Round.Pos.X 1\nSET Round.Pos.Y 5\nSET Clock.Pos.X 0\nSET Monster.Pos.Y -100\nSET Target.Pos.X 0\nGOTO display\nLABEL countdown\nSUB Round.Pos.Y Round.Pos.Y DeltaTime\nGREATER R7 Round.Pos.Y 0.00001\nIF R7 display\nADD Round.Pos.Z Round.Pos.Z 1\nSET Round.Pos.X 0\nSET Round.Pos.Y 0\nSET ResetAnimations.Trg.Force 1\nSET R0 0\nLABEL revive\nSET Player.SelIndex R0\nNOT R7 Player.Valid\nIF R7 revived\nSET Player.Var1 0\nSET Player.Var2 0\nSET Player.Var3 0\nSET Player.Var4 0\nLABEL revived\nADD R0 R0 1\nLESS R7 R0 Player.Count\nIF R7 revive\nLABEL initialize\nSET Clock.Pos.X 0\nSET Clock.Pos.Y 0\nSET Clock.Pos.Z 0\nSET KeyState.Pos.X 0\nSET KeyState.Pos.Y 0\nSET KeyState.Pos.Z 0\nSET SkullState.Pos.X 0\nSET SkullState.Pos.Y 0\nSET SkullState.Pos.Z 0\nSET ExitState.Pos.X 0\nSET Monster.Pos.Y -100\nSET Target.Pos.X 0')
for h in HIDES:
 for a in 'XYZ':g.emit(f"SET HideState{h['id']}.Pos.{a} 0")
for loot in ['LootA','LootB','LootC']:g.emit(f'SET {loot}.Pos.Y 0\nADD {loot}.Pos.Z {loot}.Pos.Z 1')
g.emit('GOTO wait\nLABEL advance\nGREATER R7 Clock.Pos.Y 4.5\nIF R7 wait\nADD Clock.Pos.Z Clock.Pos.Z DeltaTime\nLESS R7 Clock.Pos.Z 60\nIF R7 wait\nSUB Clock.Pos.Z Clock.Pos.Z 60\nIF Clock.Pos.X end_attack\nSET Clock.Pos.X 1\nGOTO wait\nLABEL end_attack\nSET Clock.Pos.X 0\nSET Monster.Pos.Y -100\nSET Target.Pos.X 0\nADD Clock.Pos.Y Clock.Pos.Y 1\nLESS R7 Clock.Pos.Y 5\nIF R7 wait\nSET Clock.Pos.Z 0\nSET SkullState.Pos.X 1\nGOTO wait\nLABEL display\nADD R0 Round.Pos.Y 0.99999\nFLOOR R0 R0')
for sec in range(1,6):
 end=g.label();g.emit(f'EQUAL R7 R0 {sec}\nNOT R7 R7\nIF R7 {end}\nSET Restart{sec}.Pos.Y 2\nLABEL {end}')
g.emit('LABEL wait\nSLEEP 0\nGOTO loop')
# Copy the office's per-client fog lifecycle, with instant clear at hunt end.
g=script('LocalFog');g.bind('Clock')
for n in ['FogOn','FogOff']:g.bind(n,'triggerActive')
g.emit('SET R6 -1\nLABEL loop\nEQUAL R7 R6 Clock.Pos.X\nNOT R7 R7\nIF R7 change\nIF Clock.Pos.X wait\nSUB R5 R5 DeltaTime\nGREATER R7 R5 0\nIF R7 wait\nGOTO clear\nLABEL change\nSET R6 Clock.Pos.X\nSET FogOn.Trg.Force 0\nSET FogOff.Trg.Force 0\nSLEEP 0\nNOT R7 Clock.Pos.X\nIF R7 clear\nSET FogOn.Trg.Force 1\nGOTO wait\nLABEL clear\nSET FogOn.Trg.Force 0\nSET FogOff.Trg.Force 0\nSLEEP 0\nIF Clock.Pos.X loop\nSET FogOff.Trg.Force 1\nSET R5 0.5\nLABEL wait\nSLEEP 0\nGOTO loop')

# Native physical gems: fixed tree mount until first pickup, then free physics.
for index,l in enumerate(LOOT,1):
 loot=['LootA','LootB','LootC'][index-1];vis=f'Gem{index}';mem=f'GemMemory{index}';x,y,z=l['position']
 g=script(f'{vis}Inventory');g.player()
 for n in [loot,vis,mem]:g.bind(n)
 g.bind(vis,'physics')
 g.emit(f'LABEL loop\nEQUAL R7 {mem}.Pos.X {loot}.Pos.Z\nNOT R7 R7\nIF R7 relocate\nLESS R7 {vis}.Pos.Y -10\nIF R7 relocate\nGREATER R7 {vis}.Pos.Y 14\nIF R7 relocate\nABS R0 {vis}.Pos.X\nGREATER R7 R0 24\nIF R7 relocate\nABS R0 {vis}.Pos.Z\nGREATER R7 R0 28\nIF R7 relocate\nSET {loot}.Pos.Y 0\nEQUAL R7 {vis}.Physics.State 3\nIF R7 held\nIF {mem}.Pos.Y wait\nGOTO dock\nLABEL held\nSET R0 0\nSET R5 0.0784\nLABEL players\nSET Player.SelIndex R0\nNOT R7 Player.Valid\nIF R7 next\nIF Player.Var1 next')
 for hand in [3,4]:
  end=g.label();g.emit(f'SET Player.SelPart {hand}\nSUB R1 Player.Pos.X {vis}.Pos.X\nSUB R2 Player.Pos.Y {vis}.Pos.Y\nSUB R3 Player.Pos.Z {vis}.Pos.Z\nMUL R1 R1 R1\nMUL R2 R2 R2\nMUL R3 R3 R3\nADD R1 R1 R2\nADD R1 R1 R3\nLESS R7 R1 R5\nNOT R7 R7\nIF R7 {end}\nSET R5 R1\nSET {mem}.Pos.Y 1\nADD {loot}.Pos.Y Player.Id 1\nLABEL {end}')
 g.emit(f'LABEL next\nADD R0 R0 1\nLESS R7 R0 Player.Count\nIF R7 players\nIF {mem}.Pos.Y wait\nGOTO dock\nLABEL relocate\nSET {loot}.Pos.Y 0\nSET {mem}.Pos.Y 0\nSET {vis}.Physics.Enabled 0\nSET {mem}.Pos.X {loot}.Pos.Z\nSLEEP 0\nLABEL dock\nSET {vis}.Pos.X {x}\nSET {vis}.Pos.Y {y}\nSET {vis}.Pos.Z {z}\nSET {vis}.Physics.Enabled 1\nLABEL wait\nSLEEP 0\nGOTO loop')
# Actual physical release: previous living carrier + pickup latch + native non-held
# state + 3D socket overlap. Proximity while held never unlocks the gate.
g=script('SkullInventory');g.player()
for n in ['SkullState','GoldenSkull','Clock','Round','ExitState']:g.bind(n)
g.bind('GoldenSkull','physics')
g.emit('LABEL loop\nLESS R7 Clock.Pos.Y 5\nIF R7 unavailable\nIF ExitState.Pos.X socketed\nEQUAL R7 GoldenSkull.Physics.State 3\nIF R7 held\nIF SkullState.Pos.Z released\nGOTO spawn\nLABEL held\nSET R0 0\nSET R5 0.1225\nLABEL players\nSET Player.SelIndex R0\nNOT R7 Player.Valid\nIF R7 next\nIF Player.Var1 next')
for hand in [3,4]:
 end=g.label();g.emit(f'SET Player.SelPart {hand}\nSUB R1 Player.Pos.X GoldenSkull.Pos.X\nSUB R2 Player.Pos.Y GoldenSkull.Pos.Y\nSUB R3 Player.Pos.Z GoldenSkull.Pos.Z\nMUL R1 R1 R1\nMUL R2 R2 R2\nMUL R3 R3 R3\nADD R1 R1 R2\nADD R1 R1 R3\nLESS R7 R1 R5\nNOT R7 R7\nIF R7 {end}\nSET R5 R1\nADD SkullState.Pos.Y Player.Id 1\nSET SkullState.Pos.Z 1\nLABEL {end}')
g.emit('LABEL next\nADD R0 R0 1\nLESS R7 R0 Player.Count\nIF R7 players\nGOTO wait\nLABEL released\nNOT R7 SkullState.Pos.Y\nIF R7 spawn\nSUB R0 SkullState.Pos.Y 1\nSET Player.SelId R0\nNOT R7 Player.Valid\nIF R7 spawn\nIF Player.Var1 spawn\nSUB R1 GoldenSkull.Pos.X 4\nABS R1 R1\nGREATER R7 R1 0.42\nIF R7 recovery\nSUB R1 GoldenSkull.Pos.Y 2.15\nABS R1 R1\nGREATER R7 R1 0.42\nIF R7 recovery\nSUB R1 GoldenSkull.Pos.Z -24\nABS R1 R1\nGREATER R7 R1 0.42\nIF R7 recovery\nSET ExitState.Pos.X 1\nGOTO socketed\nLABEL recovery\nLESS R7 GoldenSkull.Pos.Y -8\nIF R7 spawn\nGREATER R7 GoldenSkull.Pos.Y 20\nIF R7 spawn\nABS R1 GoldenSkull.Pos.X\nGREATER R7 R1 24\nIF R7 spawn\nABS R1 GoldenSkull.Pos.Z\nGREATER R7 R1 28\nIF R7 spawn\nGOTO wait\nLABEL spawn\nSET SkullState.Pos.Y 0\nSET SkullState.Pos.Z 0\nSET GoldenSkull.Physics.Enabled 0\nSET GoldenSkull.Pos.X 0\nSET GoldenSkull.Pos.Y 1.6\nSET GoldenSkull.Pos.Z 17\nSET GoldenSkull.Physics.Enabled 1\nGOTO wait\nLABEL socketed\nSET GoldenSkull.Physics.Enabled 0\nSET GoldenSkull.Pos.X 4\nSET GoldenSkull.Pos.Y 2.15\nSET GoldenSkull.Pos.Z -24\nGOTO wait\nLABEL unavailable\nSET GoldenSkull.Physics.Enabled 0\nSET GoldenSkull.Pos.Y -100\nSET SkullState.Pos.Y 0\nSET SkullState.Pos.Z 0\nLABEL wait\nSLEEP 0\nGOTO loop')
manifest['navigation']=zombie.emit(ctx)
# Shared gate and status intent, with native finish physically inside the chamber.
g=script('ExitController');g.player()
for n in ['ExitState','Finish','Clock']:g.bind(n)
for n in ['ExitOpen','Escape']:g.bind(n,'triggerActive')
g.emit('LABEL loop\nNOT R7 ExitState.Pos.X\nIF R7 closed\nLESS R7 Clock.Pos.Y 5\nIF R7 closed\nSET Finish.Pos.Y 1.2\nSET ExitOpen.Trg.Force 1\nNOT R7 Escape.Trg.Active\nIF R7 wait\nSET Player.SelId Escape.Trg.PlayerId\nNOT R7 Player.Valid\nIF R7 wait\nIF Player.Var1 wait\nSET Player.Var1 2\nGOTO wait\nLABEL closed\nSET Finish.Pos.Y -100\nSET ExitOpen.Trg.Force 0\nLABEL wait\nSLEEP 0\nGOTO loop')
# Each connected client applies spectator/revival movement only to its LocalId.
g=script('LocalMovement');g.player();g.bind('Round')
g.emit('LABEL loop\nSET Player.SelPart 0\nSET Player.SelId Player.LocalId\nNOT R7 Player.Valid\nIF R7 wait\nEQUAL R7 Player.Var5 Round.Pos.Z\nIF R7 status\nSET Player.Var5 Round.Pos.Z\nGREATER R7 Round.Pos.Z 1\nIF R7 revive\nLABEL status\nEQUAL R7 Player.Var1 1\nIF R7 dead\nGOTO wait\nLABEL dead\nLESS R7 Player.Pos.Y 0\nIF R7 spectate\nGREATER R7 Player.Pos.Y 3.8\nIF R7 spectate\nSUB R0 Player.Pos.X 28\nABS R0 R0\nGREATER R7 R0 2.2\nIF R7 spectate\nABS R0 Player.Pos.Z\nGREATER R7 R0 25.5\nIF R7 spectate\nGOTO wait\nLABEL spectate');g.teleport(28,.1,0)
g.emit('GOTO wait\nLABEL revive\nSET Player.Var1 0\nSET Player.Var2 0\nSET Player.Var3 0\nSET Player.Var4 0\nMOD R0 Player.Id 10\nMOD R1 R0 2\nMUL R1 R1 1.4\nSUB R1 R1 0.7\nMUL R0 R0 0.2\nSUB R0 -22 R0');g.teleport('R1',.1,'R0')
g.emit('LABEL wait\nSLEEP 0\nGOTO loop')
# Fresh 1-based depth-first object IDs after geometry and program declarations.
ids={};counter=0;reverse={id(v):k for k,v in names.items()}
def walk(nodes):
 global counter
 for n in nodes:
  counter+=1
  if id(n) in reverse:ids[reverse[id(n)]]=counter
  if 'levelNodeGroup' in n:walk(n['levelNodeGroup']['childNodes'])
walk(N)
for index,g in enumerate(allg,1):ids[g.name]=counter+index
for g in allg:
 missing=[c['target'] for c in g.con if c['target']!='@player' and c['target'] not in ids]
 assert not missing,missing
 add(g.name,'levelNodeGASM',g.compile(ids))
def target_anim(triggername,objectname,title,mode=3,reverse=False):
 names[triggername]['levelNodeTrigger']['triggerTargets']=[{'mode':0,'triggerTargetAnimation':dict(objectID=ids[objectname],animationName=title,loop=False,reverse=reverse,mode=mode)}]
target_anim('ExitOpen','ExitDoor','GateLift',1)
names['Escape']['levelNodeTrigger']['triggerTargets']=[{'mode':0,'triggerTargetGASM':dict(objectID=ids['ExitController'],mode=1)}]
target_anim('ResetAnimations','ExitDoor','GateLift',5)
level=dict(formatVersion=25,title='The Grave Yard [1]',creators='Ernesto',description='Sixteen haunted graves. Ten-player cooperative survival. Five 60-second zombie hunts separated by 60-second rests. Holding one of three tree gems grants immunity; tree climbing alone does not. Release the golden skull on the exit pedestal after hunt five. Captured players spectate; five-second all-dead reset. Quest validation pending.',tags=['horror','survival'],maxCheckpointCount=0,defaultSpawnPointID=ids['Start'],showReplays=False,disablePracticeMode=True,unlisted=True,ambienceSettings=dict(skyZenithColor=C(.025,.035,.08),skyHorizonColor=C(.08,.1,.15),sunAltitude=-30,sunAzimuth=0,sunSize=0,fogDensity=0,useAdvancedSunSettings=True,sunBrightness=.1,ambientColor=C(.55,.65,.85),ambientBrightness=.65),levelNodes=N)
def cost(nodes):
 total=0
 for n in nodes:
  if 'levelNodeGroup' in n:total+=2+cost(n['levelNodeGroup']['childNodes'])
  elif 'levelNodeStart' in n or 'levelNodeFinish' in n:pass
  elif 'levelNodeSign' in n:total+=5
  elif 'levelNodeGASM' in n:total+=2+len(n['levelNodeGASM']['program']['instructions'])
  else:total+=2
 return total
level['complexity']=cost(N)
(ROOT/'dist/the-grave-yard.json').write_text(json.dumps(level,indent=2))
message=ParseDict(level,pb.Level());binary=message.SerializeToString();(ROOT/'dist/the-grave-yard.level').write_bytes(binary)
assert pb.Level.FromString(binary)==message
for nm,s in scripts.items():(ROOT/'src'/f'{nm}.gasm').write_text(s)
manifest.update(nodeCount=counter+len(allg),codeBlocks=len(allg),instructions={g.name:len(g.program['instructions']) for g in allg},complexity=level['complexity'],ids=ids)
(ROOT/'docs/manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:v for k,v in manifest.items() if k in ['nodeCount','codeBlocks','complexity','revision']}))
