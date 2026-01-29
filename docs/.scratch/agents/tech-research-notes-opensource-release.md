# Technical Research: Open Source Release Tooling for Python MCP Projects

**Date**: 2026-01-29
**Requested By**: Brainstorming Session - Open Source Release Planning
**Research Scope**: Technical tooling, templates, CI/CD, documentation, code quality, and licensing for Python MCP projects

---

## Executive Summary

This research investigated the technical infrastructure needed to release the HEB MCP as a high-quality open source Python project. The Python ecosystem has undergone significant modernization in 2025-2026, with new tools like `uv` and `ruff` dramatically improving developer experience. The MCP community primarily uses MIT licensing and FastMCP framework, with modern Python packaging via `pyproject.toml`.

**Key Recommendations**:
- Use **pyproject.toml** (not setup.py) for modern Python packaging
- Adopt **uv** for dependency management (10-100x faster than pip)
- Use **ruff** for linting/formatting and **mypy** for type checking
- Implement **GitHub Actions** with trusted publishing to PyPI
- Choose **MIT License** (aligns with MCP ecosystem)
- Use **MkDocs Material** for documentation (easier than Sphinx)
- Enable **Dependabot** for security scanning

---

## 1. Project Templates and Scaffolding

### MCP-Specific Templates

**Official MCP Python SDK**:
- Repository: https://github.com/modelcontextprotocol/python-sdk
- SDK Version: mcp 1.26.0 (as of research date)
- Stable v2.0 expected Q1 2026, but v1.x recommended for production
- Install: `uv add "mcp[cli]" httpx`

**FastMCP Framework**:
- Primary Repository: https://github.com/jlowin/fastmcp
- Current Version: FastMCP 2.0 (production), 3.0 in beta
- Market Share: Powers ~70% of MCP servers across all languages
- Downloads: ~1 million per day
- Examples Repository: https://github.com/sauliussed/fastmcp-examples
- Documentation: https://gofastmcp.com

**FastMCP Features**:
- Decorator-based approach (`@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`)
- Pythonic, minimal boilerplate
- Supports automatic OpenAPI spec generation (v2.0+)
- Server proxying capabilities

### General Python Project Templates

**Cookiecutter Ecosystem**:
- Tool: https://github.com/cookiecutter/cookiecutter
- Installation: `pipx install cookiecutter` (recommended)
- Academic validation: Recent 2026 research confirms Cookiecutter as mature, popular standard

**Recommended Templates**:

1. **cookiecutter-pywf_open_source**
   - Repository: https://github.com/MacHu-GWU/cookiecutter-pywf_open_source
   - Experience: Based on 150+ open source Python libraries
   - Speed: Publish to PyPI within 1 hour
   - Features: Complete CI/CD, AI-powered assistance, automated workflows

2. **cookiecutter-pypackage** (Audrey Feldroy)
   - Repository: https://github.com/audreyfeldroy/cookiecutter-pypackage
   - Classic, well-maintained template
   - Includes: Tox for multi-version testing, Sphinx for docs

3. **cookiecutter-python-project**
   - Repository: https://lyz-code.github.io/cookiecutter-python-project/
   - Modern best practices
   - Features: src layout, domain-driven design, pip-tools

**Template Capabilities**:
- Hooks: Pre/post-generation scripts for validation, environment setup
- Tool Agnostic: Can generate projects for any language/framework
- Standardization: Encapsulates organizational best practices

### uv Project Initialization

**Modern Alternative to Cookiecutter**:
```bash
# Create new project with uv (2026 approach)
mkdir my-mcp-server
cd my-mcp-server
uv init
uv venv
uv add "mcp[cli]" httpx fastmcp
```

**uv Capabilities**:
- Generates basic `pyproject.toml` automatically
- Can create sample project structure via `uv init`
- Replaces: pip, pipx, venv, pip-tools
- Performance: 10-100x faster than pip

---

## 2. CI/CD Tooling

### GitHub Actions for Python Projects

**PyPI Publishing - Trusted Publishing (Recommended)**

**Official Action**: `pypa/gh-action-pypi-publish@release/v1`
- Repository: https://github.com/pypa/gh-action-pypi-publish
- Documentation: https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/

**Key Features (2026)**:
- **Trusted Publishing**: No manual API tokens needed (recommended for security)
- **PEP 740 Attestations**: Since v1.11.0, automatically generates and uploads signed digital attestations for all distributions
- **Authentication**: PyPI generates short-lived tokens per-project, auto-expiring
- **Security**: Eliminates need for long-lived API tokens in GitHub secrets

**Important Notes**:
- Action does NOT build packages (user must build to `dist/` first)
- Trusted publishing cannot be used from reusable workflows (create separate job)
- Requires PyPI project setup with trusted publisher configuration

**Typical Workflow Structure**:
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Build package
        run: |
          python -m pip install build
          python -m build
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for trusted publishing
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

### Test Coverage Tools

**Coverage.py**:
- Latest Version: 7.13.2 (released January 25, 2026)
- Python Support: 3.10-3.15 alpha (including free-threading)
- Documentation: https://coverage.readthedocs.io/

**pytest-cov**:
- Installation: `pip install pytest-cov`
- Usage: `pytest --cov`
- Generates `.coverage` file for analysis
- Note: More rigid than running coverage directly

**Coverage Analysis Services**:

1. **Codecov** (Recommended)
   - Website: https://codecov.io
   - Reason: Ease of use, better GitHub Actions integration
   - Action: `codecov/codecov-action`
   - Free for open source projects
   - Dashboard with coverage visualization

2. **Coveralls**
   - Website: https://coveralls.io
   - Alternative to Codecov
   - Free for open source
   - Less commonly recommended in 2026

**Typical Coverage Workflow**:
```yaml
- name: Run tests with coverage
  run: pytest --cov --cov-report=xml

- name: Upload to Codecov
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
```

### Security Scanning

**Dependabot (Essential)**:
- Documentation: https://docs.github.com/en/code-security/dependabot
- Cost: Free for all GitHub users
- Native integration: Built into GitHub platform

**Capabilities**:
- **Alerts**: Scans dependency files (requirements.txt, Pipfile.lock, pyproject.toml)
- **Triggers**: Scans on push and when new advisories added to GitHub Advisory Database
- **Automation**: Creates PRs to upgrade vulnerable dependencies
- **Ecosystem Support**: Python (pip), JavaScript (npm/yarn), Java (Maven), .NET (NuGet), Ruby (RubyGems), PHP (Composer)

**How It Works**:
- Scans default branch (not on schedule, but on changes)
- Checks against GitHub Advisory Database
- Generates Dependabot alerts for known vulnerabilities
- Optionally creates security update PRs automatically

**Configuration**:
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

**Assessment**: Essential foundational tool for Python projects on GitHub in 2026. Must-use for automated dependency management.

**Additional Security Tools** (from research):
- **GitLeaks**: Fast, lightweight secret scanner (prevents API keys, passwords in commits)
- **Bandit**: Python-specific security linter (can integrate with Ruff)

---

## 3. Documentation Tools

### MkDocs vs Sphinx Comparison

**MkDocs**:

**Pros**:
- **Markup**: Uses Markdown (more accessible than reStructuredText)
- **Live Preview**: `mkdocs serve` provides auto-refresh on changes
- **Ease of Use**: Simpler setup, faster iteration
- **Themes**: MkDocs Material looks polished out-of-the-box, minimal CSS tweaking
- **Lightweight**: Better for straightforward documentation needs

**Cons**:
- **API Docs**: Weaker auto-documentation from code docstrings (requires plugins)
- **Output Formats**: Primarily HTML (limited PDF/ePub support)
- **Customization**: Less extensive than Sphinx for complex needs

**Best For**: Projects prioritizing ease of use, Markdown familiarity, quick documentation updates

**Sphinx**:

**Pros**:
- **Auto-Documentation**: Excellent for generating API docs from Python docstrings (autodoc, autosummary extensions)
- **Output Formats**: HTML, PDF, ePub from same source
- **Extensibility**: Large ecosystem of extensions
- **Community**: Larger community, more resources (Python's official docs use Sphinx)

**Cons**:
- **Markup**: Uses reStructuredText (steeper learning curve)
- **Rebuild Required**: Changes require `make html` (no live preview by default)
- **Complexity**: More configuration, slower iteration

**Best For**: Projects with extensive API documentation needs, multiple output formats required

### Recommendation for MCP Projects

**MkDocs Material** is recommended for most MCP servers:
- MCP projects typically have moderate documentation needs (not massive APIs)
- Markdown is widely understood by contributors
- Live preview speeds up documentation writing
- Material theme provides professional appearance immediately

**However**, if HEB MCP has extensive public API requiring auto-generated docs from docstrings, consider Sphinx.

### API Documentation Generators

**For Sphinx Users**:
1. **autodoc**: Reuses Python docstrings in documentation
2. **autosummary**: Generates documents with autodoc directives automatically
3. **AutoAPI**: Sphinx extension that recursively discovers all package modules and public objects (zero manual intervention)

**For MkDocs Users**:
1. **mkdocstrings**: Plugin for auto-generating API docs in MkDocs
   - Supports Google-style, NumPy-style, Napoleon docstrings
   - Integration: `mkdocstrings[python]`

**Standalone Tools**:
1. **pdoc**: Simple auto-generation from docstrings
   - No configuration required
   - Supports Markdown, numpydoc, Google-style
   - Command: `pdoc module_name`
   - Website: https://pdoc.dev/

2. **pydoc**: Built into Python standard library
   - Basic documentation generation
   - Less feature-rich than modern alternatives

**Best Practices**:
- Add comprehensive docstrings to public functions, classes, exceptions
- Use consistent docstring format (Google-style or NumPy-style)
- Semi-automatic approach: Docstrings provide base, manual docs add context

### README Badges

**Shields.io** (Official Service):
- Website: https://shields.io/
- Traffic: Serves 1.6+ billion images monthly
- Format: SVG and raster badges
- Customization: Multiple styles available at https://shields.io/#styles

**Python-Specific Badges**:
- PyPI version: `![PyPI](https://img.shields.io/pypi/v/package-name)`
- PyPI downloads: Daily/weekly/monthly statistics
- Python versions: `![Python](https://img.shields.io/pypi/pyversions/package-name)`
- License: `![License](https://img.shields.io/github/license/user/repo)`
- Build status: `![Build](https://img.shields.io/github/actions/workflow/status/user/repo/workflow.yml)`
- Coverage: `![Coverage](https://img.shields.io/codecov/c/github/user/repo)`

**Badge Collections**:
- https://github.com/Ileriayo/markdown-badges - Pre-made badges including Python
- https://github.com/henriquesebastiao/badges - Customization guides
- https://github.com/Naereen/badges - Markdown code for various badges

**Badge Generator Tool**:
- https://www.readmecodegen.com/badges-generator - Visual badge builder

**Recommended Badges for MCP Server**:
```markdown
![PyPI](https://img.shields.io/pypi/v/heb-mcp)
![Python](https://img.shields.io/pypi/pyversions/heb-mcp)
![License](https://img.shields.io/github/license/username/heb-mcp)
![Build](https://img.shields.io/github/actions/workflow/status/username/heb-mcp/ci.yml)
![Coverage](https://img.shields.io/codecov/c/github/username/heb-mcp)
![Downloads](https://img.shields.io/pypi/dm/heb-mcp)
![MCP](https://img.shields.io/badge/MCP-compatible-blue)
```

---

## 4. Code Quality Tools Stack

### The Modern Python Trio: Ruff + Mypy

**Ruff** (All-in-One Linter and Formatter):

**Overview**:
- Repository: https://github.com/astral-sh/ruff
- Language: Written in Rust
- Performance: 10-100x faster than traditional tools
- Replaces: Black, isort, Flake8, Pylint, Autoflake, pyupgrade, pydocstyle, and ~12 other tools

**Adoption**:
- Major projects using Ruff: Apache Airflow, FastAPI, pandas, pydantic
- Market position: Rapidly becoming the de facto standard in 2026

**Capabilities**:
- **Linting**: 800+ rules from multiple linters
- **Formatting**: Drop-in replacement for Black
- **Auto-fixing**: Can automatically fix many violations
- **Speed**: Runs in milliseconds instead of seconds

**What Ruff Does NOT Replace**:
- **Type Checking**: Does not replace Mypy, Pyright, or Pyre
- Ruff focuses on style and common errors, not type system validation

**Configuration** (pyproject.toml):
```toml
[tool.ruff]
line-length = 88  # Black-compatible
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "B",   # bugbear
    "C4",  # comprehensions
    "UP",  # pyupgrade
    "ANN", # type annotations
]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**Mypy** (Static Type Checker):

**Overview**:
- Purpose: Verify type harmony and catch type-related errors
- Position: Must-use alongside Ruff (complementary, not redundant)
- Documentation: https://mypy-lang.org/

**Why Use Mypy with Ruff**:
- Ruff provides fast feedback on lint violations
- Mypy provides detailed feedback on type errors
- Together they form comprehensive quality checks

**Configuration** (pyproject.toml):
```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Alternative Type Checkers**:
- **Pyright**: Microsoft's type checker, faster than Mypy for large codebases
- **Pyre**: Facebook's type checker (less common)

### Real-World MCP Server Examples

**oracle-mcp-server** (danielmeppiel):
```toml
[project.optional-dependencies]
dev = ["mypy", "ruff"]

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]
```

**fibery-mcp-server** (Fibery-inc):
```toml
[tool.ruff]
line-length = 120
# Extensive type annotation rules (ANN001-ANN206)

[tool.mypy]
mypy-init-return = true
```

**supabase-mcp-server** (alexander-zuev):
```toml
[tool.ruff.lint]
select = ["E", "F", "I", "B", "C4", "UP"]

[tool.mypy]
python_version = "3.12"
strict = true
```

**RaspberryPiOS-MCP** (grammy-jiang):
- Toolchain: uv + ruff + pytest + tox
- Modern, comprehensive quality stack

### Pre-commit Hooks

**Pre-commit Framework**:
- Website: https://pre-commit.com/
- Repository: https://github.com/pre-commit/pre-commit-hooks
- Installation: `pipx install pre-commit`

**2026 Best Practices**:

**Philosophy**:
- **Best-in-class**: Select one best tool per task (avoid redundancy)
- **Auto-fix**: Implement automatic fixes where possible (reduce busywork)
- **Performance**: Consider speed impact (long checks hurt productivity)

**Recommended Hook Categories**:

1. **Guard Rails**:
   - `check-ast`: Verify Python syntax via AST
   - `check-added-large-files`: Prevent accidental large file commits
   - `check-json`, `check-yaml`, `check-toml`: Validate config files

2. **Formatters**:
   - `ruff format`: Code formatting

3. **Code Checkers**:
   - `ruff check`: Linting
   - `mypy`: Type checking

4. **Security**:
   - `gitleaks`: Scan for secrets (passwords, API keys, tokens)

5. **Git Helpers**:
   - `trailing-whitespace`: Remove trailing whitespace
   - `end-of-file-fixer`: Ensure files end with newline
   - `check-merge-conflict`: Detect merge conflict markers

**Sample Configuration** (.pre-commit-config.yaml):
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-ast
      - id: check-added-large-files
      - id: check-json
      - id: check-yaml
      - id: check-toml
      - id: trailing-whitespace
      - id: end-of-file-fixer

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
```

**Installation**:
```bash
pre-commit install  # Installs git hooks
pre-commit run --all-files  # Test on all files
```

---

## 5. Modern Python Packaging

### pyproject.toml vs setup.py

**Current State (2026)**:

The Python community has standardized on `pyproject.toml` per PEP 621. The ecosystem transitioned via PEP 517, PEP 518, and PEP 621.

**Why pyproject.toml Won**:

1. **Security**:
   - setup.py is executable code (arbitrary commands at install time = security risk)
   - pyproject.toml is declarative (no code execution)

2. **Standardization**:
   - setup.py lacks strict standard
   - pyproject.toml follows PEP 621 specification

3. **Maintainability**:
   - Declarative format easier to read and modify
   - Single file for all project metadata and tool configs

4. **Tool Support**:
   - Modern tools (Hatch, Poetry, PDM, uv) require pyproject.toml
   - Many tools configure via pyproject.toml: Setuptools, Ruff, Black, Mypy, Pytest, Tox, etc.

**Can setup.py Still Exist?**

Yes, for backward compatibility with legacy tools, but keep configuration in pyproject.toml.

**Documentation**:
- Official Guide: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
- Migration Guide: https://packaging.python.org/en/latest/guides/modernize-setup-py-project/

**Sample pyproject.toml** (MCP Server):
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "heb-mcp"
version = "0.1.0"
description = "HEB grocery shopping assistant MCP server"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["mcp", "grocery", "heb", "ai", "assistant"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "fastmcp>=2.0.0",
    "httpx>=0.27.0",
    "redis>=5.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "pytest-asyncio>=0.24.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]

[project.urls]
Homepage = "https://github.com/username/heb-mcp"
Documentation = "https://github.com/username/heb-mcp#readme"
Repository = "https://github.com/username/heb-mcp"
Issues = "https://github.com/username/heb-mcp/issues"

[project.scripts]
heb-mcp = "heb_mcp.server:main"

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "C4", "UP", "ANN"]

[tool.mypy]
python_version = "3.10"
strict = true
```

### Package Manager: uv vs Poetry vs pip

**uv** (2026 Recommendation):

**Overview**:
- Developer: Astral (creators of Ruff)
- Language: Rust
- Performance: 10-100x faster than pip
- Benchmark: JupyterLab install - 2.6s (uv) vs 21.4s (pip)

**Replaces**:
- pip (package installation)
- pipx (tool installation)
- venv (virtual environments)
- pip-tools (dependency resolution)

**Capabilities**:
- Drop-in pip replacement
- Automatic environment handling
- Automatic Python version management
- Superior dependency resolution
- Lock file generation

**When to Use**:
- Rapid development cycles
- CI/CD pipelines (speed critical)
- Quick experiments and internal tools
- Projects prioritizing simplicity and speed

**Usage**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project
uv init my-project
cd my-project
uv venv
uv add fastmcp httpx

# Install dev dependencies
uv add --dev pytest ruff mypy

# Run commands in environment
uv run pytest
uv run python -m mypy src/
```

**Poetry** (Established Alternative):

**When to Use**:
- Complex, long-term projects
- Library development requiring sophisticated dependency management
- Team collaboration with established Poetry workflows
- Need for private PyPI integration

**Strengths**:
- Mature dependency management
- Excellent lock file handling
- Publishing workflow built-in
- Large community and ecosystem

**Weaknesses vs uv**:
- Slower installation times
- More complex configuration

**pip** (Traditional):

**When to Use**:
- Very simple projects
- No lock file requirements
- Legacy compatibility

**Weaknesses**:
- No lock files
- Slower dependency resolution
- No automatic environment management

**Comparison Summary** (2026):

| Feature | uv | Poetry | pip |
|---------|-----|--------|-----|
| Speed | 10-100x faster | Moderate | Baseline |
| Lock Files | Yes | Yes | No |
| Auto venv | Yes | Yes | No |
| Python version mgmt | Yes | No | No |
| Learning Curve | Low | Medium | Low |
| Best For | Modern projects, CI/CD | Libraries, teams | Legacy, simple |

**Recommendation for HEB MCP**: Use **uv** for its speed, simplicity, and alignment with modern Python practices (2026).

---

## 6. License Analysis

### MIT vs Apache 2.0

**MIT License**:

**Characteristics**:
- **Length**: 3 paragraphs, simple language
- **Permissions**: Very permissive (commercial use, modification, distribution, private use)
- **Conditions**: Minimal (include copyright notice and license in distributions)
- **Patent Rights**: No explicit patent grant

**Pros**:
- Maximum accessibility for users
- Simple to understand
- Widely recognized and accepted
- Minimal compliance burden

**Cons**:
- No patent protection
- No explicit contributor protections

**Apache 2.0 License**:

**Characteristics**:
- **Length**: Longer, more detailed legal language
- **Permissions**: Permissive (same as MIT)
- **Conditions**: More requirements (NOTICE file, state modifications, attribution)
- **Patent Rights**: Explicit patent grant and protection

**Pros**:
- Patent protection (prevents lawsuits from contributors)
- Legal certainty for enterprise adoption
- Prevents patent trolling
- Better for corporate contributors

**Cons**:
- More complex compliance requirements
- Must maintain NOTICE file
- Must document modifications

### Python Project License Trends

**PyPI Statistics**:
- MIT: 29.14% of PyPI packages
- Apache 2.0: 23.98% of PyPI packages
- Combined: Dominate Python packaging ecosystem

**Language-Specific Trends**:
- Python: Apache 2.0 and MIT both popular
- Java: Apache 2.0 dominates (~70%)

### MCP Ecosystem License Analysis

**Official MCP Repositories**:
- Model Context Protocol specification: **MIT License**
- Official MCP servers: **MIT License**
- Python SDK: **MIT License**
- FastMCP: **MIT License** (jlowin/fastmcp)

**Finding**: The MCP ecosystem standardizes on **MIT License**.

### Recommendation for HEB MCP

**Choose MIT License**:

**Rationale**:
1. **Ecosystem Alignment**: MIT is the standard for MCP projects
2. **Simplicity**: Easier for contributors to understand and comply
3. **Accessibility**: Maximum accessibility encourages adoption and forks
4. **Community Expectation**: Python/MCP community expects permissive licensing

**When Apache 2.0 Makes Sense**:
- Patent-heavy domain (HEB grocery shopping is not)
- Major corporate contributors concerned about patent litigation
- Enterprise-focused project requiring legal certainty

**For HEB MCP**: MIT is the clear choice given the MCP ecosystem norms and the domain.

**License Text**: Use official MIT License template from https://opensource.org/licenses/MIT with:
```
Copyright (c) 2026 [Your Name/Organization]
```

---

## 7. Contribution Infrastructure

### CONTRIBUTING.md Best Practices

**Purpose**: Official guide for contributors explaining how to participate in the project.

**Location**: Root directory (alongside README.md and LICENSE)

**GitHub Integration**: Anyone creating an issue or PR gets automatic link to CONTRIBUTING.md.

**Essential Sections**:

1. **Code Style Guidelines**:
   - Reference PEP-8 (or deviations)
   - Point to linting tools (Ruff configuration)
   - Type annotation requirements

2. **Development Setup**:
   ```markdown
   ## Development Setup

   1. Clone the repository
   2. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   3. Create environment: `uv venv`
   4. Install dependencies: `uv sync`
   5. Install pre-commit hooks: `pre-commit install`
   6. Run tests: `uv run pytest`
   ```

3. **Testing Requirements**:
   - How to run tests
   - Coverage expectations
   - Test writing guidelines

4. **Documentation Requirements**:
   - Docstring format (Google-style, NumPy, etc.)
   - When to update README
   - How to build docs locally

5. **Pull Request Process**:
   - Branch naming conventions
   - PR title format
   - Review process expectations
   - CI checks that must pass

6. **Issue Templates**:
   - Link to bug report template
   - Link to feature request template
   - Link to question template

7. **Code of Conduct**:
   - Reference CODE_OF_CONDUCT.md
   - Expected behavior
   - Reporting mechanisms

**Template Resources**:
- Example: https://contributing.md/example/
- Guide: https://contributing.md/how-to-build-contributing-md/
- Mozilla Science: https://mozillascience.github.io/working-open-workshop/contributing/

**Related Files**:
- `CODE_OF_CONDUCT.md`: Contributor behavior expectations
- `SECURITY.md`: Vulnerability reporting process
- `.github/ISSUE_TEMPLATE/`: Issue templates
- `.github/PULL_REQUEST_TEMPLATE.md`: PR template

### Issue and PR Templates

**GitHub Templates Directory**: `.github/`

**Bug Report Template** (.github/ISSUE_TEMPLATE/bug_report.md):
```markdown
---
name: Bug Report
about: Report a bug to help us improve
labels: bug
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Configure MCP with '...'
2. Call tool '...'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. macOS 14.0]
- Python version: [e.g. 3.12.1]
- heb-mcp version: [e.g. 0.1.0]
- Client: [e.g. Claude Desktop, Cursor]

