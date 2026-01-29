# Feature Brainstorm Complete: Texas Grocery MCP Open Source Release

## Session Info
- **ID:** brainstorm-opensource-release-20260129
- **Date:** 2026-01-29
- **Rounds:** 1
- **Experts Consulted:** Product Owner, Requirements Advisor, Architect, Market Research, Technical Research

---

## Executive Summary

Prepare the Texas Grocery MCP (formerly HEB MCP) for open source release as a public Python package. The project enables AI agents to interact with HEB grocery stores for product search, cart management, and pickup scheduling. Release will use the trademark-safe name "texas-grocery-mcp" with comprehensive disclaimers, MIT license, and modern Python tooling (uv, Ruff, Mypy).

---

## Problem Statement

AI agents lack the ability to interact with regional grocery stores for meal planning and shopping. While national chains have some MCP coverage, Texas's dominant grocery chain (HEB) has no MCP integration, leaving a gap for the significant Texas market.

## Target Users

1. **AI Enthusiasts** - Claude Desktop/Cursor users who want grocery assistance
2. **Developers** - Building meal planning or shopping apps with AI
3. **MCP Community** - Looking for reference implementations of e-commerce MCPs

## Success Metrics

| Metric | 3 Month | 6 Month | 12 Month |
|--------|---------|---------|----------|
| GitHub Stars | 100 | 500 | 1,000+ |
| PyPI Downloads/Month | 500 | 2,000 | 5,000+ |
| Contributors | 1-2 | 5+ | 10+ |
| Open Issues | <20 | <30 | <40 |

---

## Feature Scope

### MVP (Must Have for Release)

- [ ] **Rename project** to `texas-grocery-mcp`
- [ ] **README.md** with installation, usage, client configs, disclaimers
- [ ] **LICENSE** (MIT)
- [ ] **DISCLAIMER.md** - Unofficial status, ToS acknowledgment, use at own risk
- [ ] **CONTRIBUTING.md** - Code style, PR process, development setup
- [ ] **CODE_OF_CONDUCT.md** - Contributor Covenant
- [ ] **Issue templates** - Bug report, feature request
- [ ] **CI/CD pipeline** - GitHub Actions for test, lint, type-check, publish
- [ ] **PyPI package** - Published via Trusted Publishers
- [ ] **Test coverage** - >70% line coverage
- [ ] **pyproject.toml** - Modern packaging with all metadata
- [ ] **Tool documentation** - All 19 tools documented with examples

### V1 (Should Have - 2-4 weeks post-MVP)

- [ ] **SECURITY.md** - Vulnerability reporting process
- [ ] **Docker image** - Dockerfile + ghcr.io publishing
- [ ] **MkDocs site** - Full documentation with API reference
- [ ] **Client examples** - Claude Desktop, Cursor, VS Code configs
- [ ] **Architecture diagram** - Visual of dual-MCP setup
- [ ] **Troubleshooting guide** - Common issues and solutions
- [ ] **`--minimal` mode** - Option to register only core tools

### Future (Nice to Have)

- [ ] Recipe-to-cart tool
- [ ] Dietary preference management
- [ ] Docker MCP Catalog submission
- [ ] Multi-grocer support (Kroger, etc.)
- [ ] Spanish language support

### Explicitly Out of Scope

- Path optimization through stores - Complexity not justified for MVP
- Delivery scheduling - Pickup only for initial release
- Price history tracking - Requires persistent storage
- Official HEB partnership - Proceeding as unofficial project

---

## Technical Direction

### Recommended Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | FastMCP 3.0+ | 70% ecosystem adoption |
| Package Manager | uv | 10-100x faster than pip |
| Linter/Formatter | Ruff | Replaces 12+ tools |
| Type Checker | Mypy (strict) | Complements Ruff |
| Testing | pytest + pytest-asyncio | Standard for async Python |
| CI/CD | GitHub Actions | Native, free for open source |
| Publishing | PyPI Trusted Publishers | OIDC, no API tokens |
| Docs | MkDocs Material | Easier than Sphinx |

### Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                     User's MCP Environment                          │
│                                                                    │
│  ┌──────────────────────┐        ┌──────────────────────────────┐ │
│  │  Microsoft Playwright │        │    Texas Grocery MCP         │ │
│  │  MCP (External)       │        │    (This Project)            │ │
│  │                       │  auth  │                              │ │
│  │  - Browser automation │  state │  - 19 tools across 5 domains │ │
│  │  - Login flows        │ ─────▶ │  - GraphQL + scraper clients │ │
│  │  - Session capture    │  .json │  - Redis caching             │ │
│  └───────────────────────┘        │  - Health/metrics endpoints  │ │
│                                   └──────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### Complexity Assessment

- **Overall:** Medium
- **Key drivers:** Dual-MCP auth flow, GraphQL client, 19 tools to test

### Technical Dependencies

- Python 3.10+
- FastMCP >= 3.0
- httpx (async HTTP)
- pydantic >= 2.0
- Redis (optional, for caching)
- Microsoft Playwright MCP (external, for auth)

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| HEB API changes | Medium | High | Fallback scraper, version pinning |
| C&D from HEB | Low-Medium | High | Trademark-safe name, disclaimers, pivot plan |
| Auth flow complexity | Medium | Medium | Clear documentation, troubleshooting guide |
| Tool count overwhelm | Low | Medium | Good organization, `--minimal` mode |

---

## Legal Direction

### Approach

Proceed with strong disclaimers using trademark-safe naming.

### Project Name

**`texas-grocery-mcp`** - No trademark in name, clear regional focus

### License

**MIT** - MCP ecosystem standard, maximum compatibility

### Required Disclaimers

**README.md (prominent, before installation):**
```markdown
## Disclaimer

This is an **unofficial** project and is not affiliated with, endorsed by,
or connected to H-E-B, LP in any way. "H-E-B" and related trademarks are
the property of H-E-B, LP.

This project accesses publicly available web interfaces. Users are
responsible for compliance with H-E-B's Terms of Service. Use at your own risk.

The maintainers are not responsible for any consequences of using this software,
including but not limited to account suspension or service interruption.
```

**DISCLAIMER.md (separate file):**
- Full unofficial status statement
- ToS acknowledgment
- No warranty
- User responsibility
- Data handling transparency

---

## Repository Structure

```
texas-grocery-mcp/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # Test, lint, type-check on PR
│   │   ├── release.yml         # Publish to PyPI on tag
│   │   └── security.yml        # Dependabot, pip-audit
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   └── feature_request.yml
│   └── pull_request_template.md
├── src/
│   └── texas_grocery_mcp/
│       ├── __init__.py
│       ├── server.py
│       ├── tools/
│       ├── clients/
│       ├── models/
│       ├── auth/
│       ├── reliability/
│       └── observability/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/                        # V1: MkDocs site
├── pyproject.toml
├── README.md
├── LICENSE                      # MIT
├── DISCLAIMER.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md                  # V1
├── Dockerfile                   # V1
└── .pre-commit-config.yaml
```

---

## CI/CD Workflows

### ci.yml (On every PR)

```yaml
- Checkout code
- Setup Python 3.10, 3.11, 3.12
- Install with uv
- Run ruff check
- Run ruff format --check
- Run mypy --strict
- Run pytest with coverage
- Fail if coverage < 70%
```

### release.yml (On tag push)

```yaml
- Checkout code
- Build with uv
- Publish to PyPI (Trusted Publishers)
- Create GitHub Release
```

---

## Key Decisions Made

| Decision | Choice | Rationale | Round |
|----------|--------|-----------|-------|
| Legal approach | Disclaimers (no permission) | Acceptable risk with trademark-safe name | 1 |
| Project name | texas-grocery-mcp | No trademark, clear purpose | 1 |
| License | MIT | MCP ecosystem standard | 1 |
| Python version | 3.10+ | Modern typing, broad compatibility | 1 |
| Tool count | Keep 19 | Well-organized domains, add --minimal later | 1 |
| Docker | V1 (not MVP) | Reduces MVP complexity | 1 |
| Package manager | uv | 10-100x faster, 2026 standard | 1 |
| Linting | Ruff | Replaces 12+ tools | 1 |

---

## Remaining Open Questions

