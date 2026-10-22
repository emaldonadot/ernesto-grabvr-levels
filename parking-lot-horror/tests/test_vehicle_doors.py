"""Serialized geometry checks: moving assemblies, not animation mocks alone."""
import json, math, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def xyz(d):return tuple(d.get(k,0) for k in 'xyz')
def yaw_rotate(p,q):
    a=2*math.atan2(q.get('y',0),q.get('w',1));x,y,z=p
    return (x*math.cos(a)+z*math.sin(a),y,-x*math.sin(a)+z*math.cos(a))
def plus(a,b):return tuple(x+y for x,y in zip(a,b))
def centre(node):return xyz(node['levelNodeStatic']['position'])

class VehicleDoorAssemblies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.level=json.loads((ROOT/'dist/parking-lot-horror.json').read_text())
        cls.manifest=json.loads((ROOT/'docs/manifest.json').read_text())
        nodes=[]
        def visit(items):
            for n in items:
                nodes.append(n)
                if 'levelNodeGroup' in n:visit(n['levelNodeGroup']['childNodes'])
        visit(cls.level['levelNodes'])
        cls.named={name:nodes[oid-1] for name,oid in cls.manifest['ids'].items()}

    def test_all_six_glass_frames_handles_move_with_their_door(self):
        doors=self.manifest['fleet']['doors'];self.assertEqual(len(doors),6)
        for d in doors:
            with self.subTest(door=d['name']):
                door=self.named[d['name']];data=door['levelNodeGroup']
                parent=self.named[d['vehicle']]['levelNodeGroup']
                self.assertIn(door,parent['childNodes'])
                children=data['childNodes'];end=door['animations'][0]['frames'][-1]
                origin=xyz(data['position']);root=xyz(parent['position'])
                for index in [d['glassChild'],d['handleChild'],*d['frameChildren']]:
                    p=centre(children[index])
                    closed=plus(root,yaw_rotate(plus(origin,p),parent['rotation']))
                    opened=plus(root,yaw_rotate(plus(origin,plus(yaw_rotate(p,end['rotation']),xyz(end['position']))),parent['rotation']))
                    distance=math.dist(opened,closed)
                    if d['kind']=='hinge':
                        angle=2*math.atan2(end['rotation']['y'],end['rotation']['w'])
                        self.assertAlmostEqual(distance,2*math.hypot(p[0],p[2])*abs(math.sin(angle/2)))
                    else:self.assertAlmostEqual(distance,1.5)
                    # The narrow front frame is next to the hinge and correctly
                    # travels only centimetres; glass and handle travel much farther.
                    self.assertGreater(distance,.35 if index in [d['glassChild'],d['handleChild']] else .02)
                if d['kind']=='hinge':
                    self.assertLess(end['rotation']['y'],0,'driver door must swing outside left cabin wall')
                    self.assertIsNotNone(d['mirrorChild'])
                else:self.assertAlmostEqual(end['position']['z'],1.5)

    def test_no_fixed_side_glass_covers_any_moving_window_aperture(self):
        glass=(.055,.14,.19)
        for d in self.manifest['fleet']['doors']:
            a=d['aperture'];vehicle=self.named[d['vehicle']]['levelNodeGroup']
            for n in vehicle['childNodes']:
                if 'levelNodeStatic' not in n:continue
                s=n['levelNodeStatic'];c=s.get('color1',{})
                if not all(abs(c.get(k,0)-v)<1e-5 for k,v in zip('rgb',glass)):continue
                x,y,z=xyz(s['position']);sx,sy,sz=xyz(s['scale'])
                # Side panes have thin X; windscreens/rear glass face Z.
                if sx>.15 or abs(x-a['x'])>.1:continue
                overlap_z=min(z+sz/2,a['zmax'])-max(z-sz/2,a['zmin'])
                overlap_y=min(y+sy/2,a['ymax'])-max(y-sy/2,a['ymin'])
                self.assertFalse(overlap_z>.02 and overlap_y>.02,
                    f"{d['name']} still has fixed glass in its opening at {(x,y,z)}")

    def test_every_vehicle_has_ground_obstacle_enclosing_body_and_doors(self):
        fleet=self.manifest['fleet'];obstacles={o['name']:o for o in fleet['obstacles']}
        self.assertEqual(len(obstacles),9)
        for v in fleet['vehicles']:
            o=obstacles[v['id']];x,_,z=v['center'];w,h,length=v['bounds']
            self.assertLess(o['xmin'],x-w/2);self.assertGreater(o['xmax'],x+w/2)
            self.assertLess(o['zmin'],z-length/2);self.assertGreater(o['zmax'],z+length/2)
            self.assertGreater(o['topY'],h)

if __name__=='__main__':unittest.main()
