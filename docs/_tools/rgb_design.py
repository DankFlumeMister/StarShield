#!/usr/bin/env python3
"""rgb_design.py —— RGB 子图的**电路设计数据**（单一真相源，对应 M5 / B2 后续）

只放「电路是什么」，不放「怎么画」；绘制逻辑全在 gen_rgb_sch.py。
本文件与其它子图数据源的关键差别：**元件与连接由 `docs/_generated/matrix.json`
循环生成**（95 颗灯珠手工列举不现实，也不可靠）。

数据源：`docs/_generated/matrix.json`（唯一权威：`sketch/keyboard-layout.json` KLE）
- 灯珠 i 对应 `index` = i 的键（位号 `LED{i}`），Value 写键帽标签便于新手对照；
- **数据链顺序 = index 顺序（1..95）**，即行优先、行内从左到右（KLE 输入顺序）。
  ⚠️ 该顺序**与 ZMK 侧 LED index、键位 index 三者一致**，改顺序要三处同步；
  B4 若为了走线最短改蛇形（行末折回），必须同步固件侧的 LED 映射。

坐标：KiCad 原理图坐标，mm，Y 轴向下。A2 图纸 594 × 420。
- 列间距 25.4 mm、行间距 38.1 mm（放大到整数倍，给符号短线和标签留空隙）；
- 图面**不按真实物理坐标**排列（那是 PCB 布局的事，B4 按 KLE 精确生成），
  原理图只保证「行内相对顺序」与「行序」正确。

子图间接口（全局标签，与电源/控制子图同名即相连）：
    VLED  —— LED 供电轨（电源子图 Q1 门控后的电池直供轨，ADR-0007 / ADR-0005）
    LED_DIN —— 数据链首颗的数据输入（控制子图 J3A 孔2 = P0.06，&spi3 MOSI）
    GND   —— 电源符号

设计依据：
- 灯珠：SK6812MINI-E，95 颗 per-key（ADR-0006/0007；LCSC C5149201）
- 供电：电池直供、不加升压（ADR-0007）；门控在电源子图（拓扑 C，ADR-0005）
- 走线：VLED 按 2–3 A 走线（handoff §8）；固件侧 `BRT_MAX=30` 是电流护栏
- 静态电流：0.6 mA/颗 × 95 ≈ 57 mA ⇒ 必须门控（RGB 关闭时 PMOS 切断）
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MATRIX = os.path.join(ROOT, "docs", "_generated", "matrix.json")

with open(MATRIX, encoding="utf-8") as f:
    _M = json.load(f)
KEYS = sorted(_M["matrix"], key=lambda k: k["index"])

SHEET_TITLE = "StarShield RGB 子图（95 颗 SK6812MINI-E 数据链）"
SHEET_FILE = "rgb/rgb.kicad_sch"
PAPER = "A2"

# 图面布局（1.27 的整数倍）
X0, Y0 = 50.8, 63.5
COL_PITCH = 25.4      # 行内相邻灯珠间距
ROW_PITCH = 38.1      # 行间距

LED_LIB = "LED:SK6812MINI-E"
# 封装：官方库只有两个 SK6812MINI 变体。选 **PLCC4 3.5×3.5 正装**：
#   per-key RGB 常规做法是灯珠焊在 PCB 元件面、位于轴体下方经导光柱/开孔发光。
#   另一个 `LED_SK6812MINI-E_3.2x2.8mm_P1.5mm_ReverseMount` 是**反向贴装**
#   （灯珠在 PCB 背面、光穿过 PCB 开孔），需要 PCB 开孔且损失亮度 ⇒ 不采用。
# ⚠️ UNVERIFIED（B3/B4 投板前用实物核对）：型号与封装的对应、贴装方向。
LED_FP = "LED_SMD:LED_SK6812MINI_PLCC4_3.5x3.5mm_P1.75mm"


def _value(label):
    """Value 属性：键帽标签。生成器会做 sexp 转义，这里只做可读性处理。"""
    return (label or "").strip() or "Space"


# ---------------------------------------------------------------------------
# 元件表：LED1..LED95，按行分组布置
# ---------------------------------------------------------------------------
COMPONENTS = []
_row_seq = {}        # row -> 已放置个数（决定行内 x 序号）
for k in KEYS:
    r = k["row"]
    seq = _row_seq.get(r, 0)
    _row_seq[r] = seq + 1
    at = (round(X0 + seq * COL_PITCH, 4), round(Y0 + r * ROW_PITCH, 4))
    COMPONENTS.append(dict(
        ref=f"LED{k['index']}", lib=LED_LIB, value=_value(k["label"]),
        fp=LED_FP, at=at, rot=0,
        props={
            "MPN": "SK6812MINI-E", "LCSC": "C5149201",
            "Note": f"per-key RGB：对应键 index={k['index']} (R{k['row']}C{k['col']} {k['label']})",
        },
    ))

# ---------------------------------------------------------------------------
# 连接表：每颗灯珠 4 个脚
#   pin1 VSS → GND；pin3 VDD → VLED；pin2 DIN ← 前一颗 DOUT；pin4 DOUT → 下一颗 DIN
#   LED1.DIN = LED_DIN（全局，来自控制子图）；LED95.DOUT = None（链尾，no_connect）
# ---------------------------------------------------------------------------
CONN = {}
_n = len(KEYS)
for k in KEYS:
    i = k["index"]
    ref = f"LED{i}"
    CONN[f"{ref}.1"] = "GND"
    CONN[f"{ref}.3"] = "VLED"
    CONN[f"{ref}.2"] = "LED_DIN" if i == 1 else f"LED_DIN_{i}"
    CONN[f"{ref}.4"] = f"LED_DIN_{i+1}" if i < _n else None

# 跨子图网络 → 全局标签
GLOBAL_NETS = {"VLED", "LED_DIN"}

# ---------------------------------------------------------------------------
# PWR_FLAG：VLED 在本图只有 95 个 power_in（LED VDD），没有 power_out
#   （真实驱动源是电源子图 Q1 的漏极，passive）⇒ 需要一个 PWR_FLAG。
#
# ⚠️ **GND 不要在本图加 flag**：GND 是全局电源网，电源子图已有 PWR_FLAG；
#    第二个 power output 会触发 ERC [pin_to_pin] error（2026-09-18 实测）。
#    代价：单图视角下 GND 无驱动源 ⇒ verify_rgb.py 的 ERC 豁免已列为预期。
# ---------------------------------------------------------------------------
PWR_FLAGS = [
    dict(net="VLED", at=(30.48, 45.72)),
]

# ---------------------------------------------------------------------------
# 图面文字（不进 BOM）
# ---------------------------------------------------------------------------
NOTE_Y = Y0 + 6 * ROW_PITCH + 15.24      # 最后一行灯珠下方
NOTES = [
    (25.4, 25.4,
     "StarShield RGB 子图 —— 由 docs/_tools/gen_rgb_sch.py 自动生成，请勿手改；"
     "改电路请改 docs/_tools/rgb_design.py。依据：ADR-0007（电池直供不升压）、"
     "ADR-0005（门控拓扑 C）、ADR-0006（95 键）"),
    (25.4, 33.02,
     "【数据链】LED1.DIN = LED_DIN（来自控制子图 J3A 孔2 = nice!nano D1/P0.06，&spi3 MOSI）；"
     "LEDi.DOUT → LED(i+1).DIN 依次串联到 LED95；LED95.DOUT 悬空（链尾）。"
     "链序 = 键位 index 顺序（行优先、行内从左到右），与 ZMK 侧 LED index 一致"),
    (25.4, NOTE_Y,
     "【供电】全部灯珠的 VDD 接 VLED —— 电源子图中由电池直供、经 Q1(AO3401A) PMOS 门控的 LED 轨"
     "（ADR-0007：不加 5V 升压；ADR-0005：拓扑 C，MCU 经 2N7002 反相级控制）。"
     "VLED 按 2-3 A 走线；固件侧 CONFIG_ZMK_RGB_UNDERGLOW_BRT_MAX=30 是电流护栏（30% 灰阶约 1.0 A）"),
    (25.4, NOTE_Y + 8.89,
     "【静态电流】实测 0.6 mA/颗 x 95 ≈ 57 mA ⇒ 必须物理切断：RGB 关闭 / 深度睡眠时 Q1 关断，"
     "LED 轨无电。门控极性 GPIO_ACTIVE_HIGH（经反相级后非反相）"),
    (25.4, NOTE_Y + 17.78,
     "【封装与贴装】LED_SMD:LED_SK6812MINI_PLCC4_3.5x3.5mm_P1.75mm（正装）。"
     "⚠️ UNVERIFIED：官方库另一个变体是 ReverseMount（3.2x2.8，灯珠在 PCB 背面、光穿 PCB 开孔），"
     "本项目按常规 per-key 做法选正装 —— 投板前（B3/B4）需用实物核对型号-封装对应与贴装方向"),
    (25.4, NOTE_Y + 26.67,
     "【图面说明】本图按「行内顺序」排列灯珠（列间距 25.4 / 行间距 38.1），不是真实物理坐标；"
     "PCB 布局（B4）按 sketch/keyboard-layout.json 的 KLE 坐标精确生成。"
     "每颗灯珠的 Value 是该键的键帽标签，与 docs/_generated/matrix.json 的 index 一一对应"),
]
