# Technical Research: Successful MCP Server Implementation Patterns

**Date**: 2026-01-29
**Requested By**: Project Planning
**Request**: Research technical implementation patterns of successful MCP servers, focusing on code architecture, authentication & security, reliability patterns, developer experience, and specific examples

## Executive Summary

Model Context Protocol (MCP) is rapidly maturing as an industry standard for connecting LLMs to external data sources and tools. Based on analysis of official implementations, successful community projects, and production best practices, several clear patterns emerge:

**Key Findings:**
1. **Framework Choice**: FastMCP dominates the ecosystem (powers ~70% of servers) due to superior developer experience, while the official SDK is preferred for fine-grained control
2. **Architecture**: Single-responsibility servers with clear separation of concerns consistently outperform monolithic implementations
3. **Security**: OAuth 2.1 with PKCE is the emerging standard, but credential storage remains a significant challenge across the ecosystem
4. **Reliability**: Production servers implement circuit breakers, exponential backoff, and comprehensive health checks as standard practice
5. **Developer Experience**: Containerization via Docker is becoming the de facto distribution method for production deployments

**Recommendation**: For HEB MCP, adopt FastMCP for rapid development, implement OAuth 2.1 with system keychain storage, containerize for deployment, and follow the three-layer observability pattern (protocol, tool, agent layers).

---

## Research Scope

**Questions Addressed**:
1. How do successful MCPs structure their code?
2. What are the authentication and security best practices?
3. What reliability patterns ensure production-grade quality?
4. How do successful MCPs optimize developer experience?
5. What can we learn from specific implementations?

**Context**: This research supports the HEB MCP server design to ensure we adopt proven patterns and avoid common pitfalls in the ecosystem.

---

## 1. Code Architecture Patterns

### 1.1 Framework Landscape

#### FastMCP Framework

**Ecosystem Dominance:**
- 22.4k GitHub stars, 1.7k forks
- Downloaded 1 million times daily
- Powers approximately 70% of MCP servers across all languages
- FastMCP 1.0 incorporated into official MCP SDK (2024)

**Core Philosophy:**
FastMCP emphasizes "composition over complexity" where best practices are the path of least resistance. Developers focus on business logic while the framework handles serialization, error management, and protocol compliance automatically.

**Basic Pattern:**
```python
from fastmcp import FastMCP

mcp = FastMCP("Server Name")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.resource("calculator://greet/{name}")
def greeting(name: str) -> str:
    return f"Hello, {name}!"

@mcp.prompt()
def help_prompt(topic: str) -> str:
    """Generate contextual help."""
    return f"Help information about {topic}"

if __name__ == "__main__":
    mcp.run()
```

**Key Features:**
- **Automatic Schema Generation**: Type hints automatically generate JSON schemas
- **Built-in Validation**: Parameter validation from type annotations
- **Async Support**: Native `async def` support for non-blocking I/O
- **Progress Tracking**: Context objects enable status reporting via `ctx.report_progress()`
- **Media Handling**: Image class supports binary data return

**When to Use FastMCP:**
- Rapid prototyping and development
- Standard MCP use cases without unusual requirements
- Teams prioritizing developer velocity
- Projects needing comprehensive documentation

#### Official MCP SDK

**Available Languages:**
TypeScript, Python, Go, Rust, Java, C#, PHP, Ruby, Swift

**TypeScript SDK Structure:**
```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server(
  {
    name: "example-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
      resources: {},
      prompts: {}
    },
  }
);

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const result = await executeTool(
      request.params.name,
      request.params.arguments
    );
    return {
      content: [{
        type: "text",
        text: JSON.stringify(result)
      }]
    };
  } catch (error) {
    return {
      isError: true,
      content: [{
        type: "text",
        text: error?.message || "Unknown error"
      }]
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

**When to Use Official SDK:**
- Maximum control over protocol implementation
- Custom architectural requirements
- Building framework abstractions
- Performance-critical implementations

### 1.2 Project Structure Patterns

#### Modular Go Architecture (GitHub MCP Server)

```
project/
├── cmd/
│   └── github-mcp-server/     # Entry point and CLI
├── internal/                   # Private packages
│   ├── auth/                  # Authentication logic
│   ├── tools/                 # Tool implementations
│   └── server/                # Server orchestration
├── pkg/                        # Public reusable packages
│   ├── github/                # GitHub API client
│   └── types/                 # Shared types
├── docs/                       # Documentation
│   ├── installation-guides/
│   └── server-configuration.md
├── e2e/                        # End-to-end tests
├── Dockerfile
└── README.md
```

**Principles Demonstrated:**
- Clear separation of public vs. private APIs
- Isolated authentication concerns
- Testable architecture with e2e coverage
- Documentation as first-class citizen

#### Python Project Structure (FastMCP Pattern)

```
project/
├── src/
│   ├── server.py              # Main server entry point
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py          # Search-related tools
│   │   └── cart.py            # Cart-related tools
│   ├── resources/
│   │   ├── __init__.py
│   │   └── store_locations.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── manager.py         # Token management
│   │   └── oauth.py           # OAuth flows
│   └── config.py              # Configuration
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

#### TypeScript/Node.js Structure

```
project/
├── src/
│   ├── index.ts               # Server entry point
│   ├── tools/
│   │   ├── index.ts
│   │   └── implementations/
│   ├── resources/
│   │   ├── index.ts
│   │   └── implementations/
│   ├── auth/
│   │   └── oauth-handler.ts
│   └── types/
│       └── index.ts
├── dist/                       # Compiled output
├── tests/
├── package.json
├── tsconfig.json
├── Dockerfile
└── README.md
```

### 1.3 Organization Best Practices

**Single Responsibility Principle:**
Each MCP server should have "one clear, well-defined purpose." This enables:
- Independent scaling
- Focused maintenance
- Isolated failure domains
- Clear ownership boundaries

**Anti-Pattern (Monolithic):**
```python
# DON'T: Single server handling everything
mcp = FastMCP("everything-server")

@mcp.tool
def query_database(): ...

@mcp.tool
def read_file(): ...

@mcp.tool
def send_email(): ...

@mcp.tool
def call_api(): ...
```

**Correct Pattern (Focused):**
```python
# DO: Separate servers for distinct domains
# database-mcp-server
mcp_db = FastMCP("database-server")

@mcp_db.tool
def query_database(): ...

# filesystem-mcp-server
mcp_fs = FastMCP("filesystem-server")

@mcp_fs.tool
def read_file(): ...

# email-mcp-server
mcp_email = FastMCP("email-server")

@mcp_email.tool
def send_email(): ...
```

### 1.4 Three Core Primitives Organization

#### Tools (Executable Functions)

**Definition**: Functions that perform actions or computations.

**Implementation Pattern:**
```python
from pydantic import BaseModel, Field
from typing import Literal

class SearchParams(BaseModel):
    query: str = Field(description="Search query")
    limit: int = Field(default=10, ge=1, le=100)
    category: Literal["all", "produce", "meat", "dairy"] = "all"

@mcp.tool
def search_products(params: SearchParams) -> list[dict]:
    """
    Search for products in the catalog.

    Returns a list of matching products with name, price, and availability.
    """
    # Validation happens automatically via Pydantic
    results = perform_search(
        query=params.query,
        limit=params.limit,
        category=params.category
    )
    return results
```

**Best Practices:**
- Use Pydantic models for complex parameters
- Provide detailed docstrings (visible to LLM)
- Use snake_case naming (best for GPT-4o tokenization)
- Return structured data (dicts/lists) not strings
- Implement proper error handling

#### Resources (Data Entities)

**Definition**: File-like data that can be read by clients.

**Static Resources:**
```python
@mcp.resource("heb://config/store-hours")
def store_hours() -> str:
    """Standard store operating hours."""
    return json.dumps({
        "weekday": "6:00 AM - 11:00 PM",
        "weekend": "7:00 AM - 10:00 PM"
    })
```

**Dynamic Resources (Path Parameters):**
```python
@mcp.resource("heb://stores/{store_id}/inventory/{sku}")
def product_inventory(store_id: str, sku: str) -> str:
    """
    Get real-time inventory for a specific product at a store.
    """
    inventory = fetch_inventory(store_id, sku)
    return json.dumps({
        "store_id": store_id,
        "sku": sku,
        "in_stock": inventory.quantity > 0,
        "quantity": inventory.quantity,
        "last_updated": inventory.timestamp.isoformat()
    })
```

**Resource URI Patterns:**
- Use consistent scheme (e.g., `heb://`)
- Follow hierarchical structure
- Include version in path if needed: `heb://v1/stores/{id}`
- Make URIs self-documenting

#### Prompts (Templates)

**Definition**: Pre-written templates that guide AI interactions.

**Basic Prompt:**
```python
@mcp.prompt()
def weekly_meal_planner() -> str:
    """Generate a weekly meal plan with H-E-B products."""
    return """
    Create a healthy weekly meal plan for a family of 4.

    Requirements:
    - Use seasonal produce available at H-E-B
    - Include breakfast, lunch, and dinner
    - Provide a shopping list organized by store section
    - Stay within a $200 weekly budget
    - Include at least 2 vegetarian meals
    """
```

**Parameterized Prompt:**
```python
from mcp.types import PromptMessage, TextContent

@mcp.prompt()
def recipe_suggestions(
    dietary_restrictions: str,
    budget: float,
    servings: int
) -> list[PromptMessage]:
    """Suggest recipes based on preferences and constraints."""

    prompt_text = f"""
    Suggest 5 recipes that meet these criteria:

    Dietary Restrictions: {dietary_restrictions}
    Budget per recipe: ${budget}
    Servings needed: {servings}

    For each recipe, provide:
    1. Recipe name
    2. Estimated cost at H-E-B
    3. Key ingredients (with H-E-B product codes)
    4. Preparation time
    5. Cooking instructions
    """

    return [
        PromptMessage(
            role="user",
            content=TextContent(type="text", text=prompt_text)
        )
    ]
```

---

## 2. Authentication & Security

### 2.1 OAuth 2.1 Implementation Patterns

#### Protocol Overview

