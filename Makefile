all: fmt lint type-check-strict test docker-test

fmt:
	isort src/**/*.py
	black --line-length 120 .

lint:
	ruff check .

lint-fix:
	ruff check . --fix

type-check:
	mypy .

type-check-strict:
	mypy . --strict

test:
	pytest
