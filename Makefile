SHELL=/bin/bash

venv:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

install:
	unset CONDA_PREFIX && \
	source .venv/bin/activate && maturin develop

install-release:
	unset CONDA_PREFIX && \
	source .venv/bin/activate && maturin develop --release

pre-commit:
	cargo +nightly fmt --all && cargo clippy --all-features
	.venv/bin/python -m ruff check . --fix --exit-non-zero-on-fix
	.venv/bin/python -m ruff format polars_indicator tests
	.venv/bin/mypy polars_indicator tests

test:
	.venv/bin/python -m pytest tests

run: install
	source .venv/bin/activate && python run.py

run-release: install-release
	source .venv/bin/activate && python run.py

# Build and publish commands
build:
	uv run python build_and_publish.py --build-only

publish-test:
	uv run python -m twine upload --repository testpypi target/wheels/*.whl

publish:
	uv run python build_and_publish.py

# Alias for common tasks
build-publish: publish

.PHONY: venv install install-release pre-commit test run run-release build publish-test publish build-publish

