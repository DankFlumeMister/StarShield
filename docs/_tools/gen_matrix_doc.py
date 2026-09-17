#!/usr/bin/env python3
"""gen_matrix_doc.py — 由 matrix.json 生成 docs/matrix-assignment.md 的分配表部分"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matrix_schema  # noqa: E402  字段白名单校验（禁止静默忽略新字段）

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "docs", "_generated", "matrix.json")

data = json.load(open(SRC, encoding="utf-8"))
try:
    matrix_schema.validate(data)
except ValueError as e:
    sys.exit(f"[matrix.json 字段校验失败] {e}\n"
             f"文件：{SRC}\n"
             f"若确实新增了字段，请同步更新 docs/_tools/matrix_schema.py 的白名单，"
             f"并明确该字段在原理图中的用途。")
keys = data["matrix"]
nrow, ncol = data["rows"], data["cols"]

out = []
w = out.append

w("### 95 键完整分配表\n")
w("说明：`参考号` 同时用于原理图与 PCB（`SWn` 为开关，`Dn` 为二极管，两者编号相同以方便对位）。\n")
w("| SW / D | 键位 | 矩阵行 | 矩阵列 | KLE x (u) | 键宽 × 高 |")
w("| --- | --- | --- | --- | --- | --- |")
for k in sorted(keys, key=lambda k: (k["row"], k["centerX_u"])):
    w(f"| SW{k['index']} / D{k['index']} | {k['label']} | R{k['row']} | C{k['col']} | "
      f"{k['x_u']:.2f} | {k['w_u']}u × {k['h_u']}u |")

w("")
w("### 按矩阵行汇总\n")
w("| 矩阵行 | 键数 | 对应物理行 | 键位（按 x 排序） |")
w("| --- | --- | --- | --- |")
phys = {0: "F 行", 1: "数字行", 2: "Q 行", 3: "A 行", 4: "Z 行", 5: "底行"}
for r in range(nrow):
    ks = sorted([k for k in keys if k["row"] == r], key=lambda k: k["centerX_u"])
    w(f"| R{r} | {len(ks)} | {phys.get(r,'')} | " + ", ".join(k["label"] for k in ks) + " |")

w("")
w("### 按矩阵列汇总\n")
w("| 矩阵列 | 键数 | 占用行 | 物理 x 中心 (u) |")
w("| --- | --- | --- | --- |")
for c in range(ncol):
    ks = sorted([k for k in keys if k["col"] == c], key=lambda k: k["row"])
    rows = ",".join(f"R{k['row']}" for k in ks)
    xs = ", ".join(f"{k['centerX_u']:.3f}" for k in ks)
    w(f"| C{c} | {len(ks)} | {rows} | {xs} |")

txt = "\n".join(out) + "\n"
dst = os.path.join(ROOT, "docs", "_generated", "matrix-doc-tables.md")
with open(dst, "w", encoding="utf-8", newline="\n") as f:
    f.write(txt)
print(f"已写出 {dst}  ({len(txt)} 字节)")
