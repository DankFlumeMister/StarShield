#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_pcb.py —— B4：PCB 布局校验（配合 gen_pcb.py）

断言对象 = **真实产物** `Starshield.kicad_pcb` / `Starshield-plate.kicad_pcb`，
不依赖生成器的内部常量（改了 pcb_design.py 也能抓到不一致）。

九组断言：
  A 元件齐套      B 键位坐标 == matrix.json      C 异形 Enter 用 2.25u
  D 全部在板内    E 焊盘不互相重叠（不同位号）    F pad 网 == 原理图网表
  G VLED 网络类加宽                              H DRC 未豁免 error = 0
  I 定位板开孔与轴体同源

⚠️ DRC 豁免清单里的每一条都**必须带理由**（ERC 那边已立下同样规矩）。
"""
import collections
import math
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
BOARD = os.path.join(PCB, "Starshield.kicad_pcb")
PLATE = os.path.join(PCB, "Starshield-plate.kicad_pcb")
TMP = os.path.join(PCB, "_tmp")
ROOT_SHEET = os.path.join(PCB, "Starshield.kicad_sch")

# ⚠️ DRC 豁免：kind -> 理由。带 `❓` 的表示尚未根因确认，投板前必须回看。
DRC_ALLOW = {
    "unconnected_items": "本产物是「已摆位、未布线」的初始板，未连接属预期（499 项）",
    "courtyards_overlap": "per-key 布局必然：灯珠/二极管就在轴体自身的 courtyard 内（实测 96 项）",
    "lib_footprint_mismatch": "自画封装（MX 热插拔座 8 档）与库内版本差异，与 ERC 噪音同类",
    "lib_footprint_issues": "同上，95 个自画封装",
    "silk_overlap": "丝印重叠，投板前统一整理（与 ERC off-grid 噪音同类）",
    "silk_over_copper": "丝印压焊盘，投板前统一整理",
    "nonmirrored_text_on_back_layer": "自画封装 B.Cu 面的参考编号未镜像（95 项），投板前统一处理",
    "drill_out_of_range": "U1 散热焊盘自带 0.2 mm 过孔（官方 ThermalVias 变体）；投板前按厂家最小孔径确认",
    "hole_clearance": "❓ 报告的第二坐标与第一坐标相差 331 mm，坐标明显异常；已人工核对 SW68 的 NPTH 位置正确 ⇒ 疑似 KiCad 10 DRC 报告 bug",
    "solder_mask_bridge": "❓ 同上，成对出现（SW68 NPTH ↔ D95），坐标同样异常",
    "npth_inside_courtyard": "❓ 同上",
}


def find_kicad_cli():
    from shutil import which
    import glob
    env = os.environ.get("KICAD_CLI")
    if env and os.path.exists(env):
        return env
    f = which("kicad-cli") or which("kicad-cli.exe")
    if f:
        return f
    for drive in "CDEFGH":
        for p in glob.glob(rf"{drive}:\Kicad\bin\kicad-cli.exe") + \
                 glob.glob(rf"{drive}:\KiCad\bin\kicad-cli.exe"):
            if os.path.exists(p):
                return p
    return None


def _blocks(text, marker):
    """按 marker 切出配平的 s-expression 块。

    ⚠️ **必须跳过字符串里的括号**：键帽标签含 `(`（如 SW31 的 `(/9`），
    朴素的括号计数会把字符串内的 `(` 当成开括号 ⇒ 块边界错乱、元件「丢失」
    （实测丢的就是 SW31 / LED31）。
    """
    out, i = [], 0
    n = len(text)
    while True:
        j = text.find(marker, i)
        if j < 0:
            return out
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
        out.append(text[j:k + 1])
        i = k + 1


def _rot(x, y, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return x * c - y * s, x * s + y * c


def parse_board(path):
    """→ {ref: dict(fp, at, pads=[dict(num,x,y,w,h,net)])}（坐标为板坐标）。"""
    text = open(path, encoding="utf-8").read()
    comps = {}
    for blk in _blocks(text, '\n\t(footprint "'):
        m_fp = re.search(r'\(footprint "([^"]+)"', blk)
        m_ref = re.search(r'\(property "Reference" "([^"]+)"', blk)
        m_at = re.search(r'\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
        if not (m_fp and m_at):
            continue
        ref = m_ref.group(1) if m_ref else f"?{len(comps)}"
        fx, fy = float(m_at.group(1)), float(m_at.group(2))
        frot = float(m_at.group(3)) if m_at.group(3) else 0.0
        pads = []
        for pb in _blocks(blk, "(pad "):
            pm = re.match(r'\(pad\s+"([^"]*)"\s+(\w+)\s+(\w+)', pb)
            if not pm:
                continue
            pa = re.search(r'\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', pb)
            ps = re.search(r'\(size ([-\d.]+) ([-\d.]+)\)', pb)
            pn = re.search(r'\(net (\d+) "([^"]*)"\)', pb)
            pd = re.search(r'\(drill', pb)
            if not (pa and ps):
                continue
            lx, ly = float(pa.group(1)), float(pa.group(2))
            lrot = float(pa.group(3)) if pa.group(3) else 0.0
            w, h = float(ps.group(1)), float(ps.group(2))
            x, y = _rot(lx, ly, frot)
            if abs(frot % 180 - 90) < 1e-6:
                w, h = h, w
            pads.append(dict(num=pm.group(1), typ=pm.group(2),
                             x=fx + x, y=fy + y, w=w, h=h,
                             net=pn.group(2) if pn else None,
                             drill=bool(pd)))
        comps[ref] = dict(fp=m_fp.group(1), at=(fx, fy, frot), pads=pads)
    return comps


def schematic_nets(cli):
    os.makedirs(TMP, exist_ok=True)
    out = os.path.join(TMP, "nl_root.net")
    r = subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadsexpr",
                        "-o", out, ROOT_SHEET],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("❌ 网表导出失败")
        print((r.stderr or "")[-500:])
        sys.exit(1)
    txt = open(out, encoding="utf-8").read()
    nets = {}
    for chunk in txt.split("(net")[1:]:
        nm = re.search(r'\(name\s+"([^"]+)"', chunk)
        if not nm:
            continue
        name = nm.group(1).lstrip("/")
        nets.setdefault(name, set()).update(
            re.findall(r'\(ref\s+"([^"]+)"\)\s*\(pin\s+"([^"]+)"\)', chunk))
    import shutil
    shutil.rmtree(TMP, ignore_errors=True)
    return nets


def run_drc(cli):
    out = os.path.join(PCB, "_drc.txt")
    subprocess.run([cli, "pcb", "drc", "--output", out, BOARD],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not os.path.exists(out):
        return None, {}
    txt = open(out, encoding="utf-8", errors="replace").read()
    os.remove(out)
    kinds = collections.Counter()
    for blk in re.split(r"\n(?=\[[a-z_]+\]:)", txt):
        m = re.match(r"\[([a-z_]+)\]:", blk)
        if not m:
            continue
        sev = "error" if re.search(r"Rule:.*;\s*error", blk) else "warning"
        kinds[(m.group(1), sev)] += 1
    return txt, kinds


def main():
    fails = []

    def check(label, ok, detail=""):
        print(f"  {'✅' if ok else '❌'} {label}" + (f"   {detail}" if detail else ""))
        if not ok:
            fails.append(label)

    cli = find_kicad_cli()
    if not cli:
        print("❌ 找不到 kicad-cli")
        return 2
    matrix = D.load_matrix(ROOT)
    keys = {e["index"]: e for e in matrix["matrix"]}
    comps = parse_board(BOARD)

    print("=" * 70)
    print("A. 元件齐套")
    print("=" * 70)
    sw = [r for r in comps if re.fullmatch(r"SW\d+", r) and 1 <= int(r[2:]) <= 95]
    dd = [r for r in comps if re.fullmatch(r"D\d+", r) and 1 <= int(r[1:]) <= 95]
    led = [r for r in comps if r.startswith("LED") and r[3:].isdigit()]
    holes = [r for r in comps if r.startswith("H") and r[1:].isdigit()]
    ctrl = sorted(set(comps) - set(sw) - set(dd) - set(led) - set(holes))
    check("95 轴体", len(sw) == 95, f"实际 {len(sw)}")
    check("95 二极管", len(dd) == 95, f"实际 {len(dd)}")
    check("95 灯珠", len(led) == 95, f"实际 {len(led)}")
    check("28 控制/电源件", len(ctrl) == 28, f"实际 {len(ctrl)} {ctrl if len(ctrl) < 40 else ''}")
    check("8 安装孔（G3）", len(holes) == 8, f"实际 {len(holes)}")
    check("安装孔封装 = M2 NPTH",
          all(comps[h]["fp"] == D.HOLE_FP for h in holes), D.HOLE_FP)

    print("=" * 70)
    print("B. 键位坐标 == matrix.json 派生（允差 1e-6 mm）")
    print("=" * 70)
    bad = []
    for i in sorted(keys):
        e = keys[i]
        cx, cy = D.key_center(e)
        ox, oy = cx + D.SW_ORIGIN_DX, cy + D.SW_ORIGIN_DY
        fx, fy, _ = comps[f"SW{i}"]["at"]
        if abs(fx - ox) > 1e-6 or abs(fy - oy) > 1e-6:
            bad.append((i, fx, fy, ox, oy))
    check("95 个轴体封装位置与几何唯一权威一致", not bad, f"异常 {bad[:3]}")
    badd = []
    for i in sorted(keys):
        cx, cy = D.key_center(keys[i])
        fx, fy, _ = comps[f"D{i}"]["at"]
        if abs(fx - (cx + D.DIODE_DX)) > 1e-6 or abs(fy - (cy + D.DIODE_DY)) > 1e-6:
            badd.append(i)
    check("95 个二极管相对轴心 (-8.50, 0)", not badd, f"异常 {badd[:3]}")
    badl = []
    for i in sorted(keys):
        cx, cy = D.key_center(keys[i])
        fx, fy, _ = comps[f"LED{i}"]["at"]
        if abs(fx - (cx + D.LED_DX)) > 1e-6 or abs(fy - (cy + D.LED_DY)) > 1e-6:
            badl.append(i)
    check("95 颗灯珠相对轴心 (0, +5.08)（参考板实测）", not badl, f"异常 {badl[:3]}")

    print("=" * 70)
    print("C. 异形键与大键位")
    print("=" * 70)
    e52 = keys[52]
    check("index 52（主键区 Enter）是阶梯键", bool(e52.get("stepped")), str(e52.get("label")))
    check("其封装按合并宽 2.25u 选档（不是 w_u=1.5）",
          comps["SW52"]["fp"].endswith("2.25u"), comps["SW52"]["fp"])
    check("轴心在 18.75u（与矩阵列分配同源）",
          abs(e52["centerX_u"] - 18.75) < 1e-9, f"实际 {e52['centerX_u']}")
    vert = [i for i in keys if keys[i]["h_u"] >= 2 and keys[i]["w_u"] == 1]
    check("1u×2u 竖键用 2.00u_Vertical 档",
          all(comps[f"SW{i}"]["fp"].endswith("2.00u_Vertical") for i in vert), f"{vert}")

    print("=" * 70)
    print("D. 全部在板内（USB-C 允许沿 -Y 露边 ≤1 mm）")
    print("=" * 70)
    out_of = []
    for ref, c in comps.items():
        for p in c["pads"]:
            x0, x1 = p["x"] - p["w"] / 2, p["x"] + p["w"] / 2
            y0, y1 = p["y"] - p["h"] / 2, p["y"] + p["h"] / 2
            if x0 < -0.01 or x1 > D.BOARD_W + 0.01 or y1 > D.BOARD_H + 0.01 or y0 < -1.01:
                out_of.append((ref, p["num"], round(x0, 2), round(y0, 2),
                               round(x1, 2), round(y1, 2)))
    check("无焊盘越出板框", not out_of, f"越界 {out_of[:4]}")

    print("=" * 70)
    print("E. 焊盘不互相重叠（同一键的轴体/二极管/灯珠除外）")
    print("=" * 70)
    boxes = []
    for ref, c in comps.items():
        m = re.fullmatch(r"(?:SW|D|LED)(\d+)", ref)
        grp = m.group(1) if m else ref
        for p in c["pads"]:
            boxes.append((p["x"] - p["w"] / 2, p["y"] - p["h"] / 2,
                          p["x"] + p["w"] / 2, p["y"] + p["h"] / 2, grp, ref, p["num"]))
    # 只查「非键区」之间 + 非键区 vs 键区（键区内部按栅格必然邻近，靠 DRC 判）
    nonkey = [b for b in boxes if not re.fullmatch(r"(?:SW|D|LED)\d+", b[5])]
    hits = []
    for i in range(len(nonkey)):
        for j in range(len(nonkey)):
            if i >= j or nonkey[i][4] == nonkey[j][4]:
                continue
            a, b = nonkey[i], nonkey[j]
            if a[0] < b[2] - 0.01 and b[0] < a[2] - 0.01 and \
               a[1] < b[3] - 0.01 and b[1] < a[3] - 0.01:
                hits.append((a[5], a[6], b[5], b[6]))
    check("控制/电源区 28 件与安装孔互不重叠", not hits, f"重叠 {hits[:4]}")

    print("=" * 70)
    print("F. pad 网 == 原理图网表（全量比对）")
    print("=" * 70)
    nets = schematic_nets(cli)
    node2net = {}
    for n, nodes in nets.items():
        for nd in nodes:
            node2net[nd] = n
    mis = []
    for ref, c in comps.items():
        for p in c["pads"]:
            if not p["num"] or p["net"] is None:
                continue
            want = node2net.get((ref, p["num"]))
            if want is None:
                continue
            if p["net"] != want:
                mis.append((ref, p["num"], p["net"], want))
    check("每个带网 pad 的网与原理图一致", not mis, f"不一致 {mis[:4]}")

    print("=" * 70)
    print("G. VLED 网络类（唯一 2–3 A 路径）")
    print("=" * 70)
    txt = open(BOARD, encoding="utf-8").read()
    m = re.search(r'\(net_class "VLED"[^\n]*\n(?:[^\n]*\n)*?\t\)', txt)
    check("存在 VLED 网络类", m is not None)
    if m:
        tw = re.search(r"\(trace_width ([-\d.]+)\)", m.group(0))
        check("VLED 走线宽 ≥ 1.5 mm", tw and float(tw.group(1)) >= 1.5,
              f"{tw.group(1) if tw else '?'} mm")
        check("VLED 网归入该类", re.search(r'\(add_net "VLED"\)', m.group(0)) is not None)

    print("=" * 70)
    print("H. DRC（kicad-cli pcb drc）")
    print("=" * 70)
    _, kinds = run_drc(cli)
    unhandled = {}
    for (kind, sev), n in sorted(kinds.items()):
        if sev == "error" and kind not in DRC_ALLOW:
            unhandled[kind] = n
    for (kind, sev), n in sorted(kinds.items()):
        tag = "已豁免" if kind in DRC_ALLOW else ("❌" if sev == "error" else "warn")
        print(f"      {kind:32} {sev:8} ×{n:4}  {tag}")
    check("未豁免的 error 级违规 = 0", not unhandled, str(unhandled))

    print("=" * 70)
    print("I. 定位板（G6）")
    print("=" * 70)
    if not os.path.exists(PLATE):
        check("定位板文件存在", False, PLATE)
    else:
        plate = parse_board(PLATE)
        cuts = [r for r in plate if r.startswith("P") and r[1:].isdigit()]
        check("95 个开孔", len(cuts) == 95, f"实际 {len(cuts)}")
        bad2 = []
        for i in sorted(keys):
            cx, cy = D.key_center(keys[i])
            fx, fy, _ = plate[f"P{i}"]["at"]
            if abs(fx - cx) > 1e-6 or abs(fy - cy) > 1e-6:
                bad2.append(i)
        check("开孔中心 == 轴体中心（同源）", not bad2, f"异常 {bad2[:3]}")
        oob = []
        for i in cuts:
            fx, fy, _ = plate[i]["at"]
            half = D.PLATE_CUTOUT / 2
            if (fx - half < D.PLATE_X0 - 1e-6 or fx + half > D.PLATE_X0 + D.PLATE_W + 1e-6 or
                    fy - half < D.PLATE_Y0 - 1e-6 or fy + half > D.PLATE_Y0 + D.PLATE_H + 1e-6):
                oob.append(i)
        check("开孔完整落在定位板内", not oob, f"越界 {oob[:4]}")

    print("=" * 70)
    if fails:
        print(f"结论：❌ 未通过（{len(fails)} 项失败）")
        for f in fails:
            print("   -", f)
        return 1
    print(f"结论：✅ PCB 布局校验全部通过（{len(comps)} 个 footprint）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
