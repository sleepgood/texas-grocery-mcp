# Code Review: Task 11 - Health Check Endpoints

**Date**: 2026-01-29
**Reviewer**: code-review agent
**Status**: CHANGES REQUESTED

## Files Reviewed

| File | Lines | Status |
|------|-------|--------|
| `src/texas_grocery_mcp/models/health.py` | 41 | Issues Found |
| `src/texas_grocery_mcp/observability/health.py` | 76 | Issues Found |
| `tests/unit/test_health.py` | 24 | Issues Found |

## Summary

The implementation provides basic health check functionality with liveness and readiness probes. The code is generally readable and follows the codebase patterns. However, there are several important issues that need to be addressed:

1. **Critical**: Synchronous health check creating async client (architectural mismatch)
2. **Important**: Insufficient test coverage for a production health check system
3. **Important**: Missing error handling edge cases
4. **Minor**: Inconsistent patterns with circuit breaker status access

---

## Issues Found

### Must-Fix Issues

#### Issue 1: Synchronous Function Creating Async Client
**File**: `src/texas_grocery_mcp/observability/health.py`
**Line(s)**: 30-52
**Severity**: Must-Fix

**Problem**:
The `health_ready()` function is synchronous but creates an `HEBGraphQLClient()` instance, which is an async client. The client's `get_status()` method is called, but the client lifecycle (initialization and cleanup) is not properly managed. This creates an async client that is never properly closed, leading to resource leaks.

**Current Code**:
```python
# Line 30-43
try:
    from texas_grocery_mcp.clients.graphql import HEBGraphQLClient

    client = HEBGraphQLClient()
    cb_status = client.circuit_breaker.get_status()
    
    if cb_status["state"] == "open":
        components["graphql_api"] = ComponentHealth(
            status="down", message="Circuit breaker open"
        )
        overall_status = "degraded"
    else:
        components["graphql_api"] = ComponentHealth(status="up")
```

**Recommendation**:
Since we only need circuit breaker status (not actual API calls), and the circuit breaker is a synchronous object, we should either:

Option A: Make the health check async (recommended for consistency)
Option B: Access circuit breaker status without creating the full async client
Option C: Create a synchronous health check client wrapper

The cleanest approach is Option A, making the health endpoints async, which aligns with the rest of the codebase's async patterns.

---

#### Issue 2: Insufficient Test Coverage
**File**: `tests/unit/test_health.py`
**Line(s)**: Entire file
**Severity**: Must-Fix

**Problem**:
The test coverage is minimal for a critical production health check system. Only two basic tests exist:
1. `test_health_live_returns_alive` - validates basic response
2. `test_health_ready_returns_components` - validates basic structure

Missing critical test cases:
- Circuit breaker in different states (open, closed, half_open)
- Component failures and degraded states
- Overall health status determination logic
- Edge cases (exceptions during checks)
- Cache configured vs not configured scenarios

**Current Code**:
```python
# Line 15-24
def test_health_ready_returns_components():
    """health_ready should return component statuses."""
    from texas_grocery_mcp.observability.health import health_ready

    result = health_ready()

    assert "status" in result
    assert "components" in result
    assert "timestamp" in result
    assert result["status"] in ("healthy", "degraded", "unhealthy")
```

**Recommendation**:
Add comprehensive test cases covering:
- Circuit breaker open scenario (should mark graphql_api as down, status as degraded)
- Exception handling during GraphQL client creation
- Exception handling during settings retrieval
- Multiple component failures affecting overall status
- Timestamp format validation
- Mock the HEBGraphQLClient and settings to test different scenarios

Example test structure:
```python
@patch('texas_grocery_mcp.observability.health.HEBGraphQLClient')
def test_health_ready_degraded_when_circuit_open(mock_client):
    """health_ready should report degraded when circuit is open."""
    # Test implementation

def test_health_ready_unhealthy_when_graphql_fails():
    """health_ready should report unhealthy when GraphQL check fails."""
    # Test implementation
```

---

#### Issue 3: Missing Return Type Annotation
**File**: `src/texas_grocery_mcp/observability/health.py`
**Line(s)**: 12, 20
**Severity**: Must-Fix (per project standards)

