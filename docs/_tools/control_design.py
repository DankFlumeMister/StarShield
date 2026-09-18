#!/usr/bin/env python3
"""control_design.py —— 控制板子图的**电路设计数据**（单一真相源，对应 B2）

本文件只放「电路是什么」，不放「怎么画」。绘制逻辑全在 gen_control_sch.py。
与 power_design.py（电源子图）、matrix（矩阵子图）并列，是 B2 的数据源。

坐标系：KiCad 原理图坐标，mm，Y 轴向下。A3 图纸 420 × 297。
所有元件原点都取 1.27 mm 的整数倍 ⇒ 引脚端点自动落在连接网格上。

子图间接口（与 power_design.py 的 GLOBAL_NETS / gen_matrix_sch.py 的全局标签同名）：
    OUT（来自电源子图）· RGB_PWR_EN（去电源子图 Q2 栅极）
    ROW0..ROW5 / COL0..COL17（与矩阵子图同名全局标签，2026-09-18 起矩阵侧也是全局标签）
    LED_DIN（新网：去将来的 RGB 子图；RGB 子图落地前该网只有本子图 1 个引脚，
    ERC 会报 isolated warning —— 已知且已豁免）
    GND（电源符号，全局）

设计依据（逐条已核实）：
- 排针映射：ZMK 官方 v0.3 `app/boards/arm/nice_nano/arduino_pro_micro_pins.dtsi`
  的 gpio-map（见 docs/controller-and-battery-facts.md §1.2 解析结果）
- 矩阵/595：docs/adr/0008（⚠️ 2026-09-18 修订：**3 颗** 74HC595，2 颗只有 16 位
  驱动不了 18 列 —— ngpios=24 时第 17~24 个时钟把 bit16/17 推出链尾丢失）
- 595 位序：research/_clones/zmk `app/module/drivers/gpio/gpio_595.c`（SPI MSB first、
  先移出的位最终落在链尾）⇒ bit 0..7 = 第一颗 QA..QH，bit 8..15 = 第二颗，
  bit 16..17 = 第三颗 QA/QB，bit 18..23 空闲
- 三档开关：docs/adr/0009（SP3T + toggle-mode + sideband，公共端 GND，
  触点经 GPIO_ACTIVE_LOW 读取，DT 不写 pull —— 由驱动管理）
- RGB 门控：docs/adr/0005 拓扑 C（门控本体在电源子图，本子图只引出控制脚）

⚠️ 本文件中每一处「非官方直接给出」的判断都写在注释里，标注了理由与风险。
"""

SHEET_TITLE = "StarShield 控制板子图（MCU / 595 列驱动 / 三档开关）"
SHEET_FILE = "control/control.kicad_sch"
PAPER = "A3"

# ---------------------------------------------------------------------------
# 元件表
#   ref  : 位号
#   lib  : KiCad 符号（必须在 power_symbols.json 里 —— 该文件现是全工程符号缓存）
#   value: Value 属性
#   fp   : 封装（B3 阶段统一复核；此处先给出已核实/待核实标记）
#   at   : 原点坐标 (x, y)，1.27 的整数倍
#   rot  : 旋转角（度，0/90/180/270）
#   props: 附加属性（MPN / LCSC 等），便于新手直接下单
# ---------------------------------------------------------------------------

