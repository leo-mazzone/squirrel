# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and [just](https://github.com/casey/just/) for task automation.

- **Format and lint**: `just format` (runs `uv run ruff format .` and `uv run ruff check . --fix`)
- **Type checking**: `just typecheck` (runs `uv run pyright`)
- **Run tests**: `uv run pytest`
- **Run example**: `python example.py` (requires `GEMINI_API_KEY` environment variable)

Pre-commit hooks are configured to run formatting, linting, and type checking automatically.

## Architecture

Squirrel is a natural language to SQL query system built as a LangGraph DAG (Directed Acyclic Graph) with three main processing stages:

### Core Components

**State Management (`dag.py:GraphState`)**
- Tracks engine, question, validation status, SQL query, results, and response throughout the pipeline

**Processing Nodes (`dag.py`)**
1. **Validator Node**: Uses LLM to check if question can be answered from database schema
2. **Retriever Node**: Generates SQL query from question and database context
3. **Generator Node**: Creates natural language response from query results
4. **Refusal Node**: Handles cases where question cannot be answered

**Database Interface (`db.py`)**
- `describe_db()`: Extracts and formats database schema as JSON for LLM context
- `results_as_str()`: Executes SQL and formats results using Polars

**LLM Chains (`prompts.py`)**
- Three specialized chains using Google Gemini 2.0 Flash model
- Requires `GEMINI_API_KEY` environment variable
- Each chain has specific prompts for validation, SQL generation, and response generation

### Data Flow
Question → Validation → (Valid?) → SQL Generation → Query Execution → Response Generation → Final Answer

The system uses SQLAlchemy engines and includes a sample Chinook database (`chinook.db`) for testing.

## Key Dependencies
- **LangChain/LangGraph**: LLM orchestration and graph execution
- **SQLAlchemy**: Database connections and inspection
- **Polars**: Fast query result processing
- **Google GenAI**: LLM provider (requires API key)