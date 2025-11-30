# Flow Design

## Dependency Graph
```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────┐     ┌──────────────────┐
│  Task1  │────▶│  Condition1      │
│ (Fetch) │     │  Check: success? │
└─────────┘     └────┬────────┬────┘
                     │        │
              success│        │failure
                     │        │
                     ▼        ▼
                ┌─────────┐  END
                │  Task2  │
                │(Process)│
                └────┬────┘
                     │
                     ▼
                ┌──────────────────┐
                │  Condition2      │
                │  Check: success? │
                └────┬────────┬────┘
                     │        │
              success│        │failure
                     │        │
                     ▼        ▼
                ┌─────────┐  END
                │  Task3  │
                │ (Store) │
                └────┬────┘
                     │
                     ▼
                   END
```

### Dependency Rules

- Task1 has no dependencies (always executes first)
- Task2 depends on:
  - Task1 completing
  - Task1 returning SUCCESS status
  - Data from Task1 (optional, based on implementation)


- Task3 depends on:
  - Task1 and Task2 both completing
  - Both returning SUCCESS status
  - Data from Task2 (optional)

## Q1: How do the tasks depend on one another?

**Answer:**

Tasks have **two types of dependencies**:

### 1. **Execution Order Dependency (Conditional)**
- Tasks do NOT directly depend on each other
- Dependencies are defined through **conditions** in the flow configuration
- The Flow Engine uses conditions to determine which task executes next
- Tasks are **decoupled** - they don't know about other tasks

**Example:**
```
Task1 completes → Condition evaluates result → Routes to Task2 OR End
```

### 2. **Data Dependency (Optional)**
- Tasks share data through a **context object**
- Later tasks can access results from previous tasks
- This dependency is optional - tasks can be independent

**Example:**
```python
# Task2 accesses Task1's data
previous_data = context.get("task1", {}).get("data", {})
records = previous_data.get("records", [])
# Process records from Task1
```

**Key Point:** Tasks are independent units. The Flow Engine orchestrates their execution based on conditions, not hardcoded dependencies.

---

## Q2: How is the success or failure of a task evaluated?

**Answer:**

Success/failure is evaluated through a **three-step process**:

### Step 1: **Task Returns Explicit Status**
Each task returns a `TaskResult` object with an explicit status:

```python
# Success
return TaskResult(
    status=TaskStatus.SUCCESS,
    data={"result": "data"},
    message="Task completed"
)

# Failure
return TaskResult(
    status=TaskStatus.FAILURE,
    data=None,
    message="Error occurred"
)
```

### Step 2: **Condition Compares Status**
After task execution, a condition checks the status:

```json
{
  "source_task": "task1",
  "outcome": "success",              // Expected status
  "target_task_success": "task2",    // If matches
  "target_task_failure": "end"       // If doesn't match
}
```

### Step 3: **Engine Routes Based on Evaluation**
```python
if task_result.status == condition.outcome:  # "success" == "success"
    next_task = condition.target_task_success  # Go to task2
else:
    next_task = condition.target_task_failure  # Go to end
```

**Evaluation Mechanism:**
- Tasks use **try-catch** blocks to determine status
- If operation succeeds → return SUCCESS
- If exception occurs → return FAILURE
- Condition performs **exact string match** on status value

---

## Q3: What happens if a task fails or succeeds?

**Answer:**

### **If a Task SUCCEEDS:**

1. **Result is stored** in execution history
2. **Result is added** to shared context (accessible by later tasks)
3. **Task is marked** as completed
4. **Condition evaluates** the success status
5. **Flow routes** to `target_task_success` (next task)
6. **Execution continues** to the next task

**Example:**
```
Task1 [SUCCESS]
  ↓
Condition: "success" == "success" ✓
  ↓
Route to Task2
  ↓
Task2 executes
```

**Result:**
```json
{
  "status": "running",
  "completed_tasks": ["task1"],
  "task_results": {
    "task1": {"status": "success", "data": {...}}
  },
  "current_task": "task2"  // Proceeding
}
```

### **If a Task FAILS:**

1. **Result is stored** in execution history
2. **Result is added** to shared context
3. **Task is marked** as completed (but with failure status)
4. **Condition evaluates** the failure status
5. **Flow routes** to `target_task_failure` (usually "end")
6. **Execution STOPS immediately**
7. **All remaining tasks are SKIPPED** (never execute)
8. **Final status** set to `"completed_with_failures"`

**Example:**
```
Task1 [FAILURE]
  ↓
Condition: "failure" == "success" ✗
  ↓
Route to "end"
  ↓
Flow STOPS
  ↓
Task2 and Task3 NEVER execute
```

**Result:**
```json
{
  "status": "completed_with_failures",
  "completed_tasks": ["task1"],
  "task_results": {
    "task1": {
      "status": "failure",
      "message": "Database connection failed"
    }
  },
  "message": "Flow completed with failures. Failed tasks: task1"
}
```

**Key Differences:**

| Aspect | Success | Failure |
|--------|---------|---------|
| Next Task | Executes | Skipped |
| Flow Continues | Yes | No (stops) |
| Final Status | `"completed"` | `"completed_with_failures"` |
| Remaining Tasks | Execute | Never execute |
| Context | Available to next tasks | Preserved but flow ends |

**Summary:** Success continues the flow, failure stops it immediately to prevent processing bad data or wasting resources.
