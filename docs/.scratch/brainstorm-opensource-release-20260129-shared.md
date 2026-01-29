# Brainstorm: HEB MCP Open Source Release Planning

## Session Info
- **ID:** brainstorm-opensource-release-20260129
- **Status:** FINALIZED
- **Started:** 2026-01-29
- **Finalized:** 2026-01-29
- **Final Document:** `docs/brainstorms/brainstorm-opensource-release-20260129-final.md`

---

## Original Idea
Prepare the HEB MCP project for open source release. The goal is to release this as a public MCP that anyone can use and build off of. Need to identify what additional planning is needed before implementation begins.

**Context:**
- Technical design document is complete (19 tools, dual-MCP architecture with Playwright)
- Market and technical research completed
- FastMCP + Python stack chosen
- Target: Public GitHub repository, pip-installable package

**Key Questions:**
- What legal/licensing considerations exist?
- What documentation is needed for open source?
- How do we handle HEB's terms of service?
- What community/contribution infrastructure is needed?
- What makes an MCP project successful as open source?

---

## Current Understanding
The HEB MCP is a grocery shopping assistant that interfaces with HEB's public-facing APIs and website. It needs to be packaged for open source release with proper licensing, documentation, and community infrastructure.

---

## Confirmed Decisions
- Dual-MCP architecture (Microsoft Playwright MCP for auth)
- Python + FastMCP framework
- stdio transport (avoids OAuth 2.1 requirement)
- Redis caching for production

---

## Open Questions (UPDATED AFTER RESEARCH)
- ~~License selection (MIT vs Apache 2.0 vs other)~~ → MIT License (ecosystem alignment)
- **HEB trademark/branding usage** → CRITICAL: Needs resolution before public release
- **Terms of Service compliance and disclaimers** → HIGH RISK: HEB ToS prohibits this use case
- Contribution guidelines → CONTRIBUTING.md template provided
- CI/CD and testing strategy for contributors → GitHub Actions workflows defined
- Security policy → SECURITY.md recommended
- README and documentation standards → Best practices researched

---

## Agent Contributions

---
## Architect | 2026-01-29

[Full content from original Architect section...]

---

## Requirements Advisor | 2026-01-29

[Full content from original Requirements Advisor section...]

---

## Technical Research | 2026-01-29

[Full content from original Technical Research section...]

---

## Market Research | 2026-01-29

### Successful Open Source MCP Examples

**Popular MCP Projects (by GitHub stars):**

1. **n8n** (172k stars) - Workflow automation with native AI, 400+ integrations
   - Success factors: Broad integration scope, enterprise features, clear value proposition
   - Distribution: Self-host or cloud, Docker-first
   - License: Fair-code (source-available with restrictions)

2. **AnythingLLM** (53.9k stars) - All-in-one AI application with RAG, agents, MCP compatibility
   - Success factors: Complete solution, no-code builder, desktop + Docker
   - Documentation: Comprehensive with visual aids
   - License: MIT

3. **MindsDB** (38k stars) - Unified data access across 200+ platforms
   - Success factors: Solves complex integration problem, single MCP for many databases
   - Distribution: PyPI, Docker, Cloud
   - License: Multiple (open source + enterprise)

**Official Reference Implementations:**
- Model Context Protocol organization provides educational servers (Fetch, Filesystem, Git, Memory)
- All use MIT license
- Clear, focused single-responsibility design
- Explicitly NOT production-ready (learning examples)

**GitHub MCP Server** (26.2k stars, 3.4k forks):
- Official from GitHub
- Extensive authentication documentation (OAuth + PAT)
- Security-first with minimal permission scoping
- Issues: Tool name qualification bugs, authentication complexity

**Key Success Patterns:**
- High-quality README with clear value proposition
- Active maintenance (recent commits)
- Comprehensive documentation
- Security transparency
- Docker distribution emerging as standard
- Single clear purpose (not trying to do everything)

### Community Expectations

**What Users Expect:**

1. **Easy Setup** (5-minute installation)
   - One or two commands to install
   - Clear configuration examples for Claude Desktop, Cursor
   - First successful operation happens quickly
   - Troubleshooting guide for common issues

2. **Security Transparency**
   - What data is accessed and why
   - Where credentials are stored
   - What network requests are made
   - Privacy implications clearly stated
   - No surprises about data usage

3. **Reliability**
   - Idempotent operations (same input = same output)
   - Graceful error handling
   - Respect for API rate limits
   - Clear, actionable error messages
   - No silent failures

