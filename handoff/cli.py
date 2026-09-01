"""
CLI命令行 - 不支持MCP的客户端也能通过命令行使用
"""

import argparse
import json
import sys

from .core import HandoffManager


def cmd_create(args):
    """创建接棒"""
    manager = HandoffManager()
    result = manager.create(
        task=args.task,
        completed=args.completed or "",
        todo=args.todo or "",
        notes=args.notes or "",
        files=args.files or "",
        project=args.project or "",
        tags=args.tags or "",
        created_by="cli",
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"✅ 接棒已创建: {result['id']}")
        print(f"📁 路径: {result['path']}")
        print("\n--- 接棒内容 ---")
        print(result["content"])


def cmd_accept(args):
    """接受接棒"""
    manager = HandoffManager()
    result = manager.accept(handoff_id=args.id)

    if "error" in result:
        print(f"❌ 错误: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"📋 接棒内容 ({result['id']}):")
        print("---")
        print(result["content"])


def cmd_list(args):
    """列出接棒"""
    manager = HandoffManager()
    result = manager.list(status=args.status)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if not result:
            print("暂无接棒记录")
            return

        print(f"共 {len(result)} 条接棒记录:\n")
        for i, item in enumerate(result, 1):
            status_icon = {
                "active": "⏳",
                "accepted": "🔄",
                "completed": "✅",
            }.get(item["status"], "❓")

            print(f"{i}. {status_icon} [{item['status']}] {item['id']}")
            print(f"   项目: {item['project'] or '未分类'}")
            print(f"   时间: {item['created_at']}")
            print(f"   任务: {item['task_summary']}")
            print()


def cmd_complete(args):
    """完成接棒"""
    manager = HandoffManager()
    result = manager.complete(
        handoff_id=args.id,
        output=args.output or "",
        notes=args.notes or "",
    )

    if "error" in result:
        print(f"❌ 错误: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"✅ 接棒已完成: {result['id']}")
        print(f"📁 已归档到: {result['path']}")


def cmd_get(args):
    """获取接棒详情"""
    manager = HandoffManager()
    result = manager.get(handoff_id=args.id)

    if "error" in result:
        print(f"❌ 错误: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"📋 接棒详情 ({result['id']}):")
        print(f"状态: {result['status']}")
        print("---")
        print(result["content"])


def cmd_serve(args):
    """启动MCP Server"""
    from .mcp_server import run_mcp_server
    run_mcp_server()


def main():
    parser = argparse.ArgumentParser(
        prog="handoff",
        description="Handoff - 让不同AI工具之间无缝交接工作",
    )
    parser.add_argument("--json", action="store_true", help="以JSON格式输出")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # create
    create_parser = subparsers.add_parser("create", help="创建接棒")
    create_parser.add_argument("task", help="任务描述")
    create_parser.add_argument("--completed", "-c", help="已完成内容")
    create_parser.add_argument("--todo", "-t", help="未完成内容")
    create_parser.add_argument("--notes", "-n", help="注意事项")
    create_parser.add_argument("--files", "-f", help="相关文件")
    create_parser.add_argument("--project", "-p", help="项目名称")
    create_parser.add_argument("--tags", help="标签")

    # accept
    accept_parser = subparsers.add_parser("accept", help="接受接棒")
    accept_parser.add_argument("id", nargs="?", help="接棒ID（不填取最近的）")

    # list
    list_parser = subparsers.add_parser("list", help="列出接棒")
    list_parser.add_argument(
        "--status", "-s",
        choices=["active", "accepted", "completed"],
        help="按状态筛选",
    )

    # complete
    complete_parser = subparsers.add_parser("complete", help="完成接棒")
    complete_parser.add_argument("id", nargs="?", help="接棒ID（不填取最近的）")
    complete_parser.add_argument("--output", "-o", help="产出内容")
    complete_parser.add_argument("--notes", "-n", help="备注")

    # get
    get_parser = subparsers.add_parser("get", help="获取接棒详情")
    get_parser.add_argument("id", help="接棒ID")

    # serve
    subparsers.add_parser("serve", help="启动MCP Server")

    args = parser.parse_args()

    if args.command == "create":
        cmd_create(args)
    elif args.command == "accept":
        cmd_accept(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "complete":
        cmd_complete(args)
    elif args.command == "get":
        cmd_get(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
