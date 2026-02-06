from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, TypedDict
import time

from tavily import TavilyClient

from game_research.models.answer import Answer, Source
from game_research.services.vector_db import VectorStore
from game_research.services.llm import LLM
from game_research.services.state_machine import StateMachine, Step, EntryPoint, Termination, Run, Resource


class AgentState(TypedDict):
    query: str
    documents: List[str]
    distances: List[float]
    web_results: List[dict]
    answer: Optional[Answer]
    use_web: bool
    started_at: float


def retrieve_game(vector_store: VectorStore, query: str, n_results: int = 3) -> dict:
    """Retrieve relevant game documents from the vector database."""
    results = vector_store.query(query_texts=[query], n_results=n_results)
    documents = results["documents"][0] if results.get("documents") else []
    distances = results["distances"][0] if results.get("distances") else []
    return {"documents": documents, "distances": distances}


def evaluate_retrieval(documents: List[str], distances: List[float], max_distance: float = 0.35) -> bool:
    """Evaluate whether retrieved results are good enough to answer locally."""
    if not documents or not distances:
        return False
    return min(distances) <= max_distance


def game_web_search(client: TavilyClient, query: str, max_results: int = 5) -> List[dict]:
    """Fallback web search for game information."""
    response = client.search(query=query, max_results=max_results)
    return response.get("results", [])


@dataclass
class GameResearchAgent:
    llm: LLM
    vector_store: VectorStore
    tavily_api_key: Optional[str] = None
    max_distance: float = 0.35

    def __post_init__(self):
        self.workflow = self._create_state_machine()
        self.resource = Resource(
            vars={
                "llm": self.llm,
                "vector_store": self.vector_store,
                "tavily_api_key": self.tavily_api_key,
                "max_distance": self.max_distance,
            }
        )

    def _retrieve_step(self, state: AgentState, resource: Resource) -> AgentState:
        vector_store: VectorStore = resource.vars["vector_store"]
        result = retrieve_game(vector_store, state["query"])
        return {"documents": result["documents"], "distances": result["distances"]}

    def _evaluate_step(self, state: AgentState, resource: Resource) -> AgentState:
        max_distance = resource.vars["max_distance"]
        use_web = not evaluate_retrieval(state["documents"], state["distances"], max_distance=max_distance)
        return {"use_web": use_web}

    def _web_search_step(self, state: AgentState, resource: Resource) -> AgentState:
        api_key = resource.vars.get("tavily_api_key")
        if not api_key:
            return {"web_results": []}
        client = TavilyClient(api_key=api_key)
        results = game_web_search(client, state["query"])
        return {"web_results": results}

    def _answer_step(self, state: AgentState, resource: Resource) -> AgentState:
        llm: LLM = resource.vars["llm"]
        context_chunks = state["documents"]
        web_chunks = state.get("web_results", [])

        context = "\n\n".join(context_chunks)
        web_context = "\n\n".join(
            f"Title: {item.get('title')}\nURL: {item.get('url')}\nContent: {item.get('content')}"
            for item in web_chunks
        )

        prompt = (
            "You are a game research assistant. Answer the user question using the context below. "
            "If you rely on the web results, cite them in the sources list. "
            "Return a concise answer and a list of sources.\n\n"
            f"Question: {state['query']}\n\n"
            f"Local Context:\n{context}\n\n"
            f"Web Context:\n{web_context}\n"
        )

        response = llm.invoke(prompt, response_format=Answer)
        return {"answer": response.parsed if hasattr(response, 'parsed') and response.parsed else Answer(answer=response.content, sources=[])}

    def _create_state_machine(self) -> StateMachine[AgentState]:
        machine = StateMachine[AgentState](AgentState)
        entry = EntryPoint[AgentState]()
        retrieve = Step[AgentState]("retrieve", self._retrieve_step)
        evaluate = Step[AgentState]("evaluate", self._evaluate_step)
        web_search = Step[AgentState]("web_search", self._web_search_step)
        answer = Step[AgentState]("answer", self._answer_step)
        termination = Termination[AgentState]()

        machine.add_steps([entry, retrieve, evaluate, web_search, answer, termination])
        machine.connect(entry, retrieve)
        machine.connect(retrieve, evaluate)

        def route(state: AgentState):
            return web_search if state.get("use_web") else answer

        machine.connect(evaluate, [web_search, answer], route)
        machine.connect(web_search, answer)
        machine.connect(answer, termination)
        return machine

    def run(self, query: str) -> Run:
        initial_state: AgentState = {
            "query": query,
            "documents": [],
            "distances": [],
            "web_results": [],
            "answer": None,
            "use_web": False,
            "started_at": time.time(),
        }
        return self.workflow.run(state=initial_state, resource=self.resource)
