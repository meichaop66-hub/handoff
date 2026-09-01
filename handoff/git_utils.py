"""
git工具 - 自动版本管理
"""

import os
import subprocess
from pathlib import Path


def init_git_repo(repo_path: str) -> bool:
    """初始化git仓库"""
    path = Path(repo_path)
    git_dir = path / ".git"

    if git_dir.exists():
        return True

    try:
        subprocess.run(
            ["git", "init"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        # 配置用户信息（如果没有的话）
        subprocess.run(
            ["git", "config", "user.email", "handoff@local"],
            cwd=repo_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Handoff"],
            cwd=repo_path,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def git_commit(repo_path: str, message: str) -> bool:
    """提交所有改动"""
    try:
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        # 如果没有改动，commit会失败，这是正常的
        return result.returncode == 0 or "nothing to commit" in result.stdout
    except subprocess.CalledProcessError:
        return False


def get_git_status(repo_path: str) -> str:
    """获取git状态摘要"""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def get_recent_files(repo_path: str, count: int = 5) -> str:
    """获取最近修改的文件"""
    try:
        result = subprocess.run(
            ["git", "log", "--name-only", "--pretty=format:", f"-{count}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
        return "\n".join(f"- {f}" for f in files[:count])
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
