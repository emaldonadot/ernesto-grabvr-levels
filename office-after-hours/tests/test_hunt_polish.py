"""Targeted regressions for hunt-ending fog, safe hiding and drawer gem seating.
The harness checks native targets and bytecode; it is not GRAB's physics/rendering.
"""
import unittest
from native_vm import World

class HuntPolish(unittest.TestCase):
 def world(self):
  w=World();w.frames(5);return w
 def test_fog_clears_on_native_leave_in_each_hunt_cycle(self):
  w=self.world();w.progs=[vm for vm in w.progs if vm.name!='MonsterAI']
  leave=w.byname['FogOn']['levelNodeTrigger']['triggerTargets'][1]
  self.assertEqual(leave['mode'],1)
  self.assertEqual(leave['triggerTargetAmbience']['fogDensity'],0)
  self.assertEqual(leave['triggerTargetAmbience']['changeDuration'],0)
  self.assertEqual(w.level['ambienceSettings']['fogDensity'],0)
  for _ in range(4):
   w.pos('Clock')['x']=1;w.frames(3);self.assertEqual(w.ambience['fogDensity'],.72)
   w.pos('Clock')['x']=0;w.tick()
   self.assertEqual(w.ambience['fogDensity'],0)
   self.assertIn((id(w.byname['FogOn']),0,0),w.ambience_events)
   w.frames(5)
 def test_calm_clear_retries_and_all_dead_clears_hunt_fog(self):
  w=self.world();w.progs=[vm for vm in w.progs if vm.name!='MonsterAI'];before=len(w.ambience_events)
  w.ambience={'fogDensity':.6};w.frames(40)
  self.assertEqual(w.ambience['fogDensity'],0)
  self.assertGreater(len(w.ambience_events),before)
  w.pos('Clock')['x']=1;w.frames(3);self.assertEqual(w.ambience['fogDensity'],.72)
  for player in w.players:player['vars'][0]=1
  w.frames(3)
  self.assertEqual(w.pos('Round')['x'],1)
  self.assertEqual(w.ambience['fogDensity'],0)
 def test_unclaimed_gems_stay_in_sliding_drawers_then_release_on_pickup(self):
  w=self.world()
  for i,loot in enumerate(['LootA','LootB','LootC'],1):
   gem=f'Gem{i}';room=int(w.pos(loot)['x']);drawer=w.pos(f'Drawer{room}')
   for direction in [-1,1]:
    for _ in range(10):
     drawer['z']+=direction*.07
     # Inject a fall to model the reported result between script frames.
     w.pos(gem)['y']=.25;w.tick()
     self.assertAlmostEqual(w.pos(gem)['z'],drawer['z'])
     self.assertAlmostEqual(w.pos(gem)['y'],drawer['y']+.145)
   w.hold(gem,0);w.frames(4)
   self.assertEqual(w.pos(loot)['y'],11)
   self.assertEqual(w.pos(f'GemMemory{i}')['y'],1)
   w.physics[gem]=4;w.players[0]['hands'][3]=[9,9,9]
   w.pos(gem).update(x=0,y=.3,z=12);w.frames(4)
   self.assertEqual(w.pos(gem),dict(x=0,y=.3,z=12))
   self.assertEqual(w.pos(loot)['y'],0)
  w.pos('Clock').update(x=1,z=59.99);w.frames(5)
  for i in range(1,4):self.assertEqual(w.pos(f'GemMemory{i}')['y'],0)
 def test_all_twenty_hiding_spots_protect_even_with_old_seen_flag(self):
  for i in range(1,11):
   for kind,offset in [('Closet',0),('Desk',10)]:
    w=self.world();w.players[1]['vars'][0]=1
    w.pos('Clock')['x']=1
    w.pulse(f'{kind}Use{i}',0)
    self.assertEqual(w.players[0]['vars'][2],i+offset)
    w.players[0]['vars'][3]=1
    if kind=='Desk':w.players[0]['pos'][1]=1.9
    w.pos('Monster').update(x=w.players[0]['pos'][0],y=0,z=w.players[0]['pos'][2])
    w.frames(12)
    self.assertEqual(w.players[0]['vars'][0],0)
    self.assertEqual(w.players[0]['vars'][2],i+offset)
    self.assertEqual(w.pos('Target')['x'],0)
 def test_catch_rechecks_hiding_after_a_target_was_already_chosen(self):
  w=self.world();w.pos('Clock')['x']=1
  p=w.players[0];p['vars'][2]=11;p['vars'][3]=1
  w.pos('Monster').update(x=p['pos'][0],y=0,z=p['pos'][2])
  w.pos('Target').update(x=p['id']+1,y=p['pos'][0],z=p['pos'][2])
  ai=next(vm for vm in w.progs if vm.name=='MonsterAI')
  catch=next(i for i,v in enumerate(ai.p['labels']) if v['name']=='catch')
  ai.pc=ai.labels[catch];w.dt=1/60;ai.run()
  self.assertEqual(p['vars'][0],0)
 def test_fumes_are_native_short_lived_particles_on_the_monster(self):
  w=self.world();monster=w.byname['Monster']['levelNodeGroup']
  emitter=w.byname['MonsterFumes'];self.assertIn(emitter,monster['childNodes'])
  data=emitter['levelNodeParticleEmitter']
  self.assertGreater(data['particlesPerSecond'],0)
  self.assertLessEqual(data['particlesPerSecond']*data['lifeSpan']['y'],30)
  self.assertGreater(data['velocityMin']['y'],0)
  self.assertGreater(data['endSize']['x'],data['startSize']['y'])
  self.assertEqual(data['endColor']['a'],0)
  self.assertLessEqual(data['lifeSpan']['y'],1)
  self.assertTrue(0<data['position']['y']<2.3)

if __name__=='__main__':unittest.main()
