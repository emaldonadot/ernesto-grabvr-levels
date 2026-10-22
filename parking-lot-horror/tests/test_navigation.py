"""Independent swept-path checks against emitted native MonsterAI bytecode."""
import json,math,unittest
from pathlib import Path
from native_vm import World,ROOT
M=json.loads((ROOT/'docs/manifest.json').read_text())

def hits(a,b,r,margin=1e-5):
    # Independent slab clipping; open interior and tiny numerical tolerance.
    lo,hi=0.,1.
    for axis,low,high in [(0,'xmin','xmax'),(1,'zmin','zmax')]:
        lower,upper=r[low]+margin,r[high]-margin;delta=b[axis]-a[axis]
        if abs(delta)<1e-12:
            if not lower<a[axis]<upper:return False
        else:
            t0=(lower-a[axis])/delta;t1=(upper-a[axis])/delta
            lo=max(lo,min(t0,t1));hi=min(hi,max(t0,t1))
            if lo>hi:return False
    return hi>=0 and lo<=1

class GroundNavigation(unittest.TestCase):
    def scene(self,start,target,players=1):
        self.assertIn('navigation',M,'Rebuild level with navigation module first')
        w=World(players=players);w.frames(4)
        w.progs=[p for p in w.progs if p.name in ('MonsterAI','NavClock')]
        for p in w.players:p['vars'][2]=1
        w.players[0]['vars'][2]=0;w.players[0]['pos']=[target[0],1.6,target[1]]
        w.pos('Monster').update(x=start[0],y=0,z=start[1]);w.pos('Clock')['x']=1
        return w
    def route(self,start,target,seconds=60,players=1):
        w=self.scene(start,target,players);trace=[start]
        for frame in range(seconds*60):
            w.tick();p=w.pos('Monster');point=(p['x'],p['z'])
            self.assertAlmostEqual(p['y'],0)
            if point!=trace[-1]:
                for r in M['navigation']['obstacles']:
                    self.assertFalse(hits(trace[-1],point,r),f'{r["name"]}: {trace[-1]} -> {point}')
                trace.append(point)
            if w.players[0]['vars'][0]==1:return w,trace
        self.fail(f'No capture {start} -> {target}; stopped {trace[-1]} navA{w.pos("NavA")} navB{w.pos("NavB")}')
    def test_direct_diagonal_crosses_empty_stalls(self):
        w,trace=self.route((1,-5),(9,7),players=10)
        self.assertGreater(len(trace),10)
        # Both coordinates change together: no aisle alignment doglegs.
        diagonal=sum(abs(b[0]-a[0])>1e-4 and abs(b[1]-a[1])>1e-4 for a,b in zip(trace,trace[1:]))
        self.assertGreater(diagonal,len(trace)*.9)
        distance=math.dist(trace[0],trace[-1]);self.assertGreater(distance/w.time,2.8)
    def test_detours_cars_columns_and_multiple_rows(self):
        for start,target in [((-14,-23.75),(-6.8,-23.75)),((-17.7,-26),(15,24)),((15,25),(-15,-25)),((-14,6),(-6,6)),((-4,-10),(-4,16))]:
            with self.subTest(start=start,target=target):self.route(start,target)
    def test_roof_or_car_interior_cannot_be_captured(self):
        car=next(r for r in M['navigation']['physicalVehicles'] if r['name']=='SportCar')
        target=((car['xmin']+car['xmax'])/2,(car['zmin']+car['zmax'])/2)
        for height in (1.6,2.8):
            w=self.scene((car['xmax']+.4,target[1]),target);w.players[0]['pos'][1]=height
            w.frames(300)
            self.assertEqual(w.players[0]['vars'][0],0)
    def test_hunt_ending_during_planning_prevents_late_step(self):
        w=self.scene((-17.7,-26),(15,24))
        # Deliberately end a hunt while the serialized block retains its PC
        # inside an instruction-budget slice rather than at the top-loop guard.
        w.tick();before=dict(w.pos('Monster'));w.pos('Clock')['x']=0
        for _ in range(30):
            w.tick();after=w.pos('Monster')
            if after['y']<0:break
            self.assertEqual((after['x'],after['z']),(before['x'],before['z']))
        self.assertEqual(w.pos('Monster')['y'],-100)

    def test_target_changes_do_not_allow_swept_car_crossing(self):
        w=self.scene((-15,-23),(-6,-23));prev=(-15,-23)
        for frame in range(1200):
            if frame==300:w.players[0]['pos']=[-15,1.6,-16]
            if frame==600:w.players[0]['pos']=[1,1.6,-26]
            if frame==900:w.players[0]['pos']=[13,1.6,10]
            if w.players[0]['vars'][0]:break
            w.tick();p=w.pos('Monster');current=(p['x'],p['z'])
            for r in M['navigation']['obstacles']:self.assertFalse(hits(prev,current,r),r['name'])
            prev=current

if __name__=='__main__':unittest.main()
