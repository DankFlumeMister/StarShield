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

    # --- USB 输入保护（照抄 nightliner：装在 VBUS 侧，不是电池侧）-------------
    # ⚠️ 参考设计里唯一那颗装在**电池路径**上的保险丝（Conejo 的 F1）**不可照抄**：
    #    串在电池路径上会让 RGB 的全部放电电流流过它（本项目峰值可达 A 级）⇒ 必然误断。
    #    正确位置是 USB 输入侧：串在 VBUS 与充电器 IN 之间，既能挡住输入侧短路，
    #    又不参与电池放电回路（RGB 峰值电流不流经它）。
    # 📌 额定值变更史（P15，2026-09-18 定案）：
    #    - 初值 500 mA（照抄 nightliner；配 USB500 档）
    #    - 输入档切到 ILIM（1.0 A）后 500 mA **必然熔断** ⇒ 一度改为 1.5 A
    #    - ⚠️ **再改为 2 A（hold）**：按 Bourns MF-MSMF 系列官方降额表复核，
    #      1.5 A 档（MF-MSMF150/24X）在 **60 °C 环境下降额后 Ihold 仅 1.00 A**，
    #      恰好等于工作电流 ⇒ **零余量**；70 °C 时 0.88 A ⇒ **会误断**。
    #      键盘是密闭 3D 打印壳，且 BQ24072 在 1.0 A 时耗散 1.3 W ⇒ 板内 50–60 °C 完全可能。
    #      2 A 档（MF-MSMF200）在 60 °C 降额后仍 **1.50 A**（余量 50%），85 °C 时 1.25 A（余量 25%）。
    #    - 压降核算：Rmin 20 mΩ × 1.0 A = 20 mV；即便取 R1max 80 mΩ 也仅 80 mV
    #      ⇒ 5 V 输入仍剩 ≥4.92 V，远高于 VIN-DPM 上限 4.63 V ⇒ **不影响充电**。
    # ⚠️ 类型改为**自恢复保险丝（PTC）**，不用一次性熔断丝：新手不会换件，故障后冷却自愈。
    #    它只挡输入硬故障；**限流由 BQ24072 的 ILIM 档负责**，不要把保险丝当限流器。
    # ⚠️ 封装 0603 → **1812**（KiCad 官方 `Fuse:Fuse_1812_4532Metric` 已核实存在）。
    #    体积更大但更好手焊，不违背「被动件统一 0603」的本意（那条针对 R/C）。
    dict(ref="F1", lib="Device:Fuse", value="2A",
         fp="Fuse:Fuse_1812_4532Metric", at=(134.62, 71.12), rot=0,
         props={"MPN": "MF-MSMF200", "LCSC": "❓待补（BOM 阶段）",
                "Note": "USB 输入自恢复保险丝：hold 2.0A/trip 4.0A/8V/1812；60°C 降额后仍 1.50A"}),

    # --- 充电器外围 ---------------------------------------------------------
    # C_IN：⚠️ 硬上限 < 10 µF（USB-IF 浪涌要求）
    dict(ref="C1", lib="Device:C", value="1uF",
         fp="Capacitor_SMD:C_0603_1608Metric", at=(110.49, 78.74), rot=0,
         props={"Note": "VBUS 去耦，硬上限 <10uF"}),
    # R_ILIM：EN2=1/EN1=0 ⇒ **ILIM 档**，输入限流 = K_ILIM / R_ILIM = 1610 / 1600 ≈ 1.0 A。
    # ⚠️ 即使不用 ILIM 档也必须装（数据手册：悬空会关闭所有充电，且启动时要过 ILIM 短路检测）。
    # ⚠️ 1.0 A 输入**超出** 5.1 kΩ CC 下拉所声明的 500 mA —— 这是**有意的取舍**（P13，2026-09-18），
    #    对标 EPOMAKER TH87（10000 mAh / ≤1 A）。输入不足时由 VIN-DPM 自动降流兜底。
    #    完整论证见 docs/power-architecture.md §3.7。
    dict(ref="R3", lib="Device:R", value="1.6k",
         fp="Resistor_SMD:R_0603_1608Metric", at=(95.25, 99.06), rot=0,
         props={"Note": "ILIM 档：输入限流 1610/1.6k≈1.0A；悬空=关闭充电，必须装"}),
    # R_ISET：ICHG = 890 / R_ISET。**887 Ω ⇒ ≈1.00 A（= 0.10C @10000mAh）**。
    # 📌 2026-09-18 由 1.78 kΩ（0.5 A）改为 887 Ω，理由见 §3.7：
    #    商用同容量（≥5000 mAh）键盘的充电区间是 **0.035–0.163C**，0.5 A 只等于 0.049C
    #    （下三分之一）；1.0 A = 0.10C 落在区间中部，与 EPOMAKER TH87（10000mAh / ≤1A）一致。
    # ⚠️ 耗散 (5 − 3.7) × 1.0 = 1.3 W；按 JEDEC 板 RθJA = 44.5 °C/W 估 +58 °C（Tj ≈ 83 °C），
    #    低于 125 °C 热调节门限；键盘大铜皮下实际更低（未实测，见 §3.1 的 UNVERIFIED 列表）。
    # ⚠️ 不要再照抄社区那三家的 3.9 kΩ：它们的电池只有 200–500 mAh，
    #    0.23 A 对它们相当于 0.46–0.91C；本项目 10000 mAh 照抄会变成 0.023C（约 43 h）。
    #    R_ISET 一律按 **C 倍率**换算，不按绝对电流照抄。
    dict(ref="R4", lib="Device:R", value="887",
         fp="Resistor_SMD:R_0603_1608Metric", at=(95.25, 119.38), rot=0,
         props={"Note": "ICHG=890/887≈1.0A=0.10C@10000mAh，1%"}),
    # --- R_TMR 已移除（2026-09-17，容量变更为 2×5000 mAh 并联后）-------------
    # ⚠️ 位号 R10 空出**不复用**（保持与历史版本的可比性）。
    # 原值 47 kΩ（t_MAXCHG ≈ 6.25 h）是为 3000 mAh 电芯配的。容量翻到 10000 mAh 后，
    # **任何 R_TMR 取值都不够**：定时器上限 = 10 × R_TMR(72 kΩ 上限) × K_TMR
    # = 7.2 h(min) / 9.6 h(typ) / 12 h(max)（K_TMR = 36/48/60 s/kΩ）
    # ⇒ **按最坏情况只有 7.2 h**，而 ICHG 0.5 A 充满 10000 mAh 需约 20.6 h。
    # ⇒ 改为 `TMR` 直接接 VSS，禁用所有安全定时器（数据手册明确支持）。
    # 依据与代价（含三条替代路线）见 docs/power-architecture.md §3.5。
    # ⚠️ 这不是「拆掉保护」：定时器是 TI 的额外特性，消费级充电 IC 普遍没有它
    #    （商用 10000 mAh 键盘里就有 350 mA 充电、需要 28.6 h 的机型）。
    #    真正的保命线是电芯自带保护板 + 4.2 V 恒压 + 终止电流检测，三者本项目都有。
    # R_TS：10 kΩ 到 VSS ⇒ V_TS = 75 µA × 10 kΩ = 0.75 V，落在
    # V_HOT(300 mV) ~ V_COLD(2100 mV) 窗口内 ⇒ 不使用温度监测
    #（数据手册三处明确写出此法）。代价：放弃电池温度保护。
    # ⚠️ 不要改成「板上焊一颗 NTC」—— 它测的是板温（含充电器自热），会间歇性停充。
    #    四个方案的完整对比见 docs/power-architecture.md §3.3。
    dict(ref="R5", lib="Device:R", value="10k",
         fp="Resistor_SMD:R_0603_1608Metric", at=(95.25, 78.74), rot=0,
         props={"Note": "TS 到 VSS ⇒ 禁用温度监测（数据手册认可）"}),

    dict(ref="U1", lib="Battery_Management:BQ24072RGT", value="BQ24072RGT",
         fp="Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm_ThermalVias",
         at=(152.4, 96.52), rot=0,
         props={"MPN": "BQ24072RGT",
                "Note": "EP(17) 必须焊到接地铜皮；封装已选 ThermalVias 变体（社区同做法）"}),

    # --- 输出 / 电池 --------------------------------------------------------
    dict(ref="C2", lib="Device:C", value="4.7uF",
         fp="Capacitor_SMD:C_0603_1608Metric", at=(185.42, 55.88), rot=0,
         props={"Note": "OUT 稳定"}),
    dict(ref="C3", lib="Device:C", value="4.7uF",
         fp="Capacitor_SMD:C_0603_1608Metric", at=(185.42, 78.74), rot=0,
         props={"Note": "BAT 稳定"}),
    # --- 电池接口 -----------------------------------------------------------
    # ⚠️ 电池必须是 **1S2P 一体化电池包**（两块 5000 mAh 共用**一块** PCM），
    #    不可用两块「各自带保护板」的电芯直接并联：电压差会造成大电流互充，
    #    且两块 PCM 的过流/过压阈值失配 ⇒ 一块先切断、另一块独自承担全部负载。
    # ⚠️ 该 PCM 的过流保护阈值必须 >2 A：RGB 全亮峰值约 1.9 A，否则会触发保护断电。
    #    采购要求与选型见 docs/power-architecture.md §7。
    dict(ref="J2", lib="Connector_Generic:Conn_01x02", value="B2B-PH-K-S",
         fp="Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
         at=(203.2, 71.12), rot=0,
         props={"MPN": "B2B-PH-K-S(LF)(SN)", "LCSC": "C131337",
                "Note": "pin1=电池+  pin2=GND（极性不可反）；须接 1S2P 单 PCM 电池包 10000mAh"}),

    # --- 充电指示（~CHG 开漏，充电时拉到 VSS）--------------------------------
    dict(ref="R6", lib="Device:R", value="1.5k",
         fp="Resistor_SMD:R_0603_1608Metric", at=(185.42, 106.68), rot=0,
         props={"Note": "充电 LED 限流（约 1.2 mA @4.2V）"}),
    # 位号 D96：矩阵二极管占用了 D1..D95，充电 LED 顺延编 D96 ——
    # ⚠️ 不能用 D1（与矩阵 D1 冲突，根图整体网表会合并成同一元件，2026-09-18 实测发现）；
    #    也不建议 LED1（将来 RGB 子图的 95 颗 SK6812 会用 LED1..LED95）。
    dict(ref="D96", lib="Device:LED", value="RED",
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
    "F1.1": "VBUS", "F1.2": "VCHG_IN",
    # ⚠️ P2/P10 未决：第一版 USB-C 仅充电，数据引脚留 NC。
    #    若日后要「有线档走键盘自己的 USB-C」，把 D+/D- 改成全局标签 USB_DP/USB_DM，
    #    并在 B2 里接到主控。见 docs/power-architecture.md §4。
    "J1.A6": None, "J1.A7": None, "J1.B6": None, "J1.B7": None,
    "J1.A8": None, "J1.B8": None,
    "J1.SH": "GND",   # 屏蔽壳直接接地（第一版做法，EMC 最简）

    "R1.1": "CC1", "R1.2": "GND",
    "R2.1": "CC2", "R2.2": "GND",

    "C1.1": "VCHG_IN", "C1.2": "GND",
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
    "U1.5": "OUT",         # EN2=1
    "U1.6": "GND",         # EN1=0 ⇒ 与 EN2=1 组成 **ILIM 档**：输入限流由 R3(R_ILIM) 决定。
                           # 📌 2026-09-18 由 USB500 档切过来（用户决策 P13）。这是本项目
                           #    **唯一一处主动超出 USB-C 声明**的地方，理由与代价见
                           #    docs/power-architecture.md §3.7。
                           # ⚠️ EN2 接 OUT 而**不是** VBUS：EN2/EN1 绝对最大额定只有 7 V，
                           #    而 IN 可承受 26 V ⇒ 接 VBUS 遇到超压适配器会被打坏。
                           #    OUT 恒在 3.0–4.5 V，VIH(min)=1.4 V 稳定满足。
                           # 🔁 想改回 USB500 档（0.5 A）：把这四行复原 ——
                           #    U1.5→"GND"、U1.6→"OUT"，并把 R3 改 1.5k、R4 改 1.78k。
                           #    四个方案对比见 docs/power-architecture.md §3.2。
    "U1.7": None,          # ~PGOOD 开漏，第一版悬空（预留测试点）
    "U1.8": "GND",         # VSS
    "U1.9": "nCHG",        # ~CHG 开漏 → 充电 LED
    "U1.10": "OUT", "U1.11": "OUT",
    "U1.12": "ILIM",
    "U1.13": "VCHG_IN",    # IN —— 经 F1（2 A hold 自恢复保险丝）后的 USB 输入
    "U1.14": "GND",        # TMR 接 VSS = **禁用所有安全定时器**（数据手册原文支持）。
                           # ⚠️ 电池改为 2×5000 mAh 并联（10000 mAh）后，这是唯一可行接法：
                           #    ICHG 0.5 A 充满 10000 mAh 约需 20.6 h，而定时器**最长**
                           #    只能编到 10 × 72 kΩ × K_TMR = 7.2 h(min) / 9.6 h(typ) / 12 h(max)，
                           #    内部默认仅 5 h ⇒ 任何 R_TMR 都会在中途掐断，
                           #    结果「永远只用到约一半容量」（9.6 h × 0.5 A = 4800 mAh）
                           #    且 ~CHG 以 2 Hz 闪烁，是极难排查的间歇故障。
                           #    替代路线（切 ILIM 档提电流 / 接受插两次）见
                           #    docs/power-architecture.md §3.5。
                           # ⚠️ 不要在本行填网名 "TMR" —— 那会让 R_TMR 重新变成必需件。
    "U1.15": "GND",        # TD 接 VSS = 使能充电终止（数据手册要求不可悬空）
    "U1.16": "ISET",
    "U1.17": "GND",        # 散热焊盘 EP

    "J2.1": "VBAT", "J2.2": "GND",

    # --- 充电指示 ----------------------------------------------------------
    "R6.1": "OUT", "R6.2": "CHG_LED_A",
    "D96.1": "nCHG", "D96.2": "CHG_LED_A",   # Device:LED  pin1=K  pin2=A

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
    dict(net="VCHG_IN", at=(120.65, 66.04)),   # 保险丝之后的输入段也要有驱动源
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
     "【取值依据】U1=BQ24072RGT。电池 = 2x5000mAh 并联（1S2P 共用一块 PCM，共 10000mAh）。"
     "ICHG = 890 / R_ISET = 1.0 A（=0.10C @10000mAh）；EN2=1 且 EN1=0 选 ILIM 档，"
     "输入限流 = 1610 / R_ILIM = 1.0 A；~CE 接 VSS 常开；TD 接 VSS 使能充电终止；"
     "TS 经 10k 到 VSS 禁用温度监测；TMR 接 VSS 禁用所有安全定时器（10h 仍超定时器 typ 9.6h）。"
     "VBUS 经 F1（2A hold 自恢复保险丝，1812）后进 IN。"
     "注意：输入取 1.0A 超出 5.1k 的 USB 声明，是有意取舍，见 docs/power-architecture.md 3.7"),
    (25.4, 173.99,
     "【电源路径】负载必须接 OUT 而不是 BAT（ADR-0002）。OUT 稳压到 VBAT + 225 mV，"
     "满电时 OUT 约 4.4 V。VLED 由 OUT 经 Q1 门控 —— 属电池直供，不含任何升压（ADR-0007 / ADR-0005）"),
    (25.4, 182.88,
     "【走线电流约束】VLED 按 2-3 A 走线。但 BQ24072 的 OUT 短路保护阈值 VO(SC2) = 250 mV，"
     "VBAT - VOUT 超过该值并持续 250 us 即切断 OUT 并在 60 ms 后重试 "
     "=> 固件必须把 RGB 峰值限制在约 1 A（docs/power-architecture.md 5.2）"),
    (25.4, 191.77,
     "【电池与连接器约束】J2 为 JST-PH 2.0，额定 2 A（限 AWG #24 条件）。RGB 全亮峰值约 2.4 A 超过该额定，"
     "pigtail 请指定 AWG #24。电池须为 1S2P 一体化包（两块 5000mAh 共用一块 PCM），"
     "不可用两块各自带保护板的电芯直接并联（会互充，且两块保护板阈值失配）；"
     "PCM 的过流保护阈值必须大于 2A，否则 RGB 全亮会触发保护断电"),
    (25.4, 200.66,
     "【门控拓扑 C（ADR-0005，照抄 kurtis-lew/Conejo）】Q1 的 S 必须接电源轨 OUT、D 接负载轨 VLED —— "
     "P-MOS 体二极管阳极在 D，反接会让 LED 轨经体二极管常通，门控失效。"
     "ZMK 侧 ext-power 用 GPIO_ACTIVE_HIGH。控制链：GPIO 高 -> Q2 导通 -> Q1 栅极拉低 -> VLED 得电"),
    (25.4, 209.55,
     "【本版留空 / 未决项】USB-C 的 D+ D- SBU1 SBU2 全部 NC（J1 只做充电 —— "
     "nRF52840 的 USB 是独立专用引脚，nice!nano 排针上无引出）；"
     "U1 的 ~PGOOD 悬空（预留测试点）。F1 已按降额曲线定案为 2A hold 的 1812 自恢复保险丝"
     "（1.5A 档在 60°C 降额后仅 1.00A，等于工作电流，会误断）。"
     "详见 docs/power-architecture.md 第 6 节待办"),
    (25.4, 218.44,
     "【投板后必须实测】1) AO3401A 在 Vgs 约 -0.9 V 时的关断漏电（标 UNVERIFIED）"
     "2) RGB 峰值电流下 OUT 压降是否仍在 250 mV 以内 3) 深睡整机电流（目标约 20 uA）"
     "4) TMR 接 VSS 后充电能否正常走到 4.2 V 并靠终止电流判据结束（安全定时器已禁用）"),
]