**MCP Authorization Specification (March 2025):**
- Standardizes authorization using OAuth 2.1
- PKCE (Proof Key for Code Exchange) mandatory for all clients
- Based on RFC 9068 (JWT Access Tokens)
- Protected Resource Metadata (RFC 9728) for server discovery

**Key Requirements:**
- MCP servers MUST implement OAuth 2.0 Protected Resource Metadata
- MCP clients MUST use this metadata for authorization server discovery
- All HTTP-based communication MUST use HTTPS
- JWT signatures validated via JWKS
- Token validation includes issuer, audience, expiry, and scopes

#### OAuth 2.1 Flow Pattern

**1. Discovery Phase:**
```python
# Server exposes metadata endpoint
@app.get("/.well-known/oauth-protected-resource")
def resource_metadata():
    return {
        "resource": "https://heb-mcp.example.com",
        "authorization_servers": [
            "https://auth.heb.com"
        ],
        "scopes_supported": [
            "product:read",
            "cart:write",
            "order:read"
        ],
        "bearer_methods_supported": ["header"],
        "resource_documentation": "https://docs.heb-mcp.example.com"
    }
```

**2. Authorization Request (with PKCE):**
```python
import secrets
import hashlib
import base64

def generate_pkce_challenge():
    """Generate PKCE code verifier and challenge."""
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode('utf-8').rstrip('=')

    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')

    return code_verifier, code_challenge

# Client initiates flow
code_verifier, code_challenge = generate_pkce_challenge()

auth_url = (
    f"{auth_server}/authorize?"
    f"response_type=code&"
    f"client_id={client_id}&"
    f"redirect_uri={redirect_uri}&"
    f"scope=product:read cart:write&"
    f"code_challenge={code_challenge}&"
    f"code_challenge_method=S256&"
    f"state={random_state}"
)
```

**3. Token Exchange:**
```python
import httpx

async def exchange_code_for_token(
    authorization_code: str,
    code_verifier: str
) -> dict:
    """Exchange authorization code for access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{auth_server}/token",
            data={
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "code_verifier": code_verifier
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response.json()
```

**4. Token Validation:**
```python
from jose import jwt, jwk
import httpx

async def validate_access_token(token: str) -> dict:
    """Validate JWT access token."""
    try:
        # Fetch JWKS
        async with httpx.AsyncClient() as client:
            jwks_response = await client.get(f"{auth_server}/.well-known/jwks.json")
            jwks = jwks_response.json()

        # Validate token
        claims = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience="https://heb-mcp.example.com",
            issuer=auth_server
        )

        # Check expiration
        if claims["exp"] < time.time():
            raise ValueError("Token expired")

        # Verify required scopes
        token_scopes = claims.get("scope", "").split()
        # Validate scopes match resource requirements

        return claims

    except jwt.JWTError as e:
        raise ValueError(f"Invalid token: {e}")
```

#### Kroger MCP OAuth Pattern (Real-World Example)

**Dual-Token Strategy:**
```python
class AuthManager:
    """
    Manages OAuth2 authentication with dual-token strategy:
    - Client credentials for general API access
    - Authorization code grant for user-specific operations
    """

    def __init__(self, config):
        self.client_id = config.KROGER_CLIENT_ID
        self.client_secret = config.KROGER_CLIENT_SECRET
        self.redirect_uri = config.KROGER_REDIRECT_URI
        self.user_refresh_token = config.KROGER_USER_REFRESH_TOKEN

        self.client_token = None
        self.user_token = None

    async def get_client_token(self) -> str:
        """Get client credentials token for general data access."""
        if self.client_token and not self._is_expired(self.client_token):
            return self.client_token["access_token"]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.kroger.com/v1/connect/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "scope": "product.compact"
                },
                auth=(self.client_id, self.client_secret)
            )
            self.client_token = response.json()
            return self.client_token["access_token"]

    async def get_user_token(self) -> str:
        """Get user token for cart operations."""
        if self.user_token and not self._is_expired(self.user_token):
            return self.user_token["access_token"]

        if not self.user_refresh_token:
            raise ValueError(
                "User authentication required. "
                "Please complete OAuth2 authorization flow."
            )

        # Attempt refresh
        try:
            self.user_token = await self._refresh_token(
                self.user_refresh_token
            )
            return self.user_token["access_token"]
        except Exception as e:
            raise ValueError(
                f"Token refresh failed: {e}. "
                "Please re-authorize the application."
            )

    async def _refresh_token(self, refresh_token: str) -> dict:
        """Refresh an expired access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.kroger.com/v1/connect/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token
                },
                auth=(self.client_id, self.client_secret)
            )
            return response.json()

    def _is_expired(self, token_data: dict) -> bool:
        """Check if token is expired."""
        expires_at = token_data.get("expires_at", 0)
        return time.time() >= expires_at - 60  # 60s buffer
```

**Browser-Based Authorization Flow:**
```python
def initiate_user_authorization():
    """
    CLI-mediated browser auth to avoid local web server.
    """
    auth_url = (
        f"https://api.kroger.com/v1/connect/oauth2/authorize?"
        f"scope=cart.basic:write product.compact&"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri=http://localhost:8080/callback"
    )

    print(f"Please visit this URL to authorize: {auth_url}")
    print("\nAfter authorization, you'll be redirected to localhost.")
    print("Copy the 'code' parameter from the URL and paste it here.")

    authorization_code = input("Authorization code: ")

    # Exchange code for tokens
    token_response = requests.post(
        "https://api.kroger.com/v1/connect/oauth2/token",
        data={
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": "http://localhost:8080/callback"
        },
        auth=(client_id, client_secret)
    )

    tokens = token_response.json()

    print("\nSave this refresh token to your config:")
    print(f"KROGER_USER_REFRESH_TOKEN={tokens['refresh_token']}")
```

### 2.2 Session Management

#### Token Storage Patterns

**In-Memory Storage (Development):**
```python
class InMemoryTokenStore:
    """Simple in-memory token storage for development."""

    def __init__(self):
        self._tokens = {}

    def store(self, user_id: str, token_data: dict):
        self._tokens[user_id] = token_data

    def retrieve(self, user_id: str) -> dict | None:
        return self._tokens.get(user_id)

    def delete(self, user_id: str):
        self._tokens.pop(user_id, None)
```

**Redis-Based Storage (Production):**
```python
import redis.asyncio as redis
import json

class RedisTokenStore:
    """Production token storage with Redis."""

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def store(
        self,
        user_id: str,
        token_data: dict,
        ttl: int = 3600
    ):
        """Store token with TTL matching token expiration."""
        await self.redis.setex(
            f"token:{user_id}",
            ttl,
            json.dumps(token_data)
        )

    async def retrieve(self, user_id: str) -> dict | None:
        """Retrieve token if not expired."""
        data = await self.redis.get(f"token:{user_id}")
        return json.loads(data) if data else None

    async def delete(self, user_id: str):
        """Revoke token."""
        await self.redis.delete(f"token:{user_id}")

    async def extend_ttl(self, user_id: str, ttl: int):
        """Extend token TTL on activity."""
        await self.redis.expire(f"token:{user_id}", ttl)
```

#### Session Middleware Pattern

```python
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token_store: RedisTokenStore = Depends(get_token_store)
) -> dict:
    """
    Validate access token and return user claims.
    """
    token = credentials.credentials

    try:
        # Validate JWT
        claims = await validate_access_token(token)

        # Check if token is revoked
        user_id = claims["sub"]
        stored_token = await token_store.retrieve(user_id)

        if not stored_token or stored_token["access_token"] != token:
            raise HTTPException(
                status_code=401,
                detail="Token revoked or invalid"
            )

        # Extend session on activity
        await token_store.extend_ttl(user_id, ttl=3600)

        return claims

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )

@app.post("/tools/add_to_cart")
async def add_to_cart(
    request: AddToCartRequest,
    user: dict = Depends(get_current_user)
):
    """Protected endpoint requiring user authentication."""
    # user contains validated claims
    result = await cart_service.add_item(
        user_id=user["sub"],
        item=request.item
    )
    return result
```

### 2.3 Secure Credential Storage

#### The Problem

**Current Ecosystem Issues:**
- 48% of MCP servers recommend `.env` files or hardcoded credentials
- Many servers store long-term API keys in plaintext
- Insecure file permissions (world-readable) common
- Credentials aggregated in single files increase blast radius

#### Recommended Solutions

**1. System Keychain/Credential Manager:**

**macOS Keychain:**
```python
import keyring

def store_credential(service: str, username: str, password: str):
    """Store credential in system keychain."""
    keyring.set_password(service, username, password)

def retrieve_credential(service: str, username: str) -> str:
    """Retrieve credential from system keychain."""
    return keyring.get_password(service, username)

# Usage
store_credential("heb-mcp", "api_key", "secret_api_key_value")
api_key = retrieve_credential("heb-mcp", "api_key")
```

**Windows Credential Manager:**
```python
import keyring
from keyrings.alt import Windows

# Use Windows backend explicitly
keyring.set_keyring(Windows.EncryptedKeyring())
keyring.set_password("heb-mcp", "api_key", "secret_value")
```

**2. Secret Management Tools:**

**1Password CLI:**
```bash
# Store secret in 1Password
op item create \
  --category='API Credential' \
  --title='HEB API Key' \
  api_key[password]="secret_value"

# Inject into environment
op run --env-file=".env.1password" -- python server.py
```

**.env.1password file:**
```
HEB_API_KEY=op://Private/HEB API Key/api_key
HEB_API_SECRET=op://Private/HEB API Key/api_secret
```

**Infisical CLI:**
```bash
# Login to Infisical
infisical login

# Run server with injected secrets
infisical run -- python server.py
```

**Configuration Pattern:**
```python
import os
from typing import Optional

class Config:
    """Configuration with secrets from multiple sources."""

    def __init__(self):
        # Try environment variables first (injected by secret manager)
        self.api_key = os.getenv("HEB_API_KEY")

        # Fall back to system keychain
        if not self.api_key:
            try:
                import keyring
                self.api_key = keyring.get_password("heb-mcp", "api_key")
            except Exception:
                pass

        # Fail fast if no credential found
        if not self.api_key:
            raise ValueError(
                "HEB_API_KEY not found. Configure via:\n"
                "1. Environment variable: HEB_API_KEY=xxx\n"
                "2. System keychain: keyring.set_password('heb-mcp', 'api_key', 'xxx')\n"
                "3. Secret manager (1Password, Infisical, etc.)"
            )
```

