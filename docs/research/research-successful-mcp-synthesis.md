# HEB MCP Design: Research Synthesis and Refinements

**Date**: 2026-01-29
**Status**: Draft
**Purpose**: Synthesize market and technical research findings to refine the HEB MCP server design

---

## Executive Summary

This document synthesizes findings from market research on successful MCP projects and technical research on implementation patterns to evaluate and refine the current HEB MCP server design. The analysis reveals that while the current design has solid foundational elements, significant gaps exist in production readiness, security infrastructure, and differentiation opportunities.

**Key Findings:**

1. **Strong Alignment**: The current design correctly identifies FastMCP as the framework choice, implements a sensible tool taxonomy, and plans for fallback mechanisms.

2. **Critical Gaps**: Missing OAuth 2.1 implementation, no health check infrastructure, limited observability, and no human-in-the-loop confirmation for state-changing operations.

3. **Differentiation Opportunity**: Recipe-to-cart intelligence, dietary preference management, and smart substitutions represent high-value features largely unaddressed by competitors.

4. **Infrastructure Requirements**: Production deployment requires Redis caching, circuit breakers, Prometheus metrics, and containerization - none currently specified.

---

## 1. Alignment Analysis

### 1.1 Where the Current Design Aligns with Successful Patterns

| Aspect | Current Design | Best Practice | Assessment |
|--------|---------------|---------------|------------|
| **Framework Choice** | Python + FastMCP | FastMCP dominates ecosystem (70% of servers) | **Aligned** |
| **Project Structure** | Modular: tools/, clients/, models/, auth/, utils/ | Single-responsibility, layered architecture | **Aligned** |
| **Tool Taxonomy** | 5 domains: store, product, coupon, cart, pickup | Focused servers with clear boundaries | **Aligned** |
| **Fallback Strategy** | GraphQL -> HTML Scraping | Graceful degradation pattern | **Aligned** |
| **Retry Logic** | "3x with exponential backoff" | Best practice: 3-5 retries, exp backoff, jitter | **Aligned** |
| **Data Models** | Pydantic-style structures with configurable fields | Strict input/output schemas | **Aligned** |
| **Read/Write Separation** | Auth not required for reads | Client vs user credentials pattern | **Aligned** |

**Strengths of Current Design:**

1. **Configurable Field Selection**: The `fields=["all"]` pattern for product_search reduces payload size and improves performance - a sophisticated pattern not common in simpler implementations.

2. **Hybrid Authentication Model**: Recognizing that read operations don't require auth while cart operations do aligns with the dual-token strategy used by Kroger MCP.

3. **Fallback Chain Architecture**: GraphQL -> Retry -> HTML Scraper -> Error mirrors the recommended graceful degradation pattern.

4. **Tool Count Discipline**: 19 tools across 5 domains is appropriately scoped - avoids "tool bloat" syndrome where 50+ tools overwhelm AI and users.

### 1.2 Where the Current Design Diverges or Falls Short

| Aspect | Current Design | Best Practice | Gap Severity |
|--------|---------------|---------------|--------------|
| **Authentication** | Browser login + session cookies | OAuth 2.1 with PKCE mandatory (March 2025) | **Critical** |
| **Health Checks** | Not specified | Liveness + Readiness probes required | **Critical** |
| **Observability** | Not specified | OpenTelemetry, Prometheus metrics, structured logging | **High** |
| **Circuit Breakers** | Not specified | Prevent cascading failures | **High** |
| **User Confirmation** | Not specified | Required for destructive operations | **High** |
| **Caching** | "None - always fresh" | Multi-layer caching standard for production | **Medium** |
| **Rate Limiting** | Not specified | Prevent abuse, protect upstream APIs | **Medium** |
| **Tool Annotations** | Not specified | readOnlyHint, destructiveHint standard | **Medium** |
| **Deployment** | Not specified | Docker + Kubernetes standard | **Medium** |
| **Documentation** | README mentioned | Comprehensive multi-platform guides required | **Low** |

**Critical Gaps Explained:**

1. **OAuth 2.1 Requirement**: The current design uses Playwright browser automation for authentication. Since March 2025, OAuth 2.1 is **mandatory** for all HTTP-based MCP transports. The session cookie approach is non-compliant with MCP specification.

