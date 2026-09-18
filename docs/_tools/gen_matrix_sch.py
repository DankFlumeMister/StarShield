#!/usr/bin/env python3
"""gen_matrix_sch.py — 由矩阵分配数据生成 KiCad 10 原理图（95 键矩阵，分 3 张子图）

输入：docs/_generated/matrix.json（由 docs/_tools/matrix-assign.mjs 生成）
输出：hardware/pcb/StarShield/matrix/
        matrix/matrix_r012.kicad_sch   矩阵行 R0-R1
        matrix/matrix_r234.kicad_sch   矩阵行 R2-R3
        matrix/matrix_r45.kicad_sch    矩阵行 R4-R5

⚠️ 根图 `Starshield.kicad_sch` **不由本脚本生成**（2026-09-17 拆出）：
   根图是「工程有哪些子图」的清单，属工程级；现由 `docs/_tools/gen_root_sch.py` 负责。
   新增子图（如电源子图）请改 gen_root_sch.py 的 SHEETS，不要改这里。

⚠️ 为什么要分图：KiCad 加载器对单张原理图有大小上限（实测约 226 KB / 559 个顶层元素）。
   95 键 + 95 二极管放在一张图里约 237 KB，会「加载原理图失败」。
   分 3 张后每张约 80 KB，安全。
   实验证据见 docs/matrix-assignment.md 的「踩坑记录」。

设计约定：
- 每个键位 = 一颗 SW_Push 开关，1 号引脚接「行网络」，2 号引脚接二极管阳极。
- 二极管阴极接「列网络」。电流方向：列 → 二极管 → 开关 → 行（ROW2COL 扫描）。
  KiCad 的 Device:D 符号：pin 1 = K（阴极），pin 2 = A（阳极）。
- 用「局部标签」而非长导线连接行列：同名标签自动并入同一网络。
"""
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matrix_schema  # noqa: E402  字段白名单校验（禁止静默忽略新字段）

# 确定性 UUID：用 uuid5 从稳定的名字串生成，使重复运行产出**逐字节一致**的文件。
# 这对「小步可验证、可回退」很重要：重新生成不应产生无意义的 git diff。
NS = uuid.UUID("6f1a4d2e-8b3c-4f5a-9e7d-1c2b3a4d5e6f")
_UUID_CACHE = {}


def uid(name=None):
    """name 为 None 时返回随机 UUID（仅用于不该稳定的场合）；否则返回确定性 UUID。"""
    if name is None:
        return str(uuid.uuid4())
    if name not in _UUID_CACHE:
        _UUID_CACHE[name] = str(uuid.uuid5(NS, name))
    return _UUID_CACHE[name]

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "docs", "_generated", "matrix.json")
OUT_DIR = os.path.join(ROOT, "hardware", "pcb", "StarShield")
MATRIX_DIR = os.path.join(OUT_DIR, "matrix")

# ---------- 布局参数（mm） ----------
COL_SPACING = 25.4      # 相邻矩阵列的水平间距
ROW_SPACING = 15.24     # 相邻行的垂直间距
X0, Y0 = 40.0, 40.0
# 连接网格：原理图 ERC 要求「引脚端点与导线端点落在连接网格上」。
# 键位中心 X 含半单位（如 2.00u、5.125u），减去 5.08 后会落在 0.635 的奇数倍上，
# 因此把连接网格设为 0.635mm（KiCad 允许的合法网格值），可消除
# [endpoint_off_grid] 警告。见 docs/matrix-assignment.md 踩坑记录。
GRID = 0.635

# 分图方案：每张子图承载的矩阵行区间
SHEETS = [
    ("matrix_r012", "矩阵行 R0-R1", [0, 1]),
    ("matrix_r234", "矩阵行 R2-R3", [2, 3]),
    ("matrix_r45", "矩阵行 R4-R5", [4, 5]),
]

