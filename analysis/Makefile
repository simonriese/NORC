all:
	pip install -e .

test:
	PYTHONPATH=. pytest tests/

lint:
	ruff check .

format:
	ruff format .

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .ruff_cache
	find . -name "__pycache__" -exec rm -rf {} +
