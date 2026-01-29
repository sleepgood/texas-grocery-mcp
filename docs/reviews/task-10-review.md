# Code Review: Task 10 - Logging Infrastructure

**Date**: 2026-01-29
**Reviewer**: code-review agent
**Status**: CHANGES REQUESTED

## Files Reviewed

| File | Lines Changed | Status |
|------|---------------|--------|
| `src/texas_grocery_mcp/observability/__init__.py` | +6 (new) | OK |
| `src/texas_grocery_mcp/observability/logging.py` | +73 (new) | Issues Found |
| `tests/unit/test_logging.py` | +61 (new) | OK |
| `src/texas_grocery_mcp/server.py` | +2 | OK |

## Summary

The logging infrastructure implementation is well-structured and follows good practices for structured logging with JSON output. The code is clean and the tests verify core functionality. However, there are **critical type annotation issues** that violate the project's strict mypy configuration, and one minor linting issue. Additionally, there's an **inconsistency in logger creation patterns** across the codebase that should be addressed.

---

## Issues Found

### Must-Fix Issues

These must be addressed before approval.

#### Issue 1: Type Annotation Incompatibility in Processor List
**File**: `src/texas_grocery_mcp/observability/logging.py`
**Line(s)**: 35
**Severity**: Must-Fix (blocks mypy strict mode)

**Problem**:
The `add_timestamp` function has a type signature that's incompatible with structlog's `Processor` type. This causes a mypy strict mode error.

**Current Code**:
```python
# Line 13-20
def add_timestamp(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add ISO timestamp to log entry."""
    from datetime import datetime, timezone

    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_dict

# Line 32-38
shared_processors: list[Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    add_timestamp,  # <-- Type error here
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]
```

**Error Message**:
```
src/texas_grocery_mcp/observability/logging.py:35: error: List item 2 has incompatible type 
"Callable[[Logger, str, dict[str, Any]], dict[str, Any]]"; 
expected "Callable[[Any, str, MutableMapping[str, Any]], Mapping[str, Any] | str | bytes | bytearray | tuple[Any, ...]]"
```

**Recommendation**:
Change the function signature to match structlog's expected processor interface. Use `Any` for the logger parameter and `MutableMapping` for the event_dict:

```python
from collections.abc import MutableMapping

def add_timestamp(
    logger: Any, method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Add ISO timestamp to log entry."""
    from datetime import datetime, timezone

    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_dict
```

Alternatively, cast the processor list or suppress the type check for that specific line, but fixing the signature is cleaner.

---

#### Issue 2: No-Any-Return Violation in get_logger
**File**: `src/texas_grocery_mcp/observability/logging.py`
**Line(s)**: 70-72
**Severity**: Must-Fix (blocks mypy strict mode)

**Problem**:
The function is declared to return `structlog.stdlib.BoundLogger`, but mypy detects that `structlog.get_logger()` returns `Any`, violating strict mode.

**Current Code**:
```python
# Line 70-72
def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
```

**Error Message**:
```
src/texas_grocery_mcp/observability/logging.py:72: error: Returning Any from function 
declared to return "BoundLogger"  [no-any-return]
```

**Recommendation**:
Cast the return value to the correct type:

```python
def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)  # type: ignore[no-any-return]
```

Or use a type cast:

```python
from typing import cast

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))
```

The `type: ignore` comment is cleaner and more idiomatic for this case where structlog's typing isn't fully refined.

---

#### Issue 3: Deprecated timezone.utc Usage
**File**: `src/texas_grocery_mcp/observability/logging.py`
**Line(s)**: 19
**Severity**: Must-Fix (linting failure)

**Problem**:
Using `timezone.utc` when Python 3.11+ provides `datetime.UTC` as the preferred alias.

**Current Code**:
```python
# Line 17-19
from datetime import datetime, timezone

event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
```

**Recommendation**:
Use the modern `UTC` alias:

```python
from datetime import UTC, datetime

event_dict["timestamp"] = datetime.now(UTC).isoformat()
```

This is automatically fixable with `ruff check --fix`.

---

### Nice-to-Have Improvements

These are suggestions, not blockers.

#### Suggestion 1: Logger Name Parameter Pattern Inconsistency
**File**: Multiple files
**Line(s)**: Various
**Category**: Convention / Consistency

**Current**:
The new `get_logger()` function accepts a `name` parameter, which is excellent. However, existing code uses `structlog.get_logger()` without a name parameter:

