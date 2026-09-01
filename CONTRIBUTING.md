# 贡献指南

感谢你对 Handoff 的兴趣！欢迎任何形式的贡献。

## 快速开始

1. Fork 这个仓库
2. 克隆你的 fork：`git clone https://github.com/yourname/handoff.git`
3. 创建分支：`git checkout -b feature/your-feature`
4. 安装开发依赖：`pip install -e ".[dev]"`
5. 运行测试：`python3 tests/test_full.py`
6. 提交改动：`git commit -m "feat: add your feature"`
7. 推送：`git push origin feature/your-feature`
8. 提交 Pull Request

## 贡献类型

### 报告 Bug

请在 Issue 中包含：
- 复现步骤
- 期望行为
- 实际行为
- 环境信息（OS、Python版本、handoff版本）

### 新功能建议

请在 Issue 中说明：
- 这个功能解决什么问题
- 为什么需要这个功能
- 大概的实现思路

### 代码贡献

- 保持代码风格一致（PEP 8）
- 添加测试
- 更新文档
- 提交信息使用 Conventional Commits 格式：`feat:`、`fix:`、`docs:`、`refactor:`

## 开发环境

```bash
# 安装
pip install -e ".[dev]"

# 运行测试
python3 tests/test_full.py

# 本地运行 CLI
python3 -m handoff.cli --help

# 本地运行 MCP Server
python3 -m handoff.cli serve
```

## 项目结构

```
handoff/
├── handoff/          # 核心代码
│   ├── core.py       # 核心逻辑
│   ├── cli.py        # 命令行接口
│   ├── mcp_server.py # MCP Server
│   ├── templates.py  # 文档模板
│   └── git_utils.py  # Git 工具
├── tests/            # 测试
├── examples/         # 使用示例
└── README.md
```

## 行为准则

请保持友善和尊重。我们欢迎所有背景的贡献者。

## 有问题？

欢迎开 Issue 讨论，或者直接提交 PR。
