import inspect
import os.path

from .utils import get_memory


class CodeMap(dict):
    def __init__(self, include_children, backend):
        self.include_children = include_children
        self._toplevel = []
        self.backend = backend

    def add(self, code, toplevel_code=None):
        if code in self:
            return

        if toplevel_code is None:
            filename = code.co_filename
            if filename.endswith((".pyc", ".pyo")):
                filename = filename[:-1]
            if not os.path.exists(filename):
                print('ERROR: Could not find file ' + filename)
                if filename.startswith(("ipython-input", "<ipython-input")):
                    print(
                        "NOTE: %mprun can only be used on functions defined in"
                        " physical files, and not in the IPython environment.")
                return

            toplevel_code = code
            (sub_lines, start_line) = inspect.getsourcelines(code)
            linenos = range(start_line,
                            start_line + len(sub_lines))
            self._toplevel.append((filename, code, linenos))
            self[code] = {}
        else:
            self[code] = self[toplevel_code]

        for subcode in filter(inspect.iscode, code.co_consts):
            self.add(subcode, toplevel_code=toplevel_code)

    def trace(self, code, lineno, prev_lineno):
        memory = get_memory(
            -1,
            self.backend,
            include_children=self.include_children,
            filename=code.co_filename
        )
        prev_value = self[code].get(lineno, None)
        previous_memory = prev_value[1] if prev_value else 0
        previous_inc = prev_value[0] if prev_value else 0

        prev_line_value = (
            self[code].get(prev_lineno, None)
            if prev_lineno else None
        )
        prev_line_memory = prev_line_value[1] if prev_line_value else 0
        self[code][lineno] = (
            max(previous_inc, memory-prev_line_memory),
            max(memory, previous_memory)
        )

    def items(self):
        """Iterate on the toplevel code blocks."""
        for (filename, code, linenos) in self._toplevel:
            measures = self[code]
            if not measures:
                continue  # skip if no measurement
            line_iterator = ((line, measures.get(line)) for line in linenos)
            yield (filename, line_iterator)