# nice!nano v2 排针为什么是两个 Conn_01x12：
#   1) KiCad 官方库没有 Pro_Micro / nice!nano 符号（223 个库全查过）；
#   2) 两条 1x12 恰好对应本项目的插座形态 —— decisions.md「PCB 通孔 + Mill-Max
#      插座」，Mill-Max 插座就是两条 1x12 排母；
#   3) 引脚号 1..12 与 Pro Micro 标号**直接一致**（J3A.n = Pro Micro 标号 n，
#      J3B.n = Pro Micro 标号 12+n），杜绝 2x12 符号「引脚号 ≠ 排针标号」的心智负担。
#
# 封装（B3，2026-09-18）：`Connector_PinSocket_2.54mm:PinSocket_1x12_P2.54mm_Vertical`
#   官方库**没有** Connector_Mill-Max（155 个 .pretty 全查过）⇒ 用通用 1x12 排母封装。
#   孔径匹配：排母封装焊盘孔径 1.0 mm；Mill-Max 315-43-1xx 系列推荐 PCB 孔径约 0.94 mm
#   ⇒ 可焊，但**具体料号与孔径仍须投板前用实物核对（并入 B6）**。
COMPONENTS = [
    # --- J3A：nice!nano v2 左列（Pro Micro 标号 1..12，自上而下）-------------
    dict(ref="J3A", lib="Connector_Generic:Conn_01x12", value="nice!nano v2 左列 (PM 1-12)",
         fp="Connector_PinSocket_2.54mm:PinSocket_1x12_P2.54mm_Vertical",
         at=(50.8, 139.7), rot=0,
         props={"MPN": "Mill-Max 315-43-112-41-001000 ❓待核",
                "Note": "J3A.n = Pro Micro 标号 n；映射依据 ZMK arduino_pro_micro_pins.dtsi"}),
    # --- J3B：nice!nano v2 右列（Pro Micro 标号 13..24，自上而下）-------------
    dict(ref="J3B", lib="Connector_Generic:Conn_01x12", value="nice!nano v2 右列 (PM 13-24)",
         fp="Connector_PinSocket_2.54mm:PinSocket_1x12_P2.54mm_Vertical",
         at=(76.2, 139.7), rot=0,
         props={"MPN": "Mill-Max 315-43-112-41-001000 ❓待核",
                "Note": "J3B.n = Pro Micro 标号 12+n；RAW(PM13) 接 OUT，VCC(PM16) 是 3.3V 轨"}),

    # --- 列驱动：3 颗 74HC595 级联 -------------------------------------------
    # ⚠️ 2026-09-18 修订（ADR-0008）：**3 颗**，不是 2 颗。
    #    2 颗只有 16 个输出位，而矩阵 18 列；overlay 的 ngpios=24 会让驱动每轮
    #    移 24 个时钟，第 17~24 位被推出链尾丢失 ⇒ bit16/17（COL16/17，小键盘区）
    #    永远无法驱动。源码依据：gpio_595.c 的 nwrite = ngpios/8 与 SPI MSB first。
    # 位序（已从源码推演核实）：bit 0..7 = U2.QA..QH；bit 8..15 = U3；bit 16..17 = U4.QA/QB。
    dict(ref="U2", lib="74xx:74HC595", value="74HC595",
         fp="Package_SO:SOIC-16_3.9x9.9mm_P1.27mm", at=(170.18, 127.0), rot=0,
         props={"Note": "级联第 1 颗：COL0..COL7 (bit0..7)；SER 接 MCU MOSI"}),
    dict(ref="U3", lib="74xx:74HC595", value="74HC595",
         fp="Package_SO:SOIC-16_3.9x9.9mm_P1.27mm", at=(219.71, 127.0), rot=0,
         props={"Note": "级联第 2 颗：COL8..COL15 (bit8..15)；SER 接 U2.QH'"}),
    dict(ref="U4", lib="74xx:74HC595", value="74HC595",
         fp="Package_SO:SOIC-16_3.9x9.9mm_P1.27mm", at=(269.24, 127.0), rot=0,
         props={"Note": "级联第 3 颗：COL16/COL17 (bit16/17)；QC..QH 与 QH' 空闲 NC"}),

    # --- 三档模式开关（SP3T，ADR-0009）---------------------------------------
    # 符号 Switch:SW_SP3T：pin3 = 公共端（杆的枢轴在符号左侧，已按图形核实），
    # pin1/2/4 = 三个掷点。封装用官方 Button_Switch_SMD:SW_SP3T_PCM13（B3 复核
    # 符号掷点与封装 pad 的对应）。
    # ⚠️ GPIO_ACTIVE_LOW 读取、公共端接 GND：未选中档由 ZMK 驱动内部上拉到 3.3V
    #    （ADR-0009：DT 里不写 pull，驱动按 ACTIVE_LOW 自行推导 PULL_UP）。
    dict(ref="SW1", lib="Switch:SW_SP3T", value="PCM13 (SP3T)",
         fp="Button_Switch_SMD:SW_SP3T_PCM13", at=(50.8, 63.5), rot=0,
         props={"MPN": "PCM13SMTR", "LCSC": "❓待补（BOM 阶段）",
                "Note": "pin3=公共端接GND；pin1/2/4 = 档0有线/档1蓝牙/档2 2.4G"}),

    # --- 595 去耦（每颗一颗 100nF）-------------------------------------------
    dict(ref="C4", lib="Device:C", value="100nF",
         fp="Capacitor_SMD:C_0603_1608Metric", at=(165.1, 165.1), rot=0,
         props={"Note": "U2 去耦"}),
    dict(ref="C5", lib="Device:C", value="100nF",
         fp="Capacitor_SMD:C_0603_1608Metric", at=(214.63, 165.1), rot=0,
         props={"Note": "U3 去耦"}),
    dict(ref="C6", lib="Device:C", value="100nF",
         fp="Capacitor_SMD:C_0603_1608Metric", at=(264.16, 165.1), rot=0,
         props={"Note": "U4 去耦"}),
]

