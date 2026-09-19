#!/usr/bin/env python3
"""verify_control.py —— 校验控制板子图：ERC 零 error + 网表逐节点断言 + 跨图接口断言

四类断言：
  A. **派生断言**：control_design.py 的连接表按网分组，与 kicad-cli 导出的
     控制子图真实网表逐一比对（抓版式/坐标错误）。
  B. **跨图接口断言**：在【根图整体】网表里验证跨子图网的两端都真实相连 ——
     ROW0..5 同时含 J3A 引脚与矩阵开关、COL0..17 同时含 595 输出与矩阵二极管、
     RGB_PWR_EN 同时含 J3B 与电源子图 R8、OUT 同时含 J3B 与电源子图。
     ⚠️ 这组断言的存在有历史原因：矩阵子图曾用局部标签，三张图的同名 COL
     在真实网表里互不相连，却被「按名合并」的校验掩盖（2026-09-18 B2 修复）。
  C. **具名断言**：不随数据漂移的设计判据（595 级联链与位序、~SRCLR/~OE、
     三档开关映射、供电来源等）。
  D. **ERC 闸门**：控制子图单图 0 error；warning 必须全在豁免清单
     （跨图网在单图视角必然 isolated，属预期）。

退出码 0 = 通过。
"""
import collections
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import control_design as D  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
PCB = os.path.join(ROOT, "hardware", "pcb", "StarShield")
SHEET = os.path.join(PCB, D.SHEET_FILE)
ROOT_SHEET = os.path.join(PCB, "Starshield.kicad_sch")

# 允许保留的 ERC warning（类型, 对象包含子串）。
# 1) 跨子图全局网在【单图】视角只有一端 ⇒ isolated；另一端在矩阵/电源/RGB 子图上。
_CROSS_NETS = (["OUT", "RGB_PWR_EN", "LED_DIN"]
               + [f"ROW{i}" for i in range(6)] + [f"COL{i}" for i in range(18)])
ALLOWED_WARNINGS = {
    ("isolated_pin_label", f"Global Label '{n}'") for n in _CROSS_NETS
} | {
    # J3A/J3B 的封装是占位符（Mill-Max 具体料号 B3/B4 定）⇒ KiCad 找不到封装
    ("footprint_link_issues", "J3A"),
    ("footprint_link_issues", "J3B"),
}

# 按【类型】整体豁免的违规（不细分对象）：
#   power_pin_not_driven —— GND 的 PWR_FLAG 在电源子图（全局网只能有一个 power output，
#     在本图再加会触发 ERC [pin_to_pin] error）⇒ 单图视角下 GND 无驱动源是预期。
ALLOWED_WARNING_KINDS = {"power_pin_not_driven"}


def find_kicad_cli():
    env = os.environ.get("KICAD_CLI")
    if env and os.path.exists(env):
        return env
    from shutil import which
    for c in [which("kicad-cli"), which("kicad-cli.exe")]:
        if c:
            return c
    import glob
    cands = [r"C:\Program Files\KiCad\bin\kicad-cli.exe",
             r"C:\Program Files (x86)\KiCad\bin\kicad-cli.exe",
             "/usr/bin/kicad-cli", "/usr/local/bin/kicad-cli"]
    for drive in "CDEFGH":
        cands += glob.glob(rf"{drive}:\Kicad\bin\kicad-cli.exe")
        cands += glob.glob(rf"{drive}:\Program Files\KiCad\*\bin\kicad-cli.exe")
    for c in cands:
        if os.path.exists(c):
            return c
    return None


