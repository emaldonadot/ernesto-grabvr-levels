"""Build Office After Hours using GRAB Tools format 25 and native GASM."""
import json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor'))
import grab_pb2 as pb
from google.protobuf.json_format import ParseDict
V=lambda x=0,y=0,z=0:dict(x=x,y=y,z=z)
Q=lambda yaw=0:dict(x=0,y=math.sin(math.radians(yaw/2)),z=0,w=math.cos(math.radians(yaw/2)))
C=lambda r,g,b,a=1:dict(r=r,g=g,b=b,a=a)
N=[]; names={}; scripts={}; manifest={'rooms':[],'status':'experimental-native-build','formatVersion':25,'targetPlayers':10}
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
# architecture: hall x=-2..2, offices x=2..8 / -8..-2; five 6m bays
box('Floor',(0,-.15,16),(16.4,.3,36),(.14,.17,.19))
box('Ceiling',(0,3.6,16),(16.4,.2,36),(.31,.34,.34))
for side in [-1,1]:
    box(f'OuterWall{side}',(side*8.1,1.7,16),(.2,3.4,36),(.34,.38,.37))
    for z in [-2,4,10,16,22,28,34]:
        if z in [4,10,16,22,28]:box(f'Partition{side}_{z}',(side*5,1.7,z),(6,.0+3.4,.16),(.38,.41,.39))
for z in [-2,34]:box(f'End{z}',(0,1.7,z),(16.4,3.4,.2),(.32,.37,.36))
# exit wall at z32, with doorway and escape chamber behind
for x in [-5,5]:box(f'ExitWall{x}',(x,1.7,32),(7.5,3.4,.18),(.3,.37,.35))
box('ExitLintel',(0,3.05,32),(2.5,.7,.2),(.3,.37,.35))
group('ExitDoor',(0,0,32),[part((0,1.25,0),(2.4,2.5,.16),(.07,.2,.18)),part((.8,1.1,-.12),(.12,.12,.12),(.8,.6,.12))])
trigger('ExitUse',(0,1.2,31.5),(.8,.6,.6))
add('Finish','levelNodeFinish',{'position':V(100,-49,0),'radius':.65})
box('FinishPlatform',(100,-50,0),(4,.2,4),(.1,.3,.25))
trigger('Escape',(0,1.3,33),(2.3,2.5,1))
names['Escape']['levelNodeTrigger']['triggerSources']=[{'triggerSourceBasic':{'type':1}}]
add('Start','levelNodeStart',dict(position=V(0,.2,-.5),rotation=Q(),radius=.5,name='Entry',isHidden=False))
sign('Title','AFTER HOURS\nSURVIVE FIVE HUNTS — 10 PLAYERS',(0,2.6,1),.65,180)
sign('Rules','Touch handles to open doors and drawers.\nTouch blue pads to hide / leave. One player per spot.\nFind a gem for immunity. The fog returns every minute.\nAfter five hunts: find the key and touch the exit lock.\nDEAD players spectate only.',(0,1.7,-1.85),.42)
sign('ExitLabel','EXIT — KEY REQUIRED',(0,2.85,31.85),.5,180,c=(.4,1,.65))
for z in [1,7,13,19,25,30]:
    box(f'HallLight{z}',(0,3.44,z),(1.4,.06,.5),(.78,.92,.88),isNeon=True)
    box(f'Runner{z}',(0,.015,z),(1.1,.02,4),(.12,.27,.27))
