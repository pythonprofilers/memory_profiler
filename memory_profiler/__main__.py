import os
import sys
from argparse import ArgumentParser, REMAINDER

from . import exec_with_profiler, run_module_with_profiler, TimeStamper, __version__
from .line_profiler import LineProfiler
from .utils import choose_backend, show_results


_CMD_USAGE = "python -m memory_profiler script_file.py"


def _find_script(script_name):
    """ Find the script.

    If the input is not a file, then $PATH will be searched.
    """
    if os.path.isfile(script_name):
        return script_name
    path = os.getenv('PATH', os.defpath).split(os.pathsep)
    for folder in path:
        if not folder:
            continue
        fn = os.path.join(folder, script_name)
        if os.path.isfile(fn):
            return fn

    sys.stderr.write('Could not find script {0}\n'.format(script_name))
    raise SystemExit(1)


if __name__ == '__main__':
    parser = ArgumentParser(usage=_CMD_USAGE)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        '--pdb-mmem',
        dest='max_mem',
        metavar='MAXMEM',
        type=float,
        action='store',
        help='step into the debugger when memory exceeds MAXMEM'
    )
    parser.add_argument(
        '--precision',
        dest='precision',
        type=int,
        action='store',
        default=3,
        help='precision of memory output in number of significant digits'
    )
    parser.add_argument(
        '-o',
        dest='out_filename',
        type=str,
        action='store',
        default=None,
        help='path to a file where results will be written'
    )
    parser.add_argument(
        '--timestamp',
        dest='timestamp',
        default=False,
        action='store_true',
        help='''print timestamp instead of memory measurement for
        decorated functions'''
    )
    parser.add_argument(
        '--backend',
        dest='backend',
        type=str,
        action='store',
        choices=['tracemalloc', 'psutil', 'posix'],
        default='psutil',
        help='backend using for getting memory info '
             '(one of the {tracemalloc, psutil, posix})'
    )
    parser.add_argument(
        "program",
        nargs=REMAINDER,
        help='python script or module followed by '
             'command line arguments to run'
    )
    args = parser.parse_args()

    if len(args.program) == 0:
        print("A program to run must be provided. Use -h for help")
        sys.exit(1)

    target = args.program[0]
    script_args = args.program[1:]

    _backend = choose_backend(args.backend)
    if args.timestamp:
        prof = TimeStamper(_backend)
    else:
        prof = LineProfiler(max_mem=args.max_mem, backend=_backend)

    try:
        if args.program[0].endswith('.py'):
            script_filename = _find_script(args.program[0])
            exec_with_profiler(
                script_filename, prof, args.backend, script_args
            )
        else:
            run_module_with_profiler(target, prof, args.backend, script_args)
    finally:
        if args.out_filename is not None:
            out_file = open(args.out_filename, "a")
        else:
            out_file = sys.stdout

        if args.timestamp:
            prof.show_results(stream=out_file)
        else:
            show_results(prof, precision=args.precision, stream=out_file)
