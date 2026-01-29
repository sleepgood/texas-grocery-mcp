# Technical Research: MCP Servers for Python Open Source Development and Release

**Date**: 2026-01-29
**Requested By**: Software Engineer
**Request**: Research MCP servers available for building and releasing Python open source projects, focusing on GitHub MCPs, Python/PyPI MCPs, documentation MCPs, and other development tool MCPs.

## Executive Summary

The MCP (Model Context Protocol) ecosystem in January 2026 offers robust tooling for Python open source project development and release workflows. GitHub's official MCP server provides comprehensive repository, issue, PR, and CI/CD automation capabilities. For Python-specific tasks, FastMCP is the modern framework for building Python MCPs, while specialized servers handle PyPI queries, security scanning, and dependency analysis. The official Anthropic reference servers (Git, Filesystem, etc.) provide foundational capabilities, with community-maintained alternatives available for specific needs. All MCPs can be easily configured in Claude Desktop via JSON configuration. This ecosystem significantly reduces friction for AI-assisted open source development workflows.

## TL;DR: Recommended Stack

**Three MCPs to get started**:

1. **GitHub MCP** (github/github-mcp-server)
   - Repository, issue, PR, release management
   - CI/CD integration and Dependabot security scanning
   - Command: `npx -y @github/github-mcp-server`

2. **Filesystem + Git Servers** (Anthropic official)
   - Project file access and git history analysis
   - Both Node.js based reference implementations

3. **PyPI Query MCP** (Community maintained)
   - Dependency version checking and security scanning
   - Command: `python -m mcp_pypi`

**Setup time**: 15-30 minutes total

## GitHub MCP Server

### Official GitHub MCP

**Repository**: https://github.com/github/github-mcp-server
**Status**: Actively maintained by GitHub (January 2026)
**Authentication**: GitHub Personal Access Token

**Key Capabilities**:
- Repository browsing, code search, commit analysis
- Issue and PR creation, updates, searching
- GitHub Actions workflow monitoring and analysis
- Release management
- Dependabot and security alerts
- Team collaboration features

**Installation in Claude Desktop**:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@github/github-mcp-server"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

**Generate Token**: https://github.com/settings/tokens

## Python and PyPI MCPs

### FastMCP Framework (for building MCPs)

**Version**: 2.14.4 (Jan 22, 2026)
**Status**: Production ready
**Python Support**: 3.10+

**Installation**: `pip install fastmcp`

**Best for**: Building new Python-based MCP servers

```python
from fastmcp.server import Server

server = Server("my-server")

@server.tool()
def my_tool(input: str) -> str:
    """A simple tool."""
    return f"Result: {input}"

if __name__ == "__main__":
    server.run()
```

### Official Python SDK

**Version**: 1.26.0 (Jan 24, 2026)
**Status**: Production recommended
**v2.0**: Coming Q1 2026

**Installation**: `pip install mcp`

### PyPI Query MCP (for dependency management)

**Repository**: https://github.com/loonghao/pypi-query-mcp-server
**Status**: Community maintained, actively used

**Capabilities**:
- Check latest package versions
- Python version compatibility checking
- Dependency analysis
- Security vulnerability identification

**Installation in Claude Desktop**:

```json
{
  "mcpServers": {
    "pypi": {
      "command": "python",
      "args": ["-m", "mcp_pypi"]
    }
  }
}
```

## Documentation MCPs

### MCP Sphinx Docs Server

**Repository**: https://github.com/zk-armor/mcp-sphinx-docs
**Status**: Community maintained

**Purpose**: Convert Sphinx/RST documentation to LLM-optimized Markdown

**Installation in Claude Desktop**:

```json
{
  "mcpServers": {
    "sphinx": {
      "command": "python",
      "args": ["-m", "mcp_sphinx_docs", "--docs-dir", "./docs"]
    }
  }
}
```

## Official Reference Servers (Anthropic)

### Filesystem Server

**Purpose**: Secure file operations in your project
**Installation**: Node.js server from @modelcontextprotocol/server-filesystem

