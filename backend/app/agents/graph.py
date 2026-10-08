"""LangGraph multi-agent pipeline for the college admin chatbot.

Graph shape:

    START -> router_node -> retrieve_node -> answer_node -> END

- router_node: an LLM agent that classifies the incoming question into a
  college-admin category (admissions, fees, academics, exams, hostel, contact).
- retrieve_node: performs RAG retrieval against the Chroma vector store,
  filtered by the routed category, falling back to an unfiltered search if
  nothing relevant is found in that category.
- answer_node: an LLM agent that composes the final answer strictly from the
  retrieved context plus the running conversation history.
"""
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config import settings
from app.agents.prompts import ROUTER_SYSTEM_PROMPT, ANSWER_SYSTEM_PROMPT
from app.rag.retriever import retrieve, VALID_CATEGORIES


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
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


def router_node(state: ChatState) -> dict:
    last_user_message = state["messages"][-1].content
    response = _llm().invoke(
        [
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=last_user_message),
        ]
    )
    category = response.content.strip().lower()
    if category not in VALID_CATEGORIES:
        category = "contact"
    return {"category": category}


def retrieve_node(state: ChatState) -> dict:
    last_user_message = state["messages"][-1].content
    category = state.get("category")

    docs = retrieve(last_user_message, category=category, k=4)
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
