PYTHON ?= python

.PHONY: test

test:
	$(PYTHON) -m memory_profiler test/test_func.py
	$(PYTHON) -m memory_profiler test/test_loop.py
	$(PYTHON) -m memory_profiler test/test_as.py
	$(PYTHON) -m memory_profiler test/test_global.py
	$(PYTHON) -m memory_profiler test/test_precision_command_line.py
	$(PYTHON) -m memory_profiler test/test_gen.py
	$(PYTHON) test/test_import.py
	$(PYTHON) test/test_memory_usage.py
	$(PYTHON) test/test_precision_import.py