# ---------------------------------------------------------------------------
# 网络连接表："位号.引脚号" -> 网名；None = 明确不接（生成 no_connect 标记）
#
# 网名约定：
#   GND                  —— power:GND 电源符号（全局；PWR_FLAG 已由电源子图提供）
#   VCC                  —— power:VCC 电源符号（全局 3.3V 轨；本子图内由 J3B.16 驱动，
#                           需 PWR_FLAG —— 见 PWR_FLAGS）
#   OUT / RGB_PWR_EN     —— 全局标签（与电源子图接口）
#   ROW0..5 / COL0..17   —— 全局标签（与矩阵子图接口，2026-09-18 起矩阵侧同为全局标签）
#   LED_DIN              —— 全局标签（去将来 RGB 子图；落地前是单端网）
#   595_MOSI / 595_SCK / 595_RCLK / CASCADE1 / CASCADE2 / MODE0..2 —— 本子图局部标签
# ---------------------------------------------------------------------------
CONN = {
    # --- J3A（Pro Micro 标号 1..12）-----------------------------------------
    "J3A.1": "LED_DIN",     # TX0 / D1  / P0.06 —— WS2812 数据（&spi3 MOSI）
    "J3A.2": None,          # RX1 / D0  / P0.08 —— NC。原厂 UART TX；P0.06(RX) 已被
                            #   WS2812 占用 ⇒ 串口日志本就不可用，此脚留作余量
    "J3A.3": "GND",
    "J3A.4": "GND",
    "J3A.5": "MODE0",       # D2  / P0.17 —— 档 0：有线
    "J3A.6": None,          # D3  / P0.20 —— NC，留普通 GPIO 余量
    "J3A.7": "ROW0",        # D4/A6 / P0.22
    "J3A.8": "ROW1",        # D5    / P0.24
    "J3A.9": "ROW2",        # D6/A7 / P1.00
    "J3A.10": "ROW3",       # D7    / P0.11
    "J3A.11": "ROW5",       # D8/A8 / P1.04 —— ⚠️ overlay row-gpios 第 6 项是 pro_micro 8
    "J3A.12": "ROW4",       # D9/A9 / P1.06 —— overlay 第 5 项是 pro_micro 9

    # --- J3B（引脚号 1..12 = Pro Micro 标号 13..24，即 J3B.n = 标号 12+n）----
    "J3B.1": "OUT",         # RAW(PM13) —— nice!nano 板载稳压输入，接电源子图系统轨 OUT。
                            #   ⚠️ 不是接 VBUS：电池供电时也必须有电（OUT = IN/BAT 较高者）
    "J3B.2": "GND",         # PM14
    "J3B.3": None,          # RST(PM15) —— NC：nice!nano 板载复位按钮够用（双击进 bootloader）
    "J3B.4": "VCC",         # VCC(PM16) —— nice!nano 输出的 3.3V 轨，给 3 颗 595 供电
    "J3B.5": None,          # D21/A3 / P0.31 (PM17) —— NC。**ADC 脚保留**（外接模拟量的
                            #   可能性：电量精确分压 / 温度）。⚠️ nice!nano v2 板载电池
                            #   分压在 P0.04（不在排针上），与此脚无冲突
    "J3B.6": None,          # D20/A2 / P0.29 (PM18) —— NC，ADC 脚保留
    "J3B.7": "595_RCLK",    # D19/A1 / P0.02 (PM19) —— 595 并行锁存（spi1 cs-gpios）
    "J3B.8": "MODE2",       # D18/A0 / P1.15 (PM20) —— 档 2：2.4G（Dongle）
    "J3B.9": "595_SCK",     # D15    / P1.13 (PM21)
    "J3B.10": "MODE1",      # D14    / P1.11 (PM22) —— 档 1：蓝牙
    "J3B.11": "595_MOSI",   # D16    / P0.10 (PM23)
    "J3B.12": "RGB_PWR_EN", # D10/A10 / P0.09 (PM24) —— 去电源子图 Q2 栅极（拓扑 C 反相级）

    # --- U2（级联第 1 颗，bit0..7）-------------------------------------------
    "U2.15": "COL0",        # QA
    "U2.1": "COL1",         # QB
    "U2.2": "COL2",         # QC
    "U2.3": "COL3",         # QD
    "U2.4": "COL4",         # QE
    "U2.5": "COL5",         # QF
    "U2.6": "COL6",         # QG
    "U2.7": "COL7",         # QH
    "U2.9": "CASCADE1",     # QH' —— 级联到 U3.SER
    "U2.14": "595_MOSI",    # SER
    "U2.11": "595_SCK",     # SRCLK（移位时钟）
    "U2.12": "595_RCLK",    # RCLK（锁存）
    "U2.10": "VCC",         # ~SRCLR —— 接 VCC = 不复位移位寄存器
    "U2.13": "GND",         # ~OE —— 接 GND = 输出常使能（扫描由列数据控制）
    "U2.16": "VCC",
    "U2.8": "GND",

    # --- U3（级联第 2 颗，bit8..15）------------------------------------------
    "U3.15": "COL8", "U3.1": "COL9", "U3.2": "COL10", "U3.3": "COL11",
    "U3.4": "COL12", "U3.5": "COL13", "U3.6": "COL14", "U3.7": "COL15",
    "U3.9": "CASCADE2",     # QH' —— 级联到 U4.SER
    "U3.14": "CASCADE1",    # SER ← U2.QH'
    "U3.11": "595_SCK", "U3.12": "595_RCLK", "U3.10": "VCC", "U3.13": "GND",
    "U3.16": "VCC", "U3.8": "GND",

    # --- U4（级联第 3 颗，bit16..17，其余空闲）-------------------------------
    "U4.15": "COL16",       # QA
    "U4.1": "COL17",        # QB
    "U4.2": None, "U4.3": None, "U4.4": None,     # QC..QE 空闲
    "U4.5": None, "U4.6": None, "U4.7": None,     # QF..QH 空闲
    "U4.9": None,           # QH' 空闲（链尾）
    "U4.14": "CASCADE2",    # SER ← U3.QH'
    "U4.11": "595_SCK", "U4.12": "595_RCLK", "U4.10": "VCC", "U4.13": "GND",
    "U4.16": "VCC", "U4.8": "GND",

    # --- SW1 三档开关（pin3 = 公共端）----------------------------------------
    "SW1.3": "GND",         # 公共端接 GND（ADR-0009：触点被选中时拉低，ACTIVE_LOW 读 0）
    "SW1.1": "MODE0",       # 档 0：有线（&out OUT_USB）
    "SW1.2": "MODE1",       # 档 1：蓝牙（&out OUT_BLE + BT_SEL 0）
    "SW1.4": "MODE2",       # 档 2：2.4G（&out OUT_BLE + BT_SEL 1 → Dongle）

    # --- 去耦 ----------------------------------------------------------------
    "C4.1": "VCC", "C4.2": "GND",
    "C5.1": "VCC", "C5.2": "GND",
    "C6.1": "VCC", "C6.2": "GND",
}