2. **Health Check Infrastructure**: Production MCP servers require `/health/live` and `/health/ready` endpoints for Kubernetes probes, load balancer health checks, and circuit breaker integration. The current design has no health monitoring.

3. **Missing Observability**: Without metrics, tracing, and structured logging, production troubleshooting is impossible. The Three-Layer Observability Pattern (Protocol, Tool, Agent layers) is standard practice.

---

## 2. Critical Gaps to Address

### 2.1 Must-Have for Production Readiness

#### Gap 1: OAuth 2.1 Implementation

**Current State**: Browser-based login via Playwright, session cookies stored locally.

**Required State**: OAuth 2.1 with PKCE, JWT validation, refresh token management.

**Technical Implications**:
- Implement `/.well-known/oauth-protected-resource` endpoint
- Support PKCE challenge generation
- JWT token validation with JWKS
- Secure token storage in system keychain (not `.env`)

**Implementation Pattern** (from Kroger MCP):
```python
class AuthManager:
    """Dual-token strategy: client credentials + user authorization"""

    async def get_client_token(self) -> str:
        """For public APIs (product search, store lookup)"""

    async def get_user_token(self) -> str:
        """For user-specific operations (cart, orders)"""
```

**Risk if Not Addressed**: MCP clients will reject connections; non-compliant with specification.

#### Gap 2: Health Check Endpoints

**Current State**: Not specified.

**Required State**: Component-aware health checks with degradation support.

**Technical Implications**:
- `/health/live` - Simple liveness probe (is process alive?)
- `/health/ready` - Component health (database, cache, external APIs)
- Circuit breaker status exposure
- HTTP status codes reflecting health state

**Implementation Pattern**:
```python
@app.get("/health/ready")
async def readiness():
    return {
        "status": "healthy|degraded|unhealthy",
        "components": {
            "graphql_api": {"status": "up", "latency_ms": 45},
            "html_scraper": {"status": "up"},
            "session_store": {"status": "up"}
        }
    }
```

**Risk if Not Addressed**: Dead servers receive traffic; no automated recovery.

#### Gap 3: Human-in-the-Loop Confirmation

**Current State**: Not specified for cart operations.

**Required State**: Explicit confirmation for state-changing operations.

**Technical Implications**:
- `cart_add`, `cart_remove`, `pickup_schedule` must require confirmation
- Dry-run mode showing order summary before execution
- Tool annotations: `"destructiveHint": true, "requiresConfirmation": true`

**Market Research Finding**: "Specialized feedback MCP servers emerging... community values confirmation before speculative operations."

**Implementation Pattern**:
```python
@mcp.tool(annotations={"destructiveHint": True, "requiresConfirmation": True})
def cart_add(product_id: str, quantity: int, confirm: bool = False) -> dict:
    if not confirm:
        return {
            "action": "cart_add",
            "preview": {"product": "...", "price": 4.99},
            "message": "Set confirm=true to add this item"
        }
    # Actually add to cart
```

**Risk if Not Addressed**: AI makes unintended purchases; user trust issues; support burden.

#### Gap 4: Structured Error Handling

**Current State**: Basic error model with `code`, `message`, `details`.

**Required State**: Classified errors with retry metadata and actionable guidance.

**Technical Implications**:
- Classify: Client errors (400s), Server errors (500s), External errors (502/503)
- Include retry metadata for transient failures
- Actionable messages guiding resolution
- Never expose internal system details

**Current Design Error Model Enhancement**:
```python
{
  "error": true,
  "code": "HEB_API_RATE_LIMITED",        # Specific code
  "category": "external",                 # Classification
  "message": "HEB API rate limit exceeded",
  "retry_after_seconds": 60,              # Retry metadata
  "suggestions": [
    "Wait 60 seconds before retrying",
    "Reduce request frequency"
  ],
  "fallback_available": true              # Graceful degradation hint
}
```

**Risk if Not Addressed**: Non-actionable errors; poor AI decision-making; support overhead.

### 2.2 Security Gaps

#### Gap 5: Credential Storage

**Current State**: "Session saved to `~/.heb-mcp/session.json` (encrypted)"

**Required State**: System keychain or secret manager integration.

