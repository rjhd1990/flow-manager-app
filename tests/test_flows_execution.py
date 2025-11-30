"""Flow execution tests"""

import pytest
from fastapi.testclient import TestClient


def test_execute_default_flow(client: TestClient):
    """Test executing the default flow"""
    response = client.post("/api/v1/flows/flow123/execute")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "execution_id" in data
    assert "status" in data
    assert data["message"] == "Flow execution completed"


def test_execute_flow_status_structure(client: TestClient):
    """Test execution response contains correct status structure"""
    response = client.post("/api/v1/flows/flow123/execute")
    data = response.json()

    status = data["status"]
    assert "execution_id" in status
    assert "flow_id" in status
    assert "status" in status
    assert "current_task" in status
    assert "completed_tasks" in status
    assert "task_results" in status
    assert "started_at" in status


def test_execute_flow_completes_all_tasks(client: TestClient):
    """Test that flow execution completes all tasks"""
    response = client.post("/api/v1/flows/flow123/execute")
    data = response.json()

    completed_tasks = data["status"]["completed_tasks"]
    assert len(completed_tasks) == 3
    assert "task1" in completed_tasks
    assert "task2" in completed_tasks
    assert "task3" in completed_tasks


def test_execute_flow_task_results(client: TestClient):
    """Test that task results are captured"""
    response = client.post("/api/v1/flows/flow123/execute")
    data = response.json()

    task_results = data["status"]["task_results"]
    assert len(task_results) == 3

    # Check task1 result
    assert "task1" in task_results
    assert task_results["task1"]["status"] == "success"
    assert "data" in task_results["task1"]

    # Check task2 result
    assert "task2" in task_results
    assert task_results["task2"]["status"] == "success"

    # Check task3 result
    assert "task3" in task_results
    assert task_results["task3"]["status"] == "success"


def test_execute_nonexistent_flow(client: TestClient):
    """Test executing a flow that doesn't exist"""
    response = client.post("/api/v1/flows/nonexistent_flow/execute")

    assert response.status_code == 400
    assert "detail" in response.json()


def test_execute_custom_flow(client: TestClient, sample_flow_definition):
    """Test executing a custom registered flow"""
    # Register flow
    client.post("/api/v1/flows/register", json=sample_flow_definition)

    # Execute flow
    response = client.post("/api/v1/flows/test_flow_001/execute")

    assert response.status_code == 200
    data = response.json()
    assert data["status"]["flow_id"] == "test_flow_001"


def test_execute_flow_returns_unique_execution_id(client: TestClient):
    """Test that each execution gets a unique ID"""
    response1 = client.post("/api/v1/flows/flow123/execute")
    response2 = client.post("/api/v1/flows/flow123/execute")

    exec_id_1 = response1.json()["execution_id"]
    exec_id_2 = response2.json()["execution_id"]

    assert exec_id_1 != exec_id_2
