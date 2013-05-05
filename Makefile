
.PHONY: test

test:
	python -m memory_profiler test/test_func.py
	python -m memory_profiler test/test_loop.py
	python -m memory_profiler test/test_with.py