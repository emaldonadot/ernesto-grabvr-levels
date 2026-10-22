import unittest
from native_vm import World,ROOT
import json
class Gameplay(unittest.TestCase):
 def world(self):w=World();w.frames(3);return w
 def test_schedule_key_after_fifth_completed_hunt(self):
  w=World(players=0);w.frames(1)
  for completed in range(5):
   w.frames(60,1);self.assertEqual(w.pos('Clock')['x'],1)
   self.assertEqual(w.pos('KeyState')['z'],0)
   w.frames(60,1);self.assertEqual(w.pos('Clock')['x'],0)
   self.assertEqual(w.pos('Clock')['y'],completed+1)
  self.assertGreater(w.pos('KeyState')['z'],0)
  self.assertIn(w.pos('KeyState')['x'],range(1,11))
 def test_gems_unique_and_relocated_after_hunt(self):
  w=self.world();drawers=[w.pos(n)['x'] for n in ['LootA','LootB','LootC']]
  self.assertEqual(len(set(drawers)),3)
  w.pos('LootA')['y']=11;w.pos('Clock').update(x=1,z=59.99)
  w.frames(2);self.assertEqual(w.pos('LootA')['y'],0)
  self.assertEqual(len(set(w.pos(n)['x'] for n in ['LootA','LootB','LootC'])),3)
 def test_native_doors_and_drawers_toggle_independently_of_player_state(self):
  w=self.world();w.pulse('DoorUse1',0)
  self.assertEqual(w.pos('Room1')['x'],1)
  w.pulse('DoorUse1',0);self.assertEqual(w.pos('Room1')['x'],0)
  w.pulse('DrawerUse1',0);self.assertEqual(w.pos('Room1')['y'],1)
  w.players[0]['vars'][0]=1;w.pulse('DoorUse1',0);w.pulse('DrawerUse1',0)
  self.assertEqual(w.pos('Room1')['x'],1);self.assertEqual(w.pos('Room1')['y'],0)
 def test_one_person_per_spot_and_exit_releases(self):
  w=self.world();w.pulse('ClosetUse1',0)
  self.assertEqual(w.pos('Spots1')['x'],11);self.assertEqual(w.players[0]['vars'][2],1)
  w.pulse('ClosetUse1',1);self.assertEqual(w.players[1]['vars'][2],0)
  w.frames(35);w.pulse('ClosetLeave1',0);self.assertEqual(w.pos('Spots1')['x'],0)
  w.pulse('ClosetUse1',1);self.assertEqual(w.pos('Spots1')['x'],12)
 def test_walking_out_clears_hiding(self):
  w=self.world();w.pulse('DeskUse1',0);self.assertEqual(w.players[0]['vars'][2],11)
  w.players[0]['pos']=[0,1.6,0];w.frames(3)
  self.assertEqual(w.players[0]['vars'][2],0);self.assertEqual(w.pos('Spots1')['y'],0)
 def test_physical_gem_hold_release_throw_and_drawer_movement(self):
  w=self.world();w.hold('Gem1',0);w.frames(4)
  self.assertEqual(w.pos('LootA')['y'],11)
  before=dict(w.pos('Gem1'));w.physics['Gem1']=4
  w.players[0]['hands'][3]=[9,9,9];w.pos('Gem1').update(x=1,y=2,z=5)
  w.frames(4);self.assertEqual(w.pos('LootA')['y'],0)
  self.assertEqual(w.pos('Gem1'),dict(x=1,y=2,z=5))
  room=int(w.pos('LootA')['x']);w.pulse(f'DrawerUse{room}',0)
  # GASM must leave released physics positions alone: no sticking to a drawer.
  self.assertEqual(w.pos('Gem1'),dict(x=1,y=2,z=5))
 def test_dead_players_never_get_gem_immunity_and_use_local_balcony(self):
  w=self.world();w.hold('Gem1',0);w.players[0]['vars'][0]=1;w.frames(5)
  self.assertEqual(w.pos('LootA')['y'],0)
  self.assertGreaterEqual(w.players[0]['pos'][1],8)
  controller=next(n['levelNodeGASM'] for name,n in w.byname.items() if name=='LocalSpectator')
  self.assertFalse(controller['isShared'])
 def test_immunity_hidden_and_spectator_target_filter(self):
  w=self.world();w.pos('Clock')['x']=1;w.hold('Gem1',0);w.players[1]['vars'][0]=1
  w.frames(8);self.assertEqual(w.pos('Target')['x'],0)
  w.physics['Gem1']=4;w.players[0]['vars'][2]=1;w.players[0]['vars'][3]=0
  w.frames(8);self.assertEqual(w.pos('Target')['x'],0)
  w.players[0]['vars'][3]=1;w.frames(8);self.assertEqual(w.pos('Target')['x'],0)
 def test_observed_hiding_is_safe(self):
  w=self.world();w.pos('Clock')['x']=1;w.pos('Monster').update(x=-7.35,y=0,z=-.1)
  w.players[1]['vars'][0]=1
  w.pulse('ClosetUse1',0);w.frames(20)
  self.assertEqual(w.players[0]['vars'][2],1)
  self.assertEqual(w.players[0]['vars'][0],0)
  self.assertEqual(w.pos('Target')['x'],0)
 def test_key_reappears_after_death_and_requires_key_for_exit(self):
  w=self.world();w.pulse('ExitUse',0);self.assertEqual(w.pos('ExitState')['x'],0)
  self.assertEqual(w.byname['ExitDoor']['levelNodeGroup']['rotation']['y'],0)
  w.pos('KeyState').update(x=0,y=11,z=1);w.players[0]['vars'][0]=1;w.frames(3)
  self.assertEqual(w.pos('KeyState')['y'],0);self.assertIn(w.pos('KeyState')['x'],range(1,11))
  self.assertNotEqual(w.pos('KeyState')['x'],1)
  w.pos('KeyState').update(x=0,y=12);w.pulse('ExitUse',1);self.assertEqual(w.pos('ExitState')['x'],1)
  self.assertGreater(w.byname['ExitDoor']['levelNodeGroup']['rotation']['y'],.7)
  w.pulse('Escape',0);self.assertEqual(w.players[0]['vars'][0],1)
  w.pulse('Escape',1);self.assertEqual(w.players[1]['vars'][0],2)
 def test_dead_marker_follows_player(self):
  w=self.world();w.players[0]['vars'][0]=1;w.players[0]['pos']=[3,1.6,12];w.frames(3)
  marker=w.byname['Dead0']['levelNodeSign']['position'];self.assertEqual(marker['x'],w.players[0]['pos'][0]);self.assertEqual(marker['z'],w.players[0]['pos'][2])
 def test_ten_players_three_protected_seven_vulnerable(self):
  w=World(players=10);w.frames(3)
  for p in w.players:p['pos']=[0,1.6,0]
  for index in range(3):w.hold(f'Gem{index+1}',index)
  w.pos('Monster').update(x=0,y=0,z=30);w.pos('Clock')['x']=1
  w.frames(8)
  self.assertEqual(w.pos('Target')['x'],w.players[3]['id']+1)
  protected={w.pos(n)['y']-1 for n in ['LootA','LootB','LootC']}
  self.assertEqual(len(protected),3)
  self.assertEqual(sum(p['id'] not in protected for p in w.players),7)
 def test_native_animation_endpoints_for_all_ten_offices(self):
  w=self.world()
  for i in range(1,11):
   w.pulse(f'DoorUse{i}',0)
   self.assertEqual(w.pos(f'Door{i}')['y'],0)
   self.assertEqual(w.pos(f'Room{i}')['x'],1)
   w.pulse(f'DrawerUse{i}',0)
   expected=json.loads((ROOT/'docs/manifest.json').read_text())['rooms'][i-1]['drawer'][2]-.7
   self.assertAlmostEqual(w.pos(f'Drawer{i}')['z'],expected)
   w.pulse(f'DoorUse{i}',0);self.assertEqual(w.pos(f'Door{i}')['y'],0)
   w.pulse(f'DrawerUse{i}',0);self.assertAlmostEqual(w.pos(f'Drawer{i}')['z'],expected+.7)
if __name__=='__main__':unittest.main()