# 跨子图网络 → 全局标签（必须与电源子图 GLOBAL_NETS / 矩阵子图一致）
GLOBAL_NETS = {"OUT", "RGB_PWR_EN", "ROW0", "ROW1", "ROW2", "ROW3", "ROW4", "ROW5",
               "COL0", "COL1", "COL2", "COL3", "COL4", "COL5", "COL6", "COL7",
               "COL8", "COL9", "COL10", "COL11", "COL12", "COL13", "COL14",
               "COL15", "COL16", "COL17", "LED_DIN"}

# ---------------------------------------------------------------------------
# PWR_FLAG：VCC 网在本子图内只由 J3B.16（passive）驱动，没有 power_out 引脚
#   ⇒ 需要一个 PWR_FLAG，否则单图 ERC [power_pin_not_driven] error。
#
# ⚠️ **GND 不要在本图加 flag**：GND 是全局电源网，电源子图已经有一个 PWR_FLAG。
#    全局网上出现第二个 power output 会触发 ERC [pin_to_pin] error
#    （「Power output 与 Power output 已连接」，2026-09-18 M5 时实测）。
#    代价：单图视角下 GND 无驱动源 ⇒ control/verify 的 ERC 豁免里已把
#    power_pin_not_driven 列为预期（真实驱动源在电源子图）。
# ---------------------------------------------------------------------------
PWR_FLAGS = [
    dict(net="VCC", at=(101.6, 116.84)),
]

