"""Regression checks for reported headset failures; does not emulate GRAB physics."""
import math,unittest
from native_vm import World,VM

class PlaytestFixes(unittest.TestCase):
 def world(self):
  w=World();w.frames(4);return w
 def test_closets_face_rooms_and_all_ten_native_doors_toggle(self):
  w=self.world()
  for i in range(1,11):
   side=-1 if i<=5 else 1
   c=w.byname[f'Closet{i}']['levelNodeGroup'];q=c['rotation']
   # Local +Z points backward: rear of closet lies at +/-8, front into room.
   yaw=2*math.atan2(q['y'],q['w'])
   rear=c['position']['x']+.65*math.sin(yaw)
   front=c['position']['x']-.85*math.sin(yaw)
   self.assertAlmostEqual(rear,side*8)
   self.assertLess(abs(front),abs(c['position']['x']))
   self.assertIn(w.byname[f'ClosetDoor{i}'],c['childNodes'])
   t=w.byname[f'ClosetDoorUse{i}']['levelNodeTrigger']['triggerTargets'][0]['triggerTargetAnimation']
   self.assertIs(w.nodes[t['objectID']],w.byname[f'ClosetDoor{i}'])
   door=w.byname[f'ClosetDoor{i}']['levelNodeGroup']
   w.pulse(f'ClosetDoorUse{i}',0);self.assertGreater(door['rotation']['y'],.7)
   w.pulse(f'ClosetDoorUse{i}',0);self.assertAlmostEqual(door['rotation']['y'],0)
 def test_hiding_closes_closet_and_leave_opens_toward_room(self):
  w=self.world();w.pulse('ClosetDoorUse1',0);w.pulse('ClosetUse1',0)
  self.assertEqual(w.players[0]['vars'][2],1)
  self.assertEqual(w.byname['ClosetDoor1']['levelNodeGroup']['rotation']['y'],0)
  w.frames(35);w.pulse('ClosetLeave1',0)
  self.assertEqual(w.players[0]['vars'][2],0)
  self.assertGreater(w.players[0]['pos'][0],-7.35)
  self.assertGreater(w.byname['ClosetDoor1']['levelNodeGroup']['rotation']['y'],.7)
 def test_hunt_fog_is_dense_and_locally_applied_then_clears(self):
  w=self.world();w.pos('Clock').update(x=0,z=59.99)
  w.frames(2)
  self.assertEqual(w.pos('Clock')['x'],1)
  self.assertEqual(w.ambience['fogDensity'],.72)
  density=w.ambience['fogDensity'];coefficient=.5*density**4+.000001*(1-density**4)
  self.assertGreater(1-math.exp(-10*coefficient),.7)
  w.pos('Clock')['z']=59.99;w.frames(2)
  self.assertEqual(w.ambience['fogDensity'],0)
  self.assertFalse(w.byname['LocalFog']['levelNodeGASM']['isShared'])
  self.assertFalse(w.byname['FogOn']['levelNodeTrigger']['isShared'])
 def test_late_client_applies_current_hunt_fog(self):
  w=self.world();w.pos('Clock')['x']=1
  client=VM(w,w.byname['LocalFog']['levelNodeGASM']);w.dt=1/60;client.run();client.run()
  self.assertEqual(w.ambience['fogDensity'],.72)
 def test_all_dead_countdown_five_seconds_and_revive_every_client(self):
  w=World(players=10);w.frames(4)
  for player in w.players[1:]:
   other=VM(w,w.byname['LocalSpectator']['levelNodeGASM']);other.local_id=player['id'];other.name='OtherClient';w.progs.append(other)
  w.frames(3)
  w.pulse('DoorUse1',0);w.pulse('DrawerUse1',0);w.pulse('ClosetDoorUse1',0)
  w.pos('Clock').update(x=1,y=4,z=20);w.pos('KeyState').update(x=2,y=0,z=2);w.pos('ExitState')['x']=1
  for p in w.players:p['vars'][0]=1
  w.tick(.01)
  for number in range(5,0,-1):
   self.assertEqual(w.pos('Round')['y'],number)
   sign=w.byname[f'Restart{number}']['levelNodeSign'];self.assertEqual(sign['position']['y'],9.8)
   self.assertTrue(all(p['vars'][0]==1 for p in w.players))
   if number>1:w.tick(1)
  w.tick(.99);self.assertTrue(all(p['vars'][0]==1 for p in w.players))
  w.tick(.01);w.frames(3)
  self.assertEqual(w.pos('Round')['z'],2)
  for p in w.players:
   self.assertEqual(p['vars'][0],0);self.assertEqual(p['vars'][2:4],[0,0])
   self.assertLess(abs(p['pos'][0]),2);self.assertLess(p['pos'][1],1);self.assertLess(p['pos'][2],4)
  self.assertEqual(w.pos('Clock')['x'],0);self.assertEqual(w.pos('Clock')['y'],0)
  self.assertEqual(w.pos('KeyState'),dict(x=0,y=0,z=0));self.assertEqual(w.pos('ExitState')['x'],0)
  for prefix in ['Door','Drawer','ClosetDoor']:
   obj=w.byname[f'{prefix}1']['levelNodeGroup'];self.assertEqual(obj['rotation']['y'],0)
  self.assertAlmostEqual(w.pos('Drawer1')['z'],2.15)
  for i in range(1,6):self.assertEqual(w.byname[f'Restart{i}']['levelNodeSign']['position']['y'],-100)
  # The exit trigger must rearm after its animation was reset closed.
  w.pos('KeyState').update(x=0,y=w.players[0]['id']+1,z=1)
  w.pulse('ExitUse',0)
  self.assertGreater(w.byname['ExitDoor']['levelNodeGroup']['rotation']['y'],.7)
 def test_one_survivor_empty_lobby_and_escaped_player_do_not_trigger_wipe(self):
  for count,statuses in [(0,[]),(2,[1,0]),(2,[1,2]),(2,[2,2])]:
   w=World(players=count);w.frames(4)
   for p,status in zip(w.players,statuses):p['vars'][0]=status
   w.frames(7,1)
   self.assertEqual(w.pos('Round')['x'],0);self.assertEqual(w.pos('Round')['z'],1)
 def test_initial_and_relocated_gems_fit_three_distinct_drawers(self):
  w=World()
  for i in range(1,4):
   self.assertGreater(w.pos(f'Gem{i}')['y'],1)
  w.frames(4)
  for hunt in range(4):
   previous=[w.pos(n)['x'] for n in ['LootA','LootB','LootC']]
   w.pos('Clock').update(x=1,z=59.99);w.frames(5)
   assigned=[w.pos(n)['x'] for n in ['LootA','LootB','LootC']]
   self.assertEqual(len(set(assigned)),3)
   self.assertTrue(set(previous).isdisjoint(assigned))
   for i,(old,new) in enumerate(zip(previous,assigned),1):
    self.assertNotEqual(old,new)
    gem=w.pos(f'Gem{i}');drawer=w.pos(f'Drawer{int(new)}')
    self.assertAlmostEqual(gem['x'],drawer['x']);self.assertAlmostEqual(gem['z'],drawer['z'])
    self.assertGreater(gem['y']-.1,drawer['y']+.035)
    self.assertLess(gem['y']+.1,1.235)
    self.assertEqual(w.physics[f'Gem{i}'],4)
 def test_monster_eyes_face_walk_direction_and_speed_is_3_4(self):
  for mx,mz,px,pz in [(0,10,0,25),(0,20,0,5),(-1,10,0,10),(1,10,0,10)]:
   w=self.world();w.players[0]['pos']=[px,1.6,pz];w.players[1]['vars'][0]=1
   w.pos('Monster').update(x=mx,y=0,z=mz);w.pos('Clock')['x']=1
   w.progs=[p for p in w.progs if p.name=='MonsterAI'];w.tick(.1)
   monster=w.pos('Monster');dx=monster['x']-mx;dz=monster['z']-mz
   self.assertAlmostEqual(math.hypot(dx,dz),.34)
   q=w.byname['Monster']['levelNodeGroup']['rotation'];yaw=2*math.atan2(q['y'],q['w'])
   self.assertAlmostEqual(-math.sin(yaw),dx/.34)
   self.assertAlmostEqual(-math.cos(yaw),dz/.34)

if __name__=='__main__':unittest.main()
