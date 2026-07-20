"""
Integration tests for the monitor module.
"""

import uuid

import pytest

from backend.app.models.monitor import Monitor, MonitorStatus


@pytest.mark.integration
@pytest.mark.monitor
def test_list_workspace_monitors(
    auth_client, owned_workspace, sample_monitor, db_session
):

    second_monitor: Monitor = Monitor(
        workspace_id=owned_workspace.id,
        name="Backend DB",
        url="postgres://...",
        interval_minutes=3,
        status=MonitorStatus.up.value,
    )
    db_session.add(second_monitor)
    db_session.commit()

    response = auth_client.get(f"/workspaces/{owned_workspace.id}/monitors")
    assert response.status_code == 200
    data = response.json()
    assert len(data["monitors"]) == 2

    # Test Status Filter
    res_status = auth_client.get(f"/workspaces/{owned_workspace.id}/monitors?status=up")
    assert len(res_status.json()["monitors"]) == 1
    assert res_status.json()["monitors"][0]["name"] == "Backend DB"

    # Test name Filter
    res_name = auth_client.get(f"/workspaces/{owned_workspace.id}/monitors?name=api")
    assert len(res_name.json()["monitors"]) == 1
    assert res_name.json()["monitors"][0]["name"] == "Test API Monitor"


@pytest.mark.integration
@pytest.mark.monitor
def test_get_monitor_by_id_success(auth_client, sample_monitor):
    response = auth_client.get(f"/monitors/{sample_monitor.id}")
    assert response.status_code == 200
    assert response.json()["name"] == sample_monitor.name


@pytest.mark.integration
@pytest.mark.monitor
def test_create_monitor_success(auth_client, owned_workspace):
    payload = {
        "name": "Production Frontend",
        "url": "https://myapp.com",
        "interval_minutes": 1,
    }
    response = auth_client.post(
        f"/workspaces/{owned_workspace.id}/monitors", json=payload
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["url"] == payload["url"]
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.integration
@pytest.mark.monitor
def test_create_monitor_unauthorized_workspace(auth_client, unauthorized_workspace):
    payload = {
        "name": "Hacked Monitor",
        "url": "https://hacker.com",
        "interval_minutes": 5,
    }
    response = auth_client.post(
        f"/workspaces/{unauthorized_workspace.id}/monitors", json=payload
    )
    assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.monitor
def test_get_monitor_by_id_unauthorized(auth_client, unauthorized_monitor):
    response = auth_client.get(f"/monitors/{unauthorized_monitor.id}")
    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.monitor
def test_update_monitor_success(auth_client, sample_monitor):
    payload = {"name": "Updated Name", "interval_minutes": 15}
    response = auth_client.patch(f"/monitors/{sample_monitor.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["interval_minutes"] == 15


@pytest.mark.integration
@pytest.mark.monitor
def test_update_monitor_status_permission_error(auth_client, sample_monitor):
    # Users can only set status to 'paused' or 'pending'
    payload = {"status": MonitorStatus.up.value}
    response = auth_client.patch(f"/monitors/{sample_monitor.id}", json=payload)
    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.monitor
def test_delete_monitor_success(auth_client, sample_monitor, db_session):
    response = auth_client.delete(f"/monitors/{sample_monitor.id}")
    assert response.status_code == 204

    # Verify it is deleted from the DB
    monitor_in_db = db_session.get(Monitor, sample_monitor.id)
    assert monitor_in_db is None


@pytest.mark.integration
@pytest.mark.monitor
def test_delete_monitor_unauthorized(auth_client, unauthorized_monitor, db_session):
    response = auth_client.delete(f"/monitors/{unauthorized_monitor.id}")
    assert response.status_code == 404

    # Verify it still exists in the DB
    monitor_in_db = db_session.get(Monitor, unauthorized_monitor.id)
    assert monitor_in_db is not None


@pytest.mark.integration
@pytest.mark.monitor
def test_bulk_delete_monitors(auth_client, owned_workspace, sample_monitor, db_session):
    second_monitor: Monitor = Monitor(
        workspace_id=owned_workspace.id,
        name="Another Monitor",
        url="https://another.com",
        interval_minutes=5,
    )
    db_session.add(second_monitor)
    db_session.commit()

    payload = {"monitor_ids": [str(sample_monitor.id), str(second_monitor.id)]}
    response = auth_client.post(
        f"/workspaces/{owned_workspace.id}/monitors/bulk-delete", json=payload
    )
    assert response.status_code == 204
    monitors_left = (
        db_session.query(Monitor).filter_by(workspace_id=owned_workspace.id).all()
    )
    assert len(monitors_left) == 0


@pytest.mark.integration
@pytest.mark.monitor
def test_delete_workspace_monitors(
    auth_client, owned_workspace, sample_monitor, db_session
):
    response = auth_client.delete(f"/workspaces/{owned_workspace.id}/monitors")
    assert response.status_code == 204

    monitors_left = (
        db_session.query(Monitor).filter_by(workspace_id=owned_workspace.id).all()
    )
    assert len(monitors_left) == 0


@pytest.mark.integration
@pytest.mark.monitor
@pytest.mark.viewer
def test_viewer_can_read_monitors(viewer_client, member_workspace, db_session):
    """Viewer User can see all workspace monitors."""

    monitor = Monitor(
        workspace_id=member_workspace.id,
        name="Shared Monitor",
        url="https://shared.example.com",
        interval_minutes=5,
        status=MonitorStatus.up.value,
    )
    db_session.add(monitor)
    db_session.commit()

    response = viewer_client.get(f"/workspaces/{member_workspace.id}/monitors")

    assert response.status_code == 200
    data = response.json()
    assert len(data["monitors"]) == 1
    assert data["monitors"][0]["name"] == "Shared Monitor"


# XXX: RBAC business logic is not decided yet
# VIEWER tests will fail at this point in time
@pytest.mark.integration
@pytest.mark.monitor
@pytest.mark.viewer
def test_viewer_cannot_create_monitor(viewer_client, member_workspace):
    """Viewer User should/should not have permissions to create montiros within the workspace."""
    payload = {
        "name": "Unauthorized Monitor",
        "url": "https://hacker.com",
        "interval_minutes": 5,
    }

    response = viewer_client.post(
        f"/workspaces/{member_workspace.id}/monitors", json=payload
    )

    # Correctly implemneted RBAC should return 403 Forbidden
    # Currently, our endpoint returns 201 Created
    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.monitor
@pytest.mark.viewer
def test_viewer_cannot_delete_monitor(viewer_client, member_workspace, db_session):
    """Viewer User shouldn not be allowed to delete monitors within workspace."""
    monitor = Monitor(
        workspace_id=member_workspace.id,
        name="Important Monitor",
        url="https://important.com",
        interval_minutes=5,
    )
    db_session.add(monitor)
    db_session.commit()

    response = viewer_client.delete(f"/monitors/{monitor.id}")

    assert response.status_code in [403, 404]

    monitor_in_db = db_session.get(Monitor, monitor.id)
    assert monitor_in_db is not None