**Additional context**
Add any other context about the problem here.
```

**Feature Request Template** (.github/ISSUE_TEMPLATE/feature_request.md):
```markdown
---
name: Feature Request
about: Suggest an idea for this project
labels: enhancement
---

**Is your feature request related to a problem?**
A clear description of the problem. Ex. I'm frustrated when [...]

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other approaches you've thought about.

**Additional context**
Any other context or screenshots.
```

### Community Files Checklist

- [ ] `README.md`: Project overview, quick start
- [ ] `LICENSE`: MIT License text
- [ ] `CONTRIBUTING.md`: Contribution guide
- [ ] `CODE_OF_CONDUCT.md`: Behavior expectations (recommend Contributor Covenant)
- [ ] `SECURITY.md`: Vulnerability disclosure process
- [ ] `.github/ISSUE_TEMPLATE/bug_report.md`
- [ ] `.github/ISSUE_TEMPLATE/feature_request.md`
- [ ] `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] `CHANGELOG.md`: Version history (Keep a Changelog format)

---

## 8. Additional Research Findings

### GitHub Actions Workflow Examples

**Hugging Face MCP Course**:
- Module on GitHub Actions integration with Python MCP servers
- Course URL: https://huggingface.co/learn/mcp-course/en/unit3/github-actions-integration
- Includes starter code and complete webhook server implementation
- Shows real-time CI/CD monitoring with MCP

