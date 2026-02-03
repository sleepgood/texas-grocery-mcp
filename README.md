# Texas Grocery MCP

[![PyPI version](https://badge.fury.io/py/texas-grocery-mcp.svg)](https://pypi.org/project/texas-grocery-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/mgwalkerjr95/texas-grocery-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/mgwalkerjr95/texas-grocery-mcp/actions/workflows/ci.yml)

An MCP (Model Context Protocol) server that enables AI agents to interact with HEB grocery stores for product search, product details, cart management, and digital coupons.

This project is **not affiliated with H-E-B**. It uses unofficial web APIs and browser automation against HEB.com; use responsibly and ensure your usage complies with applicable terms and laws.

## Features

- **Store Search**: Find HEB stores by address or zip code
- **Product Search**: Search products with pricing and availability
- **Cart Management**: Add/remove items with human-in-the-loop confirmation
- **Product Details**: Ingredients, nutrition facts, allergens, warnings, and dietary attributes
- **Coupons**: List/search/clip digital coupons (requires authentication)
- **Session Management**: Refresh sessions automatically (fast with embedded Playwright)

## Installation

### Basic Installation

```bash
pip install texas-grocery-mcp
```

This provides all core functionality. Session refresh requires orchestrating Playwright MCP (~4 minutes).

### Full Installation (Recommended)

```bash
pip install texas-grocery-mcp[browser]
playwright install chromium
```

This enables **fast auto-refresh** (~15 seconds) using an embedded browser. Adds ~150MB for Chromium.

### Prerequisites

For cart operations and session management, you'll also need **Microsoft Playwright MCP**:

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

Agent uses: store_change(store_id="590")
Agent uses: product_search(query="organic milk")
```

### Getting Product Details

For detailed information about a specific product (ingredients, nutrition, allergens, warnings):

```
User: What are the ingredients in H-E-B olive oil?

Agent uses: product_search(query="heb olive oil")
# Returns products with product_id

Agent uses: product_get(product_id="127074")
# Returns detailed info: ingredients, nutrition facts, warnings, dietary attributes
```

The `product_get` tool returns comprehensive information including:
- **Ingredients**: Full ingredient statement
- **Nutrition Facts**: Complete FDA panel with serving size, calories, and all nutrients
- **Safety Warnings**: Allergen info and safety precautions
- **Dietary Attributes**: Gluten-free, organic, vegan, kosher, etc.
- **Preparation/Storage**: Instructions for use and storage
- **Store Location**: Aisle or section where product is located

### Adding to Cart

Cart operations require authentication via Playwright MCP:

```
User: Add 2 gallons of milk to my cart

Agent uses: cart_add(product_id="123456", quantity=2)
# Returns preview with confirm=true instruction

Agent uses: cart_add(product_id="123456", quantity=2, confirm=true)
# Executes the action
```

## Session Management

HEB uses bot detection (reese84 token) that expires every ~11 minutes. This MCP handles session refresh automatically.

### Fast Auto-Refresh (Recommended)

If you installed with `[browser]` support:

```
Agent uses: session_refresh()
# Completes in ~10-15 seconds
```

This runs an embedded browser to refresh your session automatically.

### Manual Refresh (Fallback)

Without browser support, use the Playwright MCP orchestration:

```
Agent uses: session_refresh()
# Returns Playwright commands to execute (~4 minutes)
```

### Initial Login

For first-time authentication or when session fully expires:

1. `browser_navigate('https://www.heb.com/my-account/login')`
2. Complete login in the browser
3. Save storage state:
   ```javascript
   await page.context().storageState({ path: '~/.texas-grocery-mcp/auth.json' })
   ```
4. Retry cart operations

Or use `session_refresh(headless=False)` to login in a visible browser window.

## Available Tools

### Store Tools
- `store_search` - Find stores by address
- `store_change` - Set preferred store (syncs with HEB.com when authenticated)
- `store_get_default` - Get current default store

### Product Tools
- `product_search` - Search products by name with pricing and availability
- `product_search_batch` - Search multiple products at once (up to 20 queries)
- `product_get` - Get comprehensive product details (ingredients, nutrition, warnings, dietary attributes)

### Cart Tools
- `cart_check_auth` - Check authentication status
- `cart_get` - View cart contents
- `cart_add` - Add item (requires confirmation)
- `cart_add_with_retry` - Add item with automatic retry on failure
- `cart_remove` - Remove item (requires confirmation)

### Coupon Tools
- `coupon_list` - List available digital coupons
- `coupon_search` - Search coupons by keyword
- `coupon_categories` - Get coupon category list
- `coupon_clip` - Clip a coupon to your account (requires confirmation)
- `coupon_clipped` - List your clipped coupons

### Session Tools
- `session_status` - Check session health and token expiration
- `session_refresh` - Refresh/login (fast with `[browser]`, otherwise returns Playwright MCP commands)
- `session_save_instructions` - Get manual login + session-save instructions
- `session_save_credentials` - Save credentials for auto-login (secure)
- `session_clear_credentials` - Remove saved credentials
- `session_clear` - Clear saved session (logout)

### Health Tools
- `health_live` - Liveness probe
- `health_ready` - Readiness probe with component status

## Documentation

- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Solutions for common issues
- [Contributing](CONTRIBUTING.md) - How to contribute to this project
- [Changelog](CHANGELOG.md) - Version history and release notes
- [Security](SECURITY.md) - Security policy and best practices

## Development

```bash
# Clone repository
git clone https://github.com/mgwalkerjr95/texas-grocery-mcp
cd texas-grocery-mcp

# Install with dev dependencies (includes Playwright)
pip install -e ".[dev]"
playwright install chromium

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
