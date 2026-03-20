PYTHON ?= python3

.PHONY: install install-dev test lint check clean

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) -m ruff check .

check: lint test

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache
