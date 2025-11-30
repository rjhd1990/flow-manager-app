from app.services import FlowEngine, TaskRegistry
from app.services.tasks import task1_fetch_data, task2_process_data, task3_store_data

# Global instances
task_registry = TaskRegistry()
flow_engine = FlowEngine(task_registry)

# Register default tasks
task_registry.register("task1", task1_fetch_data)
task_registry.register("task2", task2_process_data)
task_registry.register("task3", task3_store_data)


def get_flow_engine() -> FlowEngine:
    """Dependency to get flow engine instance"""
    return flow_engine


def get_task_registry() -> TaskRegistry:
    """Dependency to get task registry instance"""
    return task_registry