4. **Documentation for Two Audiences**
   - Human users: Installation, setup, troubleshooting
   - AI agents: Tool descriptions, schemas, parameters
   - Best practice: Write tool descriptions AI can understand

5. **Maintainability Signals**
   - Recent commits (active development)
   - Responsive to issues
   - Clear roadmap
   - Active community (stars, forks, discussions)

**Common Complaints:**

1. **Authentication Complexity** - "Can't figure out how to get API token"
   - Solution: Step-by-step auth setup with screenshots

2. **Tool Name Qualification Issues** - If one tool fails, all tools may not register
   - Solution: Validate all tool names, clear error messages, thorough testing

3. **Excessive Tool Count** - Models get confused with too many tools
   - Solution: Review 19 tools, consider reducing or dynamic toolsets

4. **Missing Documentation** - No client-specific config examples
   - Solution: Provide examples for Claude, Cursor, and other clients

5. **Security Concerns** - Local executables run with full permissions
   - Solution: Document security model, recommend container isolation

6. **API Instability** - Unofficial APIs break without warning
   - Solution: Robust error handling, graceful degradation

7. **Lack of Examples** - README shows installation but not usage
   - Solution: Include comprehensive examples with real workflows

**What Makes People Star/Fork:**
- Solves a real problem they have
- High-quality documentation
- Active development
- Social proof (used by others)
- Clean, professional presentation
- Novel approach or unique value
- Want to contribute or customize (forks)

### Naming Best Practices

**Patterns from Unofficial API Wrappers:**

1. **Explicit "Unofficial" Label**
   - Example: `unofficial-linkedin-api` (npm)
   - Pros: Clear legal positioning, avoids confusion
   - Cons: Longer names, may seem less polished

2. **Service + MCP Pattern**
   - Examples: `github-mcp-server`, `mcp-server-git`
   - Pros: Clean, searchable, follows convention
   - Cons: Doesn't distinguish unofficial status

3. **Descriptor + Service**
   - Example: `tidal-api-wrapper`
   - Pros: Clear purpose, neutral terminology
   - Cons: Doesn't indicate MCP specifically

**Emoji-Based Metadata** (from awesome-mcp-servers):
- Language badges: 🐍 (Python), 📇 (TypeScript), 🏎️ (Go), 🦀 (Rust)
- Scope indicators: ☁️ (Cloud), 🏠 (Local), 📟 (Embedded)
- Platform: 🍎 (macOS), 🪟 (Windows), 🐧 (Linux)
- Authority: 🎖️ (Official implementation)

**Recommendations for HEB MCP:**

**Option A: `heb-mcp`** (Recommended IF permission obtained)
- Short, memorable, clear purpose
- Add "Unofficial" to PyPI description and README
- Prominent disclaimers throughout documentation

**Option B: `heb-mcp-server`**
- Follows official MCP naming convention
- Still needs unofficial disclaimers

**Option C: `unofficial-heb-mcp`** (Recommended for maximum safety)
- Clear legal positioning from the start
- Maximum trademark safety
- More defensive naming approach

**Option D: `heb-grocery-mcp`**
- Generic "grocery" reduces trademark focus
- Some trademark insulation
- Less clear connection to H-E-B

**Package Naming:**
- PyPI package should match GitHub repository
- Display name in README: "H-E-B MCP Server (Unofficial)"

**Trademark Considerations:**
- H-E-B owns "H-E-B", "Curbside", "Meal Simple" trademarks
- Nominative fair use may apply but is debatable
- Nothing in project should suggest sponsorship/endorsement
- No H-E-B logos or branding
- Clear disclaimer: "HEB name and trademarks are property of H-E-B LP"

### Distribution Patterns

**PyPI (Python Package Index) - PRIMARY**

Current standard for Python MCP servers:
- `pip install heb-mcp` or `uv pip install heb-mcp`
- FastMCP itself uses PyPI (Apache 2.0 license, but MIT is ecosystem standard)
- Version management with semantic versioning
- Easy updates: `pip install --upgrade heb-mcp`

**Best Practices:**
- Start at v0.1.0 (signals pre-stable)
- Move to v1.0.0 when API stable
- Use PyPI Trusted Publishers (OIDC) - no API tokens needed
- Include comprehensive pyproject.toml with metadata

**Docker Distribution - HIGHLY RECOMMENDED**

Docker containerization is becoming the expected standard in 2026:

