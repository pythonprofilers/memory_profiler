import os
import sys
import tempfile
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
        self.assertEqual(expected, result)


class TestMprofMainArgs(unittest.TestCase):
    """Tests for CLI argument handling in mprof.main() (Issue #388 / PR #390).

    Background (Issue #388):
    Subcommands like `mprof plot -1` or `mprof rm -1` allow selecting a profile
    file by negative index (-1 = most recent). To prevent argparse from treating
    `-1` as an unknown flag, `mprof.main()` inserts `"--"` before the first
    negative integer in `sys.argv`.

    However, when running `mprof run script.py -1`, inserting `"--"` into
    `sys.argv` causes `"--"` to be forwarded as an extra argument to `script.py`
    (so the script receives `['--', '-1']` instead of `['-1']`).
    """

    def test_run_preserves_negative_int_args(self):
        # Verify that `mprof run` does NOT inject "--" before negative integer
        # arguments meant for the target program. The temporary script checks
        # that its sys.argv[1:] is exactly ['-1'] and exits non-zero otherwise.
        script = (
            "import sys\n"
            "assert sys.argv[1:] == ['-1'], 'Unexpected argv: %r' % (sys.argv[1:],)\n"
        )
        with tempfile.NamedTemporaryFile('w', suffix='.py') as tmp_script, \
             tempfile.NamedTemporaryFile('w', suffix='.dat') as tmp_dat:
            tmp_script.write(script)
            tmp_script.flush()
            sys.argv = [
                'mprof', 'run', '--exit-code', '-o', tmp_dat.name,
                tmp_script.name, '-1'
            ]
            with self.assertRaises(SystemExit) as cm:
                mprof.main()
            self.assertEqual(cm.exception.code, 0)

    def test_non_run_action_accepts_negative_index(self):
        # Verify that non-`run` subcommands (such as `mprof rm --dry-run -1`)
        # still have "--" inserted before `-1` so negative profile indices
        # are accepted by argparse without raising an unrecognized argument error.
        tmp_prof = "mprofile_20990101000000.dat"
        with open(tmp_prof, "w") as f:
            f.write("")
        try:
            sys.argv = ['mprof', 'rm', '--dry-run', '-1']
            mprof.main()
        finally:
            if os.path.exists(tmp_prof):
                os.remove(tmp_prof)

    def test_plot_file_xlim_window_rescales_ylim(self):
        # Verify that plotting with --window (options.xlim) filters the plotted
        # data to the requested time window so the y-axis and peak memory marker
        # reflect the windowed data rather than out-of-window spikes (PR #367).
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as pl

        content = (
            "CMDLINE python test.py\n"
            "MEM 10.0 100.0\n"
            "MEM 20.0 101.0\n"
            "MEM 500.0 102.0\n"  # Large spike at t=2.0s outside the [0, 1.5] window
        )
        with tempfile.NamedTemporaryFile('w', suffix='.dat') as tmp_dat:
            tmp_dat.write(content)
            tmp_dat.flush()

            class Options:
                xlim = [0.0, 1.5]
                slope = False

            fig = pl.figure()
            try:
                mprof.plot_file(tmp_dat.name, options=Options())
                top_ylim = pl.ylim()[1]
                # Since the 500.0 MiB spike at t=2.0s is outside xlim=[0.0, 1.5],
                # the y-axis upper bound should be scaled to ~20.0 MiB, not 500.0 MiB.
                self.assertLess(top_ylim, 50.0)
            finally:
                pl.close(fig)

    def test_multiline_cmdline_arg_roundtrip(self):
        # Verify that multiline CLI arguments passed to `mprof run` do not
        # write raw newlines into the CMDLINE header of the .dat file, which
        # previously caused read_mprofile_file() to crash with ValueError
        # on blank or single-token continuation lines (Issue #210 / PR #363).
        multiline_arg = "hello\n\nworld"
        cmd_line = mprof.get_cmd_line(["python", "script.py", multiline_arg])
        self.assertNotIn("\n", cmd_line)

        content = (
            "CMDLINE %s\n"
            "MEM 10.0 100.0\n"
        ) % cmd_line
        with tempfile.NamedTemporaryFile('w', suffix='.dat') as tmp_dat:
            tmp_dat.write(content)
            tmp_dat.flush()
            parsed = mprof.read_mprofile_file(tmp_dat.name)
            self.assertEqual(parsed["mem_usage"], [10.0])
            self.assertIn("hello\\n\\nworld", parsed["cmd_line"])


if __name__ == "__main__":
    unittest.main()
