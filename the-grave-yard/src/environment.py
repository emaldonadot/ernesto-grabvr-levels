"""Native primitive graveyard. Metres, Y up; one of 16 graves is open.

The returned obstacle registry covers tall colliders, not low walkable soil.
Optional ``names`` and ``add`` support rounded meshes and native point lights.
"""
EPITAPHS = (
    "Dracula", "Frankenstein's Monster", "The Mummy", "The Wolf Man",
    "Nosferatu", "The Invisible Man", "The Phantom", "The Headless Horseman",
    "Dr Jekyll", "Mr Hyde", "The Creature", "The Banshee",
    "The Golem", "The Ghoul", "The Lich", "The Reaper",
)
TREE_POSITIONS = ((-19,-17), (18,-17), (-19,2), (19,9), (-17,19), (17,19))
PUMPKIN_POSITIONS = ((-15,-21), (15,-21), (-15,20), (15,20))
CANDLE_GRAVES = (1, 7, 14)
GRAVE_SPACING = 7.0
ZOMBIE_SPEED = 4.1
WALL_HEIGHT = 8.0
OPEN_GRAVE = 14
REST_POSITION = (3.5,-1.1,10.5)


def build(ctx):
    box, sign = ctx['box'], ctx['sign']
    graves, trees, pumpkins, obstacles = [], [], [], []
    names = ctx.get('names', {})
    def round_mesh(name,p,s,c,**kw):
        result=box(name,p,s,c,**kw)
        if name in names:
            names[name]['levelNodeStatic']['shape']=1001
        return result
    def light(name,p,color,intensity,radius):
        if ctx.get('add'):
            ctx['add'](name,'levelNodeLight',dict(position=dict(zip('xyz',p)),
                rotation=dict(x=0,y=0,z=0,w=1),type=0,
                color=dict(zip('rgba',(*color,1))),intensity=intensity,range=radius))

    # Four continuous slabs leave an honest 2.3 x 3.2 m opening; a sealed
    # bottom and earth walls prevent dropping into the void under the map.
    gx,gz=3.5,10.5
    x0,x1=gx-1.15,gx+1.15
    z0,z1=gz-1.6,gz+1.6
    for name,p,s in (
        ('Ground',((x0-24)/2,-.35,0),(x0+24,.7,56)),
        ('GroundEast',((x1+24)/2,-.35,0),(24-x1,.7,56)),
        ('GroundSouth',(gx,-.35,(z0-28)/2),(2.3,.7,z0+28)),
        ('GroundNorth',(gx,-.35,(z1+28)/2),(2.3,.7,28-z1))):
        box(name,p,s,(.075,.12,.09))
    box('OpenGraveBottom',(gx,-1.25,gz),(2.3,.3,3.2),(.12,.085,.055))
    for n,x in enumerate((x0,x1)):
        box(f'OpenGraveEarthSide{n}',(x,-.6,gz),(.16,1.2,3.2),(.17,.105,.06))
    for n,z in enumerate((z0,z1)):
        box(f'OpenGraveEarthEnd{n}',(gx,-.6,z),(2.3,1.2,.16),(.17,.105,.06))
    # Two climbable ledges make the open grave escapable without a jump.
    box('OpenGraveStepLow',(gx,-.8,gz-1.1),(1.0,.5,.6),(.21,.15,.10))
    box('OpenGraveStepHigh',(gx,-.35,gz-1.4),(1.0,.4,.5),(.24,.18,.12))

    # Walls exceed all climbable tree geometry. A transparent collision cap
    # preserves the moon/sky while preventing high launches over the perimeter.
    iron=(.12,.13,.15)
    solid=dict(isGrabbable=False,isGrapplable=False,isPassable=False)
    for x in (-24,24):
        # East boundary faces the spectator gallery: retain collision but clear the view.
        window=dict(isTransparent=True) if x==24 else {}
        color=(*iron,.025) if x==24 else iron
        box('FenceSide%s'%x,(x,WALL_HEIGHT/2,0),(.4,WALL_HEIGHT,56.4),color,**window,**solid)
        box('FenceSideRail%s'%x,(x,WALL_HEIGHT,0),(.5,.2,56.4),iron,**solid)
    box('FenceBack',(0,WALL_HEIGHT/2,28),(48.4,WALL_HEIGHT,.4),iron,**solid)
    box('FenceBackRail',(0,WALL_HEIGHT,28),(48.4,.2,.5),iron,**solid)
    for x in (-13.5,13.5):
        box('FenceFront%s'%x,(x,WALL_HEIGHT/2,-28),(21,WALL_HEIGHT,.4),iron,**solid)
        box('FenceFrontRail%s'%x,(x,WALL_HEIGHT,-28),(21,.2,.5),iron,**solid)
    # Seal the space above the lifting gate and overlap its posts/front walls.
    box('GateHeader',(0,(3.5+WALL_HEIGHT)/2,-28),(6.7,WALL_HEIGHT-3.5,.7),iron,**solid)
    box('YardSafetyCap',(0,WALL_HEIGHT,0),(48.4,.2,56.4),(.12,.16,.20,.025),isTransparent=True,**solid)
    for side,x in (('Left',-2.9),('Right',2.9)):
        box(f'Gate{side}Post',(x,1.8,-28),(.7,3.6,.7),(.26,.25,.24),**solid)
        round_mesh(f'Gate{side}Cap',(x,3.8,-28),(.8,.8,.8),(.3,.31,.32),**solid)

    for row in range(4):
        for col in range(4):
            i=row*4+col
            x=(col-1.5)*GRAVE_SPACING
            z=(row-1.5)*GRAVE_SPACING
            if i!=OPEN_GRAVE:
                box(f'GraveSoil{i}',(x,.035,z),(2.3,.07,3.2),(.16,.11,.09))
            box(f'Gravestone{i}',(x,.95,z+1.4),(1.6,1.9,.3),(.3,.32,.33))
            round_mesh(f'GravestoneCrown{i}',(x,1.76,z+1.4),(1.6,.6,.3),(.3,.32,.33))
            sign(f'Epitaph{i}',EPITAPHS[i],(x,1.2,z+1.19),.22)
            obstacles.append((x-.8,x+.8,z+1.25,z+1.55))
            graves.append((x,z))
            if i in CANDLE_GRAVES:
                box(f'Candle{i}',(x+.75,.38,z),(.16,.65,.16),(.88,.77,.54))
                round_mesh(f'CandleFlame{i}',(x+.75,.78,z),(.1,.2,.1),(1,.55,.08),isNeon=True,isPassable=True)
                light(f'CandleLight{i}',(x+.75,.86,z),(1,.55,.15),1.2,3.0)

    for i,(x,z) in enumerate(TREE_POSITIONS):
        box(f'TreeTrunk{i}',(x,2,z),(.9,4,.9),(.19,.12,.1))
        obstacles.append((x-.45,x+.45,z-.45,z+.45))
        # Low branch handholds form an actual climb route to the three gems.
        for j in range(3):
            box(f'TreeClimbHold{i}_{j}',(x+(.6 if j%2 else -.6),.7+j*.85,z), (1.4,.23,.42),(.16,.10,.08))
            box(f'TreeBranch{i}_{j}',(x+(j-1)*.9,3.8+j*.55,z),(2.5,.28,.42),(.18,.12,.1))
        box(f'TreeDeadTwig{i}',(x+1.9,4.4,z),(.22,1.2,.25),(.16,.10,.08))
        box(f'TreeDeadTwigB{i}',(x-1.9,4,z),(.22,.9,.25),(.16,.10,.08))
        trees.append((x,z))

    for i,(x,z) in enumerate(PUMPKIN_POSITIONS):
        round_mesh(f'Pumpkin{i}',(x,.48,z),(1,.95,1),(.85,.21,.025))
        box(f'PumpkinStem{i}',(x,1.05,z),(.16,.25,.16),(.17,.3,.08))
        # Black cut-out surrounds and inset warm emission sell a lit lantern.
        for side,dx in (('Left',-.21),('Right',.21)):
            box(f'PumpkinEyeCut{i}{side}',(x+dx,.64,z-.44),(.25,.25,.08),(.055,.025,.01),isPassable=True)
            box(f'PumpkinEyeGlow{i}{side}',(x+dx,.64,z-.485),(.16,.16,.025),(1,.56,.055),isNeon=True,isPassable=True)
        box(f'PumpkinMouthCut{i}',(x,.30,z-.45),(.62,.22,.08),(.055,.025,.01),isPassable=True)
        box(f'PumpkinMouthGlow{i}',(x,.30,z-.495),(.50,.12,.025),(1,.48,.025),isNeon=True,isPassable=True)
        for tooth,dx in enumerate((-.15,.13)):
            box(f'PumpkinTooth{i}_{tooth}',(x+dx,.35,z-.52),(.10,.10,.04),(.85,.21,.025),isPassable=True)
        light(f'PumpkinLight{i}',(x,.65,z-.62),(1,.43,.06),2.3,5.0)
        pumpkins.append((x,z))

    round_mesh('Moon',(0,31,24),(5,5,.4),(.92,.94,1),isNeon=True,isPassable=True)
    for i in range(4):
        round_mesh(f'Cloud{i}',(-15+i*9,29+i%2,23),(8,1.2,1.8),(.18,.2,.26),isPassable=True)
    # The socket is above the solid pedestal and supplied by native gameplay.
    box('SkullPedestal',(4,.9,-24),(1.1,1.8,1.1),(.4,.36,.3))
    box('SkullPedestalCap',(4,1.85,-24),(1.4,.16,1.4),(.48,.42,.31))
    return dict(graves=graves,trees=trees,pumpkins=pumpkins,candles=list(CANDLE_GRAVES),
        epitaphs=list(EPITAPHS),zombie_speed=ZOMBIE_SPEED,obstacles=obstacles,
        open_grave=OPEN_GRAVE,rest=REST_POSITION,spawn=(0,0,-23),
        gate=(0,0,-28),socket=(4,2.15,-24),
        containment=dict(wallHeight=WALL_HEIGHT,capBottom=WALL_HEIGHT-.1,gateOpeningHeight=3.5),
        gem_positions=[(x-1.2,4.1,z) for x,z in TREE_POSITIONS[:3]])
