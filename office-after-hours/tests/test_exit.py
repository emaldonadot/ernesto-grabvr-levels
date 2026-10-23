"""Exercise inventory pickup through the actual serialized exit controllers."""
import unittest
from native_vm import World

class ExitFlow(unittest.TestCase):
 def world(self):
  w=World();w.frames(3);return w
 def pos(self,w,name):
  node=w.byname[name];return node[next(k for k in node if k.startswith('levelNode'))]['position']
 def collect(self,w,player=0):
  w.pos('KeyState').update(x=1,y=0,z=1)
  if not w.pos('Room1')['y']:w.pulse('DrawerUse1',player)
  w.pulse('LootUse1',player)
  self.assertEqual(w.pos('KeyState')['y'],w.players[player]['id']+1)
  self.assertEqual(w.pos('KeyState')['x'],0)
 def test_pickup_feedback_and_approach_unlock_then_walk_to_finish(self):
  w=self.world();self.collect(w,1)
  self.assertEqual(self.pos(w,'KeyCollected')['y'],2.3)
  self.assertEqual(self.pos(w,'Finish')['y'],-100)
  w.players[1]['pos']=[0,1.6,31];before=list(w.players[1]['pos']);w.frames(4)
  self.assertEqual(w.pos('ExitState')['x'],1)
  self.assertEqual(self.pos(w,'Finish'),dict(x=0,y=1.2,z=33))
  self.assertGreater(w.byname['ExitDoor']['levelNodeGroup']['rotation']['y'],.7)
  self.assertEqual(w.players[1]['pos'],before) # No local or remote teleport.
  w.players[1]['pos']=[0,1.6,33];w.pulse('Escape',1)
  self.assertEqual(w.players[1]['vars'][0],2)
  self.assertEqual(w.players[1]['pos'],[0,1.6,33])
  w.players[0]['pos']=[0,1.6,33];w.pulse('Escape',0)
  self.assertEqual(w.players[0]['vars'][0],2)
 def test_non_holder_cannot_unlock_and_touch_path_still_works(self):
  w=self.world();self.collect(w,1)
  w.players[0]['pos']=[0,1.6,31];w.pulse('ExitUse',0)
  self.assertEqual(w.pos('ExitState')['x'],0)
  w.pulse('ExitUse',1);self.assertEqual(w.pos('ExitState')['x'],1)
 def test_balcony_or_distant_carrier_does_not_unlock(self):
  w=self.world();self.collect(w,1)
  for pos in ([0,9,31],[3,1.6,31],[0,1.6,28]):
   w.players[1]['pos']=list(pos);w.frames(4)
   self.assertEqual(w.pos('ExitState')['x'],0)
 def test_escape_requires_unlock_and_actual_finish_proximity(self):
  w=self.world();w.players[1]['pos']=[0,1.6,33];w.pulse('Escape',1)
  self.assertEqual(w.players[1]['vars'][0],0)
  w.pos('KeyState').update(x=0,y=11,z=1);w.pulse('ExitUse',0)
  w.players[1]['pos']=[0,1.6,32.4];w.pulse('Escape',1)
  self.assertEqual(w.players[1]['vars'][0],0)
  w.players[1]['pos']=[0,1.6,33];w.pulse('Escape',1)
  self.assertEqual(w.players[1]['vars'][0],2)
 def test_reset_hides_finish_and_allows_next_key_unlock(self):
  w=self.world();self.collect(w,1);w.pulse('ExitUse',1)
  w.pos('ExitState')['x']=0;w.pos('KeyState').update(x=0,y=0,z=0);w.frames(4)
  self.assertEqual(self.pos(w,'Finish')['y'],-100)
  self.assertEqual(self.pos(w,'KeyCollected')['y'],-100)
  self.collect(w,0);w.players[0]['pos']=[0,1.6,31];w.frames(4)
  self.assertEqual(w.pos('ExitState')['x'],1)
  self.assertEqual(self.pos(w,'Finish')['y'],1.2)
 def test_finish_fits_existing_chamber_and_controller_never_teleports(self):
  w=self.world();f=self.pos(w,'Finish');self.assertEqual((f['x'],f['z']),(0,33))
  self.assertEqual(self.pos(w,'Floor')['y']+w.byname['Floor']['levelNodeStatic']['scale']['y']/2,0)
  back=w.byname['End34']['levelNodeStatic'];self.assertGreater(back['position']['z']-back['scale']['z']/2,33+.65)
  g=w.byname['ExitController']['levelNodeGASM'];player=next(c for c in g['connections'] if c['name']=='@player')
  prop=next(p for p in player['properties'] if 'player' in p)
  tel={prop['components'][i]['outputRegisterIndex'] for i in range(20,25)}
  for ins in g['program']['instructions']:
   if ins['type']==1:
    dst=ins['operands'][0];self.assertFalse(dst['type']==1 and dst['index'] in tel)
