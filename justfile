# List available recipes.
help:
    @just --list --unsorted

# Run all unit tests and coverage.
test:
    pdm run pytest --spec --cov

# Run unit tests without coverage and special formatting.
test-quickly:
    pdm run pytest

# Run linting and formating checks.
check-lint:
    pdm run ruff format --check .
    pdm run isort --check .
    pdm run ruff check .

# Run static typing analysis.
check-typing:
    pdm run mypy --install-types --non-interactive

# Run all checks.
check: check-lint check-typing

# Run all checks and tests.
ready: check test

# Reformat the code using isort and ruff.
[confirm]
reformat:
    pdm run isort .
    pdm run ruff format .

# Extract current production requirements. Save to a file by appending `> requirements.txt`.
reqs:
    pdm export --prod --without-hashes

# List all commits since the last tag.
new-commits:
    git log $(git describe --tags --abbrev=0)..HEAD --oneline --no-decorate
