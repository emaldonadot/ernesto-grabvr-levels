"""Decayed native zombie, guarded pursuit, and static footprint navigation.

Adapted from the repository parking navigation contract; no other game imports
this module. Visual colliders are passable; capture is exclusively scripted.
"""
import math

CLEARANCE=.38
STATE_NAMES=('NavA','NavB','NavC','NavTime','NavRect','NavRect2','NavRect3')

def prepare_navigation(layout):
    raw=[]
    for i, item in enumerate(layout.get('obstacles', [])):
        if isinstance(item, dict):
            raw.append(item)
        else:
            xmin,xmax,zmin,zmax=item
            raw.append(dict(name=f'Obstacle{i}',xmin=xmin,xmax=xmax,zmin=zmin,zmax=zmax))
    boxes=[]
    for o in raw:
        boxes.append(dict(name=o['name'],xmin=o['xmin']-CLEARANCE,xmax=o['xmax']+CLEARANCE,
                          zmin=o['zmin']-CLEARANCE,zmax=o['zmax']+CLEARANCE))
    # Overlapping clearances form one obstacle. This prevents alternating corner
    # detours through the seam between a vehicle and a supporting column.
    changed=True
    while changed:
        changed=False
        for i,a in enumerate(boxes):
            for j,b in enumerate(boxes[i+1:],i+1):
                if a['xmin']<=b['xmax'] and b['xmin']<=a['xmax'] and a['zmin']<=b['zmax'] and b['zmin']<=a['zmax']:
                    a=dict(name=a['name']+'+'+b['name'],xmin=min(a['xmin'],b['xmin']),xmax=max(a['xmax'],b['xmax']),zmin=min(a['zmin'],b['zmin']),zmax=max(a['zmax'],b['zmax']))
                    boxes[i]=a;boxes.pop(j);changed=True;break
            if changed:break
    return dict(kind='ground-visibility-and-corner-detours',clearance=CLEARANCE,obstacles=boxes,
                physicalVehicles=[],bounds=dict(xmin=-23.2,xmax=23.2,zmin=-27.2,zmax=27.2))

def _segment(g,a,b,rect,blocked,clear):
    """SAT for a segment against an open rectangle. R0..R7 scratch."""
    x,z=a;tx,tz=b
    # Axis tests cheaply reject the vast majority of garage obstacles.
    g.emit(f'GREATER R0 {x} {rect["xmin"]}\nNOT R0 R0\nGREATER R1 {tx} {rect["xmin"]}\nNOT R1 R1\nAND R7 R0 R1\nIF R7 {clear}\nLESS R0 {x} {rect["xmax"]}\nNOT R0 R0\nLESS R1 {tx} {rect["xmax"]}\nNOT R1 R1\nAND R7 R0 R1\nIF R7 {clear}\nGREATER R0 {z} {rect["zmin"]}\nNOT R0 R0\nGREATER R1 {tz} {rect["zmin"]}\nNOT R1 R1\nAND R7 R0 R1\nIF R7 {clear}\nLESS R0 {z} {rect["zmax"]}\nNOT R0 R0\nLESS R1 {tz} {rect["zmax"]}\nNOT R1 R1\nAND R7 R0 R1\nIF R7 {clear}')
    cx=rect.get('cx',(rect['xmin']+rect['xmax'])/2 if isinstance(rect['xmin'],(int,float)) else 0);cz=rect.get('cz',(rect['zmin']+rect['zmax'])/2 if isinstance(rect['zmin'],(int,float)) else 0)
    hx=rect.get('hx',(rect['xmax']-rect['xmin'])/2 if isinstance(rect['xmin'],(int,float)) else 0);hz=rect.get('hz',(rect['zmax']-rect['zmin'])/2 if isinstance(rect['zmin'],(int,float)) else 0)
    g.emit(f'SUB R2 {tx} {x}\nSUB R3 {tz} {z}\nSUB R0 {x} {cx}\nSUB R1 {z} {cz}\nMUL R0 R0 R3\nMUL R1 R1 R2\nSUB R0 R0 R1\nABS R0 R0\nABS R2 R2\nABS R3 R3\nMUL R2 R2 {hz}\nMUL R3 R3 {hx}\nADD R2 R2 R3\nSUB R2 R2 0.000001\nLESS R7 R0 R2\nIF R7 {blocked}\nGOTO {clear}')

