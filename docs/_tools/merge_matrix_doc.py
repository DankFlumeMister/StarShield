#!/usr/bin/env python3
"""merge_matrix_doc.py — 把生成的矩阵表格注入 docs/matrix-assignment.md

**幂等**：用成对标记包裹注入区，重复运行只替换标记之间的内容，
不会重复追加、也不依赖手工占位符是否还在。

同时删除 gen_matrix_doc.py 的中间产物（表格内容已并入正式文档，无需留副本）。
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOC = os.path.join(ROOT, "docs", "matrix-assignment.md")
TABLES = os.path.join(ROOT, "docs", "_generated", "matrix-doc-tables.md")

BEGIN = "<!-- BEGIN GENERATED TABLES -->"
END = "<!-- END GENERATED TABLES -->"
# 早期版本的占位符（首次运行时替换掉）
LEGACY_MARKS = ["<!-- INSERT_TABLES -->",
                "<!-- 由 docs/_tools/gen_matrix_doc.py 生成的内容粘贴于此 -->"]


def main():
    if not os.path.exists(DOC):
        print(f"❌ 找不到 {DOC}")
        return 1
    if not os.path.exists(TABLES):
        print(f"❌ 找不到 {TABLES}，请先运行 gen_matrix_doc.py")
        return 1

    doc = open(DOC, encoding="utf-8").read()
    tables = open(TABLES, encoding="utf-8").read().rstrip()
    block = f"{BEGIN}\n\n{tables}\n\n{END}"

    if BEGIN in doc and END in doc:
        head, rest = doc.split(BEGIN, 1)
        _old, tail = rest.split(END, 1)
        doc = head + block + tail
        action = "已替换标记区间内的表格"
    else:
        # 首次运行：优先替换历史占位符，否则追加到第 2 节末尾
        replaced = False
        for mark in LEGACY_MARKS:
            if mark in doc:
                doc = doc.replace(mark, block, 1)
                replaced = True
                action = f"已用标记区间替换历史占位符"
                break
        if not replaced:
            print("⚠️ 既无标记区间也无历史占位符，未做修改（请人工确认文档结构）")
            return 1

    with open(DOC, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)

    # 中间产物已并入正式文档，删除以免两份副本漂移
    os.remove(TABLES)
    print(f"✅ {action}；已合并进 {os.path.relpath(DOC, ROOT)}，并删除中间产物")
    return 0


if __name__ == "__main__":
    sys.exit(main())
