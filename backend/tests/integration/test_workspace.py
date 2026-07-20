"""
Integration tests for workspace routes.
"""

import pytest


@pytest.mark.integration
@pytest.mark.workspace
def test_get_user_workspace_empty(auth_client):
    response = auth_client.get("/workspaces")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
@pytest.mark.workspace
def test_get_user_workspace_success(auth_client, owned_workspace, member_workspace):
    response = auth_client.get("/workspaces")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    roles = [workspace_user["role"] for workspace_user in data]
    assert "Admin" in roles
    assert "Viewer" not in roles


@pytest.mark.integration
@pytest.mark.workspace
def test_get_workspace_by_id_success(auth_client, owned_workspace):
    response = auth_client.get(f"/workspaces/{owned_workspace.id}")
    assert response.status_code == 200
    assert response.json()["name"] == "My Workspace"


@pytest.mark.integration
@pytest.mark.workspace
def test_get_workspace_by_unauthorized_id(auth_client, unauthorized_workspace):
    response = auth_client.get(f"/workspaces/{unauthorized_workspace.id}")
    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this workspace."


@pytest.mark.integration
@pytest.mark.workspace
def test_get_workspace_members_success(
    auth_client, owned_workspace, other_user, db_session
):
    from backend.app.models.workspace import WorkspaceUser

    link = WorkspaceUser(
        user_id=other_user.id, workspace_id=owned_workspace.id, role="Viewer"
    )
    db_session.add(link)
    db_session.commit()

    response = auth_client.get(f"/workspaces/{owned_workspace.id}/members")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert "email" in data[0]


@pytest.mark.integration
@pytest.mark.workspace
def test_get_workspace_members_filter_by_role(
    auth_client, owned_workspace, other_user, db_session
):
    from backend.app.models.workspace import WorkspaceUser

    link = WorkspaceUser(
        user_id=other_user.id, workspace_id=owned_workspace.id, role="Viewer"
    )
    db_session.add(link)
    db_session.commit()

    response = auth_client.get(f"/workspaces/{owned_workspace.id}/members?role=Viewer")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["role"] == "Viewer"
    assert data[0]["email"] == other_user.email


@pytest.mark.integration
@pytest.mark.workspace
def test_get_workspace_members_pagination(
    auth_client, owned_workspace, other_user, db_session
):
    from backend.app.models.workspace import WorkspaceUser

    link = WorkspaceUser(
        user_id=other_user.id, workspace_id=owned_workspace.id, role="Viewer"
    )
    db_session.add(link)
    db_session.commit()

    response = auth_client.get(
        f"/workspaces/{owned_workspace.id}/members?limit=1&offset=1"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.integration
@pytest.mark.workspace
def test_get_members_unautohrized(auth_client, unauthorized_workspace):
    response = auth_client.get(f"/workspaces/{unauthorized_workspace.id}/members")
    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.workspace
def test_create_workspace(auth_client, db_session):
    payload = {"name": "New Workspace"}

    response = auth_client.post("/workspaces", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["message"] == "Workspace created successfully"
    assert data["workspace"]["name"] == payload["name"]
    assert "id" in data["workspace"]
    assert "created_at" in data["workspace"]

    import uuid

    from backend.app.models.workspace import Workspace

    created_workspace = db_session.get(Workspace, uuid.UUID(data["workspace"]["id"]))
    assert created_workspace is not None
    assert created_workspace.name == payload["name"]


@pytest.mark.integration
@pytest.mark.workspace
def test_create_workspace_empty_body(auth_client):
    response = auth_client.post("/workspaces", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "name"]
    assert data["detail"][0]["type"] == "missing"


@pytest.mark.integration
@pytest.mark.workspace
def test_create_workspace_unauthorized(client):
    response = client.post(
        "/workspaces", json={"name": "Unauthorized Workspace Creation"}
    )
    assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.workspace
def test_create_workspace_db_error_triggers_rollback(auth_client, db_session):
    from unittest.mock import patch

    payload = {"name": "Error Workspace"}

    with patch("sqlalchemy.orm.Session.commit", side_effect=Exception("Database down")):
        response = auth_client.post("/workspaces", json=payload)

    assert response.status_code == 500

    from backend.app.models.workspace import Workspace

    workspaces = (
        db_session.query(Workspace).filter(Workspace.name == "Error Workspace").all()
    )
    assert len(workspaces) == 0


@pytest.mark.integration
@pytest.mark.workspace
def test_add_member_to_workspace_success(auth_client, owned_workspace, other_user):
    payload = {"id": str(other_user.id), "role": "Viewer"}
    response = auth_client.post(
        f"/workspaces/{owned_workspace.id}/members", json=payload
    )
    print(response.json())

    assert response.status_code == 201
    assert response.json()["message"] == "Member successfully added."


@pytest.mark.integration
@pytest.mark.workspace
def test_add_member_unauthorized(auth_client, unauthorized_workspace, other_user):
    payload = {"id": str(other_user.id), "role": "Viewer"}

    response = auth_client.post(
        f"/workspaces/{unauthorized_workspace.id}/members", json=payload
    )

    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.workspace
def test_edit_workspace_name_success(auth_client, owned_workspace):
    payload = {"name": "Nume Nou Workspace"}
    response = auth_client.patch(f"/workspaces/{owned_workspace.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Nume Nou Workspace"


@pytest.mark.integration
@pytest.mark.workspace
def test_delete_workspace_success(auth_client, owned_workspace, db_session):
    response = auth_client.delete(f"/workspaces/{owned_workspace.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Workspace successfully deleted."

    from backend.app.models.workspace import Workspace

    deleted_workspace = db_session.get(Workspace, owned_workspace.id)
    assert deleted_workspace is None


@pytest.mark.integration
@pytest.mark.workspace
def test_remove_member_success(auth_client, owned_workspace, other_user, db_session):
    from backend.app.models.workspace import WorkspaceUser

    link = WorkspaceUser(
        user_id=other_user.id, workspace_id=owned_workspace.id, role="Viewer"
    )
    db_session.add(link)
    db_session.commit()

    response = auth_client.delete(f"/workspaces/{owned_workspace.id}/{other_user.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Member successfully removed from workspace."


@pytest.mark.integration
@pytest.mark.workspace
def test_cannot_remove_admin(auth_client, owned_workspace, test_user):

    response = auth_client.delete(f"/workspaces/{owned_workspace.id}/{test_user.id}")

    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.workspace
def test_leave_workspace_success(client, member_workspace, other_user, db_session):

    client.post(
        "/login", json={"email": "other_user@example.com", "password": "Password1234!"}
    )

    response = client.delete(f"/workspaces/{member_workspace.id}/leave")
    assert response.status_code == 200
    assert response.json()["message"] == "You have successfully left the workspace."

    from backend.app.models.workspace import WorkspaceUser

    link = (
        db_session.query(WorkspaceUser)
        .filter_by(user_id=other_user.id, workspace_id=member_workspace.id)
        .first()
    )
    assert link is None


@pytest.mark.integration
@pytest.mark.workspace
def test_admin_cannot_leave_workspace(auth_client, owned_workspace):

    response = auth_client.delete(f"/workspaces/{owned_workspace.id}/leave")
    print(response.json())
    assert response.status_code == 403
