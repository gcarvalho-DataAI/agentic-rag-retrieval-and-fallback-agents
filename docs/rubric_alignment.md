# Rubric Alignment

## RAG

- Dataset preparation: `data/games/` JSON files
- Vector DB: `game-research.services.vector_db` with persistent ChromaDB at `data/chromadb/`
- Semantic search: `game-research search` uses vector DB query

## Agent Development

- Tools:
  - `retrieve_game` in `game-research.services.agent_workflow`
  - `evaluate_retrieval` in `game-research.services.agent_workflow`
  - `game_web_search` in `game-research.services.agent_workflow`
- Agent flow:
  - Retrieve -> Evaluate -> (optional) Web Search -> Answer
- State machine: `game-research.services.state_machine` used in `GameResearchAgent`
- Example usage: `examples/run_agent.py` (replaces notebook execution with script-based demo)