for side in [-1,1]:
 for bay in range(5):
    i=bay+1 if side==-1 else bay+6;z=1+6*bay;x=side*5
    # corridor-facing wall with 1.5m door opening centered on each bay
    for dz in [-1.875,1.875]:box(f'Wall{i}_{dz}',(side*2,1.7,z+dz),(.16,3.4,2.25),(.4,.44,.41))
    box(f'Header{i}',(side*2,3,z),(.18,.8,1.5),(.4,.44,.41))
    # vertically sliding doors: reliable swept clearance; touch either side
    group(f'Door{i}',(side*2,0,z),[part((0,1.25,0),(.16,2.5,1.45),(.15,.23,.23)),part((-side*.13,1.15,.42),(.12,.13,.24),(.7,.65,.37))])
    trigger(f'DoorUse{i}',(side*2,1.15,z+.42),(.85,.4,.5))
    sign(f'Number{i}',f'OFFICE {i:02}',(side*1.88,2.65,z),.28,90 if side==-1 else -90)
    # desk open knee space; drawer is a five-sided tray left of central hide space
    deskx=x;deskz=z+1.15
    box(f'DeskTop{i}',(deskx,1.3,deskz),(2.8,.13,1.2),(.43,.26,.14))
    for dx in [-1.28,1.28]:
      for dz in [-.48,.48]:box(f'DeskLeg{i}_{dx}_{dz}',(deskx+dx,.62,deskz+dz),(.11,1.24,.11),(.2,.22,.22))
    box(f'DeskBack{i}',(deskx,1.02,deskz+.52),(2.65,.45,.08),(.32,.2,.12))
    drawerx=deskx-.85
    children=[part((0,0,0),(.75,.07,.86),(.28,.18,.1)),part((0,.14,-.43),(.8,.35,.08),(.45,.27,.13)),part((0,.12,.4),(.75,.25,.06),(.28,.18,.1)),part((-.37,.12,0),(.06,.25,.8),(.28,.18,.1)),part((.37,.12,0),(.06,.25,.8),(.28,.18,.1)),part((0,.15,-.51),(.26,.06,.08),(.65,.7,.7))]
    group(f'Drawer{i}',(drawerx,.98,deskz),children)
    # Enclosure conceals the gem until the tray is pulled out.
    for ox in [-.44,.44]:box(f'DrawerHousing{i}_{ox}',(drawerx+ox,1.03,deskz),(.07,.43,1),(.32,.21,.12))
    box(f'DrawerHousingBack{i}',(drawerx,1.03,deskz+.49),(.9,.43,.07),(.32,.21,.12))
    trigger(f'DrawerUse{i}',(drawerx,1.08,deskz-.58),(.65,.4,.42))
    trigger(f'LootUse{i}',(drawerx,1.14,deskz-.68),(.5,.35,.45))
    # closed closet shell, physical open front with removable opaque door panel
    cx=x+side*1.8;cz=z-1.6
    for dx in [-.66,.66]:box(f'ClosetSide{i}_{dx}',(cx+dx,1.35,cz),(.1,2.7,1.25),(.22,.27,.26))
    box(f'ClosetBack{i}',(cx,1.35,cz+.6),(1.4,2.7,.1),(.19,.24,.23))
    box(f'ClosetTop{i}',(cx,2.66,cz),(1.4,.1,1.3),(.24,.28,.26))
    group(f'ClosetDoor{i}',(cx,0,cz-.62),[part((0,1.32,0),(1.29,2.6,.08),(.27,.32,.29)),part((.43,1.3,-.09),(.06,.3,.09),(.7,.69,.5))])
    box(f'HidePad{i}',(cx,1.2,cz-.76),(.25,.2,.06),(.12,.6,.7),isNeon=True)
    trigger(f'ClosetUse{i}',(cx,1.2,cz-.74),(.5,.5,.45))
    trigger(f'ClosetLeave{i}',(cx,1.3,cz-.45),(.5,.5,.35))
    box(f'DeskPad{i}',(deskx+.5,1.32,deskz-.35),(.23,.04,.23),(.12,.6,.7),isNeon=True)
    trigger(f'DeskUse{i}',(deskx+.5,1.32,deskz-.35),(.3,.3,.3))
    trigger(f'DeskLeave{i}',(deskx+.5,.55,deskz-.35),(.45,.4,.45))
    # chair behind desk (towards positive Z)
    box(f'ChairSeat{i}',(deskx,.55,deskz+1.2),(.65,.12,.65),(.07,.12,.14))
    box(f'ChairBack{i}',(deskx,.95,deskz+1.48),(.65,.8,.1),(.08,.15,.17))
    box(f'ChairStem{i}',(deskx,.25,deskz+1.2),(.1,.5,.1),(.4,.45,.44))
    box(f'ChairBase{i}',(deskx,.08,deskz+1.2),(.65,.08,.65),(.22,.27,.27))
    # screen and paper / office fixture
    box(f'Monitor{i}',(deskx+.5,1.7,deskz+.3),(.8,.48,.08),(.04,.08,.1))
    box(f'Screen{i}',(deskx+.5,1.7,deskz+.25),(.7,.37,.015),(.05,.21,.25),isNeon=True)
    box(f'MonitorStand{i}',(deskx+.5,1.45,deskz+.3),(.1,.25,.12),(.2,.23,.22))
    box(f'Paper{i}',(deskx+.9,1.38,deskz-.22),(.35,.012,.32),(.7,.7,.62))
    box(f'RoomLight{i}',(x,3.44,z),(1.6,.06,.45),(.7,.82,.76),isNeon=True)
    state(f'Room{i}');state(f'Spots{i}');state(f'Edge{i}');state(f'EdgeB{i}')
    manifest['rooms'].append(dict(id=i,x=x,z=z,desk=[deskx,.55,deskz],closet=[cx,1.35,cz],drawer=[drawerx,1.15,deskz],door=f'Door{i}'))
