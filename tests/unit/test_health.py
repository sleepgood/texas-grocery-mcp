"""Tests for health check tools."""

import pytest


def test_health_live_returns_alive():
    """health_live should return alive status."""
    from texas_grocery_mcp.observability.health import health_live

    result = health_live()

    assert result["status"] == "alive"


def test_health_ready_returns_components():
    """health_ready should return component statuses."""
    from texas_grocery_mcp.observability.health import health_ready

    result = health_ready()

    assert "status" in result
    assert "components" in result
    assert "timestamp" in result
    assert result["status"] in ("healthy", "degraded", "unhealthy")
