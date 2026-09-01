# Usage Examples

## Example 1: Writing an article across AI tools

### Create a handoff in Doubao
```bash
handoff create "Write first draft of first WeChat article" \
  --completed "Title, outline, style finalized, 6 illustrations ready" \
  --todo "Full draft 3000 words, follow the outline" \
  --notes "Concise and elegant, Chai Jing-style narrative, avoid AI jargon; use Greek sculpture style illustrations" \
  --files "Article outline: https://feishu.doubao.com/docx/xxx" \
  --project "WeChat Article" \
  --tags "writing,publishing"
```

### Accept and complete in WorkBuddy
```bash
# Accept handoff
handoff accept

# Complete after finishing
handoff complete \
  --output "Draft finished, saved at https://feishu.doubao.com/docx/yyy" \
  --notes "Section 3 case study needs补充, suggest user provide real data"
```

### Go back to Doubao to continue
```bash
handoff accept
# Automatically reads what WorkBuddy completed, starts editing directly
```

---

## Example 2: Coding across multiple devices

### Create a handoff on work computer
```bash
handoff create "Implement user login feature" \
  --completed "Database schema designed, API endpoints defined" \
  --todo "Write login endpoint, JWT token generation, frontend login page" \
  --notes "Use FastAPI, encrypt passwords with bcrypt" \
  --files "Code repo: https://github.com/xxx/project" \
  --project "User System" \
  --tags "backend,login"
```

### Sync to home computer
```bash
# Sync ~/.handoff directory to Git or cloud drive
cd ~/.handoff
git add -A && git commit -m "handoff update" && git push
```

### Continue on home computer
```bash
cd ~/.handoff && git pull
handoff accept
# Start coding
```

---

## Example 3: MCP Configuration

### Claude Code
Add to `~/.claude.json`:
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

Then just tell Claude:
- "Create a handoff for me, pass this feature to the next AI"
- "Accept handoff, see what's pending"
- "Complete handoff, record the output"

### Cursor
Add the same config in Cursor Settings → MCP.