**Typical CI Workflow for Python MCP**:
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync

      - name: Run ruff
        run: uv run ruff check .

      - name: Run mypy
        run: uv run mypy src/

      - name: Run tests
        run: uv run pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
```

### Python Type Checker Alternatives

**Pyright**:
- Developer: Microsoft
- Performance: Faster than Mypy for large codebases
- Integration: Excellent VS Code integration
- Mentioned in MCP code quality discussions

**Choice**: Mypy remains more common, but Pyright worth considering for performance-critical scenarios.

---

## Sources

### Project Templates & MCP
- [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [FastMCP Examples](https://github.com/sauliussed/fastmcp-examples)
- [FastMCP Tutorial - Firecrawl](https://www.firecrawl.dev/blog/fastmcp-tutorial-building-mcp-servers-python)
- [Cookiecutter Documentation](https://cookiecutter.readthedocs.io/)
- [cookiecutter-pywf_open_source](https://github.com/MacHu-GWU/cookiecutter-pywf_open_source)
- [Project Templating Research 2026](https://onlinelibrary.wiley.com/doi/full/10.1002/spe.70024)

### CI/CD & Publishing
- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)
- [Trusted Publishing - Simon Willison](https://til.simonwillison.net/pypi/pypi-releases-from-github)

### Testing & Coverage
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Codecov Python Guide](https://docs.codecov.com/docs/code-coverage-with-python)

### Security
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Dependabot Quickstart](https://docs.github.com/en/code-security/getting-started/dependabot-quickstart-guide)

### Documentation
- [MkDocs vs Sphinx Comparison](https://www.pythonsnacks.com/p/python-documentation-generator)
- [pdoc Documentation Generator](https://pdoc.dev/)
- [Shields.io Badges](https://shields.io/)
- [Markdown Badges Collection](https://github.com/Ileriayo/markdown-badges)

### Code Quality
- [Ruff - Astral](https://github.com/astral-sh/ruff)
- [Modern Python Code Quality - uv, ruff, mypy](https://simone-carolini.medium.com/modern-python-code-quality-setup-uv-ruff-and-mypy-8038c6549dcc)
- [Why Replace Flake8, Black, isort with Ruff](https://medium.com/@zigtecx/why-you-should-replace-flake8-black-and-isort-with-ruff-the-ultimate-python-code-quality-tool-a9372d1ddc1e)
- [Pre-commit Hooks Best Practices 2025](https://gatlenculp.medium.com/effortless-code-quality-the-ultimate-pre-commit-hooks-guide-for-2025-57ca501d9835)
- [Pre-commit Official Site](https://pre-commit.com/)

### Python Packaging
- [Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Modernize setup.py Projects](https://packaging.python.org/en/latest/guides/modernize-setup-py-project/)
- [Modern Python Packaging](https://chaochungkuo.github.io/posts/pyproject/)

### Package Managers
- [uv Documentation](https://docs.astral.sh/uv/)
- [Poetry vs uv 2025](https://medium.com/@hitorunajp/poetry-vs-uv-which-python-package-manager-should-you-use-in-2025-4212cb5e0a14)
- [Why Switch to uv](https://devcenter.upsun.com/posts/why-python-developers-should-switch-to-uv/)

### Licensing
- [Apache 2.0 vs MIT Comparison](https://mikatuo.com/blog/apache-20-vs-mit-licenses/)
- [Open Source License Comparison](https://www.endorlabs.com/learn/open-source-licensing-simplified-a-comparative-overview-of-popular-licenses)
- [MCP Specification Repository](https://github.com/modelcontextprotocol/modelcontextprotocol)

### Contributing Guidelines
- [How to Build CONTRIBUTING.md](https://contributing.md/how-to-build-contributing-md/)
- [CONTRIBUTING.md Example](https://contributing.md/example/)
- [Open Source Contribution Guide](https://www.contribution-guide.org/)

### MCP Server Examples
- [oracle-mcp-server](https://github.com/danielmeppiel/oracle-mcp-server)
- [fibery-mcp-server](https://github.com/Fibery-inc/fibery-mcp-server)
- [supabase-mcp-server](https://github.com/alexander-zuev/supabase-mcp-server)
- [RaspberryPiOS-MCP](https://github.com/grammy-jiang/RaspberryPiOS-MCP)
- [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course/en/unit3/github-actions-integration)

---

## Research Limitations

1. **MCP Ecosystem Maturity**: MCP is relatively new (introduced Nov 2024), so best practices are still emerging. Many examples are recent (2025-2026).

2. **Tooling Rapid Evolution**: Tools like uv and ruff are seeing rapid adoption in 2025-2026, meaning "best practices" may shift quickly.

3. **Real-World MCP Examples**: Limited number of mature, production MCP servers to analyze for patterns. Most examples are from early 2025-2026.

4. **HEB-Specific Context**: Research focused on general Python MCP practices. HEB's specific requirements (trademark, ToS, caching architecture) may introduce unique considerations.

5. **Web Search Limitations**: Some technical details may require direct repository inspection beyond what search results provide.

---

## Questions for User

1. **Package Name**: What should the PyPI package be named? `heb-mcp`, `heb-grocery-mcp`, or something else?

2. **Authorship**: How should the package author be attributed? Personal name, organization, or both?

3. **Trademark Concerns**: Have you confirmed using "HEB" in the package name is acceptable?

4. **Support Level**: What level of community support are you prepared to provide? (affects CONTRIBUTING.md tone)

5. **Testing Infrastructure**: Do you need integration tests that hit real HEB endpoints, or mock-only?

6. **Redis Dependency**: Should Redis be required or optional? (affects dependencies in pyproject.toml)

7. **Python Version Support**: Minimum Python version? (3.10, 3.11, or 3.12?)

8. **Playwright MCP Dependency**: How should the dual-MCP architecture be documented? Pre-requisite or bundled?

---

## Next Steps Recommendations

1. **Choose Package Manager**: Adopt `uv` for development and document in CONTRIBUTING.md

2. **Set Up Project Structure**: Use `uv init` or a Cookiecutter template to scaffold

3. **Configure Quality Tools**: Create pyproject.toml with Ruff and Mypy configurations

4. **Set Up Pre-commit**: Install pre-commit hooks for automated quality checks

5. **Create GitHub Workflows**:
   - CI workflow (test, lint, type-check)
   - PyPI publish workflow (on release)
   - Dependabot configuration

6. **Write Community Docs**:
   - README.md with badges and quick start
   - CONTRIBUTING.md with development setup
   - LICENSE (MIT)
   - CODE_OF_CONDUCT.md
   - SECURITY.md

7. **Documentation Site**: Set up MkDocs Material for user-facing docs

8. **Legal Review**: Confirm HEB trademark usage and ToS compliance before public release

---

## Tooling Summary Table

| Category | Tool | Why | Status |
|----------|------|-----|--------|
| Package Manager | uv | 10-100x faster, modern | Adopt |
| Linter/Formatter | Ruff | Replaces 12+ tools, Rust-fast | Adopt |
| Type Checker | Mypy | Industry standard, Ruff complement | Adopt |
| Pre-commit | pre-commit | Automate quality checks | Adopt |
| Testing | pytest | De facto standard | Adopt |
| Coverage | pytest-cov + Codecov | Standard coverage workflow | Adopt |
| CI/CD | GitHub Actions | Native GitHub integration | Adopt |
| Publishing | Trusted Publishing | Secure, no API tokens | Adopt |
| Security | Dependabot | Free, native GitHub | Enable |
| Docs | MkDocs Material | Easier than Sphinx, good for MCP | Adopt |
| Badges | Shields.io | 1.6B images/month, standard | Use |
| Packaging | pyproject.toml | PEP 621 standard | Adopt |
| License | MIT | MCP ecosystem standard | Choose |

---

**Research Completed**: 2026-01-29
**Next Phase**: Implementation planning and repository setup
