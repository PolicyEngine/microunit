install:
	pip install -e ".[dev]"

test:
	pytest tests/ --cov=microunit --cov-report=xml --maxfail=0 -v

check-format:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

build:
	pip install build
	python -m build

changelog:
	python .github/bump_version.py
	towncrier build --yes --version $$(python -c "import re; print(re.search(r'version = \"(.+?)\"', open('pyproject.toml').read()).group(1))")

clean:
	rm -rf dist/ build/ *.egg-info/