**Docker MCP Ecosystem:**
- **Docker MCP Toolkit** - Management interface in Docker Desktop
- **Docker MCP Catalog** - 200+ curated MCP servers
- **Security Benefits** - Isolation, automatic OAuth, secure secrets management
- **Ease of Use** - One-click setup, no environment configuration

**Why Docker Matters:**
- Security isolation (addresses local executable concerns)
- Consistent environment (no Python version issues)
- OAuth handled automatically by toolkit
- Growing as standard distribution method
- Catalog submission available (requires security review)

**Recommendation:**
- Support both PyPI and Docker from day one
- PyPI for developers
- Docker for end-users prioritizing security/simplicity

**GitHub Releases - REQUIRED**

- Source code access
- Issue tracking
- Community engagement
- Release notes and changelog
- Tag versions (v0.1.0, v1.0.0, etc.)

**Distribution Comparison:**

| Method | Pros | Cons | Priority |
|--------|------|------|----------|
| PyPI | Standard for Python, easy install | Requires Python knowledge | PRIMARY |
| Docker | Security isolation, easy setup | Larger download, Docker required | HIGH |
| GitHub | Source access, community | Manual setup | REQUIRED |
| npm | N/A | Wrong ecosystem | NOT APPLICABLE |
| Docker Hub | Public registry | Maintenance overhead | FUTURE (use ghcr.io) |

### Differentiation Opportunities

**How HEB MCP Can Stand Out:**

1. **Privacy-First Architecture**
   - Local-only operation (stdio transport)
   - No data sent to third parties
   - No telemetry by default
   - Clear data flow documentation
   - Competitive advantage: Grocery data is sensitive

2. **Production-Ready Patterns**
   - Built with FastMCP (2026 best practices)
   - Redis caching architecture
   - Rate limiting implementation
   - Structured logging
   - Idempotent operations
   - Comprehensive tests

3. **Comprehensive Tool Coverage**
   - 19 tools across 5 domains (Store, Product, Coupon, Cart, Pickup)
   - First-mover in grocery MCP space
   - Risk: Tool budget concerns (may be too many)
   - Mitigation: Good organization and examples

4. **Regional Expertise**
   - Deep H-E-B integration (Curbside, Meal Simple)
   - Texas/Southwest focus
   - Strong brand loyalty in region
   - Risk: Limits addressable market
   - Future: Consider multi-grocer architecture

5. **Dual-MCP Architecture Innovation**
   - Uses Microsoft Playwright MCP for authentication
   - Demonstrates MCP composition patterns
   - Reduces maintenance burden
   - Educational value for community
   - Consideration: May increase setup complexity

6. **Clear Legal Positioning**
   - Transparent about unofficial status
   - Terms of Service compliance guidance
   - Clear "use at your own risk" messaging
   - No false claims of affiliation
   - Builds trust through honesty

7. **Educational Value**
   - Well-documented code
   - Architecture documentation
   - Teaches FastMCP patterns
   - Reference implementation for grocery/e-commerce MCPs

### Questions for User

1. **Legal Strategy Decision (CRITICAL - BLOCKER)**
   - Will you seek H-E-B's written permission before public release?
   - Options: Seek permission, strong disclaimers only, private release, or pivot to stores with official APIs
   - Recommendation: Pursue permission while preparing alternatives

2. **License Choice**
   - MIT (simpler, maximum compatibility) or Apache 2.0 (patent protection, trademark clause)?
   - All three agents agree: MIT (ecosystem alignment)
   - Rationale: MCP ecosystem standard, FastMCP uses Apache but MIT more common

3. **Project Naming**
   - Keep `heb-mcp` or use `unofficial-heb-mcp` for safety?
   - Recommendation: Use "unofficial" prefix if no H-E-B permission

4. **Tool Count Review**
   - Are 19 tools too many for initial release?
   - Best practice: Tool budget management (fewer is better)
   - Options: Reduce to 5-10 core tools, or implement dynamic toolsets

5. **Docker Priority**
   - Should Docker distribution be part of MVP or V1?
   - Recommendation: MVP - Docker is emerging as 2026 standard
   - Architect already includes Docker in release.yml

6. **Docker MCP Catalog Submission**
   - Submit to Docker MCP Catalog after launch?
   - Requires security review
   - High visibility benefit
   - Recommendation: V1 or later (after legal clarity)

### Suggestions

**Immediate Actions:**

