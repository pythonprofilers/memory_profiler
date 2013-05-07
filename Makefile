PYTHON ?= python

.PHONY: test

test:
	$(PYTHON) -m memory_profiler test/test_func.py
	$(PYTHON) -m memory_profiler test/test_loop.py
	$(PYTHON) -m memory_profiler test/test_as.py
	$(PYTHON) -m memory_profiler test/test_global.py
	$(PYTHON) test/test_import.py