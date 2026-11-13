"""
MCP Server - 让支持MCP的AI工具可以调用接棒功能

兼容 mcp 1.x 与 2.x：
- 1.x 的高层入口是 mcp.server.fastmcp.FastMCP
- 2.x 把 FastMCP 改名为 mcp.server.mcpserver.MCPServer

两版的 `tool` 装饰器与 `run_stdio_async` 接口一致，因此只在导入处做一次运行时探测，
其余代码两版共用，避免把版本判断散落在业务逻辑里。
"""

import json
from typing import Any, Literal, Optional

from .core import HandoffManager

try:
    # mcp >= 2：FastMCP 已更名为 MCPServer
    from mcp.server.mcpserver import MCPServer as _ServerClass
except ImportError:
    try:
        # mcp 1.x
        from mcp.server.fastmcp import FastMCP as _ServerClass
    except ImportError:
        _ServerClass = None

MCP_AVAILABLE = _ServerClass is not None


def _dumps(payload: Any) -> str:
    """统一 JSON 序列化，保证不同 mcp 版本下客户端看到的文本一致。"""
    return json.dumps(payload, ensure_ascii=False, indent=2)


def create_mcp_server():
    """创建MCP Server"""
    if not MCP_AVAILABLE:
        raise ImportError(
            "MCP SDK未安装，请运行: pip install mcp"
        )

    server = _ServerClass("handoff")
    manager = HandoffManager()

    @server.tool(
        name="handoff_create",
        description="创建接棒文档。当你需要把任务交接给另一个AI工具时调用。需要提供任务描述、已完成内容、未完成内容、注意事项等。",
    )
    def handoff_create(
        task: str,
        completed: str = "",
        todo: str = "",
        notes: str = "",
        files: str = "",
        project: str = "",
        tags: str = "",
    ) -> str:
        """创建接棒文档。task 必填，其余可选。"""
        result = manager.create(
            task=task,
            completed=completed,
            todo=todo,
            notes=notes,
            files=files,
            project=project,
            tags=tags,
            created_by="mcp-client",
        )
        return _dumps(result)

    @server.tool(
        name="handoff_accept",
        description="接受接棒。当你开始一个新任务，需要读取之前的接棒文档时调用。不指定ID则读取最近的待接棒任务。",
    )
    def handoff_accept(handoff_id: Optional[str] = None) -> str:
        """接受接棒。handoff_id 不填则取最近的待接棒任务。"""
        result = manager.accept(handoff_id=handoff_id)
        return _dumps(result)

    @server.tool(
        name="handoff_list",
        description="列出所有接棒记录。可以按状态筛选（active/accepted/completed）。",
    )
    def handoff_list(
        status: Optional[Literal["active", "accepted", "completed"]] = None,
    ) -> str:
        """列出接棒记录。status 不填则列出全部。"""
        result = manager.list(status=status)
        return _dumps(result)

    @server.tool(
        name="handoff_complete",
        description="完成接棒。当你完成了一个接棒任务时调用，记录产出和备注。",
    )
    def handoff_complete(
        handoff_id: Optional[str] = None,
        output: str = "",
        notes: str = "",
    ) -> str:
        """完成接棒。handoff_id 不填则取最近的进行中任务。"""
        result = manager.complete(
            handoff_id=handoff_id,
            output=output,
            notes=notes,
        )
        return _dumps(result)

    @server.tool(
        name="handoff_get",
        description="获取单个接棒的完整内容。",
    )
    def handoff_get(handoff_id: str) -> str:
        """获取单个接棒的完整内容。handoff_id 必填。"""
        result = manager.get(handoff_id=handoff_id)
        return _dumps(result)

    return server


def run_mcp_server():
    """运行MCP Server（stdio模式）"""
    if not MCP_AVAILABLE:
        print("错误: MCP SDK未安装，请运行: pip install mcp")
        return

    server = create_mcp_server()

    import asyncio

    async def main():
        await server.run_stdio_async()

    asyncio.run(main())


if __name__ == "__main__":
    run_mcp_server()
