"""DUMMY sign-in: 5-digit roll number -> 4-digit OTP "emailed" -> session.

Visitors can also skip all of that and sign in as a guest (POST /auth/guest),
which issues a session with kind == "guest" and no identity attached.

=============================================================================
THIS IS NOT REAL AUTHENTICATION. Do not ship it.
=============================================================================

What's fake here, and what you'd replace it with:

- There is no student records lookup at all: ANY 5-digit number is accepted.
  Recognised demo roll numbers (DUMMY_STUDENTS) get a name-shaped email;
  anything else gets a derived student<roll>@... address. A real build looks
  the student up and rejects unknown roll numbers.
- The OTP is never emailed. It's printed to the server log AND returned in
  the response as `demo_otp` so the flow can be clicked through in a browser.
  A real build sends it over email/SMS and NEVER returns it to the client.
- OTPs and sessions are plain dicts in process memory, so they vanish on
  restart and aren't shared across workers. Use Redis or a database.
- Session tokens are random strings with no expiry and no signature. Use
  signed, expiring tokens (JWT or server-side sessions).
- Rate limiting is per-roll-number and in-memory only; there's nothing
  stopping an attacker cycling roll numbers or IPs.

The /api/chat endpoint deliberately does NOT require any of this -- the gate
is cosmetic, to demo the flow. See the note at the bottom of this file for
what enforcing it would involve.
"""
import random
import re
import secrets
import time

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter()

ROLL_NUMBER_RE = re.compile(r"^\d{5}$")
OTP_RE = re.compile(r"^\d{4}$")

OTP_TTL_SECONDS = 5 * 60
MAX_VERIFY_ATTEMPTS = 5

# Recognised demo roll numbers get a realistic-looking address. Any other
# 5-digit number is still accepted -- see _email_for().
DUMMY_STUDENTS = {
    "10234": "aarav.sharma@greenfieldcollege.edu",
    "10235": "priya.nair@greenfieldcollege.edu",
    "10236": "rohan.mehta@greenfieldcollege.edu",
    "20481": "ananya.iyer@greenfieldcollege.edu",
    "20482": "kabir.singh@greenfieldcollege.edu",
}

# roll_number -> {"otp", "expires_at", "attempts"}
_pending_otps: dict[str, dict] = {}

# token -> {"kind": "student"|"guest", "roll_number", "email", "issued_at"}
# Guest sessions carry no roll number or email.
_sessions: dict[str, dict] = {}


class RequestOtpBody(BaseModel):
    roll_number: str


class VerifyOtpBody(BaseModel):
    roll_number: str
    otp: str


def _email_for(roll_number: str) -> str:
    """Every valid-format roll number resolves to an address.

    No existence check -- this is a demo, so any 5-digit number signs in.
    Swap this for a real student-records lookup that can return None.
    """
    return DUMMY_STUDENTS.get(roll_number, f"student{roll_number}@greenfieldcollege.edu")


def _mask_email(email: str) -> str:
    """aarav.sharma@x.edu -> aa**********@x.edu"""
    local, _, domain = email.partition("@")
    if len(local) <= 2:
        return f"{local[:1]}*@{domain}"
    return f"{local[:2]}{'*' * (len(local) - 2)}@{domain}"


@router.post("/auth/request-otp")
def request_otp(body: RequestOtpBody):
    roll_number = body.roll_number.strip()

    if not ROLL_NUMBER_RE.match(roll_number):
        raise HTTPException(
            status_code=400,
            detail="Please enter your 5 digit roll number (digits only).",
        )

    email = _email_for(roll_number)

    otp = f"{random.randint(0, 9999):04d}"
    _pending_otps[roll_number] = {
        "otp": otp,
        "expires_at": time.time() + OTP_TTL_SECONDS,
        "attempts": 0,
    }

    print(
        f"[dummy-auth] OTP for roll number {roll_number} ({email}): {otp} "
        f"-- expires in {OTP_TTL_SECONDS // 60} minutes. "
        "No email was actually sent."
    )

    return {
        "message": f"A 4 digit OTP was sent to {_mask_email(email)}.",
        "masked_email": _mask_email(email),
        "expires_in_seconds": OTP_TTL_SECONDS,
        # DEMO ONLY -- a real API must never return the OTP to the caller.
        # It's here so the flow is clickable without a mail server.
        "demo_otp": otp,
    }


