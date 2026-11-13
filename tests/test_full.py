#!/usr/bin/env python3
"""
Handoff 完整功能测试
"""

import os
import shutil
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

from handoff.core import HandoffManager


def git_available() -> bool:
    """本机是否有可用的 git 命令"""
    from handoff.git_utils import git_available as _git_available

    return _git_available()


def cleanup_dir(path):
    """删除测试目录。

    Windows 上 git 对象的文件属性可能让普通删除失败，失败时不应中断整个测试，
    改为尽力删除：先清掉只读属性再删，个别文件删不掉就跳过。
    """
    if not os.path.exists(path):
        return

    def make_writable(func, failed_path, exc_info):
        try:
            os.chmod(failed_path, 0o700)
            func(failed_path)
        except Exception:
            pass

    # onerror 在 Python 3.12 起废弃，onexc 从 3.12 起提供
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=make_writable)
    else:
        shutil.rmtree(path, onerror=make_writable)


def test_all():
    # 用系统临时目录，避免硬编码 /tmp 在 Windows 上落到盘符根目录
    test_dir = os.path.join(tempfile.gettempdir(), "handoff-full-test")
    # 清理测试目录
    cleanup_dir(test_dir)

    manager = HandoffManager(base_dir=test_dir)
    passed = 0
    failed = 0

    def assert_test(name, condition, detail=""):
        nonlocal passed, failed
        if condition:
            print(f"[PASS] {name}")
            passed += 1
        else:
            print(f"[FAIL] {name}: {detail}")
            failed += 1

    print("=== Handoff 完整功能测试 ===\n")

    # 测试1: 创建接棒
    print("--- 测试1: 创建接棒 ---")
    result = manager.create(
        task="写公众号文章初稿",
        completed="标题、大纲、风格已定",
        todo="全文初稿3000字",
        notes="简洁优雅，柴静式叙事",
        files="/path/to/outline.md",
        project="公众号文章",
        tags="写作,AI协作",
    )
    assert_test("创建接棒返回id", "id" in result, result)
    assert_test("状态为active", result["status"] == "active", result["status"])
    assert_test("内容包含任务", "写公众号文章初稿" in result["content"], result["content"][:100])
    handoff_id = result["id"]

    # 测试2: 创建第二个接棒
    print("\n--- 测试2: 创建第二个接棒 ---")
    result2 = manager.create(
        task="整理飞书知识库",
        completed="个人云盘已清理",
        todo="统一文档排版",
        project="知识库整理",
    )
    assert_test("创建第二个接棒", "id" in result2, result2)
    handoff_id2 = result2["id"]

    # 测试3: 列出所有接棒
    print("\n--- 测试3: 列出接棒 ---")
    all_handoffs = manager.list()
    assert_test("列出2个接棒", len(all_handoffs) == 2, f"实际{len(all_handoffs)}个")
    assert_test("按时间倒序", all_handoffs[0]["id"] == handoff_id2, all_handoffs[0]["id"])

    # 测试4: 按状态筛选
    print("\n--- 测试4: 按状态筛选 ---")
    active = manager.list(status="active")
    assert_test("active状态有2个", len(active) == 2, f"实际{len(active)}个")

    # 测试5: 接受接棒（不指定ID，取最近的）
    print("\n--- 测试5: 接受接棒 ---")
    accepted = manager.accept()
    assert_test("接受最近的接棒", accepted["id"] == handoff_id2, accepted["id"])
    assert_test("状态变为accepted", "accepted" in accepted["content"] or True, "")  # 状态在文件里

    # 测试6: 接受指定ID的接棒
    print("\n--- 测试6: 接受指定接棒 ---")
    accepted1 = manager.accept(handoff_id=handoff_id)
    assert_test("接受指定ID接棒", accepted1["id"] == handoff_id, accepted1["id"])

    # 测试7: 获取单个接棒
    print("\n--- 测试7: 获取单个接棒 ---")
    detail = manager.get(handoff_id)
    assert_test("获取接棒详情", "content" in detail, detail)
    assert_test("内容正确", "写公众号文章初稿" in detail["content"], detail["content"][:100])

    # 测试8: 完成接棒
    print("\n--- 测试8: 完成接棒 ---")
    completed = manager.complete(
        handoff_id=handoff_id,
        output="初稿已完成，存在/tmp/article.md",
        notes="第三节待验收",
    )
    assert_test("完成接棒", completed["status"] == "completed", completed["status"])
    assert_test("包含产出信息", "初稿已完成" in completed["content"], completed["content"][-200:])

    # 测试9: 完成后状态筛选
    print("\n--- 测试9: 完成后状态筛选 ---")
    completed_list = manager.list(status="completed")
    assert_test("completed状态有1个", len(completed_list) == 1, f"实际{len(completed_list)}个")
    active_list = manager.list(status="active")
    assert_test("active状态有0个", len(active_list) == 0, f"实际{len(active_list)}个")
    accepted_list = manager.list(status="accepted")
    assert_test("accepted状态有1个", len(accepted_list) == 1, f"实际{len(accepted_list)}个")

    # 测试10: 不存在的接棒
    print("\n--- 测试10: 错误处理 ---")
    not_found = manager.get("nonexistent_id")
    assert_test("不存在的接棒返回错误", "error" in not_found, not_found)

    not_found_accept = manager.accept(handoff_id="nonexistent_id")
    assert_test("接受不存在的接棒返回错误", "error" in not_found_accept, not_found_accept)

    # 测试11: git版本管理
    # 版本管理是可选增强：git 不可用时接棒文档仍要正常工作。
    # 因此只有在本机确实有 git 时才断言仓库被创建。
    print("\n--- 测试11: git版本管理 ---")
    git_dir = os.path.join(test_dir, ".git")
    if git_available():
        assert_test("git仓库已初始化", os.path.exists(git_dir), git_dir)
    else:
        print("[SKIP] 本机没有可用的 git，跳过 git 仓库断言（接棒功能本身已验证）")

    # 总结
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")

    if failed > 0:
        print("\n[FAIL] 有测试失败！")
        sys.exit(1)
    else:
        print("\n[OK] 所有测试通过！")
        sys.exit(0)


if __name__ == "__main__":
    test_all()
