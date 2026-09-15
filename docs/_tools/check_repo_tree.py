#!/usr/bin/env python3
"""check_repo_tree.py —— 提交前闸门：公开仓库只允许出现白名单内的顶层条目

为什么需要这个脚本（真实事故）：
    调研工具/子代理会把第三方项目克隆、把抓取物和一次性脚本落在仓库**根目录**，
    例如 `sanmo61/`（第三方三模键盘工程 257 个文件）、`sanmo61.zip`（10 MB）、
    `api.ps1`、`osh_ch582m.html`。
    一次 `git add -A` 就把它们提交并推送到了**公开**仓库。

    `.gitignore` 挡不住这类问题：它只能枚举「已知的坏东西」，
    而新目录的名字在发生前是想不到的。

    所以本脚本反过来做：**枚举允许的东西**。任何白名单之外的顶层条目一律报错。
    在 `git add` 之前跑一次，就能把这类事故挡在提交之外。

用法：
    python docs/_tools/check_repo_tree.py            # 检查已跟踪文件
    python docs/_tools/check_repo_tree.py --staged   # 检查暂存区（更早发现）
退出码 0 = 通过，1 = 发现越界条目（不要提交）
"""
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 允许出现在仓库根目录的条目（白名单）。
# 新增顶层文件/目录时**必须**同步加到这里 —— 这是刻意的摩擦力。
ALLOWED_TOP = {
    ".gitattributes", ".gitignore", ".github",
    "LICENSE", "README.md",
    "docs", "firmware", "hardware", "research", "sketch", "tutorials",
}

# 已知的内部/临时顶层条目：允许存在于磁盘，但**绝不允许被跟踪**。
# 若它们出现在跟踪清单里，说明 .gitignore 失效或用了 git add -f。
FORBIDDEN_TRACKED = {
    "PROJECT_HANDOFF.md", "_research", ".research", ".zmk-research",
    "_jst", "node_modules",
}


def tracked_files(staged: bool) -> list:
    if staged:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True, text=True).stdout
    else:
        out = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout
    return [l for l in out.splitlines() if l.strip()]


def main() -> int:
    staged = "--staged" in sys.argv
    files = tracked_files(staged)
    if not files:
        print("（没有文件）")
        return 0

    tops = sorted({f.split("/")[0] for f in files})
    offenders = [t for t in tops if t not in ALLOWED_TOP]
    forbidden = [f for f in files if f.split("/")[0] in FORBIDDEN_TRACKED]

    label = "暂存区" if staged else "已跟踪文件"
    print(f"{label}: {len(files)} 个，顶层条目 {len(tops)} 个")
    print("  顶层: " + ", ".join(tops))

    if offenders:
        print()
        print("❌ 顶层出现白名单之外的条目 —— 极可能是调研临时产物/第三方克隆：")
        for t in offenders:
            n = sum(1 for f in files if f.split("/")[0] == t)
            print(f"     {t}   ({n} 个文件)")
        print()
        print("   处置：确认是临时产物后用 `git rm -r --cached <路径>` 剔出索引，")
        print("         并在 .gitignore 补规则；确认要发布才把它加进 ALLOWED_TOP。")
    if forbidden:
        print()
        print("❌ 内部/临时条目被跟踪了（.gitignore 失效或被 -f 强制加入）：")
        for f in forbidden:
            print(f"     {f}")

    if offenders or forbidden:
        return 1
    print("✅ 顶层条目全部在白名单内")
    return 0


if __name__ == "__main__":
    sys.exit(main())