# Creature: hovering shadow with glowing eyes and long arms, no lava (scripted immunity)
parts=[part((0,1.3,0),(.65,1.5,.42),(.015,.025,.03)),part((0,2.2,0),(.65,.65,.55),(.015,.025,.03)),part((-.5,1.05,0),(.18,1.6,.18),(.02,.03,.035)),part((.5,1.05,0),(.18,1.6,.18),(.02,.03,.035))]
for x in [-.16,.16]:parts.append(part((x,2.23,-.29),(.13,.08,.025),(.95,.16,.05),isNeon=True))
group('Monster',(0,-100,0),parts)
for name in ['Clock','LootA','LootB','LootC','KeyState','Target','Waypoint','ExitState']:state(name)
for j,c in enumerate([(.1,1,.8),(.5,.4,1),(1,.3,.7)],1):
    child=part((0,0,0),(.19,.3,.19),c,isNeon=True,isPassable=True)
    child['levelNodeStatic']['shape']=1006
    group(f'Gem{j}',(0,-100,0),[child])
group('Key',(0,-100,0),[part((0,0,0),(.12,.12,.12),(.9,.7,.13),isNeon=True,isPassable=True),part((.14,0,0),(.25,.045,.045),(.9,.7,.13),isNeon=True,isPassable=True)])
# overhead dead markers: 16 concurrent display slots; gameplay loops use actual Player.Count
for n in range(16):sign(f'Dead{n}','[ X ]\nDEAD',(0,-100,0),.24,c=(1,.2,.2))
# Atmosphere triggers forced by clock. Empty source list: no automatic activation.
for nm,fog,brightness in [('FogOn',.075,.35),('FogOff',.002,.7)]:
 add(nm,'levelNodeTrigger',dict(shape=1000,position=V(0,-200,0),scale=V(.1,.1,.1),rotation=Q(),isShared=True,triggerSources=[],triggerTargets=[{'mode':0,'triggerTargetAmbience':dict(skyColor0=C(.08,.12,.14),skyColor1=C(.12,.16,.17),sunAltitude=30,sunAzimuth=0,sunSize=0,fogDensity=fog,changeDuration=1.5,useAdvancedSunSettings=True,sunBrightness=.2,ambientColor=C(.7,.8,.8),ambientBrightness=brightness)}]))
# GASM builder: follows GRAB Tools component ordering, 1-based depth-first object ids.
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
    specs={'position':[(f'{alias}.Pos.{a}',7) for a in 'XYZ'],'rotation':[(f'{alias}.Rot.{a}',7) for a in 'XYZ'],'triggerActive':[(f'{alias}.Trg.{a}',t) for a,t in [('Active',0),('PlayerId',0),('Force',7),('Part',0)]],
    'player':[(f'Player.{a}',t) for a,t in [('SelIndex',1),('SelId',1),('SelPart',1),('Control',1),('Count',0),('Valid',0),('Id',0),('Pos.X',0),('Pos.Y',0),('Pos.Z',0),('Rot.X',0),('Rot.Y',0),('Rot.Z',0),('Name',0),('Col.Sel',1),('Col.R',0),('Col.G',0),('Col.B',0),('LocalId',0),('Vel.X',7),('Vel.Y',7),('Vel.Z',7),('Tel.Pos.X',1),('Tel.Pos.Y',1),('Tel.Pos.Z',1),('Tel.Rot.Y',1),('Tel.Apply',1)]],
    'playerVariables':[(f'Player.Var{i}',7) for i in range(1,6)]}
    conn=next((c for c in self.con if c['target']==name),None)
    if conn is None:conn={'target':name,'name':alias,'type':1 if name=='@player' else 0,'properties':[]};self.con.append(conn)
    comps=[]
    for rn,t in specs[prop]:
       key={0:'inputRegisters',1:'outputRegisters',7:'inoutRegisters'}[t];idx=len(self.program[key]);self.program[key].append({'name':rn});self.reg[rn]=(t,idx)
       component={'inputRegisterIndex':-1,'outputRegisterIndex':-1,'inoutRegisterIndex':-1};component[{0:'inputRegisterIndex',1:'outputRegisterIndex',7:'inoutRegisterIndex'}[t]]=idx;comps.append(component)
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
    return dict(position=V(0,-150,0),rotation=Q(),scale=V(1,1,1),program=p,connections=cons,startActive=True,isShared=True)
