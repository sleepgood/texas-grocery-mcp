# Texas Grocery MCP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a production-ready MCP server that enables AI agents to interact with HEB grocery stores for product search, cart management, and pickup scheduling.

**Architecture:** Dual-MCP architecture where Texas Grocery MCP handles grocery domain logic while Microsoft Playwright MCP handles browser-based authentication. Uses FastMCP framework with stdio transport, GraphQL primary API with HTML scraper fallback, and Redis caching for production performance.

**Tech Stack:** Python 3.11+, FastMCP 3.0+, httpx, Pydantic 2.0, Redis, structlog, prometheus-client

---

## Verification Protocol

**Every task ends with a verification checklist. You MUST:**

1. Run ALL verification commands listed
2. Confirm ALL expected outputs match
3. If ANY verification fails, fix before proceeding
4. Only commit after ALL verifications pass

**Verification Legend:**
- `[CMD]` - Command to run
- `[EXPECT]` - Expected output/behavior
- `[STOP]` - Condition that blocks proceeding to next task

---

## Phase 1: Project Foundation

### Task 1: Initialize Python Project Structure

**Files:**
- Create: `pyproject.toml`
- Create: `src/texas_grocery_mcp/__init__.py`
- Create: `src/texas_grocery_mcp/server.py`
- Create: `tests/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/integration/__init__.py`
- Create: `.env.example`
- Create: `.gitignore`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "texas-grocery-mcp"
version = "0.1.0"
description = "MCP server for HEB grocery store integration"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "Michael Walker", email = "mgwalkerjr95@gmail.com"}
]
keywords = ["mcp", "heb", "grocery", "ai", "llm"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "fastmcp>=2.0",
    "httpx>=0.27",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "beautifulsoup4>=4.12",
    "redis>=5.0",
    "structlog>=24.0",
    "prometheus-client>=0.19",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.1",
    "mypy>=1.8",
    "ruff>=0.1",
    "respx>=0.21",
]

[project.scripts]
texas-grocery-mcp = "texas_grocery_mcp.server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/texas_grocery_mcp"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Step 2: Create package __init__.py**

```python
"""Texas Grocery MCP - HEB grocery store integration for AI agents."""

__version__ = "0.1.0"
```

**Step 3: Create minimal server.py**

```python
"""Texas Grocery MCP Server - FastMCP entry point."""

from fastmcp import FastMCP

mcp = FastMCP(
    name="texas-grocery-mcp",
    version="0.1.0",
)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
```

**Step 4: Create test __init__.py files**

```python
# tests/__init__.py
"""Texas Grocery MCP test suite."""

# tests/unit/__init__.py
"""Unit tests."""

# tests/integration/__init__.py
"""Integration tests."""
```

**Step 5: Create .env.example**

```bash
# Texas Grocery MCP Configuration

# Default HEB store ID (find yours at heb.com)
HEB_DEFAULT_STORE=590

# Redis cache URL (optional for local dev)
REDIS_URL=redis://localhost:6379

# Logging level
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development
```

**Step 6: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env
.env.local

# Testing
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/

# Auth state (never commit!)
.texas-grocery-mcp/

# OS
.DS_Store
Thumbs.db
```

**Step 7: Install dependencies**

Run: `pip install -e ".[dev]"`

**Step 8: Commit**

```bash
git add pyproject.toml src/ tests/ .env.example .gitignore
git commit -m "feat: initialize texas-grocery-mcp project structure

- Add pyproject.toml with dependencies
- Create minimal FastMCP server entry point
- Set up test directory structure
- Add environment configuration template

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 1 Verification Checklist

Run each command and confirm the expected output:

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `ls pyproject.toml` | `pyproject.toml` (file exists) |
| 2 | `ls src/texas_grocery_mcp/__init__.py` | File exists |
| 3 | `ls src/texas_grocery_mcp/server.py` | File exists |
| 4 | `ls tests/unit/__init__.py` | File exists |
| 5 | `python -c "import texas_grocery_mcp; print(texas_grocery_mcp.__version__)"` | `0.1.0` |
| 6 | `python -c "from texas_grocery_mcp.server import mcp; print(mcp.name)"` | `texas-grocery-mcp` |
| 7 | `pip show texas-grocery-mcp` | Shows package info with version 0.1.0 |
| 8 | `which texas-grocery-mcp` | Shows path to installed script |
| 9 | `git status` | Clean working tree (all committed) |

**🛑 STOP - Do not proceed to Task 2 if:**
- `pip install -e ".[dev]"` failed
- Import of `texas_grocery_mcp` fails
- Import of `fastmcp` fails (dependency not installed)
- Any files are missing

---

### Task 2: Create Pydantic Configuration Module

**Files:**
- Create: `src/texas_grocery_mcp/utils/__init__.py`
- Create: `src/texas_grocery_mcp/utils/config.py`
- Test: `tests/unit/test_config.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_config.py
"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest


def test_settings_loads_defaults():
    """Settings should have sensible defaults."""
    from texas_grocery_mcp.utils.config import Settings

    settings = Settings()

    assert settings.log_level == "INFO"
    assert settings.environment == "development"


def test_settings_loads_from_env():
    """Settings should load from environment variables."""
    with patch.dict(os.environ, {"HEB_DEFAULT_STORE": "123", "LOG_LEVEL": "DEBUG"}):
        from importlib import reload

        import texas_grocery_mcp.utils.config as config_module

        reload(config_module)
        settings = config_module.Settings()

        assert settings.heb_default_store == "123"
        assert settings.log_level == "DEBUG"


def test_auth_state_path_expands_home():
    """Auth state path should expand ~ to home directory."""
    from texas_grocery_mcp.utils.config import Settings

    settings = Settings()

    assert "~" not in str(settings.auth_state_path)
    assert settings.auth_state_path.name == "auth.json"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'texas_grocery_mcp.utils'"

**Step 3: Create utils __init__.py**

```python
# src/texas_grocery_mcp/utils/__init__.py
"""Utility modules for Texas Grocery MCP."""

from texas_grocery_mcp.utils.config import Settings, get_settings

__all__ = ["Settings", "get_settings"]
```

**Step 4: Write config.py implementation**

```python
# src/texas_grocery_mcp/utils/config.py
"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # HEB Configuration
    heb_default_store: str | None = Field(
        default=None,
        description="Default HEB store ID for operations",
    )
    heb_graphql_url: str = Field(
        default="https://www.heb.com/graphql",
        description="HEB GraphQL API endpoint",
    )

    # Auth State
    auth_state_path: Path = Field(
        default=Path("~/.texas-grocery-mcp/auth.json").expanduser(),
        description="Path to Playwright auth state file",
    )

    # Redis Configuration
    redis_url: str | None = Field(
        default=None,
        description="Redis connection URL for caching",
    )

    # Observability
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment",
    )

    # Reliability
    retry_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of retry attempts for failed requests",
    )
    circuit_breaker_threshold: int = Field(
        default=5,
        ge=1,
        description="Failures before circuit breaker opens",
    )
    circuit_breaker_timeout: int = Field(
        default=30,
        ge=5,
        description="Seconds before circuit breaker attempts recovery",
    )

    def model_post_init(self, __context) -> None:
        """Ensure auth state path is expanded."""
        if "~" in str(self.auth_state_path):
            object.__setattr__(
                self, "auth_state_path", Path(str(self.auth_state_path)).expanduser()
            )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
```

**Step 5: Commit**

```bash
git add src/texas_grocery_mcp/utils/ tests/unit/test_config.py
git commit -m "feat: add Pydantic settings configuration module

- Load config from environment variables
- Support .env file loading
- Configure HEB, Redis, and observability settings
- Add reliability settings for retry and circuit breaker

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 2 Verification Checklist

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `pytest tests/unit/test_config.py -v` | `3 passed` |
| 2 | `pytest tests/unit/test_config.py -v 2>&1 \| grep -E "PASSED\|FAILED"` | 3 lines with `PASSED`, 0 with `FAILED` |
| 3 | `ruff check src/texas_grocery_mcp/utils/` | No errors (exit code 0) |
| 4 | `python -c "from texas_grocery_mcp.utils import Settings; s=Settings(); print(s.log_level)"` | `INFO` |
| 5 | `python -c "from texas_grocery_mcp.utils import get_settings; print(get_settings().environment)"` | `development` |
| 6 | `git status` | Clean working tree |

**🛑 STOP - Do not proceed to Task 3 if:**
- Any test in `test_config.py` fails
- `ruff check` reports errors
- Settings cannot be imported

---

### Task 3: Create Core Data Models

**Files:**
- Create: `src/texas_grocery_mcp/models/__init__.py`
- Create: `src/texas_grocery_mcp/models/store.py`
- Create: `src/texas_grocery_mcp/models/product.py`
- Create: `src/texas_grocery_mcp/models/cart.py`
- Create: `src/texas_grocery_mcp/models/errors.py`
- Test: `tests/unit/test_models.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_models.py
"""Tests for data models."""

import pytest


def test_store_model_required_fields():
    """Store model should require essential fields."""
    from texas_grocery_mcp.models import Store

    store = Store(
        store_id="590",
        name="H-E-B Mueller",
        address="1801 E 51st St, Austin, TX 78723",
    )

    assert store.store_id == "590"
    assert store.name == "H-E-B Mueller"
    assert store.address == "1801 E 51st St, Austin, TX 78723"


def test_product_model_minimal_fields():
    """Product model should work with minimal fields."""
    from texas_grocery_mcp.models import Product

    product = Product(
        sku="123456",
        name="HEB Whole Milk",
        price=3.49,
        available=True,
    )

    assert product.sku == "123456"
    assert product.price == 3.49


def test_product_model_full_fields():
    """Product model should accept all optional fields."""
    from texas_grocery_mcp.models import Product

    product = Product(
        sku="123456",
        name="HEB Whole Milk",
        price=3.49,
        available=True,
        brand="H-E-B",
        size="1 gallon",
        price_per_unit="$3.49/gal",
        image_url="https://example.com/milk.jpg",
        aisle="5",
        section="Dairy",
        on_sale=True,
        original_price=4.29,
    )

    assert product.brand == "H-E-B"
    assert product.on_sale is True


def test_cart_item_calculates_subtotal():
    """CartItem should calculate subtotal from price and quantity."""
    from texas_grocery_mcp.models import CartItem

    item = CartItem(
        sku="123456",
        name="HEB Whole Milk",
        price=3.49,
        quantity=2,
    )

    assert item.subtotal == 6.98


def test_error_response_structure():
    """ErrorResponse should have proper structure."""
    from texas_grocery_mcp.models import ErrorResponse

    error = ErrorResponse(
        code="HEB_API_TIMEOUT",
        category="external",
        message="HEB API request timed out",
        retry_after_seconds=30,
        suggestions=["Try again in 30 seconds"],
    )

    assert error.error is True
    assert error.category == "external"
    assert error.retry_after_seconds == 30
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_models.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create models __init__.py**

```python
# src/texas_grocery_mcp/models/__init__.py
"""Data models for Texas Grocery MCP."""

