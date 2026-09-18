#!/usr/bin/env python3
"""gen_control_sch.py —— 由 control_design.py 生成控制板子图原理图

输入：docs/_tools/control_design.py（电路数据）+ docs/_tools/power_symbols.json（符号缓存）
输出：hardware/pcb/StarShield/control/control.kicad_sch

画法约定与 gen_power_sch.py 完全一致（不要另起一套）：
1. 每个引脚 = 一根 2.54 mm 短线 + 一个标签，连通性由网名决定；
2. GND/VCC 用 power 符号；跨子图网（OUT/RGB_PWR_EN/ROW/COL/LED_DIN）用全局标签；
   其余用局部标签；
3. 引脚坐标从符号定义里算（symbol_pin），不手抄；
4. UUID 用 uuid5 从稳定名字串生成 ⇒ 重复运行产出逐字节一致的文件。
"""
import json
import os
import re
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import control_design as D  # noqa: E402

# 确定性 UUID：与矩阵/电源/根图同一命名空间
NS = uuid.UUID("6f1a4d2e-8b3c-4f5a-9e7d-1c2b3a4d5e6f")
_CACHE = {}


def uid(name):
    if name not in _CACHE:
        # ⚠️ 前缀 "control:" —— 与电源子图的 "power:" 平级，保证跨生成器不撞名
        _CACHE[name] = str(uuid.uuid5(NS, "control:" + name))
    return _CACHE[name]


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SYMFILE = os.path.join(ROOT, "docs", "_tools", "power_symbols.json")
OUT_DIR = os.path.join(ROOT, "hardware", "pcb", "StarShield", "control")
OUT = os.path.join(OUT_DIR, "control.kicad_sch")

STUB = 2.54


