import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.graph import college_chatbot_graph
from app.suggestions import STARTER_SUGGESTIONS, suggestions_for

router = APIRouter()


class ChatTurn(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatTurn] = []


class ChatResponse(BaseModel):
    reply: str
    category: str
    sources: list[str]
    # Follow-up question chips, picked from the routed category.
    suggestions: list[str] = []


def _to_lc_messages(history: list[ChatTurn]):
    messages = []
    for turn in history:
        if turn.role == "user":
            messages.append(HumanMessage(content=turn.content))
        elif turn.role == "assistant":
            messages.append(AIMessage(content=turn.content))
    return messages


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty")

    messages = _to_lc_messages(request.history)
    messages.append(HumanMessage(content=request.message))

    try:
        result = college_chatbot_graph.invoke({"messages": messages})
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the client
        raise HTTPException(status_code=502, detail=f"Chatbot agent failed: {exc}") from exc

    reply = result["messages"][-1].content
    category = result.get("category", "contact")
    return ChatResponse(
        reply=reply,
        category=category,
        sources=result.get("sources", []),
        suggestions=suggestions_for(category),
    )


@router.get("/suggestions")
def starter_suggestions():
    """Chips to show before the first question has been asked."""
    return {"suggestions": STARTER_SUGGESTIONS}


@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    """Same pipeline as /chat, but reports progress as each node finishes.

    LangGraph's .stream(stream_mode="updates") yields once per completed
    node, so the status the user sees tracks where the graph actually is --
    it isn't a timer guessing at progress. Each emitted label describes the
    node that is about to run:

        (start)          -> "Understanding your question"
        router done      -> "Searching the <category> documents"
        retrieve done    -> "Collating <n> sources and writing your answer"
        answer done      -> final payload

    It also forwards the answer token by token ({"type": "token"}), so the
    reply types itself into the bubble instead of landing in one block.
    Mock mode has no streaming model, so no token events arrive there and
    the client falls back to the full reply in the final payload.

    Newline-delimited JSON rather than SSE, because the browser needs to
    POST the conversation history and EventSource can't.

    /chat is unchanged and still the simpler option for scripts and curl.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty")

    messages = _to_lc_messages(request.history)
    messages.append(HumanMessage(content=request.message))

    def event(payload: dict) -> str:
        return json.dumps(payload) + "\n"

    def generate():
        yield event({"type": "status", "label": "Understanding your question"})

        state: dict = {}
        try:
            # Two modes at once: "updates" for node transitions (the status
            # line) and "messages" for individual LLM tokens (the answer
            # appearing as it's written).
            for mode, chunk in college_chatbot_graph.stream(
                {"messages": messages}, stream_mode=["updates", "messages"]
            ):
                if mode == "messages":
                    message_chunk, metadata = chunk
                    # The router is an LLM call too -- only forward tokens
                    # from the node that writes the answer.
                    if metadata.get("langgraph_node") != "answer":
                        continue
                    text = getattr(message_chunk, "content", "")
                    if text:
                        yield event({"type": "token", "text": text})
                    continue

                for node, payload in chunk.items():
                    state.update(payload or {})

                    if node == "router":
                        category = state.get("category", "relevant")
                        yield event({
                            "type": "status",
                            "label": f"Searching the {category} documents",
                        })
                    elif node == "retrieve":
                        count = len(state.get("sources") or [])
                        noun = "source" if count == 1 else "sources"
                        yield event({
                            "type": "status",
                            "label": f"Collating {count} {noun} and writing your answer",
                        })
        except Exception as exc:  # noqa: BLE001 - must reach the client as an event
            yield event({"type": "error", "detail": f"Chatbot agent failed: {exc}"})
            return

        reply_messages = state.get("messages") or []
        if not reply_messages:
            yield event({"type": "error", "detail": "The agent produced no answer."})
            return

        category = state.get("category", "contact")
        yield event({
            "type": "done",
            "reply": reply_messages[-1].content,
            "category": category,
            "sources": state.get("sources", []),
            "suggestions": suggestions_for(category),
        })

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
        headers={
            # Without nosniff, Chrome buffers the first chunk of the body to
            # sniff its type, so the browser sees the answer arrive in a few
            # large lumps instead of token by token.
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-cache, no-store",
            # Tells nginx and friends not to buffer this response either.
            "X-Accel-Buffering": "no",
        },
    )
