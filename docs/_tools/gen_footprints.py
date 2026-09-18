#!/usr/bin/env python3
"""gen_footprints.py —— 生成工程自带的 MX 热插拔座封装（B3 定案：方案 a 自画）

背景（为什么自画）：
    官方库**没有** MX 热插拔座封装；社区库 `daprice/keyswitches.pretty` 的
    `Kailh_socket_MX` 是 **CC BY-SA 4.0**，没有官方库那种「用于设计不受本许可约束」
    的例外 ⇒ 抄文件会污染 CERN-OHL-S-2.0 许可链（项目硬规则：不引入无例外的第三方文件）。
    ⇒ 自画。几何取自**公开物理尺寸**（Cherry MX 官方目录 mx_cat.pdf 的开关尺寸、
    Kailh MX socket 的公开尺寸），不从社区库复制文件。

做法（不手抄任何一个坐标）：
    以官方 `Button_Switch_Keyboard:SW_Cherry_MX_<宽度>u_PCB` 为基底 —— 它已包含
    ① 轴体中心柱孔 / 定位柱孔 ② **卫星轴（stabilizer）孔位**（这是它按宽度分档的原因，
    官方库没有独立的 stabilizer 封装）③ 轴体 PTH 电气焊盘；
    本脚本只做三件事：
      1. 改封装名与描述；
      2. **追加 2 个 B.Cu 的 SMD 焊盘**（Kailh socket 的金属叶片），编号与官方 PTH
         焊盘相同（1 / 2）⇒ 同 net、装配时二选一（直焊用 PTH，热插拔用 SMD）；
      3. 追加说明性 Fab 文字。
    ⇒ 孔位与 stabilizer 间距**全部来自官方文件**，不手抄、不会抄错。

坐标系要点（踩过的坑）：
    官方 MX 封装的**原点不在轴体中心，而在其中一个引脚上**。
    交叉验证：官方 pad1 (0,0)、pad2 (−6.35, 2.54)；以轴体中心为原点时引脚在
    (2.54,−5.08) / (−3.81,−2.54)（间距同为 √(6.35²+2.54²)=6.84 mm）⇒ 两坐标系一致。
    Kailh socket 的焊盘公开尺寸（轴体中心坐标系）：(−6.29, 5.08) 与 (7.56, 2.54)，
    2.55 × 2.5 mm —— 即轴体引脚位置**点对称**（socket 在 PCB 另一侧）后沿 X 外移 3.75 mm。
    换算到官方原点（减去 (2.54, −5.08)）：(−8.83, 10.16) 与 (5.02, 7.62)。
    ⚠️ socket 焊在 **B.Cu（PCB 背面）**，轴体从正面插入 —— 这是热插拔的常规做法。

输出：hardware/pcb/StarShield/footprints/StarShield.pretty/*.kicad_mod
"""
import os
import re
import sys
import uuid

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT_DIR = os.path.join(ROOT, "hardware", "pcb", "StarShield", "footprints", "StarShield.pretty")

# 官方封装库（只读取，不复制）
OFFICIAL = r"D:\Kicad\share\kicad\footprints\Button_Switch_Keyboard.pretty"

# 本项目用到的宽度档位（来自 docs/_generated/matrix.json 的键宽分布）
VARIANTS = ["1.00u", "1.25u", "1.50u", "1.75u", "2.00u", "2.00u_Vertical", "2.25u", "6.25u"]

# Kailh socket 的 SMD 焊盘（**官方 MX 封装坐标系**，见模块 docstring 的换算）
SOCKET_PADS = [
    ("1", -8.83, 10.16),
    ("2", 5.02, 7.62),
]
PAD_W, PAD_H = 2.55, 2.5

NS = uuid.UUID("6f1a4d2e-8b3c-4f5a-9e7d-1c2b3a4d5e6f")


def uid(name):
    return str(uuid.uuid5(NS, "fp:" + name))


def socket_pad_sexp(num, x, y, name):
    return (
        f'\t(pad "{num}" smd rect\n'
        f'\t\t(at {x} {y})\n'
        f'\t\t(size {PAD_W} {PAD_H})\n'
        f'\t\t(layers "B.Cu" "B.Paste" "B.Mask")\n'
        f'\t\t(remove_unused_layers no)\n'
        f'\t\t(uuid "{uid(name)}")\n'
        f'\t)'
    )


def build(variant):
    src = os.path.join(OFFICIAL, f"SW_Cherry_MX_{variant}_PCB.kicad_mod")
    if not os.path.exists(src):
        raise SystemExit(f"❌ 官方封装不存在：{src}")
    txt = open(src, encoding="utf-8").read()

    name = f"SW_MX_Hotswap_Optional_{variant}"
    # 1) 改名
    txt = txt.replace(f'(footprint "SW_Cherry_MX_{variant}_PCB"', f'(footprint "{name}"', 1)
    # 2) 描述与标签
    txt = re.sub(r'\(descr\s+"[^"]*"',
                 '(descr "MX 热插拔座封装（StarShield 自画）：轴体直焊 PTH + Kailh socket 的 B.Cu SMD 焊盘，装配二选一；孔位与 stabilizer 间距取自官方 SW_Cherry_MX_%s_PCB（公开物理尺寸）"' % variant,
                 txt, count=1)
    txt = re.sub(r'\(tags\s+"[^"]*"',
                 '(tags "MX hotswap Kailh socket optional StarShield"', txt, count=1)
    # 3) generator 标注（保留可追溯性）
    txt = re.sub(r'\(generator\s+"[^"]*"',
                 '(generator "docs/_tools/gen_footprints.py"', txt, count=1)

    # 4) 在最后一个 pad 之后、embedded_fonts 之前追加 socket 焊盘
    marker = "\t(embedded_fonts"
    assert marker in txt, "官方封装结构变了：找不到 (embedded_fonts"
    pads = "\n".join(socket_pad_sexp(n, x, y, f"{name}:p{n}") for n, x, y in SOCKET_PADS)
    extra = pads + (
        f'\n\t(fp_text user "Kailh socket pads on B.Cu (back). Switch inserts from front."\n'
        f'\t\t(at 0 -4.5)\n'
        f'\t\t(layer "B.Fab")\n'
        f'\t\t(effects (font (size 0.8 0.8) (thickness 0.12)))\n'
        f'\t\t(uuid "{uid(name + ":note")}")\n'
        f'\t)'
    )
    txt = txt.replace(marker, extra + "\n" + marker, 1)
    return name, txt


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for v in VARIANTS:
        name, txt = build(v)
        out = os.path.join(OUT_DIR, name + ".kicad_mod")
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)
        print(f"  {name:42} {len(txt):7} 字节")
    print(f"\n✅ 已生成 {len(VARIANTS)} 个封装 → {os.path.relpath(OUT_DIR, ROOT)}")
    print("⚠️ 这些封装**尚未用实物核对**（socket 焊盘位置/孔径）⇒ 标 UNVERIFIED，并入 B6。")


if __name__ == "__main__":
    main()