**Market Research Finding**: "48% of MCP servers recommend `.env` files or hardcoded credentials... insecure file permissions common."

**Implementation Pattern**:
```python
import keyring

def store_credential(service: str, key: str, value: str):
    keyring.set_password(service, key, value)

def retrieve_credential(service: str, key: str) -> str:
    return keyring.get_password(service, key)
```

**Risk if Not Addressed**: Credential exposure; security audit failure.

#### Gap 6: Tool Annotations for Safety

**Current State**: Not specified.

**Required State**: All tools annotated with safety hints.

**Technical Implications**:
- `readOnlyHint: true` for search, browse, get operations
- `destructiveHint: true` for add, remove, schedule operations
- Clients use annotations to warn users before execution

**Risk if Not Addressed**: AI performs destructive actions without user awareness.

### 2.3 Reliability Gaps

#### Gap 7: Circuit Breaker Pattern

**Current State**: Not specified.

**Required State**: Circuit breakers for external dependencies.

**Technical Implications**:
- Prevent repeated calls to failing HEB APIs
- Three states: Closed (normal), Open (failing), Half-Open (recovery)
- Default configuration: 5 failures threshold, 30s timeout

**Risk if Not Addressed**: Cascading failures; resource exhaustion; poor user experience.

#### Gap 8: Caching Layer

**Current State**: "None - always fresh prices/inventory; simplicity for MVP"

**Required State**: Multi-layer caching with appropriate TTLs.

**Market Research Context**: ">80% cache hit rate for product searches" is production target.

**Recommended Strategy**:
| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Product catalog | 1 hour | Stable data, high read volume |
| Store locations | 24 hours | Rarely changes |
| Inventory levels | 5 minutes | Balance freshness vs load |
| Prices | 15 minutes | Balance freshness vs load |
| Cart data | None | Always fresh |

**Risk if Not Addressed**: Poor performance; excessive API load; potential rate limiting.

#### Gap 9: Rate Limiting

**Current State**: Not specified.

**Required State**: Per-user and per-tool rate limits.

**Implementation Pattern**:
```python
# Per-user limits
RATE_LIMITS = {
    "product_search": "60/minute",
    "cart_add": "30/minute",
    "pickup_schedule": "10/minute"
}
```

**Risk if Not Addressed**: Abuse potential; upstream API rate limiting; cost overruns.

### 2.4 Observability Gaps

#### Gap 10: Metrics and Tracing

**Current State**: Not specified.

**Required State**: Full observability stack.

**Technical Implications**:
- Prometheus metrics endpoint (`/metrics`)
- OpenTelemetry tracing integration
- Structured logging to stderr (JSON format)
- Correlation IDs across requests

**Key Metrics to Track**:
- `mcp_tool_calls_total{tool_name, status}`
- `mcp_tool_duration_seconds{tool_name}`
- `mcp_circuit_breaker_state{service}`
- `mcp_cache_hit_rate{cache_type}`

**Risk if Not Addressed**: Production troubleshooting impossible; no performance baseline.

---

## 3. Differentiation Opportunities

### 3.1 Market Gaps Analysis

Based on competitive analysis from market research:

| Feature | Microsoft Dynamics | SAP | Shopify | Kroger | HEB MCP Opportunity |
|---------|-------------------|-----|---------|--------|---------------------|
| Recipe-to-Cart | No | No | No | Limited | **High differentiation** |
| Dietary Intelligence | No | No | Limited | Partial | **High differentiation** |
| Smart Substitutions | Yes (generic) | Yes | Yes | Yes | **Medium (explain why)** |
| Regional Focus | Global | Global | Global | National | **High (Texas specialty)** |
| Budget Optimization | Limited | Limited | No | Limited | **Medium differentiation** |

### 3.2 Killer Features to Prioritize

#### Opportunity 1: Recipe-to-Cart Intelligence (HIGH PRIORITY)

**Market Gap**: "Existing grocery MCPs lack sophisticated recipe parsing and ingredient mapping."

**User Need**: "Add ingredients for chicken parmesan for 4 people" -> automatic shopping list

**HEB Advantages**:
- HEB Meal Simple private label creates natural integration point
- Central Market specialty items for recipe enthusiasts
- Texas regional cuisines (authentic Tex-Mex ingredients)

