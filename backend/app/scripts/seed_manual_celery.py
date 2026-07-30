import uuid
from datetime import datetime, timezone

from backend.app.core.logger_setup import setup_logging
from backend.app.db.database import Base, SessionLocal
from backend.app.models.monitor import Monitor, MonitorStatus
from backend.app.models.ping_history import PingHistory
from backend.app.models.user import User, UserRole
from backend.app.models.workspace import Workspace, WorkspaceUser

logger = setup_logging()


def run_celery_seed():
    db = SessionLocal()
    Base.metadata.create_all(bind=db.get_bind())

    try:
        print("Starting seeding for Celery & Redis testing...")

        existing_user = (
            db.query(User).filter_by(email="celery_tester@pulsecheck.com").first()
        )

        if existing_user:
            print("Tables already seeded. Skipping seeding process.")
            return

        # create user
        user_id = uuid.uuid4()
        test_user = User(
            id=user_id,
            email="celery_tester@pulsecheck.com",
            hashed_password="mock_password_hash",
            role=UserRole.admin,
            is_active=True,
        )
        db.add(test_user)

        # create workspace
        workspace_id = uuid.uuid4()
        test_ws = Workspace(id=workspace_id, name="Celery Test Lab")
        db.add(test_ws)

        db.commit()  # Save to have valid IDs

        # create user-workspace link
        ws_user = WorkspaceUser(
            user_id=user_id, workspace_id=workspace_id, role=UserRole.admin
        )
        db.add(ws_user)

        # create postman-echo monitors with different behaviors
        monitors = [
            # 🟢 Scenario 1: Stable UP (Testing "State unchanged (up)")
            # Always returns HTTP 200 OK.
            Monitor(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                name="[ECHO] Site Stable - 200 OK",
                url="https://postman-echo.com/get",
                status=MonitorStatus.up,
                interval_minutes=1,
            ),
            # 🔴 Scenario 2: Sudden Downtime (Testing "Website WENT DOWN - Queueing alert")
            # Always returns HTTP 500. Initially set as 'up' to force the transition
            # and see how `send_email_alert` is queued.
            Monitor(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                name="[ECHO] Site with Error - 500",
                url="https://postman-echo.com/status/500",
                status=MonitorStatus.up,
                interval_minutes=1,
            ),
            # 🟡 Scenario 3: Client Error (Testing status codes 400+)
            # Returns HTTP 404. Since your code says `status_code < 400` means UP,
            # this 404 will be considered DOWN.
            Monitor(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                name="[ECHO] Site Not Found - 404",
                url="https://postman-echo.com/status/404",
                status=MonitorStatus.up,
                interval_minutes=1,
            ),
            # ⏳ Scenario 4: Network Timeout (Testing the `except httpx.RequestError` block)
            # Postman Echo /delay/10 keeps the connection open for 10 seconds.
            # Since `httpx.get` has `timeout=10.0`, this request will fail (status_code = 0).
            Monitor(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                name="[ECHO] Site Slow - Timeout",
                url="https://postman-echo.com/delay/10",
                status=MonitorStatus.up,
                interval_minutes=1,
            ),
            # 🔄 Scenario 5: Modulo and Different Interval (Testing interval_minutes = 3)
            # This monitor will be queried only at minutes divisible by 3 (e.g., :00, :03, :06).
            Monitor(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                name="[ECHO] Site Intermittent (3 min)",
                url="https://postman-echo.com/status/200",
                status=MonitorStatus.up,
                interval_minutes=3,
            ),
            # ⏸️ Scenario 6: Paused Monitor (Testing the exclusion from schedule_active_monitors)
            # The beat should totally ignore it, so you won't see ping logs for it.
            Monitor(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                name="[ECHO] Site Ignored - Paused",
                url="https://postman-echo.com/get",
                status=MonitorStatus.paused,
                interval_minutes=1,
            ),
            # 🚑 Scenario 7: Recovery (Testing "Website RECOVERED" and `send_recovery_alert`)
            # Returns 200 OK, but we tell the database it was DOWN.
            # On the first run, the system will detect it has recovered (DOWN -> UP).
            Monitor(
                id=uuid.uuid4(),
                workspace_id=workspace_id,
                name="[ECHO] Site Recovered - 200 OK",
                url="https://postman-echo.com/status/200",
                status=MonitorStatus.down,
                interval_minutes=1,
            ),
        ]

        db.add_all(monitors)
        db.commit()

        print("Seeding successful.")
        print(f"Added {len(monitors)} monitors with different behaviors.")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_celery_seed()
