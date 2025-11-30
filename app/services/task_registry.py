from typing import Callable, Dict


class TaskRegistry:
    """Registry to store and retrieve task implementations"""

    def __init__(self):
        self._tasks: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        """Register a task implementation"""
        self._tasks[name] = func

    def get(self, name: str) -> Callable:
        """Get a task implementation"""
        if name not in self._tasks:
            raise ValueError(f"Task '{name}' not found in registry")
        return self._tasks[name]

    def exists(self, name: str) -> bool:
        """Check if task exists"""
        return name in self._tasks

    def list_tasks(self) -> list:
        """List all registered task names"""
        return list(self._tasks.keys())
