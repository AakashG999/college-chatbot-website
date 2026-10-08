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