**3. Dynamic/Ephemeral Credentials:**

```python
import boto3
from datetime import datetime, timedelta

class TemporaryCredentialProvider:
    """Generate short-lived credentials on-demand."""

    def __init__(self):
        self.sts_client = boto3.client('sts')

    def get_temporary_credentials(
        self,
        role_arn: str,
        session_name: str,
        duration: int = 3600  # 1 hour
    ) -> dict:
        """
        Assume IAM role and return temporary credentials.
        """
        response = self.sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name,
            DurationSeconds=duration
        )

        credentials = response['Credentials']

        return {
            "access_key": credentials['AccessKeyId'],
            "secret_key": credentials['SecretAccessKey'],
            "session_token": credentials['SessionToken'],
            "expiration": credentials['Expiration'].isoformat()
        }

    def credentials_expired(self, expiration: str) -> bool:
        """Check if credentials are expired."""
        exp_time = datetime.fromisoformat(expiration)
        return datetime.now() >= exp_time - timedelta(minutes=5)
```

**Best Practice: Never Commit Secrets:**

**.gitignore:**
```
# Secrets and credentials
.env
.env.local
*.key
*.pem
config/secrets.json
credentials.json

# System-specific
.keyring/
```

**Config Template (Commit This):**
```yaml
# config.template.yaml
api:
  base_url: "https://api.heb.com"
  timeout: 30

auth:
  # DO NOT put actual credentials here
  # Use environment variables or secret manager
  client_id: "${HEB_CLIENT_ID}"
  client_secret: "${HEB_CLIENT_SECRET}"
```

### 2.4 Security Best Practices Summary

**Defense in Depth Layers:**

1. **Network Layer**
   - HTTPS mandatory for all communication
   - Local-only binding for development
   - Rate limiting and DDoS protection

2. **Authentication Layer**
   - OAuth 2.1 with PKCE
   - JWT validation with JWKS
   - Short-lived access tokens (15-60 minutes)
   - Refresh token rotation

3. **Authorization Layer**
   - Scope-based access control
   - Principle of least privilege
   - Per-resource permission checks

4. **Input Validation Layer**
   - Schema enforcement (Pydantic)
   - SQL injection prevention
   - Path traversal protection
   - Size limits on uploads

5. **Output Sanitization Layer**
   - Remove sensitive data from logs
   - Sanitize error messages
   - Content Security Policy headers

**Security Checklist:**
- [ ] HTTPS enforced on all endpoints
- [ ] OAuth 2.1 with PKCE implemented
- [ ] Secrets stored in system keychain or secret manager
- [ ] JWT validation with signature verification
- [ ] Input validation on all parameters
- [ ] Rate limiting configured
- [ ] Audit logging enabled
- [ ] Error messages don't leak system details
- [ ] Dependencies scanned for vulnerabilities
- [ ] Security headers configured (CSP, HSTS, etc.)

---

## 3. Reliability Patterns

### 3.1 Retry Logic and Exponential Backoff

#### Pattern Overview

Exponential backoff increases wait time between retries after each failure (2^attempt × base_delay + jitter), preventing "thundering herd" problems where all clients retry simultaneously.

**Configuration Recommendations:**
- **Max Attempts**: 3-5 retries
- **Base Delay**: 1.0 seconds
- **Max Delay**: 60 seconds
- **Jitter**: 0.5 (50% randomization)

#### Implementation Pattern

```python
import asyncio
import random
from typing import TypeVar, Callable, Awaitable
from functools import wraps

T = TypeVar('T')

class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: float = 0.5
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

def with_retry(
    config: RetryConfig = RetryConfig(),
    retry_on: tuple = (Exception,)
):
    """
    Decorator for automatic retry with exponential backoff.

    Only retries on specified exceptions (default: all).
    Preserves idempotency - only use for safe operations.
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)

                except retry_on as e:
                    last_exception = e

                    # Don't retry on last attempt
                    if attempt == config.max_attempts - 1:
                        break

                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )

                    # Add jitter to prevent thundering herd
                    jitter = delay * config.jitter * random.random()
                    final_delay = delay + jitter

                    # Log retry attempt
                    print(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {final_delay:.2f}s...",
                        file=sys.stderr
                    )

                    await asyncio.sleep(final_delay)

            # All retries exhausted
            raise last_exception

        return wrapper
    return decorator
```

#### Usage Example

```python
import httpx

# Only retry on specific transient errors
@with_retry(
    config=RetryConfig(max_attempts=3, base_delay=1.0),
    retry_on=(httpx.TimeoutException, httpx.NetworkError)
)
async def fetch_product_data(product_id: str) -> dict:
    """
    Fetch product data with automatic retries on network errors.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.heb.com/products/{product_id}",
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()

# Usage
try:
    product = await fetch_product_data("12345")
except Exception as e:
    # All retries failed
    return {
        "isError": True,
        "content": [{
            "type": "text",
            "text": f"Failed to fetch product after retries: {e}"
        }]
    }
```

### 3.2 Circuit Breaker Pattern

#### Pattern Overview

Circuit breakers prevent repeated calls to failing services, giving them time to recover. They have three states:
- **Closed**: Normal operation, requests pass through
- **Open**: Service failing, requests rejected immediately
- **Half-Open**: Testing recovery with limited requests

**Configuration:**
- **Failure Threshold**: 5 failures
- **Success Threshold**: 2 successes to close
- **Timeout**: 30 seconds before trying half-open
- **Window**: 60 seconds for counting failures

#### Implementation

```python
import asyncio
from enum import Enum
from datetime import datetime, timedelta
from collections import deque

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 30.0,
        window: float = 60.0
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.window = window

        self.state = CircuitState.CLOSED
        self.failures = deque()
        self.successes = 0
        self.last_failure_time = None

    def _clean_old_failures(self):
        """Remove failures outside the time window."""
        cutoff = datetime.now() - timedelta(seconds=self.window)
        while self.failures and self.failures[0] < cutoff:
            self.failures.popleft()

    def can_attempt(self) -> bool:
        """Check if request can proceed."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if timeout elapsed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.successes = 0
                    return True
            return False

        # HALF_OPEN: allow limited requests
        return True

    def record_success(self):
        """Record successful request."""
        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failures.clear()
                self.last_failure_time = None

    def record_failure(self):
        """Record failed request."""
        self._clean_old_failures()
        self.failures.append(datetime.now())
        self.last_failure_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery - back to open
            self.state = CircuitState.OPEN
            self.successes = 0
        elif len(self.failures) >= self.failure_threshold:
            # Threshold exceeded - open circuit
            self.state = CircuitState.OPEN

    def get_status(self) -> dict:
        """Get current circuit breaker status."""
        self._clean_old_failures()
        return {
            "state": self.state.value,
            "failures": len(self.failures),
            "failure_threshold": self.failure_threshold,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None
        }

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass

def with_circuit_breaker(breaker: CircuitBreaker):
    """Decorator to apply circuit breaker pattern."""
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            if not breaker.can_attempt():
                raise CircuitBreakerOpenError(
                    f"Circuit breaker open. Service unavailable. "
                    f"Status: {breaker.get_status()}"
                )

            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                raise

        return wrapper
    return decorator
```

#### Usage Example

```python
# Create circuit breaker instance
api_breaker = CircuitBreaker(
    failure_threshold=5,
    success_threshold=2,
    timeout=30.0
)

@with_circuit_breaker(api_breaker)
async def call_external_api(endpoint: str) -> dict:
    """Call external API with circuit breaker protection."""
    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, timeout=10.0)
        response.raise_for_status()
        return response.json()

# MCP tool implementation
@mcp.tool
async def search_products(query: str) -> str:
    """Search products with circuit breaker protection."""
    try:
        results = await call_external_api(
            f"https://api.heb.com/search?q={query}"
        )
        return json.dumps(results)

    except CircuitBreakerOpenError as e:
        # Circuit open - return cached data or error
        return json.dumps({
            "error": "Service temporarily unavailable",
            "message": "Product search is experiencing issues. Please try again later.",
            "use_cache": True
        })
    except Exception as e:
        return json.dumps({
            "error": "Search failed",
            "message": str(e)
        })

# Health check endpoint exposes breaker status
@app.get("/health/circuit-breakers")
def circuit_breaker_status():
    return {
        "api": api_breaker.get_status()
    }
```

### 3.3 Fallback Strategies

#### Graceful Degradation Pattern

```python
from typing import Optional
import aioredis

class ProductService:
    """Product service with fallback strategies."""

    def __init__(self, cache: aioredis.Redis):
        self.cache = cache
        self.breaker = CircuitBreaker()

    async def get_product(self, product_id: str) -> dict:
        """
        Get product with fallback chain:
        1. Try live API
        2. Fall back to cache
        3. Return minimal placeholder
        """
        try:
            # Try primary source
            product = await self._fetch_from_api(product_id)
            # Update cache on success
            await self._cache_product(product_id, product)
            return product

        except CircuitBreakerOpenError:
            # Circuit open - use cache immediately
            cached = await self._get_from_cache(product_id)
            if cached:
                cached["_source"] = "cache"
                cached["_warning"] = "Live data unavailable"
                return cached
            return self._placeholder(product_id)

        except Exception as e:
            # API error - try cache
            cached = await self._get_from_cache(product_id)
            if cached:
                cached["_source"] = "cache"
                cached["_warning"] = f"Live data error: {e}"
                return cached

            # Last resort - minimal data
            return self._placeholder(product_id)

    @with_circuit_breaker(breaker)
    async def _fetch_from_api(self, product_id: str) -> dict:
        """Fetch from primary API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.heb.com/products/{product_id}"
            )
            response.raise_for_status()
            return response.json()

    async def _get_from_cache(self, product_id: str) -> Optional[dict]:
        """Retrieve from cache."""
        cached = await self.cache.get(f"product:{product_id}")
        return json.loads(cached) if cached else None

    async def _cache_product(self, product_id: str, product: dict):
        """Cache product data."""
        await self.cache.setex(
            f"product:{product_id}",
            3600,  # 1 hour TTL
            json.dumps(product)
        )

    def _placeholder(self, product_id: str) -> dict:
        """Return minimal placeholder when all sources fail."""
        return {
            "_source": "placeholder",
            "_warning": "Product data unavailable",
            "product_id": product_id,
            "name": "Product information unavailable",
            "available": False
        }
```

