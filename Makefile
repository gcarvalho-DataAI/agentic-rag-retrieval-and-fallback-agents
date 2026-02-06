.PHONY: setup test index search agent

setup:
	uv sync --group dev

test:
	uv run --group dev pytest -q

index:
	uv run game-research index --data data/games --store data/chromadb --collection game-research-games

search:
	uv run game-research search "Racing games on PlayStation" --collection game-research-games

agent:
	uv run game-research agent "When was Gran Turismo released?" --collection game-research-games
