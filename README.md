# Handoff 接棒工具

> 让不同AI工具之间无缝交接工作。你在A工具里干到一半，说一句"接棒"，换B工具打开就能继续，不用重新讲一遍背景。

## 这是什么

Handoff是一个**跨AI工具的工作交接工具**。它不是AI的记忆工具（ai-memory已经做了），而是**项目的工作交接单**。

- ai-memory = AI的笔记本（被动记录所有会话）
- Handoff = 项目的交接单（人主动创建，结构化传递任务状态）

## 解决什么问题

你在豆包里跟AI讨论了半天文章选题、大纲、风格要求。然后想让WorkBuddy去写初稿。

**现在你要做的**：
1. 自己回忆"我们刚才定了什么来着？"
2. 手动整理：标题、大纲、风格、素材位置
3. 复制粘贴到WorkBuddy
4. WorkBuddy写完，你再回豆包，又要重新说一遍

**用了Handoff之后**：
- 在豆包里说"创建接棒" → 自动生成交接单
- 打开WorkBuddy说"接棒" → 自动读取交接单，直接开始
- 写完说"完成接棒" → 记录产出，自动归档
- 回豆包说"接棒" → 自动读到完成状态，继续改

## 核心功能

| 命令 | 说明 |
|------|------|
| `handoff create` | 创建接棒文档 |
| `handoff accept` | 接受接棒（读取最近的待接棒任务） |
| `handoff list` | 查看所有接棒记录 |
| `handoff complete` | 完成接棒（记录产出，归档） |
| `handoff get` | 获取单个接棒的完整内容 |
| `handoff serve` | 启动MCP Server（供AI工具调用） |

## 安装

```bash
pip install handoff
```

或者从源码安装：

```bash
git clone https://github.com/meichaop66-hub/handoff.git
cd handoff
pip install -e .
```

## 使用方式

### 方式一：命令行

```bash
# 创建接棒
handoff create "写公众号文章初稿" \
  --completed "标题、大纲、风格已定" \
  --todo "全文初稿3000字" \
  --notes "简洁优雅，柴静式叙事，避免AI黑话" \
  --project "公众号文章"

# 查看待接棒任务
handoff list --status active

# 接受接棒（不指定ID取最近的）
handoff accept

# 完成接棒
handoff complete --output "初稿已存到 /path/to/article.md" --notes "第三节待验收"

# 查看所有记录
handoff list
```

### 方式二：MCP协议（推荐）

在支持MCP的AI工具（Claude Code、Cursor、Codex等）配置中添加：

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

然后你就可以直接跟AI说：
- "帮我创建接棒，这个任务交给下一个AI"
- "接棒，看看有什么待办"
- "完成接棒，记录一下产出"

## 数据存储

所有接棒文档存在 `~/.handoff/` 目录下：

```
~/.handoff/
├── active/      # 待接棒/进行中的任务
├── archive/     # 已完成的接棒（归档）
└── .git/        # 自动版本管理
```

每个接棒是一个纯Markdown文件，人能直接读、直接改。用git自动版本管理，能回溯、能同步到远程仓库。

## 接棒文档长什么样

```markdown
---
id: handoff_20260902_223000
created_at: 2026-09-02 22:30:00
status: active
project: 公众号文章
tags: 写作, AI协作
---

# 接棒文档

## 任务
写《我和AI共事30天》公众号文章初稿

## 已完成
标题、大纲、核心案例、风格要求

## 未完成
全文初稿（约3000字）

## 注意事项
- 风格：简洁优雅，柴静式叙事，不大白话
- 避免：赋能、闭环、抓手等AI黑话
- 素材位置：gitee仓库/文章线/素材/
- 写完存到：gitee仓库/文章线/草稿/

## 相关文件
- 大纲：/path/to/outline.md
- 素材：/path/to/notes.md
```

## 和ai-memory的区别

| | ai-memory | Handoff |
|---|---|---|
| 定位 | AI的记忆工具 | 项目的交接单 |
| 触发方式 | 被动记录所有会话 | 人主动说"接棒"才创建 |
| 内容 | 原始对话+自动摘要 | 结构化的任务状态+未完成项+注意事项 |
| 解决的问题 | "AI忘了上次说什么" | "换个AI工具，不用重新讲一遍" |

## 技术栈

- Python 3.9+
- MCP（Model Context Protocol）
- 纯Markdown文件存储
- git自动版本管理
- 零数据库、零云端服务，本地运行

## 开发状态

当前版本：v0.1.0（MVP）

- [x] 核心功能：create/accept/list/complete/get
- [x] CLI命令行
- [x] MCP Server
- [x] git自动版本管理
- [ ] 自动扫描上下文（git状态、最近文件）
- [ ] AI辅助生成接棒内容
- [ ] 接棒模板自定义
- [ ] Web界面

## License

MIT