- [ ] **Maintenance level** - Define and document in README (resolve during: MVP)
- [ ] **Redis requirement** - Required or optional dependency? (resolve during: Implementation)
- [ ] **GitHub org vs personal** - Create organization or use personal account? (resolve during: MVP)

---

## Risks Identified

| Risk | Type | Likelihood | Impact | Mitigation |
|------|------|------------|--------|------------|
| HEB sends C&D | Legal | Low-Medium | High | Trademark-safe name, disclaimers, pivot plan ready |
| HEB API breaks | Technical | Medium | High | Fallback scraper, graceful degradation |
| Low adoption | Market | Medium | Medium | Quality docs, community engagement |
| Maintainer burnout | Operational | Medium | Medium | Set expectations, accept help |
| Security vulnerability | Technical | Low | High | Dependabot, security policy, quick response |

---

## Implementation Checklist

### Phase 1: Repository Setup (Day 1-2)

- [ ] Create GitHub repository `texas-grocery-mcp`
- [ ] Initialize with pyproject.toml
- [ ] Add LICENSE (MIT)
- [ ] Add .gitignore (Python)
- [ ] Add .pre-commit-config.yaml (Ruff, Mypy)
- [ ] Create basic README with disclaimers
- [ ] Set up branch protection rules

### Phase 2: CI/CD Pipeline (Day 2-3)

- [ ] Create .github/workflows/ci.yml
- [ ] Create .github/workflows/release.yml
- [ ] Add issue templates
- [ ] Add PR template
- [ ] Configure Dependabot
- [ ] Set up PyPI Trusted Publisher

### Phase 3: Code Migration (Day 3-5)

- [ ] Rename all `heb_mcp` references to `texas_grocery_mcp`
- [ ] Update imports and package name
- [ ] Ensure all tests pass
- [ ] Achieve >70% coverage
- [ ] Pass Ruff and Mypy checks

### Phase 4: Documentation (Day 5-7)

- [ ] Write comprehensive README
- [ ] Create DISCLAIMER.md
- [ ] Create CONTRIBUTING.md
- [ ] Create CODE_OF_CONDUCT.md
- [ ] Document all 19 tools with examples
- [ ] Add Claude Desktop config example
- [ ] Add Cursor/VS Code config example

### Phase 5: Release (Day 7-8)

- [ ] Final review of all files
- [ ] Test `pip install` in clean environment
- [ ] Tag v0.1.0
- [ ] Publish to PyPI
- [ ] Create GitHub Release with notes
- [ ] Announce (optional: Reddit, HN, Discord)

### Phase 6: V1 Enhancements (Week 2-4)

- [ ] Add SECURITY.md
- [ ] Create Dockerfile
- [ ] Publish Docker image to ghcr.io
- [ ] Set up MkDocs documentation site
- [ ] Add troubleshooting guide
- [ ] Implement `--minimal` mode

---

## Recommendation

**Build as:** Small-to-Medium Feature (MVP achievable in 1 week)

**Complexity:** Medium

**Confidence Level:** High - Technical design is solid, legal risk is manageable with mitigations

---

## Next Step

The technical design document already exists. Begin implementation with Phase 1 (Repository Setup).

**Command to start:**
```
Create the texas-grocery-mcp repository with the structure defined above,
starting with pyproject.toml, LICENSE, README with disclaimers, and CI/CD workflows.
```

---

## Appendix: Research Documents

- **Market Research:** `docs/.scratch/agents/market-research-notes-opensource-release.md`
- **Technical Research:** `docs/.scratch/agents/tech-research-notes-opensource-release.md`
- **Architect Notes:** `docs/.scratch/agents/architect-notes-opensource-release.md`
- **Requirements Notes:** `docs/.scratch/agents/requirements-advisor-notes-opensource-release.md`
- **Product Owner Notes:** `docs/.scratch/agents/product-owner-notes-opensource-release.md`
- **Shared Brainstorm:** `docs/.scratch/brainstorm-opensource-release-20260129-shared.md`
- **Technical Design:** `docs/plans/2026-01-29-heb-mcp-design.md`
- **MCP Research Synthesis:** `docs/research/research-successful-mcp-synthesis.md`
