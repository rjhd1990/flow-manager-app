"""Execution status retrieval tests"""

import pytest
from fastapi.testclient import TestClient


def test_get_execution_status(client: TestClient):
    """Test retrieving execution status"""
    # Execute flow
    exec_response = client.post("/api/v1/flows/flow123/execute")

    # Debug: print response if there's an issue
    assert exec_response.status_code == 200, f"Execute failed: {exec_response.text}"

    response_data = exec_response.json()

    # Verify execution_id exists in response
    assert (
        "execution_id" in response_data
    ), f"Missing execution_id in response: {response_data}"

    execution_id = response_data["execution_id"]

    # Get status
    status_response = client.get(f"/api/v1/flows/execution/{execution_id}")

    assert (
        status_response.status_code == 200
    ), f"Get status failed: {status_response.text}"
    data = status_response.json()

    assert data["execution_id"] == execution_id
    assert data["flow_id"] == "flow123"
    assert data["status"] == "completed"


def test_get_execution_status_structure(client: TestClient):
    """Test execution status response structure"""
    # Execute flow
    exec_response = client.post("/api/v1/flows/flow123/execute")
    assert exec_response.status_code == 200

    execution_id = exec_response.json()["execution_id"]

    # Get status
    response = client.get(f"/api/v1/flows/execution/{execution_id}")
    assert response.status_code == 200

    data = response.json()

    required_fields = [
        "execution_id",
        "flow_id",
        "status",
        "current_task",
        "completed_tasks",
        "task_results",
        "started_at",
        "ended_at",
    ]

    for field in required_fields:
        assert field in data, f"Missing field: {field}"


def test_get_nonexistent_execution_status(client: TestClient):
    """Test getting status for nonexistent execution"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/flows/execution/{fake_id}")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_execution_status_has_timestamps(client: TestClient):
    """Test that execution status includes timestamps"""
    # Execute flow
    exec_response = client.post("/api/v1/flows/flow123/execute")
    assert exec_response.status_code == 200

    execution_id = exec_response.json()["execution_id"]

    # Get status
    response = client.get(f"/api/v1/flows/execution/{execution_id}")
    assert response.status_code == 200

    data = response.json()

    assert data["started_at"] is not None
    assert data["ended_at"] is not None
    assert isinstance(data["started_at"], str)
    assert isinstance(data["ended_at"], str)