allg=[]
def script(name):g=G(name);allg.append(g);return g
# clock: state Clock.Pos.X=attack 0/1, Y=completed attacks, Z=elapsed seconds.
g=script('RoundClock')
for n in ['Clock','KeyState','LootA','LootB','LootC']:g.bind(n)
for n in ['FogOn','FogOff']:g.bind(n,'triggerActive')
g.emit('SET Clock.Pos.X 0\nSET Clock.Pos.Y 0\nSET Clock.Pos.Z 0\nSET KeyState.Pos.X 0\nSET KeyState.Pos.Y 0\nSET KeyState.Pos.Z 0\nGOTO relocate\nLABEL loop\nADD Clock.Pos.Z Clock.Pos.Z DeltaTime\nLESS R7 Clock.Pos.Z 60\nIF R7 wait\nSUB Clock.Pos.Z Clock.Pos.Z 60\nIF Clock.Pos.X end_attack\nSET Clock.Pos.X 1\nSET FogOn.Trg.Force 1\nSET FogOff.Trg.Force 0\nGOTO wait\nLABEL end_attack\nSET Clock.Pos.X 0\nADD Clock.Pos.Y Clock.Pos.Y 1\nSET FogOn.Trg.Force 0\nSET FogOff.Trg.Force 1\nLESS R7 Clock.Pos.Y 5\nIF R7 relocate\nIF KeyState.Pos.Z relocate\nSET KeyState.Pos.Z 1\nRAND KeyState.Pos.X 10\nADD KeyState.Pos.X KeyState.Pos.X 1\nLABEL relocate\nRAND LootA.Pos.X 10\nADD LootA.Pos.X LootA.Pos.X 1\nLABEL rollB\nRAND LootB.Pos.X 10\nADD LootB.Pos.X LootB.Pos.X 1\nEQUAL R7 LootA.Pos.X LootB.Pos.X\nIF R7 rollB\nLABEL rollC\nRAND LootC.Pos.X 10\nADD LootC.Pos.X LootC.Pos.X 1\nEQUAL R7 LootA.Pos.X LootC.Pos.X\nIF R7 rollC\nEQUAL R7 LootB.Pos.X LootC.Pos.X\nIF R7 rollC\nSET LootA.Pos.Y 0\nSET LootB.Pos.Y 0\nSET LootC.Pos.Y 0\nLABEL wait\nSLEEP 0\nGOTO loop')
# ownership at gem state is authoritative; no per-player immunity variable needed.
for r in manifest['rooms']:
 i=r['id'];x=r['x'];z=r['z'];cx,_,cz=r['closet'];dx,_,dz=r['desk']
 g=script(f'Office{i:02}')
 g.player()
 for n in [f'Room{i}',f'Spots{i}',f'Edge{i}',f'EdgeB{i}',f'Door{i}',f'Drawer{i}',f'ClosetDoor{i}','Clock','Monster','LootA','LootB','LootC','KeyState']:g.bind(n)
 for n in ['DoorUse','DrawerUse','LootUse','ClosetUse','ClosetLeave','DeskUse','DeskLeave']:g.bind(f'{n}{i}','triggerActive')
 g.emit(f'LABEL loop\nSET Door{i}.Pos.Y 0\nMUL Door{i}.Pos.Y Room{i}.Pos.X 2.7\nMUL R0 Room{i}.Pos.Y -0.7\nADD Drawer{i}.Pos.Z R0 {dz}\nSET ClosetDoor{i}.Pos.Y 0')
 # one edge-latch for each event. memory stores active not player id; player-specific filtering after edge.
 events=[('DoorUse',f'Edge{i}.Pos.X'),('DrawerUse',f'Edge{i}.Pos.Y'),('LootUse',f'Edge{i}.Pos.Z'),('ClosetUse',f'EdgeB{i}.Pos.X'),('DeskUse',f'EdgeB{i}.Pos.Y')]
 for ev,latch in events:
    t=f'{ev}{i}';skip=g.label('evskip');g.emit(f'EQUAL R7 {t}.Trg.Active {latch}\nIF R7 {skip}\nSET {latch} {t}.Trg.Active\nNOT R7 {t}.Trg.Active\nIF R7 {skip}\nSET Player.SelId {t}.Trg.PlayerId\nNOT R7 Player.Valid\nIF R7 {skip}\nIF Player.Var1 {skip}')
    if ev=='DoorUse':g.emit(f'NOT Room{i}.Pos.X Room{i}.Pos.X')
    elif ev=='DrawerUse':g.emit(f'NOT Room{i}.Pos.Y Room{i}.Pos.Y')
    elif ev=='LootUse':
      g.emit(f'NOT R7 Room{i}.Pos.Y\nIF R7 {skip}\nADD R0 Player.Id 1')
      for loot in ['LootA','LootB','LootC']:
        end=g.label('lootnext');g.emit(f'IF {loot}.Pos.Y {end}\nEQUAL R7 {loot}.Pos.X {i}\nNOT R7 R7\nIF R7 {end}')
        for other in ['LootA','LootB','LootC']:
          g.emit(f'EQUAL R7 {other}.Pos.Y R0\nIF R7 {end}')
        g.emit(f'SET {loot}.Pos.Y R0\nSET {loot}.Pos.X 0');g.end(end)
      end=g.label('keynext');g.emit(f'IF KeyState.Pos.Y {end}\nEQUAL R7 KeyState.Pos.X {i}\nNOT R7 R7\nIF R7 {end}\nSET KeyState.Pos.Y R0\nSET KeyState.Pos.X 0');g.end(end)
    else:
      closet=ev=='ClosetUse';occ=f'Spots{i}.Pos.'+('X' if closet else 'Y');spot=i if closet else i+10
      leave=g.label('leave');done=g.label('hideend')
      g.emit(f'ADD R0 Player.Id 1\nEQUAL R7 {occ} R0\nIF R7 {leave}\nIF {occ} {done}\nIF Player.Var3 {done}\nSET {occ} R0\nSET Player.Var3 {spot}\nSET Player.Var4 0')
      # witnessed hiding: same office rectangle, or hall opposite open door.
      seen=g.label('seen');unseen=g.label('unseen')
      g.emit(f'NOT R7 Clock.Pos.X\nIF R7 {unseen}\nSUB R1 Monster.Pos.X {x}\nABS R1 R1\nLESS R7 R1 2.8\nIF R7 {seen}\nNOT R7 Room{i}.Pos.X\nIF R7 {unseen}\nABS R1 Monster.Pos.X\nGREATER R7 R1 2.1\nIF R7 {unseen}\nSUB R1 Monster.Pos.Z {z}\nABS R1 R1\nGREATER R7 R1 1.5\nIF R7 {unseen}\nLABEL {seen}\nSUB R1 Monster.Pos.Z {z}\nABS R1 R1\nGREATER R7 R1 3\nIF R7 {unseen}\nSET Player.Var4 1\nLABEL {unseen}')
      if closet:g.teleport(cx,1.2,cz)
      else:g.teleport(dx+.5,.55,dz-.1)
      g.emit(f'GOTO {done}\nLABEL {leave}\nSET {occ} 0\nSET Player.Var3 0\nSET Player.Var4 0')
      if closet:g.teleport(cx,1.4,cz-1.1)
      else:g.teleport(dx+.5,1.4,dz-1.05)
      g.end(done)
    g.end(skip)
 # inside leave buttons use separate occupancy check and same main latch: use an independent wait debounce register
 g.emit('SUB R6 R6 DeltaTime\nGREATER R7 R6 0\nIF R7 maintain')
 for ev,axis,spot,tx,ty,tz in [('ClosetLeave','X',i,cx,1.4,cz-1.1),('DeskLeave','Y',i+10,dx+.5,1.4,dz-1.05)]:
    skip=g.label();t=f'{ev}{i}';g.emit(f'NOT R7 {t}.Trg.Active\nIF R7 {skip}\nSET Player.SelId {t}.Trg.PlayerId\nIF Player.Var1 {skip}\nEQUAL R7 Player.Var3 {spot}\nNOT R7 R7\nIF R7 {skip}\nSET Spots{i}.Pos.{axis} 0\nSET Player.Var3 0\nSET Player.Var4 0\nSET R6 0.8');g.teleport(tx,ty,tz);g.end(skip)
 g.emit('LABEL maintain')
 # release hidden spots if owner died, disconnected, or left by walking/crouching out
 for axis,spot in [('X',i),('Y',i+10)]:
    end=g.label();clear=g.label();g.emit(f'NOT R7 Spots{i}.Pos.{axis}\nIF R7 {end}\nSUB R0 Spots{i}.Pos.{axis} 1\nSET Player.SelId R0\nNOT R7 Player.Valid\nIF R7 {clear}\nIF Player.Var1 {clear}\nEQUAL R7 Player.Var3 {spot}\nNOT R7 R7\nIF R7 {clear}')
    hx,hz,limx,limz,maxy=(cx,cz,.62,.6,2.5) if axis=='X' else (dx+.5,dz-.1,.85,.6,1.12)
    g.emit(f'SUB R1 Player.Pos.X {hx}\nABS R1 R1\nGREATER R7 R1 {limx}\nIF R7 {clear}\nSUB R1 Player.Pos.Z {hz}\nABS R1 R1\nGREATER R7 R1 {limz}\nIF R7 {clear}\nGREATER R7 Player.Pos.Y {maxy}\nIF R7 {clear}\nGOTO {end}\nLABEL {clear}\nSET Spots{i}.Pos.{axis} 0\nSET Player.Var3 0\nSET Player.Var4 0\nLABEL {end}')
 g.emit('SLEEP 0\nGOTO loop')
