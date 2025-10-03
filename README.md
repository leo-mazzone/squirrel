# Squirrel

> [!IMPORTANT]  
> This is currently a personal project for learning and development. Everything on this page is aspirational. The code will be incomplete and unstable until this notice disappears.

Squirrel lets you query information from a SQL database using natural language.

## Internals
Using a directed acyclic graph of calls to an LLM, it first ensures the question can be answered given a database description. It then generates a SQL query, which is refined to update time identifiers, as well as to map a categorical variable implied by the question onto the existing categories of available columnns. The query is eventually run against the database, and results are passed to a final LLM, which generates the response.

## Example usage
```python
import squirrel
from sqlalchemy import create_engine

engine = create_engine("postgres://")

print(squirrel.ask("Who was the youngest winner of an Olympic Gold Medal in athletics last year?", engine=engine))
```

## Development
- This project uses [just](https://github.com/casey/just/) for convenience.
- Please run `pre-commit install`
- Built with assistance from [Claude Code](https://claude.ai/code)