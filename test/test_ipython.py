import unittest
from unittest.mock import patch

from IPython.core.interactiveshell import InteractiveShell
from memory_profiler import LineProfiler, MemitResult, load_ipython_extension


def sample_func(n):
    arr = [1] * n
    return len(arr)


class TestIPythonMagics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ip = InteractiveShell.instance()
        load_ipython_extension(cls.ip)
        cls.ip.user_ns['sample_func'] = sample_func

    def test_mprun(self):
        with patch('IPython.core.page.page') as mock_page:
            prof = self.ip.run_line_magic('mprun', '-r -f sample_func sample_func(1000)')
        self.assertIsInstance(prof, LineProfiler)
        self.assertTrue(mock_page.called)
        output = mock_page.call_args[0][0]
        self.assertIn('Filename:', output)
        self.assertIn('def sample_func(n):', output)

    def test_memit(self):
        res = self.ip.run_line_magic('memit', '-o -q [1] * 10000')
        self.assertIsInstance(res, MemitResult)
        self.assertGreater(len(res.mem_usage), 0)
        self.assertIn('peak memory:', str(res))


if __name__ == '__main__':
    unittest.main()