@router.post("/auth/verify-otp")
def verify_otp(body: VerifyOtpBody):
    roll_number = body.roll_number.strip()
    otp = body.otp.strip()

    if not ROLL_NUMBER_RE.match(roll_number):
        raise HTTPException(
            status_code=400,
            detail="Please enter your 5 digit roll number (digits only).",
        )
    if not OTP_RE.match(otp):
        raise HTTPException(
            status_code=400,
            detail="Please enter the 4 digit OTP (digits only).",
        )

    pending = _pending_otps.get(roll_number)
    if pending is None:
        raise HTTPException(
            status_code=400,
            detail="No OTP was requested for this roll number. Please request one first.",
        )

    if time.time() > pending["expires_at"]:
        del _pending_otps[roll_number]
        raise HTTPException(
            status_code=400, detail="That OTP has expired. Please request a new one."
        )

    if pending["attempts"] >= MAX_VERIFY_ATTEMPTS:
        del _pending_otps[roll_number]
        raise HTTPException(
            status_code=429,
            detail="Too many incorrect attempts. Please request a new OTP.",
        )

    # Constant-time compare so a timing side channel can't leak the OTP
    # digit by digit. (Belt and braces for a 4-digit code, but it's the
    # habit worth keeping in the real version.)
    if not secrets.compare_digest(otp, pending["otp"]):
        pending["attempts"] += 1
        remaining = MAX_VERIFY_ATTEMPTS - pending["attempts"]
        raise HTTPException(
            status_code=401,
            detail=f"Incorrect OTP. {remaining} attempt(s) remaining.",
        )

    del _pending_otps[roll_number]

    email = _email_for(roll_number)
    token = secrets.token_urlsafe(24)
    _sessions[token] = {
        "kind": "student",
        "roll_number": roll_number,
        "email": email,
        "issued_at": time.time(),
    }

    print(f"[dummy-auth] Roll number {roll_number} verified; session issued.")

    return {
        "message": "Verified.",
        "session_token": token,
        "kind": "student",
        "roll_number": roll_number,
        "masked_email": _mask_email(email),
    }


@router.post("/auth/guest")
def guest_session():
    """Sign in without a roll number.

    No identity is collected, so there's nothing to verify -- the token just
    marks the visitor as a guest. The chatbot answers from the same public
    knowledge base either way; `kind` is here so a future version can gate
    student-specific lookups (fee dues, grades) behind kind == "student".
    """
    token = secrets.token_urlsafe(24)
    _sessions[token] = {
        "kind": "guest",
        "roll_number": None,
        "email": None,
        "issued_at": time.time(),
    }

    print("[dummy-auth] Guest session issued.")

    return {
        "message": "Signed in as a guest.",
        "session_token": token,
        "kind": "guest",
        "roll_number": None,
        "masked_email": None,
    }


def _bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    return token.strip() if scheme.lower() == "bearer" else None


@router.get("/auth/session")
def current_session(authorization: str | None = Header(default=None)):
    """Is this token still good?

    The widget keeps its session in sessionStorage, which survives page
    reloads -- but sessions here live in process memory, so a server restart
    invalidates the token while the browser still has it. The widget calls
    this on load so it doesn't show a signed-in UI backed by a dead token.
    """
    session = get_session(_bearer_token(authorization))
    if session is None:
        raise HTTPException(status_code=401, detail="Not signed in.")
    email = session.get("email")
    return {
        "kind": session.get("kind", "student"),
        "roll_number": session.get("roll_number"),
        # Guests have no email to mask.
        "masked_email": _mask_email(email) if email else None,
    }


@router.post("/auth/logout")
def logout(authorization: str | None = Header(default=None)):
    """Drop the session server-side. Safe to call with an unknown token."""
    token = _bearer_token(authorization)
    if token:
        _sessions.pop(token, None)
    return {"message": "Signed out."}


def get_session(token: str | None) -> dict | None:
    """Look up a session by token. Returns None if unknown.

    Nothing calls this yet -- /api/chat is intentionally left open so the
    demo gate doesn't break existing scripts and curl tests. To actually
    enforce sign-in, add a dependency to the chat route that reads the
    Authorization header and 401s when this returns None, and give sessions
    a real expiry.
    """
    if not token:
        return None
    return _sessions.get(token)
