"""Build Parking Lot Horror using GRAB Tools format 25 and native GASM."""
import json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
import grab_pb2 as pb
from google.protobuf.json_format import ParseDict
V=lambda x=0,y=0,z=0:dict(x=x,y=y,z=z)
Q=lambda yaw=0:dict(x=0,y=math.sin(math.radians(yaw/2)),z=0,w=math.cos(math.radians(yaw/2)))
C=lambda r,g,b,a=1:dict(r=r,g=g,b=b,a=a)
N=[]; names={}; scripts={}; manifest={'status':'experimental-native-build','formatVersion':25,'targetPlayers':10,'revision':'parking-horror-3','monsterSpeed':3.7}
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

# Game configuration: fixed loot mounts replace office relocation; five hunts total.
CONFIG=dict(players=10,calmSeconds=60,huntSeconds=60,waves=5,monsterSpeed=3.7,resetSeconds=5)
import parking, vehicles, monster, navigation
ctx={k:globals()[k] for k in ['box','group','part','sign','trigger','animation','attach','names','V','Q','C','add']}
layout=parking.build(ctx); fleet=vehicles.build(ctx); creature=monster.build(ctx)
manifest.update(config=CONFIG,layout=layout,fleet=fleet,creature=creature)
HIDES=fleet['hides']; LOOT=fleet['loot']; DOORS=fleet['doors']
nav=navigation.prepare(layout,fleet);manifest['navigation']=nav
for n in navigation.STATE_NAMES:state(n)
for n in ['Clock','Round','KeyState','Target','Waypoint','ExitState','LootA','LootB','LootC']:
 state(n)
for h in HIDES:state(f"HideState{h['id']}")
# The covered finish room continues the garage floor; the gate seals the doorway.
# A native finish block appears inside only after the shared key unlock succeeds.
box('ExitRoomFloor',(0,-.16,32.7),(6.6,.32,9.8),(.13,.22,.20))
box('ExitRoomRoof',(0,4.60,33.45),(6.6,.24,8.3),(.19,.215,.225))
for side in [-1,1]:box(f'ExitRoomSide{side}',(side*3.15,2.24,33.45),(.3,4.48,8.3),(.19,.215,.225))
box('ExitRoomBack',(0,2.24,37.45),(6.6,4.48,.3),(.19,.215,.225))
box('ExitRoomLight',(0,4.43,34.5),(2,.04,.5),(.6,.95,.75),isNeon=True)
sign('ExitRoomFinishLabel','ESCAPED\nTOUCH THE GREEN FINISH BLOCK',(0,2.7,37.2),.38,180,c=(.4,1,.65))
group('ExitDoor',(0,0,29.35),[part((0,2.24,0),(5.4,4.48,.18),(.24,.28,.29)),part((0,1.6,-.11),(5.4,.3,.04),(.75,.1,.08),isNeon=True)])
animation('ExitDoor','GateLift',position=(0,5,0),duration=1.3)
box('ExitLock',(0,1.1,29.15),(.4,.48,.12),(.95,.7,.12),isNeon=True)
attach('ExitDoor','ExitLock',(0,1.1,-.2))
# Low, passable green strips lead from the doorway to the native finish.
for i,z in enumerate([30.4,31.8,33.2,34.3],1):
 box(f'FinishPath{i}',(0,.025,z),(.75,.035,.4),(.2,1,.55),isNeon=True,isPassable=True)

manifest['exitRoom']=dict(bounds=dict(xmin=-3,xmax=3,zmin=29.35,zmax=37.3),floorTop=0,finish=[0,1.2,35],gate=[0,0,29.35])
for name in ['ExitOpen','ResetAnimations']:
 trigger(name,(0,-200,0));names[name]['levelNodeTrigger']['triggerSources']=[]