**Problem**:
Functions return `dict` type annotations but the codebase uses Pydantic models extensively. The function actually returns the result of `.model_dump()`, which is more specifically a `dict[str, Any]`. This is inconsistent with the strong typing patterns in the rest of the codebase.

**Current Code**:
```python
# Line 12
def health_live() -> dict:

# Line 20
def health_ready() -> dict:
```

**Recommendation**:
Use more specific return type annotations:
```python
def health_live() -> dict[str, str]:
    """Liveness probe - is the process running?"""
    
def health_ready() -> dict[str, Any]:
    """Readiness probe - can the server handle requests?"""
```

Or better yet, return the Pydantic models directly and let the caller serialize if needed:
```python
def health_live() -> dict[str, str]:  # Simple dict is fine here

def health_ready() -> HealthResponse:  # Return the model
    # ... implementation ...
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(UTC).isoformat(),
        components=components,
        circuit_breakers=circuit_breakers,
    )
```

---

#### Issue 4: TODO Comment in Production Code
**File**: `src/texas_grocery_mcp/observability/health.py`
**Line(s)**: 60
**Severity**: Must-Fix

**Problem**:
There's a TODO comment for Redis connectivity check in what appears to be production-ready code. This means the cache health check always reports "up" even if Redis is actually down (when configured).

**Current Code**:
```python
# Line 59-65
if settings.redis_url:
    # TODO: Check Redis connectivity
    components["cache"] = ComponentHealth(status="up")
else:
    components["cache"] = ComponentHealth(
        status="up", message="Not configured (using in-memory)"
    )
```

**Recommendation**:
Either:
1. Implement the Redis connectivity check before shipping
2. Document explicitly that Redis check is not implemented and mark cache as "degraded" when Redis is configured but unchecked
3. Remove the Redis check entirely until it can be properly implemented

Suggested implementation:
```python
if settings.redis_url:
    # Redis check not yet implemented - report degraded
    components["cache"] = ComponentHealth(
        status="degraded", 
        message="Redis configured but connectivity check not implemented"
    )
    if overall_status == "healthy":
        overall_status = "degraded"
```

---

### Nice-to-Have Improvements

#### Suggestion 1: Add Latency Measurement
**File**: `src/texas_grocery_mcp/observability/health.py`
**Line(s)**: 29-52
**Category**: Observability

**Current**:
The `ComponentHealth` model has a `latency_ms` field, but it's never populated. Health checks don't measure response times.

**Suggested**:
Measure the time taken for each component check and populate the latency field:

```python
import time

start_time = time.perf_counter()
try:
    # ... health check logic ...
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    components["graphql_api"] = ComponentHealth(
        status="up",
        latency_ms=elapsed_ms
    )
```

**Rationale**:
Latency information is valuable for monitoring and alerting. If a component is "up" but slow, it indicates degraded performance.

---

#### Suggestion 2: Add Component Names as Constants
**File**: `src/texas_grocery_mcp/observability/health.py`
**Line(s)**: 37, 42, 49, 61, 63, 67
**Category**: Maintainability

**Current**:
Component names are hardcoded strings throughout the function: `"graphql_api"`, `"cache"`, `"heb_graphql"`.

**Suggested**:
Define component names as module-level constants:

```python
# At module level
COMPONENT_GRAPHQL_API = "graphql_api"
COMPONENT_CACHE = "cache"
CIRCUIT_BREAKER_HEB_GRAPHQL = "heb_graphql"

# In function
components[COMPONENT_GRAPHQL_API] = ComponentHealth(status="up")
```

**Rationale**:
Prevents typos, makes refactoring easier, and provides a single source of truth for component identifiers.

---

#### Suggestion 3: Extract Component Checks to Separate Functions
**File**: `src/texas_grocery_mcp/observability/health.py`
**Line(s)**: 29-75
**Category**: Readability / Testability

**Current**:
The `health_ready()` function has all component checks inline, making it long (47 lines) and harder to test individual checks.

**Suggested**:
Extract each component check to its own function:

