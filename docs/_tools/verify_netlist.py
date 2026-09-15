#!/usr/bin/env python3
"""verify_netlist.py — 校验 StarShield 矩阵原理图的网表是否电气正确

对每张矩阵子图调用 kicad-cli 导出网表，然后校验：
  1. 元件数量（开关 + 二极管 = 键数）
  2. 每个开关的 pin1 接在某条 ROW 网络上
  3. 每个开关的 pin2 接在某个二极管的阳极上（同一网络内存在 D 的 pin2）
  4. 每个二极管的 K(pin1) 接在某条 COL 网络上
  5. 全部开关合计恰好 95 个，列网络节点合计 = 键数
  6. 无「同一矩阵格被两个键占用」的冲突（行,列 组合唯一）
"""
import collections
import os
import re
import subprocess
import sys

# Windows 控制台默认 GBK，直接 print emoji/中文会 UnicodeEncodeError
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def find_kicad_cli():
    """定位 kicad-cli，避免写死本机路径（否则别人克隆后脚本跑不起来）。

    查找顺序：
      1. 环境变量 KICAD_CLI（显式指定，优先级最高）
      2. PATH 上的 kicad-cli
      3. 各平台常见安装位置
    """
    env = os.environ.get("KICAD_CLI")
    if env and os.path.exists(env):
        return env
    from shutil import which
    found = which("kicad-cli") or which("kicad-cli.exe")
    if found:
        return found
    candidates = [
        # Windows
        r"C:\Program Files\KiCad\bin\kicad-cli.exe",
        r"C:\Program Files (x86)\KiCad\bin\kicad-cli.exe",
        # Linux / macOS
        "/usr/bin/kicad-cli", "/usr/local/bin/kicad-cli",
        "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
    ]
    import glob
    # 兼容自定义安装位置（形如 <盘符>:\KiCad\bin\kicad-cli.exe）
    for drive in "CDEFGH":
        candidates += glob.glob(rf"{drive}:\KiCad\bin\kicad-cli.exe")
        candidates += glob.glob(rf"{drive}:\Program Files\KiCad\*\bin\kicad-cli.exe")
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


KICAD_CLI = find_kicad_cli()
if not KICAD_CLI:
    print("❌ 找不到 kicad-cli。")
    print("   请安装 KiCad，或用环境变量显式指定，例如：")
    print(r'     PowerShell:  $env:KICAD_CLI = "C:\Program Files\KiCad\bin\kicad-cli.exe"')
    print(r'     bash:        export KICAD_CLI=/usr/bin/kicad-cli')
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.normpath(os.path.join(HERE, "..", "..", "hardware", "pcb", "StarShield"))
SHEETS = [
    "matrix/matrix_r012.kicad_sch",
    "matrix/matrix_r234.kicad_sch",
    "matrix/matrix_r45.kicad_sch",
]
TMP = os.path.join(PCB, "_tmp")
os.makedirs(TMP, exist_ok=True)


def cleanup():
    """删除本次校验产生的临时网表与目录，保持工作区干净（否则会污染 git status）。"""
    import shutil
    try:
        shutil.rmtree(TMP, ignore_errors=True)
    except Exception:
        pass

WS = r"\s+"


