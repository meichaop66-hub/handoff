"""
核心逻辑 - 接棒文档的创建、读取、管理
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .templates import render_handoff, render_complete
from .git_utils import init_git_repo, git_commit


class HandoffManager:
    """接棒管理器"""

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = os.path.expanduser("~/.handoff")

        self.base_dir = Path(base_dir)
        self.active_dir = self.base_dir / "active"
        self.archive_dir = self.base_dir / "archive"

        # 确保目录存在
        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # 初始化git
        init_git_repo(str(self.base_dir))

    def _generate_id(self) -> str:
        """生成接棒ID"""
        return datetime.now().strftime("handoff_%Y%m%d_%H%M%S")

    def _parse_front_matter(self, content: str) -> dict:
        """解析YAML front matter"""
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return {}

        result = {}
        for line in match.group(1).split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        return result

    def _get_handoff_path(self, handoff_id: str) -> Optional[Path]:
        """根据ID查找接棒文件路径"""
        # 先在active目录找
        active_file = self.active_dir / f"{handoff_id}.md"
        if active_file.exists():
            return active_file

        # 再在archive目录找
        archive_file = self.archive_dir / f"{handoff_id}.md"
        if archive_file.exists():
            return archive_file

        return None

    def create(
        self,
        task: str,
        completed: str = "",
        todo: str = "",
        notes: str = "",
        files: str = "",
        project: str = "",
        tags: str = "",
        created_by: str = "",
    ) -> dict:
        """创建接棒文档"""
        handoff_id = self._generate_id()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        content = render_handoff(
            handoff_id=handoff_id,
            task=task,
            completed=completed,
            todo=todo,
            notes=notes,
            files=files,
            project=project,
            tags=tags,
            created_at=created_at,
            status="active",
            created_by=created_by,
        )

        file_path = self.active_dir / f"{handoff_id}.md"
        file_path.write_text(content, encoding="utf-8")

        # git提交
        git_commit(str(self.base_dir), f"create handoff: {handoff_id}")

        return {
            "id": handoff_id,
            "path": str(file_path),
            "status": "active",
            "created_at": created_at,
            "content": content,
        }

    def accept(self, handoff_id: Optional[str] = None) -> dict:
        """接受接棒 - 读取待接棒文档，标记为已接受"""
        if handoff_id:
            file_path = self._get_handoff_path(handoff_id)
            if not file_path:
                return {"error": f"接棒文档不存在: {handoff_id}"}
        else:
            # 找最近的active状态接棒
            active_files = sorted(self.active_dir.glob("*.md"), reverse=True)
            if not active_files:
                return {"error": "没有待接棒的任务"}
            file_path = active_files[0]

        content = file_path.read_text(encoding="utf-8")
        front_matter = self._parse_front_matter(content)

        # 标记为accepted（修改front matter中的status）
        if front_matter.get("status") == "active":
            new_content = content.replace(
                "status: active", "status: accepted", 1
            )
            file_path.write_text(new_content, encoding="utf-8")
            git_commit(str(self.base_dir), f"accept handoff: {file_path.stem}")

        return {
            "id": file_path.stem,
            "path": str(file_path),
            "status": front_matter.get("status", "unknown"),
            "content": content,
            "front_matter": front_matter,
        }

    def complete(
        self,
        handoff_id: Optional[str] = None,
        output: str = "",
        notes: str = "",
    ) -> dict:
        """完成接棒 - 追加完成信息，移到archive"""
        if handoff_id:
            file_path = self._get_handoff_path(handoff_id)
            if not file_path:
                return {"error": f"接棒文档不存在: {handoff_id}"}
        else:
            # 找最近的accepted状态接棒
            active_files = sorted(self.active_dir.glob("*.md"), reverse=True)
            file_path = None
            for f in active_files:
                content = f.read_text(encoding="utf-8")
                fm = self._parse_front_matter(content)
                if fm.get("status") in ("accepted", "active"):
                    file_path = f
                    break

            if not file_path:
                return {"error": "没有进行中的接棒任务"}

        content = file_path.read_text(encoding="utf-8")

        # 追加完成信息
        complete_content = render_complete(
            handoff_id=file_path.stem,
            output=output,
            notes=notes,
        )
        new_content = content + complete_content

        # 修改status为completed
        new_content = new_content.replace(
            "status: accepted", "status: completed", 1
        )
        new_content = new_content.replace(
            "status: active", "status: completed", 1
        )

        # 移到archive
        archive_path = self.archive_dir / file_path.name
        archive_path.write_text(new_content, encoding="utf-8")
        file_path.unlink()

        git_commit(str(self.base_dir), f"complete handoff: {file_path.stem}")

        return {
            "id": file_path.stem,
            "path": str(archive_path),
            "status": "completed",
            "content": new_content,
        }

    def list(self, status: Optional[str] = None) -> list:
        """列出所有接棒"""
        result = []

        # 列出active目录
        for f in sorted(self.active_dir.glob("*.md"), reverse=True):
            content = f.read_text(encoding="utf-8")
            fm = self._parse_front_matter(content)

            if status and fm.get("status") != status:
                continue

            # 提取任务摘要（## 任务后面的第一行）
            task_match = re.search(r"## 任务\n(.+?)(?:\n|$)", content)
            task_summary = task_match.group(1).strip() if task_match else ""

            result.append(
                {
                    "id": f.stem,
                    "status": fm.get("status", "unknown"),
                    "project": fm.get("project", ""),
                    "tags": fm.get("tags", ""),
                    "created_at": fm.get("created_at", ""),
                    "task_summary": task_summary[:80],
                    "location": "active",
                }
            )

        # 列出archive目录
        for f in sorted(self.archive_dir.glob("*.md"), reverse=True):
            content = f.read_text(encoding="utf-8")
            fm = self._parse_front_matter(content)

            if status and fm.get("status") != status:
                continue

            task_match = re.search(r"## 任务\n(.+?)(?:\n|$)", content)
            task_summary = task_match.group(1).strip() if task_match else ""

            result.append(
                {
                    "id": f.stem,
                    "status": fm.get("status", "unknown"),
                    "project": fm.get("project", ""),
                    "tags": fm.get("tags", ""),
                    "created_at": fm.get("created_at", ""),
                    "task_summary": task_summary[:80],
                    "location": "archive",
                }
            )

        return result

    def get(self, handoff_id: str) -> dict:
        """获取单个接棒的完整内容"""
        file_path = self._get_handoff_path(handoff_id)
        if not file_path:
            return {"error": f"接棒文档不存在: {handoff_id}"}

        content = file_path.read_text(encoding="utf-8")
        front_matter = self._parse_front_matter(content)

        return {
            "id": handoff_id,
            "path": str(file_path),
            "status": front_matter.get("status", "unknown"),
            "content": content,
            "front_matter": front_matter,
        }