# visuals for three gems and key, follows owner or drawer; missing owner causes re-roll.
for index,loot in enumerate(['LootA','LootB','LootC','KeyState']):
 vis=f'Gem{index+1}' if index<3 else 'Key'
 g=script(f'{vis}Inventory');g.player();g.bind(loot);g.bind(vis)
 for i in range(1,11):g.bind(f'Drawer{i}')
 g.emit(f'LABEL loop\nSET {vis}.Pos.Y -100\nIF {loot}.Pos.Y owned\nNOT R7 {loot}.Pos.X\nIF R7 wait')
 for r in manifest['rooms']:
   i=r['id'];end=g.skip('EQUAL',f'{loot}.Pos.X',i) # skip helper jumps on true; use direct branch for matches below
   # replace comparison to skip on unequal
   g.lines[-2:]=[f'EQUAL R7 {loot}.Pos.X {i}','NOT R7 R7',f'IF R7 {end}']
   g.emit(f'SET {vis}.Pos.X Drawer{i}.Pos.X\nADD {vis}.Pos.Y Drawer{i}.Pos.Y 0.17\nSET {vis}.Pos.Z Drawer{i}.Pos.Z\nGOTO wait');g.end(end)
 g.emit(f'GOTO wait\nLABEL owned\nSUB R0 {loot}.Pos.Y 1\nSET Player.SelId R0\nNOT R7 Player.Valid\nIF R7 lost\nIF Player.Var1 lost\nSET {vis}.Pos.X Player.Pos.X\nADD {vis}.Pos.Y Player.Pos.Y 0.5\nSET {vis}.Pos.Z Player.Pos.Z\nGOTO wait\nLABEL lost\nSET {loot}.Pos.Y 0\nRAND {loot}.Pos.X 10\nADD {loot}.Pos.X {loot}.Pos.X 1\nLABEL wait\nSLEEP 0\nGOTO loop')
