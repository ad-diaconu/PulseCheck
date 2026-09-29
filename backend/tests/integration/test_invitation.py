# test_invitation.py
"""
Integration tests for workspace invitation routes.
"""

import uuid

import pytest


@pytest.mark.integration
@pytest.mark.invitation
def test_create_invitation_success(auth_client, owned_workspace, other_user):
    response = auth_client.post(
        f"/workspaces/{owned_workspace.id}/invitations",
        json={"email": other_user.email, "role": "Viewer"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["workspace_id"] == str(owned_workspace.id)
    assert data["invited_user_id"] == str(other_user.id)
    assert data["status"] == "pending"


@pytest.mark.integration
@pytest.mark.invitation
def test_create_invitation_user_not_found(auth_client, owned_workspace):
    response = auth_client.post(
        f"/workspaces/{owned_workspace.id}/invitations",
        json={"email": "nobody@example.com", "role": "Viewer"},
    )

    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.invitation
def test_create_invitation_user_already_member(
    auth_client, member_workspace, other_user
):
    """other_user is already part of member_workspace as Viewer."""
    response = auth_client.post(
        f"/workspaces/{member_workspace.id}/invitations",
        json={"email": other_user.email, "role": "Viewer"},
    )

    assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.invitation
def test_create_invitation_duplicate_pending(
    auth_client, owned_workspace, other_user, pending_invitation
):
    """A pending invitation for other_user already exists in owned_workspace."""
    response = auth_client.post(
        f"/workspaces/{owned_workspace.id}/invitations",
        json={"email": other_user.email, "role": "Viewer"},
    )

    assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.invitation
def test_create_invitation_unauthorized(
    auth_client, unauthorized_workspace, other_user
):
    """test_user is not an admin of unauthorized_workspace."""
    response = auth_client.post(
        f"/workspaces/{unauthorized_workspace.id}/invitations",
        json={"email": other_user.email, "role": "Viewer"},
    )

    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.invitation
def test_get_my_pending_invitations_success(viewer_client, pending_invitation):
    """other_user (viewer_client) has one pending invitation."""
    response = viewer_client.get("/invitations")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(pending_invitation.id)
    assert data[0]["status"] == "pending"


@pytest.mark.integration
@pytest.mark.invitation
def test_get_my_pending_invitations_empty(auth_client):
    """test_user has no pending invitations."""
    response = auth_client.get("/invitations")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
@pytest.mark.invitation
def test_accept_invitation_success(viewer_client, pending_invitation, other_user):
    response = viewer_client.post(f"/invitations/{pending_invitation.id}/accept")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"

    # verify the workspace membership was actually created
    members_response = viewer_client.get(
        f"/workspaces/{pending_invitation.workspace_id}/members"
    )
    member_emails = [m["email"] for m in members_response.json()]
    assert other_user.email in member_emails


@pytest.mark.integration
@pytest.mark.invitation
def test_decline_invitation_success(viewer_client, pending_invitation):
    response = viewer_client.post(f"/invitations/{pending_invitation.id}/decline")

    assert response.status_code == 200
    assert response.json()["status"] == "declined"


@pytest.mark.integration
@pytest.mark.invitation
def test_respond_to_invitation_not_addressed_to_user(auth_client, pending_invitation):
    """test_user is the sender, not the recipient — cannot respond to it."""
    response = auth_client.post(f"/invitations/{pending_invitation.id}/accept")

    assert response.status_code == 403


@pytest.mark.integration
@pytest.mark.invitation
def test_respond_to_already_answered_invitation(viewer_client, pending_invitation):
    first_response = viewer_client.post(f"/invitations/{pending_invitation.id}/accept")
    assert first_response.status_code == 200

    second_response = viewer_client.post(
        f"/invitations/{pending_invitation.id}/decline"
    )
    assert second_response.status_code == 400


@pytest.mark.integration
@pytest.mark.invitation
def test_respond_to_nonexistent_invitation(viewer_client):
    fake_id = uuid.uuid4()
    response = viewer_client.post(f"/invitations/{fake_id}/accept")

    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.invitation
def test_create_invitation_unauthorized_no_login(client, owned_workspace, other_user):
    response = client.post(
        f"/workspaces/{owned_workspace.id}/invitations",
        json={"email": other_user.email, "role": "Viewer"},
    )

    assert response.status_code == 401