SW_SYM = """\t\t(symbol "Switch:SW_Push"
\t\t\t(pin_numbers (hide yes))
\t\t\t(pin_names (offset 1.016) (hide yes))
\t\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes)
\t\t\t(duplicate_pin_numbers_are_jumpers no)
\t\t\t(property "Reference" "SW" (at 1.27 2.54 0) (show_name no) (do_not_autoplace no)
\t\t\t\t(effects (font (size 1.27 1.27)) (justify left)))
\t\t\t(property "Value" "SW_Push" (at 0 -1.524 0) (show_name no) (do_not_autoplace no)
\t\t\t\t(effects (font (size 1.27 1.27))))
\t\t\t(property "Footprint" "Button_Switch_Keyboard:SW_MX_Hotswap" (at 0 5.08 0) (show_name no) (do_not_autoplace no) (hide yes)
\t\t\t\t(effects (font (size 1.27 1.27))))
\t\t\t(property "Datasheet" "" (at 0 5.08 0) (show_name no) (do_not_autoplace no) (hide yes)
\t\t\t\t(effects (font (size 1.27 1.27))))
\t\t\t(property "Description" "Push button switch, generic, two pins" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes)
\t\t\t\t(effects (font (size 1.27 1.27))))
\t\t\t(symbol "SW_Push_0_1"
\t\t\t\t(circle (center -2.032 0) (radius 0.508) (stroke (width 0) (type default)) (fill (type none)))
\t\t\t\t(polyline (pts (xy 0 1.27) (xy 0 3.048)) (stroke (width 0) (type default)) (fill (type none)))
\t\t\t\t(circle (center 2.032 0) (radius 0.508) (stroke (width 0) (type default)) (fill (type none)))
\t\t\t\t(polyline (pts (xy 2.54 1.27) (xy -2.54 1.27)) (stroke (width 0) (type default)) (fill (type none)))
\t\t\t)
\t\t\t(symbol "SW_Push_1_1"
\t\t\t\t(pin passive line (at -5.08 0 0) (length 2.54)
\t\t\t\t\t(name "1" (effects (font (size 1.27 1.27))))
\t\t\t\t\t(number "1" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at 5.08 0 180) (length 2.54)
\t\t\t\t\t(name "2" (effects (font (size 1.27 1.27))))
\t\t\t\t\t(number "2" (effects (font (size 1.27 1.27)))))
\t\t\t)
\t\t\t(embedded_fonts no)
\t\t)"""

D_SYM = """\t\t(symbol "Device:D"
\t\t\t(pin_numbers (hide yes))
\t\t\t(pin_names (offset 1.016) (hide yes))
\t\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (in_pos_files yes)
\t\t\t(duplicate_pin_numbers_are_jumpers no)
\t\t\t(property "Reference" "D" (at 0 2.54 0) (show_name no) (do_not_autoplace no)
\t\t\t\t(effects (font (size 1.27 1.27))))
\t\t\t(property "Value" "D" (at 0 -2.54 0) (show_name no) (do_not_autoplace no)
\t\t\t\t(effects (font (size 1.27 1.27))))
\t\t\t(property "Footprint" "Diode_SMD:D_SOD-123" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes)
\t\t\t\t(effects (font (size 1.27 1.27))))
\t\t\t(property "Datasheet" "" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes)
\t\t\t\t(effects (font (size 1.27 1.27))))
\t\t\t(property "Description" "Diode" (at 0 0 0) (show_name no) (do_not_autoplace no) (hide yes)
\t\t\t\t(effects (font (size 1.27 1.27))))
\t\t\t(symbol "D_0_1"
\t\t\t\t(polyline (pts (xy -1.27 1.27) (xy -1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
\t\t\t\t(polyline (pts (xy 1.27 1.27) (xy 1.27 -1.27) (xy -1.27 0) (xy 1.27 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))
\t\t\t)
\t\t\t(symbol "D_1_1"
\t\t\t\t(pin passive line (at -3.81 0 0) (length 2.54)
\t\t\t\t\t(name "K" (effects (font (size 1.27 1.27))))
\t\t\t\t\t(number "1" (effects (font (size 1.27 1.27)))))
\t\t\t\t(pin passive line (at 3.81 0 180) (length 2.54)
\t\t\t\t\t(name "A" (effects (font (size 1.27 1.27))))
\t\t\t\t\t(number "2" (effects (font (size 1.27 1.27)))))
\t\t\t)
\t\t\t(embedded_fonts no)
\t\t)"""