# Monster controller nearest eligible player. Pursuit moves via corridor/office doorway waypoints.
g=script('MonsterAI');g.player()
for n in ['Monster','Clock','Target','Waypoint','LootA','LootB','LootC']:g.bind(n)
for i in range(1,11):g.bind(f'Room{i}');g.bind(f'Door{i}')
g.emit('LABEL loop\nIF Clock.Pos.X hunting\nSET Monster.Pos.Y -100\nSET Target.Pos.X 0\nGOTO wait\nLABEL hunting\nGREATER R7 Monster.Pos.Y -50\nIF R7 scan\nSET Monster.Pos.Y 0\nRAND R0 2\nMUL Monster.Pos.Z R0 30\nSET Monster.Pos.X 0\nLABEL scan\nSET R0 0\nSET R5 100000\nSET Target.Pos.X 0\nLABEL players\nSET Player.SelIndex R0\nNOT R7 Player.Valid\nIF R7 next\nIF Player.Var1 next\nADD R6 Player.Id 1')
for loot in ['LootA','LootB','LootC']:g.emit(f'EQUAL R7 {loot}.Pos.Y R6\nIF R7 next')
g.emit('NOT R7 Player.Var3\nIF R7 candidate\nNOT R7 Player.Var4\nIF R7 next\nLABEL candidate\nSUB R1 Player.Pos.X Monster.Pos.X\nSUB R2 Player.Pos.Z Monster.Pos.Z\nMUL R1 R1 R1\nMUL R2 R2 R2\nADD R1 R1 R2\nLESS R7 R1 R5\nNOT R7 R7\nIF R7 next\nSET R5 R1\nSET Target.Pos.X R6\nSET Target.Pos.Y Player.Pos.X\nSET Target.Pos.Z Player.Pos.Z\nLABEL next\nADD R0 R0 1\nLESS R7 R0 Player.Count\nIF R7 players\nNOT R7 Target.Pos.X\nIF R7 wait\nSET Waypoint.Pos.X Target.Pos.Y\nSET Waypoint.Pos.Z Target.Pos.Z')
# Route from monster current room into corridor if target is outside its current room.
for r in manifest['rooms']:
 x,z,i=r['x'],r['z'],r['id'];skip=g.label('route');leave=g.label('leave')
 g.emit(f'SUB R1 Monster.Pos.X {x}\nABS R1 R1\nGREATER R7 R1 2.9\nIF R7 {skip}\nSUB R1 Monster.Pos.Z {z}\nABS R1 R1\nGREATER R7 R1 2.9\nIF R7 {skip}\nSUB R1 Target.Pos.Y {x}\nABS R1 R1\nGREATER R7 R1 2.9\nIF R7 {leave}\nSUB R1 Target.Pos.Z {z}\nABS R1 R1\nLESS R7 R1 2.9\nIF R7 route_done\nLABEL {leave}\nSET Room{i}.Pos.X 1\nSET Waypoint.Pos.X 0\nSET Waypoint.Pos.Z {z}\nSUB R1 Monster.Pos.Z {z}\nABS R1 R1\nLESS R7 R1 0.25\nIF R7 route_done\nSET Waypoint.Pos.X Monster.Pos.X\nGOTO route_done\nLABEL {skip}')
