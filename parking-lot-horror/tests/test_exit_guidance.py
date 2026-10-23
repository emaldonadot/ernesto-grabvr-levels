"""Exit instruction, key authorization and physical route regressions."""
import unittest
from native_vm import World

class ExitGuidance(unittest.TestCase):
 def world(self):
  w=World();w.frames(4);return w
 def pos(self,w,name):
  node=w.byname[name];return node[next(k for k in node if k.startswith('levelNode'))]['position']
 def collect(self,w,player=1):
  w.pos('Clock')['y']=5;w.pos('KeyState').update(x=1,z=1)
  w.pulse('KeyUse',player)
  self.assertEqual(w.pos('KeyState')['y'],w.players[player]['id']+1)
 def test_pickup_instructions_approach_unlock_and_two_survivors_finish(self):
  w=self.world();self.collect(w)
  self.assertEqual(self.pos(w,'KeyCollected')['y'],2.4)
  self.assertLess(self.pos(w,'Finish')['y'],-50)
  w.players[1]['pos']=[0,1.6,28.4];w.frames(4)
  self.assertEqual(w.pos('ExitState')['x'],1)
  self.assertEqual(self.pos(w,'ExitReady')['y'],3.5)
  self.assertLess(self.pos(w,'ExitLabel')['y'],-50)
  self.assertEqual(self.pos(w,'Finish'),dict(x=0,y=1.2,z=35))
  self.assertEqual(w.players[1]['pos'],[0,1.6,28.4])
  for player in (1,0):
   w.players[player]['pos']=[0,1.6,35];w.pulse('Escape',player)
   self.assertEqual(w.players[player]['vars'][0],2)
   self.assertEqual(w.players[player]['pos'],[0,1.6,35])
 def test_unauthorized_early_distant_and_elevated_approaches_do_not_unlock(self):
  w=self.world();w.pos('KeyState')['y']=12
  w.players[1]['pos']=[0,1.6,28.4];w.frames(3)
  self.assertEqual(w.pos('ExitState')['x'],0) # fifth hunt guard
  w.players[1]['pos']=[10,1.6,26]
  self.collect(w)
  w.players[1]['pos']=[10,1.6,26];w.players[0]['pos']=[0,1.6,28.4];w.frames(4)
  self.assertEqual(w.pos('ExitState')['x'],0)
  for pos in ([0,6,28.4],[0,1.6,25],[4,1.6,28.4]):
   w.players[1]['pos']=list(pos);w.frames(3)
   self.assertEqual(w.pos('ExitState')['x'],0)
  w.pulse('ExitUse',0);self.assertEqual(w.pos('ExitState')['x'],0)
  w.pulse('ExitUse',1);self.assertEqual(w.pos('ExitState')['x'],1)
 def test_wipe_clears_stage_feedback_and_rearms_exit(self):
  w=self.world();self.collect(w);w.pulse('ExitUse',1)
  for p in w.players:p['vars'][0]=1
  w.frames(2);w.frames(6,1);w.frames(5)
  self.assertEqual(w.pos('ExitState')['x'],0)
  self.assertLess(self.pos(w,'ExitReady')['y'],-50)
  self.assertLess(self.pos(w,'KeyCollected')['y'],-50)
  self.assertEqual(self.pos(w,'ExitLabel')['y'],3.5)
  self.collect(w,0);w.players[0]['pos']=[0,1.6,28.4];w.frames(4)
  self.assertEqual(w.pos('ExitState')['x'],1)
 def test_gold_lock_moves_with_gate_and_green_strips_stay_supported(self):
  w=self.world();door=w.byname['ExitDoor']['levelNodeGroup']
  self.assertIn(w.byname['ExitLock'],door['childNodes'])
  lock=w.byname['ExitLock']['levelNodeStatic'];use=w.byname['ExitUse']['levelNodeTrigger']
  for axis in 'xyz':
   absolute=door['position'][axis]+lock['position'][axis]
   self.assertLessEqual(abs(absolute-use['position'][axis]),use['scale'][axis]/2)
  floor=w.byname['ExitRoomFloor']['levelNodeStatic']
  for i in range(1,5):
   strip=w.byname[f'FinishPath{i}']['levelNodeStatic']
   self.assertTrue(strip['isNeon']);self.assertTrue(strip['isPassable'])
   self.assertGreater(strip['position']['z'],29.35)
   self.assertLess(strip['position']['z'],35)
   self.assertLess(strip['position']['y'],.1)
   for axis in ('x','z'):
    self.assertLessEqual(abs(strip['position'][axis]-floor['position'][axis])+strip['scale'][axis]/2,floor['scale'][axis]/2)
  self.assertIn('INVENTORY',w.byname['KeyInstructions']['levelNodeSign']['text'])
  self.assertIn('GREEN STRIPS',w.byname['ExitReady']['levelNodeSign']['text'])