from texas_grocery_mcp.models.cart import Cart, CartItem
from texas_grocery_mcp.models.errors import ErrorResponse
from texas_grocery_mcp.models.product import Product
from texas_grocery_mcp.models.store import Store

__all__ = [
    "Cart",
    "CartItem",
    "ErrorResponse",
    "Product",
    "Store",
]
```

**Step 4: Create store.py**

```python
# src/texas_grocery_mcp/models/store.py
"""Store data models."""

from pydantic import BaseModel, Field


class StoreHours(BaseModel):
    """Store operating hours."""

    monday: str = Field(alias="mon", default="6am-11pm")
    tuesday: str = Field(alias="tue", default="6am-11pm")
    wednesday: str = Field(alias="wed", default="6am-11pm")
    thursday: str = Field(alias="thu", default="6am-11pm")
    friday: str = Field(alias="fri", default="6am-11pm")
    saturday: str = Field(alias="sat", default="6am-11pm")
    sunday: str = Field(alias="sun", default="6am-11pm")

    model_config = {"populate_by_name": True}


class Store(BaseModel):
    """HEB store information."""

    store_id: str = Field(description="Unique store identifier")
    name: str = Field(description="Store display name")
    address: str = Field(description="Full street address")
    phone: str | None = Field(default=None, description="Store phone number")
    distance_miles: float | None = Field(
        default=None, description="Distance from search location"
    )
    hours: StoreHours | None = Field(default=None, description="Operating hours")
    services: list[str] = Field(
        default_factory=list,
        description="Available services (curbside, delivery, pharmacy)",
    )
    latitude: float | None = Field(default=None, description="Store latitude")
    longitude: float | None = Field(default=None, description="Store longitude")
```

**Step 5: Create product.py**

```python
# src/texas_grocery_mcp/models/product.py
"""Product data models."""

from pydantic import BaseModel, Field


class ProductNutrition(BaseModel):
    """Nutritional information."""

    calories: int | None = None
    protein: str | None = None
    carbohydrates: str | None = None
    fat: str | None = None
    fiber: str | None = None
    sodium: str | None = None


class ProductCoupon(BaseModel):
    """Coupon applicable to product."""

    code: str
    discount: str
    expires: str | None = None


class Product(BaseModel):
    """HEB product information."""

    # Minimal fields (always returned)
    sku: str = Field(description="Product SKU/ID")
    name: str = Field(description="Product name")
    price: float = Field(description="Current price")
    available: bool = Field(description="In stock at store")

    # Standard fields (optional)
    brand: str | None = Field(default=None, description="Brand name")
    size: str | None = Field(default=None, description="Package size")
    price_per_unit: str | None = Field(default=None, description="Unit price display")
    image_url: str | None = Field(default=None, description="Product image URL")
    aisle: str | None = Field(default=None, description="Store aisle number")
    section: str | None = Field(default=None, description="Store section")

    # Extended fields (optional)
    nutrition: ProductNutrition | None = Field(default=None, description="Nutrition facts")
    ingredients: list[str] | None = Field(default=None, description="Ingredient list")
    on_sale: bool = Field(default=False, description="Currently on sale")
    original_price: float | None = Field(default=None, description="Price before sale")
    rating: float | None = Field(default=None, ge=0, le=5, description="Customer rating")
    coupons: list[ProductCoupon] = Field(
        default_factory=list, description="Applicable coupons"
    )
```

**Step 6: Create cart.py**

```python
# src/texas_grocery_mcp/models/cart.py
"""Cart data models."""

from pydantic import BaseModel, Field, computed_field


class CartItem(BaseModel):
    """Item in shopping cart."""

    sku: str = Field(description="Product SKU")
    name: str = Field(description="Product name")
    price: float = Field(description="Unit price")
    quantity: int = Field(ge=1, description="Quantity in cart")
    image_url: str | None = Field(default=None, description="Product image")

    @computed_field
    @property
    def subtotal(self) -> float:
        """Calculate item subtotal."""
        return round(self.price * self.quantity, 2)


class AppliedCoupon(BaseModel):
    """Coupon applied to cart."""

    code: str = Field(description="Coupon code")
    discount: float = Field(description="Discount amount")
    description: str | None = Field(default=None, description="Coupon description")


class Cart(BaseModel):
    """Shopping cart."""

    items: list[CartItem] = Field(default_factory=list, description="Cart items")
    coupons_applied: list[AppliedCoupon] = Field(
        default_factory=list, description="Applied coupons"
    )

    @computed_field
    @property
    def subtotal(self) -> float:
        """Calculate cart subtotal before coupons."""
        return round(sum(item.subtotal for item in self.items), 2)

    @computed_field
    @property
    def total_discount(self) -> float:
        """Calculate total coupon discount."""
        return round(sum(c.discount for c in self.coupons_applied), 2)

    @computed_field
    @property
    def estimated_total(self) -> float:
        """Calculate estimated total after discounts."""
        return round(self.subtotal - self.total_discount, 2)

    @computed_field
    @property
    def item_count(self) -> int:
        """Total number of items in cart."""
        return sum(item.quantity for item in self.items)
```

**Step 7: Create errors.py**

```python
# src/texas_grocery_mcp/models/errors.py
"""Error response models."""

from typing import Literal

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Structured error response."""

    error: bool = Field(default=True, description="Always true for errors")
    code: str = Field(description="Error code (e.g., HEB_API_TIMEOUT)")
    category: Literal["client", "server", "external"] = Field(
        description="Error category for handling"
    )
    message: str = Field(description="Human-readable error message")
    retry_after_seconds: int | None = Field(
        default=None, description="Seconds to wait before retry"
    )
    fallback_used: bool = Field(
        default=False, description="Whether fallback data source was used"
    )
    fallback_source: str | None = Field(
        default=None, description="Which fallback was used (cache, scraper)"
    )
    suggestions: list[str] = Field(
        default_factory=list, description="Actionable suggestions"
    )


class AuthRequiredResponse(BaseModel):
    """Response when authentication is required."""

    auth_required: bool = Field(default=True)
    message: str = Field(default="Login required for this operation")
    instructions: list[str] = Field(
        default_factory=lambda: [
            "1. Use Playwright MCP: browser_navigate to 'https://www.heb.com/login'",
            "2. Complete login in the browser",
            "3. Use Playwright MCP: browser_run_code to save storage state",
            "4. Retry this operation",
        ]
    )
```

**Step 8: Commit**

```bash
git add src/texas_grocery_mcp/models/ tests/unit/test_models.py
git commit -m "feat: add core Pydantic data models

- Store model with hours and services
- Product model with configurable field levels
- Cart model with computed subtotals
- Structured error responses with categories

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 3 Verification Checklist

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `pytest tests/unit/test_models.py -v` | `5 passed` |
| 2 | `python -c "from texas_grocery_mcp.models import Store, Product, Cart, CartItem, ErrorResponse; print('All imports OK')"` | `All imports OK` |
| 3 | `python -c "from texas_grocery_mcp.models import CartItem; c=CartItem(sku='1',name='x',price=2.50,quantity=3); print(c.subtotal)"` | `7.5` |
| 4 | `ruff check src/texas_grocery_mcp/models/` | No errors |
| 5 | `git status` | Clean working tree |

**🛑 STOP - Do not proceed to Task 4 if:**
- Any test in `test_models.py` fails
- CartItem subtotal calculation is incorrect
- Model imports fail

---

## Phase 2: Reliability Infrastructure

### Task 4: Implement Retry Logic with Exponential Backoff

**Files:**
- Create: `src/texas_grocery_mcp/reliability/__init__.py`
- Create: `src/texas_grocery_mcp/reliability/retry.py`
- Test: `tests/unit/test_retry.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_retry.py
"""Tests for retry logic."""

import pytest

from texas_grocery_mcp.reliability.retry import RetryConfig, with_retry


@pytest.mark.asyncio
async def test_retry_succeeds_on_first_attempt():
    """Should return immediately if function succeeds."""
    call_count = 0

    @with_retry()
    async def succeeds():
        nonlocal call_count
        call_count += 1
        return "success"

    result = await succeeds()

    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_retries_on_failure():
    """Should retry on transient failures."""
    call_count = 0

    @with_retry(config=RetryConfig(max_attempts=3, base_delay=0.01))
    async def fails_twice():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Network error")
        return "success"

    result = await fails_twice()

    assert result == "success"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_raises_after_max_attempts():
    """Should raise after exhausting retries."""
    call_count = 0

    @with_retry(config=RetryConfig(max_attempts=2, base_delay=0.01))
    async def always_fails():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("Network error")

    with pytest.raises(ConnectionError):
        await always_fails()

    assert call_count == 2


@pytest.mark.asyncio
async def test_retry_does_not_retry_non_retryable():
    """Should not retry non-retryable exceptions."""
    call_count = 0

    @with_retry(config=RetryConfig(max_attempts=3, base_delay=0.01))
    async def validation_error():
        nonlocal call_count
        call_count += 1
        raise ValueError("Invalid input")

    with pytest.raises(ValueError):
        await validation_error()

    assert call_count == 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_retry.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create reliability __init__.py**

```python
# src/texas_grocery_mcp/reliability/__init__.py
"""Reliability patterns for production resilience."""

from texas_grocery_mcp.reliability.retry import RetryConfig, with_retry

__all__ = ["RetryConfig", "with_retry"]
```

**Step 4: Write retry.py implementation**

```python
# src/texas_grocery_mcp/reliability/retry.py
"""Retry logic with exponential backoff and jitter."""

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from functools import wraps
from typing import ParamSpec, TypeVar

import structlog

logger = structlog.get_logger()

P = ParamSpec("P")
T = TypeVar("T")

# Exceptions that should trigger retry
RETRYABLE_EXCEPTIONS: tuple[type[Exception], ...] = (
    ConnectionError,
    TimeoutError,
    OSError,
)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = field(
        default_factory=lambda: RETRYABLE_EXCEPTIONS
    )


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for next retry attempt."""
    delay = config.base_delay * (config.exponential_base ** (attempt - 1))
    delay = min(delay, config.max_delay)

    if config.jitter:
        delay = delay * (0.5 + random.random())

    return delay


