#!/usr/bin/env python3
"""power_design.py —— 电源子图的**电路设计数据**（单一真相源）

本文件只放「电路是什么」，不放「怎么画」。绘制逻辑全在 gen_power_sch.py。
改动电路（加元件、改网络、改取值）只改这里；改画法/版式只改生成器。

坐标系：KiCad 原理图坐标，mm，Y 轴向下。A3 图纸 420 × 297。
所有元件原点都取 1.27 mm 的整数倍 ⇒ 引脚端点自动落在连接网格上（避免 ERC [endpoint_off_grid]）。

设计依据（逐条已核实，勿凭记忆改）：
- `docs/power-architecture.md` §3 元件取值表（来源 TI SLUS810N 正文）
- `docs/bq24072-pinout.md` 引脚表（SLUS810N 表 7-1 + KiCad 官方符号双重核实）
- `docs/adr/0005` 拓扑 C：`2N7002` 反相级 + `AO3401A` 高边开关，`GPIO_ACTIVE_HIGH`
- 参考实现：`kurtis-lew/Conejo` Q3（`S=VDDH` 电源 / `D=EXT_PWR` 负载，体二极管方向正确）

⚠️ 本文件中每一处「非数据手册直接给出」的判断都写在注释里，标注了理由与风险。
"""

SHEET_TITLE = "StarShield 电源子图（充电 / 电池 / RGB 门控）"
SHEET_FILE = "power/power.kicad_sch"
PAPER = "A3"

