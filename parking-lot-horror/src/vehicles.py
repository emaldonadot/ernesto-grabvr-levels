"""Nine native primitive vehicles, doors and interaction locations.

All model fronts face local -Z. Doors pivot at their front edge; all supplied
gameplay points are world coordinates. No external meshes or logos required.
"""
import math


def build(ctx):
    group, part = ctx['group'], ctx['part']
    attach, trigger = ctx['attach'], ctx['trigger']
    animation, names = ctx['animation'], ctx['names']
    Q = ctx['Q']
    result = dict(vehicles=[], doors=[], hides=[], loot=[], obstacles=[])
    rubber=(.025,.03,.035); alloy=(.43,.48,.5); glass=(.055,.14,.19)
    lamp=(.87,.92,.72); red=(.7,.035,.025); black=(.045,.055,.065)

    def p(pos,size,color,shape=1000,rz=0,rx=0,**kw):
        node=part(pos,size,color,**kw)
        node['levelNodeStatic']['shape']=shape
        if rz:
            a=math.radians(rz/2)
            node['levelNodeStatic']['rotation']=dict(x=0,y=0,z=math.sin(a),w=math.cos(a))
        if rx:
            a=math.radians(rx/2)
            node['levelNodeStatic']['rotation']=dict(x=math.sin(a),y=0,z=0,w=math.cos(a))
        return node

    def make(vid,kind,x,z,yaw,color,w=2.05,length=4.8,h=1.7):
        root=vid; children=[]
        group(root,(x,0,z),children)
        names[root]['levelNodeGroup']['rotation']=Q(yaw)
        def world(pos):
            a=math.radians(yaw);px,py,pz=pos
            return [round(x+px*math.cos(a)+pz*math.sin(a),5),py,
                    round(z-px*math.sin(a)+pz*math.cos(a),5)]
        def mesh(pos,size,c,**kw):children.append(p(pos,size,c,**kw))
        def wheel(wx,wz,r=.36):
            mesh((wx,r,wz),(r*2,.23,r*2),rubber,shape=1002,rz=90)
            mesh((wx+(.13 if wx>0 else -.13),r,wz),(r*1.12,.025,r*1.12),alloy,shape=1002,rz=90)
            mesh((wx+(.15 if wx>0 else -.15),r,wz),(.16,.03,.16),black,shape=1002,rz=90)
        def door(tag,origin,panel,sliding=False):
            dn=vid+tag; clip=tag+'Slide' if sliding else tag+'Hinge'
            panel_y=.8 if kind=='sport' else .89
            panel_h=.44 if kind=='sport' else .64
            glass_y=1.17 if kind=='sport' else (h+.98)/2
            glass_h=.30 if kind=='sport' else h-1.13
            pieces=[p((panel[0],panel_y,panel[2]),(.09,panel_h,1.45 if sliding else 1.05),color),
                    p((panel[0],glass_y,panel[2]),(.07,glass_h,1.35 if sliding else .92),glass),
                    p((panel[0]-.08,panel[1]+.04,panel[2]+.28),(.1,.065,.23),alloy)]
            # Glass, its frame and the real handle form one animated assembly.
            # The blue external control remains fixed so the open door can
            # always be operated; it is a button, not the physical handle.
            pane_length=1.35 if sliding else .92
            for edge in [-1,1]:
                pieces.append(p((panel[0],glass_y,panel[2]+edge*(pane_length/2+.025)),
                                (.085,glass_h+.08,.05),color))
            pieces.append(p((panel[0],glass_y+glass_h/2+.025,panel[2]),
                            (.085,.05,pane_length+.1),color))
            if not sliding:
                pieces.append(p((-.12,1.22,.12),(.22,.14,.2),color))
            group(dn,(0,0,0),pieces);attach(root,dn,origin)
            animation(dn,clip,position=(0,0,1.5) if sliding else (0,0,0),yaw=0 if sliding else -78)
            use=dn+'Use';up=(origin[0]-.23,1.08,origin[2]+panel[2]+.22)
            trigger(use,world(up),(.4,.38,.42))
            mesh(up,(.07,.13,.18),(.1,.65,.8),isNeon=True)
            result['doors'].append(dict(name=dn,use=use,animation=clip,
                kind='slide' if sliding else 'hinge',vehicle=vid,glassChild=1,
                handleChild=2,frameChildren=[3,4,5],mirrorChild=None if sliding else 6,
                aperture=dict(x=origin[0],zmin=origin[2]+panel[2]-pane_length/2,
                              zmax=origin[2]+panel[2]+pane_length/2,
                              ymin=glass_y-glass_h/2,ymax=glass_y+glass_h/2)))
            return dn,use
        if kind in ('sport','minivan','suv'):
            # Open cabin: only floor, roof, pillars, passenger/rear shell.
            mesh((0,.47,0),(w-.18,.22,length),color)
            mesh((0,.77,-length/2+.62),(w,.46,1.2),color)
            mesh((0,.72,length/2-.36),(w,.4,.7),color)
            roof=h-.08
            roof_center=.32 if kind=='sport' else .15
            roof_length=1.75 if kind=='sport' else length-1.65
            mesh((0,roof,roof_center),(w-.12 if kind=='sport' else w,.12,roof_length),color)
            for px in [-w/2+.05,w/2-.05]:
                for pz in [-length/2+1.22,length/2-.48]:
                    mesh((px,(roof+.65)/2,pz),(.09,roof-.65,.10),color)
            # Windshield and back window, tinted; dashboard/steering visible.
            if kind=='sport':
                mesh((0,1.18,-.82),(w-.18,.53,.065),glass,rx=35)
                for sx in [-w/2+.08,w/2-.08]:mesh((sx,1.18,-.82),(.075,.57,.075),color,rx=35)
            else:
                mesh((0,(roof+1.05)/2,-length/2+1.21),(w-.12,roof-1.05,.065),glass,rx=12 if kind=='suv' else 5)
            mesh((0,roof-.3,length/2-.47),(w-.12,.45,.06),glass)
            mesh((0,.98,-length/2+1.34),(w-.2,.19,.32),black)
            mesh((-.48,1.08,-length/2+1.62),(.32,.32,.055),rubber,shape=1002,rz=90)
            for sx in [-.48,.48]:
                mesh((sx,.67,-.24),(.55,.17,.6),black)
                mesh((sx,.99,.02),(.55,.58,.12),black)
                mesh((sx,1.35,.02),(.31,.22,.12),black)
            mesh((0,.77,.25),(.23,.32,.8),black)
            for sx in [-1,1]:
                if sx==1:mesh((sx*(w/2+.12),1.22,-.83),(.22,.14,.2),color)
                mesh((sx*.66,.83,-length/2-.025),(.42,.15,.05),lamp,isNeon=True)
                mesh((sx*.73,.79,length/2+.025),(.28,.18,.05),red,isNeon=True)
                for wz in [-length/2+.82,length/2-.8]:wheel(sx*w/2,wz)
            mesh((0,.52,-length/2-.04),(w,.15,.13),alloy)
            mesh((0,.75,-length/2-.07),(.72,.2,.045),black)
            for gx in [-.28,-.14,0,.14,.28]:mesh((gx,.75,-length/2-.1),(.045,.16,.035),alloy)
            mesh((0,.54,length/2+.05),(.55,.13,.025),(.77,.79,.72))
            if kind=='sport':
                # Low coupe profile, bonnet stripes, rear wing and split exhaust.
                for sx in [-.22,.22]:
                    mesh((sx,1.01,-1.7),(.15,.015,.85),black)
                for sx in [-.7,.7]:
                    mesh((sx,1.03,1.83),(.07,.3,.09),black)
                    mesh((sx,.44,2.29),(.15,.11,.12),alloy)
                mesh((0,1.2,1.83),(2.0,.075,.3),black)
            if kind=='suv':
                # Explorer-like upright nose, broad grille and raised roof rails.
                for sx in [-.78,.78]:mesh((sx,h+.025,.28),(.075,.12,2.55),black)
                for sz in [-.7,1.18]:mesh((0,h+.055,sz),(1.65,.065,.08),alloy)
                mesh((0,.9,-length/2-.07),(1.38,.35,.07),black)
                for yy in [.79,.90,1.01]:mesh((0,yy,-length/2-.12),(1.3,.035,.025),alloy)
                mesh((0,.91,-length/2-.15),(.23,.10,.025),(.04,.2,.6))
            door('DriverDoor',(-w/2,0,-.95),(0,.86,.525))
            mesh((w/2,.91,.15),(.1,.8,2.3),color)
            mesh((w/2,1.17 if kind=='sport' else 1.52,.15),(.06,.3 if kind=='sport' else .65,2.15),glass)
            if kind=='minivan':
                # Sliding door behind driver opens to a genuine hollow cabin.
                dn,use=door('SideDoor',(-w/2,0,.3),(0,.85,.725),True)
                mesh((-w/2,.9,2.02),(.1,.8,.62),color)
                # No fixed pane here: it overlapped the driver-door glass,
                # leaving a window behind when the driver door swung open.
                mesh((0,.53,1.1),(w-.25,.08,1.6),black)
                mesh((0,1.13,1.97),(w-.3,.8,.13),black)
                hid=len(result['hides'])+1
                leave=vid+'HideLeave';enter=vid+'HideUse'
                trigger(enter,world((-w/2-.28,1.03,.95)),(.42,.4,.42))
                trigger(leave,world((-.58,1.03,1.05)),(.35,.35,.35))
                mesh((-w/2-.1,1.03,.95),(.055,.15,.23),(.1,.8,.6),isNeon=True)
                mesh((-.58,1.03,1.05),(.11,.11,.11),(.1,.8,.6),isNeon=True)
                force=[]
                for suffix in ('Open','Close'):
                    fn=vid+'Hide'+suffix;trigger(fn,(0,-200,0),(.1,.1,.1))
                    names[fn]['levelNodeTrigger']['triggerSources']=[];force.append(fn)
                result['hides'].append(dict(id=hid,use=enter,leave=leave,open=force[0],close=force[1],door=dn,
                    position=world((0,.58,1.06)),exit=world((-w/2-.7,.1,1.0)),halfExtent=[.85,.75]))
            else:
                mesh((-w/2,.9,1.0),(.1,.75,1.25),color)
                mesh((-w/2,1.17 if kind=='sport' else 1.52,.96),(.065,.3 if kind=='sport' else .65,1.15),glass)
            if vid in ('SportCar','Minivan1','ExplorerSUV'):
                slot={'SportCar':1,'Minivan1':2,'ExplorerSUV':3}[vid]
                lp=world((-.48,.92,-.22));lu=vid+'LootUse'
                trigger(lu,lp,(.38,.32,.38))
                mesh((-.48,.76,-.22),(.3,.06,.3),(.2,.22,.23))
                result['loot'].append(dict(slot=slot,position=lp,use=lu,vehicle=vid))
        elif kind in ('mt07','ryker'):
            blue=color
            mesh((0,.63,.05),(.3,.19,1.65),black)
            mesh((0,.84,.35),(.48,.16,.85),rubber)
            mesh((0,.93,-.32),(.54,.38,.65),blue)
            mesh((0,.55,-.12),(.48,.48,.52),alloy)
            for ex in [-.17,0,.17]:mesh((ex,.54,-.4),(.075,.4,.16),black)
            mesh((0,1.25,-.77),(1.0,.08,.1),alloy)
            for sx in [-1,1]:
                mesh((sx*.43,1.25,-.77),(.24,.1,.12),rubber)
                mesh((sx*.40,1.5,-.78),(.2,.13,.045),alloy)
                mesh((sx*.33,1.37,-.78),(.045,.25,.045),black)
            if kind=='mt07':
                for wz in [-1.02,1.03]:wheel(0,wz,.34)
                for sx in [-.16,.16]:mesh((sx,.69,-1.0),(.075,.7,.09),alloy)
                mesh((0,1.05,-.96),(.29,.22,.1),lamp,isNeon=True)
                mesh((.27,.4,.65),(.18,.18,.62),alloy)
            else:
                for sx in [-.66,.66]:
                    wheel(sx,-.91,.32)
                    mesh((sx,.31,-.89),(.8,.11,.12),alloy)
                    mesh((sx,.69,-.9),(.4,.13,.6),blue)
                    mesh((sx, .68,-1.22),(.23,.12,.07),lamp,isNeon=True)
                wheel(0,1.1,.36)
                mesh((0,.74,-.76),(.68,.19,.35),blue)
            mesh((0,.96,.87),(.2,.1,.06),red,isNeon=True)
        else:
            # Low crushed roof, displaced panels, uneven wheel alignment.
            mesh((0,.35,0),(w,.38,length),color)
            mesh((.17,.7,.18),(w*.8,.2,length*.55),color,rz=12)
            mesh((.31,.82,.32),(w*.58,.15,1.5),color,rz=-17)
            mesh((-.62,.65,.45),(.12,.48,1.7),alloy,rz=26)
            mesh((-.22,.57,-1.2),(w*.85,.13,1.1),alloy,rz=-9)
            mesh((.28,.68,.13),(w*.65,.08,.9),glass,rz=17)
            for sx in [-1,1]:
                wheel(sx*w/2,-1.26,.3);wheel(sx*w/2,1.2,.3)
                mesh((sx*.6,.37,-length/2),(.3,.13,.06),lamp)
            for dx,dz in [(-.65,-.8),(.45,.6),(.7,1.4)]:
                mesh((dx,.65,dz),(.5,.12,.65),black,rz=24)
        result['vehicles'].append(dict(id=vid,kind=kind,center=[x,0,z],bounds=[w,h,length],yaw=yaw))
        # Ground-navigation blockers include wheels/mirrors and the complete
        # swept envelope of both doors. The navigation layer adds actor radius.
        # These are deliberately conservative: doors may open during a chase.
        if kind in ('sport','minivan','suv'):
            local_bounds=(-w/2-1.25,w/2+.25,-length/2-.15,length/2+.85)
        else:
            local_bounds=(-w/2-.25,w/2+.25,-length/2-.15,length/2+.15)
        lx0,lx1,lz0,lz1=local_bounds
        corners=[world((px,0,pz)) for px in (lx0,lx1) for pz in (lz0,lz1)]
        result['obstacles'].append(dict(name=vid,xmin=min(c[0] for c in corners),
            xmax=max(c[0] for c in corners),zmin=min(c[2] for c in corners),
            zmax=max(c[2] for c in corners),topY=h+.15,
            includesDoorSweep=kind in ('sport','minivan','suv')))

    make('SportCar','sport',-10.15,-23.75,180,(.61,.045,.035),w=2.05,length=4.5,h=1.45)
    make('Minivan1','minivan',-4.35,-23.75,180,(.62,.64,.61),w=2.15,length=5,h=2.0)
    make('ExplorerSUV','suv',4.35,-23.75,180,(.035,.17,.58),w=2.15,length=4.95,h=1.95)
    make('Minivan2','minivan',4.35,23.75,0,(.31,.09,.08),w=2.15,length=5,h=2.0)
    make('BlueStreetBike','mt07',-10.15,-11.65,0,(.035,.16,.8),w=1.1,length=2.5,h=1.6)
    make('RykerTrike','ryker',10.15,11.65,180,(.26,.28,.3),w=1.9,length=2.7,h=1.6)
    make('Wreck1','wreck',-4.35,-6.05,180,(.34,.24,.12),length=4.3,h=.9)
    make('Wreck2','wreck',-10.15,6.05,0,(.21,.27,.24),length=4.4,h=.9)
    make('Wreck3','wreck',-1.45,11.65,180,(.35,.13,.11),length=4.2,h=.9)
    return result