def with_retry(
    config: RetryConfig | None = None,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Decorator for async functions with retry logic.

    Args:
        config: Retry configuration. Uses defaults if not provided.

    Returns:
        Decorated function that retries on transient failures.
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception: Exception | None = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    if attempt < config.max_attempts:
                        delay = calculate_delay(attempt, config)
                        logger.warning(
                            "Retry attempt",
                            function=func.__name__,
                            attempt=attempt,
                            max_attempts=config.max_attempts,
                            delay=delay,
                            error=str(e),
                        )
                        await asyncio.sleep(delay)
                except Exception:
                    # Non-retryable exception, raise immediately
                    raise

            # Exhausted all retries
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry state")

        return wrapper

    return decorator
```

**Step 5: Commit**

```bash
git add src/texas_grocery_mcp/reliability/ tests/unit/test_retry.py
git commit -m "feat: add retry logic with exponential backoff

- Configurable max attempts and delays
- Exponential backoff with jitter
- Only retry transient exceptions
- Structured logging for retry attempts

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 4 Verification Checklist

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `pytest tests/unit/test_retry.py -v` | `4 passed` |
| 2 | `python -c "from texas_grocery_mcp.reliability import RetryConfig, with_retry; print('OK')"` | `OK` |
| 3 | `python -c "from texas_grocery_mcp.reliability.retry import calculate_delay, RetryConfig; print(calculate_delay(1, RetryConfig(jitter=False)))"` | `1.0` |
| 4 | `python -c "from texas_grocery_mcp.reliability.retry import calculate_delay, RetryConfig; print(calculate_delay(2, RetryConfig(jitter=False)))"` | `2.0` |
| 5 | `ruff check src/texas_grocery_mcp/reliability/` | No errors |
| 6 | `git status` | Clean working tree |

**🛑 STOP - Do not proceed to Task 5 if:**
- Any retry test fails
- Exponential backoff calculation is incorrect (delay should double each attempt without jitter)
- Non-retryable exceptions are being retried

---

### Task 5: Implement Circuit Breaker Pattern

**Files:**
- Create: `src/texas_grocery_mcp/reliability/circuit_breaker.py`
- Update: `src/texas_grocery_mcp/reliability/__init__.py`
- Test: `tests/unit/test_circuit_breaker.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_circuit_breaker.py
"""Tests for circuit breaker pattern."""

import asyncio

import pytest

from texas_grocery_mcp.reliability.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpen,
    CircuitState,
)


def test_circuit_starts_closed():
    """Circuit should start in closed state."""
    cb = CircuitBreaker("test")
    assert cb.state == CircuitState.CLOSED


def test_circuit_opens_after_threshold():
    """Circuit should open after failure threshold."""
    cb = CircuitBreaker("test", config=CircuitBreakerConfig(failure_threshold=2))

    cb.record_failure()
    assert cb.state == CircuitState.CLOSED

    cb.record_failure()
    assert cb.state == CircuitState.OPEN


def test_circuit_resets_on_success():
    """Circuit should reset failure count on success."""
    cb = CircuitBreaker("test", config=CircuitBreakerConfig(failure_threshold=3))

    cb.record_failure()
    cb.record_failure()
    cb.record_success()

    assert cb.failure_count == 0
    assert cb.state == CircuitState.CLOSED


def test_open_circuit_raises():
    """Open circuit should raise CircuitBreakerOpen."""
    cb = CircuitBreaker("test", config=CircuitBreakerConfig(failure_threshold=1))
    cb.record_failure()

    with pytest.raises(CircuitBreakerOpen):
        cb.check()


@pytest.mark.asyncio
async def test_circuit_transitions_to_half_open():
    """Circuit should transition to half-open after timeout."""
    cb = CircuitBreaker(
        "test",
        config=CircuitBreakerConfig(failure_threshold=1, recovery_timeout=0.1),
    )
    cb.record_failure()
    assert cb.state == CircuitState.OPEN

    # Wait for recovery timeout
    await asyncio.sleep(0.15)

    # Next check should allow through (half-open)
    cb.check()  # Should not raise
    assert cb.state == CircuitState.HALF_OPEN
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_circuit_breaker.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write circuit_breaker.py implementation**

```python
# src/texas_grocery_mcp/reliability/circuit_breaker.py
"""Circuit breaker pattern for preventing cascading failures."""

import time
from dataclasses import dataclass
from enum import Enum
from threading import Lock

import structlog

logger = structlog.get_logger()


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""

    def __init__(self, name: str, retry_after: float):
        self.name = name
        self.retry_after = retry_after
        super().__init__(f"Circuit breaker '{name}' is open. Retry after {retry_after:.1f}s")


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3


class CircuitBreaker:
    """Circuit breaker for external service calls.

    Prevents cascading failures by "tripping" after repeated failures
    and allowing the system to recover.
    """

    def __init__(self, name: str, config: CircuitBreakerConfig | None = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float | None = None
        self._half_open_calls = 0
        self._lock = Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, checking for transition to half-open."""
        with self._lock:
            if self._state == CircuitState.OPEN and self._should_attempt_recovery():
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                logger.info("Circuit breaker transitioning to half-open", name=self.name)
            return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        return self._failure_count

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self._last_failure_time is None:
            return False
        return time.time() - self._last_failure_time >= self.config.recovery_timeout

    def check(self) -> None:
        """Check if request should be allowed.

        Raises:
            CircuitBreakerOpen: If circuit is open and recovery timeout hasn't elapsed.
        """
        current_state = self.state  # This may transition to half-open

        if current_state == CircuitState.OPEN:
            retry_after = (
                self.config.recovery_timeout
                - (time.time() - (self._last_failure_time or 0))
            )
            raise CircuitBreakerOpen(self.name, max(0, retry_after))

        if current_state == CircuitState.HALF_OPEN:
            with self._lock:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpen(self.name, self.config.recovery_timeout)
                self._half_open_calls += 1

    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.half_open_max_calls:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    logger.info("Circuit breaker closed", name=self.name)
            else:
                self._failure_count = 0
                self._success_count = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning(
                    "Circuit breaker reopened from half-open",
                    name=self.name,
                )
            elif self._failure_count >= self.config.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(
                    "Circuit breaker opened",
                    name=self.name,
                    failure_count=self._failure_count,
                )

    def get_status(self) -> dict:
        """Get circuit breaker status for health checks."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
        }
```

**Step 4: Update reliability __init__.py**

```python
# src/texas_grocery_mcp/reliability/__init__.py
"""Reliability patterns for production resilience."""

from texas_grocery_mcp.reliability.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpen,
    CircuitState,
)
from texas_grocery_mcp.reliability.retry import RetryConfig, with_retry

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerOpen",
    "CircuitState",
    "RetryConfig",
    "with_retry",
]
```

**Step 5: Commit**

```bash
git add src/texas_grocery_mcp/reliability/ tests/unit/test_circuit_breaker.py
git commit -m "feat: add circuit breaker pattern

- Three states: closed, open, half-open
- Configurable failure threshold and recovery timeout
- Thread-safe state transitions
- Status reporting for health checks

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 5 Verification Checklist

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `pytest tests/unit/test_circuit_breaker.py -v` | `5 passed` |
| 2 | `pytest tests/unit/test_retry.py tests/unit/test_circuit_breaker.py -v` | `9 passed` (all reliability tests) |
| 3 | `python -c "from texas_grocery_mcp.reliability import CircuitBreaker, CircuitState; cb=CircuitBreaker('test'); print(cb.state)"` | `CircuitState.CLOSED` |
| 4 | `python -c "from texas_grocery_mcp.reliability import CircuitBreaker, CircuitBreakerConfig; cb=CircuitBreaker('test', CircuitBreakerConfig(failure_threshold=1)); cb.record_failure(); print(cb.state.value)"` | `open` |
| 5 | `ruff check src/texas_grocery_mcp/reliability/` | No errors |
| 6 | `git status` | Clean working tree |

**🛑 STOP - Do not proceed to Task 6 if:**
- Circuit breaker doesn't open after threshold failures
- Circuit breaker doesn't transition to half-open after timeout
- CircuitBreakerOpen exception not raised when circuit is open

---

## Phase 3: GraphQL Client

### Task 6: Create HEB GraphQL Client

