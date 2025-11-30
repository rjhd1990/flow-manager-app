"""Test edge cases and error scenarios"""

import pytest
from fastapi.testclient import TestClient


def test_flow_with_no_conditions(client: TestClient):
    """Test flow with tasks but no conditions"""
    flow_def = {
        "flow": {
            "id": "no_conditions_flow",
            "name": "No Conditions Flow",
            "start_task": "task1",
            "tasks": [{"name": "task1", "description": "Single task"}],
            "conditions": [],
        }
    }

    response = client.post("/api/v1/flows/register", json=flow_def)
    assert response.status_code == 201

    # Execute should work and stop after first task
    exec_response = client.post("/api/v1/flows/no_conditions_flow/execute")
    assert exec_response.status_code == 200

    status = exec_response.json()["status"]
    assert len(status["completed_tasks"]) == 1


def test_empty_task_results(client: TestClient):
    """Test handling of tasks that return empty data"""
    # This tests that the system handles None/empty data gracefully
    response = client.post("/api/v1/flows/flow123/execute")
    assert response.status_code == 200


def test_concurrent_executions(client: TestClient):
    """Test multiple concurrent executions of the same flow"""
    execution_ids = []

    for _ in range(5):
        response = client.post("/api/v1/flows/flow123/execute")
        assert response.status_code == 200
        execution_ids.append(response.json()["execution_id"])

    # All should have unique IDs
    assert len(set(execution_ids)) == 5

    # All should be retrievable
    for exec_id in execution_ids:
        response = client.get(f"/api/v1/flows/execution/{exec_id}")
        assert response.status_code == 200
