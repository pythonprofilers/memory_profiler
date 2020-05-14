import unittest

from memory_profiler import LineProfiler, profile, show_results
from io import StringIO


class TestIncrementDisplay(unittest.TestCase):
    """Tests memory incrementation / decrementation display"""

    def test_loop_count(self):

        def some_loop():
            for i in range(12):  # line -2
                a = 1            # line -1

        profiler = LineProfiler()
        wrapped = profiler(some_loop)
        wrapped()
        show_results(profiler)
        for_line = list(list(profiler.code_map.values())[0].values())[-2]
        looped_instruction = list(list(profiler.code_map.values())[0].values())[-1]

        self.assertEqual(for_line[2], 13)
        self.assertEqual(looped_instruction[2], 12)

    def test_normal_incr(self):

        def normal_incr():
            use_some_memory = [1] * (10 ** 6)

        profiler = LineProfiler()
        wrapped = profiler(normal_incr)
        wrapped()

        show_results(profiler)
        results = list(list(profiler.code_map.values())[0].values())[-1]

        self.assertGreater(results[0], 0)
        self.assertGreater(results[1], results[0])
        self.assertEqual(results[2], 1)

    def test_loop_incr(self):

        def loop_incr():
            a = []
            b = [2] * (2 * 10 ** 7)      # line -4
            for i in range(3):
                c = [2] * (2 * 10 ** 7)  # line -2
                a.append(c)

        profiler = LineProfiler()
        wrapped = profiler(loop_incr)
        wrapped()

        show_results(profiler)
        b_line = list(list(profiler.code_map.values())[0].values())[-4]
        c_line = list(list(profiler.code_map.values())[0].values())[-2]
        self.assertAlmostEqual(b_line[2] * 3, c_line[2], delta=1)
        self.assertEqual(c_line[2], 3)

    def test_decr(self):

        def del_stuff():
            b = [2] * (2 * 10 ** 7)
            del b

        profiler = LineProfiler()
        wrapped = profiler(del_stuff)
        wrapped()

        show_results(profiler)
        b_line = list(list(profiler.code_map.values())[0].values())[-2]
        del_line = list(list(profiler.code_map.values())[0].values())[-1]

        self.assertGreater(0, del_line[0])
        self.assertGreater(del_line[1], 0)
        self.assertAlmostEqual(-del_line[0], b_line[0], delta=1)


if __name__ == '__main__':
    unittest.main()
