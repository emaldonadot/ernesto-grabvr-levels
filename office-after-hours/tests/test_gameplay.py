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
 def test_doors_drawers_toggle_and_dead_cannot_interact(self):
  w=self.world();self.assertEqual(w.pos('Room1')['x'],0)
  w.pulse('DoorUse1',0);self.assertEqual(w.pos('Room1')['x'],1)
  w.pulse('DoorUse1',0);self.assertEqual(w.pos('Room1')['x'],0)
  w.pulse('DrawerUse1',0);self.assertEqual(w.pos('Room1')['y'],1)
  w.players[0]['vars'][0]=1;w.pulse('DoorUse1',0);w.pulse('DrawerUse1',0)
  self.assertEqual(w.pos('Room1')['x'],0);self.assertEqual(w.pos('Room1')['y'],1)
 def test_one_person_per_spot_and_exit_releases(self):
  w=self.world();w.pulse('ClosetUse1',0)
  self.assertEqual(w.pos('Spots1')['x'],11);self.assertEqual(w.players[0]['vars'][2],1)
  w.pulse('ClosetUse1',1);self.assertEqual(w.players[1]['vars'][2],0)
  w.pulse('ClosetLeave1',0);self.assertEqual(w.pos('Spots1')['x'],0)
  w.pulse('ClosetUse1',1);self.assertEqual(w.pos('Spots1')['x'],12)
 def test_walking_out_clears_hiding(self):
  w=self.world();w.pulse('DeskUse1',0);self.assertEqual(w.players[0]['vars'][2],11)
  w.players[0]['pos']=[0,1.6,0];w.frames(3)
  self.assertEqual(w.players[0]['vars'][2],0);self.assertEqual(w.pos('Spots1')['y'],0)
 def test_pickup_requires_drawer_open_and_max_one_gem(self):
  w=self.world();w.pos('LootA').update(x=1,y=0);w.pos('LootB').update(x=1,y=0)
  w.pulse('LootUse1',0);self.assertEqual(w.pos('LootA')['y'],0)
  w.pulse('DrawerUse1',0);w.pulse('LootUse1',0)
  self.assertEqual(sum(w.pos(n)['y']==11 for n in ['LootA','LootB','LootC']),1)
 def test_immunity_hidden_and_spectator_target_filter(self):
  w=self.world();w.pos('Clock')['x']=1;w.pos('LootA')['y']=11;w.players[1]['vars'][0]=1
  w.frames(8);self.assertEqual(w.pos('Target')['x'],0)
  w.pos('LootA')['y']=0;w.players[0]['vars'][2]=1;w.players[0]['vars'][3]=0
  w.frames(8);self.assertEqual(w.pos('Target')['x'],0)
  w.players[0]['vars'][3]=1;w.frames(8);self.assertEqual(w.pos('Target')['x'],11)
 def test_witnessed_hiding_retains_spotted_state(self):
  w=self.world();w.pos('Clock')['x']=1;w.pos('Monster').update(x=-5,y=0,z=1)
  # pause monster to hold a controlled line of sight for this interaction
  w.progs=[p for p in w.progs if len(p.p['instructions'])<500]
  w.pulse('ClosetUse1',0);self.assertEqual(w.players[0]['vars'][3],1)
 def test_key_reappears_after_death_and_requires_key_for_exit(self):
  w=self.world();w.pulse('ExitUse',0);self.assertEqual(w.pos('ExitState')['x'],0)
  w.pos('KeyState').update(x=0,y=11,z=1);w.players[0]['vars'][0]=1;w.frames(3)
  self.assertEqual(w.pos('KeyState')['y'],0);self.assertIn(w.pos('KeyState')['x'],range(1,11))
  self.assertNotEqual(w.pos('KeyState')['x'],1)
  w.pos('KeyState').update(x=0,y=12);w.pulse('ExitUse',1);self.assertEqual(w.pos('ExitState')['x'],1)
  w.pulse('Escape',0);self.assertEqual(w.players[0]['vars'][0],1)
  w.pulse('Escape',1);self.assertEqual(w.players[1]['vars'][0],2)
 def test_dead_marker_follows_player(self):
  w=self.world();w.players[0]['vars'][0]=1;w.players[0]['pos']=[3,1.6,12];w.frames(3)
  marker=w.byname['Dead0']['levelNodeSign']['position'];self.assertEqual(marker['x'],3);self.assertEqual(marker['z'],12)
 def test_ten_players_three_protected_seven_vulnerable(self):
  w=World(players=10);w.frames(3)
  for p in w.players:p['pos']=[0,1.6,0]
  for loot,p in zip(['LootA','LootB','LootC'],w.players[:3]):w.pos(loot).update(x=0,y=p['id']+1)
  w.pos('Monster').update(x=0,y=0,z=30);w.pos('Clock')['x']=1
  w.frames(8)
  self.assertEqual(w.pos('Target')['x'],w.players[3]['id']+1)
  protected={w.pos(n)['y']-1 for n in ['LootA','LootB','LootC']}
  self.assertEqual(len(protected),3)
  self.assertEqual(sum(p['id'] not in protected for p in w.players),7)
 def test_all_ten_office_doors_and_drawers_move_on_hand_contact(self):
  w=self.world()
  for i in range(1,11):
   w.pulse(f'DoorUse{i}',0)
   self.assertEqual(w.pos(f'Door{i}')['y'],2.7)
   w.pulse(f'DrawerUse{i}',0)
   expected=json.loads((ROOT/'docs/manifest.json').read_text())['rooms'][i-1]['drawer'][2]-.7
   self.assertAlmostEqual(w.pos(f'Drawer{i}')['z'],expected)
   w.pulse(f'DoorUse{i}',0);self.assertEqual(w.pos(f'Door{i}')['y'],0)
   w.pulse(f'DrawerUse{i}',0);self.assertAlmostEqual(w.pos(f'Drawer{i}')['z'],expected+.7)
if __name__=='__main__':unittest.main()