#### Stale-While-Revalidate Pattern

```python
class CacheWithRevalidation:
    """Cache that serves stale data while fetching fresh data."""

    def __init__(self, cache: aioredis.Redis):
        self.cache = cache

    async def get_or_fetch(
        self,
        key: str,
        fetch_func: Callable[[], Awaitable[dict]],
        ttl: int = 3600,
        stale_ttl: int = 7200
    ) -> tuple[dict, bool]:
        """
        Get from cache or fetch.
        Returns (data, is_fresh) tuple.
        """
        # Try cache first
        cached_data = await self.cache.get(f"data:{key}")
        timestamp = await self.cache.get(f"timestamp:{key}")

        if cached_data:
            age = time.time() - float(timestamp or 0)

            # Fresh data - return immediately
            if age < ttl:
                return json.loads(cached_data), True

            # Stale but usable - return and revalidate in background
            if age < stale_ttl:
                asyncio.create_task(
                    self._revalidate(key, fetch_func, ttl)
                )
                data = json.loads(cached_data)
                data["_cache_age"] = int(age)
                return data, False

        # No cache or too stale - fetch synchronously
        try:
            fresh_data = await fetch_func()
            await self._store(key, fresh_data, ttl)
            return fresh_data, True
        except Exception as e:
            # Fetch failed - return stale if available
            if cached_data:
                data = json.loads(cached_data)
                data["_error"] = f"Revalidation failed: {e}"
                return data, False
            raise

    async def _revalidate(
        self,
        key: str,
        fetch_func: Callable,
        ttl: int
    ):
        """Background revalidation."""
        try:
            fresh_data = await fetch_func()
            await self._store(key, fresh_data, ttl)
        except Exception as e:
            # Log but don't fail - stale data already served
            print(f"Revalidation failed for {key}: {e}", file=sys.stderr)

    async def _store(self, key: str, data: dict, ttl: int):
        """Store data with timestamp."""
        await self.cache.setex(f"data:{key}", ttl * 2, json.dumps(data))
        await self.cache.setex(f"timestamp:{key}", ttl * 2, str(time.time()))
```

### 3.4 Health Check Implementation

#### Comprehensive Health Checks

```python
from enum import Enum
from fastapi import FastAPI, status
from pydantic import BaseModel

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class ComponentHealth(BaseModel):
    status: HealthStatus
    message: str
    latency_ms: Optional[float] = None
    details: Optional[dict] = None

class HealthCheckResponse(BaseModel):
    status: HealthStatus
    timestamp: str
    components: dict[str, ComponentHealth]

class HealthChecker:
    """Comprehensive health check implementation."""

    def __init__(
        self,
        db_client,
        cache_client,
        api_circuit_breaker: CircuitBreaker
    ):
        self.db = db_client
        self.cache = cache_client
        self.api_breaker = api_circuit_breaker

    async def liveness_check(self) -> bool:
        """
        Liveness check - is the process alive?
        Returns immediately, doesn't check dependencies.
        """
        return True

    async def readiness_check(self) -> HealthCheckResponse:
        """
        Readiness check - can we handle requests?
        Checks all critical dependencies.
        """
        components = {}

        # Check database
        components["database"] = await self._check_database()

        # Check cache
        components["cache"] = await self._check_cache()

        # Check external API circuit breaker
        components["external_api"] = self._check_circuit_breaker()

        # Check disk space
        components["disk"] = self._check_disk_space()

        # Check memory
        components["memory"] = self._check_memory()

        # Determine overall status
        overall_status = self._compute_overall_status(components)

        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            components=components
        )

    async def _check_database(self) -> ComponentHealth:
        """Check database connectivity and latency."""
        try:
            start = time.time()
            # Execute simple query
            await self.db.execute("SELECT 1")
            latency = (time.time() - start) * 1000

            if latency > 1000:  # > 1s is degraded
                return ComponentHealth(
                    status=HealthStatus.DEGRADED,
                    message="Database slow",
                    latency_ms=latency
                )

            return ComponentHealth(
                status=HealthStatus.HEALTHY,
                message="Database operational",
                latency_ms=latency
            )

        except Exception as e:
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message=f"Database unavailable: {e}"
            )

    async def _check_cache(self) -> ComponentHealth:
        """Check cache connectivity."""
        try:
            start = time.time()
            await self.cache.ping()
            latency = (time.time() - start) * 1000

            return ComponentHealth(
                status=HealthStatus.HEALTHY,
                message="Cache operational",
                latency_ms=latency
            )

        except Exception as e:
            # Cache failure is degraded, not unhealthy
            return ComponentHealth(
                status=HealthStatus.DEGRADED,
                message=f"Cache unavailable (using fallback): {e}"
            )

    def _check_circuit_breaker(self) -> ComponentHealth:
        """Check circuit breaker status."""
        breaker_status = self.api_breaker.get_status()

        if breaker_status["state"] == "open":
            return ComponentHealth(
                status=HealthStatus.DEGRADED,
                message="External API circuit breaker open",
                details=breaker_status
            )

        return ComponentHealth(
            status=HealthStatus.HEALTHY,
            message="External API available",
            details=breaker_status
        )

    def _check_disk_space(self) -> ComponentHealth:
        """Check available disk space."""
        import shutil

        stat = shutil.disk_usage("/")
        percent_used = (stat.used / stat.total) * 100

        if percent_used > 90:
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message=f"Disk space critical: {percent_used:.1f}% used",
                details={"percent_used": percent_used}
            )
        elif percent_used > 80:
            return ComponentHealth(
                status=HealthStatus.DEGRADED,
                message=f"Disk space low: {percent_used:.1f}% used",
                details={"percent_used": percent_used}
            )

        return ComponentHealth(
            status=HealthStatus.HEALTHY,
            message=f"Disk space OK: {percent_used:.1f}% used",
            details={"percent_used": percent_used}
        )

    def _check_memory(self) -> ComponentHealth:
        """Check memory usage."""
        import psutil

        memory = psutil.virtual_memory()
        percent_used = memory.percent

        if percent_used > 90:
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                message=f"Memory critical: {percent_used}% used",
                details={"percent_used": percent_used}
            )
        elif percent_used > 80:
            return ComponentHealth(
                status=HealthStatus.DEGRADED,
                message=f"Memory high: {percent_used}% used",
                details={"percent_used": percent_used}
            )

        return ComponentHealth(
            status=HealthStatus.HEALTHY,
            message=f"Memory OK: {percent_used}% used",
            details={"percent_used": percent_used}
        )

    def _compute_overall_status(
        self,
        components: dict[str, ComponentHealth]
    ) -> HealthStatus:
        """Compute overall health from component health."""
        statuses = [c.status for c in components.values()]

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

# FastAPI endpoints
app = FastAPI()

@app.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness():
    """Liveness probe for Kubernetes."""
    return {"status": "alive"}

@app.get("/health/ready", response_model=HealthCheckResponse)
async def readiness(health_checker: HealthChecker = Depends(get_health_checker)):
    """Readiness probe with detailed component status."""
    health = await health_checker.readiness_check()

    # Set HTTP status based on health
    status_code = {
        HealthStatus.HEALTHY: status.HTTP_200_OK,
        HealthStatus.DEGRADED: status.HTTP_200_OK,  # Still accepting traffic
        HealthStatus.UNHEALTHY: status.HTTP_503_SERVICE_UNAVAILABLE
    }[health.status]

    return Response(
        content=health.json(),
        media_type="application/json",
        status_code=status_code
    )
```

### 3.5 Monitoring and Observability

#### Three-Layer Observability Pattern

**Layer 1: Protocol Layer**
Monitors JSON-RPC 2.0 protocol health over transport (STDIO, WebSocket, HTTP+SSE).

**Layer 2: Tool Layer**
Tracks tool performance using SRE "Golden Signals": Latency, Traffic, Errors, Saturation.

**Layer 3: Agent/Application Layer**
Monitors autonomous recovery and agent interaction patterns.

#### OpenTelemetry Integration

```python
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# Setup tracing
trace_provider = TracerProvider()
trace_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
)
trace.set_tracer_provider(trace_provider)

# Setup metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://localhost:4317")
)
meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Instrument FastAPI and httpx
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()

# Custom metrics
meter = metrics.get_meter(__name__)
tool_calls_counter = meter.create_counter(
    "mcp.tool.calls",
    description="Number of tool calls"
)
tool_duration_histogram = meter.create_histogram(
    "mcp.tool.duration",
    description="Tool execution duration in seconds"
)
tool_errors_counter = meter.create_counter(
    "mcp.tool.errors",
    description="Number of tool errors"
)

# Custom instrumentation
tracer = trace.get_tracer(__name__)

@mcp.tool
async def search_products(query: str) -> str:
    """Search products with full observability."""

    # Start span
    with tracer.start_as_current_span("search_products") as span:
        span.set_attribute("query", query)
        span.set_attribute("tool.name", "search_products")

        start_time = time.time()

        try:
            # Execute search
            results = await product_service.search(query)

            # Record metrics
            duration = time.time() - start_time
            tool_calls_counter.add(1, {"tool": "search_products", "status": "success"})
            tool_duration_histogram.record(duration, {"tool": "search_products"})

            # Add span attributes
            span.set_attribute("result.count", len(results))
            span.set_attribute("duration.seconds", duration)

            return json.dumps(results)

        except Exception as e:
            # Record error
            duration = time.time() - start_time
            tool_calls_counter.add(1, {"tool": "search_products", "status": "error"})
            tool_errors_counter.add(1, {"tool": "search_products", "error": type(e).__name__})
            tool_duration_histogram.record(duration, {"tool": "search_products"})

            # Add error to span
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            span.record_exception(e)

            raise
```

#### Structured Logging

