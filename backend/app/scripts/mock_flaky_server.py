"""
Mock flaky HTTP server, for manually testing the alerting flow end-to-end.

Not part of the real application — run it standalone, on its own port, and
point a test Monitor's URL at it. It alternates between 200 (up) and 500
(down) every N requests, so you get a real, predictable UP<->DOWN
transition — the exact trigger alert_tasks.py's send_email_alert /
send_recovery_alert are meant to fire on (Postman Echo's /status/500 is
static, so it never actually transitions, it's just always down).

Run it with:
    uv run uvicorn backend.app.scripts.mock_flaky_server:app --port 8001 --reload

Then set a Monitor's URL to:
    http://host.docker.internal:8001/flaky
(host.docker.internal, not localhost — the celery worker runs inside
Docker, so "localhost" from its point of view is the container itself,
not your machine.)
"""

from fastapi import FastAPI, Response

app = FastAPI()

REQUESTS_PER_PHASE = 3  # how many requests "up" and "down" each last
_request_count = 0


@app.get("/flaky")
def flaky():
    global _request_count
    _request_count += 1

    # Every REQUESTS_PER_PHASE requests, flip between an "up" phase and a
    # "down" phase. E.g. with REQUESTS_PER_PHASE=3: requests 1-3 -> up,
    # 4-6 -> down, 7-9 -> up, ...
    phase = (_request_count - 1) // REQUESTS_PER_PHASE
    is_up_phase = phase % 2 == 0

    if is_up_phase:
        return {"status": "ok", "request_count": _request_count}
    return Response(status_code=500, content="Simulated failure")
