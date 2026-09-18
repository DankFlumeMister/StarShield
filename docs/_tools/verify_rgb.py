#!/usr/bin/env python3
"""verify_rgb.py —— 校验 RGB 子图：ERC 零 error + 网表断言 + 跨图接口断言（M5）

四组断言：
  A. 派生断言：rgb_design.py（由 matrix.json 生成）的连接表 vs 子图真实网表；
  B. 跨图接口：根图整体网表中 VLED 同时含电源子图 Q1 与 95 颗灯珠、
     LED_DIN 同时含控制子图 J3A.1 与 LED1.DIN；
  C. 具名断言：数据链顺序（LEDi.DOUT ↔ LED(i+1).DIN）、链尾 NC、
     每颗 VDD→VLED / VSS→GND、灯珠数 95、位号与 index 对应；
  D. ERC 闸门：0 error，warning 全在豁免清单。

⚠️ 单图导出时局部网名无 sheet 前缀；根图整体导出时局部网名带前缀
   （形如 `RGB（...）/LED_DIN_95`）⇒ 一律按「最后一段」取网名。
"""
import collections
import json
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
import rgb_design as D  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
PCB = os.path.join(ROOT, "hardware", "pcb", "StarShield")
SHEET = os.path.join(PCB, D.SHEET_FILE)
ROOT_SHEET = os.path.join(PCB, "Starshield.kicad_sch")
MATRIX = os.path.join(ROOT, "docs", "_generated", "matrix.json")

# 单图视角的预期违规（另一端在别的子图上 / 驱动源是连接器 passive 引脚）：
# 1) LED_DIN 在本图只有 LED1.DIN 一端 ⇒ isolated；
# 2) LED1 的 DIN 是 input 引脚，真实驱动源是控制子图 J3A.1（连接器，passive）
#    ⇒ 单图 ERC 判「input pin not driven」。
ALLOWED_WARNINGS = {
    ("isolated_pin_label", "Global Label 'LED_DIN'"),
    ("pin_not_driven", "Symbol LED1 Pin 2"),
}