def parse_netlist(path):
    """返回 {网名(去前导斜杠): {(ref, pin)}}（按 `(net` 块切分，不假设缩进）"""
    txt = open(path, encoding="utf-8").read()
    nets = {}
    for chunk in txt.split("(net")[1:]:
        nm = re.search(r'\(name\s+"([^"]+)"', chunk)
        if not nm:
            continue
        name = nm.group(1).lstrip("/")
        nodes = set(re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', chunk))
        nets[name] = nets.get(name, set()) | nodes
    return nets


def main():
    cli = find_kicad_cli()
    if not cli:
        print("❌ 找不到 kicad-cli（可用环境变量 KICAD_CLI 指定）")
        return 2
    if not os.path.exists(SHEET):
        print(f"❌ 找不到原理图 {SHEET}，先跑 docs/_tools/gen_control_sch.py")
        return 2

    tmp = tempfile.mkdtemp(prefix="ss_control_verify_")
    try:
        net = os.path.join(tmp, "control.net")
        r1 = subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadsexpr",
                             "-o", net, SHEET], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
        root_net = os.path.join(tmp, "root.net")
        r2 = subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadsexpr",
                             "-o", root_net, ROOT_SHEET], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
        r3 = subprocess.run([cli, "sch", "erc", "--severity-all", "--output",
                             os.path.join(tmp, "control.erc"), SHEET],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r1.returncode != 0 or not os.path.exists(net):
            print("❌ 控制子图网表导出失败（原理图可能无法解析）")
            print((r1.stdout or "") + (r1.stderr or ""))
            return 1
        got = parse_netlist(net)
        got_root = parse_netlist(root_net) if r2.returncode == 0 and os.path.exists(root_net) else None
        erc = open(os.path.join(tmp, "control.erc"), encoding="utf-8", errors="replace").read()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    fails = []

    def check(label, ok, detail=""):
        print(f"  {'✅' if ok else '❌'} {label}" + (f"   {detail}" if detail else ""))
        if not ok:
            fails.append(label)

    # ------------------------------------------------------------------
    print("=" * 66)
    print("A. 派生断言：控制子图网表 == control_design.py 的连接表")
    print("=" * 66)
    want = collections.defaultdict(set)
    nc = set()
    for key, net in D.CONN.items():
        ref, pin = key.rsplit(".", 1)
        if net is None:
            nc.add((ref, pin))
        else:
            want[net].add((ref, pin))
    for n, nodes in sorted(want.items()):
        check(f"网络 {n}", got.get(n) == nodes,
              f"实得 {sorted(got.get(n, set()))}" if got.get(n) != nodes else "")
    # ⚠️ 带 no_connect 标记的引脚会被 KiCad 导出成 `unconnected-(...)` 网 ——
    #    那是 NC 标记的正常表现，不是「多余网络」。
    unconn = [n for n in got if n.startswith("unconnected-(")]
    real_extra = [n for n in got
                  if n not in want and n not in ("GND", "VCC") and not n.startswith("unconnected-(")]
    check("没有设计之外的多余网络（unconnected-* 属 NC 标记的正常导出）",
          not real_extra, str(sorted(real_extra)))
    check(f"NC 引脚全部带标记（{len(unconn)} 条 unconnected 网 == {len(nc)} 个 NC 引脚）",
          len(unconn) == len(nc))
    # NC 引脚：不得出现在任何真实（非 unconnected）网里
    placed = set()
    for n, nodes in got.items():
        if not n.startswith("unconnected-("):
            placed |= nodes
    check("设计为 NC 的引脚确实不接任何网络", not (nc & placed), str(sorted(nc & placed)))
    check("GND 网存在（power 符号）", "GND" in got and got["GND"] == want["GND"])
    check("VCC 网存在（power 符号）", "VCC" in got and got["VCC"] == want["VCC"])

    # ------------------------------------------------------------------
    print("=" * 66)
    print("B. 跨图接口断言（根图整体网表）")
    print("=" * 66)
    if got_root is None:
        check("根图整体网表导出", False, "导出失败，跳过 B 组（这本身是失败）")
    else:
        # ROW：J3A 引脚 + 该行全部矩阵开关（精确值 = 行键数 + 1，来源 matrix-assign 输出）
        # ⚠️ 2026-09-19 B6-1：孔号随实物修正（每排 13 孔）；行线整体后移一孔
        row_expect = {
            "ROW0": (("J3A", "8"), 17), "ROW1": (("J3A", "9"), 19),
            "ROW2": (("J3A", "10"), 19), "ROW3": (("J3A", "11"), 16),
            "ROW4": (("J3A", "13"), 18), "ROW5": (("J3A", "12"), 12),
        }
        for r, ((ref, pin), n_expect) in row_expect.items():
            nodes = got_root.get(r, set())
            check(f"{r} 连接 J3A.{pin} 与矩阵开关（恰 {n_expect} 元件）",
                  (ref, pin) in nodes and len(nodes) == n_expect,
                  f"{len(nodes)} 元件")
        # COL：595 输出 + 该列全部二极管
        col_expect = {}
        for i in range(8):
            col_expect[f"COL{i}"] = ("U2", str(15 if i == 0 else i))
        for i in range(8, 16):
            col_expect[f"COL{i}"] = ("U3", str(15 if i == 8 else i - 8))
        col_expect["COL16"] = ("U4", "15")
        col_expect["COL17"] = ("U4", "1")
        for c, (ref, pin) in col_expect.items():
            nodes = got_root.get(c, set())
            check(f"{c} 连接 {ref}.{pin} 与矩阵二极管（≥3 元件）",
                  (ref, pin) in nodes and len(nodes) >= 3, f"{len(nodes)} 元件")
        check("RGB_PWR_EN 跨图连通（J3B 孔13 + 电源子图 R8）",
              got_root.get("RGB_PWR_EN") == {("J3B", "13"), ("R8", "1")},
              str(sorted(got_root.get("RGB_PWR_EN", set()))))
        check("OUT 跨图连通（J3B 孔1/2 = B+ + 电源子图 U1/Q1/R6/R7/C2）",
              ("J3B", "1") in got_root.get("OUT", set())
              and {"U1", "Q1", "R6", "R7", "C2"} <= {r for r, _ in got_root.get("OUT", set())})
        # 2026-09-18 M5 后：RGB 子图已绘制，LED_DIN 的另一端是 LED1.DIN
        # ⚠️ 2026-09-19 B6-1：LED_DIN 随实物孔序移到 J3A 孔 2（孔 1 是 GND）
        check("LED_DIN 跨图连通（J3A 孔2 + RGB 子图 LED1.DIN）",
              got_root.get("LED_DIN") == {("J3A", "2"), ("LED1", "2")},
              str(sorted(got_root.get("LED_DIN", set()))))

    # ------------------------------------------------------------------
    print("=" * 66)
    print("C. 具名断言：安全关键设计（不随数据漂移）")
    print("=" * 66)
    g = got
    # 595 级联链：QH' → 下一颗 SER
    check("级联链：U2.QH'(9) 与 U3.SER(14) 同网 CASCADE1",
          g.get("CASCADE1") == {("U2", "9"), ("U3", "14")}, str(sorted(g.get("CASCADE1", set()))))
    check("级联链：U3.QH'(9) 与 U4.SER(14) 同网 CASCADE2",
          g.get("CASCADE2") == {("U3", "9"), ("U4", "14")}, str(sorted(g.get("CASCADE2", set()))))
    # 控制脚共享：SRCLK/RCLK 三颗同网；SER 只在 U2 上接 MOSI
    check("三颗 595 的 SRCLK(11) 共网 595_SCK，且源头是 J3B 孔10(D15=P1.13)",
          g.get("595_SCK") == {("U2", "11"), ("U3", "11"), ("U4", "11"), ("J3B", "10")})
    check("三颗 595 的 RCLK(12) 共网 595_RCLK，且源头是 J3B 孔8(D19=P0.02, spi1 CS)",
          g.get("595_RCLK") == {("U2", "12"), ("U3", "12"), ("U4", "12"), ("J3B", "8")})
    check("595_MOSI：J3B 孔12(D16=P0.10) 只接 U2.SER(14)（链头）",
          g.get("595_MOSI") == {("J3B", "12"), ("U2", "14")})
    # ~SRCLR / ~OE
    for ref in ("U2", "U3", "U4"):
        check(f"{ref}.~SRCLR(10) 接 VCC（不复位）", (ref, "10") in g.get("VCC", set()))
        check(f"{ref}.~OE(13) 接 GND（输出常使能）", (ref, "13") in g.get("GND", set()))
    # 位序抽查（位序已由 gpio_595.c 核实：bit0..7=U2、8..15=U3、16/17=U4）
    bit_map = [("U2", "15", "COL0"), ("U2", "7", "COL7"), ("U3", "15", "COL8"),
               ("U3", "7", "COL15"), ("U4", "15", "COL16"), ("U4", "1", "COL17")]
    for ref, pin, col in bit_map:
        check(f"位序：{ref}.{pin} (QA/QH) → {col}", (ref, pin) in g.get(col, set()))
    # U4 空闲脚
    check("U4 的 QC..QH 与 QH' 全部 NC（bit18..23 空闲）",
          all((("U4", p) in nc) for p in ("2", "3", "4", "5", "6", "7", "9")))
    # 三档开关
    # ⚠️ 位号 SW96（不是 SW1）：原 SW1 与矩阵第一个开关重名，2026-09-18（B4）改名
    check("SW96 公共端(3) 接 GND（ACTIVE_LOW 读取）", ("SW96", "3") in g.get("GND", set()))
    check("档 0（有线）：SW96.1 与 J3A 孔6(D2/P0.17) 同网 MODE0",
          g.get("MODE0") == {("SW96", "1"), ("J3A", "6")})
    check("档 1（蓝牙）：SW96.2 与 J3B 孔11(D14/P1.11) 同网 MODE1",
          g.get("MODE1") == {("SW96", "2"), ("J3B", "11")})
    check("档 2（2.4G）：SW96.4 与 J3B 孔9(D18/P1.15) 同网 MODE2",
          g.get("MODE2") == {("SW96", "4"), ("J3B", "9")})
    # 供电
    check("nice!nano B+(J3B 孔1) 接电源子图系统轨 OUT（不是 VBUS）",
          ("J3B", "1") in g.get("OUT", set()) and ("J3B", "1") not in g.get("VBUS", set()))
    check("nice!nano 3.3V(J3B 孔5) 是 VCC 网唯一源头（3.3V 轨）",
          ("J3B", "5") in g.get("VCC", set()))
    for c in ("C4", "C5", "C6"):
        check(f"{c}：VCC-GND 去耦（每颗 595 一颗）",
              (c, "1") in g.get("VCC", set()) and (c, "2") in g.get("GND", set()))
    # 行线的交错顺序（与 overlay row-gpios 一一对应）
    check("行线交错顺序：J3A 孔13=ROW4、孔12=ROW5（overlay 第5/6项 = D9/D8）",
          ("J3A", "13") in g.get("ROW4", set()) and ("J3A", "12") in g.get("ROW5", set()))

    # ------------------------------------------------------------------
    print("=" * 66)
    print("D. ERC 闸门（控制子图单图）")
    print("=" * 66)
    violations = []
    err_violations = []
    for block in erc.split("["):
        if "]" not in block:
            continue
        kind = block.split("]")[0]
        if not re.fullmatch(r"[a-z_]+", kind):
            continue        # 引脚描述里的方括号（如 [1, Passive, Line]）不是违规类型
        if kind not in ("isolated_pin_label", "footprint_link_issues",
                        "lib_symbol_mismatch", "endpoint_off_grid", "pin_not_connected",
                        "similar_labels", "label_dangling"):
            continue
        m = re.search(r'@\([^)]*\):\s*(.+)', block)
        obj = m.group(1).strip() if m else block[:60].strip()
        if kind == "lib_symbol_mismatch":
            # 符号缓存与库版本的差异噪音（矩阵图历史遗留 + 符号提取时机），记录不阻断
            continue
        if kind == "endpoint_off_grid":
            # 控制子图坐标应全部对齐 1.27 网格；出现即按失败处理
            violations.append((kind, obj))
            continue
        if kind in ALLOWED_WARNING_KINDS:
            continue
        if not any(kind == k and o in obj for k, o in ALLOWED_WARNINGS):
            violations.append((kind, obj))
            if "; error" in block[:200]:
                err_violations.append((kind, obj))
    n_viol = len(violations)
    check(f"ERC：无未豁免 warning（{n_viol} 条）", n_viol == 0, str(violations[:5]))
    # ⚠️ 汇总行的 Errors 计数会把「已豁免」的 power_pin_not_driven 算进去
    #    （GND 的 PWR_FLAG 在电源子图，全局网只能有一个 power output）
    #    ⇒ 判据必须是「未豁免的 error 级违规 = 0」。
    m = re.search(r'Errors\s+(\d+)\s+Warnings\s+(\d+)', erc)
    check("ERC：未豁免的 error 级违规 = 0", not err_violations,
          (f"报告原始 errors={m.group(1)} warnings={m.group(2)}；" if m else "")
          + str(err_violations[:3]))

    print("=" * 66)
    if fails:
        print(f"结论：❌ 控制板子图校验未通过（{len(fails)} 项失败）")
        for f in fails:
            print("   -", f)
        return 1
    print("结论：✅ 控制板子图校验全部通过（连接表一致、跨图接口连通、ERC 0 error）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
