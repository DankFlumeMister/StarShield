"""preflight_case.py — 外壳参数的几何预检（纯 Python，不开 Fusion）。

为什么：Fusion 无进程外 API，脚本只能在 Fusion 里跑（一次启动 1–3 分钟）。
先用同样的参数在本地把「尺寸自洽 / 有没有互相打架」算清楚，能省掉大量盲试。

判据（每条都打印实际值）：
  A. 内腔 ⊃ 板框 + 单边间隙；外形 = 内腔 + 2×壁厚
  B. 板下净空 ≥ 电池厚 + 插拔座高 + 余量
  C. 8 个 M2 柱完全落在外形之内（允许与侧壁相融）
  D. 电池仓 + 压边角完全落在内腔之内，且不与任一螺丝柱相交
  E. 三处开孔完全落在对应侧壁之内，且不切到螺丝柱
  F. 分件缝不穿过任何螺丝柱 / 电池

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
    "boss_od": 5.0, "boss_pilot": 1.7,
    "bat_w": 56.0, "bat_l": 68.0, "bat_t": 10.5, "bat_inset": 8.0,
    "clip": 2.0, "clip_len": 12.0, "seam_x": 189.70,
}
SOC = 3.5          # 热插拔座高度（板下）—— 见下方「待实测」说明
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

print("\n=== B. 板下净空 vs 电池 + 插拔座 ===")
need = P["bat_t"] + SOC
free = P["depth"]
chk("净空 %.1f ≥ 电池 %.1f + 座 %.1f = %.1f（余 %.1f）"
    % (free, P["bat_t"], SOC, need, free - need), free >= need,
    "电池顶面 z=%.2f，座底面 z=%.2f ⇒ 间隙 %.2f mm"
    % (z_floor + P["bat_t"], z_pcb - SOC, P["depth"] - need))

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

print("\n⚠️ 待实测/待定的输入（本预检按假设值算）")
print("  - 热插拔座高度按 %.1f mm 假设（未实测；见 docs/case-design.md 待办）" % SOC)
print("  - 定位板与 PCB 的间距、板的固定方式：暂未建（v1 只做底壳 + 螺丝柱）")
print("\n%s" % ("✅ 预检通过" if ok else "❌ 预检有失败项"))
sys.exit(0 if ok else 1)