**Proposed Tools to Add**:
```python
# New tool
@mcp.tool
def recipe_to_cart(
    recipe_url: str | None = None,
    recipe_text: str | None = None,
    servings: int = 4,
    exclude_pantry_staples: bool = True
) -> dict:
    """
    Parse a recipe and add ingredients to cart.

    Returns:
    - ingredients_found: Items matched to HEB products
    - ingredients_unclear: Items needing clarification
    - estimated_cost: Total cart addition cost
    - requires_confirmation: True (always for cart changes)
    """
```

**Technical Complexity**: High (NLP for recipe parsing, product matching)

**Competitive Moat**: Yes - builds on HEB's product taxonomy expertise

#### Opportunity 2: Dietary Preference Management (HIGH PRIORITY)

**Market Gap**: "MCPs lack persistent user preference and dietary restriction management."

**User Need**: "I'm allergic to peanuts" should filter all future recommendations.

**HEB Advantages**:
- Integration with HEB loyalty program data
- Central Market positioning for specialty diets
- Texas health-conscious demographic

**Proposed Tools to Add**:
```python
# New resource
@mcp.resource("heb://user/preferences")
def user_preferences() -> str:
    """User's stored dietary preferences, restrictions, and shopping patterns."""

# New tool
@mcp.tool
def preferences_set(
    dietary_restrictions: list[str] | None = None,  # ["gluten-free", "nut-free"]
    preferred_brands: list[str] | None = None,       # ["HEB Organics", "Central Market"]
    budget_preference: str | None = None,            # "value" | "premium"
    household_size: int | None = None
) -> dict:
    """Update user shopping preferences."""
```

**Technical Complexity**: Medium (preference storage, filtering logic)

**Competitive Moat**: Yes - personalization builds switching costs

#### Opportunity 3: Smart Substitution Logic (MEDIUM PRIORITY)

**Market Gap**: "Out of stock shouldn't end the conversation."

**User Need**: Comparable alternatives with explanation ("Same protein, similar price")

**HEB Advantages**:
- Partner selection expertise (HEB employees known for quality picks)
- Store format variety (HEB vs H-E-B Plus vs Central Market)

**Proposed Enhancement**:
```python
# Enhance existing product_find_alternatives
@mcp.tool
def product_find_alternatives(
    product_id: str,
    match_criteria: list[str] = ["price", "brand_tier", "nutrition"],
    explain: bool = True
) -> dict:
    """
    Find alternatives with explanation.

    Returns:
    - alternatives: Ranked list with match scores
    - explanation: "Similar protein (24g vs 26g), lower price ($4.29 vs $4.99)"
    - auto_substitute: Recommended if >90% match
    """
```

**Technical Complexity**: Medium (product attribute comparison, scoring)

**Competitive Moat**: Partial - explainability differentiates

#### Opportunity 4: Local & Regional Product Discovery (MEDIUM PRIORITY)

**Market Gap**: "National grocery MCPs don't highlight regional specialties."

**User Need**: "Show me Texas-made products" or "What's local and in season?"

**HEB Advantages**:
- HEB's Texas brand identity
- Primo Picks curation
- Central Market unique inventory
- Seasonal Texas products (peaches, pecans)

**Proposed Resource**:
```python
@mcp.resource("heb://products/local/{region}")
def local_products(region: str = "texas") -> str:
    """
    Texas-made and local producer products.
    Includes: HEB-exclusive items, Primo Picks, seasonal local.
    """
```

**Technical Complexity**: Low (product tagging/taxonomy)

**Competitive Moat**: Yes - regional expertise is defensible

#### Opportunity 5: Budget Optimization (LOWER PRIORITY)

**Market Gap**: "No MCP intelligently optimizes for budget while maintaining quality."

**User Need**: "Keep my weekly grocery bill under $150"

**HEB Advantages**:
- HEB digital coupons and Combo Locos
- Private label value positioning
- Loyalty program data

**Complexity**: High (promotional pricing, time-bound offers)

**Recommendation**: Defer to V2 - complex to execute correctly

### 3.3 Proposed Feature Prioritization

**V1 (MVP) - Core Functionality**:
- Product search with dietary filtering
- Store locator
- Cart management with confirmation
- Coupon browsing
- Pickup scheduling

