import os

from game_research.services.vector_db import VectorStoreManager
from game_research.services.data import load_games, games_to_corpus
from game_research.services.rag import RAG
from game_research.services.llm import LLM

# Requires OPENAI_API_KEY

def main():
    api_key = os.environ["OPENAI_API_KEY"]
    manager = VectorStoreManager(openai_api_key=api_key, persist_path="data/chromadb")
    store = manager.get_or_create_store("game_research-games")
    games = load_games("data/games")
    store.add(games_to_corpus(games))

    rag = RAG(llm=LLM(), vector_store=store)
    run = rag.invoke("When was Gran Turismo released?")
    print(run.get_final_state()["answer"])


if __name__ == "__main__":
    main()
