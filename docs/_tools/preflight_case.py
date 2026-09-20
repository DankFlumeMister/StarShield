"""preflight_case.py — 外壳参数的几何预检（纯 Python，不开 Fusion）。

为什么：Fusion 无进程外 API，脚本只能在 Fusion 里跑（一次启动 1–3 分钟）。
先用同样的参数在本地把「尺寸自洽 / 有没有互相打架」算清楚，能省掉大量盲试。

判据（每条都打印实际值）：
  A. 内腔 ⊃ 板框 + 单边间隙；外形 = 内腔 + 2×壁厚
  B. 板下净空 ≥ 电池厚 + **压边** + 插拔座高 + 余量
     ⚠️ 2026-09-21 修：原判据漏了压边 ⇒ 座高取错（3.5）时也不会报错，实际会撞。见 docs/case-benchmark.md §3.1
  C. 8 个 M2 柱完全落在外形之内（允许与侧壁相融）
  D. 电池仓 + 压边角完全落在内腔之内，且不与任一螺丝柱相交
  E. 三处开孔完全落在对应侧壁之内，且不切到螺丝柱
  F. 分件缝不穿过任何螺丝柱 / 电池
  G. 螺丝柱满足「M2 热熔螺母」的 2× 规则与孔深（2026-09-21 新增，依据 docs/case-benchmark.md §2.3）

用法：python docs/_tools/preflight_case.py
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"D:/StarShield"
INP = os.path.join(ROOT, "hardware", "case", "case_inputs.json")

P = {
    "wall": 2.0, "floor": 2.5, "clearance": 0.3, "depth": 15.0, "lip": 4.5,
    "boss_od": 6.4, "boss_pilot": 3.0, "boss_pilot_depth": 5.0,   # M2 热熔螺母（OD3.2×L4，2× 规则，见 case-benchmark §2.3/§3.5）
    "bat_w": 56.0, "bat_l": 68.0, "bat_t": 10.5, "bat_inset": 8.5,
    "clip": 2.0, "clip_len": 12.0, "seam_x": 189.70,
}
# 热插拔座在 PCB **下方**的占高：Kailh CPG151101S11 原厂图纸 1.80±0.05（总高 3.05）[DOC]
# 2026-09-21 更正：旧值 3.5 是假设值，且与压边参数自相矛盾（见 docs/case-benchmark.md §3.1）
SOC = 1.8
MARGIN = 0.7       # 板下余量（座/压边/电池的装配与打印公差）
PCB_T = 1.6
OPENINGS = [
    {"name": "charge USB-C", "kind": "front", "center": 15.0, "w": 11.0},
    {"name": "module USB-C", "kind": "left", "center": 17.8, "w": 10.0},
    {"name": "SW96 mode sw", "kind": "front", "center": 33.0, "w": 8.0},
]

d = json.load(open(INP, encoding="utf-8"))
bx0, by0, bx1, by1 = d["board_outline"]["bbox"]
holes = d["mounting_holes"]

ix0, iy0 = bx0 - P["clearance"], by0 - P["clearance"]
ix1, iy1 = bx1 + P["clearance"], by1 + P["clearance"]
ox0, oy0 = ix0 - P["wall"], iy0 - P["wall"]
ox1, oy1 = ix1 + P["wall"], iy1 + P["wall"]
z_floor = P["floor"]
z_pcb = z_floor + P["depth"]
z_top = z_pcb + PCB_T + P["lip"]

ok = True


def chk(name, cond, detail):
    global ok
    ok &= bool(cond)
    print("  %s %s   %s" % ("✅" if cond else "❌", name, detail))


print("=== A. 尺寸自洽 ===")
print("  板框 %.4f × %.4f；内腔 %.2f × %.2f；外形 %.2f × %.2f；总高 %.2f"
      % (bx1 - bx0, by1 - by0, ix1 - ix0, iy1 - iy0, ox1 - ox0, oy1 - oy0, z_top))
chk("内腔比板框大（单边 %.2f）" % P["clearance"],
    ix0 < bx0 and iy0 < by0 and ix1 > bx1 and iy1 > by1, "内腔含板框 ✓")
chk("外形 = 内腔 + 2×壁厚", abs((ox1 - ox0) - ((ix1 - ix0) + 2 * P["wall"])) < 1e-6,
    "%.2f = %.2f + 2×%.1f" % (ox1 - ox0, ix1 - ix0, P["wall"]))

print("\n=== B. 板下净空 vs 电池 + 压边 + 插拔座 ===")
need = P["bat_t"] + P["clip"] + SOC
free = P["depth"]
chk("净空 %.1f ≥ 电池 %.1f + 压边 %.1f + 座 %.1f + 余量 %.1f = %.1f"
    % (free, P["bat_t"], P["clip"], SOC, MARGIN, need + MARGIN),
    free >= need + MARGIN,
    "压边顶面 z=%.2f，座底面 z=%.2f ⇒ 间隙 %.2f mm"
    % (z_floor + P["bat_t"] + P["clip"], z_pcb - SOC, P["depth"] - need))
chk("电池顶面不碰座底面", P["bat_t"] + P["clip"] <= P["depth"] - SOC,
    "%.1f + %.1f = %.1f ≤ %.1f − %.1f = %.1f"
    % (P["bat_t"], P["clip"], P["bat_t"] + P["clip"], P["depth"], SOC, P["depth"] - SOC))

print("\n=== C. 螺丝柱 ===")
for h in holes:
    r = P["boss_od"] / 2
    inside = (h["x"] - r >= ox0 - 1e-9) and (h["x"] + r <= ox1 + 1e-9) and \
             (h["y"] - r >= oy0 - 1e-9) and (h["y"] + r <= oy1 + 1e-9)
    chk("%-3s (%.2f, %.2f) φ%g" % (h["ref"], h["x"], h["y"], P["boss_od"]), inside,
        "柱边 x %.2f..%.2f / y %.2f..%.2f" % (h["x"] - r, h["x"] + r, h["y"] - r, h["y"] + r))
chk("柱顶 = PCB 下表面 z=%.2f" % z_pcb, True, "柱高 %.1f（内腔地面起）" % (z_pcb - z_floor))

print("\n=== D. 电池仓 + 压边 vs 螺丝柱 ===")
bats = [(ix0 + P["bat_inset"], (iy0 + iy1) / 2 - P["bat_l"] / 2),
        (ix1 - P["bat_inset"] - P["bat_w"], (iy0 + iy1) / 2 - P["bat_l"] / 2)]
for k, (bxx, byy) in enumerate(bats, 1):
    inside = (bxx >= ix0) and (bxx + P["bat_w"] <= ix1) and (byy >= iy0) and (byy + P["bat_l"] <= iy1)
    chk("电池 %d 在内腔内" % k, inside, "x %.2f..%.2f  y %.2f..%.2f" % (bxx, bxx + P["bat_w"], byy, byy + P["bat_l"]))
    bad = []
    for h in holes:
        # 压边占据：电池四周 2mm 环 + 四个角上的 L（简化按「电池外扩 clip」的矩形环检查）
        ex0, ey0 = bxx - P["clip"], byy - P["clip"]
        ex1, ey1 = bxx + P["bat_w"] + P["clip"], byy + P["bat_l"] + P["clip"]
        if ex0 - P["boss_od"] / 2 <= h["x"] <= ex1 + P["boss_od"] / 2 and \
           ey0 - P["boss_od"] / 2 <= h["y"] <= ey1 + P["boss_od"] / 2:
            bad.append(h["ref"])
    chk("电池 %d 压边区不与螺丝柱相交" % k, not bad, ("相撞：%s" % bad) if bad else "无相交")

print("\n=== E. 开孔 vs 侧壁 / 螺丝柱 ===")
for op in OPENINGS:
    if op["kind"] == "front":
        a0, a1 = op["center"] - op["w"] / 2, op["center"] + op["w"] / 2
        inwall = (a0 >= ox0) and (a1 <= ox1)
        near = [h["ref"] for h in holes if abs(h["y"] - oy0) < 12 and a0 - 3 <= h["x"] <= a1 + 3]
    else:
        a0, a1 = op["center"] - op["w"] / 2, op["center"] + op["w"] / 2
        inwall = (a0 >= oy0) and (a1 <= oy1)
        near = [h["ref"] for h in holes if abs(h["x"] - ox0) < 12 and a0 - 3 <= h["y"] <= a1 + 3]
    chk("%-14s %s 壁 中心 %.1f 宽 %g" % (op["name"], op["kind"], op["center"], op["w"]),
        inwall and not near, ("落在壁内 ✓；附近柱 %s" % near) if near else "落在壁内、不切柱")

print("\n=== F. 分件缝 ===")
hit = [h["ref"] for h in holes if abs(h["x"] - P["seam_x"]) < P["boss_od"]]
cross_bat = [k + 1 for k, (bxx, _b) in enumerate(bats)
             if bxx - P["clip"] < P["seam_x"] < bxx + P["bat_w"] + P["clip"]]
chk("缝 x=%.2f 不穿螺丝柱" % P["seam_x"], not hit, ("穿：%s" % hit) if hit else "无")
chk("缝不穿电池仓", not cross_bat, ("穿：%s" % cross_bat) if cross_bat else "无")
print("  两件跨度：A %.1f mm・B %.1f mm（打印床 256 ✓）"
      % (P["seam_x"] - ox0, ox1 - P["seam_x"]))

print("\n=== G. 螺丝柱：M2 热熔螺母是否合规 ===")
# 依据：柱外径 ≥ 2× 嵌件外径 —— 环向应力膝点（absurdtools）；柱壁 ≥ 1.6 mm（meshra / printforgehq）
# 假定嵌件 M2 × OD3.2 × L4（社区最常见规格；**采购后按厂家图纸复核**）
INS_OD = 3.2
chk("柱外径 %.1f ≥ 2× 嵌件外径 %.1f = %.1f" % (P["boss_od"], INS_OD, 2 * INS_OD),
    P["boss_od"] >= 2 * INS_OD, "余量 %.2f mm" % (P["boss_od"] - 2 * INS_OD))
chk("柱壁 (柱径−孔径)/2 ≥ 1.6 mm", (P["boss_od"] - P["boss_pilot"]) / 2 >= 1.6,
    "(%.1f − %.1f)/2 = %.2f mm" % (P["boss_od"], P["boss_pilot"], (P["boss_od"] - P["boss_pilot"]) / 2))
chk("螺母孔深 %.1f ≥ 螺母长 4.0 + 1.0 让位" % P["boss_pilot_depth"],
    P["boss_pilot_depth"] >= 5.0, "孔底 z=%.2f（柱顶 z=%.2f）"
    % (z_pcb - P["boss_pilot_depth"], z_pcb))
chk("孔深 < 柱高（不穿透底板）", P["boss_pilot_depth"] < (z_pcb - z_floor),
    "%.1f < %.1f" % (P["boss_pilot_depth"], z_pcb - z_floor))
# 柱与电池压边的净距（两边都是本体材料，但过窄的缝打印会拉丝 ⇒ 目标 ≥ 1.0 mm）
worst = 9e9
for h in holes:
    if abs(h["y"] - (iy0 + iy1) / 2) < P["bat_l"] / 2 + P["clip"]:
        for (bxx, _byy) in bats:
            for edge in (bxx - P["clip"], bxx + P["bat_w"] + P["clip"]):
                worst = min(worst, abs(h["x"] - edge) - P["boss_od"] / 2)
chk("柱边与压边外缘净距 ≥ 1.0 mm", worst >= 1.0 - 1e-6,
    "最窄 %.2f mm（过窄会拉丝/粘连；不够就把 bat_inset 调大）" % worst)

print("\n⚠️ 待实测/待定的输入")
print("  - 热插拔座占高按 %.1f mm（Kailh 图纸标称 ±0.05，非实物实测；B6 采购后复核）" % SOC)
print("  - USB-C 开口宽 11.0/10.0：按连接器体+0.3/边成立，**插头外壳宽度未实测**（量一根目标线）")
print("  - 倾角 5.5° / 脚垫 Ø8×3 / 缝销 Ø4×8 —— 已在 docs/case-benchmark.md 定值，**v2 才建几何**")
print("\n%s" % ("✅ 预检通过" if ok else "❌ 预检有失败项"))
sys.exit(0 if ok else 1)
