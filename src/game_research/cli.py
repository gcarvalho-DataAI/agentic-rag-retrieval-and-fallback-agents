from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from game_research.models.game import Game
from game_research.services.data import load_game, load_games, games_to_corpus
from game_research.services.vector_db import VectorStoreManager
from game_research.services.llm import LLM
from game_research.services.agent_workflow import GameResearchAgent


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise SystemExit(f"Missing required env var: {key}")
    return value


def _cmd_validate(args: argparse.Namespace) -> int:
    game = load_game(args.path)
    print(game.model_dump_json(indent=2, by_alias=True))
    return 0


def _cmd_schema(_: argparse.Namespace) -> int:
    print(json.dumps(Game.model_json_schema(), indent=2))
    return 0


def _cmd_index(args: argparse.Namespace) -> int:
    api_key = _require_env("OPENAI_API_KEY")
    manager = VectorStoreManager(api_key, persist_path=args.store)
    store = manager.get_or_create_store(args.collection)
    games = load_games(args.data)
    store.add(games_to_corpus(games))
    print(f"Indexed {len(games)} games into collection '{args.collection}'.")
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    api_key = _require_env("OPENAI_API_KEY")
    manager = VectorStoreManager(api_key, persist_path=args.store)
    store = manager.get_or_create_store(args.collection)
    results = store.query(query_texts=[args.query], n_results=args.top)
    print(json.dumps(results, indent=2))
    return 0


def _cmd_agent(args: argparse.Namespace) -> int:
    api_key = _require_env("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    manager = VectorStoreManager(api_key, persist_path=args.store)
    store = manager.get_or_create_store(args.collection)
    llm = LLM(model=args.model)
    agent = GameResearchAgent(llm=llm, vector_store=store, tavily_api_key=tavily_key)
    run = agent.run(args.query)
    answer = run.get_final_state().get("answer")
    if answer:
        print(answer.model_dump_json(indent=2))
    else:
        print(json.dumps({"answer": "No answer produced", "sources": []}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="game_research")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate a game JSON file")
    validate.add_argument("path", help="Path to game JSON file")
    validate.set_defaults(func=_cmd_validate)

    schema = sub.add_parser("schema", help="Print Game schema")
    schema.set_defaults(func=_cmd_schema)

    index = sub.add_parser("index", help="Index game dataset into ChromaDB")
    index.add_argument("--data", default="data/games", help="Path to game JSON directory")
    index.add_argument("--store", default="data/chromadb", help="Path to ChromaDB persistence dir")
    index.add_argument("--collection", default="game_research-games", help="Collection name")
    index.set_defaults(func=_cmd_index)

    search = sub.add_parser("search", help="Semantic search in ChromaDB")
    search.add_argument("query", help="Search query")
    search.add_argument("--store", default="data/chromadb", help="Path to ChromaDB persistence dir")
    search.add_argument("--collection", default="game_research-games", help="Collection name")
    search.add_argument("--top", type=int, default=3, help="Top K results")
    search.set_defaults(func=_cmd_search)

    agent = sub.add_parser("agent", help="Run the agent with fallback")
    agent.add_argument("query", help="User question")
    agent.add_argument("--store", default="data/chromadb", help="Path to ChromaDB persistence dir")
    agent.add_argument("--collection", default="game_research-games", help="Collection name")
    agent.add_argument("--model", default="gpt-4o-mini", help="LLM model")
    agent.set_defaults(func=_cmd_agent)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