def parse_netlist(path):
    """返回 (refs, nets: {netname: set((ref,pin))})"""
    txt = open(path, encoding="utf-8").read()
    refs = set(re.findall(r'\(comp\s+\(ref\s+"([^"]+)"\)', txt))
    nets = {}
    for m in re.finditer(r'\(net\s+\(code\s+"[^"]*"\)\s+\(name\s+"([^"]+)"\)(.*?)\n\t\t\)\n', txt, re.S):
        name, body = m.group(1), m.group(2)
        nodes = set()
        for nm in re.finditer(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', body):
            nodes.add((nm.group(1), nm.group(2)))
        nets[name.lstrip("/")] = nodes
    return refs, nets


def main():
    all_refs = set()
    all_nets = collections.defaultdict(set)
    for sh in SHEETS:
        out = os.path.join(TMP, "nl_" + os.path.basename(sh) + ".net")
        r = subprocess.run(
            [KICAD_CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", out,
             os.path.join(PCB, sh)],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print(f"❌ 网表导出失败: {sh}")
            return 1
        refs, nets = parse_netlist(out)
        all_refs |= refs
        for n, nodes in nets.items():
            all_nets[n] |= nodes

    sw = sorted([r for r in all_refs if r.startswith("SW")], key=lambda s: int(s[2:]))
    dd = sorted([r for r in all_refs if r.startswith("D") and not r.startswith("SW")],
                key=lambda s: int(s[1:]))
    nets = dict(all_nets)
    rows = sorted([n for n in nets if n.startswith("ROW")], key=lambda s: int(s[3:]))
    cols = sorted([n for n in nets if n.startswith("COL")], key=lambda s: int(s[3:]))

    print("=" * 62)
    print(f"元件总数      : {len(all_refs)}   (开关 {len(sw)} + 二极管 {len(dd)})")
    print(f"网络总数      : {len(nets)}   (ROW {len(rows)} + COL {len(cols)})")
    print("=" * 62)

    fails = []

    def check(label, ok, detail=""):
        print(f"  {'✅' if ok else '❌'} {label}" + (f"   {detail}" if detail else ""))
        if not ok:
            fails.append(label)

    check("开关数量 = 95", len(sw) == 95, f"实际 {len(sw)}")
    check("二极管数量 = 95", len(dd) == 95, f"实际 {len(dd)}")
    check("行网络 = 6 (ROW0..ROW5)", len(rows) == 6 and rows == [f"ROW{i}" for i in range(6)], str(rows))
    check("列网络 = 18 (COL0..COL17)", len(cols) == 18 and cols == [f"COL{i}" for i in range(18)], str(cols))

    # 每个开关 pin1 在某 ROW 上
    node2net = collections.defaultdict(set)
    for n, nodes in nets.items():
        for nd in nodes:
            node2net[nd].add(n)
    bad = [s for s in sw if not (node2net[(s, "1")] & set(rows))]
    check("每个开关 pin1 接 ROW", not bad, f"异常 {bad[:5]}")

    # 每个二极管 K(pin1) 在某 COL 上
    bad = [d for d in dd if not (node2net[(d, "1")] & set(cols))]
    check("每个二极管 K(pin1) 接 COL", not bad, f"异常 {bad[:5]}")

    # 每个开关 pin2 与某二极管 pin2(A) 同网
    bad = []
    for s in sw:
        ns = node2net[(s, "2")]
        if not any(any(ref.startswith("D") and pin == "2" for ref, pin in nets[n]) for n in ns):
            bad.append(s)
    check("每个开关 pin2 接二极管阳极", not bad, f"异常 {bad[:5]}")

    # 每个二极管 A(pin2) 与某开关 pin2 同网
    bad = []
    for d in dd:
        ns = node2net[(d, "2")]
        if not any(any(ref.startswith("SW") and pin == "2" for ref, pin in nets[n]) for n in ns):
            bad.append(d)
    check("每个二极管阳极接开关", not bad, f"异常 {bad[:5]}")

    # 列网络节点合计 = 95
    tot = sum(len(nets[c]) for c in cols)
    check("列网络节点合计 = 95", tot == 95, f"实际 {tot}")

    # (row, col) 组合唯一 —— 矩阵无冲突
    combos = collections.Counter()
    for s in sw:
        rn = node2net[(s, "1")] & set(rows)
        cn = None
        # 找该开关所连二极管，再取其列
        for n in node2net[(s, "2")]:
            for ref, pin in nets[n]:
                if ref.startswith("D") and not ref.startswith("SW"):
                    c = node2net[(ref, "1")] & set(cols)
                    if c:
                        cn = c
        if rn and cn:
            combos[(list(rn)[0], list(cn)[0])] += 1
    dup = {k: v for k, v in combos.items() if v > 1}
    check("矩阵 (行,列) 组合唯一", not dup and len(combos) == 95,
          f"唯一组合 {len(combos)} 个, 冲突 {list(dup.items())[:5]}")

    print("=" * 62)
    cleanup()
    if fails:
        print(f"结论：❌ 未通过（{len(fails)} 项失败）")
        for f in fails:
            print("   -", f)
        return 1
    print("结论：✅ 网表校验全部通过（95 键、6 行 × 18 列、无冲突、无悬空）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
