"""extract_case_inputs.py — 从 PCB 提出外壳建模所需的精确几何，写成 JSON。

为什么：外壳的每一个尺寸都必须源自板文件（板框、安装孔、开口），
手抄数字一定会漂。产物 `hardware/case/case_inputs.json` 是**派生数据**，
可由本脚本随时重建（外壳脚本读它，不读板文件）。

用法（工作目录必须是 D:/Kicad/bin）：
  cd /d/Kicad/bin && ./python.exe D:/StarShield/docs/_tools/extract_case_inputs.py
"""
import json
import math
import os
import sys

import pcbnew

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"D:/StarShield"
BOARD = ROOT + "/hardware/pcb/StarShield/Starshield.kicad_pcb"
PLATE = ROOT + "/hardware/pcb/StarShield/Starshield-plate.kicad_pcb"
OUT = ROOT + "/hardware/case/case_inputs.json"
S = 1e6

b = pcbnew.LoadBoard(BOARD)


def outline_of(board):
    """把 Edge.Cuts 上的图元整理成闭合多边形（只处理直线段；弧按端点近似并标注）。"""
    segs = []
    arcs = 0
    for d in board.Drawings():
        if d.GetLayer() != pcbnew.Edge_Cuts:
            continue
        cls = d.GetClass()
        if cls == "PCB_SHAPE":
            st = d.GetShape()
            if st == pcbnew.SHAPE_T_SEGMENT:
                a, c = d.GetStart(), d.GetEnd()
                segs.append(((a.x / S, a.y / S), (c.x / S, c.y / S)))
            else:
                arcs += 1
        elif cls == "PCB_ARC":
            arcs += 1
    # 串成环
    pts = [segs[0][0], segs[0][1]]
    used = {0}
    while len(used) < len(segs):
        last = pts[-1]
        found = False
        for i, (a, c) in enumerate(segs):
            if i in used:
                continue
            if math.dist(last, a) < 1e-6:
                pts.append(c)
                used.add(i)
                found = True
                break
            if math.dist(last, c) < 1e-6:
                pts.append(a)
                used.add(i)
                found = True
                break
        if not found:
            break
    return pts, arcs, len(segs)


pts, arcs, nseg = outline_of(b)
xs = [p[0] for p in pts]
ys = [p[1] for p in pts]
outline = {"points": [[round(x, 4), round(y, 4)] for x, y in pts],
           "bbox": [round(min(xs), 4), round(min(ys), 4), round(max(xs), 4), round(max(ys), 4)],
           "segments": nseg, "arcs": arcs}

# 安装孔：**只认位号以 H 开头的 MountingHole 封装**
# ⚠️ 不能按孔径筛 —— MX 热插拔座自带 φ1.70 / φ3.05 的 NPTH 定位孔（每键 3 个，共 280+），
#    按孔径筛会把它们一并算成安装孔（首版就踩了，得到 210 个「安装孔」）。
holes = []
other_npth = []
for fp in b.GetFootprints():
    for pad in fp.Pads():
        d = pad.GetDrillSize().x / S
        if d <= 0 or pad.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
            continue
        c = pad.GetCenter()
        rec = {"ref": fp.GetReference(), "x": round(c.x / S, 4),
               "y": round(c.y / S, 4), "d": round(d, 3)}
        if fp.GetReference().startswith("H"):
            holes.append(rec)
        else:
            other_npth.append(rec)
holes.sort(key=lambda h: (h["x"], h["y"]))

# 板厚度等
thick = None
for k in ("thickness",):
    pass
try:
    thick = b.GetDesignSettings().GetBoardThickness() / S
except Exception:
    pass

# 定位板外形（同源生成，单独一块板文件）
plate_outline = None
if os.path.exists(PLATE):
    pb = pcbnew.LoadBoard(PLATE)
    pp, parc, pseg = outline_of(pb)
    pxs = [p[0] for p in pp]
    pys = [p[1] for p in pp]
    plate_outline = {"bbox": [round(min(pxs), 4), round(min(pys), 4),
                              round(max(pxs), 4), round(max(pys), 4)],
                     "segments": pseg, "arcs": parc}
    # 定位板开孔（按图元形状分类统计；首版只数「非线段」得出 0，是口径错）
    from collections import Counter
    shapes = Counter()
    for d in pb.Drawings():
        if d.GetLayer() != pcbnew.Edge_Cuts:
            continue
        if d.GetClass() == "PCB_SHAPE":
            shapes[str(d.GetShape())] += 1
        else:
            shapes[d.GetClass()] += 1
    plate_outline["shape_types"] = dict(shapes)

data = {
    "_note": "由 docs/_tools/extract_case_inputs.py 从板文件提取；外壳脚本只读这里，不读板文件。",
    "source_board": "hardware/pcb/StarShield/Starshield.kicad_pcb",
    "board_outline": outline,
    "board_thickness_mm": round(thick, 3) if thick else None,
    "mounting_holes": holes,
    "plate": plate_outline,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("板框 bbox =", outline["bbox"], " 段数", nseg, " 弧", arcs)
print("安装孔 %d 个：" % len(holes))
for h in holes:
    print("   %-4s (%.2f, %.2f) phi%.2f" % (h["ref"], h["x"], h["y"], h["d"]))
print("其它 NPTH（轴体/开关定位孔，非安装孔）= %d 个" % len(other_npth))
print("板厚 =", data["board_thickness_mm"])
print("定位板 =", plate_outline)
print("✅ 已写入", OUT)