def kicad_str(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def load_symbols():
    with open(SYMFILE, encoding="utf-8") as f:
        data = json.load(f)
    syms = data["symbols"]
    pins = {}
    for key, txt in syms.items():
        m = {}
        for pm in re.finditer(
                r"\(pin\s+([a-z_]+)\s+\w+\s*\(at\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\)"
                r"\s*\(length\s+([\d.]+)\)", txt):
            seg = txt[pm.end():pm.end() + 400]
            num = re.search(r'\(number "([^"]+)"', seg)
            if not num:
                continue
            m[num.group(1)] = (float(pm.group(2)), float(pm.group(3)), float(pm.group(4)))
        pins[key] = m
    return data, syms, pins


META, SYMS, PINS = load_symbols()
COMP = {c["ref"]: c for c in D.COMPONENTS}


def pin_pos(ref, num):
    c = COMP[ref]
    table = PINS[c["lib"]]
    if num not in table:
        raise KeyError(f"{ref} ({c['lib']}) 没有引脚 {num}；可用：{sorted(table)}")
    px, py, ang = table[num]
    ox, oy = c["at"]
    rot = c.get("rot", 0) % 360
    if rot == 0:
        fx, fy = px, -py
    elif rot == 90:
        fx, fy = -py, -px
    elif rot == 180:
        fx, fy = -px, py
    else:
        fx, fy = py, px
    return (round(ox + fx, 4), round(oy + fy, 4))


def pin_dir(ref, num):
    lib = COMP[ref]["lib"]
    px, py, ang = PINS[lib][num]
    a = (ang + 180) % 360
    dx, dy = {0: (1.0, 0.0), 90: (0.0, 1.0), 180: (-1.0, 0.0), 270: (0.0, -1.0)}[int(a)]
    return (dx, -dy)


def offset(p, d, n):
    return (round(p[0] + d[0] * n, 4), round(p[1] + d[1] * n, 4))


def label_angle(d):
    return {(1.0, 0.0): 0, (-1.0, 0.0): 180, (0.0, 1.0): 270, (0.0, -1.0): 90}[d]


def gnd_rot(d):
    return {(0.0, 1.0): 0, (0.0, -1.0): 180, (-1.0, 0.0): 270, (1.0, 0.0): 90}[d]


# power 符号网名 → 符号 lib_id（GND / VCC 直接用 power 符号，别的网用标签）
POWER_SYMS = {"GND": "power:GND", "VCC": "power:VCC"}


def lib_symbols_block(used):
    """输出 lib_symbols 缓存块。

    ⚠️ 条目名必须是 `库名:符号名`（只给第一个 (symbol " 加前缀，子单元不加）——
    见 gen_power_sch.py 的同函数注释（漏加前缀 = 全部引脚认不出的静默灾难）。
    """
    out = ["\t(lib_symbols"]
    for key in used:
        lib = key.split(":")[0]
        txt = SYMS[key].replace('(symbol "', '(symbol "%s:' % lib, 1)
        for line in txt.split("\n"):
            out.append("\t" + line)
    out.append("\t)")
    return out


def sym_inst(lib, at, rot, ref, value, fp, extra, name, ref_hidden=False, pins=()):
    x, y = at
    lines = [
        f'\t(symbol (lib_id "{lib}") (at {x} {y} {rot}) (unit 1)',
        "\t\t(exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes)",
        f'\t\t(uuid "{uid(name)}")',
    ]
    hide = " (hide yes)" if ref_hidden else ""
    lines.append(f'\t(property "Reference" "{kicad_str(ref)}" (at {x} {round(y - 5.08, 4)} 0)'
                 f'\n\t\t\t(effects (font (size 1.27 1.27)){hide}))')
    lines.append(f'\t(property "Value" "{kicad_str(value)}" (at {x} {round(y + 5.08, 4)} 0)'
                 f'\n\t\t\t(effects (font (size 1.27 1.27)){hide}))')
    lines.append(f'\t(property "Footprint" "{kicad_str(fp)}" (at {x} {y} 0)'
                 f'\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes)))')
    lines.append(f'\t(property "Datasheet" "" (at {x} {y} 0)'
                 f'\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes)))')
    for k, v in extra.items():
        lines.append(f'\t\t(property "{kicad_str(k)}" "{kicad_str(v)}" (at {x} {y} 0)'
                     f'\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes)))')
    for pn in pins:
        lines.append(f'\t\t(pin "{pn}" (uuid "{uid(name + ":p" + pn)}"))')
    lines.append("\t)")
    return lines


def wire(p1, p2, name):
    return (f'\t(wire (pts (xy {p1[0]} {p1[1]}) (xy {p2[0]} {p2[1]}))\n'
            f'\t\t(stroke (width 0) (type default)) (uuid "{uid(name)}"))')


def label(net, at, ang):
    just = {0: "left", 180: "right", 90: "left", 270: "right"}[ang]
    return (f'\t(label "{kicad_str(net)}" (at {at[0]} {at[1]} {ang}) (fields_autoplaced yes)\n'
            f'\t\t(effects (font (size 1.27 1.27)) (justify {just} bottom))\n'
            f'\t\t(uuid "{uid("lbl:" + net + ":" + str(at))}")\n\t)')


def global_label(net, at, ang):
    just = {0: "left", 180: "right", 90: "left", 270: "right"}[ang]
    return (f'\t(global_label "{kicad_str(net)}" (shape passive) (at {at[0]} {at[1]} {ang})'
            f' (fields_autoplaced yes)\n'
            f'\t\t(effects (font (size 1.27 1.27)) (justify {just}))\n'
            f'\t\t(uuid "{uid("glbl:" + net + ":" + str(at))}")\n\t)')


def no_connect(at, name):
    return f'\t(no_connect (at {at[0]} {at[1]}) (uuid "{uid("nc:" + name)}"))'


def text_note(at, s):
    return (f'\t(text "{kicad_str(s)}" (exclude_from_sim no) (at {at[0]} {at[1]} 0)\n'
            f'\t\t(effects (font (size 1.27 1.27)) (justify left bottom))\n'
            f'\t\t(uuid "{uid("note:" + str(at))}"))')


# GND/VCC 电源符号的位号池（与电源子图错开：电源子图用 #PWR01xx 顺序，
# 本子图独立成图，位号唯一性由 KiCad 按图管理，但保险起见用高位段）
GND_REF = [f"#PWR02{i:02d}" for i in range(1, 200)]


def build():
    body, problems = [], []

    # 1) 引脚连接表（按「坐标+网名」去重 + 撞点检查，同 gen_power_sch.py）
    entries = []
    pin_at = {}
    for key, net in D.CONN.items():
        ref, num = key.rsplit(".", 1)
        if ref not in COMP:
            problems.append(f"连接表里的位号 {ref} 不在元件表中")
            continue
        p, d = pin_pos(ref, num), pin_dir(ref, num)
        entries.append((p, d, net, ref, num))
        if p in pin_at and pin_at[p] != net:
            problems.append(f"同一坐标 {p} 被两个不同网络占用：{pin_at[p]} / {net}（{ref}.{num}）")
        pin_at[p] = net

    seen = set()
    for p, d, net, ref, num in entries:
        if (p, net) in seen:
            continue
        seen.add((p, net))
        nm = f"{ref}.{num}"
        if net is None:
            body.append(no_connect(p, nm))
            continue
        end = offset(p, d, STUB)
        if end in pin_at and pin_at[end] != net:
            problems.append(f"{nm} 的短线终点 {end} 撞到网络 {pin_at[end]}")
        body.append(wire(p, end, f"w:{nm}"))
        if net in POWER_SYMS:
            lib = POWER_SYMS[net]
            body.append("\n".join(sym_inst(lib, end, gnd_rot(d), GND_REF.pop(),
                                           net, "", {}, f"pwr:{nm}", ref_hidden=True,
                                           pins=("1",))))
        elif net in D.GLOBAL_NETS:
            body.append(global_label(net, end, label_angle(d)))
        else:
            body.append(label(net, end, label_angle(d)))

    # 2) PWR_FLAG（VCC）
    for f in D.PWR_FLAGS:
        at, net = f["at"], f["net"]
        body.append("\n".join(sym_inst("power:PWR_FLAG", at, 0, "#FLG01",
                                       "PWR_FLAG", "", {}, f"flag:{net}", ref_hidden=True,
                                       pins=("1",))))
        if net in POWER_SYMS:
            lib = POWER_SYMS[net]
            body.append("\n".join(sym_inst(lib, at, 0, GND_REF.pop(),
                                           net, "", {}, f"flagpwr:{net}", ref_hidden=True,
                                           pins=("1",))))
        else:
            body.append(global_label(net, at, 90) if net in D.GLOBAL_NETS
                        else label(net, at, 90))

    # 3) 元件符号
    for c in D.COMPONENTS:
        key = c["lib"]
        nums = sorted(PINS[key], key=lambda s: (len(s), s))
        body.append("\n".join(sym_inst(key, c["at"], c.get("rot", 0), c["ref"], c["value"],
                                       c["fp"], c.get("props", {}), f"comp:{c['ref']}",
                                       pins=nums)))

    # 4) 图面文字
    for nx, ny, s in D.NOTES:
        body.append(text_note((nx, ny), s))

    return body, problems


def header():
    return [
        "(kicad_sch",
        "\t(version 20260306)",
        '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{uid("sheet:control")}")',
        f'\t(paper "{D.PAPER}")',
        "\t(title_block",
        f'\t\t(title "{kicad_str(D.SHEET_TITLE)}")',
        '\t\t(rev "0.1")',
        '\t\t(comment 1 "自动生成：docs/_tools/gen_control_sch.py（数据源 docs/_tools/control_design.py）")',
        "\t)",
    ]


def footer():
    return ["\t(sheet_instances", '\t\t(path "/" (page "1"))', "\t)", "\t(embedded_fonts no)", ")"]


def main():
    used = sorted({c["lib"] for c in D.COMPONENTS}
                  | {"power:GND", "power:VCC", "power:PWR_FLAG"})

    body, problems = build()
    lines = header() + lib_symbols_block(used) + body + footer()

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(f"  {os.path.relpath(OUT, ROOT):58} {os.path.getsize(OUT):8} 字节")
    print(f"  元件 {len(D.COMPONENTS)} 个 / 引脚连接 {len(D.CONN)} 条 / 图形文字 {len(D.NOTES)} 条")
    if problems:
        print("\n⚠️ 版式检查发现问题（连通性仍由 verify_control.py 断言兜底）：")
        for p in problems:
            print("   -", p)
        return 1
    print("✅ 版式自检通过：无「同点不同网」/「短线终点撞网」")
    return 0


if __name__ == "__main__":
    sys.exit(main())