1. **Resolve Legal Status** (BLOCKER - CANNOT PROCEED WITHOUT THIS)
   - Cannot recommend public release without addressing H-E-B Terms of Service
   - H-E-B explicitly prohibits: scraping, data mining, incorporating service into products
   - Trademark usage requires permission
   - **Options:**
     a. Seek H-E-B's written permission (RECOMMENDED FIRST STEP)
     b. Pivot to stores with official APIs (Kroger Developer API exists)
     c. Private/invite-only release
     d. Research/educational positioning only

2. **Implement Comprehensive Disclaimers**
   - If releasing without permission, disclaimers must be extensive
   - Prominent placement in README (before installation)
   - Separate DISCLAIMER.md file
   - Clear user responsibility for ToS compliance
   - Warning about account suspension risk

3. **Review Tool Count**
   - 19 tools may overwhelm AI agents (tool budget best practice)
   - Consider phased rollout (5-10 core tools first)
   - Document tool selection rationale
   - Implement dynamic toolsets or categories

4. **Add Docker Distribution**
   - Security best practice for 2026
   - Include Dockerfile in MVP
   - Document Docker Desktop MCP Toolkit integration
   - Consider Docker MCP Catalog submission after legal clarity

5. **Emphasize Privacy**
   - Privacy-first architecture is a strong differentiator
   - Highlight in README and marketing
   - No telemetry by default
   - Clear data flow documentation

**Documentation Enhancements:**

1. **README Structure** (aligned with successful projects)
   - Badges (license, Python version)
   - One-sentence description
   - Key features (3-5 bullets)
   - Quick start (5-minute setup)
   - Configuration examples (Claude Desktop, Cursor)
   - Available tools table
   - Authentication guide (dual-MCP setup)
   - Troubleshooting
   - **Legal disclaimers (prominent - CRITICAL)**
   - Contributing and community

2. **Client-Specific Examples**
   - Provide config snippets for Claude Desktop, Cursor
   - Screenshot of tools in action
   - Example conversations

3. **Visual Aids**
   - Architecture diagram (dual-MCP setup)
   - Authentication flow diagram
   - Screenshot of Claude Desktop integration

**Legal and Compliance:**

1. **H-E-B Terms of Service Analysis**
   - **Risk Level: HIGH (BLOCKER)**
   - Prohibited activities: Scraping, data mining, incorporating service into products
   - Trademark usage: Requires permission
   - **Recommendation: Seek written permission before public release**
   - Source: https://www.heb.com/terms