trigger('ExitUse',(0,1.1,29.05),(.9,.65,.55));trigger('Escape',(0,1.4,35),(2,2.8,2))
names['Escape']['levelNodeTrigger']['triggerSources']=[{'triggerSourceBasic':{'type':1}}]
add('Start','levelNodeStart',dict(position=V(0,.1,-27),rotation=Q(),radius=1,name='Parking Entry',isHidden=False))
add('Finish','levelNodeFinish',dict(position=V(0,-100,35),radius=1))
# Spectators stay physically separated from live loot, with sightlines into the lot.
box('SpectatorFloor',(24,-.1,0),(4.8,.2,52),(.15,.32,.36))
box('SpectatorRoof',(24,3.3,0),(4.8,.2,52),(.18,.25,.28))
for x in [21.6,26.4]:box(f'SpectatorSide{x}',(x,1.6,0),(.15,3.2,52),(.2,.45,.5),isTransparent=x==21.6)
for z in [-26,26]:box(f'SpectatorEnd{z}',(24,1.6,z),(4.8,3.2,.15),(.2,.45,.5))
sign('SpectatorLabel','SPECTATOR — ELIMINATED\nWatch the survivors through the garage window.',(24,2,-25),.38,180)
sign('Title','PARKING LOT HORROR\nSURVIVE FIVE HUNTS — 10 PLAYERS',(0,3,-26),.6)
sign('Rules','60 seconds calm / 60 seconds hunt. Five hunts only.\nTouch blue car handles to open doors. HOLD a gem for immunity.\nBlue van pads hide / leave. One player per van. Hiding protects you.\nAfter hunt five, TOUCH the gold pedestal key: it becomes inventory.\nApproach the GOLD LOCK or touch it; follow GREEN strips to finish.',(0,1.8,-28),.4)
sign('ExitLabel','EXIT — KEY REQUIRED\nTOUCH KEY ON RIGHT PEDESTAL AFTER HUNT FIVE',(0,3.5,29.2),.36,180,c=(1,.8,.3))
sign('KeyCollected','KEY COLLECTED — INVENTORY\nAPPROACH EXIT OR TOUCH GOLD LOCK',(0,-100,29.1),.32,180,c=(1,.8,.2))
sign('ExitReady','EXIT OPEN — WALK THROUGH\nFOLLOW GREEN STRIPS; TOUCH GREEN FINISH',(0,-100,29.15),.36,180,c=(.3,1,.6))
sign('KeyInstructions','AFTER HUNT FIVE: TOUCH GOLD KEY\nPICKUP STORES IT IN INVENTORY\nTHEN APPROACH EXIT OR TOUCH GOLD LOCK',(2.8,2.3,27),.25,180,c=(1,.8,.3))
for sec in range(1,6):sign(f'Restart{sec}',f'ALL PLAYERS ELIMINATED\nNEW ROUND IN {sec}',(24,-100,0),.7)
group('Key',(0,-100,0),[part((0,0,0),(.15,.15,.15),(.95,.75,.12),isNeon=True,isPassable=True),part((.18,0,0),(.28,.04,.04),(.95,.75,.12),isNeon=True,isPassable=True)])
trigger('KeyUse',(2.8,1,26.8),(.5,.5,.5));box('KeyPedestal',(2.8,.5,26.8),(.6,1,.6),(.2,.25,.25))
for j,l in enumerate(LOOT,1):
 c=[(.1,1,.8),(.5,.4,1),(1,.3,.7)][j-1];p=part((0,0,0),(.22,.2,.22),c,isNeon=True,isGrabbable=True);p['levelNodeStatic']['shape']=1006
 group(f'Gem{j}',tuple(l['position']),[p]);names[f'Gem{j}']['levelNodeGroup'].update(physicsObject=True,localPhysicsObject=False,mass=.15);state(f'GemMemory{j}')
for nm,fog,brightness in [('FogOn',.68,.3),('FogOff',0,.65)]:
 color=(.3,.38,.4) if fog else (.06,.09,.12)
 add(nm,'levelNodeTrigger',dict(shape=1000,position=V(0,-200,0),scale=V(.1,.1,.1),rotation=Q(),isShared=False,triggerSources=[],triggerTargets=[{'mode':0,'triggerTargetAmbience':dict(skyColor0=C(*color),skyColor1=C(*color),sunAltitude=30,sunAzimuth=0,sunSize=0,fogDensity=fog,changeDuration=0,useAdvancedSunSettings=True,sunBrightness=.15,ambientColor=C(.7,.8,.85),ambientBrightness=brightness)}]))
