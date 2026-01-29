# Requirements Advisor Notes: HEB MCP Open Source Release

**Date:** 2026-01-29
**Task:** Analyze requirements for open source release of HEB MCP
**Status:** Complete

---

## Problem Understanding

### What problem are we solving?
Preparing a functional MCP server (HEB grocery shopping assistant) for public release on GitHub as an open source project, enabling developers to use, contribute to, and build upon the codebase.

### Who experiences this problem?
1. **Potential Users**: Developers wanting to integrate HEB grocery shopping into AI workflows
2. **Contributors**: Open source developers wanting to improve the project
3. **Bug Reporters**: Users encountering issues who need guidance
4. **Feature Requesters**: Community members with enhancement ideas
5. **Maintainers**: Project team managing community contributions

### Current State
- Technical design is complete (19 tools, dual-MCP architecture)
- Code structure defined (FastMCP + Python)
- Architecture decisions documented
- No public-facing documentation exists yet
- No community infrastructure in place
- Legal/licensing decisions pending

---

## User Stories

### Story 1: First-Time User Installation
**As a** developer new to the HEB MCP project,
**I want to** quickly understand what the project does and install it in under 5 minutes,
**so that** I can evaluate if it meets my needs without significant time investment.

**Acceptance Criteria:**
- [ ] Given I visit the GitHub repository, when I read the README, then I understand what HEB MCP does within 30 seconds
- [ ] Given I want to install, when I follow the installation guide, then I have a working setup in under 5 minutes
- [ ] Given I'm new to MCPs, when I read the documentation, then I understand prerequisites (Claude Desktop, Playwright MCP)
- [ ] Given I want to test it, when I complete setup, then I can run a simple product search without authentication
- [ ] Given something goes wrong, when I check troubleshooting, then I find solutions for common issues (Python version, Redis, auth)

### Story 2: Contributing Developer
**As a** developer wanting to contribute code,
**I want to** understand the project structure and contribution process,
**so that** I can submit high-quality pull requests that align with project standards.

**Acceptance Criteria:**
- [ ] Given I want to contribute, when I read CONTRIBUTING.md, then I understand the dev setup process (fork, clone, install dependencies)
- [ ] Given I'm ready to code, when I check guidelines, then I know code style requirements (Ruff, MyPy, test coverage)
- [ ] Given I've made changes, when I run tests, then I can verify my changes locally before submitting
- [ ] Given I submit a PR, when maintainers review, then I receive feedback based on documented standards
- [ ] Given I'm a first-time contributor, when I look for issues, then I find clearly labeled "good first issue" tasks

### Story 3: Bug Reporter
**As a** user encountering a problem,
**I want to** report bugs with enough context for maintainers to reproduce,
**so that** issues can be fixed quickly.

**Acceptance Criteria:**
- [ ] Given I found a bug, when I open an issue, then I'm guided by a template asking for tool name, error message, environment
- [ ] Given the bug involves auth, when I report it, then the template reminds me NOT to share cookies/tokens
- [ ] Given I'm unsure if it's a bug, when I check existing issues, then I find similar problems and resolutions
- [ ] Given I need help, when I check SECURITY.md, then I know how to report security vulnerabilities privately

### Story 4: Feature Requester
**As a** community member with an idea,
**I want to** propose new features aligned with project goals,
**so that** my suggestions are considered for the roadmap.

**Acceptance Criteria:**
- [ ] Given I have a feature idea, when I open an issue, then I'm guided by a template asking for use case, MVP scope, alternatives
- [ ] Given I'm proposing a new tool, when I submit the request, then I explain what HEB API it uses
- [ ] Given my feature is complex, when maintainers review, then they can triage it as MVP / V1 / V2 / Future
- [ ] Given similar features exist, when I search issues, then I find related discussions to avoid duplicates

### Story 5: Maintainer Managing Community
**As a** project maintainer,
**I want to** efficiently manage contributions and issues,
**so that** the project remains healthy and community members feel heard.

**Acceptance Criteria:**
- [ ] Given a PR arrives, when I review it, then automated checks (tests, linting, coverage) have already run
- [ ] Given an issue is opened, when I triage it, then the template provides structured information
- [ ] Given a security issue is reported, when I receive it, then I have a process for private disclosure (SECURITY.md)
- [ ] Given code is merged, when it's released, then semantic versioning is followed and changelog is updated

---

## Essential Documentation

### README.md Structure