# Target in room: line up in hall, then enter via door. Monster opens office door.
for r in manifest['rooms']:
 x,z,i=r['x'],r['z'],r['id'];skip=g.label('enter');aligned=g.label('aligned')
 g.emit(f'SUB R1 Target.Pos.Y {x}\nABS R1 R1\nGREATER R7 R1 2.9\nIF R7 {skip}\nSUB R1 Target.Pos.Z {z}\nABS R1 R1\nGREATER R7 R1 2.9\nIF R7 {skip}\nSET Room{i}.Pos.X 1\nSET Waypoint.Pos.X 0\nSET Waypoint.Pos.Z {z}\nSUB R1 Monster.Pos.Z {z}\nABS R1 R1\nLESS R7 R1 0.25\nIF R7 {aligned}\nGOTO route_done\nLABEL {aligned}\nSET Waypoint.Pos.X {x}\nGOTO route_done\nLABEL {skip}')
g.emit('LABEL route_done\nSUB R1 Waypoint.Pos.X Monster.Pos.X\nSUB R2 Waypoint.Pos.Z Monster.Pos.Z\nMUL R3 R1 R1\nMUL R4 R2 R2\nADD R3 R3 R4\nSQRT R3 R3\nLESS R7 R3 0.02\nIF R7 catch\nMUL R4 DeltaTime 2.6\nGREATER R7 R4 R3\nNOT R7 R7\nIF R7 step\nSET R4 R3\nLABEL step\nDIV R4 R4 R3\nMUL R1 R1 R4\nMUL R2 R2 R4\nADD Monster.Pos.X Monster.Pos.X R1\nADD Monster.Pos.Z Monster.Pos.Z R2\nLABEL catch\nSUB R1 Target.Pos.Y Monster.Pos.X\nSUB R2 Target.Pos.Z Monster.Pos.Z\nMUL R1 R1 R1\nMUL R2 R2 R2\nADD R1 R1 R2\nGREATER R7 R1 0.65\nIF R7 wait\nSUB R0 Target.Pos.X 1\nSET Player.SelId R0\nSET Player.Var1 1\nSET Player.Var3 0\nSET Player.Var4 0\nLABEL wait\nSLEEP 0\nGOTO loop')
# exit: key holder unlocks for everyone; death remains a scripted spectator state.
g=script('ExitController');g.player()
for n in ['KeyState','ExitState','ExitDoor']:g.bind(n)
g.bind('ExitUse','triggerActive')
g.bind('Escape','triggerActive')
g.emit('LABEL loop\nIF ExitState.Pos.X open\nNOT R7 ExitUse.Trg.Active\nIF R7 wait\nSET Player.SelId ExitUse.Trg.PlayerId\nIF Player.Var1 wait\nADD R0 Player.Id 1\nEQUAL R7 R0 KeyState.Pos.Y\nNOT R7 R7\nIF R7 wait\nSET ExitState.Pos.X 1\nLABEL open\nSET ExitDoor.Pos.Y 3\nNOT R7 Escape.Trg.Active\nIF R7 wait\nSET Player.SelId Escape.Trg.PlayerId\nIF Player.Var1 wait\nSET Player.Var1 2')
g.teleport(100,-49,0)
g.emit('LABEL wait\nSLEEP 0\nGOTO loop')
# separate marker code per player index; spectators keep movement, no object physics to grab.
for i in range(16):
 g=script(f'DeadMarker{i:02}');g.player();g.bind(f'Dead{i}');g.emit(f'LABEL loop\nSET Dead{i}.Pos.Y -100\nSET Player.SelIndex {i}\nNOT R7 Player.Valid\nIF R7 wait\nEQUAL R7 Player.Var1 1\nNOT R7 R7\nIF R7 wait\nSET Dead{i}.Pos.X Player.Pos.X\nADD Dead{i}.Pos.Y Player.Pos.Y 0.65\nSET Dead{i}.Pos.Z Player.Pos.Z\nLABEL wait\nSLEEP 0\nGOTO loop')
