#!/usr/bin/env python3
"""gen_power_sch.py —— 由 power_design.py 生成电源子图原理图

输入：docs/_tools/power_design.py（电路数据）+ docs/_tools/power_symbols.json（符号定义）
输出：hardware/pcb/StarShield/power/power.kicad_sch

画法约定（为什么这样画）：
1. **每个引脚 = 一根 2.54 mm 短线 + 一个标签**，不画长走线。
   理由：本项目是**生成的**原理图，长走线需要人工避让、极易出现交叉/压符号，
   而「短线 + 同名标签」让连通性由网名决定，几何错误就不再等于电气错误。
   代价：图面不像手绘原理图那样一目了然；正确性由 verify_power.py 的网表断言兜底。
2. GND 用 `power:GND` 电源符号；跨子图的电源/信号（VBUS/OUT/VLED/RGB_PWR_EN）用**全局标签**；
   其余用局部标签。这样 B2 控制板子图沿用同名即可接上，无需层次化引脚。
3. 引脚坐标**从符号定义里算**（不是手抄）：symbol_pin(ref, num) 用符号自身的
   `(pin ... (at x y ang) (length L))` 加上实例原点换算，杜绝手算错位。
4. UUID 用 uuid5 从稳定名字串生成 ⇒ 重复运行产出**逐字节一致**的文件。
   与 gen_matrix_sch.py 共用同一个命名空间常量。
"""
import json
import os
import re
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import power_design as D  # noqa: E402

# 确定性 UUID：与 gen_matrix_sch.py 用同一个命名空间，保证跨生成器不撞名。
NS = uuid.UUID("6f1a4d2e-8b3c-4f5a-9e7d-1c2b3a4d5e6f")
_CACHE = {}


def uid(name):
    if name not in _CACHE:
        _CACHE[name] = str(uuid.uuid5(NS, "power:" + name))
    return _CACHE[name]


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SYMFILE = os.path.join(ROOT, "docs", "_tools", "power_symbols.json")
OUT_DIR = os.path.join(ROOT, "hardware", "pcb", "StarShield", "power")
OUT = os.path.join(OUT_DIR, "power.kicad_sch")

STUB = 2.54     # 引脚引出的短线长度
GRID = 1.27     # 设计网格


def kicad_str(s):
    """把任意文本安全地放进 KiCad 双引号字符串（反斜杠与双引号都要转义）。"""
    return s.replace("\\", "\\\\").replace('"', '\\"')


# ---------------------------------------------------------------------------
# 符号库：读 power_symbols.json，并把每个符号的引脚几何解出来
# ---------------------------------------------------------------------------
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

# 元件索引
COMP = {c["ref"]: c for c in D.COMPONENTS}


def pin_pos(ref, num):
    """引脚连接点在原理图坐标系里的绝对坐标。

    KiCad 符号库的 Y 轴向上、原理图 Y 轴向下 ⇒ 库坐标 (px, py) 对应原理图偏移 (px, -py)。
    rot != 0 时再做旋转（当前所有元件 rot=0，GND 电源符号的引脚就在原点，故不受旋转影响）。
    """
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
    """引脚连接点朝外（背离元件本体）的单位方向，用于决定短线走向。"""
    lib = COMP[ref]["lib"]
    px, py, ang = PINS[lib][num]
    a = (ang + 180) % 360
    dx, dy = {0: (1.0, 0.0), 90: (0.0, 1.0), 180: (-1.0, 0.0), 270: (0.0, -1.0)}[int(a)]
    return (dx, -dy)     # 库→原理图 Y 翻转


def offset(p, d, n):
    return (round(p[0] + d[0] * n, 4), round(p[1] + d[1] * n, 4))


# 标签/电源符号的朝向：以「短线朝外方向」为准
def label_angle(d):
    return {(1.0, 0.0): 0, (-1.0, 0.0): 180, (0.0, 1.0): 270, (0.0, -1.0): 90}[d]


def gnd_rot(d):
    """GND 符号的引脚就在原点 ⇒ 旋转只影响外观，不影响连通性。"""
    return {(0.0, 1.0): 0, (0.0, -1.0): 180, (-1.0, 0.0): 270, (1.0, 0.0): 90}[d]