**Configuration**:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": ["/path/to/filesystem-server.js"],
      "env": {
        "ALLOWED_DIRECTORIES": "/path/to/your/project"
      }
    }
  }
}
```

### Git Server

**Purpose**: Analyze git history, branches, diffs
**Installation**: Node.js server from @modelcontextprotocol/server-git

**Configuration**:

```json
{
  "mcpServers": {
    "git": {
      "command": "node",
      "args": ["/path/to/git-server.js", "/path/to/your/project"]
    }
  }
}
```

## CI/CD and Automation

**GitHub Actions**: Integrated via GitHub MCP
**Docker MCP**: Container orchestration
**TestKube MCP**: Testing automation
**CircleCI**: Available via integrations

## Claude Desktop Configuration

**File locations**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Complete configuration example**:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@github/github-mcp-server"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_YOUR_TOKEN"
      }
    },
    "filesystem": {
      "command": "node",
      "args": ["/path/to/filesystem-server.js"],
      "env": {
        "ALLOWED_DIRECTORIES": "/path/to/your/project"
      }
    },
    "git": {
      "command": "node",
      "args": ["/path/to/git-server.js", "/path/to/your/project"]
    },
    "pypi": {
      "command": "python",
      "args": ["-m", "mcp_pypi"]
    }
  }
}
```

**Setup steps**:
1. Generate GitHub token at https://github.com/settings/tokens
2. Open Claude Desktop config file (Settings > Developer > Edit Config)
3. Add MCP servers using examples above
4. Replace placeholders with your values
5. Save and restart Claude Desktop
6. Verify in Claude: click "+" > "Connectors"

## Comparison Matrix

| Feature | GitHub MCP | PyPI MCP | Git Server | Filesystem |
|---------|-----------|----------|-----------|-----------|
| Repo management | ✓ Full | - | ✓ Read | - |
| Issue/PR automation | ✓ Full | - | - | - |
| CI/CD integration | ✓ Full | - | - | - |
| Release management | ✓ Full | - | - | - |
| Dependency checking | - | ✓ Full | - | - |
| Security scanning | ✓ Alerts | ✓ Full | - | - |
| File access | - | - | - | ✓ Full |
| Git history | - | - | ✓ Full | - |
| Code search | ✓ GitHub | - | ✓ Limited | ✓ Full |

## Recommendations

### For GitHub-hosted Python projects:

**Essential** (Day 1):
- GitHub MCP - Repository and release management
- PyPI Query MCP - Dependency management

**Recommended** (Week 1):
- Filesystem server - Project structure access
- Git server - History analysis

**Optional** (As needed):
- Sphinx Docs MCP - If using Sphinx
- Docker MCP - If containerized releases

### Installation Priority

1. **GitHub MCP** (5 min) - Highest value
2. **PyPI MCP** (2 min) - Easy addition
3. **Filesystem + Git** (10 min) - Better context
4. **Sphinx Docs** (5 min) - If needed

### Version Information

- GitHub MCP: Latest (Jan 2026)
- Python SDK: 1.26.0 (v2.0 Q1 2026)
- FastMCP: 2.14.4 (v3.0 in dev)
- PyPI Query: Community maintained
- Node.js requirement: v18+ LTS
- Python requirement: 3.10+

## Security Considerations

**Token Management**:
- Use GitHub token with minimal required scopes
- Claude Desktop auto-encrypts to OS keychain
- Never commit tokens to version control

**Access Control**:
- Restrict Filesystem server to project directory
- Use ALLOWED_DIRECTORIES environment variable

**Recommended Token Scopes**:
- `repo` - Repository access
- `workflow` - GitHub Actions
- `delete_repo` - Release management (optional)

## Troubleshooting

**MCP not connecting**:
1. Check token validity (ghp_... prefix)
2. Verify paths are absolute
3. Check Node.js installed (for filesystem/git)
4. View logs: Settings > Developer > Logs

**Command not found**:
- Verify Node.js: `node --version`
- Verify Python: `python3 --version`
- Install packages: `npm install ...` or `pip install ...`

## Workflow Examples

### Release Workflow
```
User: "Create release v1.2.0 with changelog from last 5 commits"
Claude: Analyzes commits, generates changelog, creates GitHub release
```

### Dependency Update Workflow
```
User: "Check all dependencies for updates and security issues"
Claude: Queries PyPI, identifies updates, flags vulnerabilities
```

### Documentation Workflow
```
User: "Read the docs and help me understand this API"
Claude: Accesses Sphinx docs, explains API, provides examples
```

## Sources and References

- [GitHub MCP Server Repository](https://github.com/github/github-mcp-server)
- [Model Context Protocol Servers](https://github.com/modelcontextprotocol/servers)
- [Official Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Framework](https://pypi.org/project/fastmcp/)
- [PyPI Query MCP](https://github.com/loonghao/pypi-query-mcp-server)
- [Claude Desktop MCP Setup](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [MCP Specification](https://modelcontextprotocol.io/specification/2025-11-25)
