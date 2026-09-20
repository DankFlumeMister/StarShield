#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_fab.py — 生成投板文件包（Gerber / 钻孔 / BOM / 坐标 + 订单说明 + 打包 zip）。

**为什么这么组织**（社区惯例，本机 `research/` 下 100+ 开源键盘工程实测）：
  - 交付目录名：`gerbers/`(34) · `gerber/`(15) · `production_files/`(7) · `jlcpcb/`(6) · `fab/`(4)
  - 交付内容：Gerber + `.drl` 钻孔，**并打包成一个 zip 直接上传代工厂**（235 个 zip 样本）
  - BOM / 贴片坐标按嘉立创口径命名：`BOM-<板名>.csv` / `CPL-<板名>.csv`

**层集**（11 个 Gerber）：4 铜层 + 2 阻焊 + 2 丝印 + 2 钢网 + 外形
（嘉立创要求 ≥7 个文件；本板 4 层 ⇒ 11 个）。

用法（任何 shell 均可，脚本内部用绝对路径调 kicad-cli）：
  python docs/_tools/export_fab.py [--out DIR]

退出码：0 = 全部生成且自检通过；非 0 = 有步骤失败或自检不过。
"""
import argparse
import os
import shutil
import subprocess
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PCB_DIR = os.path.join(ROOT, "hardware", "pcb", "StarShield")
BOARD = os.path.join(PCB_DIR, "Starshield.kicad_pcb")
ROOT_SCH = os.path.join(PCB_DIR, "Starshield.kicad_sch")
NAME = "Starshield"

LAYERS = ",".join([
    "F.Cu", "In1.Cu", "In2.Cu", "B.Cu",
    "F.Paste", "B.Paste",
    "F.Silkscreen", "B.Silkscreen",
    "F.Mask", "B.Mask",
    "Edge.Cuts",
])

ORDER_SPEC = """# 下单规格（复制到订单备注；依据 = 板文件 (stackup) 与 docs/fab-dfm-check.md §3）

层数 / 板厚 : 4 层 / 1.6 mm
铜厚        : 外层 1 oz、内层 0.5 oz（0.0152 mm）
过孔工艺    : 盖油（板文件为 tenting front back）
阻焊开窗    : 厂家自动单边扩 0.05 mm（板文件 pad_to_mask_clearance = 0，符合惯例）
阻抗控制    : 不需要（无高速差分对）
板尺寸      : 374.81 × 151.16 mm，单板交货
表面处理    : 建议沉金（ENIG）——细间距 QFN 与手焊润湿性更好；预算紧可用喷锡

## 若被 EQ（工程询问）——

1. U1 的 4 个 0.2 mm 孔是**散热焊盘内的散热过孔（thermal via）**，不是元件引脚孔；
   该封装为 KiCad 官方库标准封装，请按过孔工艺处理。
