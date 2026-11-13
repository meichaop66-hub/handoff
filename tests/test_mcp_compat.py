#!/usr/bin/env python3
"""
Handoff MCP 兼容性测试

覆盖两件事：
1. MCP Server 在 mcp 1.x 与 2.x 下都能注册出同样的一组工具与同样的输入 schema。
2. git 不可用时（未安装或不在 PATH），接棒文档仍能正常创建/读取/完成，
   而不是让 MCP server 直接崩溃。

本测试只依赖标准库与已安装的 mcp 包；若 mcp 未安装则跳过协议层断言。
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Windows 终端默认可能是 GBK 等非 UTF-8 编码，输出中文与符号会抛
# UnicodeEncodeError。强制 stdout/stderr 使用 UTF-8，避免测试被终端编码打断。
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

def cleanup_dir(path):
    """尽力删除目录：Windows 上 git 对象的只读属性可能导致普通删除失败。"""
    if not os.path.exists(path):
        return

    def make_writable(func, failed_path, exc_info):
        try:
            os.chmod(failed_path, 0o700)
            func(failed_path)
        except Exception:
            pass

    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=make_writable)
    else:
        shutil.rmtree(path, onerror=make_writable)

PASSED = 0
FAILED = 0


def assert_test(name, condition, detail=""):
    global PASSED, FAILED
    if condition:
        print(f"[PASS] {name}")
        PASSED += 1
    else:
        print(f"[FAIL] {name}: {detail}")
        FAILED += 1


def test_git_utils_degrades_without_git():
    """git 不可用时 git_utils 不能抛异常"""
    print("\n--- 测试: git 缺失时降级 ---")
    from handoff import git_utils

    original_run = subprocess.run

    def boom(*args, **kwargs):
        raise FileNotFoundError("git 不存在")

    test_dir = tempfile.mkdtemp(prefix="handoff-nogit-")
    try:
        subprocess.run = boom
        try:
            init_ok = git_utils.init_git_repo(test_dir)
            assert_test("init_git_repo 不抛异常", init_ok is False, f"返回 {init_ok}")

            commit_ok = git_utils.git_commit(test_dir, "test")
            assert_test("git_commit 不抛异常", commit_ok is False, f"返回 {commit_ok}")

            status = git_utils.get_git_status(test_dir)
            assert_test("get_git_status 返回空串", status == "", repr(status))

            files = git_utils.get_recent_files(test_dir)
            assert_test("get_recent_files 返回空串", files == "", repr(files))
        finally:
            subprocess.run = original_run
    finally:
        cleanup_dir(test_dir)


def test_handoff_manager_works_without_git():
    """git 不可用时 HandoffManager 仍可正常工作"""
    print("\n--- 测试: git 缺失时接棒文档仍可用 ---")
    from handoff.core import HandoffManager
    from handoff import git_utils

    original_run = subprocess.run

    def boom(*args, **kwargs):
        raise FileNotFoundError("git 不存在")

    test_dir = tempfile.mkdtemp(prefix="handoff-nogit-mgr-")
    try:
        subprocess.run = boom
        try:
            manager = HandoffManager(base_dir=test_dir)
            created = manager.create(task="无 git 环境下的接棒", project="test")
            assert_test("创建接棒成功", "id" in created, created)

            listed = manager.list()
            assert_test("列出接棒成功", len(listed) == 1, listed)

            got = manager.get(created["id"])
            assert_test("读取接棒成功", "无 git 环境下的接棒" in got.get("content", ""), got)

            accepted = manager.accept(handoff_id=created["id"])
            assert_test("接受接棒成功", accepted["id"] == created["id"], accepted)

            completed = manager.complete(handoff_id=created["id"], output="产出")
            assert_test("完成接棒成功", completed["status"] == "completed", completed)
        finally:
            subprocess.run = original_run
    finally:
        cleanup_dir(test_dir)


def _tool_schema(tool):
    """读取工具的输入 schema。

    mcp 1.x 的 Tool 用 parameters，2.x 用 inputSchema，两个名字都兼容。
    """
    schema = getattr(tool, "inputSchema", None)
    if schema is None:
        schema = getattr(tool, "parameters", None)
    return schema or {}


def test_git_calls_have_timeout_and_no_stdin_inheritance():
    """git 调用必须有超时，且不能继承 MCP server 的 stdin 管道

    MCP server 的 stdin 是 JSON-RPC 管道。若 git 子进程继承它，git 的交互式
    行为会与协议流互相干扰；而没有超时的 git 调用可能永久阻塞工具响应。
    """
    print("\n--- 测试: git 调用有超时且不继承 stdin ---")
    from handoff import git_utils

    captured = []
    original_run = subprocess.run

    def spy_run(args, **kwargs):
        captured.append((args, kwargs))
        raise FileNotFoundError("git 不存在")

    try:
        subprocess.run = spy_run
        git_utils._run_git(["status"], os.getcwd())
        git_utils.git_available()
    finally:
        subprocess.run = original_run

    assert_test("捕获到 git 调用", len(captured) >= 2, captured)

    for args, kwargs in captured:
        assert_test(
            f"{args[0] if args else '?'} 调用带 timeout",
            kwargs.get("timeout") is not None,
            kwargs,
        )
        assert_test(
            f"{args[0] if args else '?'} 调用不继承 stdin",
            kwargs.get("stdin") is subprocess.DEVNULL,
            kwargs.get("stdin"),
        )


def test_git_timeout_is_bounded():
    """git 超时后必须返回 False，而不是抛异常或挂死"""
    print("\n--- 测试: git 超时后降级 ---")
    from handoff import git_utils

    original_run = subprocess.run

    def timeout_run(args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args, timeout=kwargs.get("timeout", 1))

    test_dir = tempfile.mkdtemp(prefix="handoff-timeout-")
    try:
        subprocess.run = timeout_run
        try:
            assert_test(
                "git_commit 超时返回 False",
                git_utils.git_commit(test_dir, "x") is False,
                "应返回 False",
            )
            assert_test(
                "init_git_repo 超时返回 False",
                git_utils.init_git_repo(test_dir) is False,
                "应返回 False",
            )
        finally:
            subprocess.run = original_run
    finally:
        cleanup_dir(test_dir)


def test_mcp_server_tool_contract():
    """MCP Server 注册的工具名与输入 schema 在 1.x / 2.x 下必须一致"""
    print("\n--- 测试: MCP 工具契约 ---")
    try:
        from handoff.mcp_server import MCP_AVAILABLE, create_mcp_server
    except Exception as exc:
        print(f"[SKIP] 跳过（无法导入 mcp_server: {exc}）")
        return

    if not MCP_AVAILABLE:
        print("[SKIP] 跳过（未安装 mcp）")
        return

    import mcp

    try:
        server = create_mcp_server()
    except Exception as exc:
        print(f"[FAIL] create_mcp_server 抛异常: {exc}")
        globals()["FAILED"] = globals()["FAILED"] + 1
        return

    mcp_version = getattr(mcp, "__version__", "unknown")
    print(f"  当前 mcp 版本: {mcp_version}")

    # FastMCP/MCPServer 都提供 _tool_manager.list_tools()
    tools = server._tool_manager.list_tools()
    names = sorted(t.name for t in tools)
    expected = [
        "handoff_accept",
        "handoff_complete",
        "handoff_create",
        "handoff_get",
        "handoff_list",
    ]
    assert_test(f"工具名一致 ({mcp_version})", names == expected, names)

    create_tool = next((t for t in tools if t.name == "handoff_create"), None)
    assert_test("handoff_create 存在", create_tool is not None, names)
    if create_tool is not None:
        schema = _tool_schema(create_tool)
        assert_test("handoff_create 必填 task", "task" in schema.get("required", []), schema.get("required"))
        props = set(schema.get("properties", {}))
        expected_props = {"task", "completed", "todo", "notes", "files", "project", "tags"}
        assert_test("handoff_create 参数齐全", props == expected_props, sorted(props))

    # 工具描述不应为空，模型据此决定何时调用
    for tool in tools:
        assert_test(f"{tool.name} 有描述", bool(tool.description), "描述为空")


def _tool_text(result):
    """从 call_tool 的返回值里取出文本内容。

    mcp 1.x 返回 list[TextContent]，2.x 返回带 .content 的结果对象，
    两种形态都要能取到文本。
    """
    content = getattr(result, "content", None)
    if content is None and isinstance(result, tuple):
        content = result[0]
    if content is None:
        content = result

    if isinstance(content, (list, tuple)):
        parts = []
        for block in content:
            text = getattr(block, "text", None)
            if text is None and isinstance(block, dict):
                text = block.get("text")
            if text:
                parts.append(text)
        return "\n".join(parts)

    text = getattr(content, "text", None)
    if text is None and isinstance(content, dict):
        text = content.get("text")
    return text or ""


def test_mcp_server_tool_calls():
    """通过高层 API 实际调用每个工具，验证返回体是合法 JSON"""
    print("\n--- 测试: MCP 工具可调用且返回合法 JSON ---")
    try:
        from handoff.mcp_server import MCP_AVAILABLE, create_mcp_server
    except Exception as exc:
        print(f"[SKIP] 跳过（无法导入 mcp_server: {exc}）")
        return

    if not MCP_AVAILABLE:
        print("[SKIP] 跳过（未安装 mcp）")
        return

    import handoff.core as core_module

    test_dir = tempfile.mkdtemp(prefix="handoff-mcp-call-")
    original_init = core_module.HandoffManager.__init__

    def patched_init(self, base_dir=None):
        original_init(self, base_dir=test_dir)

    core_module.HandoffManager.__init__ = patched_init
    try:
        server = create_mcp_server()

        async def run_calls():
            created = await server.call_tool(
                "handoff_create",
                {"task": "兼容性验证任务", "project": "compat", "tags": "测试"},
            )
            text = _tool_text(created)
            data = json.loads(text)
            assert_test("handoff_create 返回合法 JSON", "id" in data, text[:200])
            assert_test("中文内容未被转义", "兼容性验证任务" in text, text[:200])

            listed = await server.call_tool("handoff_list", {})
            text = _tool_text(listed)
            items = json.loads(text)
            assert_test("handoff_list 返回数组", isinstance(items, list), type(items).__name__)

            accepted = await server.call_tool("handoff_accept", {})
            text = _tool_text(accepted)
            assert_test("handoff_accept 返回合法 JSON", "id" in json.loads(text), text[:200])

            missing = await server.call_tool("handoff_get", {"handoff_id": "nope"})
            text = _tool_text(missing)
            assert_test("不存在的接棒返回 error", "error" in json.loads(text), text[:200])

        asyncio.run(run_calls())
    finally:
        core_module.HandoffManager.__init__ = original_init
        cleanup_dir(test_dir)


def test_mcp_server_stdio_handshake():
    """以 stdio 子进程方式跑一次真实协议握手"""
    print("\n--- 测试: stdio 协议握手 ---")
    try:
        import mcp  # noqa: F401
    except Exception:
        print("[SKIP] 跳过（未安装 mcp）")
        return

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    home = tempfile.mkdtemp(prefix="handoff-stdio-")
    env = dict(os.environ)
    env["HOME"] = home
    env["USERPROFILE"] = home
    env["PYTHONPATH"] = repo_root

    proc = subprocess.Popen(
        [sys.executable, "-m", "handoff.mcp_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        encoding="utf-8",
        bufsize=1,
        cwd=home,
    )
    try:
        def send(payload):
            proc.stdin.write(json.dumps(payload) + "\n")
            proc.stdin.flush()

        send({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1"},
            },
        })

        response = None
        deadline = 30
        for _ in range(deadline * 10):
            line = proc.stdout.readline()
            if not line:
                break
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if obj.get("id") == 1:
                response = obj
                break

        assert_test("initialize 有响应", response is not None, "超时未收到响应")
        if response:
            server_info = response.get("result", {}).get("serverInfo", {})
            assert_test("serverInfo.name 为 handoff", server_info.get("name") == "handoff", server_info)

        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})

        tools_response = None
        for _ in range(300):
            line = proc.stdout.readline()
            if not line:
                break
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if obj.get("id") == 2:
                tools_response = obj
                break

        assert_test("tools/list 有响应", tools_response is not None, "超时未收到响应")
        if tools_response:
            names = sorted(t["name"] for t in tools_response.get("result", {}).get("tools", []))
            assert_test(
                "工具名齐全",
                names == [
                    "handoff_accept", "handoff_complete", "handoff_create",
                    "handoff_get", "handoff_list",
                ],
                names,
            )
    finally:
        proc.kill()
        cleanup_dir(home)


def main():
    print("=== Handoff MCP 兼容性测试 ===\n")
    test_git_utils_degrades_without_git()
    test_git_calls_have_timeout_and_no_stdin_inheritance()
    test_git_timeout_is_bounded()
    test_handoff_manager_works_without_git()
    test_mcp_server_tool_contract()
    test_mcp_server_tool_calls()
    test_mcp_server_stdio_handshake()

    print(f"\n=== 测试结果 ===")
    print(f"通过: {PASSED}")
    print(f"失败: {FAILED}")
    print(f"总计: {PASSED + FAILED}")

    if FAILED > 0:
        print("\n[FAIL] 有测试失败！")
        sys.exit(1)
    print("\n[OK] 所有测试通过！")
    sys.exit(0)


if __name__ == "__main__":
    main()
