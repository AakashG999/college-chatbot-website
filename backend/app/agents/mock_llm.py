"""A dependency-free stand-in for ChatOpenAI, used only when
USE_MOCK_LLM=true, so the LangGraph pipeline (router -> retrieve -> answer)
can be run end-to-end with no API key and no network access.

- Routing is done with simple keyword matching instead of an LLM call. Every
  category with a keyword hit is returned (most hits first, ties broken by
  where the topic is mentioned), so multi-intent questions route to several.
- The "answer" is extractive: it returns the top retrieved excerpt for each
  routed category verbatim with a [MOCK MODE] label, rather than a
  generated, synthesized response.

This is for local wiring/retrieval testing only. Swap back to the real
ChatOpenAI path (the default when USE_MOCK_LLM is unset) for actual answer
quality.
"""
from langchain_core.messages import AIMessage

CATEGORY_KEYWORDS = {
    # Keywords are deliberately specific (multi-word phrases where possible)
    # to avoid generic terms like "apply" or "eligible" colliding across
    # categories (e.g. "apply for a scholarship" vs. "apply for admission").
    "admissions": ["admission", "application form", "entrance test", "enroll", "transfer admission"],
    "fees": ["fee", "tuition", "scholarship", "payment", "refund", "financial aid", "waiver"],
    "academics": ["semester", "attendance", "cgpa", "grade", "elective", "curriculum", "credit", "probation"],
    "exams": ["exam", "admit card", "revaluation", "backlog", "supplementary", "malpractice"],
    "hostel": ["hostel", "mess", "curfew", "room", "accommodation"],
    "library": ["library", "book", "journal", "borrow"],
    "it": ["wifi", "wi-fi", "portal", "password", "email account", "login", "it helpdesk"],
    "conduct": ["ragging", "conduct", "harassment", "posh", "discipline", "icc"],
    "grievance": ["grievance", "complaint", "escalat"],
    "placements": ["placement", "internship", "recruit", "career", "resume"],
    "campus-life": ["club", "fest", "transport", "bus", "sports", "student council"],
    "international": ["international student", "visa", "frro", "exchange program"],
    "health": ["health center", "medical", "doctor", "insurance", "counsel", "wellness"],
    "alumni": ["convocation", "alumni", "degree certificate", "graduation"],
    "contact": ["contact", "office hours", "address", "phone number", "email the"],
}


class MockChatModel:
    """Drop-in replacement for the `.invoke(messages) -> AIMessage` interface
    the graph expects, backed entirely by local keyword logic."""

    def invoke(self, messages):
        system_content = messages[0].content if messages else ""
        last_human = next(
            (
                m.content
                for m in reversed(messages)
                if m.__class__.__name__ == "HumanMessage"
            ),
            "",
        )

        if "Classify the student's question" in system_content:
            return AIMessage(content=self._classify(last_human))
        return AIMessage(content=self._answer(last_human))

    def _classify(self, question: str, limit: int = 3) -> str:
        q = question.lower()
        scored = []
        for category, keywords in CATEGORY_KEYWORDS.items():
            positions = [q.find(kw) for kw in keywords if kw in q]
            if positions:
                # "contact" is the catch-all, so it loses ties to real topics.
                scored.append(
                    (-len(positions), category == "contact", min(positions), category)
                )
        if not scored:
            return "contact"
        return ", ".join(category for *_, category in sorted(scored)[:limit])

    def _answer(self, prompt_text: str) -> str:
        # answer_node builds the human prompt as:
        #   "Context from college documents:\n<context>\n\nStudent question: <q>"
        if "Context from college documents:" in prompt_text:
            context_part = prompt_text.split("Context from college documents:", 1)[1]
            context_part = context_part.split("Student question:", 1)[0].strip()
        else:
            context_part = ""

        if not context_part:
            return (
                "[MOCK MODE] No relevant context was retrieved from the "
                "knowledge base for this question."
            )

        # retrieve_node lists excerpts grouped by category, best first, each
        # headed "[source: ... | category: <c>]". Take the top one per
        # category so every part of a multi-intent question is answered.
        excerpts, seen = [], set()
        for excerpt in context_part.split("\n\n---\n\n"):
            header = excerpt.strip().split("\n", 1)[0]
            category = header.rsplit("category:", 1)[-1].strip(" ]")
            if category not in seen:
                seen.add(category)
                excerpts.append(excerpt.strip())
        return (
            "[MOCK MODE — extractive stand-in, not a real LLM response]\n\n"
            + "\n\n---\n\n".join(excerpts)
        )