**V1.5 (Post-MVP, High Value)**:
- Recipe-to-cart (basic: parse recipe URLs)
- Dietary preference storage
- Smart substitutions with explanation
- Local product discovery resource

**V2 (Future)**:
- Budget optimization
- Meal planning prompts
- Price history tracking
- Multi-language (Spanish)

---

## 4. Concrete Refinements

### 4.1 Specific Changes to Design Document

#### 4.1.1 Architecture Section Updates

**Add OAuth 2.1 Infrastructure**:
```
┌─────────────────────────────────────────────────────────────────┐
│                        HEB MCP Server                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ OAuth 2.1    │  │ Health Check │  │ Metrics      │          │
│  │ /authorize   │  │ /health/*    │  │ /metrics     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │  Store Tools    │  │  Product Tools  │  │  Cart Tools    │  │
│  └────────┬────────┘  └────────┬────────┘  └───────┬────────┘  │
│           │                    │                   │            │
│  ┌────────▼────────────────────▼───────────────────▼────────┐  │
│  │                    Request Layer                          │  │
│  │  Circuit Breaker → Retry Logic → Fallback → Cache         │  │
│  └────────┬─────────────────────────────────┬───────────────┘  │
│           │                                 │                   │
│  ┌────────▼────────┐               ┌────────▼────────┐         │
│  │  GraphQL Client │               │   Redis Cache   │         │
│  └────────┬────────┘               └─────────────────┘         │
│           │                                                     │
│  ┌────────▼────────┐                                           │
│  │  HTML Scraper   │                                           │
│  │  (Fallback)     │                                           │
│  └─────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Update Key Design Decisions Table**:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | Python + FastMCP | Ecosystem standard (70%), fastest development |
| Authentication | OAuth 2.1 + PKCE | MCP specification requirement (March 2025) |
| Token Storage | System keychain | Security best practice vs .env files |
| Primary Data Source | HEB GraphQL API | Structured data, no auth for reads |
| Cart Operations | OAuth user tokens | Replace Playwright browser automation |
| Caching | Redis with TTLs | Production performance requirement |
| Fallback Strategy | GraphQL -> Cache -> Scraper | Multi-layer resilience |
| Deployment | Docker + Kubernetes | Production standard |

#### 4.1.2 MCP Tools Section Updates

**Add Tool Annotations**:

| Tool | Read/Write | Destructive | Requires Confirmation |
|------|------------|-------------|----------------------|
| `store_search` | Read | No | No |
| `store_get` | Read | No | No |
| `product_search` | Read | No | No |
| `product_get` | Read | No | No |
| `coupon_search` | Read | No | No |
| `cart_get` | Read | No | No |
| `cart_add` | **Write** | **Yes** | **Yes** |
| `cart_remove` | **Write** | **Yes** | **Yes** |
| `cart_update_quantity` | **Write** | **Yes** | **Yes** |
| `cart_apply_coupon` | **Write** | No | No |
| `pickup_schedule` | **Write** | **Yes** | **Yes** |

**New Tools to Add**:

| Tool | Description | Auth | Priority |
|------|-------------|------|----------|
| `recipe_to_cart` | Parse recipe, add ingredients to cart | Yes | V1.5 |
| `preferences_get` | Get user dietary preferences | Yes | V1.5 |
| `preferences_set` | Update dietary preferences | Yes | V1.5 |
| `product_get_local` | Browse Texas-local products | No | V1.5 |

**Updated Tool Count**: 23 tools (was 19)

#### 4.1.3 New Data Models to Add

**PreferenceProfile Model**:
```python
{
  "dietary_restrictions": ["gluten-free", "nut-allergy"],
  "preferred_brands": ["HEB Organics", "Central Market"],
  "avoid_ingredients": ["high-fructose-corn-syrup"],
  "budget_preference": "value",  # value | balanced | premium
  "household_size": 4,
  "updated_at": "2026-01-29T10:00:00Z"
}
```

**RecipeParseResult Model**:
```python
{
  "recipe_name": "Chicken Parmesan",
  "servings": 4,
  "ingredients": [
    {
      "ingredient": "chicken breast",
      "quantity": "2 lbs",
      "matched_products": [
        {"sku": "123", "name": "HEB Chicken Breast", "price": 8.99}
      ],
      "match_confidence": 0.95
    }
  ],
  "pantry_staples_excluded": ["salt", "pepper", "olive oil"],
  "estimated_total": 24.50,
  "requires_confirmation": true
}
```

**HealthCheckResponse Model**:
```python
{
  "status": "healthy",  # healthy | degraded | unhealthy
  "timestamp": "2026-01-29T10:15:30Z",
  "components": {
    "graphql_api": {"status": "up", "latency_ms": 45},
    "cache": {"status": "up", "hit_rate": 0.82},
    "html_scraper": {"status": "up"},
    "auth_service": {"status": "up"}
  },
  "circuit_breakers": {
    "heb_api": {"state": "closed", "failures": 0}
  }
}
```

#### 4.1.4 Error Handling Section Updates

**Replace Current Error Model**:
```python
{
  "error": true,
  "code": "HEB_GRAPHQL_TIMEOUT",
  "category": "external",           # NEW: client | server | external
  "message": "HEB API request timed out",
  "retry_after_seconds": 30,        # NEW: retry metadata
  "fallback_used": true,            # NEW: degradation indicator
  "fallback_source": "cache",       # NEW: what fallback was used
  "suggestions": [
    "Data may be slightly stale (cached 5 minutes ago)",
    "Fresh data will be available shortly"
  ]
}
```

#### 4.1.5 New Section: Observability

**Add to Design Document**:

```markdown
## Observability

