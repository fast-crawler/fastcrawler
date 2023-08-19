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
    python test/shared/_fastapi.py & P1=$! & sleep 3

    python -m pytest & P2=$!
    wait $P1 $P2

# Task to run pre-commit checks
precommit:
    pre-commit run --all-files
