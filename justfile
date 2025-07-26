# Reformat and lint
format:
    uv run ruff format .
    uv run ruff check . --fix

# Static type check
typecheck:
    uv run pyright
