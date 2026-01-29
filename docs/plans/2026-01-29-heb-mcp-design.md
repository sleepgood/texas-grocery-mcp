# Texas Grocery MCP Server Design

> **Project Name:** `texas-grocery-mcp`
> **PyPI Package:** `texas-grocery-mcp`
> **Python Import:** `texas_grocery_mcp`

**Date:** 2026-01-29
**Status:** Approved
**Last Updated:** 2026-01-29 (Refined based on MCP ecosystem research)

## Overview

An MCP (Model Context Protocol) server that enables AI agents to interact with HEB grocery stores for meal planning, shopping list creation, price comparison, and order placement.

### Goals

- Enable AI agents to search HEB products, check prices and inventory
- Find item locations within stores
- Discover coupons and cheaper alternatives
- Manage shopping carts and schedule pickup orders
- Work reliably with fallback mechanisms when primary APIs fail

### Non-Goals (for MVP)

- Path optimization through stores (future enhancement)
- Delivery scheduling (pickup only for now)
- Multiple store carts simultaneously
- Price history tracking

## Architecture

This design uses a **dual-MCP architecture** where authentication is handled by a separate browser automation MCP (Microsoft Playwright MCP), keeping the Texas Grocery MCP focused on grocery domain logic.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           User's MCP Environment                         │
│                                                                         │
│  ┌─────────────────────────┐         ┌─────────────────────────────┐   │
│  │  Microsoft Playwright   │         │        Texas Grocery MCP Server       │   │
│  │  MCP (External)         │         │        (This Project)       │   │
│  │                         │         │                             │   │
│  │  - Browser automation   │         │  ┌───────────────────────┐  │   │
│  │  - Login flows          │  auth   │  │    Health & Metrics   │  │   │
│  │  - CAPTCHA handling     │  state  │  │  /health/* /metrics   │  │   │
│  │  - 2FA support          │ ──────▶ │  └───────────────────────┘  │   │
│  │                         │  .json  │                             │   │
│  │  Exports:               │         │  ┌─────────┬─────────┬───┐  │   │
│  │  ~/.texas-grocery-mcp/auth.json   │         │  │ Store   │ Product │...│  │   │
│  └─────────────────────────┘         │  │ Tools   │ Tools   │   │  │   │
│                                      │  └────┬────┴────┬────┴───┘  │   │
│                                      │       │         │           │   │
│                                      │  ┌────▼─────────▼────────┐  │   │
│                                      │  │    Request Layer      │  │   │
│                                      │  │ Circuit Breaker →     │  │   │
│                                      │  │ Retry → Fallback      │  │   │
│                                      │  └────┬─────────┬────────┘  │   │
│                                      │       │         │           │   │
│                                      │  ┌────▼────┐ ┌──▼───────┐  │   │
│                                      │  │ GraphQL │ │ HTML     │  │   │
│                                      │  │ Client  │ │ Scraper  │  │   │
│                                      │  └─────────┘ └──────────┘  │   │
│                                      └─────────────────────────────┘   │
│                                                   │                     │
└───────────────────────────────────────────────────┼─────────────────────┘
                                                    │
                                                    ▼
                                            HEB APIs & Website
                                            - www.heb.com/graphql
                                            - www.heb.com
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | Python + FastMCP | Ecosystem standard (70% of MCPs), fastest development |
| Browser Auth | Microsoft Playwright MCP | Separation of concerns; 26.4k stars; Microsoft-maintained |
| Primary Data Source | HEB GraphQL API | Publicly accessible, no auth for reads, structured data |
| Auth State Storage | JSON file (`~/.texas-grocery-mcp/auth.json`) | Portable; works with Playwright MCP's storage state export |
| Fallback Strategy | GraphQL → Cache → HTML Scraper | Multi-layer resilience |
| Caching | Redis with TTLs | Production performance; 80%+ cache hit target |
| Transport | stdio (local) | Avoids OAuth 2.1 requirement for HTTP transports |

### Why Dual-MCP Architecture?

| Benefit | Explanation |
|---------|-------------|
| **Lighter Texas Grocery MCP** | No bundled browser engine (~200MB smaller) |
| **Better maintained auth** | Microsoft maintains Playwright MCP separately |
| **Reusable pattern** | Same auth flow works for other grocery sites |
| **Cleaner separation** | Texas Grocery MCP focuses purely on grocery domain logic |
| **Easier testing** | Can mock auth state without browser |

### Prerequisites

Users must install Microsoft Playwright MCP alongside Texas Grocery MCP:

```bash
# Install Playwright MCP (one-time)
npm install -g @anthropic-ai/mcp-playwright

# Install Texas Grocery MCP
pip install texas-grocery-mcp
```

## API Endpoints

### HEB GraphQL

**Primary Endpoint:** `https://www.heb.com/graphql`
**Alternate:** `https://api-edge.heb-ecom-api.hebdigital-prd.com/graphql`

**Known Operations:**
- `StoreSearch` - Find stores by address + radius
- Category browse - Products by category + store
- Product search - Search with pricing, availability, images

**Authentication:** Not required for read operations.

## MCP Tools

All tools include **annotations** for safety (per MCP best practices):
- `readOnlyHint`: Tool only reads data, no side effects
- `destructiveHint`: Tool modifies state (cart, orders)
- `requiresConfirmation`: Tool requires explicit `confirm=true` parameter

### Store Tools

| Tool | Description | Auth | Annotations |
|------|-------------|------|-------------|
| `store_search` | Find stores by address/zip + radius | No | readOnly |
| `store_get` | Get details for a specific store | No | readOnly |
| `store_set_default` | Set preferred store for future calls | No | - |
| `store_get_default` | Get currently set default store | No | readOnly |

### Product Tools

| Tool | Description | Auth | Annotations |
|------|-------------|------|-------------|
| `product_search` | Search products by query, with configurable fields | No | readOnly |
| `product_get` | Get full details for a product by SKU/ID | No | readOnly |
| `product_browse_category` | Browse products in a category | No | readOnly |
| `product_check_inventory` | Check availability at a store | No | readOnly |
| `product_get_location` | Get aisle/section in store | No | readOnly |
| `product_find_alternatives` | Find similar/cheaper products | No | readOnly |

### Coupon Tools

| Tool | Description | Auth | Annotations |
|------|-------------|------|-------------|
| `coupon_search` | Search coupons by product/category | No | readOnly |
| `coupon_browse` | Browse all current deals | No | readOnly |
| `coupon_check_applicable` | Check which coupons apply to a cart | No | readOnly |

### Cart Tools

| Tool | Description | Auth | Annotations |
|------|-------------|------|-------------|
| `cart_check_auth` | Check if authenticated, return instructions if not | No | readOnly |
| `cart_get` | View current cart contents | Yes | readOnly |
| `cart_add` | Add item(s) to cart | Yes | **destructive, requiresConfirmation** |
| `cart_remove` | Remove item from cart | Yes | **destructive, requiresConfirmation** |
| `cart_update_quantity` | Change quantity of cart item | Yes | **destructive, requiresConfirmation** |
| `cart_get_coupon_suggestions` | Get applicable coupons for current cart | Yes | readOnly |
| `cart_apply_coupon` | Apply a coupon code | Yes | destructive |

### Pickup Tools

| Tool | Description | Auth | Annotations |
|------|-------------|------|-------------|
| `pickup_get_slots` | Get available pickup time slots | Yes | readOnly |
| `pickup_schedule` | Book a pickup slot | Yes | **destructive, requiresConfirmation** |

**Total: 19 tools** across 5 domains.

### Human-in-the-Loop Confirmation

Tools marked `requiresConfirmation` require explicit confirmation before execution:

```python
# Without confirmation - returns preview only
cart_add(product_id="123456", quantity=2)
# Returns:
{
  "preview": true,
  "action": "add_to_cart",
  "product": {"name": "HEB Milk 1 Gallon", "price": 3.49},
  "quantity": 2,
  "estimated_subtotal": 6.98,
  "message": "Set confirm=true to add this item to cart"
}

# With confirmation - executes the action
cart_add(product_id="123456", quantity=2, confirm=true)
# Returns:
{
  "success": true,
  "cart": {...}
}
```

This prevents AI agents from making unintended purchases.

## Data Models

### Store

```python
{
  "store_id": "590",
  "name": "H-E-B Mueller",
  "address": "1801 E 51st St, Austin, TX 78723",
  "phone": "(512) 929-7752",
  "distance_miles": 2.3,
  "hours": {"mon": "6am-11pm", ...},
  "services": ["curbside", "delivery", "pharmacy"]
}
```

### Product

Configurable fields - caller specifies what to return.

```python
{
  # Minimal fields (always returned)
  "sku": "123456",
  "name": "Hill Country Fare Chicken Breast",
  "price": 4.99,
  "available": true,

  # Standard fields (opt-in)
  "brand": "Hill Country Fare",
  "size": "1 lb",
  "price_per_unit": "$4.99/lb",
  "image_url": "https://...",
  "location": {"aisle": "5", "section": "Meat"},

  # Comprehensive fields (opt-in)
  "nutrition": {"calories": 120, "protein": "26g", ...},
  "ingredients": ["chicken breast", ...],
  "on_sale": true,
  "original_price": 6.49,
  "rating": 4.5,
  "coupons": [{"code": "SAVE1", "discount": "$1 off"}]
}
```

### Cart

```python
{
  "items": [
    {"sku": "123456", "name": "...", "quantity": 2, "price": 4.99, "subtotal": 9.98}
  ],
  "subtotal": 45.67,
  "coupons_applied": [{"code": "SAVE5", "discount": 5.00}],
  "estimated_total": 40.67,
  "applicable_coupons": [{"code": "FRESH10", "potential_savings": 4.50}]
}
```

### PickupSlot

```python
{
  "slot_id": "abc123",
  "date": "2026-01-30",
  "time_start": "10:00 AM",
  "time_end": "11:00 AM",
  "available": true
}
```

### Error

```python
{
  "error": true,
  "code": "HEB_UNAVAILABLE",
  "message": "Could not reach HEB after retries and fallback",
  "details": {
    "graphql_error": "Connection timeout",
    "fallback_error": "CAPTCHA detected"
  },
  "suggestions": ["Try again in a few minutes", "Check if heb.com is accessible"]
}
```

## Request Patterns

### Configurable Fields

```python
# Minimal request - just the basics
product_search(query="chicken breast", store_id="590")
# Returns: sku, name, price, available

# Standard request - common fields
product_search(
  query="chicken breast",
  store_id="590",
  fields=["brand", "size", "price_per_unit", "image_url", "location"]
)

# Full request - everything
product_search(
  query="chicken breast",
  store_id="590",
  fields=["all"]
)
```

### Store Override

```python
# Uses default store (set previously)
product_search(query="milk")

# Override for this call only
product_search(query="milk", store_id="123")
```

## Error Handling

```
Request
    │
    ▼
Circuit Breaker Check ──── Open ──▶ Return cached data or error
    │
    │ Closed/Half-Open
    ▼
Try GraphQL API ──── Success ──▶ Cache result → Return data
    │
    │ Fail
    ▼
Retry (3x with exponential backoff + jitter) ──── Success ──▶ Return data
    │
    │ Still failing
    ▼
Try Cache (stale-while-revalidate) ──── Hit ──▶ Return cached (with "source": "cache")
    │
    │ Miss
    ▼
Fallback to HTML scraping ──── Success ──▶ Return data (with "source": "fallback")
    │
    │ Fail
    ▼
Return classified error with retry metadata
```

### Error Response Model

Errors are classified and include actionable metadata:

```python
{
  "error": true,
  "code": "HEB_API_RATE_LIMITED",
  "category": "external",           # client | server | external
  "message": "HEB API rate limit exceeded",
  "retry_after_seconds": 60,        # When to retry (if applicable)
  "fallback_available": true,       # Was fallback attempted?
  "fallback_source": "cache",       # What fallback was used
  "suggestions": [
    "Wait 60 seconds before retrying",
    "Cached data from 5 minutes ago is available"
  ]
}
```

### Circuit Breaker Configuration

```python
CIRCUIT_BREAKER = {
    "failure_threshold": 5,      # Open after 5 consecutive failures
    "recovery_timeout": 30,      # Try half-open after 30 seconds
    "half_open_max_calls": 3     # Test calls before closing
}
```

## Caching Strategy

Multi-layer caching with appropriate TTLs:

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Store locations | 24 hours | Rarely changes |
| Product catalog | 1 hour | Stable data, high read volume |
| Prices | 15 minutes | Balance freshness vs load |
| Inventory levels | 5 minutes | Needs relative freshness |
| Search results | 10 minutes | Common queries benefit from caching |
| Cart data | **No cache** | Always fresh |

### Cache Keys

```python
# Pattern: heb:{type}:{store_id}:{identifier}
"heb:store:590"                      # Store details
"heb:product:590:123456"             # Product at store
"heb:search:590:chicken_breast"      # Search results
"heb:inventory:590:123456"           # Stock level
```

### Stale-While-Revalidate

When cache is stale but API fails, return stale data with warning:

```python
{
  "data": {...},
  "source": "cache",
  "cache_age_seconds": 320,
  "warning": "Data may be outdated (cached 5 minutes ago)"
}
```

## Observability

### Health Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/health/live` | Liveness probe (is process running?) | `{"status": "alive"}` |
| `/health/ready` | Readiness probe (can serve traffic?) | Component health details |

### Readiness Response

```python
{
  "status": "healthy",          # healthy | degraded | unhealthy
  "timestamp": "2026-01-29T10:15:30Z",
  "components": {
    "graphql_api": {"status": "up", "latency_ms": 45},
    "cache": {"status": "up", "hit_rate": 0.82},
    "html_scraper": {"status": "up"}
  },
  "circuit_breakers": {
    "heb_api": {"state": "closed", "failures": 0}
  }
}
```

### Metrics (Prometheus)

```
# Tool call metrics
texas_grocery_mcp_tool_calls_total{tool="product_search", status="success"} 1523
texas_grocery_mcp_tool_duration_seconds{tool="product_search", quantile="0.95"} 0.087

# Cache metrics
texas_grocery_mcp_cache_hits_total{type="product"} 4521
texas_grocery_mcp_cache_misses_total{type="product"} 892

# Circuit breaker state
texas_grocery_mcp_circuit_breaker_state{service="heb_api"} 0  # 0=closed, 1=open, 2=half-open

# Error metrics
texas_grocery_mcp_errors_total{category="external", code="rate_limited"} 12
```

### Logging

- **Format:** Structured JSON to stderr (stdout reserved for MCP protocol)
- **Correlation IDs:** Track requests across components
- **No PII:** User identifiers are hashed

```json
{
  "timestamp": "2026-01-29T10:15:30.123Z",
  "level": "info",
  "tool": "product_search",
  "store_id": "590",
  "query": "chicken",
  "latency_ms": 87,
  "cache_hit": true,
  "correlation_id": "abc123"
}
```

## Authentication Flow

### Hybrid Model

**Read operations:** Work immediately, no authentication required.

**Cart operations:** Require authentication via Playwright MCP.

### Login Flow (Dual-MCP)

```
┌──────────────┐     ┌─────────────────────┐     ┌──────────────┐
│   AI Agent   │     │   Playwright MCP    │     │   Texas Grocery MCP    │
│  (Claude)    │     │   (Browser Auth)    │     │  (Grocery)   │
└──────┬───────┘     └──────────┬──────────┘     └──────┬───────┘
       │                        │                       │
       │  1. cart_add(item)     │                       │
       │ ───────────────────────────────────────────────▶
       │                        │                       │
       │  2. {auth_required: true, use_playwright_mcp}  │
       │ ◀───────────────────────────────────────────────
       │                        │                       │
       │  3. navigate(heb.com/login)                    │
       │ ──────────────────────▶│                       │
       │                        │                       │
       │     [User logs in manually in browser]         │
       │                        │                       │
       │  4. save_storage_state(~/.texas-grocery-mcp/auth.json)   │
       │ ──────────────────────▶│                       │
       │                        │                       │
       │  5. {authenticated: true}                      │
       │ ◀──────────────────────│                       │
       │                        │                       │
       │  6. cart_add(item) [retry]                     │
       │ ───────────────────────────────────────────────▶
       │                        │                       │
       │  7. {success: true, cart: {...}}               │
       │ ◀───────────────────────────────────────────────
```

### Step-by-Step Flow

1. **Agent calls cart operation** (e.g., `cart_add`)
2. **Texas Grocery MCP checks for auth state** at `~/.texas-grocery-mcp/auth.json`
3. **If no auth or expired**, returns:
   ```python
   {
     "auth_required": true,
     "message": "Login required for cart operations",
     "action": "Use Playwright MCP to authenticate",
     "instructions": [
       "1. Call playwright.navigate('https://www.heb.com/login')",
       "2. Complete login in browser",
       "3. Call playwright.save_storage_state('~/.texas-grocery-mcp/auth.json')",
       "4. Retry this operation"
     ]
   }
   ```
4. **Agent uses Playwright MCP** to open browser and navigate to HEB login
5. **User logs in manually** (handles CAPTCHA, 2FA if needed)
6. **Agent calls Playwright MCP** to save storage state (cookies + localStorage)
7. **Agent retries cart operation** - Texas Grocery MCP loads auth state and succeeds

### Auth State File Format

The auth state file (`~/.texas-grocery-mcp/auth.json`) follows Playwright's storage state format:

```json
{
  "cookies": [
    {
      "name": "SESSION_ID",
      "value": "abc123...",
      "domain": ".heb.com",
      "path": "/",
      "expires": 1738281600,
      "httpOnly": true,
      "secure": true
    }
  ],
  "origins": [
    {
      "origin": "https://www.heb.com",
      "localStorage": [
        {"name": "user_preferences", "value": "..."}
      ]
    }
  ]
}
```

### Session Persistence

- Auth state stored in `~/.texas-grocery-mcp/auth.json` (Playwright format)
- Texas Grocery MCP validates cookies before cart operations
- Checks `expires` field to detect stale sessions
- Returns `auth_required` response when re-auth needed
- No passwords stored - only session cookies and localStorage

## Project Structure

```
texas-grocery-mcp/
├── pyproject.toml              # Project config, dependencies
├── Dockerfile                  # Container deployment
├── docker-compose.yml          # Local dev with Redis
├── README.md                   # Setup & usage docs
├── .env.example                # Template for config
│
├── src/
│   └── texas_grocery_mcp/
│       ├── __init__.py
│       ├── server.py           # FastMCP server entry point
│       │
│       ├── tools/              # MCP tool definitions
│       │   ├── __init__.py
│       │   ├── store.py        # store_* tools
│       │   ├── product.py      # product_* tools
│       │   ├── coupon.py       # coupon_* tools
│       │   ├── cart.py         # cart_* tools
│       │   └── pickup.py       # pickup_* tools
│       │
│       ├── clients/            # External service clients
│       │   ├── __init__.py
│       │   ├── graphql.py      # HEB GraphQL API client
│       │   ├── scraper.py      # HTML fallback scraper
│       │   └── cache.py        # Redis cache client
│       │
│       ├── models/             # Pydantic data models
│       │   ├── __init__.py
│       │   ├── store.py
│       │   ├── product.py
│       │   ├── cart.py
│       │   ├── pickup.py
│       │   └── health.py       # Health check models
│       │
│       ├── auth/               # Session management
│       │   ├── __init__.py
│       │   └── session.py      # Load Playwright auth state
│       │
│       ├── reliability/        # Production resilience
│       │   ├── __init__.py
│       │   ├── retry.py        # Retry with exponential backoff + jitter
│       │   ├── circuit_breaker.py  # Prevent cascading failures
│       │   └── fallback.py     # Graceful degradation chain
│       │
│       ├── observability/      # Monitoring & debugging
│       │   ├── __init__.py
│       │   ├── health.py       # /health/live, /health/ready
│       │   ├── metrics.py      # Prometheus metrics
│       │   └── logging.py      # Structured JSON logging
│       │
│       └── utils/
│           ├── __init__.py
│           └── config.py       # Pydantic settings
│
├── tests/
│   ├── __init__.py
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
│
└── docs/
    ├── installation.md         # Setup guide
    ├── configuration.md        # Config reference
    └── api-reference.md        # Tool documentation
```

## Dependencies

```toml
[project]
dependencies = [
    "fastmcp>=3.0",              # MCP framework (ecosystem standard)
    "httpx>=0.27",               # Async HTTP for GraphQL
    "pydantic>=2.0",             # Data validation
    "pydantic-settings>=2.0",    # Typed configuration
    "beautifulsoup4>=4.12",      # HTML fallback parsing
    "redis>=5.0",                # Caching layer
    "structlog>=24.0",           # Structured JSON logging
    "prometheus-client>=0.19",   # Metrics endpoint
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.1",
    "mypy>=1.8",
    "ruff>=0.1",
]
```

**Note:** Playwright is NOT a dependency. Browser automation is handled by Microsoft Playwright MCP, which users install separately.

## Client Configuration

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
        "HEB_DEFAULT_STORE": "590",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### VS Code (Cline/Continue)

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic-ai/mcp-playwright"]
    },
    "heb": {
      "command": "uvx",
      "args": ["texas-grocery-mcp"]
    }
  }
}
```

### Docker Compose (Development)

```yaml
version: '3.8'
services:
  texas-grocery-mcp:
    build: .
    volumes:
      - ~/.texas-grocery-mcp:/root/.texas-grocery-mcp  # Auth state
    environment:
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=DEBUG
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Reference Projects

- [Microsoft Playwright MCP](https://github.com/microsoft/playwright-mcp) - Browser automation (26.4k stars)
- [kroger-mcp](https://github.com/CupOfOwls/kroger-mcp) - FastMCP architecture template
- [heb-scraper](https://github.com/alfredopzr/heb-scraper) - HEB GraphQL queries
- [strands-agent-shopper](https://github.com/cornflowerblu/strands-agent-shopper) - HEB browser automation patterns
- [groceries-mcp](https://github.com/o-b-one/groceries-mcp) - Multi-vendor MCP design

## Future Enhancements

### V1.5 - Differentiation Features (High Priority)

Based on market research, these features would set Texas Grocery MCP apart from competitors:

1. **Recipe-to-Cart Intelligence**
   - Parse recipe URLs or text: "Add ingredients for chicken parmesan for 4"
   - Exclude pantry staples (salt, pepper, oil)
   - HEB Meal Simple integration for ready-made options
   - *Market gap: No competitor does this well*

2. **Dietary Preference Management**
   - Persistent allergy/restriction filtering
   - Preferred brands (HEB Organics, Central Market)
   - Budget preference (value vs premium)
   - *Builds personalization moat and switching costs*

3. **Smart Substitutions with Explanations**
   - When items unavailable, suggest alternatives
   - Explain *why*: "Similar protein (24g vs 26g), lower price"
   - Auto-substitute option for >90% match score
   - *Builds trust through transparency*

4. **Texas Local Product Discovery**
   - HEB-exclusive items
   - Primo Picks curation
   - Seasonal Texas products
   - *Regional expertise is defensible*

### V2 - Advanced Features

5. **Path optimization** - Sort shopping list by optimal route through store
6. **Delivery support** - Add delivery scheduling alongside pickup
7. **Budget optimization** - "Keep weekly groceries under $150" with Combo Locos
8. **Price alerts** - Notify when items drop below threshold
9. **Multi-store comparison** - Compare prices across nearby stores
10. **Spanish language support** - Serve Texas Hispanic community

## Research Documents

This design was refined based on comprehensive MCP ecosystem research:

- **Market Research:** `docs/research/market/research-successful-mcp-market.md`
- **Technical Research:** `docs/research/technical/research-successful-mcp-technical.md`
- **Synthesis:** `docs/research/research-successful-mcp-synthesis.md`

Key findings:
- FastMCP powers 70% of successful MCPs
- OAuth 2.1 mandatory for HTTP transports (we use stdio to avoid this)
- Human-in-the-loop confirmation is community expectation
- Recipe-to-cart is a major market gap
- Production MCPs need health checks, metrics, and caching
