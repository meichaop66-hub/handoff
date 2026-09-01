"""
接棒文档模板
"""

from datetime import datetime


def render_handoff(
    handoff_id: str,
    task: str,
    completed: str = "",
    todo: str = "",
    notes: str = "",
    files: str = "",
    project: str = "",
    tags: str = "",
    created_at: str = "",
    status: str = "active",
    created_by: str = "",
) -> str:
    """渲染接棒文档"""
    if not created_at:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "---",
        f"id: {handoff_id}",
        f"created_at: {created_at}",
        f"status: {status}",
        f"project: {project}",
        f"tags: {tags}",
        f"created_by: {created_by}",
        "---",
        "",
        "# 接棒文档",
        "",
        "## 任务",
        task,
        "",
    ]

    if completed:
        lines.extend(["## 已完成", completed, ""])

    if todo:
        lines.extend(["## 未完成", todo, ""])

    if notes:
        lines.extend(["## 注意事项", notes, ""])

    if files:
        lines.extend(["## 相关文件", files, ""])

    return "\n".join(lines)


def render_complete(
    handoff_id: str,
    output: str = "",
    notes: str = "",
    completed_at: str = "",
) -> str:
    """渲染完成接棒的追加内容"""
    if not completed_at:
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "",
        "---",
        "",
        "## 接棒完成",
        f"**完成时间**: {completed_at}",
        "",
    ]

    if output:
        lines.extend(["### 产出", output, ""])

    if notes:
        lines.extend(["### 备注", notes, ""])

    return "\n".join(lines)
