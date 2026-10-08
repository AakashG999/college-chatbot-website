"""Follow-up question chips shown under each answer.

These are keyed off the category the router already picked, so they cost
nothing extra -- no second LLM call, no latency, and every suggestion is
answerable from the knowledge base in app/data (which is the point: a
generated follow-up can easily ask something the docs don't cover).

Keep them short. They render as pills in a 360px wide chat window, so
anything past ~45 characters wraps badly.

The trade-off: they're fixed per category rather than tailored to the exact
question. If you want genuinely conversational follow-ups, generate them in
answer_node from the retrieved context and return them through the graph
state instead.
"""
import re
from collections import Counter
from itertools import zip_longest


CATEGORY_SUGGESTIONS: dict[str, list[str]] = {
    "admissions": [
        "What documents do I need?",
        "When is the application deadline?",
        "Is there a lateral entry option?",
    ],
    "fees": [
        "What scholarships can I apply for?",
        "How do I pay my fees?",
        "What if I pay late?",
    ],
    "academics": [
        "How does the CGPA system work?",
        "What is the attendance requirement?",
        "Can I take open electives?",
    ],
    "exams": [
        "How do I apply for revaluation?",
        "When are admit cards released?",
        "What if I fail a course?",
    ],
    "hostel": [
        "What are the hostel fees?",
        "What is the curfew time?",
        "Can I change my meal plan?",
    ],
    "library": [
        "How many books can I borrow?",
        "What are the library timings?",
        "Are there group study rooms?",
    ],
    "it": [
        "How do I reset my portal password?",
        "How do I get campus Wi-Fi?",
        "Where is the IT helpdesk?",
    ],
    "conduct": [
        "How do I report ragging?",
        "What does the ICC handle?",
        "What are the disciplinary penalties?",
    ],
    "grievance": [
        "How long does resolution take?",
        "How do I escalate a grievance?",
        "Where do I file a complaint?",
    ],
    "placements": [
        "What is the placement eligibility?",
        "When is the placement season?",
        "Are internships available?",
    ],
    "campus-life": [
        "What student clubs are there?",
        "Tell me about the annual fests",
        "Is there a campus bus service?",
    ],
    "international": [
        "How does FRRO registration work?",
        "Are there exchange programs?",
        "How do international students apply?",
    ],
    "health": [
        "What are the health centre timings?",
        "Is medical insurance included?",
        "How do I book counselling?",
    ],
    "alumni": [
        "When is convocation held?",
        "How do I get my degree certificate?",
        "What does the alumni association do?",
    ],
    "contact": [
        "What are the office hours?",
        "How do I reach the accounts office?",
        "Where is the campus located?",
    ],
}

# Shown before the first question, and as a fallback for an unknown category.
STARTER_SUGGESTIONS = [
    "How do I apply for admission?",
    "What are the tuition fees?",
    "What is the attendance requirement?",
    "What are the hostel rules?",
]

MAX_SUGGESTIONS = 3


def suggestions_for(category: str | None) -> list[str]:
    return CATEGORY_SUGGESTIONS.get(category or "", STARTER_SUGGESTIONS)[:MAX_SUGGESTIONS]


_STOPWORDS = {
    "a", "about", "an", "and", "any", "are", "can", "do", "does", "for",
    "get", "how", "i", "if", "in", "is", "it", "many", "me", "my", "of",
    "on", "tell", "the", "there", "to", "what", "when", "where",
}


def _content_words(text: str) -> set[str]:
    """Lowercased words minus stopwords, with a plural "s" dropped so
    "fees"/"fee" and "timings"/"timing" match."""
    words = set()
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        if w in _STOPWORDS:
            continue
        words.add(w[:-1] if len(w) > 3 and w.endswith("s") else w)
    return words


# Words used by exactly one chip ("curfew", "revaluation") pin down what
# that chip asks; shared ones ("hostel", "fees") only name the topic.
_word_counts = Counter(
    w
    for q in {q for pool in CATEGORY_SUGGESTIONS.values() for q in pool}
    | set(STARTER_SUGGESTIONS)
    for w in _content_words(q)
)


def _already_asked(suggestion: str, asked_words: set[str]) -> bool:
    words = _content_words(suggestion)
    matched = words & asked_words
    if not words or not matched:
        return False
    # "What are the hostel fees?" after "hostel fees?" -- every word asked.
    if matched == words:
        return True
    # "What is the curfew time?" after "...hostel curfew...?" -- a word only
    # this chip uses, covering at least half of it. The half rule stops a
    # stray verb ("change") from hiding "Can I change my meal plan?".
    has_distinctive = any(_word_counts[w] == 1 for w in matched)
    return has_distinctive and 2 * len(matched) >= len(words)


def suggestions_for_categories(
    categories: list[str] | None, asked: list[str] = ()
) -> list[str]:
    """Chips for an answer: take turns across its categories so each topic
    gets at least one follow-up before any gets a second, skipping any the
    student has already asked (`asked` = their questions so far) -- the
    answer has covered those, so offering them again is noise."""
    asked_words = set().union(*(_content_words(q) for q in asked))
    pools = [CATEGORY_SUGGESTIONS.get(c, []) for c in categories or []]
    picked = []
    for row in zip_longest(*pools):
        picked.extend(
            q for q in row
            if q and q not in picked and not _already_asked(q, asked_words)
        )
    if not picked:
        picked = [q for q in STARTER_SUGGESTIONS if not _already_asked(q, asked_words)]
    return picked[:MAX_SUGGESTIONS]