names['FogOn']['levelNodeTrigger']['triggerTargets'].append(dict(mode=1,triggerTargetAmbience=dict(names['FogOff']['levelNodeTrigger']['triggerTargets'][0]['triggerTargetAmbience'])))
# Round shared authority. It stops permanently after five completed hunts.
g=script('RoundClock');g.player()
for n in ['Clock','Round','KeyState','ExitState','Monster','Target','LootA','LootB','LootC']:g.bind(n)
g.bind('ResetAnimations','triggerActive')
for h in HIDES:g.bind(f"HideState{h['id']}")
for sec in range(1,6):g.bind(f'Restart{sec}')
g.emit('SET Round.Pos.Z 1\nGOTO initialize\nLABEL loop\nSET ResetAnimations.Trg.Force 0')
for sec in range(1,6):g.emit(f'SET Restart{sec}.Pos.Y -100')
g.emit('IF Round.Pos.X countdown\nSET R0 0\nSET R1 0\nSET R2 0\nLABEL scan\nSET Player.SelIndex R0\nNOT R7 Player.Valid\nIF R7 next\nADD R1 R1 1\nEQUAL R7 Player.Var1 1\nADD R2 R2 R7\nLABEL next\nADD R0 R0 1\nLESS R7 R0 Player.Count\nIF R7 scan\nNOT R7 R1\nIF R7 advance\nEQUAL R7 R1 R2\nNOT R7 R7\nIF R7 advance\nSET Round.Pos.X 1\nSET Round.Pos.Y 5\nSET Clock.Pos.X 0\nSET Monster.Pos.Y -100\nSET Target.Pos.X 0\nGOTO display\nLABEL countdown\nSUB Round.Pos.Y Round.Pos.Y DeltaTime\nGREATER R7 Round.Pos.Y 0.00001\nIF R7 display\nADD Round.Pos.Z Round.Pos.Z 1\nSET Round.Pos.X 0\nSET Round.Pos.Y 0\nSET ResetAnimations.Trg.Force 1\nSET R0 0\nLABEL revive\nSET Player.SelIndex R0\nNOT R7 Player.Valid\nIF R7 revived\nSET Player.Var1 0\nSET Player.Var2 0\nSET Player.Var3 0\nSET Player.Var4 0\nLABEL revived\nADD R0 R0 1\nLESS R7 R0 Player.Count\nIF R7 revive\nLABEL initialize\nSET Clock.Pos.X 0\nSET Clock.Pos.Y 0\nSET Clock.Pos.Z 0\nSET KeyState.Pos.X 0\nSET KeyState.Pos.Y 0\nSET KeyState.Pos.Z 0\nSET ExitState.Pos.X 0\nSET Monster.Pos.Y -100\nSET Target.Pos.X 0')
for h in HIDES:
 for a in 'XYZ':g.emit(f"SET HideState{h['id']}.Pos.{a} 0")
for loot in ['LootA','LootB','LootC']:g.emit(f'SET {loot}.Pos.Y 0\nADD {loot}.Pos.Z {loot}.Pos.Z 1')
g.emit('GOTO wait\nLABEL advance\nGREATER R7 Clock.Pos.Y 4.5\nIF R7 wait\nADD Clock.Pos.Z Clock.Pos.Z DeltaTime\nLESS R7 Clock.Pos.Z 60\nIF R7 wait\nSUB Clock.Pos.Z Clock.Pos.Z 60\nIF Clock.Pos.X end_attack\nSET Clock.Pos.X 1\nGOTO wait\nLABEL end_attack\nSET Clock.Pos.X 0\nSET Monster.Pos.Y -100\nSET Target.Pos.X 0\nADD Clock.Pos.Y Clock.Pos.Y 1\nLESS R7 Clock.Pos.Y 5\nIF R7 wait\nSET Clock.Pos.Z 0\nSET KeyState.Pos.X 1\nSET KeyState.Pos.Z 1\nGOTO wait\nLABEL display\nADD R0 Round.Pos.Y 0.99999\nFLOOR R0 R0')
for sec in range(1,6):
 end=g.label();g.emit(f'EQUAL R7 R0 {sec}\nNOT R7 R7\nIF R7 {end}\nSET Restart{sec}.Pos.Y 2\nLABEL {end}')
