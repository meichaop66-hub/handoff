# Contributing Guide

Thanks for your interest in Handoff! Contributions of all kinds are welcome.

## Quick Start

1. Fork this repository
2. Clone your fork: `git clone https://github.com/yourname/handoff.git`
3. Create a branch: `git checkout -b feature/your-feature`
4. Install dev dependencies: `pip install -e ".[dev]"`
5. Run tests: `python3 tests/test_full.py`
6. Commit changes: `git commit -m "feat: add your feature"`
7. Push: `git push origin feature/your-feature`
8. Submit a Pull Request

## Types of Contributions

### Bug Reports

Please include in your Issue:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment info (OS, Python version, handoff version)

### Feature Suggestions

Please explain in your Issue:
- What problem this feature solves
- Why this feature is needed
- Rough implementation ideas

### Code Contributions

- Keep code style consistent (PEP 8)
- Add tests
- Update documentation
- Use Conventional Commits format: `feat:`, `fix:`, `docs:`, `refactor:`

## Development Environment

```bash
# Install
pip install -e ".[dev]"

# Run tests
python3 tests/test_full.py

# Run CLI locally
python3 -m handoff.cli --help

# Run MCP Server locally
python3 -m handoff.cli serve
```

## Project Structure

```
handoff/
├── handoff/          # Core code
│   ├── core.py       # Core logic
│   ├── cli.py        # CLI interface
│   ├── mcp_server.py # MCP Server
│   ├── templates.py  # Document templates
│   └── git_utils.py  # Git utilities
├── tests/            # Tests
├── examples/         # Usage examples
└── README.md
```

## Code of Conduct

Please be kind and respectful. We welcome contributors from all backgrounds.

## Questions?

Feel free to open an Issue to discuss, or just submit a PR.
