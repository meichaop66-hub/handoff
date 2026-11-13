"""
git工具 - 自动版本管理

版本管理是锦上添花，不是接棒的前提：
- git 不可用（未安装、不在 PATH）时，接棒文档本身仍要能正常读写。
- git 调用卡住时（索引锁、钩子等待、凭据交互），不能连带卡住 MCP server，
  因此每次调用都有超时，超时按「本次未提交」处理。

所有 git 调用都降级为返回 False/None，而不是抛异常打断 MCP server。
"""

import subprocess
from pathlib import Path

# 单次 git 调用的超时上限（秒）。
# 取值偏小：git 操作只是附加能力，接棒文档已经写盘成功，不值得为它长时间阻塞。
GIT_TIMEOUT = 10


def git_available() -> bool:
    """检测本机是否有可用的 git 命令。

    版本管理是可选增强：git 不可用时接棒文档本身仍要能正常工作。
    """
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT,
            stdin=subprocess.DEVNULL,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def _run_git(args, repo_path, check=False):
    """执行 git 命令。

    - git 不存在、超时或执行失败时返回 None，不抛异常。
    - stdin 显式接到 DEVNULL：MCP server 的 stdin 是 JSON-RPC 管道，
      若被 git 子进程继承，git 的交互式行为会与协议流互相干扰。
    """
    try:
        return subprocess.run(
            ["git"] + args,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=check,
            timeout=GIT_TIMEOUT,
            stdin=subprocess.DEVNULL,
        )
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
        OSError,
    ):
        return None


def init_git_repo(repo_path: str) -> bool:
    """初始化git仓库。git不可用时返回False，不影响接棒文档本身的使用。"""
    path = Path(repo_path)
    git_dir = path / ".git"

    if git_dir.exists():
        return True

    result = _run_git(["init"], repo_path, check=True)
    if result is None:
        return False

    # 配置用户信息（如果没有的话）
    _run_git(["config", "user.email", "handoff@local"], repo_path)
    _run_git(["config", "user.name", "Handoff"], repo_path)
    return True


def git_commit(repo_path: str, message: str) -> bool:
    """提交所有改动。git不可用时返回False，接棒文档本身不受影响。"""
    staged = _run_git(["add", "-A"], repo_path, check=True)
    if staged is None:
        return False

    result = _run_git(["commit", "-m", message], repo_path)
    if result is None:
        return False

    # 如果没有改动，commit会失败，这是正常的
    return result.returncode == 0 or "nothing to commit" in result.stdout


def get_git_status(repo_path: str) -> str:
    """获取git状态摘要"""
    result = _run_git(["status", "--short"], repo_path)
    return result.stdout.strip() if result is not None else ""


def get_recent_files(repo_path: str, count: int = 5) -> str:
    """获取最近修改的文件"""
    result = _run_git(
        ["log", "--name-only", "--pretty=format:", f"-{count}"], repo_path
    )
    if result is None:
        return ""
    files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
    return "\n".join(f"- {f}" for f in files[:count])
