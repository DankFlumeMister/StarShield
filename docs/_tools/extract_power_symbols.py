#!/usr/bin/env python3
"""extract_power_symbols.py —— 从本机 KiCad 官方符号库导出电源子图所需的符号定义

输出：docs/_tools/power_symbols.json
      {"_meta": {...provenance...}, "symbols": {"<库>:<符号名>": "<s-expression 文本>"}}

为什么要有这一步（而不是让生成器直接读 KiCad 安装目录）：
    生成链必须**不依赖本机是否装了 KiCad**。把用到的符号定义抽成一份入库的
    数据文件，生成器只读这份文件 ⇒ 别人 clone 后无需装 KiCad 也能重跑生成器。
    （对比：docs/_tools/field_schema.json 也是同样的「单一真相源数据文件」做法。）

⚠️ 本脚本**只在需要新增/更新符号时手工运行一次**，不属于「必须重跑的生成器」。
   它依赖本机 KiCad 安装（默认 D:\\Kicad，可用 KICAD_SYMBOLS_DIR 覆盖）。

为什么要把「派生符号」展平：
    KiCad 官方库里很多料号是派生符号（如 Transistor_FET:2N7002 只是
    `(extends "Q_NMOS_GSD")`）。原理图的 lib_symbols 缓存里 KiCad 存的是**展平后**的
    完整定义。直接抄派生符号会导致 KiCad 找不到父符号 ⇒ 加载报错。
    本脚本把父符号的图形/引脚与子符号的属性合并，并同步改写子单元名
    （`Q_NMOS_GSD_0_1` → `2N7002_0_1`，否则 KiCad 解析单元名失败）。

许可：符号文本来自 KiCad 官方符号库（CC-BY-SA-4.0，附「用于设计不受本许可约束」的例外条款）。
      本项目只嵌入**自己原理图用到的**符号定义，属该例外覆盖的「生成文件」。
"""
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "docs", "_tools", "power_symbols.json")

# 需要导出的符号（库名, 符号名）。库名即 .kicad_sym 文件名，也是原理图里的库前缀。
WANTED = [
    ("Battery_Management", "BQ24072RGT"),
    ("Connector", "USB_C_Receptacle_USB2.0_16P"),
    ("Device", "R"),
    ("Device", "C"),
    ("Device", "Fuse"),
    ("Device", "LED"),
    ("Connector_Generic", "Conn_01x02"),
    ("Transistor_FET", "2N7002"),
    ("Transistor_FET", "AO3401A"),
    ("power", "GND"),
    ("power", "VBUS"),
    ("power", "PWR_FLAG"),
]


def find_symbols_dir():
    env = os.environ.get("KICAD_SYMBOLS_DIR")
    if env and os.path.isdir(env):
        return env
    import glob
    cands = []
    for drive in "CDEFGH":
        cands += glob.glob(rf"{drive}:\Kicad\share\kicad\symbols")
        cands += glob.glob(rf"{drive}:\Program Files\KiCad\*\share\kicad\symbols")
    cands += ["/usr/share/kicad/symbols",
              "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"]
    for c in cands:
        if os.path.isdir(c):
            return c
    return None


def read_lib(symdir, lib):
    p = os.path.join(symdir, lib + ".kicad_sym")
    if not os.path.exists(p):
        return None, None
    txt = open(p, encoding="utf-8").read()
    m = re.search(r'\(version\s+(\d+)\)', txt)
    return txt, (m.group(1) if m else "?")


def split_top_level(s):
    """把一个 s-expression 的顶层子节点切出来（只处理本文件的用途，足够健壮）。"""
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '"':
            i += 1
            while i < n and s[i] != '"':
                i += 2 if s[i] == "\\" else 1
            i += 1
            continue
        if c == "(":
            d = 0
            j = i
            while j < n:
                ch = s[j]
                if ch == '"':
                    j += 1
                    while j < n and s[j] != '"':
                        j += 2 if s[j] == "\\" else 1
                    j += 1
                    continue
                if ch == "(":
                    d += 1
                elif ch == ")":
                    d -= 1
                    if d == 0:
                        break
                j += 1
            out.append(s[i:j + 1])
            i = j + 1
            continue
        i += 1
    return out


