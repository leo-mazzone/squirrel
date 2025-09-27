# Claude Code Configuration for Squirrel

## Project Overview
Squirrel is a natural language to SQL query system using LLMs and directed acyclic graphs. It processes user questions, generates and refines SQL queries, and provides natural language responses.

## Technology Stack
- **Language**: Python 3.13+
- **Package Manager**: uv
- **LLM Framework**: LangChain + LangGraph
- **Database**: SQLAlchemy (currently using SQLite with chinook.db for testing)
- **Task Runner**: just
- **Linting/Formatting**: ruff
- **Type Checking**: pyright
- **Testing**: pytest
- **Pre-commit**: Configured with ruff and typecheck hooks

## Development Workflow

### Formatting & Linting
- **ALWAYS run `just format` after making code changes** 
- This runs `ruff format` and `ruff check --fix`
- Line length limit: 88 characters
- Fix any formatting violations before completing tasks

### Type Checking
- Run `just typecheck` to perform static type analysis with pyright
- Ensure type safety before completing tasks

### Testing
- Run tests with `pytest` or `uv run pytest`
- Key test files:
  - `test/test_basic.py` - Basic functionality tests
  - `test/test_dates.py` - Date processing tests
- Test database: `chinook.db` (SQLite)

### Pre-commit Hooks
- Pre-commit is configured to run formatting and type checking
- Install with `pre-commit install`

## Code Structure
- `src/squirrel/` - Main package
  - `dag.py` - Main DAG implementation for query processing
  - `dates.py` - Date expression processing
  - `db.py` - Database utilities
  - `prompts.py` - LLM prompts and parsing

## Key Commands
- `just format` - Format and lint code
- `just typecheck` - Run type checker
- `pytest` - Run tests
- `uv run [command]` - Run commands in project environment

## Important Notes
- Always ensure formatting passes before completing tasks
- Follow existing code patterns and conventions
- Use type hints consistently
- Test date processing functionality thoroughly
- The project uses uv for dependency management