"""
MCP Server - 让支持MCP的AI工具可以调用接棒功能
"""

import json
from typing import Optional

from .core import HandoffManager

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


def create_mcp_server():
    """创建MCP Server"""
    if not MCP_AVAILABLE:
        raise ImportError(
            "MCP SDK未安装，请运行: pip install mcp"
        )

    server = Server("handoff")
    manager = HandoffManager()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="handoff_create",
                description="创建接棒文档。当你需要把任务交接给另一个AI工具时调用。需要提供任务描述、已完成内容、未完成内容、注意事项等。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "任务描述，需要做什么",
                        },
                        "completed": {
                            "type": "string",
                            "description": "已完成的内容",
                        },
                        "todo": {
                            "type": "string",
                            "description": "未完成的内容，下一步要做什么",
                        },
                        "notes": {
                            "type": "string",
                            "description": "注意事项、偏好、风格要求等",
                        },
                        "files": {
                            "type": "string",
                            "description": "相关文件路径",
                        },
                        "project": {
                            "type": "string",
                            "description": "项目名称",
                        },
                        "tags": {
                            "type": "string",
                            "description": "标签，用逗号分隔",
                        },
                    },
                    "required": ["task"],
                },
            ),
            Tool(
                name="handoff_accept",
                description="接受接棒。当你开始一个新任务，需要读取之前的接棒文档时调用。不指定ID则读取最近的待接棒任务。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "handoff_id": {
                            "type": "string",
                            "description": "接棒ID，不填则取最近的",
                        },
                    },
                },
            ),
            Tool(
                name="handoff_list",
                description="列出所有接棒记录。可以按状态筛选（active/accepted/completed）。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "筛选状态: active/accepted/completed，不填则列出全部",
                            "enum": ["active", "accepted", "completed"],
                        },
                    },
                },
            ),
            Tool(
                name="handoff_complete",
                description="完成接棒。当你完成了一个接棒任务时调用，记录产出和备注。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "handoff_id": {
                            "type": "string",
                            "description": "接棒ID，不填则取最近的进行中任务",
                        },
                        "output": {
                            "type": "string",
                            "description": "产出内容，完成了什么、存在哪",
                        },
                        "notes": {
                            "type": "string",
                            "description": "备注，还有什么待验收",
                        },
                    },
                },
            ),
            Tool(
                name="handoff_get",
                description="获取单个接棒的完整内容。",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "handoff_id": {
                            "type": "string",
                            "description": "接棒ID",
                        },
                    },
                    "required": ["handoff_id"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "handoff_create":
            result = manager.create(
                task=arguments.get("task", ""),
                completed=arguments.get("completed", ""),
                todo=arguments.get("todo", ""),
                notes=arguments.get("notes", ""),
                files=arguments.get("files", ""),
                project=arguments.get("project", ""),
                tags=arguments.get("tags", ""),
                created_by=arguments.get("created_by", "mcp-client"),
            )
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        elif name == "handoff_accept":
            result = manager.accept(
                handoff_id=arguments.get("handoff_id")
            )
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        elif name == "handoff_list":
            result = manager.list(
                status=arguments.get("status")
            )
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        elif name == "handoff_complete":
            result = manager.complete(
                handoff_id=arguments.get("handoff_id"),
                output=arguments.get("output", ""),
                notes=arguments.get("notes", ""),
            )
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        elif name == "handoff_get":
            result = manager.get(
                handoff_id=arguments.get("handoff_id", "")
            )
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]

    return server


def run_mcp_server():
    """运行MCP Server（stdio模式）"""
    if not MCP_AVAILABLE:
        print("错误: MCP SDK未安装，请运行: pip install mcp")
        return

    from mcp.server.stdio import stdio_server

    server = create_mcp_server()

    import asyncio
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(main())


if __name__ == "__main__":
    run_mcp_server()