# 按【类型】整体豁免：GND 的 PWR_FLAG 在电源子图（全局网只能有一个 power output），
# 本图不加 flag ⇒ 单图视角下「GND 无驱动源」是预期。
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
    txt = open(path, encoding="utf-8").read()
    nets = {}
    for chunk in txt.split("(net")[1:]:
        nm = re.search(r'\(name\s+"([^"]+)"', chunk)
        if not nm:
            continue
        # 局部网名在根图导出时带 sheet 路径前缀 ⇒ 取最后一段
        name = nm.group(1).lstrip("/").split("/")[-1]
        nodes = set(re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', chunk))
        nets[name] = nets.get(name, set()) | nodes
    return nets


def main():
    cli = find_kicad_cli()
    if not cli:
        print("❌ 找不到 kicad-cli（可用环境变量 KICAD_CLI 指定）")
        return 2
    if not os.path.exists(SHEET):
        print(f"❌ 找不到原理图 {SHEET}，先跑 docs/_tools/gen_rgb_sch.py")
        return 2

    tmp = tempfile.mkdtemp(prefix="ss_rgb_verify_")
    try:
        net = os.path.join(tmp, "rgb.net")
        r1 = subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadsexpr",
                             "-o", net, SHEET], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
        root_net = os.path.join(tmp, "root.net")
        r2 = subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadsexpr",
                             "-o", root_net, ROOT_SHEET], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
        r3 = subprocess.run([cli, "sch", "erc", "--severity-all", "--output",
                             os.path.join(tmp, "rgb.erc"), SHEET],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r1.returncode != 0 or not os.path.exists(net):
            print("❌ RGB 子图网表导出失败")
            print((r1.stdout or "") + (r1.stderr or ""))
            return 1
        got = parse_netlist(net)
        got_root = parse_netlist(root_net) if r2.returncode == 0 and os.path.exists(root_net) else None
        erc = open(os.path.join(tmp, "rgb.erc"), encoding="utf-8", errors="replace").read()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    fails = []

    def check(label, ok, detail=""):
        print(f"  {'✅' if ok else '❌'} {label}" + (f"   {detail}" if detail else ""))
        if not ok:
            fails.append(label)

    # ------------------------------------------------------------------
    print("=" * 66)
    print("A. 派生断言：RGB 子图网表 == rgb_design.py 的连接表")
    print("=" * 66)
    want = collections.defaultdict(set)
    nc = set()
    for key, net in D.CONN.items():
        ref, pin = key.rsplit(".", 1)
        if net is None:
            nc.add((ref, pin))
        else:
            want[net].add((ref, pin))
    bad = [n for n in sorted(want) if got.get(n) != want[n]]
    check(f"全部 {len(want)} 条网络与连接表一致", not bad, str(bad[:5]))
    unconn = [n for n in got if n.startswith("unconnected-(")]
    extra = [n for n in got if n not in want and n != "GND" and not n.startswith("unconnected-(")]
    check("没有设计之外的多余网络", not extra, str(sorted(extra)[:5]))
    check(f"NC 引脚全部带标记（{len(unconn)} == {len(nc)}）", len(unconn) == len(nc))
    placed = set()
    for n, nodes in got.items():
        if not n.startswith("unconnected-("):
            placed |= nodes
    check("NC 引脚不接任何网络", not (nc & placed), str(sorted(nc & placed)))

    # ------------------------------------------------------------------
    print("=" * 66)
    print("B. 跨图接口断言（根图整体网表）")
    print("=" * 66)
    if got_root is None:
        check("根图整体网表导出", False, "导出失败")
    else:
        vled = got_root.get("VLED", set())
        check("VLED 跨图连通（电源子图 Q1 + 95 颗灯珠 = 96 元件）",
              ("Q1", "3") in vled and len(vled) == 96, f"{len(vled)} 元件")
        check("LED_DIN 跨图连通（控制子图 J3A.1 + LED1.DIN）",
              got_root.get("LED_DIN") == {("J3A", "1"), ("LED1", "2")},
              str(sorted(got_root.get("LED_DIN", set()))))

    # ------------------------------------------------------------------
    print("=" * 66)
    print("C. 具名断言：数据链与供电")
    print("=" * 66)
    n_led = len([c for c in D.COMPONENTS if c["ref"].startswith("LED")])
    check(f"灯珠数量 = 95（chain-length 一致）", n_led == 95, f"实际 {n_led}")
    # 链序：LEDi.DOUT(4) 与 LED(i+1).DIN(2) 同网
    bad_link = []
    for i in range(1, 95):
        nxt = f"LED_DIN_{i+1}" if i + 1 > 1 else "LED_DIN"
        want_nodes = {(f"LED{i}", "4"), (f"LED{i+1}", "2")}
        key = "LED_DIN" if i == 0 else f"LED_DIN_{i+1}"
        if got.get(key) != want_nodes:
            bad_link.append((i, key, sorted(got.get(key, set()))))
    check("数据链 94 段全部首尾相接（LEDi.DOUT → LED(i+1).DIN）", not bad_link,
          str(bad_link[:3]))
    check("LED1.DIN 接全局 LED_DIN（来自 nice!nano P0.06）",
          ("LED1", "2") in got.get("LED_DIN", set()))
    check("LED95.DOUT 为链尾 NC", ("LED95", "4") in nc)
    # 供电
    vled_nodes = got.get("VLED", set())
    gnd_nodes = got.get("GND", set())
    miss_v = [f"LED{i}" for i in range(1, 96) if (f"LED{i}", "3") not in vled_nodes]
    miss_g = [f"LED{i}" for i in range(1, 96) if (f"LED{i}", "1") not in gnd_nodes]
    check("95 颗灯珠 VDD(3) 全部接 VLED", not miss_v, str(miss_v[:5]))
    check("95 颗灯珠 VSS(1) 全部接 GND", not miss_g, str(miss_g[:5]))
    # 位号 ↔ index 对应（抽查 3 个：Esc / Enter / 末键）
    try:
        m = json.load(open(MATRIX, encoding="utf-8"))["matrix"]
        by_idx = {k["index"]: k for k in m}
        comp_by_ref = {c["ref"]: c for c in D.COMPONENTS}
        ok_map = all(
            comp_by_ref[f"LED{i}"]["props"]["Note"].startswith(
                f"per-key RGB：对应键 index={i} (R{by_idx[i]['row']}C{by_idx[i]['col']}")
            for i in (1, 52, 95)
        )
        check("位号 LEDi ↔ 键 index i（抽查 1 / 52 / 95）", ok_map)
    except Exception as e:          # pragma: no cover
        check("位号 ↔ index 对应检查", False, str(e))

    # ------------------------------------------------------------------
    print("=" * 66)
    print("D. ERC 闸门（RGB 子图单图）")
    print("=" * 66)
    violations = []
    err_violations = []
    for block in erc.split("["):
        if "]" not in block:
            continue
        kind = block.split("]")[0]
        # ⚠️ ERC 报告里引脚描述也带方括号（如 `Pin 2 [DIN, Input, Line]`）——
        #    按 "[" 切分会把它们误当成违规类型。只接受纯小写下划线标识符。
        if not re.fullmatch(r"[a-z_]+", kind):
            continue
        if kind in ("lib_symbol_mismatch",):
            continue        # 符号缓存与库版本差异的噪音（矩阵图同款）
        m = re.search(r'@\([^)]*\):\s*(.+)', block)
        obj = m.group(1).strip() if m else block[:60].strip()
        if kind in ALLOWED_WARNING_KINDS:
            continue
        if any(kind == k and o in obj for k, o in ALLOWED_WARNINGS):
            continue
        violations.append((kind, obj))
        if "; error" in block[:200]:
            err_violations.append((kind, obj))
    check(f"ERC：无未豁免违规（{len(violations)} 条）", not violations, str(violations[:5]))
    # ⚠️ 汇总行的 Errors 计数包含「已豁免」的跨图条目（如 LED1.DIN 由控制子图驱动）
    #    ⇒ 判据必须是「未豁免的 error 级违规 = 0」，不能看原始计数。
    m = re.search(r'Errors\s+(\d+)\s+Warnings\s+(\d+)', erc)
    check("ERC：未豁免的 error 级违规 = 0", not err_violations,
          (f"报告原始 errors={m.group(1)} warnings={m.group(2)}；" if m else "")
          + str(err_violations[:3]))

    print("=" * 66)
    if fails:
        print(f"结论：❌ RGB 子图校验未通过（{len(fails)} 项失败）")
        for f in fails:
            print("   -", f)
        return 1
    print("结论：✅ RGB 子图校验全部通过（95 颗数据链、跨图接口连通、ERC 0 error）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
