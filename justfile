
# List available recipes.
help:
    @just --list --unsorted

# Run all unit tests and coverage.
test:
    uv run pytest --spec --cov

# Run unit tests without coverage and special formatting.
qtest:
    uv run pytest

# Run linting and formating checks.
lint:
    uv run ruff format --check .
    uv run ruff check .

# Run security and safety checks.
safety:
    uv run vulture  --exclude .venv --min-confidence 100 .
    uv run radon mi --show --multi --min B .

# Run static typing analysis.
type:
    uv run mypy --install-types --non-interactive

# Run all checks.
check: lint type
#check: lint safety type

# Run all checks and tests.
ready: check test

# Reformat the code using ruff.
[confirm]
reformat:
    uv run ruff format .
    uv run ruff check --select I --fix .

# Extract current production requirements. Save to a file by appending `> requirements.txt`.
reqs:
    uv export --no-dev

# List all commits since the last tag.
new-commits:
    git log $(git describe --tags --abbrev=0)..HEAD --oneline --no-decorate