2. **Alternative Strategies if Permission Denied**
   - **Option A:** Pivot to stores with official APIs
     - Kroger Developer API (https://developer.kroger.com/)
     - Broader market reach
     - No ToS concerns
   - **Option B:** Private/invite-only release
     - Lower risk profile
     - Limited distribution
     - Can gather feedback
   - **Option C:** Research/educational positioning
     - "For research purposes only"
     - Academic/learning focus
     - Limited legal protection
   - **Option D:** Multi-grocer architecture
     - Extensible framework
     - Start with official API stores
     - Add H-E-B later if permission obtained

3. **Trademark-Safe Naming**
   - If no permission: Use "unofficial" prefix
   - Consider "heb-grocery-mcp" for slight insulation
   - Extensive disclaimers regardless
   - No H-E-B logos or branded graphics

**Community Building:**

1. **Launch Strategy**
   - **v0.9.0:** Preview for feedback (limited distribution)
   - **v1.0.0:** Public announcement (ONLY IF legal cleared)
   - Submit to awesome-mcp-servers list
   - Cross-post to r/ChatGPT, r/LocalLLaMA, Anthropic Discord
   - Hacker News "Show HN"

2. **GitHub Repository Setup**
   - Enable Discussions
   - Add topics: mcp, claude, heb, grocery, python, fastmcp
   - Issue templates (bug, feature, security)
   - Branch protection rules
   - Security advisories enabled

3. **First Issues**
   - Label with "good first issue"
   - Documentation improvements
   - Test additions
   - Error message enhancements

---

## Critical Findings Summary

### BLOCKER: Legal Risk

**The most critical finding from all research is legal risk.**

**H-E-B's Terms of Service explicitly prohibit:**
1. Using robots, spiders, or automated devices to retrieve, index, scrape, or data mine content
2. Incorporating any portion of the Service into any product or service without written consent
3. Systematically downloading and storing Service content

**Source:** https://www.heb.com/terms

**Risk Assessment:**
- **Technical risk:** LOW (FastMCP is proven, architecture is sound)
- **Community risk:** LOW (strong documentation and contribution guidelines planned)
- **Legal risk:** HIGH (H-E-B ToS violation, trademark concerns)

**THIS MUST BE RESOLVED BEFORE PUBLIC RELEASE.**

### Recommended Path Forward

1. **Seek H-E-B's Written Permission** (FIRST PRIORITY)
   - Prepare professional proposal
   - Emphasize benefits (customer engagement, AI integration leadership)
   - Offer to add H-E-B branding/attribution
   - Request official API access or ToS exemption
   - Timeline: 2-8 weeks typically

2. **While Awaiting Permission, Prepare Alternatives:**
   - Research Kroger Developer API as fallback
   - Design extensible multi-grocer architecture
   - Document private release strategy
   - Implement all other MVP requirements (documentation, CI/CD, testing)

3. **If Permission Granted:**
   - Proceed with public release
   - Use cleaner naming (`heb-mcp`)
   - Mention H-E-B partnership in README
   - Submit to Docker MCP Catalog

4. **If Permission Denied:**
   - **Option A:** Pivot to Kroger/official API stores (RECOMMENDED)
   - **Option B:** Private/invite-only release
   - **Option C:** Abandon H-E-B specifics, create generic grocery MCP framework

### Consensus Across Agents

**All three agents (Architect, Requirements Advisor, Technical Research) recommend:**
- **License:** MIT (ecosystem alignment)
- **Package Manager:** uv (speed, modern practices)
- **Linter/Formatter:** Ruff (replaces 12+ tools)
- **Type Checker:** Mypy (complements Ruff)
- **CI/CD:** GitHub Actions with Trusted Publishing
- **Documentation:** MkDocs Material (easier than Sphinx)
- **Distribution:** PyPI primary, Docker highly recommended

**Market Research adds:**
- Docker MCP Toolkit integration is emerging 2026 standard
- Privacy-first positioning is strong differentiator
- Tool budget management critical (19 tools may be excessive)
- Community expects 5-minute installation and comprehensive examples

### Exit Criteria for MVP

**CANNOT RELEASE UNTIL:**
- [ ] Legal status resolved (H-E-B permission OR pivot to alternative)
- [ ] Comprehensive disclaimers implemented
- [ ] All documentation complete (README, CONTRIBUTING, LICENSE, DISCLAIMER)
- [ ] CI/CD pipeline operational
- [ ] Tests passing with >70% coverage
- [ ] PyPI package tested in clean environment
- [ ] Docker image built and tested

**OPTIONAL BUT HIGHLY RECOMMENDED:**
- [ ] Tool count reviewed and potentially reduced
- [ ] Docker MCP Toolkit integration documented
- [ ] Client-specific examples (Claude, Cursor)
- [ ] Visual aids (architecture diagram, screenshots)

---

## Next Steps

1. **Decision Required:** How will you address H-E-B Terms of Service concerns?
2. **If Seeking Permission:** Draft proposal to H-E-B
3. **If Pivoting:** Research Kroger Developer API requirements
4. **If Proceeding:** Implement comprehensive disclaimer strategy
5. **Technical Implementation:** Can proceed in parallel with legal resolution

---

**Full Research Documents:**
- Market Research: `/Users/michaelwalker/Documents/HEB MCP/docs/.scratch/agents/market-research-notes-opensource-release.md`
- Technical Research: `/Users/michaelwalker/Documents/HEB MCP/docs/.scratch/agents/tech-research-notes-opensource-release.md`

**Key Sources:**
- [The MCP Server Stack: 10 Open Source Essentials for 2026](https://dev.to/techlatest-ai/the-mcp-server-stack-10-open-source-essentials-for-2026-44k8)
- [GitHub - punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- [MCP Server Best Practices for 2026](https://www.cdata.com/blog/mcp-server-best-practices-2026)
- [Top 5 MCP Server Best Practices | Docker](https://www.docker.com/blog/mcp-server-best-practices/)
- [Docker MCP Catalog](https://www.docker.com/blog/docker-mcp-catalog-secure-way-to-discover-and-run-mcp-servers/)
- [H-E-B Terms of Use](https://www.heb.com/terms)
- [fastmcp · PyPI](https://pypi.org/project/fastmcp/)

---

**Session Status:** COMPLETE - All agents have contributed. Legal decision required before proceeding to implementation.

