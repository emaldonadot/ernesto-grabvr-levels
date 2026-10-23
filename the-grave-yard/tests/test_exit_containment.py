"""Check serialized exit flow and enclosure geometry, without engine simulation."""
import unittest
from native_vm import World

class ExitContainment(unittest.TestCase):
    def world(self):
        w=World();w.frames(5);return w
    def data(self,w,name):
        n=w.byname[name];return n[next(k for k in n if k.startswith('levelNode'))]
    def bounds(self,d):
        return {a:(d['position'][a]-d['scale'][a]/2,d['position'][a]+d['scale'][a]/2) for a in 'xyz'}
    def test_eight_meter_barriers_exceed_climbable_trees_and_are_solid(self):
        w=self.world()
        walls=['FenceSide-24','FenceSide24','FenceBack','FenceFront-13.5','FenceFront13.5']
        max_tree=max(self.bounds(self.data(w,name))['y'][1] for name in w.byname if name.startswith(('TreeTrunk','TreeBranch','TreeClimbHold','TreeDeadTwig')))
        for name in walls:
            d=self.data(w,name);b=self.bounds(d)
            self.assertEqual(b['y'],(0,8))
            self.assertGreater(b['y'][1],max_tree+2)
            for flag in ('isGrabbable','isGrapplable','isPassable'):self.assertFalse(d[flag])
    def test_closed_perimeter_has_no_corner_or_gate_header_gaps(self):
        w=self.world();parts=[]
        for name in ['FenceSide-24','FenceSide24','FenceBack','FenceFront-13.5','FenceFront13.5','GateLeftPost','GateRightPost','GateHeader']:
            parts.append(self.bounds(self.data(w,name)))
        # Closed gate panel is local to the identity group at (0,0,-28).
        door=self.data(w,'ExitDoor');panel=door['childNodes'][0]['levelNodeStatic']
        panel=dict(panel,position={a:panel['position'][a]+door['position'][a] for a in 'xyz'})
        parts.append(self.bounds(panel))
        def covered(x,y,z):return any(all(b[a][0]-.00001<=v<=b[a][1]+.00001 for a,v in zip('xyz',(x,y,z))) for b in parts)
        for y in (.05,1.6,3.49,3.51,5,7.9):
            for i in range(481):
                x=-24+i*.1
                self.assertTrue(covered(x,y,-28),(x,y,-28))
                self.assertTrue(covered(x,y,28),(x,y,28))
            for i in range(561):
                z=-28+i*.1
                self.assertTrue(covered(-24,y,z),(-24,y,z))
                self.assertTrue(covered(24,y,z),(24,y,z))
    def test_sky_cap_is_transparent_solid_and_overlaps_all_walls(self):
        w=self.world();d=self.data(w,'YardSafetyCap');b=self.bounds(d)
        self.assertTrue(d['isTransparent']);self.assertLess(d['color1']['a'],.1)
        self.assertFalse(d['isPassable']);self.assertFalse(d['isGrabbable']);self.assertFalse(d['isGrapplable'])
        self.assertEqual(b['y'][0],7.9)
        self.assertLess(b['x'][0],-24);self.assertGreater(b['x'][1],24)
        self.assertLess(b['z'][0],-28);self.assertGreater(b['z'][1],28)
    def test_staged_guidance_requires_physical_release_then_walk_to_finish(self):
        w=self.world()
        self.assertEqual(self.data(w,'ExitGuideWait')['position']['y'],2.65)
        w.pos('Clock')['y']=5;w.frames(6)
        self.assertEqual(self.data(w,'ExitGuideReady')['position']['y'],2.65)
        w.hold('GoldenSkull',1);w.frames(6)
        self.assertEqual(self.data(w,'ExitGuideHeld')['position']['y'],2.65)
        w.pos('GoldenSkull').update(x=4,y=2.15,z=-24)
        w.players[1]['hands'][3]=[4,2.15,-24];w.frames(5)
        self.assertEqual(w.pos('ExitState')['x'],0)
        w.physics['GoldenSkull']=4;w.frames(8)
        self.assertEqual(w.pos('ExitState')['x'],1)
        self.assertEqual(self.data(w,'ExitGuideOpen')['position']['y'],2.65)
        self.assertEqual(self.data(w,'Finish')['position'],dict(x=0,y=1.2,z=-34))
        for player in (1,0):
            w.players[player]['pos']=[0,1.6,-34]
            w.pulse('Escape',player)
            self.assertEqual(w.players[player]['vars'][0],2)
            self.assertEqual(w.players[player]['pos'],[0,1.6,-34])
    def test_escape_bookkeeping_rejects_touch_without_reaching_finish(self):
        w=self.world();w.pos('Clock')['y']=5;w.pos('ExitState')['x']=1;w.frames(5)
        w.players[1]['pos']=[.9,1.6,-33.1];w.pulse('Escape',1)
        self.assertEqual(w.players[1]['vars'][0],0)
        w.players[1]['pos']=[0,1.6,-34];w.pulse('Escape',1)
        self.assertEqual(w.players[1]['vars'][0],2)
    def test_reset_restores_locked_guidance_and_hides_finish(self):
        w=self.world();w.pos('Clock')['y']=5;w.pos('ExitState')['x']=1;w.frames(5)
        w.pos('Clock')['y']=0;w.pos('ExitState')['x']=0;w.frames(5)
        self.assertEqual(self.data(w,'ExitGuideWait')['position']['y'],2.65)
        self.assertEqual(self.data(w,'ExitGuideOpen')['position']['y'],-100)
        self.assertEqual(self.data(w,'Finish')['position']['y'],-100)
    def test_socket_ring_and_path_do_not_obstruct_players_or_skull(self):
        w=self.world()
        for name in [f'SkullSocketRing{i}' for i in range(4)]+[f'ExitPathLight{i}' for i in range(5)]:
            d=self.data(w,name);self.assertTrue(d['isPassable']);self.assertTrue(d['isNeon'])
        floor=self.bounds(self.data(w,'ExitRoomFloor'))
        for i in (2,3,4):
            d=self.data(w,f'ExitPathLight{i}')
            for a in ('x','z'):self.assertTrue(floor[a][0]<d['position'][a]<floor[a][1])
        self.assertGreaterEqual(floor['z'][1],-28)
        self.assertLessEqual(floor['z'][0],-35)
