# MCP Quick Reference: Python Open Source Release

Fast lookup for setting up MCPs with Claude Desktop.

## 30-Second Setup

### Prerequisites
```bash
# Check you have these
node --version        # Should be v18+
python3 --version     # Should be 3.10+
```

### Three Steps

**1. Create GitHub Token** (2 min)
- Go to: https://github.com/settings/tokens
- Create token with scopes: repo, workflow, delete_repo
- Copy token (looks like: ghp_xxxxxxxxxxxx)

**2. Edit Claude Config** (1 min)
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**3. Add Configuration** (1 min)
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@github/github-mcp-server"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_YOUR_TOKEN_HERE"
      }
    },
    "pypi": {
      "command": "python",
      "args": ["-m", "mcp_pypi"]
    }
  }
}
```

Replace `ghp_YOUR_TOKEN_HERE` with your actual token.

**4. Restart Claude** (1 min)
- Close Claude Desktop
- Reopen Claude Desktop
- Click "+" > "Connectors" to verify

## Installation Commands

### Minimal Setup
```bash
# Just GitHub MCP (no additional packages needed, uses npx)
# Just PyPI MCP
pip install mcp-pypi
```

### Full Setup
```bash
# Python packages
pip install mcp-pypi

# Node.js servers (if using filesystem/git)
npm install @modelcontextprotocol/server-filesystem
npm install @modelcontextprotocol/server-git

# For documentation
pip install mcp-sphinx-docs
```

## Configuration Templates

### Template 1: Minimal (GitHub Only)
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@github/github-mcp-server"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_YOUR_TOKEN"
      }
    }
  }
}
```

### Template 2: Recommended (GitHub + Dependencies)
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
    "pypi": {
      "command": "python",
      "args": ["-m", "mcp_pypi"]
    }
  }
}
```

### Template 3: Complete (All Tools)
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
        "ALLOWED_DIRECTORIES": "/Users/yourname/path/to/project"
      }
    },
    "git": {
      "command": "node",
      "args": ["/path/to/git-server.js", "/Users/yourname/path/to/project"]
    },
    "pypi": {
      "command": "python",
      "args": ["-m", "mcp_pypi"]
    }
  }
}
```

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection Failed" (GitHub) | Check token: starts with `ghp_`, not expired, has `repo` scope |
| "Connection Failed" (PyPI) | Run: `pip install mcp-pypi` |
| "Command not found" (node) | Install Node.js: https://nodejs.org (LTS version) |
| "Command not found" (python) | Use `python3` instead, or verify version |
| MCP loads but no tools | Check Settings > Developer > Logs for errors |

## Verification

After restart, in Claude Desktop:
1. Click "+" button at bottom of chat
2. Select "Connectors"
3. Should see your MCPs listed
4. Check for green "Connected" status

## GitHub Token Scopes

Required:
- ✓ repo - Repository access
- ✓ workflow - GitHub Actions

Optional:
- ✓ delete_repo - For release management

## MCPs Quick Reference

| MCP | Command | Purpose |
|-----|---------|---------|
| GitHub | `npx @github/github-mcp-server` | Repos, PRs, issues, releases |
| PyPI | `python -m mcp_pypi` | Package versions, security |
| Filesystem | `node filesystem-server.js` | Read/write files |
| Git | `node git-server.js /repo/path` | Repository history |
| Sphinx | `python -m mcp_sphinx_docs` | Documentation queries |

## Common Workflows

### Check Dependencies
```
Claude: "Check requirements.txt for security issues"
→ PyPI MCP finds vulnerabilities
```

### Manage Issues
```
Claude: "Create an issue for the bug on line 42 of server.py"
→ GitHub MCP creates issue with context
```

### Release Management
```
Claude: "Create release v1.2.0 with changelog"
→ GitHub MCP analyzes commits, creates release
```

### Documentation Help
```
Claude: "Read the README and help me understand setup"
→ Filesystem MCP reads file, Claude explains
```

## Version Information (Jan 2026)

- GitHub MCP: Latest (actively maintained)
- Python SDK: 1.26.0 (v2.0 coming Q1 2026)
- FastMCP: 2.14.4 (framework for building MCPs)
- PyPI Query: Community maintained, actively used
- Node.js: v18+ LTS recommended
- Python: 3.10+ required

## File Paths Reference

### Config File Locations
| OS | Path |
|----|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

### Server Executable Paths

If installed with npm:
```
/path/to/node_modules/@modelcontextprotocol/server-filesystem/dist/index.js
/path/to/node_modules/@modelcontextprotocol/server-git/dist/index.js
```

## Environment Variables

### Security
Use Claude Desktop's secure storage for tokens:
- Mark fields as `"sensitive": true` in manifest
- OS keychain auto-encrypts (macOS: Keychain, Windows: Credential Manager)

### Filesystem Restrictions
```json
"env": {
  "ALLOWED_DIRECTORIES": "/absolute/path/to/project"
}
```

## Documentation

- Full guide: `/docs/research/technical/mcp-servers-python-release-research.md`
- GitHub MCP docs: https://github.com/github/github-mcp-server
- MCP docs: https://modelcontextprotocol.io/
- GitHub token page: https://github.com/settings/tokens

## Debug Commands

```bash
# Test GitHub token
curl -H "Authorization: token ghp_YOUR_TOKEN" https://api.github.com/user

# Verify Node.js
which node
node --version

# Verify Python
which python3
python3 --version

# Test MCP PyPI
python3 -m mcp_pypi --help
```

## Keys Reminders

- Always use ABSOLUTE paths in config (not ~/project)
- Restart Claude after editing config
- Tokens start with `ghp_` prefix
- Never commit tokens to version control
- Check "Connectors" to verify MCPs loaded
- Sensitive fields auto-encrypt in Claude Desktop
