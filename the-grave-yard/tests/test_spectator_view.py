"""Check transparent sightlines while retaining the tall collision boundary."""
import unittest
from native_vm import World

class SpectatorView(unittest.TestCase):
    def test_gallery_and_perimeter_do_not_occlude_survivors(self):
        w=World()
        for name in ('SpectatorSide25.5','SpectatorSide30.5','FenceSide24'):
            d=w.byname[name]['levelNodeStatic']
            self.assertTrue(d['isTransparent'],name)
            self.assertLessEqual(d['color1']['a'],.025,name)
            self.assertFalse(d['isPassable'],name)
            self.assertFalse(d['isGrabbable'],name)
            self.assertFalse(d['isGrapplable'],name)
        wall=w.byname['FenceSide24']['levelNodeStatic']
        self.assertEqual(wall['scale']['y'],8)
        # The complete gallery walking length looks through the transparent slab.
        glass=w.byname['SpectatorSide25.5']['levelNodeStatic']
        for z in (-25,0,25):
            for d in (wall,glass):
                self.assertLessEqual(d['position']['z']-d['scale']['z']/2,z)
                self.assertGreaterEqual(d['position']['z']+d['scale']['z']/2,z)
        self.assertFalse(w.byname['FenceSide-24']['levelNodeStatic'].get('isTransparent',False))

    def test_remote_spectator_remains_separated_and_survivor_is_unchanged(self):
        w=World();w.frames(4)
        movement=next(p for p in w.progs if p.name=='LocalMovement');movement.local_id=11
        survivor=list(w.players[0]['pos'])
        w.players[1]['vars'][0]=1;w.frames(5)
        self.assertEqual(w.players[1]['pos'],[28,.1,0])
        self.assertEqual(w.players[0]['pos'],survivor)
        self.assertEqual(w.players[0]['vars'][0],0)
        self.assertFalse(w.byname['LocalMovement']['levelNodeGASM']['isShared'])