def header(sheet_uuid, title, paper="A3"):
    return [
        "(kicad_sch",
        "\t(version 20260306)",
        '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{sheet_uuid}")',
        f'\t(paper "{paper}")',
        "\t(title_block",
        f'\t\t(title "{title}")',
        '\t\t(rev "0.1")',
        '\t\t(comment 1 "自动生成：docs/_tools/gen_matrix_sch.py")',
        "\t)",
        "\t(lib_symbols",
        SW_SYM,
        D_SYM,
        "\t)",
    ]


def footer():
    return [
        "\t(sheet_instances",
        '\t\t(path "/" (page "1"))',
        "\t)",
        "\t(embedded_fonts no)",
        ")",
    ]


def kicad_str(s):
    """把任意文本安全地放进 KiCad 的双引号字符串里。

    ⚠️ 必须同时转义反斜杠和双引号：本布局里有一个键位的标签是「|/\\」（反斜杠结尾），
    只替换双引号会生成 "...|/\\" 这种把结束引号转义掉的非法语法，
    导致 KiCad 报「加载原理图失败」。此坑已实测踩过。
    """
    return s.replace("\\", "\\\\").replace('"', '\\"')


def build_matrix_sheet_file(sheet_uuid, rows, keys, ncol):
    body = []
    sheet_keys = [k for k in keys if k["row"] in rows]
    local_rows = {r: i for i, r in enumerate(rows)}
    # 注意：不要在此处额外放「每行一个的行标签」——
    # 每个开关的 pin1 上已经贴了同名 ROW 标签，悬空的额外标签会触发 ERC
    # [label_dangling] 错误（已实测：每张子图 2 条 error）。行网络入口由
    # 后续的控制板子图负责引出。
    for k in sheet_keys:
        r, c = k["row"], k["col"]
        y = Y0 + local_rows[r] * ROW_SPACING
        xs = X0 + c * COL_SPACING
        xd = xs + 20.32
        idx = k["index"]
        nm = f"key{idx}"          # 确定性 UUID 的名字前缀（键号全局唯一）
        ref_sw, ref_d = f"SW{idx}", f"D{idx}"
        val = kicad_str(k["label"] or "Space")
        body.append(
            f'\t(symbol (lib_id "Switch:SW_Push") (at {xs:.2f} {y:.2f} 0) (unit 1)\n'
            f'\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes)\n'
            f'\t\t(uuid "{uid(nm + ":sw")}")\n'
            f'\t\t(property "Reference" "{ref_sw}" (at {xs:.2f} {y-3.81:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27))))\n'
            f'\t\t(property "Value" "{val}" (at {xs:.2f} {y+3.81:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27))))\n'
            f'\t\t(property "Footprint" "Button_Switch_Keyboard:SW_MX_Hotswap" (at {xs:.2f} {y+5.08:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(property "Datasheet" "" (at {xs:.2f} {y+5.08:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(property "Description" "Push button switch, generic, two pins" (at {xs:.2f} {y:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(pin "1" (uuid "{uid(nm + ":sw:1")}"))\n'
            f'\t\t(pin "2" (uuid "{uid(nm + ":sw:2")}"))\n'
            f'\t)'
        )
        body.append(
            f'\t(symbol (lib_id "Device:D") (at {xd:.2f} {y:.2f} 180) (unit 1)\n'
            f'\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes)\n'
            f'\t\t(uuid "{uid(nm + ":d")}")\n'
            f'\t\t(property "Reference" "{ref_d}" (at {xd:.2f} {y-2.54:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27))))\n'
            f'\t\t(property "Value" "1N4148W" (at {xd:.2f} {y+2.54:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27))))\n'
            f'\t\t(property "Footprint" "Diode_SMD:D_SOD-123" (at {xd:.2f} {y:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(property "Datasheet" "" (at {xd:.2f} {y:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(property "Description" "Diode" (at {xd:.2f} {y:.2f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'\t\t(pin "1" (uuid "{uid(nm + ":d:1")}"))\n'
            f'\t\t(pin "2" (uuid "{uid(nm + ":d:2")}"))\n'
            f'\t)'
        )
        sw_p2 = xs + 5.08
        d_a = xd - 3.81
        d_k = xd + 3.81
        # ⚠️ ROW/COL 必须是【全局标签】(global_label)，不能用局部 label：
        #    KiCad 的局部标签作用域是单张 sheet —— 三张矩阵子图的同名 COL 在真实
        #    网表里带各自的 sheet 路径前缀（如 /矩阵行 R0-R1/COL0），互不相连。
        #    这个坑曾被「单图导出 + 按名合并」的校验方式掩盖（2026-09-18 B2 时用
        #    根图整体网表证实并修复）。控制板子图也用同名全局标签接入。
        #    shape 用 passive，与 gen_power_sch.py 一致（不同 shape 同名会触发
        #    ERC [global_label_not_shape_matched]）。
        body.append(
            f'\t(global_label "ROW{r}" (shape passive) (at {xs-5.08:.2f} {y:.2f} 180)'
            f' (fields_autoplaced yes)\n'
            f'\t\t(effects (font (size 1.0 1.0)) (justify right))\n'
            f'\t\t(uuid "{uid(nm + ":lblrow")}")\n\t)'
        )
        body.append(f'\t(wire (pts (xy {sw_p2:.2f} {y:.2f}) (xy {d_a:.2f} {y:.2f}))\n'
                    f'\t\t(stroke (width 0) (type default)) (uuid "{uid(nm + ":w1")}"))')
        body.append(f'\t(wire (pts (xy {d_k:.2f} {y:.2f}) (xy {d_k+5.08:.2f} {y:.2f}))\n'
                    f'\t\t(stroke (width 0) (type default)) (uuid "{uid(nm + ":w2")}"))')
        body.append(
            f'\t(global_label "COL{c}" (shape passive) (at {d_k+5.08:.2f} {y:.2f} 0)'
            f' (fields_autoplaced yes)\n'
            f'\t\t(effects (font (size 1.0 1.0)) (justify left))\n'
            f'\t\t(uuid "{uid(nm + ":lblcol")}")\n\t)'
        )
    return header(sheet_uuid, f"StarShield {'/'.join('R'+str(r) for r in rows)}") + body + footer()


