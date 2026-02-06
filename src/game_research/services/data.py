from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from game_research.models.game import Game
from game_research.services.documents import Document, Corpus


def load_game(path: str | Path) -> Game:
    data = json.loads(Path(path).read_text())
    return Game.model_validate(data)


def load_games(directory: str | Path) -> List[Game]:
    dir_path = Path(directory)
    game_files = sorted(dir_path.glob("*.json"))
    return [load_game(path) for path in game_files]


def games_to_corpus(games: Iterable[Game]) -> Corpus:
    corpus = Corpus()
    for game in games:
        content = (
            f"Name: {game.name}\n"
            f"Platform: {game.platform}\n"
            f"Genre: {game.genre}\n"
            f"Publisher: {game.publisher}\n"
            f"Year of Release: {game.year_of_release}\n"
            f"Description: {game.description}\n"
        )
        metadata = {
            "name": game.name,
            "platform": game.platform,
            "genre": game.genre,
            "publisher": game.publisher,
            "year": game.year_of_release,
        }
        corpus.append(Document(content=content, metadata=metadata))
    return corpus

