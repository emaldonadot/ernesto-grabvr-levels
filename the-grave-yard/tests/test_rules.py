import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rules import GraveYardRound, Phase

class TestGraveYardRules(unittest.TestCase):
    def setUp(self):
        self.game = GraveYardRound()
        self.game.add_player(1)
        self.game.add_player(2)

    def test_five_hunts_only(self):
        for n in range(5):
            self.game.tick(60)
            self.assertEqual(self.game.phase, Phase.HUNT)
            self.game.tick(60)
            self.assertEqual(self.game.completed_hunts, n + 1)
        self.assertEqual(self.game.phase, Phase.ESCAPE)
        self.game.tick(600)
        self.assertEqual(self.game.completed_hunts, 5)

    def test_tree_does_not_protect(self):
        self.game.tick(60)
        self.game.players[1].climbing_tree = True
        self.assertTrue(self.game.capture(1))

    def test_gem_protects_even_on_ground(self):
        self.game.tick(60)
        self.game.players[1].holding_gem = True
        self.assertFalse(self.game.capture(1))

    def test_no_capture_during_rest(self):
        self.assertFalse(self.game.capture(1))

    def test_skull_requires_release_in_socket_after_fifth_hunt(self):
        self.assertFalse(self.game.place_skull(1, True, True))
        self.game.tick(600)
        self.assertFalse(self.game.place_skull(1, True, False))
        self.assertFalse(self.game.place_skull(1, False, True))
        self.assertTrue(self.game.place_skull(1, True, True))
        self.assertTrue(self.game.gate_open)
        self.assertFalse(self.game.finish(1, False))
        self.assertTrue(self.game.finish(1, True))

    def test_wipe_resets_after_five_seconds(self):
        self.game.tick(60)
        self.assertTrue(self.game.capture(1))
        self.assertTrue(self.game.capture(2))
        self.game.tick(4)
        self.assertFalse(self.game.players[1].alive)
        self.game.tick(1)
        self.assertTrue(self.game.players[1].alive)
        self.assertEqual(self.game.phase, Phase.REST)

if __name__ == "__main__":
    unittest.main()
