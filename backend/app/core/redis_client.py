"""
Shared Redis client for caching purposes. Separate from Celery's own internal Redis usage as a task broker.
"""

import os

import redis

REDIS_URL = os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0")

# decode_responses=True: makes get/set work with plain Python str instead
# of bytes, so callers don't have to .decode()/.encode() everywhere.
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