g.emit('LABEL wait\nSLEEP 0\nGOTO loop')
# Copy the office's per-client fog lifecycle, with instant clear at hunt end.
g=script('LocalFog');g.bind('Clock')
for n in ['FogOn','FogOff']:g.bind(n,'triggerActive')
g.emit('SET R6 -1\nLABEL loop\nEQUAL R7 R6 Clock.Pos.X\nNOT R7 R7\nIF R7 change\nIF Clock.Pos.X wait\nSUB R5 R5 DeltaTime\nGREATER R7 R5 0\nIF R7 wait\nGOTO clear\nLABEL change\nSET R6 Clock.Pos.X\nSET FogOn.Trg.Force 0\nSET FogOff.Trg.Force 0\nSLEEP 0\nNOT R7 Clock.Pos.X\nIF R7 clear\nSET FogOn.Trg.Force 1\nGOTO wait\nLABEL clear\nSET FogOn.Trg.Force 0\nSET FogOff.Trg.Force 0\nSLEEP 0\nIF Clock.Pos.X loop\nSET FogOff.Trg.Force 1\nSET R5 0.5\nLABEL wait\nSLEEP 0\nGOTO loop')

# Shared hide ownership sets intent only; local movement handles every teleport.
# Var2 movement command: +hideID enter, -hideID leave; Var4 local acknowledged hideID.
for h in HIDES:
 i=h['id'];st=f'HideState{i}';g=script(f'Hide{i}');g.player();g.bind(st)
 for k in ['use','leave','open','close']:g.bind(h[k],'triggerActive')
 g.emit(f'LABEL loop\nSET {h["open"]}.Trg.Force 0\nSET {h["close"]}.Trg.Force 0\nEQUAL R7 {h["use"]}.Trg.Active {st}.Pos.Y\nIF R7 leavecheck\nSET {st}.Pos.Y {h["use"]}.Trg.Active\nNOT R7 {h["use"]}.Trg.Active\nIF R7 leavecheck\nSET Player.SelId {h["use"]}.Trg.PlayerId\nNOT R7 Player.Valid\nIF R7 leavecheck\nIF Player.Var1 leavecheck\nADD R0 Player.Id 1\nEQUAL R7 {st}.Pos.X R0\nIF R7 exit\nIF {st}.Pos.X leavecheck\nIF Player.Var3 leavecheck\nSET {st}.Pos.X R0\nSET Player.Var3 {i}\nSET Player.Var2 {i}\nSET Player.Var4 0\nSET R6 0.75\nSET {h["close"]}.Trg.Force 1\nGOTO maintain\nLABEL leavecheck\nSUB R6 R6 DeltaTime\nGREATER R7 R6 0\nIF R7 maintain\nNOT R7 {h["leave"]}.Trg.Active\nIF R7 maintain\nSET Player.SelId {h["leave"]}.Trg.PlayerId\nNOT R7 Player.Valid\nIF R7 maintain\nIF Player.Var1 maintain\nEQUAL R7 Player.Var3 {i}\nNOT R7 R7\nIF R7 maintain\nLABEL exit\nSET {st}.Pos.X 0\nSET Player.Var3 0\nSET Player.Var2 {-i}\nSET Player.Var4 0\nSET {h["open"]}.Trg.Force 1\nSET R6 0.75\nLABEL maintain\nNOT R7 {st}.Pos.X\nIF R7 wait\nSUB R0 {st}.Pos.X 1\nSET Player.SelId R0\nNOT R7 Player.Valid\nIF R7 clear\nIF Player.Var1 clear\nEQUAL R7 Player.Var3 {i}\nNOT R7 R7\nIF R7 clear\nGREATER R7 R6 0\nIF R7 wait')
 x,_,z=h['position'];hx,hz=h['halfExtent']
 g.emit(f'SUB R1 Player.Pos.X {x}\nABS R1 R1\nGREATER R7 R1 {hx}\nIF R7 clear\nSUB R1 Player.Pos.Z {z}\nABS R1 R1\nGREATER R7 R1 {hz}\nIF R7 clear\nGOTO wait\nLABEL clear\nSET {st}.Pos.X 0\nNOT R7 Player.Valid\nIF R7 wait\nEQUAL R7 Player.Var3 {i}\nNOT R7 R7\nIF R7 wait\nSET Player.Var3 0\nSET Player.Var2 0\nSET Player.Var4 0\nLABEL wait\nSLEEP 0\nGOTO loop')