# ---------------------------------------------------------------------------
# 输出构件
# ---------------------------------------------------------------------------
def lib_symbols_block(used):
    """输出 lib_symbols 缓存块。

    ⚠️ 关键坑（已实测）：`lib_symbols` 里的条目名必须是 `库名:符号名`（与实例的 lib_id 一致），
    而 power_symbols.json 里存的是库文件的原始文本，名字是**裸符号名**。
    只给第一个 `(symbol "` 加库前缀 —— 子单元（如 `R_0_1`）**不能**加前缀，否则 KiCad 解析单元失败。
    漏加前缀的症状极具误导性：KiCad 认不出任何引脚 ⇒ 所有引脚被当成同一个点、
    `pintype` 全部退化成 unspecified、每个元件自成一个网络 —— 看起来像「全部悬空」，
    而真实原因是符号名对不上。
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
    lines.append(f'\t\t(property "Reference" "{kicad_str(ref)}" (at {x} {round(y - 5.08, 4)} 0)'
                 f'\n\t\t\t(effects (font (size 1.27 1.27)){hide}))')
    lines.append(f'\t\t(property "Value" "{kicad_str(value)}" (at {x} {round(y + 5.08, 4)} 0)'
                 f'\n\t\t\t(effects (font (size 1.27 1.27)){hide}))')
    lines.append(f'\t\t(property "Footprint" "{kicad_str(fp)}" (at {x} {y} 0)'
                 f'\n\t\t\t(effects (font (size 1.27 1.27)) (hide yes)))')
    lines.append(f'\t\t(property "Datasheet" "" (at {x} {y} 0)'
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


# ---------------------------------------------------------------------------
# 装配
# ---------------------------------------------------------------------------
def build():
    body, problems = [], []

    # 1) 引脚连接表 + 按「坐标+网名」去重（U1 的 2/3、8/17、J1 的四组同名引脚都stacked）
    entries = []          # (pos, dir, net, ref, num)
    pin_at = {}           # pos -> net（用于撞点检查）
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
        if net == "GND":
            body.append("\n".join(sym_inst("power:GND", end, gnd_rot(d), GND_REF.pop(),
                                           "GND", "", {}, f"gnd:{nm}", ref_hidden=True, pins=("1",))))
        elif net in D.GLOBAL_NETS:
            body.append(global_label(net, end, label_angle(d)))
        else:
            body.append(label(net, end, label_angle(d)))

    # 2) PWR_FLAG（同点引脚自动相连，无需额外拉线）
    for i, f in enumerate(D.PWR_FLAGS, 1):
        at, net = f["at"], f["net"]
        body.append("\n".join(sym_inst("power:PWR_FLAG", at, 0, f"#FLG0{i}",
                                       "PWR_FLAG", "", {}, f"flag:{net}", ref_hidden=True,
                                       pins=("1",))))
        if net == "GND":
            body.append("\n".join(sym_inst("power:GND", at, 0, GND_REF.pop(),
                                           "GND", "", {}, f"flaggnd:{net}", ref_hidden=True,
                                           pins=("1",))))
        else:
            body.append(global_label(net, at, 90))

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


# GND 电源符号的位号池（ERC 要求 #PWR 位号唯一）
GND_REF = [f"#PWR0{i:02d}" for i in range(1, 200)]


def header():
    return [
        "(kicad_sch",
        "\t(version 20260306)",
        '\t(generator "eeschema")',
        '\t(generator_version "10.0")',
        f'\t(uuid "{uid("sheet:power")}")',
        f'\t(paper "{D.PAPER}")',
        "\t(title_block",
        f'\t\t(title "{kicad_str(D.SHEET_TITLE)}")',
        '\t\t(rev "0.1")',
        '\t\t(comment 1 "自动生成：docs/_tools/gen_power_sch.py（数据源 docs/_tools/power_design.py）")',
        "\t)",
    ]


def footer():
    return ["\t(sheet_instances", '\t\t(path "/" (page "1"))', "\t)", "\t(embedded_fonts no)", ")"]


def main():
    used = sorted({c["lib"] for c in D.COMPONENTS}) + ["power:GND", "power:PWR_FLAG"]

    body, problems = build()
    lines = header() + lib_symbols_block(used) + body + footer()

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(f"  {os.path.relpath(OUT, ROOT):58} {os.path.getsize(OUT):8} 字节")
    print(f"  元件 {len(D.COMPONENTS)} 个 / 引脚连接 {len(D.CONN)} 条 / 图形文字 {len(D.NOTES)} 条")
    if problems:
        print("\n⚠️ 版式检查发现问题（连通性仍由 verify_power.py 断言兜底）：")
        for p in problems:
            print("   -", p)
        return 1
    print("✅ 版式自检通过：无「同点不同网」/「短线终点撞网」")
    return 0


if __name__ == "__main__":
    sys.exit(main())
