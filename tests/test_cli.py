import json
import subprocess


def test_cli_schema_outputs_json():
    result = subprocess.run(
        ["uv", "run", "game-research", "schema"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert "properties" in payload


def test_cli_validate_game():
    result = subprocess.run(
        ["uv", "run", "game-research", "validate", "data/games/001.json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["Name"] == "Gran Turismo"
