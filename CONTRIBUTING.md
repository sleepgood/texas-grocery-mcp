# Contributing to Texas Grocery MCP

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/texas-grocery-mcp
   cd texas-grocery-mcp
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   playwright install chromium
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/texas_grocery_mcp --cov-report=html
```

### Code Quality

Before submitting a PR, ensure your code passes all checks:

```bash
# Linting
ruff check src/ tests/

# Type checking
mypy src/

# Format check (ruff will auto-fix)
ruff check src/ tests/ --fix
```

### Project Structure

```
src/texas_grocery_mcp/
├── auth/           # Session and authentication management
├── clients/        # GraphQL and HTTP clients
├── models/         # Pydantic data models
├── reliability/    # Caching, throttling, retry logic
├── services/       # Business logic services
├── tools/          # MCP tool implementations
└── server.py       # Main MCP server entry point
```

## Submitting Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a Pull Request against `main`

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

## Testing Guidelines

- Write tests for all new functionality
- Maintain or improve code coverage
- Use `pytest` fixtures and `respx` for mocking HTTP requests
- Unit tests go in `tests/unit/`
- Integration tests (requiring real API calls) go in `tests/integration/`

## Code Style

- Follow PEP 8 (enforced by ruff)
- Use type hints for all function signatures
- Keep functions focused and small
- Document complex logic with comments
- Use meaningful variable and function names

## Reporting Issues

When reporting bugs, please include:

1. Python version
2. Operating system
3. Steps to reproduce
4. Expected vs actual behavior
5. Relevant error messages or logs

## Questions?

Feel free to open an issue for questions or discussions about the project.