# Native physical gems: fixed vehicle console until first pickup, then free physics.
for index,l in enumerate(LOOT,1):
 loot=['LootA','LootB','LootC'][index-1];vis=f'Gem{index}';mem=f'GemMemory{index}';x,y,z=l['position']
 g=script(f'{vis}Inventory');g.player()
 for n in [loot,vis,mem]:g.bind(n)
 g.bind(vis,'physics')
 g.emit(f'LABEL loop\nEQUAL R7 {mem}.Pos.X {loot}.Pos.Z\nNOT R7 R7\nIF R7 relocate\nLESS R7 {vis}.Pos.Y -10\nIF R7 relocate\nGREATER R7 {vis}.Pos.Y 6\nIF R7 relocate\nABS R0 {vis}.Pos.X\nGREATER R7 R0 21\nIF R7 relocate\nABS R0 {vis}.Pos.Z\nGREATER R7 R0 30\nIF R7 relocate\nSET {loot}.Pos.Y 0\nEQUAL R7 {vis}.Physics.State 3\nIF R7 held\nIF {mem}.Pos.Y wait\nGOTO dock\nLABEL held\nSET R0 0\nSET R5 0.0784\nLABEL players\nSET Player.SelIndex R0\nNOT R7 Player.Valid\nIF R7 next\nIF Player.Var1 next')
 for hand in [3,4]:
  end=g.label();g.emit(f'SET Player.SelPart {hand}\nSUB R1 Player.Pos.X {vis}.Pos.X\nSUB R2 Player.Pos.Y {vis}.Pos.Y\nSUB R3 Player.Pos.Z {vis}.Pos.Z\nMUL R1 R1 R1\nMUL R2 R2 R2\nMUL R3 R3 R3\nADD R1 R1 R2\nADD R1 R1 R3\nLESS R7 R1 R5\nNOT R7 R7\nIF R7 {end}\nSET R5 R1\nSET {mem}.Pos.Y 1\nADD {loot}.Pos.Y Player.Id 1\nLABEL {end}')
 g.emit(f'LABEL next\nADD R0 R0 1\nLESS R7 R0 Player.Count\nIF R7 players\nIF {mem}.Pos.Y wait\nGOTO dock\nLABEL relocate\nSET {loot}.Pos.Y 0\nSET {mem}.Pos.Y 0\nSET {vis}.Physics.Enabled 0\nSET {mem}.Pos.X {loot}.Pos.Z\nSLEEP 0\nLABEL dock\nSET {vis}.Pos.X {x}\nSET {vis}.Pos.Y {y}\nSET {vis}.Pos.Z {z}\nSET {vis}.Physics.Enabled 1\nLABEL wait\nSLEEP 0\nGOTO loop')