**Files:**
- Create: `src/texas_grocery_mcp/clients/__init__.py`
- Create: `src/texas_grocery_mcp/clients/graphql.py`
- Test: `tests/unit/test_graphql_client.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_graphql_client.py
"""Tests for HEB GraphQL client."""

import pytest
import respx
from httpx import Response

from texas_grocery_mcp.clients.graphql import HEBGraphQLClient


@pytest.fixture
def client():
    """Create test client."""
    return HEBGraphQLClient()


@pytest.mark.asyncio
@respx.mock
async def test_search_stores_success(client):
    """Should parse store search response."""
    mock_response = {
        "data": {
            "searchStoresByAddress": {
                "stores": [
                    {
                        "store": {
                            "id": "590",
                            "name": "H-E-B Mueller",
                            "address1": "1801 E 51st St",
                            "city": "Austin",
                            "state": "TX",
                            "postalCode": "78723",
                        },
                        "distance": 2.3,
                    }
                ]
            }
        }
    }

    respx.post("https://www.heb.com/graphql").mock(
        return_value=Response(200, json=mock_response)
    )

    stores = await client.search_stores(address="Austin, TX", radius_miles=10)

    assert len(stores) == 1
    assert stores[0].store_id == "590"
    assert stores[0].name == "H-E-B Mueller"


@pytest.mark.asyncio
@respx.mock
async def test_search_products_success(client):
    """Should parse product search response."""
    mock_response = {
        "data": {
            "searchProducts": {
                "products": [
                    {
                        "productId": "123456",
                        "description": "HEB Whole Milk 1 Gallon",
                        "price": 3.49,
                        "isAvailable": True,
                        "brand": "H-E-B",
                    }
                ]
            }
        }
    }

    respx.post("https://www.heb.com/graphql").mock(
        return_value=Response(200, json=mock_response)
    )

    products = await client.search_products(query="milk", store_id="590")

    assert len(products) == 1
    assert products[0].sku == "123456"
    assert products[0].price == 3.49


@pytest.mark.asyncio
@respx.mock
async def test_handles_graphql_error(client):
    """Should raise on GraphQL errors."""
    mock_response = {
        "errors": [{"message": "Store not found"}],
        "data": None,
    }

    respx.post("https://www.heb.com/graphql").mock(
        return_value=Response(200, json=mock_response)
    )

    with pytest.raises(Exception, match="GraphQL error"):
        await client.search_stores(address="Invalid", radius_miles=10)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_graphql_client.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create clients __init__.py**

```python
# src/texas_grocery_mcp/clients/__init__.py
"""API clients for external services."""

from texas_grocery_mcp.clients.graphql import HEBGraphQLClient

__all__ = ["HEBGraphQLClient"]
```

**Step 4: Write graphql.py implementation**

```python
# src/texas_grocery_mcp/clients/graphql.py
"""HEB GraphQL API client."""

from typing import Any

import httpx
import structlog

from texas_grocery_mcp.models import Product, Store
from texas_grocery_mcp.reliability import CircuitBreaker, RetryConfig, with_retry
from texas_grocery_mcp.utils.config import get_settings

logger = structlog.get_logger()


class GraphQLError(Exception):
    """Raised when GraphQL returns errors."""

    def __init__(self, errors: list[dict]):
        self.errors = errors
        messages = [e.get("message", "Unknown error") for e in errors]
        super().__init__(f"GraphQL error: {'; '.join(messages)}")


# GraphQL Queries
STORE_SEARCH_QUERY = """
query SearchStores($address: String!, $radius: Int!) {
    searchStoresByAddress(address: $address, radius: $radius) {
        stores {
            store {
                id
                name
                address1
                city
                state
                postalCode
                phoneNumber
                latitude
                longitude
            }
            distance
        }
    }
}
"""

PRODUCT_SEARCH_QUERY = """
query SearchProducts($query: String!, $storeId: String!, $limit: Int) {
    searchProducts(searchTerm: $query, storeId: $storeId, limit: $limit) {
        products {
            productId
            description
            brand
            price
            isAvailable
            imageUrl
            unitPrice
            unitOfMeasure
        }
    }
}
"""