# ---------------------------------------------------------------------------
# 元件表
#   ref  : 位号
#   lib  : KiCad 符号（必须在 power_symbols.json 里）
#   value: Value 属性
#   fp   : 封装
#   at   : 原点坐标 (x, y)，1.27 的整数倍
#   rot  : 旋转角（度，0/90/180/270）
#   props: 附加属性（MPN / LCSC 等），便于新手直接下单
# ---------------------------------------------------------------------------
COMPONENTS = [
    # --- USB-C 输入 ---------------------------------------------------------
    dict(ref="J1", lib="Connector:USB_C_Receptacle_USB2.0_16P",
         value="USB_C_Receptacle_USB2.0_16P",
         fp="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
         at=(50.8, 76.2), rot=0,
         props={"MPN": "TYPE-C-31-M-12", "LCSC": "C165948",
                "Note": "SMD 卧式正贴（非 mid-mount）"}),
    # --- CC 下拉：声明为 UFP 设备。⚠️ CC1 与 CC2 绝不可短接 -----------------
    dict(ref="R1", lib="Device:R", value="5.1k",
         fp="Resistor_SMD:R_0603_1608Metric", at=(95.25, 55.88), rot=0,
         props={"Note": "CC1 下拉 1%"}),
    dict(ref="R2", lib="Device:R", value="5.1k",
         fp="Resistor_SMD:R_0603_1608Metric", at=(110.49, 55.88), rot=0,
         props={"Note": "CC2 下拉 1%"}),

    # --- 充电器外围 ---------------------------------------------------------
    # C_IN：⚠️ 硬上限 < 10 µF（USB-IF 浪涌要求）
    dict(ref="C1", lib="Device:C", value="1uF",
         fp="Capacitor_SMD:C_0603_1608Metric", at=(110.49, 78.74), rot=0,
         props={"Note": "VBUS 去耦，硬上限 <10uF"}),
    # R_ILIM：EN2=0/EN1=1 选 USB500 档，此电阻不参与限流，但**必须装**
    #（数据手册：ILIM 悬空会关闭所有充电，且启动时要做 ILIM 短路检测）
    dict(ref="R3", lib="Device:R", value="1.6k",
         fp="Resistor_SMD:R_0603_1608Metric", at=(95.25, 99.06), rot=0,
         props={"Note": "USB500 档下不参与限流，但必须装（悬空=关闭充电）"}),
    # R_ISET：ICHG = 890 / R_ISET ⇒ 0.5 A。与 USB500 的 500 mA 输入上限相配，
    # 避免「编程 1 A 但永远达不到」的虚标。
    dict(ref="R4", lib="Device:R", value="1.78k",
         fp="Resistor_SMD:R_0603_1608Metric", at=(95.25, 119.38), rot=0,
         props={"Note": "ICHG=890/1.78k≈0.5A，1%"}),
    # R_TS：10 kΩ 到 VSS ⇒ V_TS = 75 µA × 10 kΩ = 0.75 V，落在
    # V_HOT(300 mV) ~ V_COLD(2100 mV) 窗口内 ⇒ 不使用温度监测
    #（数据手册三处明确写出此法）。代价：放弃电池温度保护。
    dict(ref="R5", lib="Device:R", value="10k",
         fp="Resistor_SMD:R_0603_1608Metric", at=(95.25, 78.74), rot=0,
         props={"Note": "TS 到 VSS ⇒ 禁用温度监测（数据手册认可）"}),

    dict(ref="U1", lib="Battery_Management:BQ24072RGT", value="BQ24072RGT",
         fp="Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm",
         at=(152.4, 96.52), rot=0,
         props={"MPN": "BQ24072RGT", "Note": "EP(17) 必须焊到接地铜皮 + 热过孔"}),

    # --- 输出 / 电池 --------------------------------------------------------
    dict(ref="C2", lib="Device:C", value="4.7uF",
         fp="Capacitor_SMD:C_0603_1608Metric", at=(185.42, 55.88), rot=0,
         props={"Note": "OUT 稳定"}),
    dict(ref="C3", lib="Device:C", value="4.7uF",
         fp="Capacitor_SMD:C_0603_1608Metric", at=(185.42, 78.74), rot=0,
         props={"Note": "BAT 稳定"}),
    dict(ref="J2", lib="Connector_Generic:Conn_01x02", value="B2B-PH-K-S",
         fp="Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
         at=(203.2, 71.12), rot=0,
         props={"MPN": "B2B-PH-K-S(LF)(SN)", "LCSC": "C131337",
                "Note": "pin1=电池+  pin2=GND（⚠️ 极性不可反）"}),

    # --- 充电指示（~CHG 开漏，充电时拉到 VSS）--------------------------------
    dict(ref="R6", lib="Device:R", value="1.5k",
         fp="Resistor_SMD:R_0603_1608Metric", at=(185.42, 106.68), rot=0,
         props={"Note": "充电 LED 限流（约 1.2 mA @4.2V）"}),
    dict(ref="D1", lib="Device:LED", value="RED",
         fp="LED_SMD:LED_0603_1608Metric", at=(185.42, 121.92), rot=0,
         props={"Note": "充电中亮，充满灭（选红光：低压差下仍可见）"}),

    # --- RGB 门控（拓扑 C，照抄 Conejo 的 S/D 方向）--------------------------
    # Q1 高边开关：S = OUT（电源轨）→ D = VLED（负载）
    # ⚠️ 方向绝不可反：P-MOS 体二极管 anode 在 D，反接会让 LED 轨经体二极管常通。
    dict(ref="Q1", lib="Transistor_FET:AO3401A", value="AO3401A",
         fp="Package_TO_SOT_SMD:SOT-23", at=(241.3, 60.96), rot=0,
         props={"MPN": "AO3401A", "Note": "P-MOS；S=OUT(电源) D=VLED(负载)"}),
    # R7：Q1 栅极上拉到源极（OUT）。GPIO 无法把栅极拉到 4.2 V，
    #      所以必须经 Q2 反相级；上拉只负责「Q2 未导通时确保关断」。
    dict(ref="R7", lib="Device:R", value="10k",
         fp="Resistor_SMD:R_0603_1608Metric", at=(261.62, 60.96), rot=0,
         props={"Note": "Q1 栅极上拉到 OUT"}),
    dict(ref="Q2", lib="Transistor_FET:2N7002", value="2N7002",
         fp="Package_TO_SOT_SMD:SOT-23", at=(241.3, 96.52), rot=0,
         props={"MPN": "2N7002", "Note": "N-MOS 反相级；D 接 Q1 栅极"}),
    dict(ref="R8", lib="Device:R", value="100",
         fp="Resistor_SMD:R_0603_1608Metric", at=(222.25, 96.52), rot=0,
         props={"Note": "Q2 栅极串联限流"}),
    dict(ref="R9", lib="Device:R", value="10k",
         fp="Resistor_SMD:R_0603_1608Metric", at=(261.62, 96.52), rot=0,
         props={"Note": "Q2 栅极下拉（MCU 未初始化时保证 LED 轨关断）"}),
]

