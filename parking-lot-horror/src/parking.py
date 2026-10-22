"""Covered 60-space parking structure. Geometry only; gameplay lives in build.py.

All coordinates are metres, Y up. Each outside row contains ten stalls;
each of the two inner back-to-back banks contains twenty stalls.
"""

ROWS = (-23.75, -11.65, -6.05, 6.05, 11.65, 23.75)
AISLES = (-17.7, 0.0, 17.7)
STALL_WIDTH = 2.9
STALL_DEPTH = 5.6


def build(ctx):
    """Build static architecture using the integration builder's native helpers."""
    box, sign = ctx['box'], ctx['sign']
    concrete = (.19, .215, .225)
    dark_concrete = (.105, .12, .13)
    white = (.74, .76, .69)
    yellow = (.78, .57, .12)
    bounds = dict(xmin=-21.5, xmax=21.5, zmin=-29.5, zmax=29.5)
    box('ParkingFloor', (0, -.16, 0), (43, .32, 59), dark_concrete)
    box('ParkingRoof', (0, 4.60, 0), (43, .24, 59), concrete)

    # Tall enclosing concrete keeps the chase in the actual playable footprint.
    # The north opening is left clear for LevelCreator's animated escape gate.
    for side in (-1, 1):
        x = side * 21.35
        if side == 1:
            box('ParkingSideWall1Lower', (x, .55, 0), (.30, 1.10, 59), concrete)
            box('ParkingSideWall1Upper', (x, 3.55, 0), (.30, 1.46, 59), concrete)
            box('ParkingSideWall1Window', (x, 1.965, 0), (.30, 1.73, 59),
                (.27, .43, .46), isTransparent=True)
        else:
            box(f'ParkingSideWall{side}', (x, 2.14, 0), (.30, 4.28, 59), concrete)
        box(f'ParkingSideStripe{side}', (x-side*.16, 1.18, 0), (.025, .18, 58), yellow)
    box('ParkingSouthWall', (0, 2.14, -29.35), (43, 4.28, .30), concrete)
    for side in (-1, 1):
        box(f'ParkingNorthWall{side}', (side*12.1, 2.14, 29.35),
            (18.8, 4.28, .30), concrete)
    box('ParkingGateLintel', (0, 4.05, 29.35), (5.4, .45, .30), concrete)

    columns, obstacles = [], []
    # Back-edge columns leave all three 6.5m aisles and end cross-aisles clear.
    # Van doors slide alongside the body, not into these back-edge columns.
    for zi, z in enumerate((-28.2, -8.85, 8.85, 28.2)):
        box(f'ParkingBeam{zi}', (0, 4.26, z), (42.4, .42, .60), (.145, .16, .17))
        for xi, x in enumerate((-14.5, -5.8, 5.8, 14.5)):
            name = f'ParkingColumn{zi}_{xi}'
            box(name, (x, 2.10, z), (.50, 4.20, .50), (.28, .295, .29))
            box(name+'Base', (x, .22, z), (.66, .44, .66), (.14, .155, .16))
            box(name+'Band', (x, 1.10, z), (.515, .23, .515), yellow)
            footprint = dict(name=name, xmin=x-.33, xmax=x+.33,
                             zmin=z-.33, zmax=z+.33)
            columns.append(dict(name=name, x=x, z=z, height=4.2))
            obstacles.append(footprint)

    stalls = []
    headings = (0, 180, 0, 180, 0, 180)  # Local +Z faces its drive aisle.
    for r, z in enumerate(ROWS):
        for edge in range(11):
            x = -14.5 + STALL_WIDTH*edge
            box(f'StallDivider{r}_{edge}', (x, .012, z),
                (.075, .024, STALL_DEPTH), white, isPassable=True)
        # White back stripe defines stall depth; open front meets the aisle.
        back_z = z - 2.8 if headings[r] == 0 else z + 2.8
        box(f'StallBackLine{r}', (0, .013, back_z),
            (29.075, .026, .075), white, isPassable=True)
        for slot in range(10):
            stalls.append(dict(id=r*10+slot+1, row=r, slot=slot,
                               x=round(-13.05+STALL_WIDTH*slot, 4), z=z,
                               yaw=headings[r], width=STALL_WIDTH,
                               depth=STALL_DEPTH))
        # Row identification faces the side cross-aisle, above head height.
        sign(f'ParkingRowLabel{r}', f'ROW {chr(65+r)}  /  10 SPACES',
             (-15.15, 2.65, z), .26, 90, c=(.76, .82, .77))

    # Nine fluorescent fixtures and metal housings give a recognisable low
    # concrete garage ceiling without expensive per-stall light nodes.
    for ai, z in enumerate(AISLES):
        for li, x in enumerate((-10.0, 0.0, 10.0)):
            box(f'ParkingLightHousing{ai}_{li}', (x, 4.32, z),
                (2.45, .13, .52), (.08, .10, .11))
            for tube, dz in enumerate((-.13, .13)):
                box(f'ParkingLightTube{ai}_{li}_{tube}', (x, 4.235, z+dz),
                    (2.20, .04, .07), (.63, .76, .68), isNeon=True)
        # A pair of yellow bands frames each row access lane on the end aisles.
        for side in (-1, 1):
            box(f'CrossAisleGuide{ai}_{side}', (side*19.8, .016, z),
                (.10, .032, 5.7), yellow, isPassable=True)

    # Exit readability comes from a sign rather than a false additional opening.
    sign('ParkingEscapeSign', 'ESCAPE GATE  /  KEY REQUIRED',
         (0, 3.65, 29.12), .42, 180, c=(.40, .95, .64))
    sign('ParkingSouthLocator', 'PARKING B2  /  60 SPACES',
         (0, 3.45, -29.12), .46, 0, c=(.82, .86, .78))
    return dict(
        capacity=60, rows=list(ROWS), stalls=stalls,
        rowHeadings=list(headings), stallWidth=STALL_WIDTH,
        stallDepth=STALL_DEPTH, aisles=list(AISLES), aisleWidth=6.5,
        sideCrossAisles=[-17.7, 17.7], columns=columns,
        floorBounds=bounds, ceilingY=4.48, spawn=[0, .1, -27],
        exitPoint=[0, .1, 28], gateOpening=dict(xmin=-2.7, xmax=2.7, z=29.35),
        obstacles=obstacles,
    )
