#!/usr/bin/env python3
"""verify_power.py —— 校验电源子图：ERC 零 error + 网表逐节点断言

两类断言，作用不同，都要有：
  A. **派生断言**：把 docs/_tools/power_design.py 的连接表按网络分组，跟 kicad-cli 导出的
     真实网表逐一比对。这能抓出**版式/坐标错误**（引脚画歪了、短线撞了别的网）。
  B. **具名断言**：把「安全关键」的几条连接显式写死（高边开关 S/D 方向、EN1 接 OUT、
     ~CE/EN2/TD 接 GND …）。这能抓出 power_design.py 里被误改的**设计错误** ——
     派生断言此时会「跟着一起错」，所以必须另有一套不随数据漂移的判据。

输出临时文件放在系统临时目录，不污染 git status。
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
import power_design as D  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
PCB = os.path.join(ROOT, "hardware", "pcb", "StarShield")
SHEET = os.path.join(PCB, D.SHEET_FILE)

# 允许保留的 ERC warning（类型, 涉及对象）；其余任何违规都算失败。
# isolated_pin_label：VLED / RGB_PWR_EN 的另一端在尚未绘制的 B2 控制板子图上。
ALLOWED_WARNINGS = {
    ("isolated_pin_label", "Global Label 'VLED'"),
    ("isolated_pin_label", "Global Label 'RGB_PWR_EN'"),
}


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
    """返回 {网名(去前导斜杠): {(ref, pin)}}"""
    txt = open(path, encoding="utf-8").read()
    nets = {}
    for m in re.finditer(r'\(net\s*\(code\s+"[^"]*"\)\s*\(name\s+"([^"]+)"\)(.*?)\n\t\t\)\n', txt, re.S):
        name, body = m.group(1).lstrip("/"), m.group(2)
        nets[name] = set(re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', body))
    return nets


def main():
    cli = find_kicad_cli()
    if not cli:
        print("❌ 找不到 kicad-cli（可用环境变量 KICAD_CLI 指定）")
        return 2
    if not os.path.exists(SHEET):
        print(f"❌ 找不到原理图 {SHEET}，先跑 docs/_tools/gen_power_sch.py")
        return 2

    tmp = tempfile.mkdtemp(prefix="ss_power_verify_")
    try:
        net = os.path.join(tmp, "power.net")
        r1 = subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadsexpr",
                             "-o", net, SHEET], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
        r2 = subprocess.run([cli, "sch", "erc", "--severity-all", "--output",
                             os.path.join(tmp, "power.erc"), SHEET],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r1.returncode != 0 or not os.path.exists(net):
            print("❌ 网表导出失败（原理图可能无法解析）")
            print((r1.stdout or "") + (r1.stderr or ""))
            return 1
        got = parse_netlist(net)
        erc = open(os.path.join(tmp, "power.erc"), encoding="utf-8", errors="replace").read()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    fails = []

    def check(label, ok, detail=""):
        print(f"  {'✅' if ok else '❌'} {label}" + (f"   {detail}" if detail else ""))
        if not ok:
            fails.append(label)

    print("=" * 66)
    print("A. 派生断言：网表 == power_design.py 的连接表")
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
              "" if got.get(n) == nodes else f"期望 {sorted(nodes)} 实得 {sorted(got.get(n) or [])}")
    extra = sorted(set(got) - set(want) - {n for n in got if n.startswith("unconnected-")})
    check("没有设计之外的多余网络", not extra, str(extra))

    # 明确不接的引脚：KiCad 会为它们生成 unconnected-<REF>-<名>-Pad<PIN> 的单点网络，
    # 因此「设计为 NC 的引脚」不应出现在任何真实网络里。
    joined = set()
    for n, nodes in got.items():
        if not n.startswith("unconnected-"):
            joined |= nodes
    nc_missing = sorted(f"{r}.{p}" for r, p in nc if (r, p) in joined)
    check("设计为 NC 的引脚确实不接任何网络", not nc_missing, str(nc_missing))
    check("NC 引脚数量 = 8（D+ D- SBU1 SBU2 各 2 个 + TMR + PGOOD）",
          len(nc) == 8, f"实得 {len(nc)}")

    print()
    print("=" * 66)
    print("B. 具名断言：安全关键连接（不随数据源漂移）")
    print("=" * 66)
    check("高边 P-MOS：源极 S=Q1.2 接 OUT，漏极 D=Q1.3 接 VLED（体二极管方向正确）",
          ("Q1", "2") in got.get("OUT", set()) and got.get("VLED") == {("Q1", "3")},
          "反接会让 LED 轨经体二极管常通")
    check("N-MOS 反相级：Q2.1(G) 由 RGB_PWR_EN 驱动，Q2.2(S)=GND，Q2.3(D)=Q1 栅极",
          ("Q2", "1") in got.get("Q2_G", set()) and ("Q2", "2") in got.get("GND", set())
          and ("Q2", "3") in got.get("Q1_G", set()))
    check("Q1 栅极上拉 R7 到 OUT（保证 Q2 截止时可靠关断）",
          got.get("Q1_G") == {("Q1", "1"), ("Q2", "3"), ("R7", "2")}
          and ("R7", "1") in got.get("OUT", set()))
    check("Q2 栅极下拉 R9 到 GND（MCU 未初始化时 LED 轨关断）",
          ("R9", "1") in got.get("Q2_G", set()) and ("R9", "2") in got.get("GND", set()))
    check("负载挂在 OUT 而不是 BAT（ADR-0002 电源路径管理）",
          ("Q1", "2") in got.get("OUT", set()) and ("Q1", "2") not in got.get("VBAT", set()))
    check("EN2=GND 且 EN1=OUT ⇒ USB500 档（500 mA 输入上限）",
          ("U1", "5") in got.get("GND", set()) and ("U1", "6") in got.get("OUT", set()))
    check("~CE 接 VSS = 充电常开；TD 接 VSS = 使能终止",
          ("U1", "4") in got.get("GND", set()) and ("U1", "15") in got.get("GND", set()))
    check("ILIM 装了 R3 且 R3 另一端接地（悬空会关闭所有充电）",
          got.get("ILIM") == {("R3", "1"), ("U1", "12")} and ("R3", "2") in got.get("GND", set()))
    check("ISET 装了 R4（0.5 A）；TS 经 R5 到 VSS（禁用温测）",
          got.get("ISET") == {("R4", "1"), ("U1", "16")} and got.get("TS") == {("R5", "1"), ("U1", "1")})
    check("散热焊盘 EP(U1.17) 接地", ("U1", "17") in got.get("GND", set()))
    check("CC1 / CC2 各自 5.1k 下拉且互不短接",
          got.get("CC1") == {("J1", "A5"), ("R1", "1")} and got.get("CC2") == {("J1", "B5"), ("R2", "1")})
    check("充电 LED 极性：OUT → R6 → LED 阳极，阴极接 ~CHG 开漏",
          got.get("CHG_LED_A") == {("D1", "2"), ("R6", "2")} and got.get("nCHG") == {("D1", "1"), ("U1", "9")}
          and ("R6", "1") in got.get("OUT", set()))
    check("USB-C 四个 VBUS 焊盘并联接 IN、四个 GND 焊盘接地",
          {("J1", p) for p in ("A4", "A9", "B4", "B9")} <= got.get("VBUS", set())
          and {("J1", p) for p in ("A1", "A12", "B1", "B12")} <= got.get("GND", set()))

    print()
    print("=" * 66)
    print("C. ERC 闸门")
    print("=" * 66)
    errs = re.findall(r"\[([a-z_0-9]+)\]:([^\n]*)\n\s*; error\n\s*@\([^)]*\): ([^\n]*)", erc)
    warns = re.findall(r"\[([a-z_0-9]+)\]:([^\n]*)\n\s*; warning\n\s*@\([^)]*\): ([^\n]*)", erc)
    check("ERC error = 0", not errs, str(errs[:6]))
    unexpected = [(t, obj.strip()) for t, _m, obj in warns
                  if (t, obj.strip()) not in ALLOWED_WARNINGS]
    check("ERC warning 全部在已知豁免清单内", not unexpected, str(unexpected[:6]))
    for t, _m, obj in warns:
        print(f"      允许保留： [{t}] {obj.strip()}")

    print("=" * 66)
    if fails:
        print(f"结论：❌ 未通过（{len(fails)} 项）")
        for f in fails:
            print("   -", f)
        return 1
    print("结论：✅ 电源子图校验全部通过（网表与设计一致、ERC 0 error）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
