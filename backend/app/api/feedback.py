"""Thumbs up / down on chatbot answers, with a follow-up form on a dislike.

DUMMY STORAGE: feedback is appended to a list in process memory, so it's
gone on restart and not shared across workers. Point _FEEDBACK at a real
table before this is worth anything.

What the dislike form asks for depends on who's signed in:
  - guests    -> contact number + reason (there's no other way to reach them)
  - students  -> reason only (the roll number is already on the session)

The split is enforced here, not just in the UI, so the rule holds even if
someone posts straight to the endpoint.
"""
import re
import time

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.api.auth import _bearer_token, get_session

router = APIRouter()

RATINGS = {"like", "dislike"}
MAX_REASON_CHARS = 1000

# Indian mobile numbers: 10 digits. Anything the user types is stripped of
# spaces, dashes and a +91 prefix before this is applied.
CONTACT_RE = re.compile(r"^\d{10}$")

_FEEDBACK: list[dict] = []
_NEXT_ID = {"value": 1}

# feedback id -> the session token that submitted it, so only the person who
# left a rating can retract it. Kept out of _FEEDBACK so the demo GET below
# can't leak tokens. A real build would key on a user id instead.
_OWNERS: dict[int, str | None] = {}


class FeedbackBody(BaseModel):
    rating: str
    question: str = ""
    answer: str = ""
    reason: str = ""
    contact_number: str = ""


def _normalise_contact(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    # Tolerate 0-prefixed and +91-prefixed forms.
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    return digits


@router.post("/feedback")
def submit_feedback(body: FeedbackBody, authorization: str | None = Header(default=None)):
    rating = body.rating.strip().lower()
    if rating not in RATINGS:
        raise HTTPException(status_code=400, detail="rating must be 'like' or 'dislike'.")

    session = get_session(_bearer_token(authorization))
    # No session means we can't tell who this is, so treat them as a guest
    # and ask for a contact number.
    is_guest = session is None or session.get("kind") == "guest"

    reason = body.reason.strip()
    contact = ""

    if rating == "dislike":
        if not reason:
            raise HTTPException(
                status_code=400,
                detail="Please tell us what was wrong with the answer.",
            )
        if len(reason) > MAX_REASON_CHARS:
            raise HTTPException(
                status_code=400,
                detail=f"Please keep the reason under {MAX_REASON_CHARS} characters.",
            )
        if is_guest:
            contact = _normalise_contact(body.contact_number)
            if not CONTACT_RE.match(contact):
                raise HTTPException(
                    status_code=400,
                    detail="Please enter a valid 10 digit contact number.",
                )

    feedback_id = _NEXT_ID["value"]
    _NEXT_ID["value"] += 1

    entry = {
        "id": feedback_id,
        "rating": rating,
        "reason": reason,
        "contact_number": contact,
        "user_kind": "guest" if is_guest else "student",
        "roll_number": None if session is None else session.get("roll_number"),
        "question": body.question[:500],
        "answer": body.answer[:1000],
        "created_at": time.time(),
    }
    _FEEDBACK.append(entry)
    _OWNERS[feedback_id] = _bearer_token(authorization)

    who = entry["roll_number"] or entry["user_kind"]
    print(
        f"[feedback] #{feedback_id} {rating} from {who}"
        + (f" | reason: {reason[:80]}" if reason else "")
        + (f" | contact: {contact}" if contact else "")
    )

    return {
        "id": feedback_id,
        "message": "Thanks for the feedback."
        if rating == "like"
        else "Thanks — we've logged this and the team will take a look.",
        "requires_contact": is_guest,
    }


@router.delete("/feedback/{feedback_id}")
def retract_feedback(feedback_id: int, authorization: str | None = Header(default=None)):
    """Undo a rating -- the user tapped the same thumb again.

    Only the session that left it can retract it. Already-gone ids return
    200 rather than 404, so a double-tap race doesn't surface an error.
    """
    entry = next((f for f in _FEEDBACK if f["id"] == feedback_id), None)
    if entry is None:
        return {"message": "Already removed.", "removed": False}

    if _OWNERS.get(feedback_id) != _bearer_token(authorization):
        raise HTTPException(
            status_code=403, detail="That feedback belongs to a different session."
        )

    _FEEDBACK.remove(entry)
    _OWNERS.pop(feedback_id, None)
    print(f"[feedback] #{feedback_id} retracted")
    return {"message": "Feedback removed.", "removed": True}


@router.get("/feedback")
def list_feedback():
    """DEMO ONLY -- unauthenticated read of everything submitted, including
    contact numbers. Delete this or put it behind staff auth; it exists so
    the flow can be verified without a database."""
    return {
        "count": len(_FEEDBACK),
        "likes": sum(1 for f in _FEEDBACK if f["rating"] == "like"),
        "dislikes": sum(1 for f in _FEEDBACK if f["rating"] == "dislike"),
        "items": _FEEDBACK,
    }