# Key availability is strictly guarded by the fifth completed hunt.
g=script('KeyInventory');g.player();g.bind('KeyState');g.bind('Key');g.bind('Clock');g.bind('KeyUse','triggerActive');g.bind('KeyCollected');g.bind('ExitState')
g.emit('LABEL loop\nSET KeyCollected.Pos.Y -100\nSET Key.Pos.Y -100\nLESS R7 Clock.Pos.Y 5\nIF R7 wait\nIF KeyState.Pos.Y owned\nSET Key.Pos.X 2.8\nSET Key.Pos.Y 1.14\nSET Key.Pos.Z 26.8\nNOT R7 KeyUse.Trg.Active\nIF R7 wait\nSET Player.SelId KeyUse.Trg.PlayerId\nNOT R7 Player.Valid\nIF R7 wait\nIF Player.Var1 wait\nADD KeyState.Pos.Y Player.Id 1\nSET KeyState.Pos.X 0\nGOTO wait\nLABEL owned\nSUB R0 KeyState.Pos.Y 1\nSET Player.SelId R0\nNOT R7 Player.Valid\nIF R7 lost\nIF Player.Var1 lost\nIF ExitState.Pos.X carried\nSET KeyCollected.Pos.Y 2.4\nLABEL carried\nSET Key.Pos.X Player.Pos.X\nADD Key.Pos.Y Player.Pos.Y 0.5\nSET Key.Pos.Z Player.Pos.Z\nGOTO wait\nLABEL lost\nSET KeyState.Pos.Y 0\nSET KeyState.Pos.X 1\nLABEL wait\nSLEEP 0\nGOTO loop')
# Skeleton targets living, unhidden, unprotected players on the garage ground.
navigation.emit_clock(script('NavClock'))
g=script('MonsterAI');g.player();g.bind('Monster','rotation')
for n in ['Monster','Clock','Target','Waypoint','LootA','LootB','LootC']:g.bind(n)
for n in navigation.STATE_NAMES:g.bind(n)
g.emit('LABEL loop\nIF Clock.Pos.X hunting\nSET Monster.Pos.Y -100\nSET Target.Pos.X 0\nSET NavA.Pos.Z 0\nGOTO wait\nLABEL hunting\nGREATER R7 Monster.Pos.Y -50\nIF R7 scan\nSET Monster.Pos.Y 0\nSET Monster.Pos.X -17.7\nSET Monster.Pos.Z 0\nSET NavA.Pos.Z 0\nSET NavB.Pos.Z 0\nSET NavC.Pos.Z NavTime.Pos.X\nLABEL scan\nSET Player.SelPart 0\nSET R0 0\nSET R5 100000\nSET Target.Pos.X 0\nLABEL players\nSET Player.SelIndex R0\nNOT R7 Player.Valid\nIF R7 next\nIF Player.Var1 next\nIF Player.Var3 next\nADD R6 Player.Id 1')
for loot in ['LootA','LootB','LootC']:g.emit(f'EQUAL R7 {loot}.Pos.Y R6\nIF R7 next')
g.emit('SUB R1 Player.Pos.X Monster.Pos.X\nSUB R2 Player.Pos.Z Monster.Pos.Z\nMUL R1 R1 R1\nMUL R2 R2 R2\nADD R1 R1 R2\nLESS R7 R1 R5\nNOT R7 R7\nIF R7 next\nSET R5 R1\nSET Target.Pos.X R6\nSET Target.Pos.Y Player.Pos.X\nSET Target.Pos.Z Player.Pos.Z\nLABEL next\nADD R0 R0 1\nLESS R7 R0 Player.Count\nIF R7 players\nNOT R7 Target.Pos.X\nIF R7 wait\nSET Waypoint.Pos.X Target.Pos.Y\nSET Waypoint.Pos.Z Target.Pos.Z')
# Native ground-plane visibility, persistent corner detours and swept step checks.
navigation.emit_route(g,nav)
g.emit('SUB R0 Target.Pos.X 1\nSET Player.SelId R0\nNOT R7 Player.Valid\nIF R7 wait\nIF Player.Var1 wait\nIF Player.Var3 wait\nNOT R7 Clock.Pos.X\nIF R7 wait\nADD R6 Player.Id 1')
for loot in ['LootA','LootB','LootC']:g.emit(f'EQUAL R7 {loot}.Pos.Y R6\nIF R7 wait')
g.emit('SUB R1 Player.Pos.X Monster.Pos.X\nSUB R2 Player.Pos.Z Monster.Pos.Z\nMUL R1 R1 R1\nMUL R2 R2 R2\nADD R1 R1 R2\nGREATER R7 R1 0.65\nIF R7 wait')
navigation.emit_capture_guard(g,nav,'wait')
# Route/LOS evaluation may span native instruction slices. Revalidate the actual
# selected player and current hand immunity immediately before capture.
g.emit('SUB R0 Target.Pos.X 1\nSET Player.SelId R0\nNOT R7 Player.Valid\nIF R7 wait\nIF Player.Var1 wait\nIF Player.Var3 wait\nNOT R7 Clock.Pos.X\nIF R7 wait\nADD R6 Player.Id 1')
for loot in ['LootA','LootB','LootC']:g.emit(f'EQUAL R7 {loot}.Pos.Y R6\nIF R7 wait')
g.emit('SUB R1 Player.Pos.X Monster.Pos.X\nSUB R2 Player.Pos.Z Monster.Pos.Z\nMUL R1 R1 R1\nMUL R2 R2 R2\nADD R1 R1 R2\nGREATER R7 R1 0.65\nIF R7 wait\nGREATER R7 Player.Pos.Y 2.2\nIF R7 wait\nSET Player.Var1 1\nSET Player.Var2 0\nSET Player.Var3 0\nSET Player.Var4 0\nLABEL wait\nSLEEP 0\nGOTO loop')
# Gate authorization shared; escape is an intent consumed locally.
g=script('ExitController');g.player()
for n in ['KeyState','ExitState','Clock','Finish','ExitLabel','ExitReady']:g.bind(n)
for n in ['ExitUse','ExitOpen','Escape']:g.bind(n,'triggerActive')
g.emit('''LABEL loop
IF ExitState.Pos.X open
SET ExitLabel.Pos.Y 3.5
SET ExitReady.Pos.Y -100
SET Finish.Pos.Y -100
SET ExitOpen.Trg.Force 0
LESS R7 Clock.Pos.Y 5
IF R7 wait
IF ExitUse.Trg.Active touch
GOTO approach
LABEL touch
SET Player.SelId ExitUse.Trg.PlayerId
NOT R7 Player.Valid
IF R7 approach
IF Player.Var1 approach
ADD R0 Player.Id 1
EQUAL R7 R0 KeyState.Pos.Y
IF R7 unlock
LABEL approach
NOT R7 KeyState.Pos.Y
IF R7 wait
SUB R0 KeyState.Pos.Y 1
SET Player.SelId R0
NOT R7 Player.Valid
IF R7 wait
IF Player.Var1 wait
ABS R0 Player.Pos.X
GREATER R7 R0 2.3
IF R7 wait
LESS R7 Player.Pos.Z 27.7
IF R7 wait
GREATER R7 Player.Pos.Z 29.35
IF R7 wait
LESS R7 Player.Pos.Y 0
IF R7 wait
GREATER R7 Player.Pos.Y 3.2
IF R7 wait
LABEL unlock
SET ExitState.Pos.X 1
LABEL open
SET ExitLabel.Pos.Y -100
SET ExitReady.Pos.Y 3.5
SET Finish.Pos.Y 1.2
SET ExitOpen.Trg.Force 1
NOT R7 Escape.Trg.Active
IF R7 wait
SET Player.SelId Escape.Trg.PlayerId
NOT R7 Player.Valid
IF R7 wait
IF Player.Var1 wait
SUB R0 Player.Pos.X 0
SUB R1 Player.Pos.Y 1.2
SUB R2 Player.Pos.Z 35
MUL R0 R0 R0
MUL R1 R1 R1
MUL R2 R2 R2
ADD R0 R0 R1
ADD R0 R0 R2
GREATER R7 R0 1
IF R7 wait
SET Player.Var1 2
SET Player.Var3 0
SET Player.Var2 0
LABEL wait
SLEEP 0
GOTO loop''')
# Every client handles only its selected LocalId: hiding, death, escape and reset.
g=script('LocalMovement');g.player();g.bind('Round')
g.emit('LABEL loop\nSET Player.SelPart 0\nSET Player.SelId Player.LocalId\nNOT R7 Player.Valid\nIF R7 wait\nEQUAL R7 Player.Var5 Round.Pos.Z\nIF R7 status\nSET Player.Var5 Round.Pos.Z\nGREATER R7 Round.Pos.Z 1\nIF R7 revive\nLABEL status\nEQUAL R7 Player.Var1 1\nIF R7 dead\nEQUAL R7 Player.Var1 2\nIF R7 escaped\nIF Player.Var2 movehide\nGOTO wait\nLABEL movehide')
for h in HIDES:
 i=h['id'];enter=g.label('enter');leave=g.label('leave');next_=g.label('next')
 g.emit(f'EQUAL R7 Player.Var2 {i}\nIF R7 {enter}\nEQUAL R7 Player.Var2 {-i}\nIF R7 {leave}\nGOTO {next_}\nLABEL {enter}')
 g.teleport(*h['position']);g.emit(f'SET Player.Var4 {i}\nSET Player.Var2 0\nGOTO wait\nLABEL {leave}');g.teleport(*h['exit']);g.emit(f'SET Player.Var4 0\nSET Player.Var2 0\nGOTO wait\nLABEL {next_}')
