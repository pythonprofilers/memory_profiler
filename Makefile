
.PHONY: test

test:
	python -m memory_profiler test/test_func.py
	python -m memory_profiler test/test_loop.py
	python -m memory_profiler test/test_as.py
	python -m memory_profiler test/test_global.py
	python test/test_import.py