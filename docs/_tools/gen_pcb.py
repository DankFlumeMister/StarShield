#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_pcb.py —— B4：由 pcb_design.py + 原理图生成 `Starshield.kicad_pcb` 与定位板

链路（改布局只改上游，不要手工改产物）：
    sketch/keyboard-layout.json ─▶ docs/_generated/matrix.json ┐
    docs/_tools/pcb_design.py  （坐标规则 / 控制肩摆放）        ├─▶ 本生成器 ─▶ Starshield.kicad_pcb
    6 张子图 .kicad_sch        （位号 / 封装 / 值 / 网表）      ┘              Starshield-plate.kicad_pcb

⚠️ 产物是「已摆位、已带网、未布线」的初始板。布线在 KiCad 里人工/交互完成；
   **布线后再跑本脚本会覆盖手动成果** —— 之后只跑 verify_pcb.py。
   文件头会写入这条警告。

为什么不用 pcbnew 脚本：KiCad Python 每次生成的 uuid/tstamp 都不同，
破坏本项目「重跑生成器 ⇒ git status 零差异」的确定性判据。
⇒ 本生成器自己拼 s-expression，uuid 由 md5(位号/路径) 派生 ⇒ 可复现。
"""
import hashlib
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import pcb_design as D

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PCB = os.path.join(ROOT, "hardware", "pcb", "StarShield")
TMP = os.path.join(PCB, "_tmp")
MATRIX = os.path.join(ROOT, "docs", "_generated", "matrix.json")

SHEETS = [
    "matrix/matrix_r012.kicad_sch",
    "matrix/matrix_r234.kicad_sch",
    "matrix/matrix_r45.kicad_sch",
    "power/power.kicad_sch",
    "control/control.kicad_sch",
    "rgb/rgb.kicad_sch",
]
ROOT_SHEET = "Starshield.kicad_sch"


# --------------------------------------------------------------------------
# 环境
# --------------------------------------------------------------------------
def find_kicad_cli():
    env = os.environ.get("KICAD_CLI")
    if env and os.path.exists(env):
        return env
    from shutil import which
    found = which("kicad-cli") or which("kicad-cli.exe")
    if found:
        return found
    import glob
    cands = []
    for drive in "CDEFGH":
        cands += glob.glob(rf"{drive}:\KiCad\bin\kicad-cli.exe")
        cands += glob.glob(rf"{drive}:\Kicad\bin\kicad-cli.exe")
        cands += glob.glob(rf"{drive}:\Program Files\KiCad\*\bin\kicad-cli.exe")
    for c in cands:
        if os.path.exists(c):
            return c
    return None


def fp_dirs():
    """先工程自带库（自画封装），再官方库。"""
    import glob
    out = [os.path.join(PCB, "footprints")]
    for drive in "CDEFGH":
        for p in glob.glob(rf"{drive}:\Kicad\share\kicad\footprints") + \
                 glob.glob(rf"{drive}:\KiCad\share\kicad\footprints") + \
                 glob.glob(rf"{drive}:\Program Files\KiCad\*\share\kicad\footprints"):
            if os.path.isdir(p):
                out.append(p)
    return out


_DIRS = fp_dirs()


def find_fp(lib, name):
    for d in _DIRS:
        p = os.path.join(d, f"{lib}.pretty", f"{name}.kicad_mod")
        if os.path.exists(p):
            return p
    return None


def uuid_for(*parts):
    h = hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def num(v):
    return f"{v:.6f}".rstrip("0").rstrip(".")


# --------------------------------------------------------------------------
# 读原理图（位号 / 封装 / 值）
# --------------------------------------------------------------------------
def collect_comps():
    out = {}
    for rel in SHEETS:
        path = os.path.join(PCB, rel)
        txt = open(path, encoding="utf-8").read()
        for blk in txt.split("\t(symbol (lib_id ")[1:]:
            m_ref = re.search(r'\(property "Reference" "([^"]+)"', blk)
            m_fp = re.search(r'\(property "Footprint" "([^"]+)"', blk)
            # ⚠️ 值可能含转义引号（键帽标签 `"` 在原理图里写作 `\"`）—— 必须按
            #    「非引号或非转义反斜杠」解析，否则会把 `\"` 截断成 `\`，
            #    写回时变成未闭合字符串，KiCad 报「未闭合的分隔字符串」（实测）。
            m_val = re.search(r'\(property "Value" "((?:[^"\\]|\\.)*)"', blk)
            if not (m_ref and m_fp and m_fp.group(1)):
                continue
            out[m_ref.group(1)] = dict(
                fp=m_fp.group(1),
                value=m_val.group(1) if m_val else "",
                sheet=rel.split("/")[0])
    return out


def export_netlist(cli):
    os.makedirs(TMP, exist_ok=True)
    out = os.path.join(TMP, "nl_root.net")
    r = subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadsexpr",
                        "-o", out, os.path.join(PCB, ROOT_SHEET)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("❌ 网表导出失败")
        print((r.stderr or "")[-600:])
        sys.exit(1)
    txt = open(out, encoding="utf-8").read()
    nets = {}
    for chunk in txt.split("(net")[1:]:
        nm = re.search(r'\(name\s+"([^"]+)"', chunk)
        if not nm:
            continue
        name = nm.group(1).lstrip("/")
        nodes = set(re.findall(r'\(ref\s+"([^"]+)"\)\s*\(pin\s+"([^"]+)"\)', chunk))
        nets.setdefault(name, set()).update(nodes)
    return nets


# --------------------------------------------------------------------------
# 摆位
# --------------------------------------------------------------------------
def placements(comps, matrix):
    """返回 {ref: (x, y, rot)}。键区由 matrix.json 派生，控制区查 CONTROL 表。"""
    keys = {e["index"]: e for e in matrix["matrix"]}
    place = {}
    for ref in comps:
        m = re.fullmatch(r"SW(\d+)", ref)
        if m and int(m.group(1)) <= 95:
            e = keys[int(m.group(1))]
            x, y = D.switch_origin(e)
            place[ref] = (x, y, 0.0)
            continue
        m = re.fullmatch(r"D(\d+)", ref)
        if m and int(m.group(1)) <= 95:
            e = keys[int(m.group(1))]
            cx, cy = D.key_center(e)
            place[ref] = (cx + D.DIODE_DX, cy + D.DIODE_DY, D.DIODE_ROT)
            continue
        m = re.fullmatch(r"LED(\d+)", ref)
        if m:
            e = keys[int(m.group(1))]
            cx, cy = D.key_center(e)
            place[ref] = (cx + D.LED_DX, cy + D.LED_DY, D.LED_ROT)
            continue
        if ref in D.CONTROL:
            place[ref] = D.CONTROL[ref]
        else:
            raise SystemExit(f"❌ 位号 {ref} 既不在键区也不在 CONTROL 表 —— "
                             f"新增元件请先在 pcb_design.py 登记")
    return place


# --------------------------------------------------------------------------
# 封装实例化（把 .kicad_mod 内联进板文件）
# --------------------------------------------------------------------------
def _pad_blocks(text):
    """生成器：产出 (start, end) 覆盖 `(pad ...)` 块（按括号配平）。

    ⚠️ 必须跳过**字符串里的括号**：键帽标签含 `(`（如 `(/9`），朴素计数会算错
    边界（verify_pcb 一侧实测因此丢掉 SW31 / LED31）。
    """
    i = 0
    n = len(text)
    while True:
        j = text.find("(pad", i)
        if j < 0:
            return
        k = j
        depth = 0
        inq = False
        esc = False
        while k < n:
            ch = text[k]
            if inq:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    inq = False
            else:
                if ch == '"':
                    inq = True
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        break
            k += 1
        yield j, k + 1
        i = k + 1


def instantiate(fp_id, ref, value, x, y, rot, netmap):
    lib, name = fp_id.split(":", 1)
    path = find_fp(lib, name)
    if not path:
        raise SystemExit(f"❌ 封装不存在：{fp_id}")
    raw = open(path, encoding="utf-8").read()

    # 去掉外层 (footprint "..." 首行、内层 (layer "...") 行、末尾 )
    head_end = raw.index("\n") + 1
    body = raw[head_end:raw.rindex(")")]
    body = re.sub(r"\n[ \t]*\(layer \"[^\"]*\"\)", "", body, count=1)
    body = "\n".join(("\t" + ln) if ln.strip() else ln for ln in body.split("\n"))

    txt = (f'\t(footprint "{fp_id}"\n'
           f'\t\t(layer "F.Cu")\n'
           f'\t\t(uuid "{uuid_for("fp", ref)}")\n'
           f'\t\t(at {num(x)} {num(y)} {num(rot)})\n'
           f'{body}\n\t)\n')

    txt = txt.replace('(property "Reference" "REF**"', f'(property "Reference" "{ref}"')
    # ⚠️ 值**原样透传**，不做额外转义：原理图里的 Value 已经是 KiCad 的转义形式
    #    （键帽标签 `"` 写作 `\"`、`\` 写作 `\\`，实测两种 KiCad 都认）。
    #    再转一次就会变成 `\\"` 之类的二重转义；且 re.sub 的替换串本身也会
    #    处理反斜杠 ⇒ 必须用 lambda，不能把值直接放进替换模板（实测踩过）。
    txt = re.sub(r'\(property "Value" "(?:[^"\\]|\\.)*"',
                 lambda _m: f'(property "Value" "{value}"', txt, count=1)

    # pad 挂网
    ins = []
    for a, b in _pad_blocks(txt):
        blk = txt[a:b]
        m = re.match(r'\(pad\s+"([^"]*)"', blk)
        if not m:
            continue
        padnum = m.group(1)
        net = netmap.get((ref, padnum))
        if net is None:
            continue
        m_uuid = re.search(r'\(uuid\s+"[^"]+"\)', blk)
        if m_uuid:
            p = a + m_uuid.end()
        else:
            p = b - 1
        ins.append((p, f' (net {net[0]} "{net[1]}")'))
    for p, s in reversed(ins):
        txt = txt[:p] + s + txt[p:]
    return txt


def hole_instance(ref, x, y):
    return instantiate(D.HOLE_FP, ref, "M2", x, y, 0.0, {})


# --------------------------------------------------------------------------
# 板文件骨架
# --------------------------------------------------------------------------
LAYERS = """	(layers
		(0 "F.Cu" signal)
		(4 "In1.Cu" signal)
		(6 "In2.Cu" signal)
		(2 "B.Cu" signal)
		(9 "F.Adhes" user "F.Adhesive")
		(11 "B.Adhes" user "B.Adhesive")
		(13 "F.Paste" user)
		(15 "B.Paste" user)
		(5 "F.SilkS" user)
		(7 "B.SilkS" user)
		(1 "F.Mask" user)
		(3 "B.Mask" user)
		(17 "Dwgs.User" user "User.Drawings")
		(19 "Cmts.User" user "User.Comments")
		(21 "Eco1.User" user "User.Eco1")
		(23 "Eco2.User" user "User.Eco2")
		(25 "Edge.Cuts" user)
		(27 "Margin" user)
		(31 "F.CrtYd" user "F.Courtyard")
		(29 "B.CrtYd" user "B.Courtyard")
		(35 "F.Fab" user)
		(33 "B.Fab" user)
	)"""

# 层叠（2026-09-20 补）：**必须写出来**，否则铜厚只存在于厂家默认值里，
# DRC 的载流相关检查与「内层到底多厚」都无从谈起（见 research/power-trace-width-precedent.md）。
# 参数来源（都是一手样例，不是猜的）：
#   - 结构与写法照抄社区 4 层板 `ScottoModules`（内层 1 oz）与 `Conejo`（JLC 默认内层 0.0152）；
#     两者都实际投过板。
#   - 本板**声明内层 1 oz（0.035）** —— 灯轨峰值 2.4 A 需要它
#     （0.5 oz 内层下 2.4 A 需 3.43 mm 走线，不现实；1 oz 下 1.5 mm 即可 ≈2.24 A）。
#   - ⚠️ 语法（官方文档 file-formats/sexpr-pcb）：**`(stackup)` 必须放在 `(setup)` 段内部**，
#     不能放板级 —— 板级写法是 KiCad 5 的旧格式，KiCad 10 会直接报「未知标记 stackup」并拒绝加载。
#     （社区样本 Conejo / ScottoModules 是老版本文件，不能照抄它们的位置。）
#   - ⚠️ 下单时必须向厂家**明确指定内层 1 oz**；若厂家只给默认的 0.5 oz，
#     加宽后的 1.5 mm 走线仍可覆盖固件护栏电流 1.0 A（0.5 oz 下 ≈1.35 A @ΔT20），但覆盖不了峰值。
STACKUP = """	(stackup
		(layer "F.SilkS" (type "Top Silk Screen"))
		(layer "F.Paste" (type "Top Solder Paste"))
		(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
		(layer "F.Cu" (type "copper") (thickness 0.035))
		(layer "dielectric 1" (type "prepreg") (thickness 0.1) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
		(layer "In1.Cu" (type "copper") (thickness 0.0152))
		(layer "dielectric 2" (type "core") (thickness 1.24) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
		(layer "In2.Cu" (type "copper") (thickness 0.0152))
		(layer "dielectric 3" (type "prepreg") (thickness 0.1) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
		(layer "B.Cu" (type "copper") (thickness 0.035))
		(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
		(layer "B.Paste" (type "Bottom Solder Paste"))
		(layer "B.SilkS" (type "Bottom Silk Screen"))
		(copper_finish "None")
		(dielectric_constraints no)
	)"""
# ⚠️ **4 层板（2026-09-19 用户定）**：
#    - 层号与顺序**照抄 KiCad 自己写出来的形式**（不是按惯例猜）：`B.Cu` 的 id 是 **2**、不是 31；
#      `In1.Cu`=4、`In2.Cu`=6。KiCad 也会把 F.SilkS/B.SilkS 的别名串去掉 —— 一并照抄。
#    - **不要用 MCP `add_layer` 加层**：层数属设计数据，必须由生成器产出，
#      否则下一次 `gen_pcb.py` 会把内层覆盖掉（本轮实测踩过）。
#    - 叠层规划：**In1.Cu = GND 平面、In2.Cu = VLED 平面**，两个外层放信号；
#      VLED 的 2.4 A 靠 In2 平面承载（见 handoff §9 B4）。


def header(title, w, h, note):
    return f"""(kicad_pcb
	(version 20260206)
	(generator "gen_pcb.py")
	(generator_version "1.0")
	(general
		(thickness 1.6)
		(legacy_teardrops no)
	)
	(paper "A4")
	(title_block
		(title "{title}")
		(comment 1 "{note}")
	)
{LAYERS}
	(setup
{STACKUP}
		(pad_to_mask_clearance 0)
		(allow_soldermask_bridges_in_footprints no)
		(tenting front back)
		(aux_axis_origin 0 0)
		(grid_origin 0 0)
		(pcbplotparams
			(layerselection 0x00000000_00000000_00000000_000000a5)
			(usegerberextensions no)
			(usegerberattributes yes)
			(svgprecision 6)
			(plotframeref no)
			(mode 1)
			(useauxorigin no)
		)
	)
"""


def net_class_block(cls_names, all_nets):
    # ⚠️ 语法实测（KiCad 10.0.6，用 kicad-cli pcb drc 逐个变体试出来的）：
    #    ① net_class 是**板级**条目，放 (setup) 里会报「意外 net_class」；
    #    ② 名字后**必须跟一个描述字符串**，否则报「应为 'symbol'」；
    #    ③ 字段名是 via_dia / via_drill / uvia_dia / uvia_drill（**不是**
    #       via_diameter）—— 写错时会明确列出可用字段，本注释即据此修正；
    #    ④ 归属用 (add_net "...") —— 本版本支持，故 VLED 的加宽是**文件内生效**的。
    desc = {
        "Default": "默认类（信号 / 矩阵行列 / LED 数据链）",
        "Power": "电源轨 OUT / VBUS / VCHG_IN / VBAT（≤1.5 A）",
        "VLED": "RGB 灯珠供电：峰值 2.4 A（ADR-0007 电池直供）⇒ 必须宽走线或铺铜",
    }
    special = set(D.POWER_NETS) | {"VLED"}
    out = []
    for name in cls_names:
        c = D.NET_CLASSES[name]
        if name == "VLED":
            members = ["VLED"]
        elif name == "Power":
            members = sorted(D.POWER_NETS)
        else:
            members = [n for n in all_nets if n not in special]
        add = "".join(f'\n\t\t(add_net "{n}")' for n in members)
        out.append(
            f'	(net_class "{name}" "{desc.get(name, name)}"\n'
            f'		(clearance {c["clearance"]})\n'
            f'		(trace_width {c["trace_width"]})\n'
            f'		(via_dia {c["via_diameter"]})\n'
            f'		(via_drill {c["via_drill"]})\n'
            f'		(uvia_dia 0.3)\n'
            f'		(uvia_drill 0.1)\n'
            f'{add}\n'
            f'	)')
    return "\n".join(out) + "\n"


def outline(x0, y0, w, h):
    pts = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h), (x0, y0)]
    s = []
    for i in range(4):
        a, b = pts[i], pts[i + 1]
        s.append(f"	(gr_line (start {num(a[0])} {num(a[1])}) (end {num(b[0])} {num(b[1])})"
                 f' (stroke (width 0.1) (type solid)) (layer "Edge.Cuts")'
                 f' (uuid "{uuid_for("edge", str(i), num(a[0]), num(a[1]))}"))')
    return "\n".join(s) + "\n"


def plate_cutout(ref, x, y, size):
    u1 = uuid_for("platecut", ref)
    u2 = uuid_for("platecutpad", ref)
    return (f'	(footprint "StarShield:Plate_Cutout_MX_{num(size)}mm"\n'
            f'		(layer "F.Cu")\n'
            f'		(uuid "{u1}")\n'
            f'		(at {num(x)} {num(y)} 0)\n'
            f'		(property "Reference" "{ref}"\n'
            f'			(at 0 0 0)\n'
            f'			(layer "F.SilkS")\n'
            f'			(hide yes)\n'
            f'			(uuid "{uuid_for("platecutref", ref)}")\n'
            f'			(effects (font (size 1 1) (thickness 0.15)))\n'
            f'		)\n'
            f'		(pad "" np_thru_hole rect\n'
            f'			(at 0 0 0)\n'
            f'			(size {num(size)} {num(size)})\n'
            f'			(drill {num(size)} {num(size)})\n'
            f'			(layers "*.Cu" "*.Mask")\n'
            f'			(uuid "{u2}")\n'
            f'		)\n'
            f'	)\n')


# --------------------------------------------------------------------------
def main():
    cli = find_kicad_cli()
    if not cli:
        print("❌ 找不到 kicad-cli")
        return 2
    matrix = D.load_matrix(ROOT)
    comps = collect_comps()
    nets = export_netlist(cli)

    # 网编号：0 = 未连接，其余按名字排序稳定编号
    names = sorted(n for n in nets if n and not n.startswith("unconnected"))
    net_no = {n: i + 1 for i, n in enumerate(names)}
    netmap = {}
    for n, nodes in nets.items():
        if n.startswith("unconnected"):
            continue
        for ref, pin in nodes:
            netmap[(ref, pin)] = (net_no[n], n)

    place = placements(comps, matrix)

    parts = [header("StarShield 95-key wireless",
                    D.BOARD_W, D.BOARD_H,
                    "由 docs/_tools/gen_pcb.py 生成 —— 布线后请勿重跑（会覆盖手动成果）"),
             net_class_block(["Default", "Power", "VLED"], names),
             '	(net 0 "")\n']
    for n in names:
        parts.append(f'	(net {net_no[n]} "{n}")\n')

    parts.append(outline(0, 0, D.BOARD_W, D.BOARD_H))
    for ref in sorted(comps, key=lambda r: (len(r), r)):
        x, y, rot = place[ref]
        parts.append(instantiate(comps[ref]["fp"], ref, comps[ref]["value"], x, y, rot, netmap))
    for ref, x, y in D.HOLES:
        parts.append(hole_instance(ref, x, y))
    parts.append("	(embedded_fonts no)\n)\n")

    dst = os.path.join(PCB, "Starshield.kicad_pcb")
    open(dst, "w", encoding="utf-8", newline="\n").write("".join(parts))

    # ---- 定位板（G6）-------------------------------------------------------
    keys = {e["index"]: e for e in matrix["matrix"]}
    pl = [header("StarShield plate",
                 D.PLATE_W, D.PLATE_H,
                 "定位板：与 PCB 同源生成，开孔 14x14 mm；PCB-mount 卫星轴 ⇒ 无需卫星轴开孔"),
          net_class_block(["Default"], []),
          outline(D.PLATE_X0, D.PLATE_Y0, D.PLATE_W, D.PLATE_H)]
    for i in sorted(keys):
        cx, cy = D.key_center(keys[i])
        pl.append(plate_cutout(f"P{i}", cx, cy, D.PLATE_CUTOUT))
    for ref, x, y in D.HOLES:
        pl.append(hole_instance(ref, x, y))
    pl.append("	(embedded_fonts no)\n)\n")
    pdst = os.path.join(PCB, "Starshield-plate.kicad_pcb")
    open(pdst, "w", encoding="utf-8", newline="\n").write("".join(pl))

    import shutil
    shutil.rmtree(TMP, ignore_errors=True)

    print(f"  {os.path.relpath(dst, ROOT)}        {os.path.getsize(dst)} 字节")
    print(f"  {os.path.relpath(pdst, ROOT)}  {os.path.getsize(pdst)} 字节")
    print(f"  元件 {len(comps)} 个 + 安装孔 {len(D.HOLES)} 个 + 网 {len(names)} 条")
    print(f"  板框 {num(D.BOARD_W)} × {num(D.BOARD_H)} mm（键区 {num(D.KEY_W)} × {num(D.KEY_H)}"
          f"，顶部控制肩 {num(D.SHELF_H)} mm）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