### Health Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/health/live` | Liveness probe | `{"status": "alive"}` |
| `/health/ready` | Readiness probe | Component health details |
| `/metrics` | Prometheus metrics | Prometheus text format |

### Metrics Collected

| Metric | Type | Labels |
|--------|------|--------|
| `heb_mcp_tool_calls_total` | Counter | tool_name, status |
| `heb_mcp_tool_duration_seconds` | Histogram | tool_name |
| `heb_mcp_cache_hit_total` | Counter | cache_type |
| `heb_mcp_circuit_breaker_state` | Gauge | service |
| `heb_mcp_active_sessions` | Gauge | - |

### Logging

- Format: JSON structured logging
- Output: stderr only (stdout reserved for MCP protocol)
- Fields: timestamp, level, tool, user_id (hashed), latency_ms, status
```

#### 4.1.6 New Section: Deployment

**Add to Design Document**:

```markdown
## Deployment

### Docker Configuration

Dockerfile provided with:
- Python 3.11 slim base image
- Non-root user execution
- Health check integration
- Resource limits

### Kubernetes Deployment

- Minimum 2 replicas for availability
- Horizontal Pod Autoscaler (target 70% CPU)
- Rolling updates (maxSurge: 1, maxUnavailable: 0)
- Liveness/Readiness probes configured

### Environment Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `HEB_CLIENT_ID` | Yes | OAuth client ID |
| `HEB_CLIENT_SECRET` | Yes | OAuth client secret |
| `REDIS_URL` | Yes (prod) | Redis cache connection |
| `LOG_LEVEL` | No | DEBUG, INFO, WARNING, ERROR |
| `ENVIRONMENT` | No | development, staging, production |
```

### 4.2 Updated Project Structure

```
heb-mcp/
├── pyproject.toml
├── Dockerfile                      # NEW
├── docker-compose.yml              # NEW
├── README.md
├── .env.example
│
├── src/
│   └── heb_mcp/
│       ├── __init__.py
│       ├── server.py
│       │
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── store.py
│       │   ├── product.py
│       │   ├── coupon.py
│       │   ├── cart.py
│       │   ├── pickup.py
│       │   ├── recipe.py           # NEW: recipe_to_cart
│       │   └── preferences.py      # NEW: user preferences
│       │
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── graphql.py
│       │   ├── scraper.py
│       │   └── cache.py            # NEW: Redis client
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── store.py
│       │   ├── product.py
│       │   ├── cart.py
│       │   ├── pickup.py
│       │   ├── preferences.py      # NEW
│       │   ├── recipe.py           # NEW
│       │   └── health.py           # NEW
│       │
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── oauth.py            # NEW: OAuth 2.1 implementation
│       │   ├── manager.py          # Renamed from session.py
│       │   └── keychain.py         # NEW: System keychain integration
│       │
│       ├── reliability/            # NEW directory
│       │   ├── __init__.py
│       │   ├── retry.py
│       │   ├── circuit_breaker.py
│       │   └── fallback.py
│       │
│       ├── observability/          # NEW directory
│       │   ├── __init__.py
│       │   ├── health.py
│       │   ├── metrics.py
│       │   └── logging.py
│       │
│       └── utils/
│           ├── __init__.py
│           └── config.py
│
├── tests/
│   ├── __init__.py
│   ├── unit/                       # NEW: explicit unit tests
│   ├── integration/                # NEW: explicit integration tests
│   └── e2e/                        # NEW: end-to-end tests
│
└── docs/
    ├── installation.md             # NEW
    ├── configuration.md            # NEW
    └── api-reference.md            # NEW
