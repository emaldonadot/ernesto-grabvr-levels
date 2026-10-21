"""Check the serialized artifact against an independently exported GRAB layout."""
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=json.loads((ROOT/'tests/fixtures/native_connection_layout.json').read_text())
def nodes(ns):
 for n in ns:
  yield n
  if 'levelNodeGroup'in n:yield from nodes(n['levelNodeGroup']['childNodes'])
class NativeContract(unittest.TestCase):
 def setUp(self):
  self.level=json.loads((ROOT/'dist/office-after-hours.json').read_text())
  self.blocks=[n['levelNodeGASM'] for n in nodes(self.level['levelNodes']) if 'levelNodeGASM'in n]
 def test_player_component_layout_matches_exported_grab_level(self):
  for g in self.blocks:
   p=g['program']
   for c in g['connections']:
    for prop in c['properties']:
     if 'player'not in prop:continue
     self.assertEqual(len(prop['components']),len(FIXTURE['player']))
     for component,expected in zip(prop['components'],FIXTURE['player']):
      field=expected['direction']+'RegisterIndex';idx=component[field]
      self.assertGreaterEqual(idx,0)
      self.assertEqual(p[expected['direction']+'Registers'][idx]['name'],expected['name'])
 def test_trigger_component_layout_matches_exported_grab_level(self):
  for g in self.blocks:
   for c in g['connections']:
    for prop in c['properties']:
     if 'triggerActive'not in prop:continue
     self.assertEqual(len(prop['components']),FIXTURE['trigger_component_count'])
     for slot in [3,4,5]:self.assertTrue(all(v==-1 for v in prop['components'][slot].values()))
 def test_legacy_player_contract_is_rejected(self):
  from native_vm import World,VM
  import copy
  w=World();block=copy.deepcopy(next(g for g in self.blocks if any('player'in p for c in g['connections'] for p in c['properties'])))
  prop=next(p for c in block['connections'] for p in c['properties'] if 'player'in p)
  prop['components'].pop()
  with self.assertRaisesRegex(ValueError,'player.*28'):VM(w,block)
 def test_legacy_trigger_contract_is_rejected(self):
  from native_vm import World,VM
  import copy
  w=World();block=copy.deepcopy(next(g for g in self.blocks if any('triggerActive'in p for c in g['connections'] for p in c['properties'])))
  prop=next(p for c in block['connections'] for p in c['properties'] if 'triggerActive'in p)
  prop['components']=prop['components'][:4]
  with self.assertRaisesRegex(ValueError,'triggerActive.*6'):VM(w,block)
 def test_hand_triggers_have_native_controller_start_targets(self):
  manifest=json.loads((ROOT/'docs/manifest.json').read_text())
  flat=list(nodes(self.level['levelNodes']))
  ids=manifest['ids']
  for i in range(1,11):
   for event in ['LootUse','ClosetUse','ClosetLeave','DeskUse','DeskLeave']:
    t=flat[ids[f'{event}{i}']-1]['levelNodeTrigger']
    self.assertEqual(t['triggerTargets'],[{'mode':0,'triggerTargetGASM':{'objectID':ids[f'Office{i:02}'],'mode':1}}])
 def test_direct_native_animation_targets_and_hinge_geometry(self):
  from native_vm import World
  import math
  w=World()
  for i in range(1,11):
   side=-1 if i<=5 else 1
   door=w.byname[f'Door{i}'];data=door['levelNodeGroup']
   self.assertEqual(door['activeAnimation'],-1)
   self.assertAlmostEqual(data['position']['z'],1+6*((i-1)%5)-.725)
   panel=data['childNodes'][0]['levelNodeStatic']
   # Panel's hinge edge stays at local zero; far edge swings into the office.
   self.assertAlmostEqual(panel['position']['z']-panel['scale']['z']/2,0)
   q=door['animations'][0]['frames'][-1]['rotation']
   self.assertAlmostEqual(2*math.atan2(q['y'],q['w']),side*math.pi/2)
   for prefix,name in [('Door','Hinge'),('Drawer','Slide')]:
    t=w.byname[f'{prefix}Use{i}']['levelNodeTrigger']['triggerTargets'][0]
    self.assertNotIn('triggerTargetGASM',t)
    a=t['triggerTargetAnimation'];self.assertEqual(a['mode'],3)
    self.assertEqual(a['animationName'],name);self.assertFalse(a['loop'])
    self.assertIs(w.nodes[a['objectID']],w.byname[f'{prefix}{i}'])
   children=w.byname[f'Drawer{i}']['levelNodeGroup']['childNodes']
   self.assertIn(w.byname[f'DrawerUse{i}'],children)
 def test_gems_are_shared_collidable_grabbable_physics(self):
  from native_vm import World
  w=World()
  for i in range(1,4):
   data=w.byname[f'Gem{i}']['levelNodeGroup']
   self.assertTrue(data['physicsObject']);self.assertFalse(data['localPhysicsObject'])
   self.assertGreater(data['mass'],0)
   for child in data['childNodes']:
    self.assertTrue(child['levelNodeStatic']['isGrabbable'])
    self.assertFalse(child['levelNodeStatic'].get('isPassable',False))
if __name__=='__main__' :unittest.main()