```python
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@mcp.tool
async def add_to_cart(product_id: str, quantity: int) -> str:
    """Add item to cart with structured logging."""

    log = logger.bind(
        tool="add_to_cart",
        product_id=product_id,
        quantity=quantity
    )

    log.info("tool_call_started")

    try:
        result = await cart_service.add_item(product_id, quantity)

        log.info(
            "tool_call_completed",
            cart_id=result["cart_id"],
            total_items=result["total_items"]
        )

        return json.dumps(result)

    except Exception as e:
        log.error(
            "tool_call_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

#### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Define metrics
tool_calls = Counter(
    'mcp_tool_calls_total',
    'Total number of tool calls',
    ['tool_name', 'status']
)

tool_duration = Histogram(
    'mcp_tool_duration_seconds',
    'Tool execution duration',
    ['tool_name'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
)

active_connections = Gauge(
    'mcp_active_connections',
    'Number of active MCP connections'
)

circuit_breaker_state = Gauge(
    'mcp_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=half-open, 2=open)',
    ['service']
)

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

# Update metrics in middleware
@app.middleware("http")
async def track_metrics(request: Request, call_next):
    active_connections.inc()
    try:
        response = await call_next(request)
        return response
    finally:
        active_connections.dec()
```

---

## 4. Developer Experience

### 4.1 Configuration Management

#### Environment-Based Configuration

**Configuration Hierarchy:**
1. Environment variables (highest priority)
2. `.env` file
3. `config.yaml`
4. Default values (lowest priority)

**Implementation Pattern:**
```python
from pydantic import BaseSettings, Field, validator
from typing import Optional, Literal
import os

class DatabaseConfig(BaseSettings):
    """Database configuration."""
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    database: str = Field(..., env="DB_NAME")
    username: str = Field(..., env="DB_USERNAME")
    password: str = Field(..., env="DB_PASSWORD")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")

    class Config:
        env_file = ".env"
        env_prefix = ""

class CacheConfig(BaseSettings):
    """Cache configuration."""
    redis_url: str = Field(..., env="REDIS_URL")
    ttl: int = Field(default=3600, env="CACHE_TTL")

    class Config:
        env_file = ".env"

class AuthConfig(BaseSettings):
    """Authentication configuration."""
    client_id: str = Field(..., env="HEB_CLIENT_ID")
    client_secret: str = Field(..., env="HEB_CLIENT_SECRET")
    redirect_uri: str = Field(..., env="HEB_REDIRECT_URI")
    auth_server_url: str = Field(..., env="HEB_AUTH_SERVER_URL")

    class Config:
        env_file = ".env"

class ServerConfig(BaseSettings):
    """Main server configuration."""
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        env="ENVIRONMENT"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        env="LOG_LEVEL"
    )

    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    auth: AuthConfig = Field(default_factory=AuthConfig)

    # Feature flags
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_tracing: bool = Field(default=False, env="ENABLE_TRACING")

    # Reliability settings
    retry_max_attempts: int = Field(default=3, env="RETRY_MAX_ATTEMPTS")
    circuit_breaker_threshold: int = Field(default=5, env="CIRCUIT_BREAKER_THRESHOLD")

    @validator("environment")
    def validate_environment(cls, v):
        """Enforce production safeguards."""
        if v == "production":
            # Could add additional production-specific validation
            pass
        return v

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"  # Support DB__HOST format

# Load configuration
config = ServerConfig()

# Usage
print(f"Running in {config.environment} mode")
print(f"Database: {config.database.host}:{config.database.port}")
```

**Example .env file:**
```bash
# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database
DB_HOST=postgres.production.internal
DB_PORT=5432
DB_NAME=heb_mcp
DB_USERNAME=mcp_user
DB_PASSWORD=${DB_PASSWORD}  # Injected by secret manager
DB_POOL_SIZE=20

# Cache
REDIS_URL=redis://redis.production.internal:6379/0
CACHE_TTL=3600

# Authentication (injected by 1Password/Infisical)
HEB_CLIENT_ID=${HEB_CLIENT_ID}
HEB_CLIENT_SECRET=${HEB_CLIENT_SECRET}
HEB_REDIRECT_URI=https://mcp.heb.com/callback
HEB_AUTH_SERVER_URL=https://auth.heb.com

# Feature Flags
ENABLE_CACHING=true
ENABLE_METRICS=true
ENABLE_TRACING=true

# Reliability
RETRY_MAX_ATTEMPTS=3
CIRCUIT_BREAKER_THRESHOLD=5
```

**Configuration Validation on Startup:**
```python
def validate_config() -> list[str]:
    """Validate configuration and return errors."""
    errors = []

    try:
        config = ServerConfig()
    except ValidationError as e:
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"])
            errors.append(f"{field}: {error['msg']}")

    return errors

if __name__ == "__main__":
    # Validate before starting
    config_errors = validate_config()
    if config_errors:
        print("Configuration errors:", file=sys.stderr)
        for error in config_errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    # Start server
    mcp.run()
```

### 4.2 Installation Patterns

#### Distribution Methods Comparison

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| **pip/PyPI** | Python servers | Standard Python packaging, Easy versioning | Requires Python environment |
| **npm/npx** | TypeScript servers | Zero-install with npx, Always latest | Requires Node.js, Security risks |
| **uvx** | Python servers | Isolated environments, Fast (Rust-powered) | Newer tool, less adoption |
| **Docker** | Production | Isolated, Consistent, Secure | Larger size, Docker required |
| **Pre-built Binary** | Distribution | No runtime needed, Fast startup | Platform-specific builds |

#### Python Package (PyPI)

**Setup:**
```python
# pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "heb-mcp-server"
version = "1.0.0"
description = "H-E-B Model Context Protocol Server"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "H-E-B Digital", email = "engineering@heb.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "fastmcp>=3.0.0",
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "structlog>=24.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.8.0",
    "ruff>=0.1.0",
]

[project.scripts]
heb-mcp = "heb_mcp.server:main"

[project.urls]
Homepage = "https://github.com/heb/heb-mcp-server"
Documentation = "https://heb-mcp.readthedocs.io"
Repository = "https://github.com/heb/heb-mcp-server"
"Bug Tracker" = "https://github.com/heb/heb-mcp-server/issues"
```

**Installation:**
```bash
# Install from PyPI
pip install heb-mcp-server

# Run server
heb-mcp

# Install with development dependencies
pip install heb-mcp-server[dev]
```

#### Docker Distribution (Recommended)

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 mcp && \
    mkdir -p /app && \
    chown -R mcp:mcp /app

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=mcp:mcp . .

# Switch to non-root user
USER mcp

# Expose health check port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8080/health/live')"