**Section 1: What is HEB MCP?**
- One-sentence description: "An MCP server enabling AI agents to search products, manage carts, and schedule pickup at HEB grocery stores"
- Key capabilities (19 tools across 5 domains)
- Visual: Architecture diagram showing dual-MCP setup
- Badge row: License, Python version, build status, PyPI version

**Section 2: Quick Start**
- Prerequisites (Python 3.11+, Claude Desktop, Playwright MCP, Redis)
- Installation command: `pip install heb-mcp`
- Configuration snippet (claude_desktop_config.json)
- First test: "Search for milk at store 590"

**Section 3: Features**
- Table of 19 tools with one-line descriptions
- Highlight: Read operations work without auth
- Highlight: Cart operations require Playwright MCP for auth
- Link to full API reference

**Section 4: Authentication**
- Explain dual-MCP architecture (why two MCPs?)
- Step-by-step: How to authenticate using Playwright MCP
- Security note: Auth state stored locally in ~/.heb-mcp/auth.json
- Troubleshooting: Session expiration, CAPTCHA handling

**Section 5: Development**
- Link to CONTRIBUTING.md
- How to run tests: `pytest`
- How to run locally with Redis: `docker-compose up`

**Section 6: Important Disclaimers**
- Unofficial project, not affiliated with HEB
- Users responsible for compliance with HEB Terms of Service
- No warranties or guarantees
- Link to LICENSE

**Section 7: Community**
- Link to issue templates
- Link to CODE_OF_CONDUCT.md
- Link to SECURITY.md

### Installation Guide (docs/installation.md)

**Prerequisites Section**
- Python 3.11+ (check: `python --version`)
- Claude Desktop or VS Code with Cline/Continue
- npm (for Playwright MCP): `npm --version`
- Optional: Redis for caching (Docker or local)

**Step 1: Install Playwright MCP**
```bash
npm install -g @anthropic-ai/mcp-playwright
```

**Step 2: Install HEB MCP**
```bash
pip install heb-mcp
# or with pipx:
pipx install heb-mcp
```

**Step 3: Configure Claude Desktop**
- File location: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
- Add both Playwright and HEB MCPs
- Set default store ID: `HEB_DEFAULT_STORE=590`

**Step 4: Verify Installation**
- Restart Claude Desktop
- Check MCP tools appear in Claude
- Test: "Search for chicken breast at HEB store 590"

**Step 5 (Optional): Redis Setup**
```bash
docker run -d -p 6379:6379 redis:7-alpine
# or use docker-compose.yml from repo
```

**Step 6: Authentication (for cart operations)**
- Follow authentication flow section
- Save auth state using Playwright MCP

**Troubleshooting Section**
- Python version too old
- Playwright MCP not found in PATH
- Redis connection failed (runs without Redis, just slower)
- Auth state expired

### Usage Examples (docs/usage.md)

**Example 1: Product Search**
```
User: Find organic chicken breast at store 590
Agent uses: product_search(query="organic chicken breast", store_id="590", fields=["brand", "price", "price_per_unit", "location"])
```

**Example 2: Store Lookup**
```
User: Find HEB stores near Austin, TX
Agent uses: store_search(address="Austin, TX", radius_miles=10)
```

**Example 3: Check Product Location**
```
User: Where is item 123456 in store 590?
Agent uses: product_get_location(sku="123456", store_id="590")
```

**Example 4: Find Cheaper Alternatives**
```
User: Find cheaper alternatives to item 123456
Agent uses: product_find_alternatives(sku="123456", store_id="590")
```

**Example 5: Adding to Cart (with confirmation)**
```
User: Add 2 gallons of milk (SKU 123456) to cart
Agent uses: cart_add(product_id="123456", quantity=2)
Returns preview asking for confirmation
User: Confirm
Agent uses: cart_add(product_id="123456", quantity=2, confirm=true)
Item added successfully
```

**Example 6: Recipe to Cart**
```
User: Add ingredients for chicken parmesan for 4 people
Agent uses: Multiple product_search calls
Agent uses: cart_add for each ingredient (with confirmation)
```

### API Reference (docs/api-reference.md)

**For each of 19 tools:**
- Tool name and description
- Parameters (name, type, required, default)
- Return value structure
- Authentication requirement (Yes/No)
- Annotations (readOnly, destructive, requiresConfirmation)
- Example request/response
- Error codes

**Tool Categories:**
1. Store Tools (4 tools)
2. Product Tools (6 tools)
3. Coupon Tools (3 tools)
4. Cart Tools (6 tools)
5. Pickup Tools (2 tools)

