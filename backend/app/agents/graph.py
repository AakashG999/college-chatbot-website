"""LangGraph multi-agent pipeline for the college admin chatbot.

Graph shape:

    START -> router_node -> retrieve_node -> answer_node -> END

- router_node: an LLM agent that classifies the incoming question into one
  or more college-admin categories (admissions, fees, exams, hostel, ...).
  A question like "hostel fees and exam dates?" is multi-intent and routes
  to every topic it touches, most relevant first.
- retrieve_node: performs RAG retrieval against the Chroma vector store once
  per routed category, merging the results, and falls back to an unfiltered
  search if nothing relevant is found in any of them.
- answer_node: an LLM agent that composes the final answer strictly from the
  retrieved context plus the running conversation history, covering every
  part of a multi-intent question.
"""
import re
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config import settings
from app.agents.prompts import ROUTER_SYSTEM_PROMPT, ANSWER_SYSTEM_PROMPT
from app.rag.retriever import retrieve, VALID_CATEGORIES


# A question rarely spans more than a few topics; past this, the per-topic
# retrieval budget gets too thin to be useful.
MAX_INTENTS = 3

# Chunks per question, split across its categories (never fewer than
# MIN_CHUNKS_PER_CATEGORY each), so a multi-intent question doesn't flood
# the answer prompt.
TOTAL_CHUNKS = 6
MIN_CHUNKS_PER_CATEGORY = 2


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
    # Every topic the question touches, most relevant first.
    categories: list[str]
    # categories[0] -- kept for callers that only want the main topic.
    category: str
    context: str
    sources: list[str]


def _llm(temperature: float = 0.0):
    if settings.use_mock:
        from app.agents.mock_llm import MockChatModel

        return MockChatModel()

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.chat_model,
        temperature=temperature,
        api_key=settings.openai_api_key,
        # Needed for token-level callbacks, which is how /api/chat/stream
        # forwards the answer to the browser as it's written. .invoke() still
        # returns the whole message, so the non-streaming path is unaffected.
        streaming=True,
    )


def parse_categories(raw: str) -> list[str]:
    """Turn the router's reply ("hostel, exams") into valid, de-duplicated
    categories in the order given. Anything unrecognised is dropped; if
    nothing survives, the question goes to the catch-all "contact"."""
    categories = []
    for token in re.split(r"[\s,;]+", raw.strip().lower()):
        token = token.strip(".`'\"-")
        if token in VALID_CATEGORIES and token not in categories:
            categories.append(token)
    return categories[:MAX_INTENTS] or ["contact"]


def router_node(state: ChatState) -> dict:
    last_user_message = state["messages"][-1].content
    response = _llm().invoke(
        [
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=last_user_message),
        ]
    )
    categories = parse_categories(response.content)
    return {"categories": categories, "category": categories[0]}


def retrieve_node(state: ChatState) -> dict:
    last_user_message = state["messages"][-1].content
    categories = state.get("categories") or [state.get("category") or "contact"]

    # One filtered search per topic, so a two-part question gets material
    # for both parts instead of only whichever topic dominates the embedding.
    if len(categories) == 1:
        k = 4  # same as before multi-intent support
    else:
        k = max(MIN_CHUNKS_PER_CATEGORY, TOTAL_CHUNKS // len(categories))
    docs, seen = [], set()
    for category in categories:
        for d in retrieve(last_user_message, category=category, k=k):
            key = (d.metadata.get("source"), d.page_content)
            if key not in seen:
                seen.add(key)
                docs.append(d)

    if not docs:
        # Fall back to an unfiltered search across the whole knowledge base.
        docs = retrieve(last_user_message, category=None, k=4)

    context = "\n\n---\n\n".join(
        f"[source: {d.metadata.get('source', 'unknown')} | "
        f"category: {d.metadata.get('category', 'general')}]\n{d.page_content}"
        for d in docs
    )
    sources = sorted({d.metadata.get("source", "unknown") for d in docs})
    return {"context": context, "sources": sources}


def answer_node(state: ChatState) -> dict:
    context = state.get("context", "")
    history = state["messages"]

    prompt_messages = [
        SystemMessage(content=ANSWER_SYSTEM_PROMPT),
        *history[:-1],  # prior conversation turns, if any
        HumanMessage(
            content=(
                f"Context from college documents:\n{context}\n\n"
                f"Student question: {history[-1].content}"
            )
        ),
    ]
    response = _llm(temperature=0.3).invoke(prompt_messages)
    return {"messages": [AIMessage(content=response.content)]}


def build_graph():
    graph = StateGraph(ChatState)
    graph.add_node("router", router_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("answer", answer_node)

    graph.add_edge(START, "router")
    graph.add_edge("router", "retrieve")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


# Compiled once at import time; FastAPI reuses this across requests.
college_chatbot_graph = build_graph()
