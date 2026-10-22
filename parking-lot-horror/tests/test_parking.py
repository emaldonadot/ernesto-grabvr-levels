import json,sys,unittest
from pathlib import Path
from native_vm import World,VM,ROOT
sys.path.insert(0,str(ROOT/'vendor'))
import grab_pb2 as pb
from google.protobuf.json_format import ParseDict
M=json.loads((ROOT/'docs/manifest.json').read_text())
FIX=json.loads((ROOT/'tests/fixtures/native_connection_layout.json').read_text())
class Parking(unittest.TestCase):
 def world(self,players=2):
  w=World(players=players);w.frames(4);return w
 def test_schedule_five_hunts_key_and_no_sixth(self):
  w=self.world(0)
  for wave in range(5):
   w.frames(60,1);self.assertEqual(w.pos('Clock')['x'],1)
   self.assertEqual(w.pos('KeyState')['z'],0)
   w.frames(60,1);self.assertEqual(w.pos('Clock')['x'],0)
   self.assertEqual(w.pos('Clock')['y'],wave+1)
  self.assertEqual(w.pos('KeyState')['z'],1)
  w.frames(240,1);self.assertEqual(w.pos('Clock')['y'],5);self.assertEqual(w.pos('Clock')['x'],0)
  self.assertEqual(w.pos('Monster')['y'],-100)
 def test_fog_is_local_and_clears_after_hunt(self):
  w=self.world(0);w.pos('Clock')['x']=1;w.frames(5)
  self.assertGreater(w.ambience['fogDensity'],0)
  w.pos('Clock')['x']=0;w.frames(5);self.assertEqual(w.ambience['fogDensity'],0)
  self.assertFalse(w.byname['LocalFog']['levelNodeGASM']['isShared'])
 def test_exact_capacity_vehicle_and_gem_registry(self):
  self.assertEqual(len(M['layout']['stalls']),60)
  self.assertEqual([sum(s['row']==i for s in M['layout']['stalls']) for i in range(6)],[10]*6)
  self.assertEqual(len(M['fleet']['vehicles']),9);self.assertEqual(len(M['fleet']['loot']),3)
  self.assertEqual({x['vehicle'] for x in M['fleet']['loot']},{'SportCar','Minivan1','ExplorerSUV'})
  self.assertEqual(sum(x['kind']=='wreck' for x in M['fleet']['vehicles']),3)
 def test_hidden_is_safe_occupied_and_local_enter_leave(self):
  w=self.world();h=M['fleet']['hides'][0]
  w.pulse(h['use'],0);self.assertEqual(w.players[0]['vars'][2],1)
  self.assertEqual(w.pos('HideState1')['x'],11)
  self.assertAlmostEqual(w.players[0]['pos'][0],h['position'][0])
  w.pulse(h['use'],1);self.assertEqual(w.players[1]['vars'][2],0)
  w.pos('Clock')['x']=1;w.pos('Monster').update(x=h['position'][0],y=0,z=h['position'][2])
  w.frames(20);self.assertEqual(w.players[0]['vars'][0],0)
  w.frames(60);w.pulse(h['leave'],0);self.assertEqual(w.players[0]['vars'][2],0)
  self.assertEqual(w.pos('HideState1')['x'],0)
  self.assertAlmostEqual(w.players[0]['pos'][0],h['exit'][0])
 def test_nonhost_client_consumes_own_hide_intent(self):
  w=self.world();h=M['fleet']['hides'][1]
  movement=next(p for p in w.progs if p.name=='LocalMovement');movement.local_id=11
  w.pulse(h['use'],1)
  self.assertEqual(w.players[1]['vars'][2],2)
  self.assertAlmostEqual(w.players[1]['pos'][0],h['position'][0])
  self.assertAlmostEqual(w.players[1]['pos'][2],h['position'][2])
 def test_walking_out_releases_hide(self):
  w=self.world();w.pulse(M['fleet']['hides'][0]['use'],0);w.frames(60)
  w.players[0]['pos']=[0,1.6,0];w.frames(4)
  self.assertEqual(w.players[0]['vars'][2],0);self.assertEqual(w.pos('HideState1')['x'],0)
 def test_gem_hold_release_and_fixed_console_mount(self):
  w=self.world();p=M['fleet']['loot'][0]['position']
  for a,v in zip('xyz',p):self.assertAlmostEqual(w.pos('Gem1')[a],v)
  w.hold('Gem1',0);w.frames(5);self.assertEqual(w.pos('LootA')['y'],11)
  w.physics['Gem1']=4;w.pos('Gem1').update(x=1,y=2,z=3);w.frames(5)
  self.assertEqual(w.pos('LootA')['y'],0);self.assertEqual(w.pos('Gem1'),dict(x=1,y=2,z=3))
 def test_touch_capture_and_local_spectator(self):
  w=self.world();w.players[0]['pos']=[0,1.6,0];w.players[1]['pos']=[15,1.6,20]
  w.pos('Monster').update(x=0,y=0,z=0);w.pos('Clock')['x']=1;w.frames(4)
  self.assertEqual(w.players[0]['vars'][0],1);self.assertEqual(w.players[0]['pos'][0],24)
 def test_held_immunity_prevents_capture(self):
  w=self.world();w.hold('Gem1',0);w.frames(5)
  w.players[0]['pos']=[0,1.6,0];w.pos('Monster').update(x=0,y=0,z=0);w.pos('Clock')['x']=1;w.frames(5)
  self.assertEqual(w.players[0]['vars'][0],0)
 def test_key_requires_fifth_wave_owner_and_escape_local(self):
  w=self.world();w.pulse('KeyUse',0);self.assertEqual(w.pos('KeyState')['y'],0)
  w.pulse('ExitUse',0);self.assertEqual(w.pos('ExitState')['x'],0)
  w.pos('Clock')['y']=5;w.pos('KeyState').update(x=1,z=1)
  w.pulse('KeyUse',0);self.assertEqual(w.pos('KeyState')['y'],11)
  w.pulse('ExitUse',1);self.assertEqual(w.pos('ExitState')['x'],0)
  w.pulse('ExitUse',0);self.assertEqual(w.pos('ExitState')['x'],1)
  w.pulse('Escape',0);self.assertEqual(w.players[0]['vars'][0],2)
  self.assertEqual(w.players[0]['pos'],[100,-49,0])
 def test_dead_key_owner_returns_key(self):
  w=self.world();w.pos('Clock')['y']=5;w.pos('KeyState').update(y=11,z=1)
  w.players[0]['vars'][0]=1;w.frames(5)
  self.assertEqual(w.pos('KeyState')['y'],0);self.assertAlmostEqual(w.pos('Key')['y'],1.14)
 def test_wipe_resets_full_calm_and_local_revives(self):
  w=self.world();w.pos('Clock').update(x=1,y=3,z=30)
  for p in w.players:p['vars'][0]=1
  w.frames(2);self.assertEqual(w.pos('Round')['x'],1)
  w.frames(6,1);self.assertEqual(w.pos('Round')['z'],2)
  self.assertEqual(w.pos('Clock')['x'],0);self.assertEqual(w.pos('Clock')['y'],0)
  self.assertEqual(w.players[0]['vars'][0],0);self.assertLess(w.players[0]['pos'][2],-26)
 def test_all_teleports_only_local_controller(self):
  w=self.world()
  for name,node in w.byname.items():
   if 'levelNodeGASM' not in node:continue
   g=node['levelNodeGASM'];outputs=g['program']['outputRegisters']
   tele={i for i,x in enumerate(outputs) if x['name'].startswith('Player.Tel.')}
   writes=any(x['operands'] and x['operands'][0].get('type')==1 and x['operands'][0].get('index') in tele for x in g['program']['instructions'])
   if writes:self.assertEqual(name,'LocalMovement');self.assertFalse(g['isShared'])
 def test_cross_aisle_routes_reach_targets_within_one_hunt(self):
  for start,target in [((-17.7,0),(10,23)),((17.7,17.7),(-10,-23)),((0,-17.7),(12,11)),((-10,-23),(-10,23)),((10,23),(-10,-23))]:
   with self.subTest(start=start,target=target):
    w=World(players=1);w.progs=[p for p in w.progs if p.name=='MonsterAI']
    w.pos('Clock')['x']=1;w.pos('Monster').update(x=start[0],y=0,z=start[1]);w.players[0]['pos']=[target[0],1.6,target[1]]
    for _ in range(3600):
     w.tick()
     if w.players[0]['vars'][0]==1:break
    self.assertEqual(w.players[0]['vars'][0],1)
    self.assertLess(w.time,60)
 def test_native_layout_refs_and_protobuf(self):
  w=self.world();parsed=ParseDict(json.loads((ROOT/'dist/parking-lot-horror.json').read_text()),pb.Level())
  self.assertEqual(pb.Level.FromString((ROOT/'dist/parking-lot-horror.level').read_bytes()),parsed)
  for node in w.nodes.values():
   if 'levelNodeGASM' in node:
    g=node['levelNodeGASM']
    for c in g['connections']:
     self.assertTrue(c['objectID'] in w.nodes or c['type']==1)
     for prop in c['properties']:
      kind=next(k for k in prop if k not in ['components','objectID'])
      if kind=='player':
       self.assertEqual(len(prop['components']),28)
       for slot,expected in zip(prop['components'],FIX['player']):self.assertGreaterEqual(slot[expected['direction']+'RegisterIndex'],0)
      if kind=='triggerActive':self.assertEqual(len(prop['components']),6)
      for slot in prop['components']:self.assertEqual(set(slot),{'inputRegisterIndex','outputRegisterIndex','inoutRegisterIndex'})
   if 'levelNodeTrigger' in node:
    for t in node['levelNodeTrigger']['triggerTargets']:
     for key in ['triggerTargetGASM','triggerTargetAnimation']:
      if key in t:self.assertIn(t[key]['objectID'],w.nodes)
     if 'triggerTargetAnimation' in t:
      a=t['triggerTargetAnimation'];self.assertIn(a['animationName'],[x['name'] for x in w.nodes[a['objectID']]['animations']])
 def test_native_driver_hinges_and_sliding_doors(self):
  w=self.world()
  for d in M['fleet']['doors']:
   w.pulse(d['use'],0);self.assertTrue(w.animation_open[id(w.byname[d['name']])])
   if d['kind']=='slide':self.assertAlmostEqual(w.pos(d['name'])['z'],w.byname[d['name']]['levelNodeGroup']['_base']['z']+1.5)
   w.pulse(d['use'],0);self.assertFalse(w.animation_open[id(w.byname[d['name']])])
 def test_skeleton_scale_speed_and_parented_fumes(self):
  self.assertEqual(M['creature']['height'],2.525);self.assertGreater(M['config']['monsterSpeed'],3.4)
  w=self.world();self.assertIn(w.byname['MonsterFumes'],w.byname['Monster']['levelNodeGroup']['childNodes'])
if __name__=='__main__':unittest.main()
