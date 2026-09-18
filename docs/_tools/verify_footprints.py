#!/usr/bin/env python3
"""verify_footprints.py —— 全工程封装（Footprint）存在性核查（B3）

为什么要有它：
    「这个封装在库里存不存在」此前靠人工看，矩阵子图 95 个热插拔座的封装
    不在官方库里这件事，就是以 95 条 ERC `footprint_link_issues` warning 的形式
    默默存在的 —— 没人逐条看过。B3 把它变成**一条命令可复现的断言**。

做法：
    直接扫描 4 张子图的 `.kicad_sch`，提取每个元件的 `Footprint` 属性，
    逐个去本机 KiCad 封装库（`<lib>.pretty/<name>.kicad_mod`）查存在性。
    ⇒ 不依赖任何生成器的内部常量，改了数据源也能抓到。

退出码 0 = 全部封装都在库里（或都在豁免清单里）。
"""
import collections
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PCB = os.path.join(ROOT, "hardware", "pcb", "StarShield")

SHEETS = [
    ("矩阵 R0-R1", "matrix/matrix_r012.kicad_sch"),
    ("矩阵 R2-R3", "matrix/matrix_r234.kicad_sch"),
    ("矩阵 R4-R5", "matrix/matrix_r45.kicad_sch"),
    ("电源", "power/power.kicad_sch"),
    ("控制板", "control/control.kicad_sch"),
    ("RGB", "rgb/rgb.kicad_sch"),
]

# 已知缺失 / 待办：写成豁免，避免每次都刷屏；但**必须带理由**，且要能追溯。
#   键 = 完整 fp id（"库:名"）
ALLOWED_MISSING = {
    # ✅ B3 已定案（2026-09-18，用户选「自画」）⇒ 矩阵子图已改用
    #    `StarShield:SW_MX_Hotswap_Optional_<宽度>u`（工程自带库，由 gen_footprints.py 生成）。
    #    以下旧值**不应再出现**；若哪天子图里又冒出来，说明有生成器没同步。
    "Button_Switch_Keyboard:SW_MX_Hotswap":
        "已被 StarShield:SW_MX_Hotswap_Optional_* 取代（B3 自画）；若出现说明有生成器未同步",
}


def find_footprint_dirs():
    """定位封装库根目录：先看**工程自带库**，再看 KiCad 官方库。

    工程自带库 `hardware/pcb/StarShield/footprints/` 存放本项目自画的封装
    （B3：MX 热插拔座 `StarShield:SW_MX_Hotswap_Optional_*`）——
    因为官方库没有热插拔座，而社区库是 CC BY-SA 4.0（无官方库那种例外条款）不可引入。
    """
    proj = os.path.join(PCB, "footprints")
    if os.path.isdir(proj):
        return proj
    cands = []
    env = os.environ.get("KICAD_FOOTPRINT_DIR")
    if env:
        cands.append(env)
    import glob
    for drive in "CDEFGH":
        cands += glob.glob(rf"{drive}:\Kicad\share\kicad\footprints")
        cands += glob.glob(rf"{drive}:\Program Files\KiCad\*\share\kicad\footprints")
    cands += ["/usr/share/kicad/footprints",
              "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"]
    for c in cands:
        if os.path.isdir(c):
            return c
    return None


# 官方库（用于「工程库里没有就去官方库找」的兜底查找）
OFFICIAL_FP_DIRS = None


def _official_dirs():
    global OFFICIAL_FP_DIRS
    if OFFICIAL_FP_DIRS is None:
        import glob
        cands = []
        env = os.environ.get("KICAD_FOOTPRINT_DIR")
        if env:
            cands.append(env)
        for drive in "CDEFGH":
            cands += glob.glob(rf"{drive}:\Kicad\share\kicad\footprints")
            cands += glob.glob(rf"{drive}:\Program Files\KiCad\*\share\kicad\footprints")
        cands += ["/usr/share/kicad/footprints",
                  "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"]
        OFFICIAL_FP_DIRS = [c for c in cands if os.path.isdir(c)]
    return OFFICIAL_FP_DIRS


