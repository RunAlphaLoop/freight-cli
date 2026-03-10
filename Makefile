.PHONY: pypi clean install dev

pypi: clean
	pip install build twine -q && python -m build && twine upload dist/*

clean:
	rm -rf dist build *.egg-info

install:
	pip install -e .

dev:
	pip install -e ".[dev]"