# ---------------------------------------------------------------------------
# 图面文字（只在原理图上可见；不进 BOM）
# 注意：不要在这里放 * / \ " 之类的字符（sexp 转义坑，见 handoff §10.2 第 11 条）。
# ---------------------------------------------------------------------------
NOTES = [
    (25.4, 33.02,
     "StarShield 控制板子图 —— 由 docs/_tools/gen_control_sch.py 自动生成，请勿手改；"
     "改电路请改 docs/_tools/control_design.py。依据：docs/adr/0008(修订) / 0009 / "
     "docs/controller-and-battery-facts.md / ZMK arduino_pro_micro_pins.dtsi"),
    (25.4, 43.18,
     "【排针映射】J3A.n = Pro Micro 标号 n（1..12），J3B.n = 标号 12+n（13..24）。"
     "映射来自 ZMK 官方 v0.3 nice_nano 的 arduino_pro_micro_pins.dtsi。"
     "投板前必须用实物核对排针 pitch / 每边脚数（handoff B6）"),
    (25.4, 190.5,
     "【595 级联与位序】3 颗 74HC595（2026-09-18 修订，原 2 颗无法驱动 18 列 —— "
     "bit16/17 会被推出链尾）。位序：bit0..7 = U2.QA..QH = COL0..7；"
     "bit8..15 = U3 = COL8..15；bit16..17 = U4.QA/QB = COL16/17。"
     "~SRCLR 接 VCC（不复位）、~OE 接 GND（输出常使能）。"
     "位序依据 ZMK gpio_595.c：SPI MSB first，先移出的位最终在链尾"),
    (25.4, 203.2,
     "【三档开关】SP3T PCM13，公共端(pin3)接 GND，三个掷点接 MODE0/1/2。"
     "ZMK 用 toggle-mode + sideband 读取（GPIO_ACTIVE_LOW，DT 不写 pull —— 驱动管理）。"
     "档 0 = 有线（USB 输出）；档 1 = 蓝牙直连主机（配对位 0）；档 2 = 2.4G（配对位 1 连 Dongle）。"
     "开关 GPIO 定案 D2(P0.17) / D14(P1.11) / D18(P1.15)：保留 D0(UART 语义)、"
     "D3(普通余量)、D20/D21(ADC 余量)"),
    (25.4, 216.0,
     "【供电】J3B.13(RAW) 接电源子图 OUT（系统轨 3.0-4.4V，电池/USB 较高者）—— "
     "nice!nano 板载稳压后输出 VCC(PM16) 3.3V，给 3 颗 595 供电（负载轻，远低于 VCC 能力）。"
     "WS2812 供电走 VLED（电源子图 Q1 门控后的 LED 轨），不在本子图 —— 见 RGB 子图(M5)"),
    (25.4, 228.6,
     "【与其它子图的接口】全局标签同名即相连：OUT/VLED/RGB_PWR_EN（电源子图）、"
     "ROW0..5 / COL0..17（矩阵子图，2026-09-18 起矩阵侧也是全局标签）、LED_DIN（RGB 子图，"
     "尚未绘制 ⇒ 本图 ERC 的 isolated warning 属已知待办）、GND（电源符号）"),
    (25.4, 241.3,
     "【投板前核对】1) nice!nano 排针 pitch/脚数（B6）2) PCM13 封装 pad 与符号掷点对应（B3/B4）"
     "3) J3A.11/12 = ROW5/ROW4 的交错顺序与 overlay row-gpios 一一对应（已按 overlay 核实，"
     "但 PCB 布局时仍需复核）"),
]