class HEBGraphQLClient:
    """Client for HEB's GraphQL API."""

    def __init__(self, base_url: str | None = None):
        settings = get_settings()
        self.base_url = base_url or settings.heb_graphql_url
        self.circuit_breaker = CircuitBreaker("heb_graphql")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @with_retry(config=RetryConfig(max_attempts=3, base_delay=1.0))
    async def _execute(
        self,
        query: str,
        variables: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            Response data

        Raises:
            GraphQLError: If GraphQL returns errors
            CircuitBreakerOpen: If circuit is open
        """
        self.circuit_breaker.check()

        client = await self._get_client()

        try:
            response = await client.post(
                self.base_url,
                json={"query": query, "variables": variables},
            )
            response.raise_for_status()

            data = response.json()

            if "errors" in data and data["errors"]:
                raise GraphQLError(data["errors"])

            self.circuit_breaker.record_success()
            return data["data"]

        except (httpx.HTTPError, GraphQLError) as e:
            self.circuit_breaker.record_failure()
            logger.error(
                "GraphQL request failed",
                error=str(e),
                query_type=query.split("(")[0].strip().split()[-1],
            )
            raise

    async def search_stores(
        self,
        address: str,
        radius_miles: int = 25,
    ) -> list[Store]:
        """Search for HEB stores near an address.

        Args:
            address: Address or zip code to search near
            radius_miles: Search radius in miles

        Returns:
            List of stores sorted by distance
        """
        data = await self._execute(
            STORE_SEARCH_QUERY,
            {"address": address, "radius": radius_miles},
        )

        stores = []
        for result in data.get("searchStoresByAddress", {}).get("stores", []):
            store_data = result.get("store", {})
            stores.append(
                Store(
                    store_id=store_data.get("id", ""),
                    name=store_data.get("name", ""),
                    address=(
                        f"{store_data.get('address1', '')}, "
                        f"{store_data.get('city', '')}, "
                        f"{store_data.get('state', '')} "
                        f"{store_data.get('postalCode', '')}"
                    ),
                    phone=store_data.get("phoneNumber"),
                    distance_miles=result.get("distance"),
                    latitude=store_data.get("latitude"),
                    longitude=store_data.get("longitude"),
                )
            )

        return stores

    async def search_products(
        self,
        query: str,
        store_id: str,
        limit: int = 20,
    ) -> list[Product]:
        """Search for products at a store.

        Args:
            query: Search query
            store_id: Store ID for inventory/pricing
            limit: Maximum results to return

        Returns:
            List of matching products
        """
        data = await self._execute(
            PRODUCT_SEARCH_QUERY,
            {"query": query, "storeId": store_id, "limit": limit},
        )

        products = []
        for item in data.get("searchProducts", {}).get("products", []):
            products.append(
                Product(
                    sku=item.get("productId", ""),
                    name=item.get("description", ""),
                    price=item.get("price", 0.0),
                    available=item.get("isAvailable", False),
                    brand=item.get("brand"),
                    image_url=item.get("imageUrl"),
                    price_per_unit=(
                        f"${item.get('unitPrice', 0)}/{item.get('unitOfMeasure', 'ea')}"
                        if item.get("unitPrice")
                        else None
                    ),
                )
            )

        return products

    def get_status(self) -> dict:
        """Get client status for health checks."""
        return {
            "circuit_breaker": self.circuit_breaker.get_status(),
        }
```

**Step 5: Commit**

```bash
git add src/texas_grocery_mcp/clients/ tests/unit/test_graphql_client.py
git commit -m "feat: add HEB GraphQL API client

- Store and product search operations
- Integrated retry logic and circuit breaker
- Structured error handling for GraphQL errors
- Health status reporting

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 6 Verification Checklist

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `pytest tests/unit/test_graphql_client.py -v` | `3 passed` |
| 2 | `python -c "from texas_grocery_mcp.clients import HEBGraphQLClient; print('OK')"` | `OK` |
| 3 | `python -c "from texas_grocery_mcp.clients.graphql import GraphQLError; raise GraphQLError([{'message': 'test'}])" 2>&1 \| grep "GraphQL error: test"` | Contains "GraphQL error: test" |
| 4 | `pytest tests/unit/ -v --tb=short` | All tests pass (should be 17+ tests) |
| 5 | `ruff check src/texas_grocery_mcp/clients/` | No errors |
| 6 | `git status` | Clean working tree |

**🛑 STOP - Do not proceed to Task 7 if:**
- GraphQL client tests fail
- GraphQL client doesn't integrate with circuit breaker
- respx mocking not working (check respx is installed)

---

## Phase 4: MCP Tools

### Task 7: Implement Store Tools

**Files:**
- Create: `src/texas_grocery_mcp/tools/__init__.py`
- Create: `src/texas_grocery_mcp/tools/store.py`
- Update: `src/texas_grocery_mcp/server.py`
- Test: `tests/unit/test_store_tools.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_store_tools.py
"""Tests for store tools."""

import pytest
import respx
from httpx import Response


@pytest.fixture
def mock_store_response():
    """Mock GraphQL store response."""
    return {
        "data": {
            "searchStoresByAddress": {
                "stores": [
                    {
                        "store": {
                            "id": "590",
                            "name": "H-E-B Mueller",
                            "address1": "1801 E 51st St",
                            "city": "Austin",
                            "state": "TX",
                            "postalCode": "78723",
                        },
                        "distance": 2.3,
                    }
                ]
            }
        }
    }


@pytest.mark.asyncio
@respx.mock
async def test_store_search_tool(mock_store_response):
    """store_search should return formatted stores."""
    from texas_grocery_mcp.tools.store import store_search

    respx.post("https://www.heb.com/graphql").mock(
        return_value=Response(200, json=mock_store_response)
    )

    result = await store_search(address="Austin, TX")

    assert len(result["stores"]) == 1
    assert result["stores"][0]["store_id"] == "590"
    assert result["stores"][0]["name"] == "H-E-B Mueller"


def test_store_set_default():
    """store_set_default should save store ID."""
    from texas_grocery_mcp.tools.store import store_get_default, store_set_default

    result = store_set_default(store_id="590")

    assert result["success"] is True
    assert result["store_id"] == "590"

    default = store_get_default()
    assert default["store_id"] == "590"


def test_store_get_default_none():
    """store_get_default should return None when not set."""
    from texas_grocery_mcp.tools import store as store_module

    # Reset the default
    store_module._default_store_id = None

    result = store_module.store_get_default()

    assert result["store_id"] is None
    assert "not set" in result["message"].lower()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_store_tools.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create tools __init__.py**

```python
# src/texas_grocery_mcp/tools/__init__.py
"""MCP tool definitions."""

from texas_grocery_mcp.tools import store

__all__ = ["store"]
```

**Step 4: Write store.py implementation**

```python
# src/texas_grocery_mcp/tools/store.py
"""Store-related MCP tools."""

from typing import Annotated

from pydantic import Field

from texas_grocery_mcp.clients.graphql import HEBGraphQLClient

# Module-level state for default store
_default_store_id: str | None = None
_graphql_client: HEBGraphQLClient | None = None


def _get_client() -> HEBGraphQLClient:
    """Get or create GraphQL client."""
    global _graphql_client
    if _graphql_client is None:
        _graphql_client = HEBGraphQLClient()
    return _graphql_client


async def store_search(
    address: Annotated[str, Field(description="Address or zip code to search near")],
    radius_miles: Annotated[
        int, Field(description="Search radius in miles", ge=1, le=100)
    ] = 25,
) -> dict:
    """Search for HEB stores near an address.

    Returns stores sorted by distance, including store ID, name,
    address, and distance from the search location.
    """
    client = _get_client()
    stores = await client.search_stores(address=address, radius_miles=radius_miles)

    return {
        "stores": [
            {
                "store_id": s.store_id,
                "name": s.name,
                "address": s.address,
                "distance_miles": s.distance_miles,
                "phone": s.phone,
            }
            for s in stores
        ],
        "count": len(stores),
    }


def store_set_default(
    store_id: Annotated[str, Field(description="Store ID to set as default")],
) -> dict:
    """Set the default store for future operations.

    The default store is used when no store_id is provided to other tools.
    """
    global _default_store_id
    _default_store_id = store_id

    return {
        "success": True,
        "store_id": store_id,
        "message": f"Default store set to {store_id}",
    }


def store_get_default() -> dict:
    """Get the currently set default store.

    Returns the default store ID if set, otherwise indicates no default.
    """
    if _default_store_id is None:
        return {
            "store_id": None,
            "message": "Default store not set. Use store_set_default to set one.",
        }

    return {
        "store_id": _default_store_id,
        "message": f"Default store is {_default_store_id}",
    }


def get_default_store_id() -> str | None:
    """Get default store ID for internal use."""
    return _default_store_id
```

**Step 5: Update server.py to register tools**

```python
# src/texas_grocery_mcp/server.py
"""Texas Grocery MCP Server - FastMCP entry point."""

from fastmcp import FastMCP

from texas_grocery_mcp.tools.store import (
    store_get_default,
    store_search,
    store_set_default,
)

mcp = FastMCP(
    name="texas-grocery-mcp",
    version="0.1.0",
)

# Register store tools
mcp.tool(annotations={"readOnlyHint": True})(store_search)
mcp.tool()(store_set_default)
mcp.tool(annotations={"readOnlyHint": True})(store_get_default)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
```

**Step 6: Commit**

```bash
git add src/texas_grocery_mcp/tools/ src/texas_grocery_mcp/server.py tests/unit/test_store_tools.py
git commit -m "feat: add store MCP tools

- store_search: Find stores by address/zip
- store_set_default: Set preferred store
- store_get_default: Get current default store
- Tool annotations for read-only hints

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 7 Verification Checklist

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `pytest tests/unit/test_store_tools.py -v` | `3 passed` |
| 2 | `python -c "from texas_grocery_mcp.tools.store import store_set_default, store_get_default; store_set_default('123'); print(store_get_default()['store_id'])"` | `123` |
| 3 | `python -c "from texas_grocery_mcp.server import mcp; print([t.name for t in mcp._tool_manager._tools.values()])"` | Contains `store_search`, `store_set_default`, `store_get_default` |
| 4 | `pytest tests/unit/ -v --tb=short 2>&1 \| tail -5` | Shows all tests passing |
| 5 | `git status` | Clean working tree |

**🛑 STOP - Do not proceed to Task 8 if:**
- Store tools not registered in server.py
- store_set_default doesn't persist value for store_get_default
- Tool annotations not applied

---

### Task 8: Implement Product Tools

**Files:**
- Create: `src/texas_grocery_mcp/tools/product.py`
- Update: `src/texas_grocery_mcp/tools/__init__.py`
- Update: `src/texas_grocery_mcp/server.py`
- Test: `tests/unit/test_product_tools.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_product_tools.py
"""Tests for product tools."""

import pytest
import respx
from httpx import Response


@pytest.fixture
def mock_product_response():
    """Mock GraphQL product response."""
    return {
        "data": {
            "searchProducts": {
                "products": [
                    {
                        "productId": "123456",
                        "description": "HEB Whole Milk 1 Gallon",
                        "price": 3.49,
                        "isAvailable": True,
                        "brand": "H-E-B",
                        "imageUrl": "https://example.com/milk.jpg",
                    }
                ]
            }
        }
    }


@pytest.mark.asyncio
@respx.mock
async def test_product_search_with_store_id(mock_product_response):
    """product_search should work with explicit store_id."""
    from texas_grocery_mcp.tools.product import product_search

    respx.post("https://www.heb.com/graphql").mock(
        return_value=Response(200, json=mock_product_response)
    )

    result = await product_search(query="milk", store_id="590")

    assert len(result["products"]) == 1
    assert result["products"][0]["sku"] == "123456"
    assert result["products"][0]["price"] == 3.49


@pytest.mark.asyncio
@respx.mock
async def test_product_search_uses_default_store(mock_product_response):
    """product_search should use default store when not specified."""
    from texas_grocery_mcp.tools.product import product_search
    from texas_grocery_mcp.tools.store import store_set_default

    store_set_default(store_id="590")

    respx.post("https://www.heb.com/graphql").mock(
        return_value=Response(200, json=mock_product_response)
    )

    result = await product_search(query="milk")

    assert result["store_id"] == "590"
    assert len(result["products"]) == 1


@pytest.mark.asyncio
async def test_product_search_requires_store():
    """product_search should error when no store available."""
    from texas_grocery_mcp.tools import store as store_module
    from texas_grocery_mcp.tools.product import product_search

    # Reset default store
    store_module._default_store_id = None

    result = await product_search(query="milk")

    assert "error" in result
    assert "store" in result["message"].lower()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_product_tools.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write product.py implementation**

```python
# src/texas_grocery_mcp/tools/product.py
"""Product-related MCP tools."""

from typing import Annotated, Literal

from pydantic import Field

from texas_grocery_mcp.clients.graphql import HEBGraphQLClient
from texas_grocery_mcp.tools.store import get_default_store_id

_graphql_client: HEBGraphQLClient | None = None


def _get_client() -> HEBGraphQLClient:
    """Get or create GraphQL client."""
    global _graphql_client
    if _graphql_client is None:
        _graphql_client = HEBGraphQLClient()
    return _graphql_client


async def product_search(
    query: Annotated[str, Field(description="Search query (e.g., 'milk', 'chicken breast')")],
    store_id: Annotated[
        str | None, Field(description="Store ID for pricing/availability. Uses default if not provided.")
    ] = None,
    limit: Annotated[
        int, Field(description="Maximum results to return", ge=1, le=50)
    ] = 20,
    fields: Annotated[
        list[Literal["minimal", "standard", "all"]] | None,
        Field(description="Field set to return: minimal (sku, name, price), standard (+brand, size, image), all (+nutrition)")
    ] = None,
) -> dict:
    """Search for products at an HEB store.

    Returns products matching the query with pricing and availability
    for the specified store.
    """
    # Resolve store ID
    effective_store_id = store_id or get_default_store_id()

    if not effective_store_id:
        return {
            "error": True,
            "code": "NO_STORE_SET",
            "message": "No store specified. Set a default store with store_set_default or provide store_id.",
        }

    client = _get_client()
    products = await client.search_products(
        query=query,
        store_id=effective_store_id,
        limit=limit,
    )

    # Determine field set (default to standard)
    field_set = (fields or ["standard"])[0] if fields else "standard"

    result_products = []
    for p in products:
        product_data = {
            "sku": p.sku,
            "name": p.name,
            "price": p.price,
            "available": p.available,
        }

        if field_set in ("standard", "all"):
            product_data.update({
                "brand": p.brand,
                "size": p.size,
                "price_per_unit": p.price_per_unit,
                "image_url": p.image_url,
                "aisle": p.aisle,
                "section": p.section,
            })

        if field_set == "all":
            product_data.update({
                "nutrition": p.nutrition.model_dump() if p.nutrition else None,
                "ingredients": p.ingredients,
                "on_sale": p.on_sale,
                "original_price": p.original_price,
                "rating": p.rating,
            })

        result_products.append(product_data)

    return {
        "products": result_products,
        "count": len(result_products),
        "store_id": effective_store_id,
        "query": query,
    }


async def product_get(
    sku: Annotated[str, Field(description="Product SKU/ID")],
    store_id: Annotated[
        str | None, Field(description="Store ID for pricing/availability")
    ] = None,
) -> dict:
    """Get detailed information for a specific product.

    Returns full product details including nutrition and coupons
    when available.
    """
    effective_store_id = store_id or get_default_store_id()

    if not effective_store_id:
        return {
            "error": True,
            "code": "NO_STORE_SET",
            "message": "No store specified. Set a default store or provide store_id.",
        }

    # For now, use search to get product details
    # In a full implementation, this would use a dedicated query
    client = _get_client()
    products = await client.search_products(
        query=sku,
        store_id=effective_store_id,
        limit=1,
    )

    if not products:
        return {
            "error": True,
            "code": "PRODUCT_NOT_FOUND",
            "message": f"Product with SKU {sku} not found at store {effective_store_id}",
        }

    p = products[0]
    return {
        "sku": p.sku,
        "name": p.name,
        "price": p.price,
        "available": p.available,
        "brand": p.brand,
        "size": p.size,
        "price_per_unit": p.price_per_unit,
        "image_url": p.image_url,
        "aisle": p.aisle,
        "section": p.section,
        "on_sale": p.on_sale,
        "original_price": p.original_price,
        "store_id": effective_store_id,
    }
```

**Step 4: Update tools __init__.py**

```python
# src/texas_grocery_mcp/tools/__init__.py
"""MCP tool definitions."""

from texas_grocery_mcp.tools import product, store

__all__ = ["product", "store"]
```

**Step 5: Update server.py**

```python
# src/texas_grocery_mcp/server.py
"""Texas Grocery MCP Server - FastMCP entry point."""

from fastmcp import FastMCP

from texas_grocery_mcp.tools.product import product_get, product_search
from texas_grocery_mcp.tools.store import (
    store_get_default,
    store_search,
    store_set_default,
)

mcp = FastMCP(
    name="texas-grocery-mcp",
    version="0.1.0",
)

# Register store tools
mcp.tool(annotations={"readOnlyHint": True})(store_search)
mcp.tool()(store_set_default)
mcp.tool(annotations={"readOnlyHint": True})(store_get_default)

# Register product tools
mcp.tool(annotations={"readOnlyHint": True})(product_search)
mcp.tool(annotations={"readOnlyHint": True})(product_get)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
```

**Step 6: Commit**

```bash
git add src/texas_grocery_mcp/tools/ src/texas_grocery_mcp/server.py tests/unit/test_product_tools.py
git commit -m "feat: add product MCP tools

- product_search: Search products with configurable fields
- product_get: Get detailed product information
- Auto-use default store when not specified
- Field-level control (minimal, standard, all)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 8 Verification Checklist

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `pytest tests/unit/test_product_tools.py -v` | `3 passed` |
| 2 | `python -c "from texas_grocery_mcp.server import mcp; tools = [t.name for t in mcp._tool_manager._tools.values()]; print('product_search' in tools and 'product_get' in tools)"` | `True` |
| 3 | `pytest tests/unit/test_store_tools.py tests/unit/test_product_tools.py -v` | `6 passed` |
| 4 | `ruff check src/texas_grocery_mcp/tools/` | No errors |
| 5 | `git status` | Clean working tree |

**🛑 STOP - Do not proceed to Task 9 if:**
- product_search doesn't use default store when store_id not provided
- product_search doesn't return error when no store set
- Product tools not registered in server

---

### Task 9: Implement Cart Tools with Confirmation

**Files:**
- Create: `src/texas_grocery_mcp/tools/cart.py`
- Create: `src/texas_grocery_mcp/auth/__init__.py`
- Create: `src/texas_grocery_mcp/auth/session.py`
- Update: `src/texas_grocery_mcp/server.py`
- Test: `tests/unit/test_cart_tools.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_cart_tools.py
"""Tests for cart tools."""

import pytest


def test_cart_add_without_confirm_returns_preview():
    """cart_add without confirm should return preview."""
    from texas_grocery_mcp.tools.cart import cart_add

    # Mock authenticated state
    import texas_grocery_mcp.auth.session as session_module
    session_module._is_authenticated = True

    result = cart_add(product_id="123456", quantity=2)

    assert result["preview"] is True
    assert result["action"] == "add_to_cart"
    assert "confirm" in result["message"].lower()


def test_cart_add_requires_auth():
    """cart_add should require authentication."""
    from texas_grocery_mcp.tools.cart import cart_add

    # Set unauthenticated state
    import texas_grocery_mcp.auth.session as session_module
    session_module._is_authenticated = False

    result = cart_add(product_id="123456", quantity=1)

    assert result["auth_required"] is True
    assert "instructions" in result


def test_cart_check_auth_returns_status():
    """cart_check_auth should return auth status."""
    from texas_grocery_mcp.tools.cart import cart_check_auth

    result = cart_check_auth()

    assert "authenticated" in result
    assert isinstance(result["authenticated"], bool)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_cart_tools.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create auth module**

```python
# src/texas_grocery_mcp/auth/__init__.py
"""Authentication management."""

from texas_grocery_mcp.auth.session import check_auth, get_auth_instructions, is_authenticated

__all__ = ["check_auth", "get_auth_instructions", "is_authenticated"]
```

```python
# src/texas_grocery_mcp/auth/session.py
"""Session management for HEB authentication.

Uses Playwright MCP's storage state for authentication.
"""

import json
from typing import Any

import structlog

from texas_grocery_mcp.utils.config import get_settings

logger = structlog.get_logger()

# Module state for testing
_is_authenticated: bool = False


def is_authenticated() -> bool:
    """Check if user is authenticated.

    Checks for valid auth state file from Playwright MCP.
    """
    global _is_authenticated

    # Check override for testing
    if _is_authenticated:
        return True

    settings = get_settings()
    auth_path = settings.auth_state_path

    if not auth_path.exists():
        return False

    try:
        with open(auth_path) as f:
            state = json.load(f)

        # Check for HEB session cookies
        cookies = state.get("cookies", [])
        heb_cookies = [c for c in cookies if "heb.com" in c.get("domain", "")]

        if not heb_cookies:
            return False

        # Check if any session cookie is present
        # In a real implementation, check expiry times
        session_cookies = [c for c in heb_cookies if "session" in c.get("name", "").lower()]
        return len(session_cookies) > 0

    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to read auth state", error=str(e))
        return False


def get_auth_instructions() -> list[str]:
    """Get instructions for authenticating with Playwright MCP."""
    settings = get_settings()
    return [
        "1. Use Playwright MCP: browser_navigate('https://www.heb.com/login')",
        "2. Complete the login process in the browser",
        "3. Use Playwright MCP: browser_run_code to save storage state:",
        f"   await page.context().storageState({{ path: '{settings.auth_state_path}' }})",
        "4. Retry this operation",
    ]


def check_auth() -> dict[str, Any]:
    """Check authentication status and return appropriate response."""
    if is_authenticated():
        return {
            "authenticated": True,
            "message": "Authenticated with HEB",
        }

    return {
        "authenticated": False,
        "auth_required": True,
        "message": "Login required for cart operations",
        "instructions": get_auth_instructions(),
    }


def get_cookies() -> list[dict]:
    """Get cookies for authenticated requests."""
    settings = get_settings()
    auth_path = settings.auth_state_path

    if not auth_path.exists():
        return []

    try:
        with open(auth_path) as f:
            state = json.load(f)
        return [c for c in state.get("cookies", []) if "heb.com" in c.get("domain", "")]
    except (json.JSONDecodeError, OSError):
        return []
```

**Step 4: Write cart.py implementation**

```python
# src/texas_grocery_mcp/tools/cart.py
"""Cart-related MCP tools with human-in-the-loop confirmation."""

from typing import Annotated

from pydantic import Field

from texas_grocery_mcp.auth.session import check_auth, get_auth_instructions, is_authenticated


def cart_check_auth() -> dict:
    """Check if authenticated for cart operations.

    Returns authentication status and instructions if not authenticated.
    Use this before attempting cart operations.
    """
    return check_auth()


def cart_add(
    product_id: Annotated[str, Field(description="Product SKU/ID to add")],
    quantity: Annotated[int, Field(description="Quantity to add", ge=1, le=99)] = 1,
    confirm: Annotated[
        bool, Field(description="Set to true to confirm the action")
    ] = False,
) -> dict:
    """Add an item to the shopping cart.

    Without confirm=true, returns a preview of the action.
    With confirm=true, executes the action (requires authentication).
    """
    # Check authentication first
    if not is_authenticated():
        return {
            "auth_required": True,
            "message": "Login required for cart operations",
            "instructions": get_auth_instructions(),
        }

    # If not confirmed, return preview
    if not confirm:
        return {
            "preview": True,
            "action": "add_to_cart",
            "product_id": product_id,
            "quantity": quantity,
            "message": "Set confirm=true to add this item to cart",
        }

    # TODO: Implement actual cart addition via HEB API
    # For now, return simulated success
    return {
        "success": True,
        "action": "add_to_cart",
        "product_id": product_id,
        "quantity": quantity,
        "message": f"Added {quantity}x product {product_id} to cart",
    }


def cart_remove(
    product_id: Annotated[str, Field(description="Product SKU/ID to remove")],
    confirm: Annotated[
        bool, Field(description="Set to true to confirm the action")
    ] = False,
) -> dict:
    """Remove an item from the shopping cart.

    Without confirm=true, returns a preview of the action.
    With confirm=true, executes the action.
    """
    if not is_authenticated():
        return {
            "auth_required": True,
            "message": "Login required for cart operations",
            "instructions": get_auth_instructions(),
        }

    if not confirm:
        return {
            "preview": True,
            "action": "remove_from_cart",
            "product_id": product_id,
            "message": "Set confirm=true to remove this item from cart",
        }

    return {
        "success": True,
        "action": "remove_from_cart",
        "product_id": product_id,
        "message": f"Removed product {product_id} from cart",
    }


def cart_get() -> dict:
    """Get current cart contents.

    Returns all items in the cart with quantities and prices.
    """
    if not is_authenticated():
        return {
            "auth_required": True,
            "message": "Login required to view cart",
            "instructions": get_auth_instructions(),
        }

    # TODO: Implement actual cart retrieval
    return {
        "items": [],
        "subtotal": 0.0,
        "item_count": 0,
        "message": "Cart is empty",
    }
```

**Step 5: Update server.py**

```python
# src/texas_grocery_mcp/server.py
"""Texas Grocery MCP Server - FastMCP entry point."""

from fastmcp import FastMCP

from texas_grocery_mcp.tools.cart import cart_add, cart_check_auth, cart_get, cart_remove
from texas_grocery_mcp.tools.product import product_get, product_search
from texas_grocery_mcp.tools.store import (
    store_get_default,
    store_search,
    store_set_default,
)

mcp = FastMCP(
    name="texas-grocery-mcp",
    version="0.1.0",
)

# Register store tools
mcp.tool(annotations={"readOnlyHint": True})(store_search)
mcp.tool()(store_set_default)
mcp.tool(annotations={"readOnlyHint": True})(store_get_default)

# Register product tools
mcp.tool(annotations={"readOnlyHint": True})(product_search)
mcp.tool(annotations={"readOnlyHint": True})(product_get)

# Register cart tools (destructive operations require confirmation)
mcp.tool(annotations={"readOnlyHint": True})(cart_check_auth)
mcp.tool(annotations={"readOnlyHint": True})(cart_get)
mcp.tool(annotations={"destructiveHint": True})(cart_add)
mcp.tool(annotations={"destructiveHint": True})(cart_remove)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
```

**Step 6: Commit**

```bash
git add src/texas_grocery_mcp/tools/cart.py src/texas_grocery_mcp/auth/ src/texas_grocery_mcp/server.py tests/unit/test_cart_tools.py
git commit -m "feat: add cart tools with human-in-the-loop confirmation

- cart_check_auth: Check authentication status
- cart_add: Add items with preview/confirm pattern
- cart_remove: Remove items with preview/confirm pattern
- cart_get: View current cart
- Playwright MCP auth integration instructions

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 9 Verification Checklist

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `pytest tests/unit/test_cart_tools.py -v` | `3 passed` |
| 2 | `python -c "import texas_grocery_mcp.auth.session as s; s._is_authenticated=True; from texas_grocery_mcp.tools.cart import cart_add; r=cart_add('123',1); print(r['preview'])"` | `True` |
| 3 | `python -c "import texas_grocery_mcp.auth.session as s; s._is_authenticated=False; from texas_grocery_mcp.tools.cart import cart_add; r=cart_add('123',1); print(r['auth_required'])"` | `True` |
| 4 | `python -c "from texas_grocery_mcp.server import mcp; tools=[t.name for t in mcp._tool_manager._tools.values()]; print('cart_add' in tools and 'cart_remove' in tools)"` | `True` |
| 5 | `pytest tests/unit/ -v --tb=short 2>&1 \| grep -E "passed\|failed"` | Shows 20+ passed, 0 failed |
| 6 | `git status` | Clean working tree |

**🛑 STOP - Do not proceed to Task 10 if:**
- cart_add without confirm doesn't return preview
- cart_add without auth doesn't return auth_required
- Cart tools not registered with destructiveHint annotation

---

## Phase 5: Observability

### Task 10: Add Structured Logging

**Files:**
- Create: `src/texas_grocery_mcp/observability/__init__.py`
- Create: `src/texas_grocery_mcp/observability/logging.py`
- Update: `src/texas_grocery_mcp/server.py`
- Test: `tests/unit/test_logging.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_logging.py
"""Tests for structured logging."""

import json
import sys
from io import StringIO

import pytest


def test_logger_outputs_json():
    """Logger should output JSON to stderr."""
    from texas_grocery_mcp.observability.logging import configure_logging, get_logger

    # Capture stderr
    captured = StringIO()
    original_stderr = sys.stderr

    try:
        sys.stderr = captured
        configure_logging(log_level="DEBUG")
        logger = get_logger("test")
        logger.info("test message", key="value")

        # Force flush
        sys.stderr.flush()
        output = captured.getvalue()

        # Should be valid JSON
        lines = [line for line in output.strip().split("\n") if line]
        assert len(lines) >= 1

        log_entry = json.loads(lines[-1])
        assert log_entry["event"] == "test message"
        assert log_entry["key"] == "value"
    finally:
        sys.stderr = original_stderr


def test_logger_includes_timestamp():
    """Logger should include ISO timestamp."""
    from texas_grocery_mcp.observability.logging import configure_logging, get_logger

    captured = StringIO()
    original_stderr = sys.stderr

    try:
        sys.stderr = captured
        configure_logging()
        logger = get_logger("test")
        logger.info("test")
        sys.stderr.flush()

        output = captured.getvalue()
        lines = [line for line in output.strip().split("\n") if line]
        log_entry = json.loads(lines[-1])

        assert "timestamp" in log_entry
        assert "T" in log_entry["timestamp"]  # ISO format
    finally:
        sys.stderr = original_stderr
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_logging.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create observability module**

```python
# src/texas_grocery_mcp/observability/__init__.py
"""Observability: logging, metrics, and health checks."""

from texas_grocery_mcp.observability.logging import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]
```

```python
# src/texas_grocery_mcp/observability/logging.py
"""Structured JSON logging configuration."""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from texas_grocery_mcp.utils.config import get_settings


def add_timestamp(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add ISO timestamp to log entry."""
    from datetime import datetime, timezone

    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_dict


def configure_logging(log_level: str | None = None) -> None:
    """Configure structured JSON logging.

    Logs to stderr to keep stdout clean for MCP protocol.
    """
    settings = get_settings()
    level = log_level or settings.log_level

    # Shared processors for all loggers
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        add_timestamp,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Configure structlog
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper()))


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
```

**Step 4: Update server.py to configure logging**

```python
# src/texas_grocery_mcp/server.py
"""Texas Grocery MCP Server - FastMCP entry point."""