```python
# In circuit_breaker.py, retry.py, session.py, graphql.py:
logger = structlog.get_logger()

# New pattern in logging.py:
def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
```

**Suggested**:
Update existing modules to use the new `get_logger()` function with module names for better log traceability:

```python
from texas_grocery_mcp.observability.logging import get_logger

logger = get_logger(__name__)
```

**Rationale**:
- Better log traceability by identifying which module emitted the log
- Consistent pattern across the codebase
- Uses the centralized logging configuration
- Follows Python logging best practices

This is not a blocker for Task 10, but should be noted for future cleanup or as part of Task 11 (Metrics).

---

#### Suggestion 2: Test Coverage for Log Levels
**File**: `tests/unit/test_logging.py`
**Line(s)**: N/A
**Category**: Test Coverage

**Current**:
Tests verify JSON output and timestamp inclusion, but don't test that the log level configuration actually works.

**Suggested**:
Add a test that verifies log levels are respected:

```python
def test_logger_respects_level():
    """Logger should respect configured log level."""
    from texas_grocery_mcp.observability.logging import configure_logging, get_logger
    
    captured = StringIO()
    original_stderr = sys.stderr
    
    try:
        sys.stderr = captured
        configure_logging(log_level="ERROR")
        logger = get_logger("test")
        
        logger.debug("debug message")
        logger.info("info message")
        logger.error("error message")
        
        sys.stderr.flush()
        output = captured.getvalue()
        
        # Only ERROR should appear
        assert "error message" in output
        assert "info message" not in output
        assert "debug message" not in output
    finally:
        sys.stderr = original_stderr
```

**Rationale**:
Ensures that the log level configuration from settings is actually applied correctly.

---

#### Suggestion 3: Consider Using __name__ as Default Logger Name
**File**: `src/texas_grocery_mcp/observability/logging.py`
**Line(s)**: 70-72
**Category**: API Design

**Current**:
`get_logger(name: str)` requires a name parameter.

**Suggested**:
Consider making the name optional with `__name__` as a sensible default when called directly:

```python
import inspect

def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name. If None, uses the calling module's __name__.
    """
    if name is None:
        # Get the caller's module name
        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get('__name__', 'unknown')
        else:
            name = 'unknown'
    return structlog.get_logger(name)
```

**Rationale**:
- Makes the API more convenient (though explicit is often better)
- This is a minor suggestion; the current explicit approach is perfectly fine

This is low priority and the current design is actually cleaner.

---

## What's Good

The logging implementation demonstrates several strong qualities:

- **Clean Architecture**: Well-organized observability module with clear separation of concerns
- **Proper JSON Logging**: Structured logs with JSON output to stderr (keeps stdout clean for MCP protocol)
- **ISO Timestamps**: Correctly uses UTC timestamps in ISO format for consistency
- **Shared Processors**: Smart use of shared processors for both structlog and stdlib logging
- **Configuration Integration**: Properly integrates with the Settings system for log level management
- **Good Documentation**: Clear docstrings explaining the purpose of each function
- **Test Coverage**: Tests verify the core functionality (JSON output and timestamp inclusion)
- **Early Initialization**: Logging is configured early in server.py before any other imports that might log
- **Type Annotations**: Attempts to use proper type hints (minor corrections needed for strict mode)

## Checklist Summary

| Category | Status |
|----------|--------|
| Code Quality | PASS |
| Patterns & Conventions | ISSUES (logger creation inconsistency - not blocking) |
| Potential Issues | PASS |
| Performance | PASS |
| Documentation | PASS |
| Basic Security | PASS |
| Type Safety | ISSUES (mypy strict mode violations - blocking) |
| Linting | ISSUES (ruff UP017 - blocking) |

---

## Additional Notes

### Structlog Configuration
The structlog configuration is solid:
- Properly configures both structlog and stdlib logging
- Uses `ProcessorFormatter` for consistent formatting
- Clears existing handlers to avoid duplicate logs
- Outputs to stderr (correct for MCP servers)

### Testing Strategy
The tests use proper stdout/stderr capture and restore, which is the right approach for testing logging output. The tests are simple and focused.

### Integration Point
The server.py integration is minimal and correct: `configure_logging()` is called once at module level before any other work.

---

## Next Steps

1. Fix the type annotation issues (Issues 1 & 2)
2. Update timezone.utc to datetime.UTC (Issue 3)
3. Run `mypy --strict` and `ruff check` to verify fixes
4. (Optional) Update existing modules to use the new get_logger() pattern
5. Re-run tests to ensure everything still passes
6. Proceed to security review
