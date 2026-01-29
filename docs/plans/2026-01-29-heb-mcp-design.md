# HEB MCP Server Design

**Date:** 2026-01-29
**Status:** Approved

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

```
┌─────────────────────────────────────────────────────────────────┐
│                        HEB MCP Server                           │
│                     (Python + FastMCP)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │  Store Tools    │  │  Product Tools  │  │  Cart Tools    │  │
│  │  store_*        │  │  product_*      │  │  cart_*        │  │
│  └────────┬────────┘  └────────┬────────┘  └───────┬────────┘  │
│           │                    │                   │            │
│  ┌────────▼────────────────────▼───────────────────▼────────┐  │
│  │                    Request Layer                          │  │
│  │         Retry Logic → Fallback Handler → Error            │  │
│  └────────┬─────────────────────────────────┬───────────────┘  │
│           │                                 │                   │
│  ┌────────▼────────┐               ┌────────▼────────┐         │
│  │  GraphQL Client │               │    Playwright   │         │
│  │  (Primary)      │               │  Browser Driver │         │
│  │                 │               │  (Cart/Auth)    │         │
│  └────────┬────────┘               └────────┬────────┘         │
│           │                                 │                   │
│  ┌────────▼────────┐               ┌────────▼────────┐         │
│  │  HTML Scraper   │               │  Session Mgmt   │         │
│  │  (Fallback)     │               │  (Cookies)      │         │
│  └─────────────────┘               └─────────────────┘         │
│                                                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                    HEB APIs & Website
                    - www.heb.com/graphql
                    - www.heb.com (browser)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | Python + FastMCP | Most HEB reference projects use Python; kroger-mcp template available |
| Primary Data Source | HEB GraphQL API | Publicly accessible, no auth for reads, structured data |
| Cart Operations | Built-in Playwright | Self-contained MCP, no external dependencies |
| Fallback Strategy | HTML Scraping | Resilience when GraphQL changes or fails |
| Caching | None | Always fresh prices/inventory; simplicity for MVP |

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

### Store Tools

| Tool | Description | Auth |
|------|-------------|------|
| `store_search` | Find stores by address/zip + radius | No |
| `store_get` | Get details for a specific store | No |
| `store_set_default` | Set preferred store for future calls | No |
| `store_get_default` | Get currently set default store | No |

### Product Tools

| Tool | Description | Auth |
|------|-------------|------|
| `product_search` | Search products by query, with configurable fields | No |
| `product_get` | Get full details for a product by SKU/ID | No |
| `product_browse_category` | Browse products in a category | No |
| `product_check_inventory` | Check availability at a store | No |
| `product_get_location` | Get aisle/section in store | No |
| `product_find_alternatives` | Find similar/cheaper products | No |

### Coupon Tools

| Tool | Description | Auth |
|------|-------------|------|
| `coupon_search` | Search coupons by product/category | No |
| `coupon_browse` | Browse all current deals | No |
| `coupon_check_applicable` | Check which coupons apply to a cart | No |

### Cart Tools

| Tool | Description | Auth |
|------|-------------|------|
| `cart_login` | Launch browser for user to authenticate | Yes (triggers) |
| `cart_get` | View current cart contents | Yes |
| `cart_add` | Add item(s) to cart | Yes |
| `cart_remove` | Remove item from cart | Yes |
| `cart_update_quantity` | Change quantity of cart item | Yes |
| `cart_get_coupon_suggestions` | Get applicable coupons for current cart | Yes |
| `cart_apply_coupon` | Apply a coupon code | Yes |

### Pickup Tools

| Tool | Description | Auth |
|------|-------------|------|
| `pickup_get_slots` | Get available pickup time slots | Yes |
| `pickup_schedule` | Book a pickup slot | Yes |

**Total: 19 tools** across 5 domains.

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
Try GraphQL API ──── Success ──▶ Return data
    │
    │ Fail
    ▼
Retry (3x with exponential backoff) ──── Success ──▶ Return data
    │
    │ Still failing
    ▼
Fallback to HTML scraping ──── Success ──▶ Return data (with "source": "fallback")
    │
    │ Fail
    ▼
Return error with details
```

## Authentication Flow

### Hybrid Model

**Read operations:** Work immediately, no authentication required.

**Cart operations:** Require authentication via browser login.

### Login Flow

1. User/Agent calls a cart tool (e.g., `cart_add`)
2. MCP checks for valid session
3. If no session or expired, returns:
   ```python
   {
     "auth_required": true,
     "message": "Login required for cart operations",
     "action": "Call cart_login to authenticate"
   }
   ```
4. User/Agent calls `cart_login`
5. Playwright launches browser to heb.com/login
6. User logs in manually
7. MCP captures session cookies
8. Browser closes
9. Session saved to `~/.heb-mcp/session.json` (encrypted)
10. Returns `{"authenticated": true, "expires": "..."}`
11. User/Agent retries cart operation - now works

### Session Persistence

- Session cookies stored locally (encrypted)
- MCP checks session validity before cart operations
- Auto-prompts for re-auth when session expires
- No passwords stored - only session tokens

## Project Structure

```
heb-mcp/
├── pyproject.toml              # Project config, dependencies
├── README.md                   # Setup & usage docs
├── .env.example                # Template for config
│
├── src/
│   └── heb_mcp/
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
│       │   └── browser.py      # Playwright automation
│       │
│       ├── models/             # Pydantic data models
│       │   ├── __init__.py
│       │   ├── store.py
│       │   ├── product.py
│       │   ├── cart.py
│       │   └── pickup.py
│       │
│       ├── auth/               # Session management
│       │   ├── __init__.py
│       │   └── session.py      # Cookie storage, validation
│       │
│       └── utils/              # Shared utilities
│           ├── __init__.py
│           ├── retry.py        # Retry logic with backoff
│           └── config.py       # Settings, defaults
│
└── tests/
    ├── __init__.py
    ├── test_store.py
    ├── test_product.py
    └── ...
```

## Dependencies

```toml
[dependencies]
fastmcp = "^0.1"
httpx = "^0.27"           # Async HTTP for GraphQL
playwright = "^1.40"      # Browser automation
pydantic = "^2.0"         # Data validation
beautifulsoup4 = "^4.12"  # HTML fallback parsing
cryptography = "^41.0"    # Session encryption
```

## Reference Projects

- [kroger-mcp](https://github.com/CupOfOwls/kroger-mcp) - FastMCP architecture template
- [heb-scraper](https://github.com/alfredopzr/heb-scraper) - HEB GraphQL queries
- [strands-agent-shopper](https://github.com/cornflowerblu/strands-agent-shopper) - HEB browser automation patterns
- [groceries-mcp](https://github.com/o-b-one/groceries-mcp) - Multi-vendor MCP design

## Future Enhancements

1. **Path optimization** - Sort shopping list by optimal route through store (like HEB's Pyxis API)
2. **Delivery support** - Add delivery scheduling alongside pickup
3. **Price alerts** - Notify when items drop below threshold
4. **Smart caching** - Optional caching with configurable TTLs
5. **Multi-store comparison** - Compare prices across nearby stores
6. **Recipe integration** - Direct integration with recipe APIs