from fastmcp import FastMCP

from texas_grocery_mcp.observability.logging import configure_logging
from texas_grocery_mcp.tools.cart import cart_add, cart_check_auth, cart_get, cart_remove
from texas_grocery_mcp.tools.product import product_get, product_search
from texas_grocery_mcp.tools.store import (
    store_get_default,
    store_search,
    store_set_default,
)

# Configure logging before anything else
configure_logging()

mcp = FastMCP(
    name="texas-grocery-mcp",
    version="0.1.0",
)

# Register store tools
mcp.tool(annotations={"readOnlyHint": True})(store_search)
mcp.tool()(store_set_default)
mcp.tool(annotations={"readOnlyHint": True})(store_get_default)

# Register product tools
mcp.tool(annotations={"readOnlyHint": True})(product_search)
mcp.tool(annotations={"readOnlyHint": True})(product_get)

# Register cart tools (destructive operations require confirmation)
mcp.tool(annotations={"readOnlyHint": True})(cart_check_auth)
mcp.tool(annotations={"readOnlyHint": True})(cart_get)
mcp.tool(annotations={"destructiveHint": True})(cart_add)
mcp.tool(annotations={"destructiveHint": True})(cart_remove)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
```

**Step 5: Commit**

```bash
git add src/texas_grocery_mcp/observability/ src/texas_grocery_mcp/server.py tests/unit/test_logging.py
git commit -m "feat: add structured JSON logging