def _visible(g,meta,a,b,blocked):
    for r in meta['obstacles']:
        nxt=g.label('visible')
        _segment(g,a,b,r,blocked,nxt);g.emit(f'LABEL {nxt}')

def emit_route(g,meta):
    """Emit after target selection; binds four declared empty-group states.

    NavA=(firstX,firstZ,phase), NavB=(secondX,secondZ,targetID),
    NavC=(stepX,stepZ,lastTime), NavTime.X=elapsed seconds.
    Continue at caller's catch label. Caller supplies wait/catch labels.
    """
    for n in STATE_NAMES:
        if not any(c['target']==n for c in g.con):g.bind(n)
    done=g.label('navready');direct=g.label('navdirect');plan=g.label('navplan');move=g.label('navmove')
    g.emit(f'NOT R7 Clock.Pos.X\nIF R7 navinactive\nSET Monster.Pos.Y 0\nEQUAL R7 NavB.Pos.Z Target.Pos.X\nIF R7 {done}\nSET NavA.Pos.Z 0\nSET NavB.Pos.Z Target.Pos.X\nLABEL {done}\nIF NavA.Pos.Z {move}\nSET Waypoint.Pos.X Target.Pos.Y\nSET Waypoint.Pos.Z Target.Pos.Z')
    # Choose the nearest intersected obstacle by centre distance; every actual
    # movement segment is independently checked against every footprint.
    # A stored detour is stable until its corners are reached.
    g.emit('SET NavRect3.Pos.Z 100000')
    for i,r in enumerate(meta['obstacles']):
        hit=g.label('navhit');nxt=g.label('navclear')
        _segment(g,('Monster.Pos.X','Monster.Pos.Z'),('Waypoint.Pos.X','Waypoint.Pos.Z'),r,hit,nxt)
        g.emit(f'LABEL {hit}\nSUB R0 Monster.Pos.X {(r["xmin"]+r["xmax"])/2}\nSUB R1 Monster.Pos.Z {(r["zmin"]+r["zmax"])/2}\nMUL R0 R0 R0\nMUL R1 R1 R1\nADD R0 R0 R1\nLESS R7 R0 NavRect3.Pos.Z\nNOT R7 R7\nIF R7 {nxt}\nSET NavRect3.Pos.Z R0\nSET NavRect.Pos.X {r["xmin"]}\nSET NavRect.Pos.Y {r["xmax"]}\nSET NavRect.Pos.Z {r["zmin"]}\nSET NavRect2.Pos.X {r["zmax"]}\nSET NavRect2.Pos.Y {(r["xmin"]+r["xmax"])/2}\nSET NavRect2.Pos.Z {(r["zmin"]+r["zmax"])/2}\nSET NavRect3.Pos.X {(r["xmax"]-r["xmin"])/2}\nSET NavRect3.Pos.Y {(r["zmax"]-r["zmin"])/2}\nLABEL {nxt}')
    g.emit(f'LESS R7 NavRect3.Pos.Z 99999\nIF R7 {plan}\nGOTO {direct}\nLABEL {plan}\nSET NavRect3.Pos.Z 100000')
    r=dict(xmin='NavRect.Pos.X',xmax='NavRect.Pos.Y',zmin='NavRect.Pos.Z',zmax='NavRect2.Pos.X',cx='NavRect2.Pos.Y',cz='NavRect2.Pos.Z',hx='NavRect3.Pos.X',hz='NavRect3.Pos.Y')
    corners=[(r['xmin'],r['zmin']),(r['xmax'],r['zmin']),(r['xmax'],r['zmax']),(r['xmin'],r['zmax'])]
    for j in range(4):
        for delta in (-1,1):
            a=corners[j];b=corners[(j+delta)%4];skip=g.label('candidate');ok=g.label('candidateok');ok2=g.label('candidateok')
            _segment(g,('Monster.Pos.X','Monster.Pos.Z'),a,r,skip,ok);g.emit(f'LABEL {ok}')
            _segment(g,b,('Target.Pos.Y','Target.Pos.Z'),r,skip,ok2);g.emit(f'LABEL {ok2}')
            g.emit(f'SUB R0 Monster.Pos.X {a[0]}\nSUB R1 Monster.Pos.Z {a[1]}\nMUL R0 R0 R0\nMUL R1 R1 R1\nADD R0 R0 R1\nSQRT R0 R0\nSUB R1 Target.Pos.Y {b[0]}\nSUB R2 Target.Pos.Z {b[1]}\nMUL R1 R1 R1\nMUL R2 R2 R2\nADD R1 R1 R2\nSQRT R1 R1\nADD R0 R0 R1\nSUB R1 {a[0]} {b[0]}\nABS R1 R1\nSUB R2 {a[1]} {b[1]}\nABS R2 R2\nADD R0 R0 R1\nADD R0 R0 R2\nLESS R7 R0 NavRect3.Pos.Z\nNOT R7 R7\nIF R7 {skip}\nSET NavRect3.Pos.Z R0\nSET NavA.Pos.X {a[0]}\nSET NavA.Pos.Y {a[1]}\nSET NavB.Pos.X {b[0]}\nSET NavB.Pos.Y {b[1]}\nLABEL {skip}')
    g.emit(f'GREATER R7 NavRect3.Pos.Z 99999\nIF R7 wait\nSET NavA.Pos.Z 1\nGOTO {move}')
    g.emit(f'GOTO wait\nLABEL {move}\nSET Waypoint.Pos.X NavA.Pos.X\nSET Waypoint.Pos.Z NavA.Pos.Y\nSUB R0 Monster.Pos.X Waypoint.Pos.X\nSUB R1 Monster.Pos.Z Waypoint.Pos.Z\nMUL R0 R0 R0\nMUL R1 R1 R1\nADD R0 R0 R1\nGREATER R7 R0 0.00000001\nIF R7 {direct}\nEQUAL R7 NavA.Pos.Z 1\nNOT R7 R7\nIF R7 {done}end\nSET NavA.Pos.X NavB.Pos.X\nSET NavA.Pos.Y NavB.Pos.Y\nSET NavA.Pos.Z 2\nGOTO wait\nLABEL {done}end\nSET NavA.Pos.Z 0\nGOTO wait\nLABEL {direct}')
    # Use elapsed wall-clock from an inexpensive independent native block. Route
    # selection can exceed one VM instruction slice without reducing walk speed.
    g.emit('SUB R4 NavTime.Pos.X NavC.Pos.Z\nSET NavC.Pos.Z NavTime.Pos.X\nLESS R7 R4 0\nIF R7 wait\nGREATER R7 R4 0.12')
    cap=g.label('cap');step=g.label('step')
    g.emit(f'IF R7 {cap}\nGOTO {step}\nLABEL {cap}\nSET R4 0.12\nLABEL {step}\nMUL R4 R4 4.1\nSUB R1 Waypoint.Pos.X Monster.Pos.X\nSUB R2 Waypoint.Pos.Z Monster.Pos.Z\nMUL R3 R1 R1\nMUL R0 R2 R2\nADD R3 R3 R0\nSQRT R3 R3\nLESS R7 R3 0.00001\nIF R7 catch\nGREATER R7 R4 R3')
    shorten=g.label('shorten');length=g.label('length')
    g.emit(f'IF R7 {shorten}\nGOTO {length}\nLABEL {shorten}\nSET R4 R3\nLABEL {length}\nATAN2 Monster.Rot.Y R1 R2\nADD Monster.Rot.Y Monster.Rot.Y 180\nDIV R4 R4 R3\nMUL R1 R1 R4\nMUL R2 R2 R4\nADD NavC.Pos.X Monster.Pos.X R1\nADD NavC.Pos.Y Monster.Pos.Z R2')
    blocked=g.label('stepblocked');apply=g.label('stepapply')
    _visible(g,meta,('Monster.Pos.X','Monster.Pos.Z'),('NavC.Pos.X','NavC.Pos.Y'),blocked)
    bounds=meta['bounds']
    for var,lo,hi in [('NavC.Pos.X',bounds['xmin'],bounds['xmax']),('NavC.Pos.Y',bounds['zmin'],bounds['zmax'])]:
        g.emit(f'LESS R7 {var} {lo}\nIF R7 wait\nGREATER R7 {var} {hi}\nIF R7 wait')
    g.emit(f'GOTO {apply}\nLABEL {blocked}\nSET NavA.Pos.Z 0\nGOTO wait\nLABEL {apply}\nNOT R7 Clock.Pos.X\nIF R7 navinactive\nSET Monster.Pos.X NavC.Pos.X\nSET Monster.Pos.Z NavC.Pos.Y\nGOTO catch\nLABEL navinactive\nSET Monster.Pos.Y -100\nSET NavA.Pos.Z 0\nGOTO wait\nLABEL catch')

