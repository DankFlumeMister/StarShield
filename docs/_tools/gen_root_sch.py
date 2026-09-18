#!/usr/bin/env python3
"""gen_root_sch.py —— 生成 KiCad 工程根图（只做一件事：列出全部层次化子图）

输出：hardware/pcb/StarShield/Starshield.kicad_sch

为什么把根图从 gen_matrix_sch.py 里拆出来：
    根图是「整个工程有哪些子图」的清单 —— 它属于工程，不属于任何一张子图。
    原先由矩阵生成器顺带写根图，导致新增子图必须去改矩阵生成器，
    职责错位、也容易忘记改。拆出后：
      gen_matrix_sch.py 只管 matrix/ 三张图
      gen_power_sch.py  只管 power/ 一张图
      gen_root_sch.py   只管根图（新增子图时**只改这里**）
    ⚠️ 子图 UUID 仍与 gen_matrix_sch.py 用同一套确定性命名（uid("sheet:" + name)），
       拆出后矩阵三张子图的 UUID 保持不变 ⇒ 根图 diff 只多出电源子图那一块。
"""
import os
import sys
import uuid

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 与 gen_matrix_sch.py / gen_power_sch.py 共用同一命名空间
NS = uuid.UUID("6f1a4d2e-8b3c-4f5a-9e7d-1c2b3a4d5e6f")


def uid(name):
    return str(uuid.uuid5(NS, name))


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "hardware", "pcb", "StarShield")
OUT = os.path.join(OUT_DIR, "Starshield.kicad_sch")

# 根图要用的图纸：矩阵三张 + 电源 + 控制 + RGB，共 6 张（各 60×40）。
# A4 装不下（A4 横放只有 297×210 mm），用 A3；6 张竖排（6×60=360）也超出 A3 高度 297
# ⇒ 改为 **3 列 × 2 行** 网格布置。
PAPER = "A3"
SHEET_W, SHEET_H = 60.0, 40.0
X0, Y0 = 60.0, 60.0
COL_STEP = 70.0
ROW_STEP = 60.0
PER_ROW = 3

# (子图内的 uuid 名, 显示名, Sheetfile)
SHEETS = [
    ("sheet:matrix_r012", "矩阵行 R0-R1", "matrix/matrix_r012.kicad_sch"),
    ("sheet:matrix_r234", "矩阵行 R2-R3", "matrix/matrix_r234.kicad_sch"),
    ("sheet:matrix_r45", "矩阵行 R4-R5", "matrix/matrix_r45.kicad_sch"),
    ("power:sheet:power", "电源 / 充电 / RGB 门控", "power/power.kicad_sch"),
    ("control:sheet:control", "控制板 / MCU / 595 / 模式开关", "control/control.kicad_sch"),
    ("rgb:sheet:rgb", "RGB（95 颗 SK6812MINI-E 数据链）", "rgb/rgb.kicad_sch"),
]


def build():
    body = []
    for i, (uname, title, file) in enumerate(SHEETS):
        x = X0 + (i % PER_ROW) * COL_STEP
        y = Y0 + (i // PER_ROW) * ROW_STEP
        body.append(
            f'\t(sheet (at {x:.2f} {y:.2f}) (size {SHEET_W:.2f} {SHEET_H:.2f}) (fields_autoplaced yes)\n'
            f'\t\t(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000))\n'
            f'\t\t(uuid "{uid(uname)}")\n'
            f'\t\t(property "Sheetname" "{title}" (at {x:.2f} {y - 1.2:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (justify left bottom)))\n'
            f'\t\t(property "Sheetfile" "{file}" (at {x:.2f} {y + SHEET_H + 1.0:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (justify left top)))\n'
            f'\t)'
        )
    head = [
        "(kicad_sch",
        "\t(version 20260306)",
        '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{uid("root-sheet")}")',
        f'\t(paper "{PAPER}")',
        "\t(title_block",
        '\t\t(title "StarShield（根图）")',
        '\t\t(rev "0.1")',
        '\t\t(comment 1 "自动生成：docs/_tools/gen_root_sch.py —— 新增子图只改这个文件")',
        "\t)",
        "\t(lib_symbols",
        "\t)",
    ]
    tail = ["\t(sheet_instances", '\t\t(path "/" (page "1"))', "\t)", "\t(embedded_fonts no)", ")"]
    return head + body + tail


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(build()) + "\n")
    print(f"  {os.path.relpath(OUT, ROOT):58} {os.path.getsize(OUT):8} 字节  共 {len(SHEETS)} 张子图")


if __name__ == "__main__":
    main()
