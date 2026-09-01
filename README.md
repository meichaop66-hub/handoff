# Handoff 接棒工具

> 让不同 AI 工具之间无缝交接工作。你在 A 工具里干到一半，说一句"创建接棒"，换 B 工具说"接棒"就能继续，不用重新讲一遍背景。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![MCP](https://img.shields.io/badge/MCP-supported-purple.svg)](https://modelcontextprotocol.io/)

---

## 这是什么

Handoff 是一个**跨 AI 工具的工作交接工具**。

它不是 AI 的记忆工具（ai-memory 已经做了），而是**项目的工作交接单**：

- **ai-memory** = AI 的笔记本（被动记录所有会话，同一个 AI 用）
- **Handoff** = 项目的交接单（人主动创建，不同 AI 之间传递任务状态）

## 解决什么问题

你在豆包里跟 AI 讨论了半天文章选题、大纲、风格要求。然后想让 WorkBuddy 去写初稿。

**现在你要做的：**
1. 自己回忆"我们刚才定了什么来着？"
2. 手动整理：标题、大纲、风格、素材位置
3. 复制粘贴到 WorkBuddy
4. WorkBuddy 写完，你再回豆包，又要重新说一遍

**每次切换 AI 工具，都要重新讲一遍。**

**用了 Handoff 之后：**
- 在豆包里说"创建接棒" → 自动生成标准化交接单
- 打开 WorkBuddy 说"接棒" → 自动读取交接单，直接开始
- 写完说"完成接棒" → 记录产出，自动归档
- 回豆包说"接棒" → 自动读到完成状态，继续改

## 快速开始（3步）

### 1. 安装

```bash
pip install handoff
```

### 2. 创建接棒

```bash
handoff create "写公众号文章初稿" \
  --completed "标题、大纲、风格已定" \
  --todo "全文初稿3000字" \
  --notes "简洁优雅，避免AI黑话" \
  --project "公众号文章"
```

### 3. 换个 AI 工具，接棒

```bash
handoff accept    # 读取最近的待接棒任务
# ...干活...
handoff complete --output "初稿已存到 /path/to/article.md"
```

就这么简单。

## 核心功能

| 命令 | 说明 |
|------|------|
| `handoff create` | 创建接棒文档（任务、已完成、未完成、注意事项） |
| `handoff accept` | 接受接棒（不指定 ID 取最近的待接棒） |
| `handoff complete` | 完成接棒（记录产出，自动归档） |
| `handoff list` | 查看所有接棒记录（支持按状态筛选） |
| `handoff get` | 获取单个接棒的完整内容 |
| `handoff serve` | 启动 MCP Server（供 AI 工具调用） |

## 两种使用方式

### 方式一：命令行（不支持 MCP 的客户端也能用）

```bash
# 创建接棒
handoff create "任务描述" --completed "已完成" --todo "未完成" --notes "注意事项"

# 查看待接棒
handoff list --status active

# 接受接棒
handoff accept

# 完成接棒
handoff complete --output "产出信息" --notes "备注"
```

### 方式二：MCP 协议（推荐，直接跟 AI 说人话）

在支持 MCP 的 AI 工具（Claude Code、Cursor、Codex、WorkBuddy 等）配置中添加：

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

然后直接跟 AI 说：
- "帮我创建接棒，这个任务交给下一个 AI"
- "接棒，看看有什么待办"
- "完成接棒，记录一下产出"

更多示例见 [examples/README.md](examples/README.md)。

## 接棒文档长什么样

每个接棒是一个纯 Markdown 文件：

```markdown
---
id: handoff_20260901_180621_13b99f
created_at: 2026-09-01 18:06:21
status: active
project: 公众号文章
tags: 写作,发布
---

# 接棒文档

## 任务
写公众号第一篇文章初稿

## 已完成
标题、大纲、风格已定，配图已做好

## 未完成
全文初稿（约3000字）

## 注意事项
- 风格：简洁优雅，柴静式叙事
- 避免：赋能、闭环、抓手等AI黑话

## 相关文件
- 文章大纲：https://feishu.doubao.com/docx/xxx
```

## 数据存储

所有接棒文档存在 `~/.handoff/` 目录：

```
~/.handoff/
├── active/      # 待接手/进行中的接棒
├── archive/     # 已完成的接棒（归档）
└── .git/        # 自动版本管理
```

- 纯 Markdown 文件，人和 AI 都能直接读、直接改
- Git 自动版本管理，能回溯、能同步到远程仓库
- 零数据库、零云端服务，数据不出你的电脑

## 和 ai-memory 的区别

| | ai-memory | Handoff |
|---|---|---|
| 定位 | AI 的记忆工具 | 项目的交接单 |
| 触发方式 | 被动记录所有会话 | 人主动说"创建接棒"才创建 |
| 内容 | 原始对话 + 自动摘要 | 结构化的任务状态 + 未完成项 + 注意事项 |
| 解决的问题 | "AI 忘了上次说什么" | "换个 AI 工具，不用重新讲一遍" |
| 使用对象 | 同一个 AI 持续使用 | 不同 AI 之间传递 |

**简单说：ai-memory 是 AI 的笔记本，Handoff 是项目的工作交接单。**

## 设计理念

1. **纯文本存储** —— 不被工具绑架，数据永远是你的
2. **本地优先** —— 不上云，隐私安全
3. **核心逻辑独立** —— 以后加网页版、手机 APP，核心不用改
4. **Git 原生** —— 开发者熟悉的工具，不用学新东西
5. **零配置** —— 装完就能用，不用搭服务

## 技术栈

- Python 3.9+
- MCP（Model Context Protocol）
- 纯 Markdown 文件存储
- Git 自动版本管理
- 零数据库、零云端服务

## 项目结构

```
handoff/
├── handoff/
│   ├── __init__.py
│   ├── core.py          # 核心逻辑（HandoffManager）
│   ├── cli.py           # 命令行接口
│   ├── mcp_server.py    # MCP Server
│   ├── templates.py     # 文档模板
│   └── git_utils.py     # Git 工具封装
├── tests/
│   └── test_full.py     # 完整功能测试（20个用例）
├── examples/
│   └── README.md        # 使用示例
├── pyproject.toml
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## 路线图

### v0.1.0（当前，MVP）
- [x] 核心功能：create / accept / list / complete / get
- [x] CLI 命令行
- [x] MCP Server
- [x] Git 自动版本管理
- [x] 完整测试（20个用例）

### v0.2.0（规划中）
- [ ] 自动扫描上下文（Git 状态、最近文件）
- [ ] AI 辅助生成接棒内容
- [ ] 接棒模板自定义
- [ ] 更好的错误提示

### 未来
- [ ] Web 界面 / 可视化看板
- [ ] 云端同步 / 多设备
- [ ] 桌面 APP
- [ ] 手机 APP / 小程序
- [ ] 团队协作功能

## 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何开始。

- 报告 Bug：开 Issue
- 新功能建议：开 Issue 讨论
- 代码贡献：提交 PR

## License

[MIT](LICENSE)