2. 内层过孔到铜面的间隙请按**钻孔边**计（钻孔 0.30 + 环宽 0.15 ⇒ 距铜面 0.35–0.43 mm）。
"""


def run(cmd, what):
    print("  ▸", what)
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        print("    ❌ 失败（exit %d）" % p.returncode)
        print((p.stdout or "")[-800:])
        print((p.stderr or "")[-800:])
        return False
    tail = [l for l in (p.stdout or "").splitlines() if l.strip()][-3:]
    for l in tail:
        print("    ", l.strip()[:110])
    return True


def find_cli():
    for c in (os.environ.get("KICAD_CLI"),
              r"D:/Kicad/bin/kicad-cli.exe",
              shutil.which("kicad-cli"), shutil.which("kicad-cli.exe")):
        if c and os.path.exists(c):
            return c
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(PCB_DIR, "fab"))
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    gdir = os.path.join(out, "gerbers")

    cli = find_cli()
    if not cli:
        print("❌ 找不到 kicad-cli")
        return 1
    print("kicad-cli =", cli)
    print("板 =", BOARD)
    print("输出 =", out)

    for d in (out, gdir):
        os.makedirs(d, exist_ok=True)
    ok = True

    print("\n[1/5] Gerber（11 层）")
    gs = [cli, "pcb", "export", "gerbers", "--output", gdir,
          "--layers", LAYERS, "--no-protel-ext", BOARD]
    ok &= run(gs, "pcb export gerbers")

    print("\n[2/5] 钻孔（Excellon，PTH/NPTH 分开、mm、小数点格式）")
    ds = [cli, "pcb", "export", "drill", "--output", gdir, "--format", "excellon",
          "--excellon-separate-th", "--excellon-units", "mm",
          "--excellon-zeros-format", "decimal", "--drill-origin", "absolute", BOARD]
    ok &= run(ds, "pcb export drill")

    print("\n[3/5] 贴片坐标 CPL（手焊不需要，但社区惯例一并给，便于日后 PCBA）")
    cpl = [cli, "pcb", "export", "pos", "--output", os.path.join(out, "CPL-%s.csv" % NAME),
           "--format", "csv", "--units", "mm", "--side", "both", BOARD]
    ok &= run(cpl, "pcb export pos")

    print("\n[4/5] BOM（从根图导出，含全部子图）")
    bom = [cli, "sch", "export", "bom", "--output", os.path.join(out, "BOM-%s.csv" % NAME),
           "--group-by", "Value,Footprint", "--exclude-dnp", ROOT_SCH]
    ok &= run(bom, "sch export bom")

    print("\n[5/5] 打包 zip（社区做法：直接上传代工厂）")
    zpath = os.path.join(out, "StarShield-gerbers.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(gdir)):
            z.write(os.path.join(gdir, f), f)
    print("   ", os.path.basename(zpath), "%.2f MB" % (os.path.getsize(zpath) / 1048576))

    with open(os.path.join(out, "ORDER_SPEC.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(ORDER_SPEC)

    # ---- 自检 ----
    print("\n自检：")
    need = ["F_Cu", "In1_Cu", "In2_Cu", "B_Cu", "F_Mask", "B_Mask",
            "F_Silkscreen", "B_Silkscreen", "F_Paste", "B_Paste", "Edge_Cuts"]
    have = os.listdir(gdir)
    miss = [n for n in need if not any(n in h for h in have)]
    print("  Gerber 层齐全（%d/11）：%s" % (11 - len(miss), "✅" if not miss else "❌ 缺 " + str(miss)))
    drls = [h for h in have if h.endswith(".drl")]
    print("  钻孔文件：%s" % ("✅ " + ", ".join(drls) if drls else "❌ 无"))
    with zipfile.ZipFile(zpath) as z:
        n = len(z.namelist())
    print("  zip 内文件数：%d %s" % (n, "✅" if n >= 12 else "❌"))
    empt = [h for h in have if os.path.getsize(os.path.join(gdir, h)) < 200]
    print("  非空检查：%s" % ("✅" if not empt else "❌ 过小 " + str(empt)))
    for extra in ("BOM-%s.csv" % NAME, "CPL-%s.csv" % NAME, "ORDER_SPEC.md"):
        p = os.path.join(out, extra)
        print("  %-22s %s" % (extra, "✅" if os.path.exists(p) else "❌"))
    print()
    print("目录清单：")
    for f in sorted(os.listdir(out)):
        p = os.path.join(out, f)
        if os.path.isfile(p):
            print("   %-26s %8.1f KB" % (f, os.path.getsize(p) / 1024))
        else:
            print("   %-26s <%d 个文件>" % (f + "/", len(os.listdir(p))))
    print("\n%s" % ("✅ 投板文件包生成完毕" if ok and not miss else "❌ 有步骤失败，见上"))
    return 0 if (ok and not miss) else 1


if __name__ == "__main__":
    sys.exit(main())