# Run server
CMD ["python", "-m", "heb_mcp.server"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  heb-mcp:
    build: .
    image: heb/mcp-server:latest
    ports:
      - "3000:3000"
      - "8080:8080"  # Health checks
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    env_file:
      - .env.production
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    restart: unless-stopped
    networks:
      - mcp-network

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
    networks:
      - mcp-network

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: heb_mcp
      POSTGRES_USER: mcp_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mcp_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - mcp-network

volumes:
  redis-data:
  postgres-data:

networks:
  mcp-network:
    driver: bridge
```

**Usage:**
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f heb-mcp

# Scale server instances
docker-compose up -d --scale heb-mcp=3

# Stop
docker-compose down
```

#### MCP Client Configuration

**Claude Desktop (macOS):**
```json
{
  "mcpServers": {
    "heb": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "HEB_CLIENT_ID",
        "-e", "HEB_CLIENT_SECRET",
        "heb/mcp-server:latest"
      ],
      "env": {
        "HEB_CLIENT_ID": "${HEB_CLIENT_ID}",
        "HEB_CLIENT_SECRET": "${HEB_CLIENT_SECRET}"
      }
    }
  }
}
```

**VS Code (Cline/Roo):**
```json
{
  "mcp.servers": [
    {
      "name": "heb",
      "command": "python",
      "args": ["-m", "heb_mcp.server"],
      "env": {
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG"
      }
    }
  ]
}
```

### 4.3 Testing Approaches

#### Testing Pyramid

```
        /\
       /  \       E2E Tests (Few)
      /____\      - Full MCP protocol
     /      \     - Real integrations
    /  Inte- \
   /  gration \   Integration Tests (Some)
  /____________\  - Component interactions
 /              \
/  Unit  Tests   \ Unit Tests (Many)
/________________\- Function-level
                  - Fast, isolated
```

#### Unit Testing

```python
import pytest
from unittest.mock import AsyncMock, Mock
from heb_mcp.tools.search import search_products
from heb_mcp.services.product import ProductService

@pytest.fixture
def mock_product_service():
    """Mock product service."""
    service = Mock(spec=ProductService)
    service.search = AsyncMock(return_value=[
        {"id": "123", "name": "Milk", "price": 3.99},
        {"id": "456", "name": "Eggs", "price": 4.99}
    ])
    return service

@pytest.mark.asyncio
async def test_search_products_success(mock_product_service):
    """Test successful product search."""
    result = await search_products(
        query="milk",
        service=mock_product_service
    )

    assert len(result) == 2
    assert result[0]["name"] == "Milk"
    mock_product_service.search.assert_called_once_with("milk")

@pytest.mark.asyncio
async def test_search_products_empty_query(mock_product_service):
    """Test search with empty query returns error."""
    with pytest.raises(ValueError, match="Query cannot be empty"):
        await search_products(query="", service=mock_product_service)

@pytest.mark.asyncio
async def test_search_products_service_error(mock_product_service):
    """Test search handles service errors gracefully."""
    mock_product_service.search.side_effect = Exception("API error")

    with pytest.raises(Exception, match="API error"):
        await search_products(query="milk", service=mock_product_service)
```

#### Integration Testing

```python
import pytest
from fastapi.testclient import TestClient
from heb_mcp.server import app
from heb_mcp.database import get_db
from heb_mcp.cache import get_cache

@pytest.fixture
def test_client():
    """Create test client with test dependencies."""
    # Override dependencies with test versions
    app.dependency_overrides[get_db] = lambda: test_db
    app.dependency_overrides[get_cache] = lambda: test_cache

    with TestClient(app) as client:
        yield client

    # Cleanup
    app.dependency_overrides.clear()

def test_health_check(test_client):
    """Test health check endpoint."""
    response = test_client.get("/health/ready")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "components" in data

def test_search_products_integration(test_client):
    """Test product search with real components."""
    response = test_client.post(
        "/mcp/tools/call",
        json={
            "name": "search_products",
            "arguments": {"query": "milk"}
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert len(data["content"]) > 0
```

#### Contract Testing (MCP Protocol Compliance)

```python
import pytest
from mcp.types import CallToolRequest, CallToolResult
from heb_mcp.server import mcp_server

@pytest.mark.asyncio
async def test_tool_returns_valid_result():
    """Test tool returns valid MCP result format."""
    request = CallToolRequest(
        method="tools/call",
        params={
            "name": "search_products",
            "arguments": {"query": "milk"}
        }
    )

    result = await mcp_server.handle_call_tool(request)

    # Validate result structure
    assert isinstance(result, CallToolResult)
    assert hasattr(result, "content")
    assert isinstance(result.content, list)
    assert all(hasattr(c, "type") for c in result.content)

@pytest.mark.asyncio
async def test_tool_error_format():
    """Test tool errors follow MCP format."""
    request = CallToolRequest(
        method="tools/call",
        params={
            "name": "invalid_tool",
            "arguments": {}
        }
    )

    result = await mcp_server.handle_call_tool(request)

    assert result.isError is True
    assert len(result.content) > 0
    assert result.content[0].type == "text"
```

#### MCP Inspector Usage

```bash
# Start MCP Inspector
npx @modelcontextprotocol/inspector python -m heb_mcp.server

# Opens browser to http://localhost:5173
# Provides interactive testing interface:
# - View all tools, resources, prompts
# - Test tools with parameters
# - Inspect JSON responses
# - Debug protocol messages
```

#### Load Testing

```python
import asyncio
import time
from statistics import mean, stdev

async def load_test_search(concurrency: int = 100, duration: int = 60):
    """
    Load test search endpoint.

    Args:
        concurrency: Number of concurrent requests
        duration: Test duration in seconds
    """
    latencies = []
    errors = 0

    async def make_request():
        nonlocal errors
        start = time.time()
        try:
            result = await search_products(query="milk")
            latencies.append(time.time() - start)
        except Exception:
            errors += 1

    # Run load test
    end_time = time.time() + duration
    tasks = []

    while time.time() < end_time:
        # Maintain concurrency level
        if len(tasks) < concurrency:
            tasks.append(asyncio.create_task(make_request()))

        # Remove completed tasks
        tasks = [t for t in tasks if not t.done()]

        await asyncio.sleep(0.01)  # Small delay

    # Wait for remaining tasks
    await asyncio.gather(*tasks)

    # Report results
    total_requests = len(latencies) + errors
    success_rate = (len(latencies) / total_requests) * 100 if total_requests > 0 else 0

    print(f"Load Test Results:")
    print(f"  Duration: {duration}s")
    print(f"  Concurrency: {concurrency}")
    print(f"  Total Requests: {total_requests}")
    print(f"  Successful: {len(latencies)}")
    print(f"  Failed: {errors}")
    print(f"  Success Rate: {success_rate:.2f}%")
    print(f"  Throughput: {total_requests / duration:.2f} req/s")

    if latencies:
        sorted_latencies = sorted(latencies)
        p50 = sorted_latencies[int(len(sorted_latencies) * 0.50)]
        p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
        p99 = sorted_latencies[int(len(sorted_latencies) * 0.99)]

        print(f"  Latency:")
        print(f"    Mean: {mean(latencies)*1000:.2f}ms")
        print(f"    Stdev: {stdev(latencies)*1000:.2f}ms")
        print(f"    P50: {p50*1000:.2f}ms")
        print(f"    P95: {p95*1000:.2f}ms")
        print(f"    P99: {p99*1000:.2f}ms")

if __name__ == "__main__":
    asyncio.run(load_test_search())
```

### 4.4 Documentation Structure

#### Best Practices from Successful MCPs

**Essential Documentation Sections:**
1. Quick Start / Getting Started
2. Installation & Configuration
3. MCP Client Setup (Claude, VS Code, etc.)
4. Available Capabilities (Tools/Resources/Prompts)
5. Authentication Setup
6. API Reference
7. Examples & Use Cases
8. Troubleshooting
9. Contributing Guidelines
10. Security Considerations

#### README Template

```markdown
# H-E-B MCP Server

> Model Context Protocol server providing access to H-E-B grocery services

[![PyPI version](https://badge.fury.io/py/heb-mcp-server.svg)](https://pypi.org/project/heb-mcp-server/)
[![Tests](https://github.com/heb/heb-mcp-server/workflows/tests/badge.svg)](https://github.com/heb/heb-mcp-server/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Quick Start

```bash
# Install
pip install heb-mcp-server

# Configure
export HEB_CLIENT_ID="your_client_id"
export HEB_CLIENT_SECRET="your_client_secret"

# Run
heb-mcp
```

## Features

- 🔍 **Product Search**: Search H-E-B's catalog of 50,000+ products
- 🛒 **Cart Management**: Add items to your H-E-B cart
- 📍 **Store Locator**: Find nearby H-E-B stores
- 📦 **Order History**: View past orders and reorder favorites
- 💰 **Deals & Coupons**: Access current deals and digital coupons

## Installation

### Using pip

```bash
pip install heb-mcp-server
```

### Using Docker (Recommended for Production)

```bash
docker pull heb/mcp-server:latest
docker run -it --rm \
  -e HEB_CLIENT_ID="your_client_id" \
  -e HEB_CLIENT_SECRET="your_client_secret" \
  heb/mcp-server:latest
```

## Configuration

### MCP Client Setup

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "heb": {
      "command": "heb-mcp",
      "env": {
        "HEB_CLIENT_ID": "your_client_id",
        "HEB_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

#### VS Code (Cline)

Add to VS Code settings:

```json
{
  "mcp.servers": [
    {
      "name": "heb",
      "command": "heb-mcp",
      "env": {
        "HEB_CLIENT_ID": "your_client_id",
        "HEB_CLIENT_SECRET": "your_client_secret"
      }
    }
  ]
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HEB_CLIENT_ID` | Yes | OAuth client ID from H-E-B Developer Portal |
| `HEB_CLIENT_SECRET` | Yes | OAuth client secret |
| `HEB_REDIRECT_URI` | No | OAuth redirect URI (default: http://localhost:8080/callback) |
| `ENVIRONMENT` | No | Environment: development, staging, production (default: development) |
| `LOG_LEVEL` | No | Log level: DEBUG, INFO, WARNING, ERROR (default: INFO) |

## MCP Capabilities

### Tools

#### `search_products`

Search for products in the H-E-B catalog.

**Parameters:**
- `query` (string, required): Search query
- `limit` (integer, optional): Maximum results (default: 10, max: 100)
- `category` (string, optional): Filter by category

**Example:**
```
Search for organic milk
```

**Returns:**
```json
[
  {
    "id": "12345",
    "name": "H-E-B Organics Whole Milk",
    "price": 4.99,
    "in_stock": true,
    "category": "Dairy"
  }
]
```

#### `add_to_cart`

Add an item to the user's cart.

**Parameters:**
- `product_id` (string, required): Product ID
- `quantity` (integer, optional): Quantity to add (default: 1)

**Authentication:** Requires user OAuth token

**Example:**
```
Add 2 gallons of milk to my cart
```

[... more tools ...]

### Resources

#### `heb://stores/{zip_code}`

Get H-E-B stores near a ZIP code.

**Example URI:** `heb://stores/78701`

#### `heb://product/{product_id}/inventory`

Get real-time inventory for a product.

**Example URI:** `heb://product/12345/inventory`

### Prompts

#### `weekly_meal_planner`

Generate a weekly meal plan with H-E-B products.

**Parameters:**
- `dietary_restrictions` (string): Any dietary restrictions
- `budget` (number): Weekly budget

## Authentication

### Getting OAuth Credentials

1. Visit [H-E-B Developer Portal](https://developer.heb.com)
2. Create a new application
3. Copy your Client ID and Client Secret
4. Set redirect URI to `http://localhost:8080/callback`

### User Authorization Flow

For features requiring user authorization (cart, orders):

```bash
# Run authorization helper
heb-mcp auth

# Follow the browser prompt to authorize
# Refresh token will be saved securely in system keychain
```

## Examples

### Recipe Meal Planning

```
I need a healthy dinner recipe for 4 people with a budget of $30.
Use H-E-B products and show me the shopping list.
```

### Reordering Groceries

```
What did I buy last week? Add the same items to my cart.
```

### Finding Deals

```
Show me current deals on produce at my local H-E-B.
```

## Troubleshooting

### "Authentication required" error

Run `heb-mcp auth` to complete user authorization flow.

### "Circuit breaker open" message

The external API is temporarily unavailable. The server will automatically retry after 30 seconds.

### Connection issues

Ensure your firewall allows connections to `api.heb.com` on port 443.

## Development

### Setup

```bash
git clone https://github.com/heb/heb-mcp-server
cd heb-mcp-server
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest --cov=heb_mcp  # With coverage
```

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector python -m heb_mcp.server
```

## Security

- Never commit credentials to version control
- Use system keychain or secret manager for credential storage
- Report security vulnerabilities to security@heb.com

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)

## Support

- Documentation: https://heb-mcp.readthedocs.io
- Issues: https://github.com/heb/heb-mcp-server/issues
- Email: mcp-support@heb.com
```

---

## 5. Specific Implementation Examples

### 5.1 Kroger MCP Analysis

**Repository**: https://github.com/EricLott/kroger-mcp

**Key Patterns Observed:**

**Dual OAuth Strategy:**
- Client credentials for public data (product search, store locations)
- Authorization code grant for user-specific operations (cart management)
- Automatic token refresh with fallback to re-authorization

**Error Handling:**
- Structured error responses with actionable guidance
- Distinguishes between auth errors, API errors, and rate limits
- Returns helpful messages guiding users to solutions

**Code Organization:**
- `auth.py`: Isolated authentication logic (AuthManager class)
- `tools.py`: API wrapper functions
- `config.py`: Centralized configuration
- `server.py`: MCP server setup

**Lessons for HEB MCP:**
- Dual-token strategy applicable if we have public + user-specific APIs
- CLI-mediated browser auth pattern works well for initial setup
- Clear error messages are critical for user experience
- Modular organization scales better than monolithic structure

### 5.2 GitHub Official MCP Server

**Repository**: https://github.com/github/github-mcp-server

**Architecture Highlights:**

**Go-Based Implementation:**
- Follows Go best practices: `cmd/`, `internal/`, `pkg/` structure
- Clear separation of public APIs (`pkg/`) vs internal (`internal/`)
- End-to-end testing in dedicated `e2e/` directory

**Multiple Auth Methods:**
- OAuth for interactive applications
- Personal Access Tokens for CLI/automation
- Environment variable injection for secure credential management

**Security Practices:**
- Principle of least privilege (minimal PAT scopes)
- Documentation-first approach to security
- File permission guidance (`chmod 600` for credentials)
- Explicit `.gitignore` patterns

**Toolset Discovery:**
- `tool-search` CLI utility for exploring available tools
- Prevents tool bloat by helping users choose relevant subset
- Progressive disclosure pattern

**Documentation Structure:**
- Installation guides per platform (VS Code, Claude Desktop, etc.)
- Separate server configuration documentation
- Security guidance prominent and detailed

**Lessons for HEB MCP:**
- Multi-platform documentation is essential
- Security guidance should be prominent, not buried
- Tool discovery mechanism prevents overwhelming users
- Telemetry/metrics should have feature flags

### 5.3 Official Reference Servers

**Repository**: https://github.com/modelcontextprotocol/servers

**Key Servers Analyzed:**

**Filesystem Server:**
- Implements configurable access controls
- Path traversal protection
- Read-only vs read-write modes
- Demonstrates security-conscious resource design

**Memory Server:**
- Knowledge graph-based persistent memory
- Shows advanced pattern: MCP server with state
- Entity-relationship modeling
- Demonstrates resource and tool interaction

**Git Server:**
- Read, search, and manipulate operations
- Demonstrates complex tool composition
- Error handling for repository operations
- Shows how to expose external tools via MCP

**Sequential Thinking Server:**
- Dynamic problem-solving pattern
- Shows prompt-driven workflows
- Demonstrates reflective capabilities
- Useful for complex multi-step processes

**Lessons for HEB MCP:**
- Filesystem patterns apply to our product catalog resources
- Memory pattern could apply to shopping preferences/history
- Git-style tool composition (search → read → write) applicable
- Sequential thinking pattern useful for meal planning workflows

### 5.4 Community Best Practices

**Highly-Starred Community Projects:**

**Database Servers (PostgreSQL, MySQL, SQLite):**
- Transaction support patterns
- Query parameterization for SQL injection prevention
- Connection pooling implementation
- Schema exploration tools

**Integration Platforms (Rube, Zapier):**
- Multi-service authentication handling
- Unified error handling across services
- Rate limiting coordination
- Action vs query tool separation

**Developer Tools (dbt MCP):**
- CLI integration patterns
- Metadata discovery approaches
- Semantic layer abstraction
- Documentation generation from code

**Key Takeaways:**
- Connection pooling is standard for database-backed servers
- Multi-service integration requires careful rate limit management
- Metadata/schema discovery improves discoverability
- Semantic abstractions make tools more AI-friendly

---

## 6. Recommendations for HEB MCP

### 6.1 Technology Stack

**Primary Recommendation: Python + FastMCP**

**Rationale:**
1. **Developer Velocity**: FastMCP provides fastest time-to-production
2. **Ecosystem**: 70% of MCP servers use FastMCP - proven at scale
3. **Team Familiarity**: Python likely more familiar than Go/TypeScript
4. **Rapid Iteration**: Decorator-based API enables quick changes

**Alternative: Official Python SDK**
- Use if you need maximum control over protocol implementation
- Consider for performance-critical paths
- More boilerplate but more flexibility

### 6.2 Architecture Recommendations

**Server Structure:**
```
heb-mcp-server/
├── src/
│   ├── heb_mcp/
│   │   ├── __init__.py
│   │   ├── server.py              # Main FastMCP server
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── search.py          # Product search
│   │   │   ├── cart.py            # Cart operations
│   │   │   ├── stores.py          # Store locator
│   │   │   └── orders.py          # Order history
│   │   ├── resources/
│   │   │   ├── __init__.py
│   │   │   ├── products.py        # Product resources
│   │   │   └── stores.py          # Store resources
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   └── meal_planning.py   # Meal planning prompts
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── product_service.py
│   │   │   ├── cart_service.py
│   │   │   └── store_service.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── oauth.py           # OAuth implementation
│   │   │   └── manager.py         # Token management
│   │   ├── reliability/
│   │   │   ├── __init__.py
│   │   │   ├── retry.py           # Retry logic
│   │   │   ├── circuit_breaker.py
│   │   │   └── cache.py           # Caching layer
│   │   ├── observability/
│   │   │   ├── __init__.py
│   │   │   ├── tracing.py
│   │   │   ├── metrics.py
│   │   │   └── logging.py
│   │   └── config.py              # Configuration
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
│   ├── installation.md
│   ├── configuration.md
│   └── api-reference.md
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

### 6.3 Authentication Strategy

**Recommended Approach: Dual OAuth + System Keychain**

**Public Operations (No Auth):**
- Product search
- Store locator
- Deals/coupons browsing

**User-Specific Operations (OAuth Required):**
- Cart management
- Order history
- Favorites/lists
- User preferences

**Implementation:**
1. Start with client credentials for public APIs
2. Implement authorization code grant with PKCE for user operations
3. Store refresh tokens in system keychain (not `.env`)
4. Provide CLI helper for initial authorization

### 6.4 Reliability Strategy

**Essential Patterns to Implement:**

1. **Retry with Exponential Backoff**
   - Max 3 attempts
   - Base delay 1s, max 60s
   - Add jitter to prevent thundering herd

2. **Circuit Breaker**
   - Threshold: 5 failures
   - Timeout: 30s
   - Success threshold: 2

3. **Caching Strategy**
   - Redis for distributed cache
   - Stale-while-revalidate pattern
   - Cache product data (1 hour TTL)
   - Cache store locations (24 hour TTL)

4. **Health Checks**
   - `/health/live` - liveness probe
   - `/health/ready` - readiness probe with component status
   - Expose circuit breaker status
   - Monitor cache hit rates

5. **Observability**
   - OpenTelemetry for traces and metrics
   - Structured logging with correlation IDs
   - Prometheus metrics endpoint
   - Grafana dashboards for visualization

### 6.5 Developer Experience

**Installation Strategy:**
- **Development**: pip install with editable mode
- **Production**: Docker with Docker Compose
- **Distribution**: Publish to PyPI + Docker Hub

**Configuration:**
- Use Pydantic Settings for type-safe config
- Support `.env` files for development
- Require secret manager for production
- Provide config validation on startup

**Testing:**
- Unit tests with pytest
- Integration tests with TestClient
- Contract tests for MCP protocol compliance
- MCP Inspector for interactive testing
- Load tests with realistic traffic patterns

**Documentation:**
- Comprehensive README with quick start
- Separate installation guides per platform
- API reference auto-generated from code
- Examples and use cases prominent
- Security guidance upfront

### 6.6 Security Checklist

- [ ] HTTPS enforced for all API calls
- [ ] OAuth 2.1 with PKCE implemented
- [ ] Refresh tokens stored in system keychain
- [ ] No credentials in environment variables for production
- [ ] Input validation on all tool parameters
- [ ] SQL injection prevention (if using database)
- [ ] Rate limiting on all endpoints
- [ ] Audit logging for user operations
- [ ] Error messages sanitized (no system details leaked)
- [ ] Dependencies scanned for vulnerabilities (Dependabot)
- [ ] Container image scanned (Trivy/Snyk)
- [ ] Security headers configured (CSP, HSTS)

### 6.7 Performance Targets

Based on production MCP best practices:

- **Throughput**: >1000 requests/second per instance
- **Latency P95**: <100ms for simple operations (search, store lookup)
- **Latency P99**: <500ms for complex operations (cart updates)
- **Error Rate**: <0.1% under normal conditions
- **Availability**: >99.9% uptime
- **Cache Hit Rate**: >80% for product searches

### 6.8 Deployment Strategy

**Phase 1: Development (Weeks 1-2)**
- FastMCP server with core tools
- Basic OAuth client credentials
- In-memory caching
- Development with MCP Inspector

**Phase 2: Beta (Weeks 3-4)**
- User OAuth implementation
- Redis caching
- Circuit breakers and retries
- Docker containerization
- Basic health checks

**Phase 3: Production (Weeks 5-6)**
- OpenTelemetry observability
- Prometheus metrics
- Load testing and optimization
- Comprehensive documentation
- Security audit

**Phase 4: Scaling (Ongoing)**
- Horizontal scaling with Kubernetes
- Advanced caching strategies
- Performance optimization
- Feature expansion

---

## 7. Trade-off Analysis

### 7.1 Framework Comparison

| Factor | FastMCP | Official SDK | Custom Implementation |
|--------|---------|--------------|----------------------|
| **Development Speed** | Fastest | Medium | Slowest |
| **Learning Curve** | Low | Medium | High |
| **Flexibility** | Medium | High | Highest |
| **Community Support** | Strong | Official | None |
| **Documentation** | Excellent | Good | Self-maintained |
| **Best For** | Most projects | Fine-grained control | Unique requirements |
| **Maintenance Burden** | Low | Medium | High |

**Recommendation**: Start with FastMCP, migrate to official SDK only if specific limitations encountered.

### 7.2 Authentication Methods

| Method | Security | UX | Complexity | Best For |
|--------|----------|-----|------------|----------|
| **OAuth 2.1 + PKCE** | Excellent | Good | High | Production |
| **API Keys** | Fair | Excellent | Low | Development |
| **Client Credentials** | Good | Excellent | Low | Public APIs |
| **System Keychain** | Excellent | Good | Medium | Token storage |
| **Secret Manager** | Excellent | Fair | Medium | Production secrets |

**Recommendation**: OAuth 2.1 for user auth, system keychain for storage, secret manager for API credentials.

### 7.3 Deployment Methods

| Method | Isolation | Portability | Startup Time | Best For |
|--------|-----------|-------------|--------------|----------|
| **Docker** | Excellent | Excellent | Medium | Production |
| **pip/PyPI** | Fair | Good | Fast | Development |
| **Pre-built Binary** | Good | Platform-specific | Fastest | Distribution |
| **Kubernetes** | Excellent | Excellent | Slow | Enterprise scale |

**Recommendation**: Docker for production, pip for development, Kubernetes if scaling beyond 10+ instances.

### 7.4 Caching Strategies

| Strategy | Consistency | Performance | Complexity | Best For |
|----------|-------------|-------------|------------|----------|
| **In-Memory** | Eventual | Excellent | Low | Development |
| **Redis** | Eventual | Excellent | Medium | Production |
| **Stale-While-Revalidate** | Eventual | Excellent | High | High availability |
| **Database** | Strong | Fair | Low | Strong consistency needed |

**Recommendation**: Redis with stale-while-revalidate for production, in-memory for development.

---

## 8. Common Pitfalls to Avoid

### 8.1 Architecture Pitfalls

**Monolithic Server Syndrome**
- **Problem**: Single server handling database, files, APIs, email, etc.
- **Solution**: Single-responsibility servers, compose via MCP client

**Tool Bloat**
- **Problem**: Exposing 50+ tools overwhelming AI and users
- **Solution**: Tool discovery mechanism, progressive disclosure, focused servers

**Tight Coupling**
- **Problem**: Tools directly accessing databases, no abstraction
- **Solution**: Service layer pattern, dependency injection

### 8.2 Security Pitfalls

**Hardcoded Credentials**
- **Problem**: API keys in `.env` files committed to git
- **Solution**: System keychain or secret manager, `.gitignore` enforcement

**Missing Input Validation**
- **Problem**: SQL injection, path traversal vulnerabilities
- **Solution**: Pydantic models, parameterized queries, path sanitization

**Information Leakage in Errors**
- **Problem**: Stack traces exposing system details to LLM
- **Solution**: Sanitized error messages, detailed logging to stderr only

### 8.3 Reliability Pitfalls

**No Retry Logic**
- **Problem**: Transient failures cause permanent errors
- **Solution**: Exponential backoff for idempotent operations

**Missing Circuit Breakers**
- **Problem**: Cascading failures, resource exhaustion
- **Solution**: Circuit breaker pattern with appropriate thresholds

**No Fallback Strategy**
- **Problem**: Service outage causes complete failure
- **Solution**: Graceful degradation, cached data, placeholders

**Missing Health Checks**
- **Problem**: Dead servers still receiving traffic
- **Solution**: Liveness and readiness probes, component monitoring

### 8.4 Developer Experience Pitfalls

**Poor Error Messages**
- **Problem**: Generic errors don't help AI decide next steps
- **Solution**: Actionable error messages with remediation guidance

**Missing Examples**
- **Problem**: Users don't know how to use tools
- **Solution**: Examples in docstrings, README, and prompts

**Configuration Complexity**
- **Problem**: Dozens of environment variables, unclear requirements
- **Solution**: Sensible defaults, validation with helpful errors, templates

**No Testing Strategy**
- **Problem**: Regressions, broken deployments
- **Solution**: Comprehensive test pyramid, CI/CD with automated tests

---

## Sources

### Official Documentation
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [Model Context Protocol GitHub](https://github.com/modelcontextprotocol)
- [Official MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Inspector Tool](https://github.com/modelcontextprotocol/inspector)
- [MCP Development Guide](https://github.com/cyanheads/model-context-protocol-resources/blob/main/guides/mcp-server-development-guide.md)

### Framework Documentation
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [FastMCP Documentation](https://gofastmcp.com/)
- [Building MCP Server with FastMCP](https://mcpcat.io/guides/building-mcp-server-python-fastmcp/)
- [FastMCP Tutorial](https://www.firecrawl.dev/blog/fastmcp-tutorial-building-mcp-servers-python)
- [Building MCP Server and Client with FastMCP 2.0](https://www.datacamp.com/tutorial/building-mcp-server-client-fastmcp)
- [FastMCP vs Official SDK Comparison](https://medium.com/@divyanshbhatiajm19/comparing-mcp-server-frameworks-which-one-should-you-choose-cbadab4ddc80)

### Best Practices & Implementation Guides
- [MCP Best Practices: Architecture & Implementation Guide](https://modelcontextprotocol.info/docs/best-practices/)
- [Error Handling in MCP Servers](https://mcpcat.io/guides/error-handling-custom-mcp-servers/)
- [15 Best Practices for Building MCP Servers](https://thenewstack.io/15-best-practices-for-building-mcp-servers-in-production/)
- [Top 5 MCP Server Best Practices - Docker](https://www.docker.com/blog/mcp-server-best-practices/)
- [Microsoft MCP Best Practices](https://github.com/microsoft/mcp-for-beginners/blob/main/08-BestPractices/README.md)

### Authentication & Security
- [MCP Authorization Specification](https://modelcontextprotocol.io/specification/draft/basic/authorization)
- [MCP OAuth 2.1 Complete Guide](https://dev.to/composiodev/mcp-oauth-21-a-complete-guide-3g91)
- [Secure MCP Server with OAuth 2.1](https://www.scalekit.com/blog/implement-oauth-for-mcp-servers)
- [MCP and Authorization - Auth0](https://auth0.com/blog/an-introduction-to-mcp-and-authorization/)
- [OAuth for MCP Explained - Stytch](https://stytch.com/blog/oauth-for-mcp-explained-with-a-real-world-example/)
- [Managing Secrets in MCP Servers - Infisical](https://infisical.com/blog/managing-secrets-mcp-servers)
- [Best Practices for MCP Secrets Management - WorkOS](https://workos.com/guide/best-practices-for-mcp-secrets-management)
- [Securing MCP Servers with 1Password](https://1password.com/blog/securing-mcp-servers-with-1password-stop-credential-exposure-in-your-agent)
- [Insecure Credential Storage in MCP - Trail of Bits](https://blog.trailofbits.com/2025/04/30/insecure-credential-storage-plagues-mcp/)

### Reliability & Observability
- [MCP Server Observability - Zeo](https://zeo.org/resources/blog/mcp-server-observability-monitoring-testing-performance-metrics)
- [MCP Observability Guide](https://mcpmanager.ai/blog/mcp-observability/)
- [Build Health Check Endpoints for MCP Servers](https://mcpcat.io/guides/building-health-check-endpoint-mcp-server/)
- [MCP Connection Health Checks](https://mcpcat.io/guides/implementing-connection-health-checks/)
- [MCP Observability with OpenTelemetry - SigNoz](https://signoz.io/blog/mcp-observability-with-otel/)
- [Understanding Retry Pattern and Circuit Breaker](https://dzone.com/articles/understanding-retry-pattern-with-exponential-back)
- [Retry with Backoff Pattern - AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/retry-backoff.html)

### Testing & Development
- [How to Test MCP Servers](https://www.merge.dev/blog/mcp-server-testing)
- [Testing MCP Servers - Codely](https://codely.com/en/blog/how-to-test-mcp-servers)
- [Debugging MCP Servers](https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices)

### Installation & Deployment
- [MCP Server Executables: npx, uvx, Docker](https://dev.to/leomarsh/mcp-server-executables-explained-npx-uvx-docker-and-beyond-1i1n)
- [Global vs Local MCP Server Installation](https://mcpcat.io/guides/installing-mcp-servers-globally-vs-locally/)
- [How to Run MCP Servers with Docker - Snyk](https://snyk.io/articles/how-to-run-mcp-servers-with-docker/)
- [Docker MCP Catalog and Toolkit](https://www.docker.com/blog/announcing-docker-mcp-catalog-and-toolkit-beta/)

### Example Implementations
- [kroger-mcp GitHub](https://github.com/EricLott/kroger-mcp)
- [GitHub Official MCP Server](https://github.com/github/github-mcp-server)
- [Awesome MCP Servers - wong2](https://github.com/wong2/awesome-mcp-servers)
- [Awesome MCP Servers - punkpeye](https://github.com/punkpeye/awesome-mcp-servers)
- [Top 8 Open Source MCP Projects](https://medium.com/@nocobase/top-8-open-source-mcp-projects-with-the-most-github-stars-f2e2a603b41d)
- [How to Build MCP Server in Python - ScrapFly](https://scrapfly.io/blog/posts/how-to-build-an-mcp-server-in-python-a-complete-guide)

### Additional Resources
- [Model Context Protocol Guide for 2026](https://publicapis.io/blog/mcp-model-context-protocol-guide)
- [MCP Introduction for Developers - Stytch](https://stytch.com/blog/model-context-protocol-introduction/)
- [MCP Architecture - Stainless](https://www.stainless.com/mcp/)

---

## Research Limitations

1. **Rapidly Evolving Ecosystem**: MCP specification updated November 2025, OAuth spec added March 2025. Some patterns may evolve further.

2. **Limited Production Case Studies**: Most MCP servers are <6 months old. Long-term operational patterns still emerging.

3. **Framework Maturity**: FastMCP 3.0 is in beta. Some patterns may change in stable release.

4. **HEB-Specific Integration**: Research is generic MCP patterns. HEB's specific APIs, infrastructure, and requirements will necessitate adaptations.

5. **Performance Data**: Limited public performance benchmarks for MCP servers at scale. Load testing recommendations based on general web service best practices.

6. **Security Audit**: This research covers best practices but doesn't constitute a security audit. Independent security review recommended before production deployment.

---

## Next Steps

1. **Architecture Review**: Review this research with the team and validate recommendations against HEB's infrastructure and requirements.

2. **Prototype Development**: Build minimal FastMCP server with one tool to validate framework choice and development workflow.

3. **Authentication Planning**: Meet with H-E-B authentication team to design OAuth integration matching their existing systems.

4. **Infrastructure Planning**: Work with DevOps to plan Docker deployment, Kubernetes configuration (if needed), and monitoring setup.

5. **Security Review**: Schedule security review of proposed architecture, authentication patterns, and credential management strategy.

6. **Development Kickoff**: Begin Phase 1 implementation following recommended structure and patterns from this research.
