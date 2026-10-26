# verification_service.py
"""
Email verification code service module.

Generates, stores and checks the 6-digit codes used for email account
validation. Codes expire on their own in a few minutes and have no value afterwards —
Redis's TTL handles that automatically, no cleanup job needed. Codes are
stored hashed (SHA-256), never in plaintext, same principle as passwords.
"""

import hashlib
import hmac
import secrets
import uuid

from backend.app.core.redis_client import redis_client

CODE_TTL_SECONDS = 900
MAX_ATTEMPTS = 5


def _code_key(user_id: uuid.UUID) -> str:
    return f"verification_code:{user_id}"


def _attempts_key(user_id: uuid.UUID) -> str:
    return f"verification_attempts:{user_id}"


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def generate_and_store_code(user_id: uuid.UUID) -> str:
    """Creates a new 6-digit code for a user, overwriting any previous one
    and resetting their failed-attempts counter. Returns the plaintext
    code — the only place it exists is this return value and the email
    we're about to put it in; Redis only ever sees the hash."""

    code = f"{secrets.randbelow(1_000_000):06d}"
    redis_client.set(_code_key(user_id), _hash_code(code), ex=CODE_TTL_SECONDS)
    redis_client.delete(_attempts_key(user_id))
    return code


def verify_code(user_id: uuid.UUID, submitted_code: str) -> bool:
    """Checks a submitted code against the stored one. Returns False for
    any failure case (no code / expired / wrong / too many attempts) —
    callers don't need to distinguish why, just that it didn't work."""
    stored_hash = redis_client.get(_code_key(user_id))
    if not stored_hash:
        return False  # expired, or never requested

    attempts = redis_client.incr(_attempts_key(user_id))
    if attempts == 1:
        redis_client.expire(_attempts_key(user_id), CODE_TTL_SECONDS)
    if attempts > MAX_ATTEMPTS:
        redis_client.delete(_code_key(user_id))  # lock out, force a resend
        return False
    if not hmac.compare_digest(_hash_code(submitted_code), stored_hash):
        return False

    redis_client.delete(_code_key(user_id), _attempts_key(user_id))
    return True
