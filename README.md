# Flow Manager API

A generic flow execution engine for sequential task processing with conditional routing.

## Features

- ✅ Generic flow execution engine
- ✅ Conditional task routing based on outcomes
- ✅ RESTful API with FastAPI
- ✅ Task registry for dynamic task registration
- ✅ Execution tracking and status monitoring


## Project Structure

```
flow-manager-app/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py        # Dependency injection
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── flows.py           # Flow management endpoints
│   ├── core/
│   │   ├── config.py              # Application settings
│   │   └── logging.py             # Logging configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── flow.py                # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── flow_engine.py         # Flow execution engine
│       ├── task_registry.py       # Task registration
│       └── tasks.py               # Task implementations
├── tests/
│   └── test_*.py
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```


## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   make install
   ```

2. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

3. **Run the application:**
   ```bash
   make run
   ```

4. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker

1. **Build and run:**
   ```bash
   make docker-build
   make docker-run
   ```

2. **View logs:**
   ```bash
   make docker-logs
   ```

3. **Stop container:**
   ```bash
   make docker-stop
   ```

## API Endpoints

### Health Check
- `GET /health` - Check API health status

### Flow Management
- `POST /api/v1/flows/register` - Register a new flow
- `POST /api/v1/flows/{flow_id}/execute` - Execute a flow
- `GET /api/v1/flows/execution/{execution_id}` - Get execution status
- `GET /api/v1/flows` - List all flows

## Usage Examples

### 1. Execute Default Flow

```bash
curl -X POST http://localhost:8000/api/v1/flows/flow123/execute
```

Response:
```json
{
  "message": "Flow execution completed",
  "execution_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": {
    "execution_id": "550e8400-e29b-41d4-a716-446655440000",
    "flow_id": "flow123",
    "status": "completed",
    "completed_tasks": ["task1", "task2", "task3"],
    "message": "Flow completed. Executed 3 tasks."
  }
}
```

### 2. Register a New Flow

```bash
curl -X POST http://localhost:8000/api/v1/flows/register \
  -H "Content-Type: application/json" \
  -d @flow_definition.json
```

### 3. Check Execution Status

```bash
curl http://localhost:8000/api/v1/flows/execution/{execution_id}
```

### 4. List All Flows

```bash
curl http://localhost:8000/api/v1/flows
```

## Flow Definition Format

```json
{
  "flow": {
    "id": "flow123",
    "name": "Data processing flow",
    "start_task": "task1",
    "tasks": [
      {
        "name": "task1",
        "description": "Fetch data"
      },
      {
        "name": "task2",
        "description": "Process data"
      },
      {
        "name": "task3",
        "description": "Store data"
      }
    ],
    "conditions": [
      {
        "name": "condition_task1_result",
        "description": "Evaluate task1 result",
        "source_task": "task1",
        "outcome": "success",
        "target_task_success": "task2",
        "target_task_failure": "end"
      },
      {
        "name": "condition_task2_result",
        "description": "Evaluate task2 result",
        "source_task": "task2",
        "outcome": "success",
        "target_task_success": "task3",
        "target_task_failure": "end"
      }
    ]
  }
}
```

## How It Works

### Flow Execution Process

1. **Flow starts** at the `start_task`
2. **Task execution**: The current task is executed with access to previous task results
3. **Condition evaluation**: After each task, its condition is evaluated
4. **Routing**: Based on task outcome (success/failure), the condition determines the next task
5. **Flow completion**: Continues until reaching "end" or no more conditions

### Task Context

Tasks receive a context dictionary containing results from all previously executed tasks:

```python
def my_task(context: Dict) -> TaskResult:
    # Access previous task results
    previous_data = context.get("previous_task", {}).get("data")

    # Process and return result
    return TaskResult(
        status=TaskStatus.SUCCESS,
        data={"result": "processed"},
        message="Task completed"
    )
```

## Adding New Tasks

1. **Create task function** in `app/services/tasks.py`:
   ```python
   def my_new_task(context: Dict) -> TaskResult:
       # Your task logic here
       return TaskResult(
           status=TaskStatus.SUCCESS,
           data={"my": "data"},
           message="Success"
       )
   ```

2. **Register task** in `app/api/dependencies.py`:
   ```python
   task_registry.register("my_new_task", my_new_task)
   ```

3. **Use in flow definition**:
   ```json
   {
     "name": "my_new_task",
     "description": "My custom task"
   }
   ```

## Testing

Run tests:
```bash
make test
```

## Development

Format code:
```bash
make format
```

Lint code:
```bash
make lint
```

## License

MIT License
