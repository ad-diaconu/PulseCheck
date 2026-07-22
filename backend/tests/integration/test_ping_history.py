"""
Integartion tests for the ping history endpoint.
"""

import pytest


@pytest.mark.integration
@pytest.mark.ping_history
def test_get_pings_successfully(auth_client, sample_monitor, sample_ping_history):
    response = auth_client.get(f"/monitors/{sample_monitor.id}/pings")
    assert response.status_code == 200
    data = response.json()
    assert len(data["pings"]) == len(sample_ping_history)
    for ping in data["pings"]:
        print(ping)
        assert "status_code" in ping
        assert "latency_ms" in ping
        assert "pinged_at" in ping


@pytest.mark.integration
@pytest.mark.ping_history
def test_get_ping_history_with_pagination(
    auth_client, sample_monitor, sample_ping_history
):
    response = auth_client.get(f"/monitors/{sample_monitor.id}/pings?limit=1&skip=0")

    assert response.status_code == 200
    assert len(response.json()["pings"]) == 1


@pytest.mark.integration
@pytest.mark.ping_history
def test_get_pings_unauthorized(auth_client, unauthorized_monitor):
    response = auth_client.get(f"/monitors/{unauthorized_monitor.id}/pings")
    assert response.status_code == 404
