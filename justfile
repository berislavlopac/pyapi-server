# List available recipes.
help:
    @just --list --unsorted

# Run all unit tests and coverage.
tests:
    pytest --spec --cov

# Run unit tests without coverage and special formatting.
tests-quick:
    pytest

# Run linting and formating checks.
check-lint:
    ruff format --check .
    isort --check .
    ruff check .

# Run static typing analysis.
check-typing:
    mypy --install-types --non-interactive

# Run all checks.
checks: check-lint check-typing

# Run all checks and tests.
ready: checks tests

# Reformat the code using isort and ruff.
[confirm]
reformat:
    isort .
    ruff format .

# Extract current production requirements. Save to a file by appending `> requirements.txt`.
reqs:
    pdm export --prod --without-hashes

# List all commits since the last tag.
new-commits:
    git log $(git describe --tags --abbrev=0)..HEAD --oneline --no-decorate
