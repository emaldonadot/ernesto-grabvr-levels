"""Tests the exported bytecode; the harness is not the GRAB engine."""
import json
import sys
import unittest
from native_vm import World, ROOT
sys.path.insert(0,str(ROOT/'vendor'))
import grab_pb2 as pb
from google.protobuf.json_format import ParseDict

class NativeGraveYard(unittest.TestCase):
    def world(self, players=2):
        w=World(players=players)
        w.frames(5)
        return w

    def test_exactly_five_native_hunts(self):
        w=self.world(0)
        for wave in range(5):
            w.frames(60,1)
            self.assertEqual(w.pos('Clock')['x'],1)
            w.frames(60,1)
            self.assertEqual(w.pos('Clock')['x'],0)
            self.assertEqual(w.pos('Clock')['y'],wave+1)
        w.frames(600,1)
        self.assertEqual(w.pos('Clock')['y'],5)
        self.assertEqual(w.pos('Clock')['x'],0)

    def test_native_fog_clears_after_hunt(self):
        w=self.world(0)
        w.pos('Clock')['x']=1; w.frames(6)
        self.assertGreater(w.ambience['fogDensity'],0)
        w.pos('Clock')['x']=0; w.frames(6)
        self.assertEqual(w.ambience['fogDensity'],0)
        self.assertFalse(w.byname['LocalFog']['levelNodeGASM']['isShared'])

    def test_gem_records_only_held_owner_and_release_clears(self):
        w=self.world()
        w.hold('Gem1',0); w.frames(8)
        self.assertEqual(w.pos('LootA')['y'],11)
        w.physics['Gem1']=4; w.frames(8)
        self.assertEqual(w.pos('LootA')['y'],0)

    def test_wipe_reset_full_calm_and_local_revive(self):
        w=self.world()
        w.pos('Clock').update(x=1,y=3,z=30)
        for p in w.players:p['vars'][0]=1
        w.frames(3)
        self.assertEqual(w.pos('Round')['x'],1)
        w.frames(4,1)
        self.assertEqual(w.players[0]['vars'][0],1)
        w.frames(2,1);w.frames(8)
        self.assertEqual(w.pos('Round')['z'],2)
        self.assertEqual(w.pos('Clock')['x'],0)
        self.assertEqual(w.pos('Clock')['y'],0)
        self.assertEqual(w.players[0]['vars'][0],0)
        self.assertEqual(w.pos('ExitState')['x'],0)

    def test_survivor_or_escaped_player_prevents_wipe(self):
        for survivor_status in (0,2):
            w=self.world()
            w.players[0]['vars'][0]=1
            w.players[1]['vars'][0]=survivor_status
            w.frames(8,1)
            self.assertEqual(w.pos('Round')['x'],0)
            self.assertEqual(w.pos('Round')['z'],1)

    def test_teleport_writes_are_client_local(self):
        w=self.world()
        for name,node in w.byname.items():
            if 'levelNodeGASM' not in node:continue
            g=node['levelNodeGASM']
            indices={i for i,r in enumerate(g['program']['outputRegisters']) if r['name'].startswith('Player.Tel.')}
            writes=any(i['operands'] and i['operands'][0]['type']==1 and i['operands'][0].get('index') in indices for i in g['program']['instructions'])
            if writes:
                self.assertEqual(name,'LocalMovement')
                self.assertFalse(g['isShared'])

    def skull_world(self):
        w=self.world()
        w.pos('Clock')['y']=5
        w.frames(5)
        return w

    def test_skull_requires_fifth_hunt_living_holder_and_physical_release(self):
        early=self.world()
        early.pos('GoldenSkull').update(x=4,y=2.15,z=-24)
        early.physics['GoldenSkull']=4
        early.pos('SkullState').update(y=11,z=1)
        early.frames(5)
        self.assertEqual(early.pos('ExitState')['x'],0)
        self.assertLess(early.pos('GoldenSkull')['y'],-50)
        w=self.skull_world()
        w.hold('GoldenSkull',0);w.frames(5)
        self.assertEqual(w.pos('SkullState')['y'],11)
        w.pos('GoldenSkull').update(x=4,y=2.15,z=-24)
        w.players[0]['hands'][3]=[4,2.15,-24]
        w.frames(5)
        self.assertEqual(w.pos('ExitState')['x'],0)
        w.physics['GoldenSkull']=4;w.frames(8)
        self.assertEqual(w.pos('ExitState')['x'],1)
        self.assertEqual(w.byname['Finish']['levelNodeFinish']['position']['y'],1.2)

    def test_skull_rejects_wrong_socket_and_dead_holder_and_recovers_lost(self):
        for position,dead in [((5,2.15,-24),False),((4,3,-24),False),((4,2.15,-24),True),((0,-10,0),False)]:
            with self.subTest(position=position,dead=dead):
                w=self.skull_world()
                w.hold('GoldenSkull',0);w.frames(5)
                w.pos('GoldenSkull').update(zip('xyz',position))
                w.physics['GoldenSkull']=4
                if dead:w.players[0]['vars'][0]=1
                w.frames(8)
                self.assertEqual(w.pos('ExitState')['x'],0)
                if dead or position[1]<-8:
                    self.assertEqual(w.pos('SkullState')['y'],0)
                    self.assertEqual(w.pos('GoldenSkull'),dict(x=0,y=1.6,z=17))

    def ai_world(self,head_y=1.6):
        w=self.world()
        w.progs=[p for p in w.progs if p.name in ('MonsterAI','NavClock')]
        w.players[0]['pos']=[0,head_y,0]
        w.players[1]['vars'][0]=2
        w.pos('Clock')['x']=1
        w.pos('ZombieState')['x']=1
        w.pos('Monster').update(x=0,y=0,z=0)
        return w

    def test_zombie_captures_reachable_climber_without_gem(self):
        w=self.ai_world(2.8)
        w.players[0]['vars'][2]=7  # legacy hiding/tree flag is no protection
        w.frames(40)
        self.assertEqual(w.players[0]['vars'][0],1)

    def test_zombie_held_gem_protects_then_release_allows_capture(self):
        w=self.ai_world()
        w.pos('LootA')['y']=11
        w.frames(40)
        self.assertEqual(w.players[0]['vars'][0],0)
        w.pos('LootA')['y']=0
        w.frames(40)
        self.assertEqual(w.players[0]['vars'][0],1)

    def test_elevated_target_still_selected_but_capture_requires_reach(self):
        w=self.ai_world(5)
        w.frames(40)
        self.assertEqual(w.pos('Target')['x'],11)
        self.assertEqual(w.players[0]['vars'][0],0)

    def test_nonhost_spectator_and_revival_move_only_own_player(self):
        w=self.world()
        movement=next(p for p in w.progs if p.name=='LocalMovement')
        movement.local_id=11
        original=list(w.players[0]['pos'])
        w.players[1]['vars'][0]=1
        w.frames(5)
        self.assertEqual(w.players[1]['pos'],[28,.1,0])
        self.assertEqual(w.players[0]['pos'],original)
        w.pos('Round')['z']=2;w.frames(5)
        self.assertEqual(w.players[1]['vars'][0],0)
        self.assertLess(w.players[1]['pos'][2],-22)
        self.assertEqual(w.players[0]['pos'],original)

    def test_zombie_routes_around_marker_and_stays_out_of_obstacle_rectangles(self):
        w=self.ai_world()
        w.pos('Monster').update(x=-10.5,y=0,z=-12)
        w.players[0]['pos']=[-10.5,1.6,-6]
        obstacles=json.loads((ROOT/'docs/manifest.json').read_text())['navigation']['obstacles']
        for _ in range(1800):
            w.tick()
            p=w.pos('Monster')
            self.assertFalse(any(o['xmin']<p['x']<o['xmax'] and o['zmin']<p['z']<o['zmax'] for o in obstacles))
            if w.players[0]['vars'][0]==1:break
        self.assertEqual(w.players[0]['vars'][0],1)
        self.assertLess(w.time,30)

    def test_exit_has_continuous_floor_and_locked_finish(self):
        w=self.world()
        self.assertLess(w.byname['Finish']['levelNodeFinish']['position']['y'],-50)
        floor=w.byname['ExitRoomFloor']['levelNodeStatic']
        self.assertEqual(floor['position']['y']+floor['scale']['y']/2,0)
        self.assertGreaterEqual(floor['position']['z']+floor['scale']['z']/2,-28)
        self.assertLessEqual(floor['position']['z']-floor['scale']['z']/2,-36)
        for name in ('ExitRoomRoof','ExitRoomSide-1','ExitRoomSide1','ExitRoomBack'):
            self.assertIn(name,w.byname)

    def test_schema_roundtrip_and_native_connection_directions(self):
        w=self.world()
        parsed=ParseDict(json.loads((ROOT/'dist/the-grave-yard.json').read_text()),pb.Level())
        self.assertEqual(pb.Level.FromString((ROOT/'dist/the-grave-yard.level').read_bytes()),parsed)
        fixture=json.loads((ROOT/'tests/fixtures/native_connection_layout.json').read_text())
        for node in w.nodes.values():
            if 'levelNodeGASM' in node:
                g=node['levelNodeGASM']
                for c in g['connections']:
                    self.assertTrue(c['type']==1 or c['objectID'] in w.nodes)
                    for prop in c['properties']:
                        kind=next(k for k in prop if k not in ('components','objectID'))
                        if kind=='player':
                            self.assertEqual(len(prop['components']),28)
                            for slot,expected in zip(prop['components'],fixture['player']):
                                self.assertGreaterEqual(slot[expected['direction']+'RegisterIndex'],0)
                        if kind=='triggerActive':self.assertEqual(len(prop['components']),6)
                        if kind=='physics':
                            self.assertEqual(len(prop['components']),2)
                            self.assertGreaterEqual(prop['components'][0]['inoutRegisterIndex'],0)
                            self.assertGreaterEqual(prop['components'][1]['inputRegisterIndex'],0)
                        for slot in prop['components']:
                            self.assertEqual(set(slot),{'inputRegisterIndex','outputRegisterIndex','inoutRegisterIndex'})
            if 'levelNodeTrigger' in node:
                for t in node['levelNodeTrigger']['triggerTargets']:
                    for key in ('triggerTargetAnimation','triggerTargetGASM'):
                        if key in t:self.assertIn(t[key]['objectID'],w.nodes)
                    if 'triggerTargetAnimation' in t:
                        a=t['triggerTargetAnimation']
                        self.assertIn(a['animationName'],[x['name'] for x in w.nodes[a['objectID']]['animations']])

if __name__=='__main__':unittest.main()
