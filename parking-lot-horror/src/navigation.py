"""Ground-plane obstacle-aware native GASM navigation.

Empty stalls have no routing restrictions. Axis-aligned, conservative swept vehicle
and column footprints are expanded by actor clearance. Persistent corner detours
are used only when a direct segment is occluded; every actual step is swept-tested.
"""
import math

CLEARANCE=.38
STATE_NAMES=('NavA','NavB','NavC','NavTime','NavRect','NavRect2','NavRect3')

def prepare(layout,fleet):
    raw=list(layout['obstacles'])+list(fleet['obstacles'])
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
                physicalVehicles=fleet['obstacles'],bounds=dict(xmin=-20.7,xmax=20.7,zmin=-28.9,zmax=28.9))

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
    g.emit(f'IF R7 {cap}\nGOTO {step}\nLABEL {cap}\nSET R4 0.12\nLABEL {step}\nMUL R4 R4 3.7\nSUB R1 Waypoint.Pos.X Monster.Pos.X\nSUB R2 Waypoint.Pos.Z Monster.Pos.Z\nMUL R3 R1 R1\nMUL R0 R2 R2\nADD R3 R3 R0\nSQRT R3 R3\nLESS R7 R3 0.00001\nIF R7 catch\nGREATER R7 R4 R3')
    shorten=g.label('shorten');length=g.label('length')
    g.emit(f'IF R7 {shorten}\nGOTO {length}\nLABEL {shorten}\nSET R4 R3\nLABEL {length}\nATAN2 Monster.Rot.Y R1 R2\nADD Monster.Rot.Y Monster.Rot.Y 180\nDIV R4 R4 R3\nMUL R1 R1 R4\nMUL R2 R2 R4\nADD NavC.Pos.X Monster.Pos.X R1\nADD NavC.Pos.Y Monster.Pos.Z R2')
    blocked=g.label('stepblocked');apply=g.label('stepapply')
    _visible(g,meta,('Monster.Pos.X','Monster.Pos.Z'),('NavC.Pos.X','NavC.Pos.Y'),blocked)
    bounds=meta['bounds']
    for var,lo,hi in [('NavC.Pos.X',bounds['xmin'],bounds['xmax']),('NavC.Pos.Y',bounds['zmin'],bounds['zmax'])]:
        g.emit(f'LESS R7 {var} {lo}\nIF R7 wait\nGREATER R7 {var} {hi}\nIF R7 wait')
    g.emit(f'GOTO {apply}\nLABEL {blocked}\nSET NavA.Pos.Z 0\nGOTO wait\nLABEL {apply}\nNOT R7 Clock.Pos.X\nIF R7 navinactive\nSET Monster.Pos.X NavC.Pos.X\nSET Monster.Pos.Z NavC.Pos.Y\nGOTO catch\nLABEL navinactive\nSET Monster.Pos.Y -100\nSET NavA.Pos.Z 0\nGOTO wait\nLABEL catch')

def emit_capture_guard(g,meta,reject='wait'):
    """No roof captures, no capture through a vehicle body or column."""
    g.emit(f'GREATER R7 Player.Pos.Y 2.2\nIF R7 {reject}')
    for r in meta['physicalVehicles']:
        nxt=g.label('targetoutside')
        for value,key,op in [('Player.Pos.X','xmin','LESS'),('Player.Pos.X','xmax','GREATER'),('Player.Pos.Z','zmin','LESS'),('Player.Pos.Z','zmax','GREATER')]:
            g.emit(f'{op} R7 {value} {r[key]}\nIF R7 {nxt}')
        g.emit(f'GOTO {reject}\nLABEL {nxt}')
    _visible(g,meta,('Monster.Pos.X','Monster.Pos.Z'),('Player.Pos.X','Player.Pos.Z'),reject)


def emit_clock(g):
    g.bind('NavTime');g.emit('LABEL loop\nADD NavTime.Pos.X NavTime.Pos.X DeltaTime\nSLEEP 0\nGOTO loop')
