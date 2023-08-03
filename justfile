# Justfile

default:
    help

# Help task to display available tasks
help:
    @echo "Available tasks:"
    @echo "  test       - Run tests using pytest."
    @echo "  precommit  - Run pre-commit checks."

# Task to run tests using pytest
test:
    @echo "Running tests..."
    python -m pytest

# Task to run pre-commit checks
precommit:
    @echo "Running pre-commit checks..."
    pre-commit run --all-files