def emit_capture_guard(g,meta,reject='wait'):
    """Reach-limited capture with gravestone/trunk line of sight.

    Height never changes eligibility or grants immunity. A target whose head
    is above the zombie's reaching arms remains pursued but cannot be touched
    until physically in reach.
    """
    g.emit(f'GREATER R7 Player.Pos.Y 3.0\nIF R7 {reject}')
    for r in meta['physicalVehicles']:
        nxt=g.label('targetoutside')
        for value,key,op in [('Player.Pos.X','xmin','LESS'),('Player.Pos.X','xmax','GREATER'),('Player.Pos.Z','zmin','LESS'),('Player.Pos.Z','zmax','GREATER')]:
            g.emit(f'{op} R7 {value} {r[key]}\nIF R7 {nxt}')
        g.emit(f'GOTO {reject}\nLABEL {nxt}')
    _visible(g,meta,('Monster.Pos.X','Monster.Pos.Z'),('Player.Pos.X','Player.Pos.Z'),reject)


def emit_clock(g):
    g.bind('NavTime');g.emit('LABEL loop\nADD NavTime.Pos.X NavTime.Pos.X DeltaTime\nSLEEP 0\nGOTO loop')


def build(ctx):
    """Build the decaying actor facing local -Z, feet on the group origin."""
    part, group, V, Q, C = (ctx[n] for n in ('part', 'group', 'V', 'Q', 'C'))
    bone=(.75,.74,.56); flesh=(.24,.37,.19); dark=(.025,.045,.015)
    pieces=[]

    def block(p,s,c=flesh,target=None,shape=1000):
        node=part(p,s,c,isPassable=True)
        node['levelNodeStatic']['shape']=shape
        (pieces if target is None else target).append(node)
        return node

    def rod(a,b,r=.045,c=bone,target=None):
        dx,dy,dz=(b[i]-a[i] for i in range(3))
        length=math.sqrt(dx*dx+dy*dy+dz*dz)
        node=block(tuple((a[i]+b[i])/2 for i in range(3)),(2*r,length,2*r),c,target,1002)
        uy=dy/length
        if uy < -.999999:
            rotation=dict(x=1,y=0,z=0,w=0)
        else:
            norm=math.sqrt(2*(1+uy))
            rotation=dict(x=dz/length/norm,y=0,z=-dx/length/norm,w=(1+uy)/norm)
        node['levelNodeStatic']['rotation']=rotation

    # Uneven flesh and torn shirt leave ribs, one arm and femur exposed.
    block((0,1.57,.02),(.64,.75,.34),(.14,.20,.16))
    block((-.22,1.6,-.12),(.26,.55,.15),flesh)
    block((.20,1.38,-.09),(.19,.36,.23),flesh)
    for i in range(4):
        rod((.02,1.84-i*.105,-.19),(.30,1.81-i*.105,-.17),.025)
    rod((0,1.91,0),(0,2.04,-.02),.065)
    block((0,2.26,-.025),(.47,.48,.42),bone,shape=1001)
    block((-.15,2.31,.015),(.27,.4,.36),flesh,shape=1001)
    block((0,2.07,-.10),(.34,.13,.30),flesh,shape=1001)
    for side in (-1,1):
        block((side*.105,2.29,-.218),(.13,.14,.04),dark,shape=1001)
        eye=block((side*.105,2.29,-.243),(.045,.045,.025),(.55,.95,.13),shape=1001)
        eye['levelNodeStatic']['isNeon']=True
    block((0,2.19,-.245),(.07,.08,.035),dark)
    block((0,2.12,-.253),(.27,.045,.03),dark)
    for x in (-.10,-.05,0,.05,.1):
        block((x,2.145,-.272),(.03,.045,.025),bone)
    for side in (-1,1):
        shoulder=(side*.39,1.86,-.01)
        elbow=(side*.47,1.86,-.39)
        wrist=(side*.46,1.78,-.84)
        rod(shoulder,elbow,.075,flesh if side<0 else bone)
        rod(elbow,wrist,.055,flesh if side<0 else bone)
        if side>0:
            rod((elbow[0]+.06,elbow[1],elbow[2]),(wrist[0]+.04,wrist[1],wrist[2]),.018)
        block(wrist,(.16,.12,.16),flesh,shape=1001)
        for finger in range(4):
            x=wrist[0]+(finger-1.5)*.038
            rod((x,wrist[1],wrist[2]-.06),(x,wrist[1]-.07,wrist[2]-.23),.014)
    block((0,1.09,0),(.52,.28,.34),(.13,.16,.12))
    group('Monster',(0,-100,0),pieces)
    # Independent native ping-pong legs use opposite phase, not body teleport
    # jitter. Offsets are relative to each hip so feet remain on the actor.
    for side in (-1,1):
        limb=[]
        rod((0,0,0),(0,-.47,-.03),.075,bone if side>0 else flesh,limb)
        block((0,-.48,-.03),(.16,.16,.16),bone,limb,1001)
        rod((0,-.52,-.03),(0,-.94,.02),.055,flesh,limb)
        block((0,-1.01,-.09),(.23,.14,.40),(.075,.09,.065),limb)
        name='ZombieLegLeft' if side<0 else 'ZombieLegRight'
        group(name,(0,0,0),limb)
        node=ctx['names'][name]
        def tilt(degrees):
            return dict(x=math.sin(math.radians(degrees/2)),y=0,z=0,w=math.cos(math.radians(degrees/2)))
        node['animations']=[dict(name='Shamble',frames=[dict(time=0,position=V(),rotation=tilt(-side*19)),dict(time=.43,position=V(),rotation=tilt(side*19))],direction=1,speed=1,interpolation=0)]
        node['activeAnimation']=0
        ctx['attach']('Monster',name,(side*.17,1.08,0))
    ctx['add']('MonsterFumes','levelNodeParticleEmitter',dict(
        position=V(),scale=V(.65,1.4,.45),rotation=Q(),particlesPerSecond=15,
        lifeSpan=dict(x=.5,y=.9),startColor=C(.25,.65,.09,.45),
        endColor=C(.48,.75,.15,0),startSize=dict(x=.05,y=.10),endSize=dict(x=.22,y=.36),
        velocity=V(),velocityMin=V(-.12,.20,-.12),velocityMax=V(.12,.55,.12),
        accelerationMin=V(-.025,.05,-.025),accelerationMax=V(.025,.12,.025)))
    ctx['attach']('Monster','MonsterFumes',(0,-100,0))
    return dict(height=2.5,speed=4.1,front='-Z',emitter='MonsterFumes',
                maxParticleLifetime=.9,walkAnimation='Shamble',captureHeadReach=3.0,
                immunity='held-gems-only',exposedBones=['skull','right-arm','right-femur'])