g.emit('GOTO wait\nLABEL dead\nLESS R7 Player.Pos.Y 0\nIF R7 spectate\nGREATER R7 Player.Pos.Y 3.1\nIF R7 spectate\nSUB R0 Player.Pos.X 24\nABS R0 R0\nGREATER R7 R0 2.2\nIF R7 spectate\nABS R0 Player.Pos.Z\nGREATER R7 R0 25.5\nIF R7 spectate\nGOTO wait\nLABEL spectate');g.teleport(24,.1,0)
g.emit('GOTO wait\nLABEL escaped\nSET Player.Var2 0\nGOTO wait\nLABEL revive\nSET Player.Var1 0\nSET Player.Var2 0\nSET Player.Var3 0\nSET Player.Var4 0\nMOD R0 Player.Id 10\nMOD R1 R0 2\nMUL R1 R1 1.4\nSUB R1 R1 0.7\nMUL R0 R0 0.2\nSUB R0 -27 R0');g.teleport('R1',.1,'R0')
g.emit('LABEL wait\nSLEEP 0\nGOTO loop')
# Assign fresh depth-first object IDs after every model/controller is final.
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
for d in DOORS:target_anim(d['use'],d['name'],d['animation'])
for h in HIDES:
 clip=next(d['animation'] for d in DOORS if d['name']==h['door'])
 target_anim(h['open'],h['door'],clip,1);target_anim(h['close'],h['door'],clip,5)
 for event in ['use','leave']:names[h[event]]['levelNodeTrigger']['triggerTargets']=[{'mode':0,'triggerTargetGASM':dict(objectID=ids[f"Hide{h['id']}"],mode=1)}]
