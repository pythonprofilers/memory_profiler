import tracemalloc
import unittest

from memory_profiler import LineProfiler, profile, show_results
from io import StringIO


class TestIncrementDisplay(unittest.TestCase):
    """Tests memory incrementation / decrementation display"""

    def setUp(self):
        tracemalloc.start()

    def tearDown(self):
        tracemalloc.stop()

    def test_loop_count(self):

        def some_loop():
            for i in range(12):  # line -2
                a = 1            # line -1

        profiler = LineProfiler(backend='tracemalloc')
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

        profiler = LineProfiler(backend='tracemalloc')
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

        profiler = LineProfiler(backend='tracemalloc')
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

        profiler = LineProfiler(backend='tracemalloc')
        wrapped = profiler(del_stuff)
        wrapped()

        show_results(profiler)
        b_line = list(list(profiler.code_map.values())[0].values())[-2]
        del_line = list(list(profiler.code_map.values())[0].values())[-1]

        self.assertGreater(0, del_line[0])
        self.assertGreater(del_line[1], 0)
        self.assertAlmostEqual(-del_line[0], b_line[0], delta=1)

    def test_no_false_negative_incr_after_peak_in_loop(self):
        """Regression test for Issue #219 / PR #350.

        When a line inside a loop reaches a high memory peak on an early
        iteration that is later freed, subsequent iterations of the following
        line must compare against the previous line's most recent memory,
        not its historical maximum memory (which would accumulate bogus
        negative increments on every iteration).
        """
        def loop_with_early_peak():
            for i in range(5):
                # Peaks on i == 0 (~150 MiB), small on i > 0
                x = [1] * (2 * 10 ** 7 if i == 0 else 10)
                y = 1  # Must NOT accumulate a ~-150 MiB decrement on i = 1..4
                del x

        profiler = LineProfiler(backend='tracemalloc')
        wrapped = profiler(loop_with_early_peak)
        wrapped()

        show_results(profiler)
        measures = list(profiler.code_map.values())[0]
        # Ordered lines: for, x = ..., y = 1, del x
        y_line = [measures[lineno] for lineno in sorted(measures)][-2]
        y_inc = y_line[0]
        # Before PR #350, y_inc was around -600 MiB (4 * -150 MiB).
        # With PR #350, y = 1 has ~0 MiB increment.
        self.assertGreater(y_inc, -5.0)


if __name__ == '__main__':
    unittest.main()
