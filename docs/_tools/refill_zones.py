#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""refill_zones.py — 用 pcbnew 引擎重填全部铺铜并保存板子（B4 收尾固化）。

为什么存在：handoff 硬约束 ②「改完铜必须重填铺铜，否则 DRC 报上百条假违规」。
以前这一步只能走 KiCad MCP（open_board → refill_zones → save_board），但 MCP 有
两个已实测的坑：open_board 对同一路径不重新读盘（陈旧内存覆盖磁盘）、save_board
会把 .kicad_pro 的 min_track_width 写回旧值。本脚本用 pcbnew 直接读写，两个坑都没有。

用法（⚠️ 必须用 KiCad 自带 python，且**工作目录切到 D:/Kicad/bin**，否则 DLL
找不到、进程直接崩——实测 SIGTERM 无输出）：

    cd /d/Kicad/bin
    ./python.exe D:/StarShield/docs/_tools/refill_zones.py [板文件路径]

默认板 = hardware/pcb/StarShield/Starshield.kicad_pcb。

坑位记录（2026-09-19 实测，KiCad 10.0.6 绑定）：
  - BOARD 没有 GetZones()；GetZoneList() 返回裸 SWIG 指针不可迭代；
    **BOARD.Zones() 返回 tuple** 才是正解。
  - SaveBoard 会把文件写成 **CRLF**，而仓库是 LF 且 .gitattributes 把
    *.kicad_pcb 标为 binary（不做行尾转换）⇒ 本脚本保存后统一转回 LF，
    否则每次重填都会在仓库里留下全文件行尾漂移。
"""
import os
import sys

import pcbnew

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DEFAULT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "hardware", "pcb", "StarShield", "Starshield.kicad_pcb")
P = sys.argv[1] if len(sys.argv) > 1 else DEFAULT

b = pcbnew.LoadBoard(P)
zones = list(b.Zones())
print(f"铺铜区数量: {len(zones)}")
for z in zones:
    # ⚠️ 不要用 z.GetLayerName() —— ZONE 是多层对象，实测它**恒返回 F.Cu**（SWIG 行为），
    #    会让人误以为铺铜全落到了顶层。必须读 LayerSet。
    names = ",".join(pcbnew.LayerName(x) for x in z.GetLayerSet().Seq()) or "(空)"
    print(f"  net={z.GetNetname():10} layers={names:16} "
          f"priority={z.GetAssignedPriority()}")
ok = pcbnew.ZONE_FILLER(b).Fill(zones)
print("Fill 返回:", ok)
pcbnew.SaveBoard(P, b)

raw = open(P, "rb").read()
if b"\r\n" in raw:
    open(P, "wb").write(raw.replace(b"\r\n", b"\n"))
    print("行尾已从 CRLF 归一为 LF（SaveBoard 默认写 CRLF，仓库为 LF）")
print("✅ 已保存", P)