```

### 4.3 Updated Dependencies

```toml
[dependencies]
fastmcp = "^3.0"                    # Updated version
httpx = "^0.27"
pydantic = "^2.0"
pydantic-settings = "^2.0"         # NEW: typed configuration
beautifulsoup4 = "^4.12"
keyring = "^24.0"                   # NEW: system keychain
redis = "^5.0"                      # NEW: caching
structlog = "^24.0"                 # NEW: structured logging
prometheus-client = "^0.19"         # NEW: metrics
opentelemetry-api = "^1.22"         # NEW: tracing
opentelemetry-sdk = "^1.22"         # NEW: tracing
python-jose = "^3.3"                # NEW: JWT handling

[dev-dependencies]
pytest = "^8.0"
pytest-asyncio = "^0.23"
pytest-cov = "^4.1"
mypy = "^1.8"
ruff = "^0.1"
```

**Removed**:
- `playwright` - replaced by OAuth for cart operations
- `cryptography` - session encryption replaced by keychain

---

## 5. Prioritized Recommendations

### 5.1 Must-Have Changes (Blocking for Launch)

| # | Change | Effort | Risk if Skipped |
|---|--------|--------|-----------------|
| 1 | **Implement OAuth 2.1 with PKCE** | High | MCP spec non-compliance; client rejection |
| 2 | **Add health check endpoints** | Low | No automated recovery; operational blind spot |
| 3 | **Human-in-the-loop for cart/pickup** | Medium | Unintended purchases; trust issues |
| 4 | **Structured error handling** | Medium | Poor AI decision-making; support burden |
| 5 | **Tool annotations** | Low | Destructive actions without user awareness |
| 6 | **Docker containerization** | Medium | Deployment inconsistencies |

**Timeline**: Complete before any production deployment

### 5.2 Should-Have Improvements (High Value)

| # | Change | Effort | Value |
|---|--------|--------|-------|
| 7 | **Redis caching layer** | Medium | Performance, API load reduction |
| 8 | **Circuit breaker pattern** | Medium | Prevent cascading failures |
| 9 | **Prometheus metrics endpoint** | Low | Operational visibility |
| 10 | **Structured logging (stderr)** | Low | Production debugging |
| 11 | **Rate limiting** | Medium | Abuse prevention |
| 12 | **Dietary preference tools** | Medium | Personalization, differentiation |
| 13 | **System keychain for tokens** | Medium | Security posture |

**Timeline**: Complete within 2 weeks of launch

### 5.3 Could-Have Enhancements (Nice to Have)

| # | Change | Effort | Value |
|---|--------|--------|-------|
| 14 | **Recipe-to-cart tool** | High | Killer feature, differentiation |
| 15 | **Smart substitution explanations** | Medium | Trust building |
| 16 | **Local product discovery** | Low | Regional differentiation |
| 17 | **OpenTelemetry tracing** | Medium | Deep debugging |
| 18 | **Kubernetes deployment config** | Medium | Enterprise scaling |
| 19 | **Multi-platform documentation** | Medium | Adoption breadth |

**Timeline**: V1.5 or V2

---

## 6. Implementation Roadmap

### Phase 1: Production Foundation (Week 1-2)

**Goal**: Make current design production-compliant

**Tasks**:
1. Implement OAuth 2.1 authentication module
2. Add health check endpoints (/health/live, /health/ready)
3. Add tool annotations for all tools
4. Implement confirmation flow for cart/pickup tools
5. Refactor error handling with categories and retry metadata
6. Create Docker and docker-compose configuration
7. Set up structured logging to stderr

**Exit Criteria**: MCP Inspector validation passes; health checks functional

### Phase 2: Reliability & Observability (Week 3-4)

**Goal**: Production-ready resilience and monitoring

**Tasks**:
1. Implement circuit breaker for HEB API calls
2. Add Redis caching with appropriate TTLs
3. Implement rate limiting
4. Add Prometheus metrics endpoint
5. Integrate system keychain for token storage
6. Comprehensive integration testing
7. Load testing against performance targets

**Exit Criteria**:
- >99% success rate under load
- <100ms P95 latency for reads
- Cache hit rate >80%

### Phase 3: Differentiation Features (Week 5-6)

**Goal**: Competitive differentiation

**Tasks**:
1. Implement dietary preference management
2. Enhance product_find_alternatives with explanations
3. Add local product discovery resource
4. Begin recipe-to-cart prototype
5. Multi-platform documentation
6. Security audit preparation

**Exit Criteria**: Differentiation features functional; documentation complete

### Phase 4: Launch & Iterate (Week 7+)

**Goal**: Production launch and continuous improvement

**Tasks**:
1. Security audit and remediation
2. Beta user testing
3. Performance optimization based on real traffic
4. Recipe-to-cart refinement
5. Budget optimization research
6. Spanish language support research

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| HEB API changes break GraphQL client | Medium | High | Fallback scraper; versioned queries |
| OAuth integration delays | Medium | High | Early authentication team engagement |
| Recipe parsing accuracy | High | Medium | Start simple (URL parsing); iterate |
| Rate limiting by HEB | Medium | Medium | Caching; exponential backoff |
| Security vulnerabilities | Low | Critical | Security audit; keychain storage |
| Performance under load | Medium | High | Load testing; horizontal scaling |

---

## 8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| MCP Spec Compliance | 100% | MCP Inspector validation |
| Availability | >99.9% | Uptime monitoring |
| P95 Latency (reads) | <100ms | Prometheus metrics |
| P95 Latency (writes) | <500ms | Prometheus metrics |
| Error Rate | <0.1% | Prometheus metrics |
| Cache Hit Rate | >80% | Redis metrics |
| User Confirmation Rate | 100% for destructive ops | Audit logs |
| Documentation Coverage | All tools/resources | Manual review |

---

## Appendix A: Quick Reference Checklists

### Production Readiness Checklist

- [ ] OAuth 2.1 with PKCE implemented
- [ ] Health check endpoints functional
- [ ] Tool annotations on all tools
- [ ] Confirmation required for destructive actions
- [ ] Structured error handling with categories
- [ ] Docker containerization complete
- [ ] Structured logging to stderr
- [ ] Security credentials in system keychain
- [ ] Circuit breakers for external APIs
- [ ] Redis caching configured
- [ ] Rate limiting enabled
- [ ] Prometheus metrics endpoint
- [ ] Documentation for Claude Desktop + VS Code
- [ ] Integration tests passing
- [ ] Load tests meet performance targets

### Security Checklist

- [ ] No credentials in code or .env
- [ ] System keychain or secret manager for tokens
- [ ] OAuth 2.1 PKCE for user authentication
- [ ] JWT validation with signature verification
- [ ] Input validation on all tool parameters
- [ ] Error messages sanitized
- [ ] Rate limiting to prevent abuse
- [ ] Audit logging for user operations
- [ ] HTTPS enforced (via infrastructure)
- [ ] Dependencies scanned for vulnerabilities

---

## Sources

This synthesis draws from:

1. **Market Research**: `/Users/michaelwalker/Documents/HEB MCP/docs/research/market/research-successful-mcp-market.md`
2. **Technical Research**: `/Users/michaelwalker/Documents/HEB MCP/docs/research/technical/research-successful-mcp-technical.md`
3. **Current Design**: `/Users/michaelwalker/Documents/HEB MCP/docs/plans/2026-01-29-heb-mcp-design.md`

Key external references:
- MCP Specification 2025-11-25
- MCP Authorization Specification (March 2025)
- Kroger MCP implementation patterns
- GitHub MCP Server architecture
- FastMCP 3.0 documentation
