"""Health check endpoints."""

from datetime import UTC, datetime
from typing import Any

from texas_grocery_mcp.models.health import (
    CircuitBreakerStatus,
    ComponentHealth,
    HealthResponse,
)


def health_live() -> dict[str, str]:
    """Liveness probe - is the process running?

    Returns a simple alive status. Use for Kubernetes liveness probes.
    """
    return {"status": "alive"}


def health_ready() -> dict[str, Any]:
    """Readiness probe - can the server handle requests?

    Returns detailed component health. Use for Kubernetes readiness probes.
    """
    components: dict[str, ComponentHealth] = {}
    circuit_breakers: dict[str, CircuitBreakerStatus] = {}
    overall_status = "healthy"

    # Check GraphQL API status
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

        circuit_breakers["heb_graphql"] = CircuitBreakerStatus(
            state=cb_status["state"],
            failures=cb_status["failure_count"],
        )
    except Exception as e:
        components["graphql_api"] = ComponentHealth(
            status="down", message=str(e)
        )
        overall_status = "unhealthy"

    # Check cache status (if configured)
    try:
        from texas_grocery_mcp.utils.config import get_settings

        settings = get_settings()
        if settings.redis_url:
            # TODO: Check Redis connectivity
            components["cache"] = ComponentHealth(status="up")
        else:
            components["cache"] = ComponentHealth(
                status="up", message="Not configured (using in-memory)"
            )
    except Exception as e:
        components["cache"] = ComponentHealth(status="down", message=str(e))
        if overall_status == "healthy":
            overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(UTC).isoformat(),
        components=components,
        circuit_breakers=circuit_breakers,
    ).model_dump()
