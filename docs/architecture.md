# Architecture

## Components

- `game-research.services.vector_db` handles ChromaDB storage and retrieval
- `game-research.services.rag` implements retrieve-augment-generate pipeline
- `game-research.services.agent_workflow` orchestrates retrieval, evaluation, and web fallback
- `game-research.services.llm` wraps OpenAI chat completions

## Data Flow

1. Game JSON files are loaded and normalized with Pydantic.
2. Documents are embedded and stored in ChromaDB.
3. Queries retrieve relevant documents for context.
4. The agent evaluates retrieval quality and optionally performs web search.
5. A final answer is generated with sources.