def cut_symbol(txt, name):
    """从 .kicad_sym 文本里切出顶层 `(symbol "name" ...)` 块。"""
    i = txt.find('\n\t(symbol "%s"' % name)
    if i < 0:
        return None
    k = txt.find("(", i + 1)
    d = 0
    p = k
    while p < len(txt):
        c = txt[p]
        if c == '"':
            p += 1
            while p < len(txt) and txt[p] != '"':
                p += 2 if txt[p] == "\\" else 1
            p += 1
            continue
        if c == "(":
            d += 1
        elif c == ")":
            d -= 1
            if d == 0:
                return txt[k:p + 1]
        p += 1
    return None


def prop_name(block):
    m = re.match(r'\(property\s+"([^"]*)"', block)
    return m.group(1) if m else None


def flatten(block, lib, cache):
    """把 `(extends "Parent")` 展平；返回 (展平后的文本, 子单元重命名映射)。"""
    m = re.search(r'\(extends\s+"([^"]+)"\)', block)
    if not m:
        return block, None
    parent_name = m.group(1)
    parent = cut_symbol(cache, parent_name)
    if parent is None:
        raise RuntimeError(f"派生符号的父符号 {parent_name} 不在同一个库里")

    # 子节点切分。⚠️ 注意：不能写成 block.index("(", 1)——那会命中「第一个子节点的左括号」
    # （index 0 才是符号自身的左括号），从而把 `(pin_names (offset 0) ...)` 拆散。
    # 必须以「符号名字符串的结束位置」为界。
    def body_of(blk):
        m0 = re.match(r'\(symbol\s+"(?:[^"\\]|\\.)*"', blk)
        return blk[m0.end(): blk.rindex(")")]

    body = body_of(block)
    pbody = body_of(parent)
    kids = split_top_level(body)
    pkids = split_top_level(pbody)

    child_props = {prop_name(k): k for k in kids if prop_name(k)}
    child_name = re.match(r'\(symbol\s+"([^"]+)"', block).group(1)

    out = []
    seen = set()
    for k in pkids:
        pn = prop_name(k)
        if pn and pn in child_props:
            out.append(child_props[pn])
            seen.add(pn)
        elif pn:
            out.append(k)
            seen.add(pn)
        else:
            out.append(k)
    for pn, k in child_props.items():
        if pn not in seen:
            out.append(k)

    text = '(symbol "%s"\n\t\t' % child_name + "\n\t\t".join(out) + "\n\t)"
    # 子单元名必须跟着改名：<Parent>_0_1 → <Child>_0_1
    text = text.replace('(symbol "%s_' % parent_name, '(symbol "%s_' % child_name)
    return text, parent_name


def main():
    symdir = find_symbols_dir()
    if not symdir:
        sys.exit("❌ 找不到 KiCad 官方符号库目录。请设置环境变量 KICAD_SYMBOLS_DIR。")
    print(f"KiCad 符号库：{symdir}")

    cache = {}
    versions = {}
    out = {}
    for lib, name in WANTED:
        if lib not in cache:
            txt, ver = read_lib(symdir, lib)
            if txt is None:
                sys.exit(f"❌ 找不到库 {lib}.kicad_sym")
            cache[lib] = txt
            versions[lib] = ver
        blk = cut_symbol(cache[lib], name)
        if blk is None:
            sys.exit(f"❌ 库里找不到符号 {lib}:{name}")
        flat, _parent = flatten(blk, lib, cache[lib])
        out[f"{lib}:{name}"] = flat
        print(f"  {lib + ':' + name:45} {len(flat):6} 字节")

    data = {
        "_meta": {
            "generated_by": "docs/_tools/extract_power_symbols.py",
            "source": "KiCad 官方符号库（CC-BY-SA-4.0，附设计使用例外条款）",
            "kicad_symbols_dir": symdir,
            "lib_versions": versions,
            "note": "派生的料号符号（extends）已展平；子单元名已同步改名。"
                    "本文件是生成器的输入数据，不是派生产物；"
                    "仅在新增/更新用到的符号时手工重跑提取脚本。",
        },
        "symbols": out,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    print(f"\n✅ 已写出 {os.path.relpath(OUT, ROOT)}  ({len(out)} 个符号)")


if __name__ == "__main__":
    main()
