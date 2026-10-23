"""Graveyard scene generator using the existing GRAB native primitive builder interface.

This module is not yet connected to the final native serialization pipeline.
Coordinates are metres, Y up.
"""
from math import sin, cos, pi

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

def build(ctx):
    box, group, part, sign = (ctx[k] for k in ("box","group","part","sign"))
    graves, trees, pumpkins = [], [], []
    box("Ground", (0,-.35,0), (48,.7,56), (.075,.12,.09))
    for x in (-24,24):
        box("FenceSide%s"%x,(x,1.45,0),(.32,2.9,56),(.14,.14,.15))
    box("FenceBack",(0,1.45,28),(48,2.9,.32),(.14,.14,.15))
    for x in (-13.5,13.5):
        box("FenceFront%s"%x,(x,1.45,-28),(21,2.9,.32),(.14,.14,.15))
    box("GateLeftPost",(-2.9,1.8,-28),(.7,3.6,.7),(.26,.25,.24))
    box("GateRightPost",(2.9,1.8,-28),(.7,3.6,.7),(.26,.25,.24))
    for row in range(4):
        for col in range(4):
            i=row*4+col
            x=(col-1.5)*GRAVE_SPACING
            z=(row-1.5)*GRAVE_SPACING
            box(f"GraveSoil{i}",(x,.035,z),(2.3,.07,3.2),(.16,.11,.09))
            box(f"Gravestone{i}",(x,.95,z+1.4),(1.6,1.9,.3),(.3,.32,.33))
            sign(f"Epitaph{i}",EPITAPHS[i],(x,1.2,z+1.19),.22)
            graves.append((x,z))
            if i in CANDLE_GRAVES:
                box(f"Candle{i}",(x+.75,.38,z),(.16,.65,.16),(.88,.77,.54))
                box(f"CandleFlame{i}",(x+.75,.78,z),(.1,.2,.1),(1,.55,.08),isNeon=True,isPassable=True)
    for i,(x,z) in enumerate(TREE_POSITIONS):
        box(f"TreeTrunk{i}",(x,2,z),(.9,4,.9),(.19,.12,.1))
        for j in range(3):
            box(f"TreeBranch{i}_{j}",(x+(j-1)*.9,3.8+j*.55,z),(2.5,.28,.42),(.18,.12,.1))
        trees.append((x,z))
    for i,(x,z) in enumerate(PUMPKIN_POSITIONS):
        node=box(f"Pumpkin{i}",(x,.48,z),(1,.95,1),(.95,.27,.035),isNeon=True)
        box(f"PumpkinStem{i}",(x,1.05,z),(.16,.25,.16),(.17,.3,.08))
        pumpkins.append((x,z))
    box("Moon",(0,31,24),(5,5,.2),(.92,.94,1),isNeon=True,isPassable=True)
    for i in range(4):
        box(f"Cloud{i}",(-15+i*9,29+i%2,23),(8,1.2,1),(.18,.2,.26),isPassable=True)
    box("OpenGraveRim",(0,.08,17),(3,.16,4),(.19,.16,.13))
    box("SkullPedestal",(4,.9,-24),(1.1,1.8,1.1),(.4,.36,.3))
    return {"graves":graves,"trees":trees,"pumpkins":pumpkins,"candles":list(CANDLE_GRAVES),
            "epitaphs":list(EPITAPHS),"zombie_speed":ZOMBIE_SPEED}
