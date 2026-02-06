from game_research.services.data import load_games


def test_load_games_from_dataset():
    games = load_games("data/games")
    assert len(games) >= 10
    assert games[0].name