def main():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)
    try:
        matrix_schema.validate(data)
    except ValueError as e:
        sys.exit(f"[matrix.json 字段校验失败] {e}\n"
                 f"文件：{SRC}\n"
                 f"若确实新增了字段，请同步更新 docs/_tools/matrix_schema.py 的白名单，"
                 f"并明确该字段在原理图中的用途。")
    keys = data["matrix"]
    for i, k in enumerate(keys, 1):
        k["index"] = i
    ncol = data["cols"]

    os.makedirs(MATRIX_DIR, exist_ok=True)

    written = []
    for name, title, rows in SHEETS:
        p = os.path.join(MATRIX_DIR, f"{name}.kicad_sch")
        content = build_matrix_sheet_file(uid("sheet:" + name), rows, keys, ncol)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(content) + "\n")
        n = sum(1 for k in keys if k["row"] in rows)
        written.append((p, n, os.path.getsize(p)))

    # ⚠️ 根图**不在这里生成** —— 根图是「工程有哪些子图」的清单，属工程级，
    #    已拆到 docs/_tools/gen_root_sch.py（新增子图只改那一个文件）。
    # 清理历史遗留：早期版本曾把 95 键全放一张图，该文件已废弃
    stale = os.path.join(OUT_DIR, "matrix.kicad_sch")
    if os.path.exists(stale):
        os.remove(stale)
        print(f"  已删除废弃文件 {os.path.relpath(stale, ROOT)}")

    for p, n, sz in written:
        print(f"  {os.path.relpath(p, ROOT):55} {n:3} 键  {sz:8} 字节")


if __name__ == "__main__":
    main()