target_anim('ExitOpen','ExitDoor','GateLift',1)
for ev,controller in [('ExitUse','ExitController'),('Escape','ExitController'),('KeyUse','KeyInventory')]:names[ev]['levelNodeTrigger']['triggerTargets']=[{'mode':0,'triggerTargetGASM':dict(objectID=ids[controller],mode=1)}]
names['ResetAnimations']['levelNodeTrigger']['triggerTargets']=[{'mode':0,'triggerTargetAnimation':dict(objectID=ids[d['name']],animationName=d['animation'],loop=False,reverse=False,mode=5)} for d in DOORS+[dict(name='ExitDoor',animation='GateLift')]]
level=dict(formatVersion=25,title='Parking Lot Horror [Exit guidance 3]',creators='Ernesto',description='60 covered parking spaces, nine vehicles, three immunity gems. Two sliding minivans offer safe hiding. Survive five 60-second skeleton hunts separated by 60-second calm phases. Hold gems for protection. Key at gate after hunt five. Captured players spectate. Experimental: Quest multiplayer validation required.',tags=['horror','survival'],maxCheckpointCount=0,defaultSpawnPointID=ids['Start'],showReplays=False,disablePracticeMode=True,unlisted=True,ambienceSettings=dict(skyZenithColor=C(.06,.09,.12),skyHorizonColor=C(.1,.13,.15),sunAltitude=30,sunAzimuth=0,sunSize=0,fogDensity=0,useAdvancedSunSettings=True,sunBrightness=.15,ambientColor=C(.7,.8,.85),ambientBrightness=.65),levelNodes=N)
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
(ROOT/'dist/parking-lot-horror.json').write_text(json.dumps(level,indent=2))
message=ParseDict(level,pb.Level());binary=message.SerializeToString();(ROOT/'dist/parking-lot-horror.level').write_bytes(binary)
assert pb.Level.FromString(binary)==message
for nm,s in scripts.items():(ROOT/'src'/f'{nm}.gasm').write_text(s)
manifest.update(nodeCount=counter+len(allg),codeBlocks=len(allg),instructions={g.name:len(g.program['instructions']) for g in allg},complexity=level['complexity'],ids=ids)
(ROOT/'docs/manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:v for k,v in manifest.items() if k in ['nodeCount','codeBlocks','complexity','revision']}))