```python
def _check_graphql_component() -> tuple[ComponentHealth, dict[str, CircuitBreakerStatus]]:
    """Check GraphQL API component health."""
    # ... existing logic ...
    return component, circuit_breaker_status

def _check_cache_component() -> ComponentHealth:
    """Check cache component health."""
    # ... existing logic ...
    return component

def health_ready() -> dict:
    """Readiness probe - can the server handle requests?"""
    components = {}
    circuit_breakers = {}
    
    # Check components
    components["graphql_api"], circuit_breakers = _check_graphql_component()
    components["cache"] = _check_cache_component()
    
    # Determine overall status
    overall_status = _compute_overall_status(components)
    
    return HealthResponse(...).model_dump()
```

**Rationale**:
Smaller, focused functions are easier to test, read, and maintain. Each component check can be tested independently.

---

#### Suggestion 4: Improve Error Messages
**File**: `src/texas_grocery_mcp/observability/health.py`
**Line(s)**: 50, 67
**Category**: Observability

**Current**:
Exception messages are passed directly via `str(e)`, which may not provide enough context.

```python
except Exception as e:
    components["graphql_api"] = ComponentHealth(
        status="down", message=str(e)
    )
```

**Suggested**:
Provide more context in error messages:

```python
except Exception as e:
    components["graphql_api"] = ComponentHealth(
        status="down", 
        message=f"GraphQL client initialization failed: {type(e).__name__}: {str(e)}"
    )
    logger.exception("Health check failed for GraphQL component")
```

**Rationale**:
Better error messages help with debugging. Including the exception type and logging the full traceback aids troubleshooting.

---

#### Suggestion 5: Add Docstring Examples
**File**: `src/texas_grocery_mcp/observability/health.py`
**Line(s)**: 12-16, 20-23
**Category**: Documentation

**Current**:
Docstrings are brief one-liners.

**Suggested**:
Add usage examples and return value documentation:

```python
def health_ready() -> dict:
    """Readiness probe - can the server handle requests?

    Returns detailed component health. Use for Kubernetes readiness probes.
    
    Returns:
        dict: Health response with structure:
            - status: "healthy" | "degraded" | "unhealthy"
            - timestamp: ISO 8601 timestamp
            - components: Dict of component statuses
            - circuit_breakers: Dict of circuit breaker states
    
    Example:
        >>> health_ready()
        {
            "status": "healthy",
            "timestamp": "2026-01-29T12:00:00Z",
            "components": {"graphql_api": {"status": "up"}},
            "circuit_breakers": {"heb_graphql": {"state": "closed"}}
        }
    """
```

**Rationale**:
Better documentation helps future developers understand expected behavior and return formats.

---

## What's Good

Despite the issues identified, there are several positive aspects of this implementation:

- **Clear separation of concerns**: Liveness and readiness probes are correctly separated
- **Good model design**: The Pydantic models (`ComponentHealth`, `CircuitBreakerStatus`, `HealthResponse`) are well-structured with appropriate fields
- **Follows existing patterns**: The code uses the same import style, type hints, and Pydantic patterns as the rest of the codebase
- **Meaningful status levels**: The three-level status system (healthy/degraded/unhealthy) provides useful granularity
- **Circuit breaker integration**: Smart to include circuit breaker state in health checks
- **Production-ready thinking**: Kubernetes probe compatibility shows thoughtfulness about deployment

## Checklist Summary

| Category | Status |
|----------|--------|
| Code Quality | ISSUES - Needs refactoring for async/sync consistency |
| Patterns & Conventions | ISSUES - Type annotations need improvement |
| Potential Issues | ISSUES - Resource leaks, incomplete implementation |
| Performance | PASS |
| Documentation | ISSUES - Missing comprehensive test coverage |
| Basic Security | PASS |

---

## Next Steps

1. **Fix async/sync mismatch** - Either make health endpoints async or restructure circuit breaker access
2. **Implement or remove TODO** - Complete Redis check or document why it's not checked
3. **Improve type annotations** - Use specific types instead of generic `dict`
4. **Expand test coverage** - Add tests for all component states and edge cases
5. **Consider refactoring** - Extract component checks to separate functions for better testability

Once these issues are addressed, the health check implementation will be production-ready and maintainable.