**Example Entry:**
```markdown
### product_search

Search for products by query with configurable fields.

**Parameters:**
- `query` (string, required): Search term
- `store_id` (string, optional): Store ID (uses default if not provided)
- `fields` (array, optional): Additional fields to return
  - Options: "brand", "size", "price_per_unit", "image_url", "location", "nutrition", "ingredients", "all"

**Returns:**
```json
{
  "results": [
    {
      "sku": "123456",
      "name": "Hill Country Fare Chicken Breast",
      "price": 4.99,
      "available": true,
      "brand": "Hill Country Fare",
      "size": "1 lb",
      "location": {"aisle": "5", "section": "Meat"}
    }
  ],
  "total_results": 15,
  "source": "api"
}
```

**Authentication:** Not required

**Annotations:** `readOnly`

**Error Codes:**
- `STORE_NOT_FOUND`: Invalid store_id
- `HEB_API_UNAVAILABLE`: API unreachable, check fallback
```

### Troubleshooting Guide (docs/troubleshooting.md)

**Common Issues:**

1. **"No auth state found" error**
   - Cause: Haven't authenticated with Playwright MCP
   - Solution: Follow authentication flow in README
   - Steps: navigate to heb.com/login, login, save_storage_state

2. **"HEB API unavailable" errors**
   - Cause: Rate limiting or API outage
   - Solution: Wait 60 seconds, retry
   - Note: Some operations may use cached data automatically

3. **"CAPTCHA detected" in scraper fallback**
   - Cause: Too many requests from IP
   - Solution: Reduce request frequency, use GraphQL API instead
   - Prevention: Enable Redis caching

4. **Session expired**
   - Cause: Auth cookies expired (HEB sessions last ~30 days)
   - Solution: Re-authenticate using Playwright MCP
   - Detection: cart_check_auth tool shows auth status

5. **Tool not found in Claude**
   - Cause: MCP not properly configured or Claude not restarted
   - Solution: Check claude_desktop_config.json, restart Claude
   - Verification: Tools should appear in Claude's tool list

6. **Redis connection failed**
   - Impact: Server runs but without caching (slower)
   - Solution: Install Redis or remove REDIS_URL from config
   - Note: Redis is optional for development

---

## Community Infrastructure

### CONTRIBUTING.md

**Section 1: Welcome**
- Thank contributors for interest
- Link to CODE_OF_CONDUCT.md
- Explain types of contributions welcome: bug reports, feature requests, code, documentation

**Section 2: Development Setup**
```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/heb-mcp.git
cd heb-mcp

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter and type checker
ruff check .
mypy src/
```

**Section 3: Making Changes**
- Branch naming: `feature/add-nutrition-filter` or `bugfix/cart-quantity-error`
- Commit messages: Conventional commits format
  - `feat: Add nutrition filtering to product search`
  - `fix: Handle expired sessions in cart operations`
  - `docs: Update authentication flow diagram`
- Code style: Ruff configuration in pyproject.toml
- Type hints: Required for all functions
- Tests: Required for new features (pytest)
- Coverage: Aim for 80%+ coverage

**Section 4: Pull Request Process**
1. Update documentation if changing user-facing behavior
2. Add tests for new functionality
3. Ensure all tests pass: `pytest`
4. Run linter: `ruff check .`
5. Submit PR with clear description
6. Link related issues: "Closes #123"
7. Wait for maintainer review
8. Address feedback
9. Maintainer merges when approved

**Section 5: Good First Issues**
- Label: `good first issue`
- Examples: Documentation improvements, adding tests, fixing typos
- Typically < 50 lines of code changes

**Section 6: Feature Requests**
- Open issue first before implementing major features
- Discuss approach with maintainers
- Align with project roadmap (MVP → V1 → V2)

**Section 7: Questions**
- Open a discussion (not an issue) for questions
- Check existing issues/discussions first
- Be specific about what you're trying to do

### CODE_OF_CONDUCT.md

Use **Contributor Covenant v2.1** (industry standard).

**Key sections:**
- Our Pledge: Inclusive, welcoming community
- Our Standards: Expected behavior (respectful, constructive, professional)
- Unacceptable Behavior: Harassment, trolling, political attacks
- Enforcement: How violations are handled
- Reporting: Contact maintainers privately
- Scope: Applies to all project spaces (issues, PRs, discussions)

### SECURITY.md

**Section 1: Reporting a Vulnerability**
- Do NOT open public issues for security bugs
- Email: [maintainer email] with "SECURITY" in subject
- Include: Description, reproduction steps, potential impact
- Response time: Within 48 hours

**Section 2: Supported Versions**
| Version | Supported |
|---------|-----------|
| 1.x.x   | Yes       |
| < 1.0   | No        |

