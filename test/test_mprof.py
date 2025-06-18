import unittest

from memory_profiler import mprof

class TestFunctionLabels(unittest.TestCase):
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

