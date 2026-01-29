# Architect Notes: HEB MCP Open Source Release

**Date:** 2026-01-29
**Task:** Technical analysis for open source release preparation

---

## Executive Summary

The HEB MCP project has a solid technical design document that covers the core functionality well. For open source release, the main technical gaps are around:
1. Code quality enforcement tooling
2. CI/CD automation
3. Extension points for contributors
4. Security practices

This document provides detailed recommendations for each area.

---

## 1. Code Quality Standards - Deep Dive

### 1.1 Linting and Formatting (Ruff)

Ruff is the recommended choice because:
- 10-100x faster than flake8 + isort + black combined
- Single tool replaces multiple tools
- Active development, strong community adoption
- Written in Rust, minimal dependencies

**pyproject.toml configuration:**
```toml
[tool.ruff]
target-version = "py310"
line-length = 88
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
]
ignore = [
    "E501",   # line too long (handled by formatter)
]

[tool.ruff.isort]
known-first-party = ["heb_mcp"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### 1.2 Type Checking (MyPy)

**pyproject.toml configuration:**
```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false  # Allow untyped test functions
```

### 1.3 Pre-commit Configuration

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies:
          - pydantic>=2.0
          - types-redis

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.1
    hooks:
      - id: gitleaks
```

### 1.4 Testing Standards

**pytest configuration (pyproject.toml):**
```toml
[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra -q --strict-markers --cov=heb_mcp --cov-report=term-missing --cov-fail-under=80"
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests",
    "integration: Integration tests (may require network)",
    "e2e: End-to-end tests",
    "slow: Slow tests (>1s)",
]

[tool.coverage.run]
branch = true
source = ["src/heb_mcp"]
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
fail_under = 80
```

**Test organization:**
```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── tools/
│   │   ├── test_store.py
│   │   ├── test_product.py
│   │   ├── test_cart.py
│   │   └── ...
│   ├── clients/
│   │   ├── test_graphql.py
│   │   └── test_cache.py
│   └── reliability/
│       ├── test_circuit_breaker.py
│       └── test_retry.py
├── integration/
│   ├── test_graphql_live.py   # Tests against real API (mock fallback)
│   └── test_cache_redis.py    # Tests with real Redis
└── e2e/
    └── test_tool_flows.py     # Full tool invocation flows
```

---

## 2. CI/CD Architecture - Detailed

### 2.1 Main CI Workflow

**.github/workflows/ci.yml:**
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install ruff mypy
      - name: Lint with ruff
        run: ruff check .
      - name: Check formatting
        run: ruff format --check .
      - name: Type check
        run: mypy src/

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov-report=xml
        env:
          REDIS_URL: redis://localhost:6379
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        if: matrix.python-version == '3.11'

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install tools
        run: pip install bandit safety pip-audit
      - name: Run bandit
        run: bandit -r src/
      - name: Run pip-audit
        run: pip-audit
      - name: Run gitleaks
        uses: gitleaks/gitleaks-action@v2
```

### 2.2 Release Workflow

**.github/workflows/release.yml:**
```yaml
name: Release