# ---------------------------------------------------------------------------
# 网络连接表："位号.引脚号" -> 网名；None = 明确不接（生成 no_connect 标记）
#
# 网名约定：
#   GND  —— 用 power:GND 电源符号（全局）
#   VBUS / OUT / VLED / RGB_PWR_EN —— 用**全局标签**（跨子图，B2 控制板子图沿用同名）
#   其余 —— 本子图内局部标签
# ---------------------------------------------------------------------------
CONN = {
    # --- J1 USB-C ----------------------------------------------------------
    "J1.A1": "GND", "J1.A12": "GND", "J1.B1": "GND", "J1.B12": "GND",
    "J1.A4": "VBUS", "J1.A9": "VBUS", "J1.B4": "VBUS", "J1.B9": "VBUS",
    "J1.A5": "CC1", "J1.B5": "CC2",
    # ⚠️ P2/P10 未决：第一版 USB-C 仅充电，数据引脚留 NC。
    #    若日后要「有线档走键盘自己的 USB-C」，把 D+/D- 改成全局标签 USB_DP/USB_DM，
    #    并在 B2 里接到主控。见 docs/power-architecture.md §4。
    "J1.A6": None, "J1.A7": None, "J1.B6": None, "J1.B7": None,
    "J1.A8": None, "J1.B8": None,
    "J1.SH": "GND",   # 屏蔽壳直接接地（第一版做法，EMC 最简）

    "R1.1": "CC1", "R1.2": "GND",
    "R2.1": "CC2", "R2.2": "GND",

    "C1.1": "VBUS", "C1.2": "GND",
    "C2.1": "OUT", "C2.2": "GND",
    "C3.1": "VBAT", "C3.2": "GND",

    "R3.1": "ILIM", "R3.2": "GND",
    "R4.1": "ISET", "R4.2": "GND",
    "R5.1": "TS", "R5.2": "GND",

    # --- U1 BQ24072RGT -----------------------------------------------------
    "U1.1": "TS",          # TS 10k 到 VSS ⇒ 禁用温测
    "U1.2": "VBAT",        # BAT（power_out，双焊盘）
    "U1.3": "VBAT",
    "U1.4": "GND",         # ~CE 接 VSS = 常开（数据手册：CE 低 = 充电使能）
    "U1.5": "GND",         # EN2=0
    "U1.6": "OUT",         # EN1=1 ⇒ 与 EN2=0 组成 USB500 档。
                           # ⚠️ 接 OUT 而不是 VBUS：EN1 绝对最大额定 7 V，
                           #    而 IN 可承受 26 V ⇒ 接 VBUS 遇到超压适配器会被打坏。
                           #    OUT 恒在 3.0–4.5 V，VIH(min)=1.4 V 稳定满足。
    "U1.7": None,          # ~PGOOD 开漏，第一版悬空（预留测试点）
    "U1.8": "GND",         # VSS
    "U1.9": "nCHG",        # ~CHG 开漏 → 充电 LED
    "U1.10": "OUT", "U1.11": "OUT",
    "U1.12": "ILIM",
    "U1.13": "VBUS",       # IN
    "U1.14": None,         # TMR 悬空 = 用内部默认定时（预充 30 min / 快充 5 h）。
                           # ⚠️ ICHG=0.5 A 时 3000 mAh 充满约需 6 h > 5 h 默认值，
                           #    但定时器在 DPPM/热调节期间按比例变慢，故仍够用。
                           #    若日后把 ICHG 调到更小，必须改为装 R_TMR。
    "U1.15": "GND",        # TD 接 VSS = 使能充电终止（数据手册要求不可悬空）
    "U1.16": "ISET",
    "U1.17": "GND",        # 散热焊盘 EP

    "J2.1": "VBAT", "J2.2": "GND",

    # --- 充电指示 ----------------------------------------------------------
    "R6.1": "OUT", "R6.2": "CHG_LED_A",
    "D1.1": "nCHG", "D1.2": "CHG_LED_A",   # Device:LED  pin1=K  pin2=A

    # --- RGB 门控 ----------------------------------------------------------
    # 控制链：GPIO(HIGH) → R8 → Q2(G) 导通 → Q1(G) 被拉到 GND → Vgs=-V(OUT) → Q1 导通 → VLED 得电
    #         GPIO 未初始化/低 → R9 下拉 Q2 截止 → R7 把 Q1 栅极拉到 OUT → Vgs=0 → 关断
    "R8.1": "RGB_PWR_EN", "R8.2": "Q2_G",
    "R9.1": "Q2_G", "R9.2": "GND",
    "Q2.1": "Q2_G", "Q2.2": "GND", "Q2.3": "Q1_G",
    "R7.1": "OUT", "R7.2": "Q1_G",
    "Q1.1": "Q1_G", "Q1.2": "OUT", "Q1.3": "VLED",
}