# assign ids after native object hierarchy is final; code blocks added at end.
for g in allg:
 if g.name=='RoundClock':
  k=g.lines.index('ADD KeyState.Pos.X KeyState.Pos.X 1')+1
  g.lines.insert(k,'SET KeyState.Pos.Z KeyState.Pos.X')
 if g.name=='KeyInventory':
  k=g.lines.index('RAND KeyState.Pos.X 10')
  g.lines.insert(k,'LABEL rerollkey')
  k=g.lines.index('ADD KeyState.Pos.X KeyState.Pos.X 1')+1
  g.lines[k:k]=['EQUAL R7 KeyState.Pos.X KeyState.Pos.Z','IF R7 rerollkey','SET KeyState.Pos.Z KeyState.Pos.X']
 if g.name=='MonsterAI':
  k=g.lines.index('SET Player.Var1 1')
  guard=['NOT R7 Player.Valid','IF R7 wait','IF Player.Var1 wait','ADD R6 Player.Id 1']
  for loot in ['LootA','LootB','LootC']:guard.extend([f'EQUAL R7 {loot}.Pos.Y R6','IF R7 wait'])
  guard.extend(['NOT R7 Player.Var3','IF R7 kill','NOT R7 Player.Var4','IF R7 wait','LABEL kill'])
  g.lines[k:k]=guard
ids={};counter=0
reverse={id(v):k for k,v in names.items()}
def walk(nodes):
 global counter
 for n in nodes:
  counter+=1
  if id(n) in reverse:ids[reverse[id(n)]]=counter
  if 'levelNodeGroup' in n:walk(n['levelNodeGroup']['childNodes'])
walk(N)
for g in allg:add(g.name,'levelNodeGASM',g.compile(ids))
level=dict(formatVersion=25,title='Office After Hours [EXPERIMENTAL]',creators='Ernesto',description='10-player, 10-office cooperative horror prototype. 60s calm / 60s hunt. Find gems, hide, survive five hunts, find the exit key. Experimental native GASM: Quest validation required.',tags=['horror','survival'],maxCheckpointCount=0,defaultSpawnPointID=ids['Start'],showReplays=False,disablePracticeMode=True,unlisted=True,ambienceSettings=dict(skyZenithColor=C(.08,.12,.14),skyHorizonColor=C(.12,.16,.17),sunAltitude=30,sunAzimuth=0,sunSize=0,fogDensity=.002,useAdvancedSunSettings=True,sunBrightness=.2,ambientColor=C(.7,.8,.8),ambientBrightness=.7),levelNodes=N)
# Complexity conservatively counts GASM instructions as well as nodes; in-game re-save recalculates.
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
(ROOT/'dist/office-after-hours.json').write_text(json.dumps(level,indent=2))
message=ParseDict(level,pb.Level());binary=message.SerializeToString();(ROOT/'dist/office-after-hours.level').write_bytes(binary)
assert pb.Level.FromString(binary)==message
for nm,s in scripts.items():(ROOT/'src'/f'{nm}.gasm').write_text(s)
manifest.update(nodeCount=counter+len(allg),codeBlocks=len(allg),instructions={g.name:len(g.program['instructions']) for g in allg},complexity=level['complexity'],ids=ids)
(ROOT/'docs/manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:v for k,v in manifest.items() if k not in ['ids','rooms','instructions']}))
