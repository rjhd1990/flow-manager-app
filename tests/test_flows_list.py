"""Flow listing tests"""

import pytest
from fastapi.testclient import TestClient


def test_list_flows_empty(client: TestClient):
    """Test listing flows when none are registered (except default)"""
    response = client.get("/api/v1/flows")
    assert response.status_code == 200

    data = response.json()
    assert "flows" in data
    assert "count" in data
    assert isinstance(data["flows"], list)
    assert data["count"] >= 1  # At least the default flow


def test_list_flows_structure(client: TestClient):
    """Test flow list response structure"""
    response = client.get("/api/v1/flows")
    data = response.json()

    assert "flows" in data
    assert "count" in data

    if data["count"] > 0:
        flow = data["flows"][0]
        assert "id" in flow
        assert "name" in flow
        assert "start_task" in flow
        assert "task_count" in flow
        assert "condition_count" in flow


def test_list_flows_contains_default(client: TestClient):
    """Test that default flow is present"""
    response = client.get("/api/v1/flows")
    data = response.json()

    flow_ids = [flow["id"] for flow in data["flows"]]
    assert "flow123" in flow_ids
