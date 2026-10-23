import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from environment import build, EPITAPHS, TREE_POSITIONS, PUMPKIN_POSITIONS

class EnvironmentTests(unittest.TestCase):
    def test_layout(self):
        nodes=[]
        def box(name,p,s,c,**kw):
            nodes.append(name)
        def sign(name,text,p,scale):
            nodes.append(name)
        layout=build(dict(box=box,group=None,part=None,sign=sign))
        self.assertEqual(len(layout["graves"]),16)
        self.assertEqual(len(layout["trees"]),6)
        self.assertEqual(len(layout["pumpkins"]),4)
        self.assertEqual(len(layout["candles"]),3)
        self.assertEqual(len(layout["epitaphs"]),16)
        self.assertEqual(len(nodes),len(set(nodes)))
        self.assertGreater(layout["zombie_speed"],3.7)
        for x,z in layout["graves"]:
            self.assertLess(abs(x),12)
            self.assertLess(abs(z),12)

if __name__=="__main__":
    unittest.main()
