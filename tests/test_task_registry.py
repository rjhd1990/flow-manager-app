"""Task registry tests"""

import pytest

from app.models import TaskResult, TaskStatus
from app.services.task_registry import TaskRegistry


def test_task_registry_register():
    """Test registering a task"""
    registry = TaskRegistry()

    def dummy_task(context):
        return TaskResult(status=TaskStatus.SUCCESS)

    registry.register("dummy", dummy_task)
    assert registry.exists("dummy")


def test_task_registry_get():
    """Test retrieving a registered task"""
    registry = TaskRegistry()

    def dummy_task(context):
        return TaskResult(status=TaskStatus.SUCCESS)

    registry.register("dummy", dummy_task)
    retrieved = registry.get("dummy")

    assert retrieved == dummy_task


def test_task_registry_get_nonexistent():
    """Test getting nonexistent task raises error"""
    registry = TaskRegistry()

    with pytest.raises(ValueError, match="not found in registry"):
        registry.get("nonexistent")


def test_task_registry_list_tasks():
    """Test listing all registered tasks"""
    registry = TaskRegistry()

    def task1(context):
        return TaskResult(status=TaskStatus.SUCCESS)

    def task2(context):
        return TaskResult(status=TaskStatus.SUCCESS)

    registry.register("task1", task1)
    registry.register("task2", task2)

    tasks = registry.list_tasks()
    assert len(tasks) == 2
    assert "task1" in tasks
    assert "task2" in tasks