**Section 3: Security Considerations**
- Auth state contains session cookies (keep ~/.heb-mcp/auth.json secure)
- Never share auth.json in bug reports
- Redis may contain cached prices/inventory (no sensitive data)
- MCP protocol uses stdio (local only, not exposed to network)

**Section 4: Known Limitations**
- Session hijacking: If auth.json is stolen, attacker can access HEB account
- Mitigation: File permissions set to 600 (owner read/write only)
- CAPTCHA: Browser automation may trigger CAPTCHAs (expected behavior)

**Section 5: Disclosure Policy**
- 90-day disclosure timeline
- Maintainers will patch and release before public disclosure
- Credit given to reporter (if desired)

### Issue Templates

**Bug Report Template (.github/ISSUE_TEMPLATE/bug_report.md)**
```markdown
## Bug Description
A clear description of what the bug is.

## Tool Affected
Which MCP tool is causing the issue? (e.g., `product_search`, `cart_add`)

## Steps to Reproduce
1. Call tool with parameters: ...
2. Observe error: ...

## Expected Behavior
What should happen?

## Actual Behavior
What actually happens?

## Error Message
```
Paste full error message here
```

## Environment
- Python version: (e.g., 3.11.5)
- HEB MCP version: (e.g., 1.0.0)
- Operating system: (e.g., macOS 14.3)
- Redis installed: Yes/No
- Playwright MCP version: (e.g., 1.2.3)

## Additional Context
- [ ] I have checked existing issues
- [ ] I have removed sensitive data (no cookies/tokens shared)
```

**Feature Request Template (.github/ISSUE_TEMPLATE/feature_request.md)**
```markdown
## Feature Description
Clear description of the proposed feature.

## Problem It Solves
What user need does this address?

## Proposed Solution
How should this work?

## Use Case Example
```
User: "Find gluten-free bread at store 590"
Agent uses: product_search(query="bread", store_id="590", dietary_filters=["gluten-free"])
```

## Alternatives Considered
What other approaches could solve this?

## API/Tool Impact
- New tool needed: Yes/No
- Existing tool enhancement: Which tool?
- Requires new HEB API endpoint: Yes/No

## Priority Suggestion
- [ ] MVP (critical for basic functionality)
- [ ] V1 (valuable enhancement)
- [ ] V2 (nice to have)
- [ ] Future (low priority)

## Additional Context
Links to related issues, documentation, etc.
```

**Pull Request Template (.github/pull_request_template.md)**
```markdown
## Description
What does this PR do?

## Related Issue
Closes #(issue number)

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to break)
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added for this change
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style (ruff check passes)
- [ ] Type hints added (mypy passes)
- [ ] Documentation updated (README, docs/, docstrings)
- [ ] Commit messages follow conventional commits
- [ ] No sensitive data included (API keys, cookies, tokens)

## Screenshots (if applicable)
```

---

## Legal Requirements

### LICENSE File

**Recommendation: MIT License**

**Rationale:**
- Most permissive OSI-approved license
- Widely understood by developers
- Compatible with commercial use
- Used by 55% of GitHub projects
- Simple and short (easier to comply with)

**Alternative: Apache 2.0**
- More explicit patent grant
- Better for corporate contributors
- More verbose (may deter casual contributors)
- Use if patent protection is critical

**License Text (MIT):**
```
MIT License

Copyright (c) 2026 [Your Name/Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### DISCLAIMER.md

**Purpose:** Clarify relationship with HEB, legal responsibilities, terms of service compliance.

```markdown
# Disclaimer

## Not Affiliated with HEB

This project is an **unofficial, community-driven** tool and is **not affiliated with, endorsed by, or sponsored by H-E-B, LP or its subsidiaries**.

The HEB name, logo, and trademarks are property of H-E-B, LP.

## Terms of Service

Users of this software are responsible for complying with HEB's Terms of Service when using this tool to interact with HEB's website and APIs.

HEB may change their APIs, terms, or access policies at any time. This software may stop working without notice if HEB makes changes.

## No Warranties

This software is provided "as is" without warranty of any kind. See LICENSE for full legal terms.

## Data and Privacy

- This software interacts with HEB's public-facing APIs and website
- Authentication is handled via browser cookies stored locally on your machine
- No data is sent to third parties
- No analytics or tracking by this project
- Users are responsible for securing their authentication state files

## Use at Your Own Risk

- Automated use of HEB's website may violate their Terms of Service
- HEB may rate-limit or block access from your IP
- This tool is intended for personal use, not commercial automation
- Users assume all legal and financial responsibility for actions taken using this tool

