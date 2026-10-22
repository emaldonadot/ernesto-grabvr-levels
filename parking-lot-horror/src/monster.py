"""Native GRAB skeleton mesh. Front is -Z; floor pivot is Y=0.

All visuals are passable: only the guarded AI catch can capture a player.
Shape enum IDs come from the vendored GRAB schema (sphere=1001,
cylinder=1002). No collision/lava damage bypasses immunity or safe hiding.
"""
import math


def build(ctx):
    part, group = ctx['part'], ctx['group']
    V, Q, C = ctx['V'], ctx['Q'], ctx['C']
    bone_color = (.72, .76, .65)
    worn = (.48, .54, .46)
    dark = (.012, .035, .034)
    pieces = []

    def ellipsoid(p, size, color=bone_color, neon=False):
        node = part(p, size, color, isPassable=True, isNeon=neon)
        node['levelNodeStatic']['shape'] = 1001
        pieces.append(node)
        return node

    def block(p, size, color=bone_color):
        node = part(p, size, color, isPassable=True)
        pieces.append(node)
        return node

    def bone(a, b, radius=.045, color=bone_color):
        dx, dy, dz = (b[i]-a[i] for i in range(3))
        length = math.sqrt(dx*dx+dy*dy+dz*dz)
        node = part(tuple((a[i]+b[i])/2 for i in range(3)),
                    (radius*2, length, radius*2), color, isPassable=True)
        body = node['levelNodeStatic']
        body['shape'] = 1002
        # Quaternion rotating the cylinder's +Y axis onto its endpoint vector.
        ux, uy, uz = dx/length, dy/length, dz/length
        if uy < -.999999:
            body['rotation'] = dict(x=1, y=0, z=0, w=0)
        else:
            norm = math.sqrt(2*(1+uy))
            body['rotation'] = dict(x=uz/norm, y=0, z=-ux/norm,
                                    w=(1+uy)/norm)
        pieces.append(node)

    # Skull crown reaches exactly the previous shadow creature's 2.525m.
    ellipsoid((0, 2.295, 0), (.45, .46, .39))
    ellipsoid((0, 2.16, -.105), (.35, .23, .32))
    for side in (-1, 1):
        ellipsoid((side*.107, 2.315, -.183), (.14, .155, .05), dark)
        ellipsoid((side*.107, 2.31, -.214), (.047, .05, .019),
                  (.23, .95, .73), True)
        ellipsoid((side*.17, 2.205, -.14), (.10, .085, .12), worn)
    # Nasal cavity, separate lower jaw, and clearly separated teeth.
    block((0, 2.24, -.263), (.065, .075, .025), dark)
    block((0, 2.135, -.25), (.285, .055, .027), dark)
    bone((-.16, 2.16, -.11), (-.13, 2.075, -.21), .028)
    bone((.16, 2.16, -.11), (.13, 2.075, -.21), .028)
    bone((-.13, 2.075, -.21), (.13, 2.075, -.21), .032)
    for x in (-.105, -.063, -.021, .021, .063, .105):
        block((x, 2.145, -.272), (.029, .046, .024))
        block((x, 2.10, -.252), (.029, .031, .025))
    bone((0, 1.88, .03), (0, 2.07, .025), .055)
    # Exposed vertebrae down the back, clavicles and sternum in front.
    for i in range(10):
        ellipsoid((0, 1.13+i*.075, .085), (.105, .067, .10), worn)
    bone((0, 1.90, -.025), (-.32, 1.86, 0), .039)
    bone((0, 1.90, -.025), (.32, 1.86, 0), .039)
    bone((0, 1.48, -.15), (0, 1.85, -.15), .037)
    # Six pairs of ribs curve around an empty torso using three segments each.
    for row in range(6):
        y = 1.82-row*.069
        width = (.255, .29, .30, .285, .26, .225)[row]
        for side in (-1, 1):
            points = [(side*.035, y, .085), (side*width, y-.018, .015),
                      (side*width*.82, y-.048, -.145),
                      (side*.035, y-.055, -.17)]
            for a, b in zip(points, points[1:]):
                bone(a, b, .022)
    # Iliac wings and open pelvic ring; no solid torso block.
    for side in (-1, 1):
        ellipsoid((side*.17, 1.19, .015), (.18, .23, .12), worn)
        bone((side*.22, 1.18, .015), (side*.10, 1.035, -.055), .046)
        bone((side*.10, 1.035, -.055), (0, 1.08, .06), .035)
    bone((-.14, 1.24, .07), (.14, 1.24, .07), .04)
    for side in (-1, 1):
        shoulder = (side*.35, 1.84, .015)
        elbow = (side*.45, 1.36, -.02)
        wrist = (side*.51, .94, -.10)
        ellipsoid(shoulder, (.13, .13, .13))
        bone(shoulder, elbow, .049)
        ellipsoid(elbow, (.10, .10, .10), worn)
        # Radius and ulna remain distinct instead of a solid forearm.
        for offset in (-.028, .028):
            bone((elbow[0]+offset, elbow[1], elbow[2]),
                 (wrist[0]+offset*.65, wrist[1], wrist[2]), .019)
        ellipsoid(wrist, (.075, .09, .07))
        for finger in range(4):
            x = wrist[0]+(finger-1.5)*.031
            bone((x, .91, -.10), (x+side*.012, .80, -.12), .011)
            bone((x+side*.012, .80, -.12), (x, .75, -.15), .009)
        bone((wrist[0]-side*.04, .91, -.10),
             (wrist[0]-side*.085, .84, -.12), .016)
        hip, knee, ankle = (side*.16, 1.08, .01), (side*.19, .58, -.025), (side*.19, .13, .025)
        bone(hip, knee, .059)
        ellipsoid(knee, (.11, .105, .115), worn)
        bone(knee, ankle, .041)
        bone((knee[0]+side*.063, .56, .015),
             (ankle[0]+side*.045, .14, .025), .018)
        ellipsoid(ankle, (.09, .08, .09))
        bone((side*.19, .095, .04), (side*.19, .07, -.19), .042)
        for toe in range(3):
            bone((side*.19+(toe-1)*.036, .07, -.15),
                 (side*.19+(toe-1)*.036, .055, -.25), .015)
    group('Monster', (0, -100, 0), pieces)
    ctx['add']('MonsterFumes', 'levelNodeParticleEmitter', dict(
        position=V(), scale=V(.65, 1.4, .45), rotation=Q(),
        particlesPerSecond=18, lifeSpan=dict(x=.55, y=1),
        startColor=C(.20, .48, .40, .40), endColor=C(.40, .70, .61, 0),
        startSize=dict(x=.06, y=.12), endSize=dict(x=.28, y=.42),
        velocity=V(), velocityMin=V(-.15, .2, -.15),
        velocityMax=V(.15, .6, .15),
        accelerationMin=V(-.03, .05, -.03),
        accelerationMax=V(.03, .15, .03)))
    ctx['attach']('Monster', 'MonsterFumes', (0, 1.3, 0))
    return dict(height=2.525, speed=3.7, geometryParts=len(pieces)-1,
                front='-Z', emitter='MonsterFumes',
                baselineSpeed=3.4, maxParticleLifetime=1)
