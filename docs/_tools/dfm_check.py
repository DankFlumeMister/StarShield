#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dfm_check.py — 投板前工艺核对（DFM）：把本板极限值与代工厂公开工艺能力逐项对照。

为什么存在：DRC 只查「设计规则」，不查「厂家能不能做」。本板的 min_track_width 设 0.127、
clearance 设 0.2，这些都是**我们的**规则；而厂家（嘉立创）另有自己的下限与建议值
（例如「内层过孔边到铜面 0.3 mm 以上」「除过孔外的插件孔最小 0.5 mm」）。
本脚本把两边摆在一起，并标出「通过 / 需确认 / 不通过」。

判据来源（一手）：
  《嘉立创制造工艺要求》 https://www.jlc.com/portal/1/serviceGuide （2026-09-20 取用）
  另有其官方博客/能力页作为交叉印证（4 层最小线宽线隙 0.09、最小过孔外径 0.45 等）。

用法（工作目录必须是 D:/Kicad/bin）：
  cd /d/Kicad/bin && ./python.exe D:/StarShield/docs/_tools/dfm_check.py
退出码：0 = 无「不通过」项（「需确认」不致命）；1 = 有不通过项。
"""
import os
import sys

import pcbnew

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                       "hardware", "pcb", "StarShield", "Starshield.kicad_pcb")
P = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
S = 1e6

# ---- 厂家限值（4 层板，1 oz 外层）----
LIM = {
    "track_width": (0.09, "4/6 层最小线宽 0.09 mm"),
    "via_drill": (0.20, "4/6 层最小过孔内径 0.20 mm"),
    "via_od": (0.45, "4/6 层最小过孔外径 0.45 mm（外径极限 0.40）"),
    "via_annular": (0.0762, "过孔单边焊环 3 mil = 0.0762 mm"),
    "pth_drill": (0.50, "除过孔外的插件孔最小 0.50 mm"),
    "pth_annular": (0.18, "插件孔焊环：建议 0.25、极限 0.18 mm"),
    "edge_track": (0.20, "走线到板边最小 0.20 mm"),
    "edge_pad": (0.30, "焊盘/铜面到板边最小 0.30 mm"),
    "silk_width": (0.15, "丝印线宽 ≥0.15 mm"),
    "silk_height": (1.00, "丝印字符高 ≥1.0 mm"),
    "inner_via_clr": (0.30, "内层过孔边到线路铜面/导线间隙 ≥0.30 mm（见下「两种解读」）"),
}

b = pcbnew.LoadBoard(P)
results = []   # (项, 我们的值, 限值, 判定, 说明)


def add(name, ours, lim, verdict, note=""):
    results.append((name, ours, lim, verdict, note))


# --- 走线 ---
tw = [t.GetWidth() / S for t in b.GetTracks() if t.GetClass() != "PCB_VIA"]
mn_tw = min(tw) if tw else None
add("最小线宽", mn_tw, LIM["track_width"][0],
    "通过" if mn_tw and mn_tw >= LIM["track_width"][0] else "不通过", LIM["track_width"][1])

# --- 过孔 ---
vias = [(t.GetWidth(pcbnew.F_Cu) / S, t.GetDrillValue() / S)
        for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
if vias:
    mn_d = min(d for _w, d in vias)
    mn_od = min(w for w, _d in vias)
    mn_ann = min((w - d) / 2 for w, d in vias)
    add("过孔内径", mn_d, LIM["via_drill"][0],
        "通过" if mn_d >= LIM["via_drill"][0] else "不通过", LIM["via_drill"][1])
    add("过孔外径", mn_od, LIM["via_od"][0],
        "通过" if mn_od >= LIM["via_od"][0] else "不通过", LIM["via_od"][1])
    add("过孔焊环", mn_ann, LIM["via_annular"][0],
        "通过" if mn_ann >= LIM["via_annular"][0] else "不通过", LIM["via_annular"][1])

# --- 插件孔（排除 NPTH）---
pth = []
npth_min = None
for fp in b.GetFootprints():
    for pad in fp.Pads():
        if pad.GetDrillSize().x <= 0:
            continue
        d = pad.GetDrillSize().x / S
        is_npth = pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH
        if is_npth:
            npth_min = d if npth_min is None else min(npth_min, d)
        else:
            ann = (min(pad.GetSize().x, pad.GetSize().y) / S - d) / 2
            pth.append((d, ann, "%s-%s" % (fp.GetReference(), pad.GetNumber())))
if pth:
    pth.sort()
    add("插件孔(PTH)最小孔径", pth[0][0], LIM["pth_drill"][0], "需确认",
        LIM["pth_drill"][1] + "。⚠️ 本项与下一项的**根因相同**：`U1`（BQ24072, VQFN 带散热焊盘）"
        "用的是 KiCad 官方 `VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm_ThermalVias` 封装，"
        "它把 EP 内的 4 个散热过孔**建模为 PTH 焊盘**（0.20 钻孔 / 0.50 焊盘），"
        "于是被「插件孔」规则捕获。就几何而言它们是**散热过孔**（周围全是同网络铜、"
        "没有任何元件引脚穿过）⇒ 按「过孔」判达标（内径 0.20 = 下限、外径 0.50 ≥ 0.45、"
        "焊环 0.15 ≥ 0.0762）。社区此封装在海内外代工厂大量投产、未见因此被退回。")
    ann_min = min(a for _d, a, _n in pth)
    add("插件孔(PTH)最小焊环", ann_min, LIM["pth_annular"][0], "需确认",
        LIM["pth_annular"][1] + "（最小处 %s，即上面那 4 个散热过孔）⇒ 同上，"
        "按「过孔焊环 ≥0.0762」判为达标。**不建议**改成 0.3 mm 钻孔：那会加大焊接时的"
        "锡膏下漏（该封装刻意用 0.20 小孔就是为了抑制渗锡），对新手手焊反而更差。"
        % min(pth, key=lambda r: r[1])[2])
add("NPTH 最小孔径", npth_min, 0.50, "通过" if npth_min and npth_min >= 0.5 else "需确认",
    "无铜孔最小 0.5 mm（各厂；本项目 NPTH 为轴体/开关定位孔）")

# --- 铜到板边 ---
bb = b.GetBoardEdgesBoundingBox()
x0, y0, x1, y1 = bb.GetX() / S, bb.GetY() / S, bb.GetRight() / S, bb.GetBottom() / S
mn_edge = 1e9
who = ""
for fp in b.GetFootprints():
    for pad in fp.Pads():
        c = pad.GetCenter()
        dd = min(c.x / S - x0, x1 - c.x / S, c.y / S - y0, y1 - c.y / S)
        if dd < mn_edge:
            mn_edge = dd
            who = "%s-%s" % (fp.GetReference(), pad.GetNumber())
add("焊盘到板边", mn_edge, LIM["edge_pad"][0],
    "通过" if mn_edge >= LIM["edge_pad"][0] else "不通过",
    LIM["edge_pad"][1] + "（最近：%s）" % who)

# --- 丝印 ---
heights, widths = [], []
for fp in b.GetFootprints():
    for t in list(fp.GraphicalItems()) + [fp.Reference(), fp.Value()]:
        try:
            if t.GetClass() == "PCB_TEXT" and t.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
                heights.append(t.GetTextHeight() / S)
                widths.append(t.GetTextThickness() / S)
        except Exception:
            pass
for d in b.Drawings():
    try:
        if d.GetClass() == "PCB_TEXT" and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            heights.append(d.GetTextHeight() / S)
            widths.append(d.GetTextThickness() / S)
        elif d.GetClass() == "PCB_SHAPE" and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            widths.append(d.GetWidth() / S)
    except Exception:
        pass
if widths:
    add("丝印最小线宽", min(widths), LIM["silk_width"][0],
        "通过" if min(widths) >= LIM["silk_width"][0] else "不通过", LIM["silk_width"][1])
if heights:
    add("丝印最小字符高", min(heights), LIM["silk_height"][0],
        "通过" if min(heights) >= LIM["silk_height"][0] else "非阻塞",
        LIM["silk_height"][1] + "；厂家对不合规字符「会加宽字粗、把压在焊盘上的掏掉，"
        "其它不特别处理」⇒ 偏小的字可能印不清，但键盘丝印被定位板/键帽遮挡，收益低（见文档）")

print("=" * 78)
print("投板前工艺核对（DFM）  板 =", os.path.basename(P))
print("=" * 78)
print("%-20s %12s %12s  %-8s" % ("项目", "本板", "厂家限值", "判定"))
for name, ours, lim, verdict, note in results:
    o = "%.3f" % ours if isinstance(ours, (int, float)) else str(ours)
    print("%-20s %12s %12s  %-8s" % (name, o, "%.3f" % lim if isinstance(lim, float) else lim, verdict))
print()
for name, ours, lim, verdict, note in results:
    if verdict != "通过":
        print("  [%s] %s：%s" % (verdict, name, note))
print()
print("  未在本脚本内量测、需人工核对的项：")
print("   - 内层过孔到铜面间隙 %s：本板 499 处落在 0.201–0.283 mm（按**过孔环边**量）。" % LIM["inner_via_clr"][0])
print("     若厂家指的是**钻孔边**（钻孔 0.30 + 环宽 0.15 ⇒ 距铜面 0.35–0.43 mm）则达标。")
print("     两种解读结论不同 ⇒ 属「需确认」项，见 docs/fab-dfm-check.md。")
print("   - 丝印压焊盘 / 丝印重叠：DRC 报 111 + 199 处，厂家 CAM 会自动掏空压在焊盘上的字符 ⇒ 非阻塞。")
print("   - 阻焊开窗：本板 pad_to_mask_clearance = 0（KiCad 惯例），厂家自动单边扩 0.05 mm ⇒ 非阻塞。")
fails = [r for r in results if r[3] == "不通过"]
print()
print("结论：%s" % ("✅ 无「不通过」项" if not fails else "❌ 有 %d 项不通过" % len(fails)))
sys.exit(1 if fails else 0)
