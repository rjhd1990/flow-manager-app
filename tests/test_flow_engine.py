"""Flow engine tests"""

import pytest

from app.models import FlowDefinition, TaskResult, TaskStatus
from app.services.flow_engine import FlowEngine
from app.services.task_registry import TaskRegistry


def test_flow_engine_initialization():
    """Test flow engine initialization"""
    registry = TaskRegistry()
    engine = FlowEngine(registry)

    assert engine.task_registry == registry
    assert len(engine.flow_definitions) == 0
    assert len(engine.executions) == 0


def test_flow_engine_register_flow(sample_flow_definition):
    """Test registering a flow in the engine"""
    registry = TaskRegistry()

    # Register tasks
    def task1(ctx):
        return TaskResult(status=TaskStatus.SUCCESS, data={"test": "data"})

    registry.register("task1", task1)
    registry.register("task2", task1)
    registry.register("task3", task1)

    engine = FlowEngine(registry)
    flow_def = FlowDefinition(**sample_flow_definition)

    engine.register_flow(flow_def)

    assert "test_flow_001" in engine.flow_definitions
    assert engine.flow_definitions["test_flow_001"].name == "Test Flow"


def test_flow_engine_validate_invalid_start_task():
    """Test flow validation with invalid start task"""
    registry = TaskRegistry()
    engine = FlowEngine(registry)

    invalid_flow = {
        "flow": {
            "id": "invalid",
            "name": "Invalid",
            "start_task": "nonexistent",
            "tasks": [{"name": "task1", "description": "Task 1"}],
            "conditions": [],
        }
    }

    flow_def = FlowDefinition(**invalid_flow)

    with pytest.raises(ValueError, match="Start task .* not found"):
        engine.register_flow(flow_def)


def test_flow_engine_list_flows(sample_flow_definition):
    """Test listing flows from engine"""
    registry = TaskRegistry()

    def dummy_task(ctx):
        return TaskResult(status=TaskStatus.SUCCESS)

    registry.register("task1", dummy_task)
    registry.register("task2", dummy_task)
    registry.register("task3", dummy_task)

    engine = FlowEngine(registry)
    flow_def = FlowDefinition(**sample_flow_definition)
    engine.register_flow(flow_def)

    flows = engine.list_flows()

    assert len(flows) == 1
    assert flows[0]["id"] == "test_flow_001"
    assert flows[0]["task_count"] == 3
    assert flows[0]["condition_count"] == 2