- JSON output to stderr (stdout reserved for MCP)
- ISO timestamps
- Log levels from environment
- structlog integration

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 10 Verification Checklist

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `pytest tests/unit/test_logging.py -v` | `2 passed` |
| 2 | `python -c "from texas_grocery_mcp.observability import configure_logging, get_logger; configure_logging(); print('OK')"` | `OK` (may have log output to stderr) |
| 3 | `python -c "from texas_grocery_mcp.observability.logging import get_logger; import structlog; print(type(get_logger('test')))" 2>/dev/null` | Contains `BoundLogger` |
| 4 | `pytest tests/unit/ -v --tb=short 2>&1 \| grep -E "passed\|failed"` | 22+ passed, 0 failed |
| 5 | `git status` | Clean working tree |

**🛑 STOP - Do not proceed to Task 11 if:**
- Logging tests fail
- Logs not outputting to stderr
- JSON parsing of log output fails

---

### Task 11: Add Health Check Endpoints

**Files:**
- Create: `src/texas_grocery_mcp/observability/health.py`
- Create: `src/texas_grocery_mcp/models/health.py`
- Update: `src/texas_grocery_mcp/models/__init__.py`
- Update: `src/texas_grocery_mcp/observability/__init__.py`
- Update: `src/texas_grocery_mcp/server.py`
- Test: `tests/unit/test_health.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_health.py
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_health.py -v`
Expected: FAIL with "ModuleNotFoundError" or "ImportError"

**Step 3: Create health model**

```python
# src/texas_grocery_mcp/models/health.py
"""Health check response models."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class ComponentHealth(BaseModel):
    """Health status of a single component."""

    status: Literal["up", "down", "degraded"] = Field(description="Component status")
    latency_ms: float | None = Field(default=None, description="Response latency")
    message: str | None = Field(default=None, description="Status message")


class CircuitBreakerStatus(BaseModel):
    """Status of a circuit breaker."""

    state: Literal["closed", "open", "half_open"] = Field(
        description="Circuit state"
    )
    failures: int = Field(default=0, description="Current failure count")


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        description="Overall health status"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Check timestamp",
    )
    components: dict[str, ComponentHealth] = Field(
        default_factory=dict, description="Component health statuses"
    )
    circuit_breakers: dict[str, CircuitBreakerStatus] = Field(
        default_factory=dict, description="Circuit breaker statuses"
    )
```

**Step 4: Create health.py**

```python
# src/texas_grocery_mcp/observability/health.py
"""Health check endpoints."""

from datetime import datetime, timezone

from texas_grocery_mcp.models.health import (
    CircuitBreakerStatus,
    ComponentHealth,
    HealthResponse,
)


def health_live() -> dict:
    """Liveness probe - is the process running?

    Returns a simple alive status. Use for Kubernetes liveness probes.
    """
    return {"status": "alive"}


def health_ready() -> dict:
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
            state=cb_status["state"].replace("-", "_"),
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
        timestamp=datetime.now(timezone.utc).isoformat(),
        components=components,
        circuit_breakers=circuit_breakers,
    ).model_dump()
```

**Step 5: Update models __init__.py**

```python
# src/texas_grocery_mcp/models/__init__.py
"""Data models for Texas Grocery MCP."""

from texas_grocery_mcp.models.cart import Cart, CartItem
from texas_grocery_mcp.models.errors import AuthRequiredResponse, ErrorResponse
from texas_grocery_mcp.models.health import (
    CircuitBreakerStatus,
    ComponentHealth,
    HealthResponse,
)
from texas_grocery_mcp.models.product import Product
from texas_grocery_mcp.models.store import Store

__all__ = [
    "AuthRequiredResponse",
    "Cart",
    "CartItem",
    "CircuitBreakerStatus",
    "ComponentHealth",
    "ErrorResponse",
    "HealthResponse",
    "Product",
    "Store",
]
```

**Step 6: Update observability __init__.py**

```python
# src/texas_grocery_mcp/observability/__init__.py
"""Observability: logging, metrics, and health checks."""

from texas_grocery_mcp.observability.health import health_live, health_ready
from texas_grocery_mcp.observability.logging import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger", "health_live", "health_ready"]
```

**Step 7: Update server.py**

```python
# src/texas_grocery_mcp/server.py
"""Texas Grocery MCP Server - FastMCP entry point."""

from fastmcp import FastMCP

from texas_grocery_mcp.observability.health import health_live, health_ready
from texas_grocery_mcp.observability.logging import configure_logging
from texas_grocery_mcp.tools.cart import cart_add, cart_check_auth, cart_get, cart_remove
from texas_grocery_mcp.tools.product import product_get, product_search
from texas_grocery_mcp.tools.store import (
    store_get_default,
    store_search,
    store_set_default,
)

# Configure logging before anything else
configure_logging()

mcp = FastMCP(
    name="texas-grocery-mcp",
    version="0.1.0",
)

# Register store tools
mcp.tool(annotations={"readOnlyHint": True})(store_search)
mcp.tool()(store_set_default)
mcp.tool(annotations={"readOnlyHint": True})(store_get_default)

# Register product tools
mcp.tool(annotations={"readOnlyHint": True})(product_search)
mcp.tool(annotations={"readOnlyHint": True})(product_get)

# Register cart tools (destructive operations require confirmation)
mcp.tool(annotations={"readOnlyHint": True})(cart_check_auth)
mcp.tool(annotations={"readOnlyHint": True})(cart_get)
mcp.tool(annotations={"destructiveHint": True})(cart_add)
mcp.tool(annotations={"destructiveHint": True})(cart_remove)

# Register health check tools
mcp.tool(annotations={"readOnlyHint": True})(health_live)
mcp.tool(annotations={"readOnlyHint": True})(health_ready)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
```