def emit(ctx):
    """Emit shared zombie controllers and return navigation build metadata."""
    script,state=ctx['script'],ctx['state']
    nav=prepare_navigation(ctx['layout'])
    for n in (*STATE_NAMES,'ZombieState'):
        state(n)
    emit_clock(script('NavClock'))
    g=script('MonsterAI');g.player();g.bind('Monster','rotation')
    for n in ['Monster','MonsterFumes','Clock','Target','Waypoint','LootA','LootB','LootC','ZombieState',*STATE_NAMES]:
        g.bind(n)
    rest=ctx['layout'].get('zombieRest',(3.5,-1.1,10.5))
    if isinstance(rest,dict):rest=(rest['x'],rest['y'],rest['z'])
    rx,ry,rz=rest
    g.emit(f'LABEL loop\nIF Clock.Pos.X hunting\nSET MonsterFumes.Pos.Y -100\nSET Target.Pos.X 0\nSET NavA.Pos.Z 0\nSET ZombieState.Pos.X 0\nGREATER R7 Clock.Pos.Y 4\nIF R7 finished\nSET Monster.Pos.X {rx}\nSET Monster.Pos.Y {ry}\nSET Monster.Pos.Z {rz}\nGOTO wait\nLABEL finished\nSET Monster.Pos.Y -100\nGOTO wait\nLABEL hunting\nIF ZombieState.Pos.X scan\nSET ZombieState.Pos.X 1\nSET Monster.Pos.Y 0\nSET Monster.Pos.X {rx}\nSET Monster.Pos.Z {rz}\nSET NavA.Pos.Z 0\nSET NavB.Pos.Z 0\nSET NavC.Pos.Z NavTime.Pos.X\nLABEL scan\nSET MonsterFumes.Pos.Y 1.3\nSET Player.SelPart 0\nSET R0 0\nSET R5 100000\nSET Target.Pos.X 0\nLABEL players\nSET Player.SelIndex R0\nNOT R7 Player.Valid\nIF R7 next\nIF Player.Var1 next\nADD R6 Player.Id 1')
    for loot in ('LootA','LootB','LootC'):
        g.emit(f'EQUAL R7 {loot}.Pos.Y R6\nIF R7 next')
    # Height does not affect target eligibility. The reach guard below prevents
    # capturing through the air while leaving unprotected climbers pursued.
    g.emit('SUB R1 Player.Pos.X Monster.Pos.X\nSUB R2 Player.Pos.Z Monster.Pos.Z\nMUL R1 R1 R1\nMUL R2 R2 R2\nADD R1 R1 R2\nLESS R7 R1 R5\nNOT R7 R7\nIF R7 next\nSET R5 R1\nSET Target.Pos.X R6\nSET Target.Pos.Y Player.Pos.X\nSET Target.Pos.Z Player.Pos.Z\nLABEL next\nADD R0 R0 1\nLESS R7 R0 Player.Count\nIF R7 players\nNOT R7 Target.Pos.X\nIF R7 wait\nSET Waypoint.Pos.X Target.Pos.Y\nSET Waypoint.Pos.Z Target.Pos.Z')
    emit_route(g,nav)
    def guard():
        g.emit('SUB R0 Target.Pos.X 1\nSET Player.SelId R0\nSET Player.SelPart 0\nNOT R7 Player.Valid\nIF R7 wait\nIF Player.Var1 wait\nNOT R7 Clock.Pos.X\nIF R7 wait\nADD R6 Player.Id 1')
        for loot in ('LootA','LootB','LootC'):
            g.emit(f'EQUAL R7 {loot}.Pos.Y R6\nIF R7 wait')
        g.emit('SUB R1 Player.Pos.X Monster.Pos.X\nSUB R2 Player.Pos.Z Monster.Pos.Z\nMUL R1 R1 R1\nMUL R2 R2 R2\nADD R1 R1 R2\nGREATER R7 R1 0.65\nIF R7 wait\nGREATER R7 Player.Pos.Y 3.0\nIF R7 wait\nLESS R7 Player.Pos.Y -0.2\nIF R7 wait')
    guard()
    emit_capture_guard(g,nav)
    # LOS can span instruction slices: recheck phase, status, identity, hand
    # protection, proximity and vertical reach immediately before capture.
    guard()
    g.emit('SET Player.Var1 1\nSET Player.Var2 0\nSET Player.Var3 0\nSET Player.Var4 0\nLABEL wait\nSLEEP 0\nGOTO loop')
    return nav