# 需要跨子图的网络 → 用全局标签（B2 控制板子图沿用同名即可接上）
GLOBAL_NETS = {"VBUS", "OUT", "VLED", "RGB_PWR_EN"}

# 特殊单点标签：网名只在标签里出现、没有对应元件引脚时，仍需一个落脚点。
# （当前为空；留作扩展用）
SPARE_NETS = []

# ---------------------------------------------------------------------------
# PWR_FLAG：KiCad ERC 要求每条「有 power_in 引脚」的网络必须被某个 power_out 驱动。
#   VBUS —— 只有 J1 的 VBUS(passive) 与 U1 的 IN(power_in) ⇒ 需要 flag
#   GND  —— 只有各 power_in / passive ⇒ 需要 flag
#   OUT / VBAT 由 U1 的 power_out 引脚驱动，**不需要** flag（多放反而会被 ERC 提示）
# 实现：flag 直接放在与目标网络同一点（同点引脚自动相连），不额外拉线。
# ---------------------------------------------------------------------------
PWR_FLAGS = [
    dict(net="VBUS", at=(63.5, 50.8)),
    dict(net="GND", at=(30.48, 134.62)),
]

# ---------------------------------------------------------------------------
# 图面文字（只在原理图上可见，便于新手对照文档；不进 BOM）
# 注意：不要在这里放 * / \ " 之类的字符 —— 会被写进 sexp 字符串，虽有转义但仍易踩坑。
# ---------------------------------------------------------------------------
NOTES = [
    (25.4, 33.02,
     "StarShield 电源子图 —— 由 docs/_tools/gen_power_sch.py 自动生成，请勿手改；"
     "改电路请改 docs/_tools/power_design.py。依据：docs/power-architecture.md / docs/bq24072-pinout.md"),
    (25.4, 165.1,
     "【取值依据】U1=BQ24072RGT。ICHG = 890 / R_ISET = 0.5 A；"
     "EN2=0 且 EN1=1 选 USB500 档（输入上限 500 mA）；~CE 接 VSS 常开；TD 接 VSS 使能充电终止；"
     "TS 经 10k 到 VSS 禁用温度监测；TMR 悬空 = 内部默认定时（预充 30 min / 快充 5 h）"),
    (25.4, 173.99,
     "【电源路径】负载必须接 OUT 而不是 BAT（ADR-0002）。OUT 稳压到 VBAT + 225 mV，"
     "满电时 OUT 约 4.4 V。VLED 由 OUT 经 Q1 门控 —— 属电池直供，不含任何升压（ADR-0007 / ADR-0005）"),
    (25.4, 182.88,
     "【走线电流约束】VLED 按 2-3 A 走线。但 BQ24072 的 OUT 短路保护阈值 VO(SC2) = 250 mV，"
     "VBAT - VOUT 超过该值并持续 250 us 即切断 OUT 并在 60 ms 后重试 "
     "=> 固件必须把 RGB 峰值限制在约 1 A（docs/power-architecture.md 5.2）"),
    (25.4, 191.77,
     "【连接器约束】J2 为 JST-PH 2.0，额定 2 A（限 AWG #24 条件）。RGB 全亮峰值约 2.4 A 超过该额定，"
     "不可靠接插件承载全亮电流；pigtail 请指定 AWG #24"),
    (25.4, 200.66,
     "【门控拓扑 C（ADR-0005，照抄 kurtis-lew/Conejo）】Q1 的 S 必须接电源轨 OUT、D 接负载轨 VLED —— "
     "P-MOS 体二极管阳极在 D，反接会让 LED 轨经体二极管常通，门控失效。"
     "ZMK 侧 ext-power 用 GPIO_ACTIVE_HIGH。控制链：GPIO 高 -> Q2 导通 -> Q1 栅极拉低 -> VLED 得电"),
    (25.4, 209.55,
     "【本版留空 / 未决项】P2 与 P10：USB-C 的 D+ D- SBU 全部 NC（第一版 USB-C 仅充电）；"
     "U1 的 ~PGOOD 悬空（预留测试点）；U1 的 TMR 悬空。详见 docs/power-architecture.md 第 6 节待办"),
    (25.4, 218.44,
     "【投板后必须实测】1) AO3401A 在 Vgs 约 -0.9 V 时的关断漏电（标 UNVERIFIED）"
     "2) RGB 峰值电流下 OUT 压降是否仍在 250 mV 以内 3) 深睡整机电流（目标约 20 uA）"),
]
