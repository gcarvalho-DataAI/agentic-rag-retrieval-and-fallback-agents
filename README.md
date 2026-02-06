# Game Research Agent

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

Game Research Agent is a recruiter-ready, product-structured agent that uses a local vector database (ChromaDB) for RAG and falls back to web search when internal knowledge is insufficient.

## Quickstart

```bash
uv sync --group dev
game-research schema
```

## Index and Query

```bash
export OPENAI_API_KEY="..."
uv run game-research index --data data/games --store data/chromadb --collection game-research
uv run game-research search "Racing games on PlayStation" --collection game-research
```

## Agent with Fallback

```bash
export OPENAI_API_KEY="..."
export TAVILY_API_KEY="..."
uv run game-research agent "When was Gran Turismo released?" --collection game-research
```

## Project Layout

- `src/game_research/` package source
- `src/game_research/models/` Pydantic models
- `src/game_research/services/` RAG, tools, state machine, vector DB
- `data/games/` game dataset (JSON)
- `data/chromadb/` persistent ChromaDB
- `examples/` runnable demos
- `docs/` product docs
- `tests/` unit tests

## Development

```bash
uv sync --group dev
uv run --group dev pytest -q
```

## License

See `LICENSE.md`.