on:
  push:
    tags:
      - "v*.*.*"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install build tools
        run: pip install build twine
      - name: Build package
        run: python -m build
      - name: Check package
        run: twine check dist/*
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish-pypi:
    needs: build
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write  # Required for trusted publishing
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1

  publish-docker:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      packages: write
    steps:
      - uses: actions/checkout@v4
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}

  github-release:
    needs: [publish-pypi, publish-docker]
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
```

### 2.3 Dependabot Configuration

**.github/dependabot.yml:**
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    groups:
      dev-dependencies:
        patterns:
          - "pytest*"
          - "mypy"
          - "ruff"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## 3. Contribution Architecture - Detailed

### 3.1 Extension Points Design

**Abstract Data Source Interface:**
```python
# src/heb_mcp/sources/base.py
from abc import ABC, abstractmethod
from typing import Any

class DataSource(ABC):
    """Base class for data sources."""

    @abstractmethod
    async def get_product(self, sku: str, store_id: str) -> dict[str, Any]:
        """Fetch a product by SKU."""
        pass

    @abstractmethod
    async def search_products(
        self,
        query: str,
        store_id: str,
        limit: int = 20
    ) -> list[dict[str, Any]]:
        """Search for products."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if source is healthy."""
        pass
```

**Abstract Cache Backend Interface:**
```python
# src/heb_mcp/cache/base.py
from abc import ABC, abstractmethod
from typing import Any, Optional

class CacheBackend(ABC):
    """Base class for cache backends."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int
    ) -> None:
        """Set value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass
```

**Tool Registry Pattern:**
```python
# src/heb_mcp/tools/registry.py
from typing import Callable, Dict
from fastmcp import FastMCP

_custom_tools: Dict[str, Callable] = {}

def register_custom_tool(name: str, handler: Callable) -> None:
    """Register a custom tool to be loaded at startup."""
    _custom_tools[name] = handler

def load_custom_tools(mcp: FastMCP) -> None:
    """Load all registered custom tools into the MCP server."""
    for name, handler in _custom_tools.items():
        mcp.tool(name=name)(handler)
```

### 3.2 Dependency Injection Pattern

```python
# src/heb_mcp/container.py
from dataclasses import dataclass
from heb_mcp.sources.base import DataSource
from heb_mcp.cache.base import CacheBackend

@dataclass
class Container:
    """Dependency injection container."""
    data_source: DataSource
    cache: CacheBackend

    @classmethod
    def create_default(cls) -> "Container":
        """Create container with default implementations."""
        from heb_mcp.sources.graphql import GraphQLSource
        from heb_mcp.cache.redis import RedisCache

        return cls(
            data_source=GraphQLSource(),
            cache=RedisCache()
        )

    @classmethod
    def create_for_testing(cls) -> "Container":
        """Create container with mock implementations."""
        from heb_mcp.sources.mock import MockSource
        from heb_mcp.cache.memory import MemoryCache

        return cls(
            data_source=MockSource(),
            cache=MemoryCache()
        )
```

### 3.3 File Size Guidelines

Keep files focused and small:
- Tool modules: < 300 lines each
- Model files: < 200 lines each
- Client files: < 400 lines each
- Total project: Aim for < 5000 lines of core code (excluding tests)

---

## 4. Versioning Strategy - Detailed

### 4.1 Version Number Management

**Single source of truth in pyproject.toml:**
```toml
[project]
name = "heb-mcp"
version = "0.1.0"
```

**Expose in package:**
```python
# src/heb_mcp/__init__.py
from importlib.metadata import version

__version__ = version("heb-mcp")
```

### 4.2 Changelog Format

**CHANGELOG.md (Keep a Changelog format):**
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Feature description

### Changed
- Change description

### Deprecated
- Deprecated feature description

### Removed
- Removed feature description

### Fixed
- Bug fix description

### Security
- Security fix description

## [0.1.0] - 2026-01-29

### Added
- Initial release with 19 MCP tools
- GraphQL client for HEB API
- Redis caching layer
- Circuit breaker and retry logic
```

### 4.3 Release Checklist

Before each release:
1. Update version in pyproject.toml
2. Update CHANGELOG.md
3. Run full test suite
4. Check documentation is up to date
5. Create git tag: `git tag -a v0.1.0 -m "Release 0.1.0"`
6. Push tag: `git push origin v0.1.0`
7. GitHub Actions handles the rest

---

## 5. Security - Detailed

### 5.1 SECURITY.md Template

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via GitHub Security Advisories:
1. Go to the Security tab of this repository
2. Click "Report a vulnerability"
3. Provide a detailed description

**What to include:**
- Type of issue (e.g., buffer overflow, injection, CSRF)
- Full paths of source file(s) related to the issue
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue

**Response Timeline:**
- Acknowledgment: Within 48 hours
- Initial assessment: Within 7 days
- Fix timeline: Within 90 days (may vary based on severity)

## Security Best Practices for Users

1. **Keep heb-mcp updated** to the latest version
2. **Never commit auth.json** - it contains session tokens
3. **Use environment variables** for sensitive configuration
4. **Review permissions** when running with elevated privileges
```

### 5.2 .gitignore Security Entries

```gitignore
# Auth and secrets
.env
.env.*
*.env
auth.json
*.pem
*.key
credentials.json
secrets.yaml
secrets.yml

# HEB-specific
.heb-mcp/
**/auth.json

# IDE secrets
.idea/secrets.xml
.vscode/settings.json
```

### 5.3 Security Scanning Tools

**bandit configuration (.bandit):**
```yaml
skips: []
exclude_dirs:
  - tests
  - .venv
  - venv
```

**Safety/pip-audit:**
- Run on every CI build
- Block PRs with known vulnerabilities
- Allow override with documented exceptions

---

## 6. File Templates Needed

### 6.1 Issue Templates

**.github/ISSUE_TEMPLATE/bug_report.md:**
```markdown
---
name: Bug report
about: Report a bug to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1.
2.
3.

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.11.0]
- heb-mcp version: [e.g., 0.1.0]

**Additional context**
Any other context about the problem.
```

**.github/ISSUE_TEMPLATE/feature_request.md:**
```markdown
---
name: Feature request
about: Suggest a new feature
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Problem**
What problem does this solve?

**Proposed Solution**
How would you like this to work?

**Alternatives Considered**
Other solutions you've considered.

**Additional context**
Any other context or screenshots.
```

### 6.2 Pull Request Template

**.github/PULL_REQUEST_TEMPLATE.md:**
```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have run `ruff check` and `ruff format`
- [ ] I have run `mypy` with no errors
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally
- [ ] I have updated the documentation accordingly
- [ ] I have added an entry to CHANGELOG.md

## Testing
Describe how this was tested.

## Screenshots (if applicable)
```

---

## 7. Recommendations Summary

### High Priority (Do Before Release)
1. Set up ruff + mypy + pre-commit
2. Create CI workflow with tests and security scanning
3. Write SECURITY.md
4. Create issue and PR templates
5. Add CHANGELOG.md

### Medium Priority (First Month)
1. Implement extension point interfaces
2. Set up release automation
3. Add Dependabot
4. Create CONTRIBUTING.md
5. Set up branch protection rules

### Low Priority (Ongoing)
1. Add CodeQL analysis
2. Set up GitHub Discussions
3. Create Codespaces/Gitpod config
4. Add conda-forge recipe
5. Create migration guides for breaking changes

---

## Open Questions for User

1. **Python Version Floor**: The design mentions Python 3.10+. Is that the floor we want, or should we support 3.9?

2. **PyPI Package Name**: Is `heb-mcp` available on PyPI? Should check and reserve.

3. **GitHub Organization**: Will this be under a personal account or an organization?

4. **Security Contact**: Use GitHub Security Advisories only, or set up a dedicated email?

5. **Docker Registry**: ghcr.io only, or also Docker Hub?

6. **Automated Changelog**: Use Conventional Commits + auto-changelog, or manual changelog?

---

## References

- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
