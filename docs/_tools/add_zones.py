#!/usr/bin/env python3
"""add_zones.py —— 给板子补上三块铺铜（B.Cu GND / In1.Cu GND / In2.Cu VLED）

为什么需要这个脚本（⚠️ 可复现性缺口，2026-09-19 补）：
    B4 会话里的铺铜是**手工加的**，`gen_pcb.py` 并不创建它们。
    于是「重新生成布局」之后板子会**一块铺铜都没有** —— 而 In1 是 GND 平面、
    In2 是 VLED 配电平面（2.4 A 灯轨的载体），丢了就不成立。
    参数从已入库的板文件（提交 d670b23）里原样抄出，避免凭记忆重建：
        GND  / B.Cu   : clearance 0.2, min_thickness 0.2, thermal 0.5/0.5
        GND  / In1.Cu : 同上
        VLED / In2.Cu : clearance **0.25**，其余同上
    三块都是**整板矩形**多边形（-0.05 … 374.7625 / -0.05 … 151.1125）。

用法（工作目录必须在 D:/Kicad/bin）：
    cd /d/Kicad/bin && ./python.exe D:/StarShield/docs/_tools/add_zones.py <board> [--apply]
不给 --apply 时只打印将要做的事。已在有铺铜的板上运行会跳过（幂等）。
填铜请随后跑 `docs/_tools/refill_zones.py`（必须显式传板路径）。
"""
import sys

import pcbnew

X0, Y0, X1, Y1 = -0.05, -0.05, 374.7625, 151.1125
ZONES = [
    ("GND", pcbnew.B_Cu, 0.20),
    ("GND", pcbnew.In1_Cu, 0.20),
    ("VLED", pcbnew.In2_Cu, 0.25),
]


def nm(v):
    return pcbnew.FromMM(v)


def norm(n):
    return n.rsplit("/", 1)[-1]


def find_net(b, want):
    for _c, ni in b.GetNetInfo().NetsByNetcode().items():
        if norm(ni.GetNetname()) == want:
            return ni
    return None


def add_zone(b, netname, layer, clearance):
    z = pcbnew.ZONE(b)
    # ⚠️ ZONE 是「多层」对象：层必须用 LayerSet 设置，SetLayer() 单独调用无效
    #    （实测：只用 SetLayer 时三块铺铜全部落到 F.Cu，Fill 也照做 ⇒ 静默错误）
    z.SetLayerSet(pcbnew.LSET(layer))
    z.SetNet(find_net(b, netname))
    z.SetLocalClearance(nm(clearance))
    z.SetMinThickness(nm(0.2))
    z.SetThermalReliefGap(nm(0.5))
    z.SetThermalReliefSpokeWidth(nm(0.5))
    z.SetIsFilled(False)
    poly = z.Outline()
    poly.NewOutline()
    for x, y in ((X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)):
        poly.Append(nm(x), nm(y))
    b.Add(z)
    return z


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    apply = "--apply" in sys.argv
    b = pcbnew.LoadBoard(path)
    have = list(b.Zones())
    print(f"板：{path}  现有铺铜 {len(have)} 块")
    if have and "--force" not in sys.argv:
        print("已有铺铜 ⇒ 跳过（幂等）。要重建请加 --force。")
        return
    if have:
        for z in have:
            b.Remove(z)
        print(f"  已先删除原有 {len(have)} 块")
    for netname, layer, cl in ZONES:
        print(f"  将新增：{netname:5} on {b.GetLayerName(layer):7} clearance {cl}")
    if not apply:
        print("\n（未落盘；加 --apply 执行，然后跑 refill_zones.py）")
        return
    for netname, layer, cl in ZONES:
        add_zone(b, netname, layer, cl)
    pcbnew.SaveBoard(path, b)
    raw = open(path, "rb").read()
    if b"\r\n" in raw:
        open(path, "wb").write(raw.replace(b"\r\n", b"\n"))
    print(f"  ✅ 已加 3 块铺铜并保存（{len(raw)} 字节，行尾归一 LF）")


if __name__ == "__main__":
    main()