## Reporting Issues with HEB Services

If you encounter problems with HEB's website or services, contact HEB directly. This project cannot help with HEB account issues, order problems, or service outages.
```

### Privacy Considerations

**Data Handling Principles:**
1. **Local First**: All data stored locally (no remote servers)
2. **No Telemetry**: No usage analytics, crash reports, or tracking
3. **Minimal Storage**: Only auth state (cookies) persisted
4. **User Control**: Users can delete ~/.heb-mcp/ at any time

**README Privacy Section:**
```markdown
## Privacy and Data

- All data stored locally on your machine
- Auth state: `~/.heb-mcp/auth.json` (cookies only)
- Redis cache: Product prices, store info (no personal data)
- No telemetry, analytics, or data sent to maintainers
- No third-party services (except HEB's own APIs)
```

**Logging Privacy:**
- Structured logs to stderr
- User identifiers hashed (never log raw session IDs)
- No logging of cart contents or purchase history
- Debug mode: Warn users that detailed request/response data is logged

---

## Scope Tiers

### MVP (Required for Release)

**Must be complete before v1.0.0 release:**

1. **Core Documentation**
   - [ ] README.md (all sections from "Essential Documentation")
   - [ ] LICENSE file (MIT recommended)
   - [ ] DISCLAIMER.md (unofficial status, TOS responsibility)
   - [ ] Installation guide (docs/installation.md)
   - [ ] Basic usage examples (docs/usage.md)

2. **Legal/Compliance**
   - [ ] License file in root
   - [ ] Disclaimer about unofficial status in README
   - [ ] No HEB trademarks in project name or logo
   - [ ] Copyright notice in source files

3. **Community Infrastructure (Basic)**
   - [ ] CONTRIBUTING.md (dev setup, PR process)
   - [ ] CODE_OF_CONDUCT.md (Contributor Covenant)
   - [ ] Bug report issue template
   - [ ] Feature request issue template

4. **Code Quality**
   - [ ] All 19 tools implemented and tested
   - [ ] Unit tests with >70% coverage
   - [ ] Linting configured (Ruff)
   - [ ] Type checking configured (MyPy)
   - [ ] CI pipeline (GitHub Actions: test, lint, type-check)

5. **Package Distribution**
   - [ ] pyproject.toml configured
   - [ ] Published to PyPI as `heb-mcp`
   - [ ] Version 1.0.0 tagged
   - [ ] Installation works via `pip install heb-mcp`

**MVP Exit Criteria:**
- New user can install and run product search in under 5 minutes
- First-time contributor can set up dev environment and run tests
- All required documentation is present and accurate

---

### V1 (Should Have for Strong Launch)

**Enhances MVP to provide professional polish:**

1. **Comprehensive Documentation**
   - [ ] Full API reference for all 19 tools (docs/api-reference.md)
   - [ ] Troubleshooting guide (docs/troubleshooting.md)
   - [ ] Architecture documentation (docs/architecture.md)
   - [ ] Configuration reference (docs/configuration.md)
   - [ ] FAQ section in README

2. **Advanced Community Infrastructure**
   - [ ] SECURITY.md (vulnerability reporting)
   - [ ] Pull request template
   - [ ] Discussion categories (Q&A, Ideas, Show and Tell)
   - [ ] "Good first issue" labels and issues
   - [ ] CHANGELOG.md (semantic versioning)

3. **Developer Experience**
   - [ ] Integration tests (test against HEB APIs)
   - [ ] E2E tests (full user workflows)
   - [ ] Test coverage >80%
   - [ ] Docker Compose for local dev with Redis
   - [ ] VS Code dev container configuration

4. **Quality Assurance**
   - [ ] GitHub Actions: Automated release to PyPI
   - [ ] GitHub Actions: Documentation deployment
   - [ ] Badge in README (build status, coverage, PyPI version)
   - [ ] Pre-commit hooks for linting/formatting

5. **Examples and Demos**
   - [ ] Example workflows (docs/examples/)
   - [ ] Video demo (YouTube or Loom)
   - [ ] Claude Desktop screenshot showing tools
   - [ ] Sample conversation showing agent using HEB MCP

**V1 Exit Criteria:**
- Project appears professional and well-maintained
- Contributors can easily find tasks and understand expectations
- Users can self-serve for common issues via documentation

---

### Future (Nice to Have, Post-Launch)

**Can be added after successful v1.0.0 launch:**

1. **Documentation Enhancements**
   - [ ] Interactive API explorer (Swagger/ReDoc)
   - [ ] Video tutorials (installation, first use, authentication)
   - [ ] Blog post: "Building an MCP for HEB"
   - [ ] Case studies from users

2. **Community Growth**
   - [ ] GitHub Discussions enabled
   - [ ] Discord server for real-time help
   - [ ] Monthly release notes blog
   - [ ] Contributor recognition (CONTRIBUTORS.md)

3. **Developer Tools**
   - [ ] Mock HEB API server for testing
   - [ ] Development mode with fake data
   - [ ] Postman collection for HEB GraphQL
   - [ ] CLI tool for testing individual tools

4. **Internationalization**
   - [ ] Spanish documentation (serves Texas Hispanic community)
   - [ ] Error messages in Spanish
   - [ ] README.es.md

5. **Advanced CI/CD**
   - [ ] Nightly builds against HEB production
   - [ ] Performance benchmarking
   - [ ] Security scanning (Dependabot, CodeQL)
   - [ ] Automated dependency updates

6. **Ecosystem Integration**
   - [ ] List in Anthropic MCP directory
   - [ ] Submit to Awesome MCP list
   - [ ] Integration with groceries-mcp multi-vendor tool
   - [ ] Blog post on Anthropic's community forum

**Future Exit Criteria:**
- None (ongoing enhancements based on community needs)

---

## Edge Cases and Questions

### Edge Cases to Address

1. **HEB API Changes**
   - What happens when HEB changes GraphQL schema?
   - Solution: Version GraphQL queries, add schema validation
   - Documentation: Warn users that API breakage is possible

2. **Multiple Claude Instances**
   - If two Claude instances share ~/.heb-mcp/auth.json, race conditions?
   - Solution: File locking on auth state reads/writes
   - Document: Not recommended to run multiple instances simultaneously

3. **Auth State Sync**
   - If user logs out on heb.com, auth.json becomes invalid
   - Solution: cart_check_auth tool detects and reports
   - Document: How to re-authenticate

4. **Store ID Confusion**
   - Users may not know their store ID
   - Solution: store_search by address, then store_set_default
   - Document: How to find store ID

5. **Rate Limiting**
   - Heavy usage triggers HEB rate limits
   - Solution: Circuit breaker opens, suggests wait time
   - Document: Expected request limits, caching benefits

6. **Redis Unavailable**
   - What if Redis crashes mid-operation?
   - Solution: Graceful degradation (continue without cache)
   - Document: Redis is optional but recommended

7. **Playwright MCP Not Installed**
   - User tries cart operations without Playwright MCP
   - Solution: cart_check_auth returns clear error with installation instructions
   - Document: Prerequisites prominently in README

### Questions for User

1. **License Decision**
   - Question: Prefer MIT (simple, permissive) or Apache 2.0 (explicit patents)?
   - Recommendation: MIT unless patent concerns exist
   - Impact: Affects contributor requirements and corporate adoption

2. **Maintainer Contact**
   - Question: What email should be in SECURITY.md for vulnerability reports?
   - Options: Personal email, create security@domain, GitHub private reporting
   - Recommendation: Enable GitHub private vulnerability reporting (free)

3. **Project Name**
   - Current: "heb-mcp"
   - Question: Is this acceptable given HEB trademark?
   - Recommendation: Keep "heb-mcp" (descriptive, not claiming affiliation)
   - Alternative: "grocery-mcp-heb" if legal concerns arise

4. **Contribution CLA**
   - Question: Require Contributor License Agreement (CLA)?
   - Pros: Legal protection for maintainers
   - Cons: Friction for contributors
   - Recommendation: No CLA for MVP (can add later if needed)

5. **Code of Conduct Enforcement**
   - Question: Who enforces CODE_OF_CONDUCT.md?
   - Recommendation: List maintainers in document with contact method
   - Backup: GitHub's community health features (comment moderation)

6. **Release Cadence**
   - Question: How often to release updates?
   - Recommendation: Semantic versioning with patch releases as needed
   - Major versions: When HEB API changes significantly
   - Minor versions: New tools or features
   - Patches: Bug fixes

7. **Telemetry Decision**
   - Question: Add optional telemetry for usage analytics?
   - Pros: Understand which tools are most used
   - Cons: Privacy concerns, complexity
   - Recommendation: No telemetry for MVP (maintain privacy-first approach)

8. **Docker Hub Publishing**
   - Question: Publish Docker image to Docker Hub?
   - Pros: Easier deployment for some users
   - Cons: Maintenance overhead
   - Recommendation: V1 or later (document docker build for now)

---

## Dependency Analysis

### Critical Path Dependencies

**Blocks Release:**
1. LICENSE file (legal requirement)
2. DISCLAIMER.md (unofficial status, TOS)
3. README.md (must explain what, why, how)
4. CONTRIBUTING.md (contributors need guidance)
5. Bug report template (issue quality)
6. Code implementation complete (all 19 tools)
7. Tests passing (quality baseline)
8. PyPI package published (installation method)

**Blocks V1 (Professional Polish):**
1. API reference documentation
2. Troubleshooting guide
3. SECURITY.md
4. CODE_OF_CONDUCT.md
5. Integration and E2E tests
6. CI/CD pipeline
7. Coverage >80%

**Non-Blocking (Future):**
- Video tutorials
- Discord server
- Mock API server
- Spanish documentation

---

## Suggestions

### Process Suggestions

1. **Documentation-First Development**
   - Write README before finalizing code
   - Forces clarity on user experience
   - Identifies gaps in tool design

2. **Staged Release Strategy**
   - v0.9.0: Preview release for feedback (close friends/colleagues)
   - v1.0.0: Public announcement on GitHub, Reddit, Discord
   - v1.1.0: Post-launch improvements based on feedback

3. **Pre-Release Checklist**
   - [ ] Test installation on fresh machine (macOS, Linux, Windows)
   - [ ] Have 2-3 people follow README and report confusion
   - [ ] Search for embarrassing TODOs in code
   - [ ] Verify no secrets/tokens in git history
   - [ ] Test both with and without Redis
   - [ ] Verify Playwright MCP integration

4. **Community Building**
   - Cross-post announcement in:
     - Reddit: r/ChatGPT, r/LocalLLaMA
     - Anthropic Discord #mcp channel
     - Hacker News (Show HN)
   - Tag Anthropic in Twitter/X announcement
   - Submit to Awesome MCP list

### Technical Suggestions

1. **README Badges**
   - Add to top of README:
   - ![Build Status](https://github.com/USER/heb-mcp/actions/workflows/test.yml/badge.svg)
   - ![PyPI Version](https://img.shields.io/pypi/v/heb-mcp)
   - ![Python Version](https://img.shields.io/pypi/pyversions/heb-mcp)
   - ![License](https://img.shields.io/github/license/USER/heb-mcp)

2. **GitHub Repository Settings**
   - Enable Discussions
   - Add topics: `mcp`, `claude`, `heb`, `grocery`, `python`, `fastmcp`
   - Set description: "MCP server for HEB grocery shopping"
   - Set website: Link to docs (GitHub Pages or ReadTheDocs)
   - Enable Issues
   - Add labels: `bug`, `enhancement`, `documentation`, `good first issue`, `help wanted`

3. **Package Metadata (pyproject.toml)**
   ```toml
   [project]
   name = "heb-mcp"
   description = "MCP server enabling AI agents to interact with HEB grocery stores"
   readme = "README.md"
   license = {file = "LICENSE"}
   authors = [{name = "Your Name", email = "your@email.com"}]
   keywords = ["mcp", "claude", "heb", "grocery", "shopping", "ai-agent"]
   classifiers = [
       "Development Status :: 4 - Beta",
       "Intended Audience :: Developers",
       "License :: OSI Approved :: MIT License",
       "Programming Language :: Python :: 3.11",
       "Programming Language :: Python :: 3.12",
   ]
   ```

4. **First Issues to Create**
   - "Good First Issue: Add tests for store_search tool"
   - "Good First Issue: Improve error messages in cart_add"
   - "Documentation: Add example workflow for meal planning"
   - "Enhancement: Support multiple store favorites"

### Content Suggestions

1. **README Opening Hook**
   - Start with compelling example:
   ```
   # HEB MCP: AI-Powered Grocery Shopping

   Enable Claude to search products, compare prices, and manage your HEB cart—all through natural conversation.

   ```
   User: "Find organic chicken breast under $6/lb near me"
   Claude: [Searches HEB] "I found Hill Country Fare organic chicken breast at $5.49/lb at HEB Mueller (2.3 miles away), aisle 5."
   ```
   ```

2. **Visual Aids**
   - Architecture diagram showing dual-MCP setup
   - Screenshot of Claude Desktop with HEB MCP tools
   - GIF of authentication flow
   - Flowchart: Read vs Write operations

3. **FAQ Section**
   ```markdown
   ## FAQ

   **Q: Is this official from HEB?**
   A: No, this is a community project. See DISCLAIMER.md.

   **Q: Will this get my account banned?**
   A: Use responsibly and comply with HEB's Terms of Service. This tool uses the same APIs as heb.com.

   **Q: Can I use this for commercial purposes?**
   A: The code is MIT licensed, but you must comply with HEB's Terms of Service.

   **Q: Why two MCPs (Playwright + HEB)?**
   A: Separating auth from business logic keeps each MCP focused and maintainable.

   **Q: Does this work with delivery?**
   A: Currently pickup only. Delivery support planned for V2.
   ```

4. **Roadmap Section in README**
   ```markdown
   ## Roadmap

   - [x] Product search and inventory
   - [x] Cart management with confirmation
   - [x] Pickup scheduling
   - [ ] Recipe-to-cart parser (V1.5)
   - [ ] Dietary preference management (V1.5)
   - [ ] Delivery support (V2)
   - [ ] Spanish language support (V2)

   See [issues](https://github.com/USER/heb-mcp/issues) for details.
   ```

---

## Compliance Checklist

### Legal Compliance
- [ ] LICENSE file present (MIT or Apache 2.0)
- [ ] Copyright notice in LICENSE
- [ ] DISCLAIMER.md explains unofficial status
- [ ] No HEB trademarks used inappropriately
- [ ] No claims of affiliation with HEB
- [ ] Clear statement about TOS responsibility

### Documentation Compliance
- [ ] README explains what project does
- [ ] Installation instructions are clear
- [ ] Prerequisites listed explicitly
- [ ] Authentication flow documented
- [ ] Troubleshooting section present
- [ ] Links to all supporting docs

### Community Compliance
- [ ] CODE_OF_CONDUCT.md present
- [ ] CONTRIBUTING.md present
- [ ] Issue templates present
- [ ] PR template present
- [ ] Contact method for security issues

### Technical Compliance
- [ ] Package installable via pip
- [ ] Tests run and pass
- [ ] Linting passes
- [ ] Type checking passes
- [ ] No secrets in repository
- [ ] .gitignore configured

### Privacy Compliance
- [ ] No telemetry without consent
- [ ] Auth state stored locally only
- [ ] No PII logged
- [ ] Data handling explained in README
- [ ] Users control their data

---

## Success Metrics

**How do we know documentation is successful?**

1. **Time to First Success**
   - Target: New user runs first product search in <5 minutes
   - Measure: Ask beta testers to time themselves

2. **Issue Quality**
   - Target: 80%+ of issues use templates and provide required info
   - Measure: Review first 20 issues

3. **Contribution Rate**
   - Target: 3+ external contributors in first month
   - Measure: GitHub contributor graph

4. **Self-Service Rate**
   - Target: 70%+ of questions answered by docs (not maintainer)
   - Measure: Link to docs in responses, track how often

5. **Onboarding Feedback**
   - Target: <10% of users report confusion in setup
   - Measure: Ask for feedback in issue/PR templates

---

## Recommendations Summary

### Immediate Actions (MVP)
1. Write README.md (use structure from "Essential Documentation")
2. Add LICENSE file (MIT recommended)
3. Add DISCLAIMER.md (unofficial status)
4. Create CONTRIBUTING.md (dev setup, PR process)
5. Add CODE_OF_CONDUCT.md (Contributor Covenant)
6. Create issue templates (bug, feature)
7. Set up CI pipeline (tests, linting, type-checking)
8. Publish to PyPI as `heb-mcp`

### V1 Enhancements
1. Write full API reference
2. Write troubleshooting guide
3. Add SECURITY.md
4. Create PR template
5. Add integration/E2E tests
6. Reach 80%+ test coverage
7. Set up GitHub Discussions

### Post-Launch
1. Announce in community channels
2. Submit to Awesome MCP
3. Create video demo
4. Monitor first issues/PRs closely
5. Iterate on docs based on feedback

---

## Conclusion

The HEB MCP project is technically well-designed and ready for implementation. The primary gaps are in documentation and community infrastructure, both of which are well-understood and have clear templates to follow.

**Key Insight:** The dual-MCP architecture (Playwright for auth, HEB for grocery logic) is a strength but requires careful documentation to avoid user confusion. The README must clearly explain why two MCPs are needed and how they work together.

**Risk:** Users may struggle with authentication flow on first use. Mitigation: Include detailed auth section in README with screenshots/diagrams.

**Opportunity:** Recipe-to-cart feature (V1.5) could be a major differentiator, but should not block MVP release.

**Recommendation:** Proceed with MVP documentation (README, LICENSE, DISCLAIMER, CONTRIBUTING, issue templates) before writing production code. This will surface any remaining design ambiguities and ensure good developer experience from day one.
