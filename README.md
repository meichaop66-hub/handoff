# Handoff

> Seamlessly hand off work between different AI tools. Start a task in Tool A, say "create handoff", switch to Tool B and say "accept handoff" — no need to repeat the context.

[English](README.md) | [中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![MCP](https://img.shields.io/badge/MCP-supported-purple.svg)](https://modelcontextprotocol.io/)

---

## What is this

Handoff is a **cross-AI work handoff tool**.

It turns "repeating the whole context every time you switch AI tools" into two sentences: say "create handoff" in Tool A, then say "accept handoff" in Tool B.

Each handoff is a standardized work handoff document — what the task is, how far it's gotten, what's left, things to watch out for, where the artifacts are. Both humans and AIs can read and edit it directly.

## What problem it solves

You spend an hour discussing article topics, outlines, and style requirements with an AI in Doubao. Then you want WorkBuddy to write the first draft.

**What you have to do now:**
1. Try to remember "what did we decide again?"
2. Manually organize: title, outline, style, asset locations
3. Copy-paste into WorkBuddy
4. When WorkBuddy finishes, you go back to Doubao and have to explain everything again

**Every time you switch AI tools, you start over.**

**With Handoff:**
- Say "create handoff" in Doubao → automatically generates a standardized handoff document
- Open WorkBuddy, say "accept handoff" → automatically reads the handoff doc and starts working
- When done, say "complete handoff" → records output, auto-archives
- Back in Doubao, say "accept handoff" → automatically reads the completion status and continues

## Quick Start (3 steps)

### 1. Install
```bash
pip install handoff
```

### 2. Create a handoff
```bash
handoff create "Write first draft of WeChat article" \
  --completed "Title, outline, style finalized" \
  --todo "Full draft ~3000 words" \
  --notes "Concise and elegant, avoid AI jargon" \
  --project "WeChat Article"
```

### 3. Switch to another AI tool, accept handoff
```bash
handoff accept    # Reads the most recent pending handoff
# ... do the work ...
handoff complete --output "Draft saved to /path/to/article.md"
```

That's it.

## Core Commands

| Command | Description |
|---------|-------------|
| `handoff create` | Create a handoff document (task, completed, todo, notes) |
| `handoff accept` | Accept a handoff (defaults to most recent pending) |
| `handoff complete` | Complete a handoff (records output, auto-archives) |
| `handoff list` | List all handoffs (filter by status) |
| `handoff get` | Get full content of a single handoff |
| `handoff serve` | Start MCP Server (for AI tools to call) |

## Two Ways to Use

### Option 1: CLI (works even without MCP support)
```bash
# Create a handoff
handoff create "Task description" --completed "Done" --todo "Remaining" --notes "Notes"

# List pending handoffs
handoff list --status active

# Accept a handoff
handoff accept

# Complete a handoff
handoff complete --output "Output info" --notes "Notes"
```

### Option 2: MCP Protocol (recommended — talk to AI naturally)

Add this to your MCP-capable AI tool config (Claude Code, Cursor, Codex, WorkBuddy, etc.):
```json
{
  "mcpServers": {
    "handoff": {
      "command": "handoff",
      "args": ["serve"]
    }
  }
}
```

Then just tell your AI:
- "Create a handoff for this task, pass it to the next AI"
- "Accept handoff, see what's pending"
- "Complete handoff, record the output"

More examples in [examples/README.md](examples/README.md).

## What a Handoff Document Looks Like

Each handoff is a plain Markdown file:

```markdown
---
id: handoff_20260901_180621_13b99f
created_at: 2026-09-01 18:06:21
status: active
project: WeChat Article
tags: writing,publishing
---

# Handoff Document

## Task
Write first draft of first WeChat article

## Completed
Title, outline, style finalized, illustrations ready

## Todo
Full draft (~3000 words)

## Notes
- Style: concise and elegant, Chai Jing-style narrative
- Avoid: AI buzzwords like "empower", "closed loop", "lever"

## Related Files
- Article outline: https://feishu.doubao.com/docx/xxx
```

## Data Storage

All handoff documents live in `~/.handoff/`:
```
~/.handoff/
├── active/      # Pending / in-progress handoffs
├── archive/     # Completed handoffs (archived)
└── .git/        # Auto version control
```

- Plain Markdown files — both humans and AIs can read and edit directly
- Git auto version control — rollback and sync to remote repos
- Zero database, zero cloud services — your data stays on your machine

## Design Principles

1. **Plain text storage** — not locked into any tool, your data is always yours
2. **Local-first** — no cloud, privacy-first
3. **Core logic independent** — future web/mobile apps reuse the same core
4. **Git-native** — tools developers already know, no new learning curve
5. **Zero config** — works immediately after install, no server setup

## Tech Stack

- Python 3.9+
- MCP (Model Context Protocol)
- Plain Markdown file storage
- Git auto version control
- Zero database, zero cloud services

## Project Structure

```
handoff/
├── handoff/
│   ├── __init__.py
│   ├── core.py          # Core logic (HandoffManager)
│   ├── cli.py           # Command-line interface
│   ├── mcp_server.py    # MCP Server
│   ├── templates.py     # Document templates
│   └── git_utils.py     # Git utility wrapper
├── tests/
│   └── test_full.py     # Full feature tests (20 cases)
├── examples/
│   └── README.md        # Usage examples
├── pyproject.toml
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Roadmap

### v0.1.0 (current, MVP)
- [x] Core: create / accept / list / complete / get
- [x] CLI
- [x] MCP Server
- [x] Git auto version control
- [x] Full test suite (20 cases)

### v0.2.0 (planned)
- [ ] Auto context scanning (Git status, recent files)
- [ ] AI-assisted handoff content generation
- [ ] Custom handoff templates
- [ ] Better error messages

### Future
- [ ] Web UI / visual dashboard
- [ ] Cloud sync / multi-device
- [ ] Desktop app
- [ ] Mobile app / mini-program
- [ ] Team collaboration features

## Contributing

Contributions welcome! Read [CONTRIBUTING.md](CONTRIBUTING.md) to get started.
- Bug reports: open an Issue
- Feature suggestions: open an Issue to discuss
- Code contributions: submit a PR

## License

[MIT](LICENSE)