def collect_footprints():
    """返回 [(sheet_name, ref, fp_id)]，ref 用位号（便于定位）。"""
    out = []
    for label, rel in SHEETS:
        path = os.path.join(PCB, rel)
        if not os.path.exists(path):
            print(f"⚠️ 找不到子图 {rel}（跳过）")
            continue
        txt = open(path, encoding="utf-8").read()
        # 每个 symbol 块：抓 Reference 与 Footprint 两属性
        for blk in txt.split("\t(symbol (lib_id ")[1:]:
            m_ref = re.search(r'\(property "Reference" "([^"]+)"', blk)
            m_fp = re.search(r'\(property "Footprint" "([^"]+)"', blk)
            if m_fp and m_fp.group(1):
                out.append((label, m_ref.group(1) if m_ref else "?", m_fp.group(1)))
    return out


def main():
    fpdir = find_footprint_dirs()
    if not fpdir:
        print("❌ 找不到 KiCad 封装库目录（可用环境变量 KICAD_FOOTPRINT_DIR 指定）")
        return 2
    print(f"KiCad 封装库：{fpdir}")

    items = collect_footprints()
    print(f"共收集 {len(items)} 个元件的封装属性")

    # 按 fp id 聚合（同一封装出现几百次只查一次）
    by_fp = collections.defaultdict(list)
    for label, ref, fp in items:
        by_fp[fp].append((label, ref))

    missing, ok = {}, {}
    for fp, where in sorted(by_fp.items()):
        if ":" not in fp:
            missing[fp] = (where, "格式非法（应为 库:名）")
            continue
        lib, name = fp.split(":", 1)
        # 先查工程自带库，再退回官方库
        path = os.path.join(fpdir, f"{lib}.pretty", f"{name}.kicad_mod")
        if not os.path.exists(path):
            for od in _official_dirs():
                p2 = os.path.join(od, f"{lib}.pretty", f"{name}.kicad_mod")
                if os.path.exists(p2):
                    path = p2
                    break
        if os.path.exists(path):
            ok[fp] = (where, path)
        else:
            missing[fp] = (where, f"不存在：{lib}.pretty/{name}.kicad_mod（工程库与官方库均无）")

    print("=" * 70)
    print(f"A. 存在于官方库的封装：{len(ok)} 种（覆盖 {sum(len(v) for v, _ in ok.values())} 个元件）")
    print("=" * 70)
    for fp, (where, _) in sorted(ok.items()):
        print(f"  ✅ {fp:62} × {len(where):3}")

    print("=" * 70)
    print(f"B. 缺失 / 非官方的封装：{len(missing)} 种（覆盖 {sum(len(v) for v, _ in missing.values())} 个元件）")
    print("=" * 70)
    unhandled = {}
    for fp, (where, why) in sorted(missing.items()):
        n = len(where)
        sample = where[0]
        if fp in ALLOWED_MISSING:
            print(f"  🟡 {fp:62} × {n:3}  [已豁免] {ALLOWED_MISSING[fp]}")
            print(f"       样例：{sample[0]} / {sample[1]}")
        else:
            print(f"  ❌ {fp:62} × {n:3}  {why}")
            print(f"       样例：{sample[0]} / {sample[1]}")
            unhandled[fp] = (where, why)

    print("=" * 70)
    if unhandled:
        print(f"结论：❌ 有 {len(unhandled)} 种封装未处理（B3 未完）")
        for fp in unhandled:
            print("   -", fp)
        return 1
    if missing:
        print(f"结论：🟡 全部封装已登记（{len(missing)} 种为已知豁免，见 ALLOWED_MISSING）")
        return 0
    print("结论：✅ 全部封装均存在于 KiCad 官方库")
    return 0


if __name__ == "__main__":
    sys.exit(main())
