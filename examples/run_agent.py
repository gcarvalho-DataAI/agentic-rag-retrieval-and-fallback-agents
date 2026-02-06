import os
from game_research.services.vector_db import VectorStoreManager
from game_research.services.data import load_games, games_to_corpus
from game_research.services.llm import LLM
from game_research.services.agent_workflow import GameResearchAgent

QUERIES = [
    "When was Gran Turismo released?",
    "Which platform did Tekken 3 release on?",
    "Who published Final Fantasy VII?",
]


def main():
    api_key = os.environ["OPENAI_API_KEY"]
    tavily_key = os.getenv("TAVILY_API_KEY")

    manager = VectorStoreManager(openai_api_key=api_key, persist_path="data/chromadb")
    store = manager.get_or_create_store("game_research-games")

    games = load_games("data/games")
    store.add(games_to_corpus(games))

    agent = GameResearchAgent(llm=LLM(), vector_store=store, tavily_api_key=tavily_key)

    for query in QUERIES:
        run = agent.run(query)
        answer = run.get_final_state().get("answer")
        print(f"\nQuery: {query}")
        if answer:
            print(answer.model_dump_json(indent=2))
        else:
            print("No answer returned")


if __name__ == "__main__":
    main()
