"""
Integration tests for Celery tasks related to pinging websites and scheduling monitors.
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest
from freezegun import freeze_time

from backend.app.models.monitor import MonitorStatus
from backend.app.models.ping_history import PingHistory
from backend.app.tasks.ping_tasks import ping_website, schedule_active_monitors


class SafeSessionProxy:
    """
    Proxies calls to the test's db_session but disables the close()
    method. This allows Celery tasks to share the test transaction
    without accidentally closing it prematurely.
    """

    def __init__(self, session):
        self._session = session

    def __getattr__(self, name):
        if name == "close":
            return lambda: None  # Disable close() so it doesn't detach instances
        return getattr(self._session, name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.celery
@patch("backend.app.tasks.ping_tasks.SessionLocal")
@patch("backend.app.tasks.ping_tasks.ping_website.delay")
def test_schedule_active_monitors_time_simulation(
    mock_ping_delay, mock_session_local, db_session, monitor_1_min, monitor_5_min
):
    """
    Tests if the system successfully choose corresponding monitors by intervals.
    Use 'freeze_time' to mimick time for the shceduler.
    """
    mock_session_local.return_value = SafeSessionProxy(db_session)

    # minute 0 ( both monitors should be called )
    with freeze_time("2026-07-07 12:00:00"):
        schedule_active_monitors()
        assert mock_ping_delay.call_count == 2
        mock_ping_delay.reset_mock()  # reset counter

    # minute 1 ( only first monitor should be called )
    with freeze_time("2026-07-07 12:01:00"):
        schedule_active_monitors()
        assert mock_ping_delay.call_count == 1
        mock_ping_delay.assert_called_with(str(monitor_1_min.id), monitor_1_min.url)
        mock_ping_delay.reset_mock()

    # minute 5 ( both monitors should be called )
    with freeze_time("2026-07-07 12:05:00"):
        schedule_active_monitors()
        assert mock_ping_delay.call_count == 2
        mock_ping_delay.reset_mock()


@pytest.mark.celery
@patch("backend.app.tasks.ping_tasks.SessionLocal")
@patch("backend.app.tasks.ping_tasks.send_email_alert.delay")
@patch("backend.app.tasks.ping_tasks.httpx.get")
def test_ping_website_triggers_down_alert(
    mock_httpx_get, mock_email_alert, mock_session_local, db_session, monitor_1_min
):
    """
    Response from SITE is 500 ERROR.
    Initial state is UP. Servers goes DOWN.
    """
    mock_session_local.return_value = SafeSessionProxy(db_session)
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_httpx_get.return_value = mock_response

    # execute tasks without Celery
    ping_website(str(monitor_1_min.id), monitor_1_min.url)

    ping = db_session.query(PingHistory).filter_by(monitor_id=monitor_1_min.id).first()
    assert ping is not None
    assert ping.status_code == 500

    db_session.refresh(monitor_1_min)
    assert monitor_1_min.status == MonitorStatus.down.value

    mock_email_alert.assert_called_once_with(
        monitor_id=str(monitor_1_min.id), website_url=monitor_1_min.url, status_code=500
    )


@pytest.mark.celery
@patch("backend.app.tasks.ping_tasks.SessionLocal")
@patch("backend.app.tasks.ping_tasks.send_email_alert.delay")
@patch("backend.app.tasks.ping_tasks.httpx.get")
def test_ping_website_prevents_alert_spam(
    mock_httpx_get, mock_email_alert, mock_session_local, db_session, monitor_1_min
):
    """
    Timeout (0). Initial state is ALREADY DOWN.
    State remains DOWN, NO new alert is sent.
    """
    mock_session_local.return_value = SafeSessionProxy(db_session)
    monitor_1_min.status = MonitorStatus.down.value
    db_session.commit()

    mock_httpx_get.side_effect = httpx.RequestError("Timeout")

    ping_website(str(monitor_1_min.id), monitor_1_min.url)

    ping = db_session.query(PingHistory).filter_by(monitor_id=monitor_1_min.id).first()
    assert ping.status_code == 0

    mock_email_alert.assert_not_called()


@pytest.mark.celery
@patch("backend.app.tasks.ping_tasks.SessionLocal")
@patch("backend.app.tasks.ping_tasks.send_recovery_alert.delay")
@patch("backend.app.tasks.ping_tasks.httpx.get")
def test_ping_website_triggers_recovery_alert(
    mock_httpx_get, mock_recovery_alert, mock_session_local, db_session, monitor_1_min
):
    """
    Site is OK. Initial state is DOWN.
    State becomes UP, recovery alert is sent.
    """
    mock_session_local.return_value = SafeSessionProxy(db_session)
    monitor_1_min.status = MonitorStatus.down.value
    db_session.commit()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_httpx_get.return_value = mock_response

    ping_website(str(monitor_1_min.id), monitor_1_min.url)

    db_session.refresh(monitor_1_min)
    assert monitor_1_min.status == MonitorStatus.up.value

    mock_recovery_alert.assert_called_once_with(
        monitor_id=str(monitor_1_min.id), website_url=monitor_1_min.url
    )
