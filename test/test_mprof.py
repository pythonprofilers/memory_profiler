import unittest

import mprof

class Test_function_labels(unittest.TestCase):
    def test(self):
        expected = {
            "x.z": "z",
            "x.y": "y",
            "x.b": "x.b",
            "f.a.b": "f.a.b",
            "g.a.b": "g.a.b",
            "g.a.c": "a.c",
            "b.c": "b.c",
        }
        result = mprof.function_labels(expected.keys())
        self.assertEqual(expected,result)

if __name__ == "__main__":
    unittest.main()