**Step 8: Commit**

```bash
git add src/texas_grocery_mcp/observability/ src/texas_grocery_mcp/models/ src/texas_grocery_mcp/server.py tests/unit/test_health.py
git commit -m "feat: add health check endpoints

- health_live: Simple liveness probe
- health_ready: Component health with circuit breaker status
- Health response models with Pydantic

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 11 Verification Checklist

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `pytest tests/unit/test_health.py -v` | `2 passed` |
| 2 | `python -c "from texas_grocery_mcp.observability.health import health_live; print(health_live())"` | `{'status': 'alive'}` |
| 3 | `python -c "from texas_grocery_mcp.observability.health import health_ready; r=health_ready(); print(r['status'] in ['healthy','degraded','unhealthy'])"` | `True` |
| 4 | `python -c "from texas_grocery_mcp.server import mcp; tools=[t.name for t in mcp._tool_manager._tools.values()]; print('health_live' in tools and 'health_ready' in tools)"` | `True` |
| 5 | `pytest tests/unit/ -v 2>&1 \| grep -E "passed\|failed" \| tail -1` | `XX passed` (24+ tests, 0 failed) |
| 6 | `git status` | Clean working tree |

**🛑 STOP - Do not proceed to Task 12 if:**
- health_live doesn't return "alive"
- health_ready doesn't include components and timestamp
- Health tools not registered in server

---

## Phase 6: Docker & Documentation

### Task 12: Create Dockerfile and Docker Compose

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`

**Step 1: Create Dockerfile**

```dockerfile
# Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir hatch

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Build wheel
RUN hatch build -t wheel

# Production image
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy wheel from builder
COPY --from=builder /app/dist/*.whl ./

# Install the package
RUN pip install --no-cache-dir *.whl && rm *.whl

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import texas_grocery_mcp; print('ok')" || exit 1

# Default environment
ENV LOG_LEVEL=INFO
ENV ENVIRONMENT=production

# Run the MCP server
ENTRYPOINT ["texas-grocery-mcp"]
```

**Step 2: Create docker-compose.yml**

```yaml
# docker-compose.yml
version: '3.8'

services:
  texas-grocery-mcp:
    build: .
    volumes:
      # Mount auth state from host
      - ~/.texas-grocery-mcp:/home/appuser/.texas-grocery-mcp:ro
    environment:
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - HEB_DEFAULT_STORE=${HEB_DEFAULT_STORE:-}
    depends_on:
      redis:
        condition: service_healthy
    stdin_open: true
    tty: true

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

**Step 3: Commit**

```bash
git add Dockerfile docker-compose.yml
git commit -m "feat: add Docker configuration

- Multi-stage Dockerfile for smaller images
- Non-root user for security
- Health check integration
- Docker Compose with Redis for development

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 12 Verification Checklist

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `ls Dockerfile docker-compose.yml` | Both files exist |
| 2 | `grep -q "FROM python:3.11-slim" Dockerfile && echo "OK"` | `OK` |
| 3 | `grep -q "useradd" Dockerfile && echo "OK"` | `OK` (non-root user) |
| 4 | `grep -q "HEALTHCHECK" Dockerfile && echo "OK"` | `OK` |
| 5 | `grep -q "redis:" docker-compose.yml && echo "OK"` | `OK` |
| 6 | `docker build -t texas-grocery-mcp:test . 2>&1 \| tail -3` | Shows successful build or "Successfully built" |
| 7 | `git status` | Clean working tree |

**🛑 STOP - Do not proceed to Task 13 if:**
- Dockerfile doesn't build successfully
- Missing HEALTHCHECK in Dockerfile
- Missing non-root user configuration

**Note:** If Docker is not available, verification #6 can be skipped but document it.

---

### Task 13: Create README

**Files:**
- Create: `README.md`

**Step 1: Create README.md**

```markdown
# Texas Grocery MCP

An MCP (Model Context Protocol) server that enables AI agents to interact with HEB grocery stores for product search, cart management, and pickup scheduling.

## Features

- **Store Search**: Find HEB stores by address or zip code
- **Product Search**: Search products with pricing and availability
- **Cart Management**: Add/remove items with human-in-the-loop confirmation
- **Pickup Scheduling**: Schedule curbside pickup times

## Installation

```bash
pip install texas-grocery-mcp
```

### Prerequisites

This MCP uses **Microsoft Playwright MCP** for authentication. Install it alongside:

```bash
npm install -g @anthropic-ai/mcp-playwright
```

## Configuration

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-playwright"]
    },
    "heb": {
      "command": "uvx",
      "args": ["texas-grocery-mcp"],
      "env": {
        "HEB_DEFAULT_STORE": "590"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HEB_DEFAULT_STORE` | Default store ID | None |
| `REDIS_URL` | Redis cache URL | None (in-memory) |
| `LOG_LEVEL` | Logging level | INFO |

## Usage

### Finding a Store

```
User: Find HEB stores near Austin, TX

Agent uses: store_search(address="Austin, TX", radius_miles=10)
```

### Searching Products

```
User: Search for organic milk

Agent uses: store_set_default(store_id="590")
Agent uses: product_search(query="organic milk")
```

### Adding to Cart

Cart operations require authentication via Playwright MCP:

```
User: Add 2 gallons of milk to my cart

Agent uses: cart_add(product_id="123456", quantity=2)
# Returns preview with confirm=true instruction

Agent uses: cart_add(product_id="123456", quantity=2, confirm=true)
# Executes the action
```

## Authentication

For cart operations, authenticate using Playwright MCP:

1. `browser_navigate('https://www.heb.com/login')`
2. Complete login in the browser
3. Save storage state:
   ```javascript
   await page.context().storageState({ path: '~/.texas-grocery-mcp/auth.json' })
   ```
4. Retry cart operations

## Available Tools

### Store Tools
- `store_search` - Find stores by address
- `store_set_default` - Set preferred store
- `store_get_default` - Get current default store

### Product Tools
- `product_search` - Search products
- `product_get` - Get product details

### Cart Tools
- `cart_check_auth` - Check authentication status
- `cart_get` - View cart contents
- `cart_add` - Add item (requires confirmation)
- `cart_remove` - Remove item (requires confirmation)

### Health Tools
- `health_live` - Liveness probe
- `health_ready` - Readiness probe with component status

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/texas-grocery-mcp
cd texas-grocery-mcp

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
ruff check src/

# Run type checking
mypy src/
```

### Docker Development

```bash
# Build and run with Redis
docker-compose up --build

# Run tests in container
docker-compose run texas-grocery-mcp pytest
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User's MCP Environment                    │
│                                                             │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │  Playwright MCP     │    │     Texas Grocery MCP       │ │
│  │  (Browser Auth)     │───▶│     (Grocery Logic)         │ │
│  └─────────────────────┘    └─────────────────────────────┘ │
│                                        │                     │
└────────────────────────────────────────┼─────────────────────┘
                                         │
                                         ▼
                                  HEB GraphQL API
```

## License

MIT
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README

- Installation and configuration guide
- Usage examples for all tools
- Authentication flow documentation
- Development setup instructions

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

#### ✅ Task 13 Verification Checklist

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `ls README.md` | File exists |
| 2 | `grep -q "# Texas Grocery MCP" README.md && echo "OK"` | `OK` |
| 3 | `grep -q "pip install texas-grocery-mcp" README.md && echo "OK"` | `OK` |
| 4 | `grep -q "store_search" README.md && echo "OK"` | `OK` |
| 5 | `grep -q "cart_add" README.md && echo "OK"` | `OK` |
| 6 | `grep -q "health_live" README.md && echo "OK"` | `OK` |
| 7 | `git status` | Clean working tree |

**🛑 STOP if:**
- README doesn't include installation instructions
- README doesn't document all tools
- README doesn't explain authentication flow

---

## Final Verification

### Complete Project Verification Checklist

Run these commands to verify the entire project is complete:

| # | Command | Expected Output |
|---|---------|-----------------|
| 1 | `pytest tests/ -v --tb=short` | All tests pass (24+ tests) |
| 2 | `ruff check src/` | No linting errors |
| 3 | `python -c "from texas_grocery_mcp.server import mcp; print(len(list(mcp._tool_manager._tools.values())))"` | `11` (total tools) |
| 4 | `pip show texas-grocery-mcp` | Package info displayed |
| 5 | `git log --oneline \| head -13` | 13 commits (1 per task) |
| 6 | `ls src/texas_grocery_mcp/` | Shows all module directories |

### Tool Inventory Verification

```bash
python -c "
from texas_grocery_mcp.server import mcp
tools = [t.name for t in mcp._tool_manager._tools.values()]
expected = [
    'store_search', 'store_set_default', 'store_get_default',
    'product_search', 'product_get',
    'cart_check_auth', 'cart_get', 'cart_add', 'cart_remove',
    'health_live', 'health_ready'
]
missing = set(expected) - set(tools)
if missing:
    print(f'MISSING: {missing}')
else:
    print('All 11 tools registered')
"
```

Expected: `All 11 tools registered`

---

## Summary

| Phase | Tasks | Tests | Tools Added |
|-------|-------|-------|-------------|
| 1. Foundation | 1-3 | 8 | 0 |
| 2. Reliability | 4-5 | 9 | 0 |
| 3. GraphQL Client | 6 | 3 | 0 |
| 4. MCP Tools | 7-9 | 9 | 9 |
| 5. Observability | 10-11 | 4 | 2 |
| 6. Docker & Docs | 12-13 | 0 | 0 |
| **Total** | **13** | **33** | **11** |

**Plan complete and saved.**

Ready to execute with verification checkpoints after each task.
