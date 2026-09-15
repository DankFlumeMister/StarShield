# BQ24072 (RGT/VQFN-16) 充电 + 电源路径电路 — 已核实事实报告

> 面向 KiCad 原理图设计。所有结论均标注来源 URL。凡不能从一手来源核实的，一律标 `UNVERIFIED`。
> 拿不到 PDF 的环境限制已绕过：本报告中的 TI 数据来自**直接从 ti.com 下载的原始 PDF 并在本地做文本提取**（Node.js + pdf-parse），不是二手转述。

---

## 0. 核实方法与来源（可复现）

| 用途 | 一手来源 | 说明 |
|---|---|---|
| 主数据源 | **TI SLUS810N**（2008-09 首发，2021-10 修订）https://www.ti.com/lit/ds/symlink/bq24072.pdf | 3731441 bytes，53 页，提取出 103879 字符纯文本；本报告所有「表 x-y / 第 N 节」编号均指该文档 |
| 引脚表交叉核对（HTML 版，页级定位） | https://www.datasheetbank.com/en/datasheet-html/140846/Teccor-Electronics/7page/BQ24072.html （SLUS810L 镜像，PDF 第 7 页 = Pin Functions） | 与 SLUS810N 引脚表逐行一致 |
| 引脚号/引脚名/引脚类型交叉核对（独立第二来源） | KiCad 官方符号 `Battery_Management:BQ24072RGT` https://gitlab.com/kicad/libraries/kicad-symbols/-/blob/master/Battery_Management.kicad_symdir/BQ24072RGT.kicad_sym | 与 TI 引脚表 100% 一致（含 thermal pad 编号 17） |
| USB-C | **USB Type-C Cable and Connector Specification Release 2.5 (March 2026)** https://usb.org/document-library/usb-type-cr-cable-and-connector-specification-release-25 | 下载官方 ZIP → 解出 `USB Type-C Spec R2.5 - March 2026.pdf` → 本地提取 442 页 / 940596 字符 |

> 方法备注：常规网页抓取工具读不了 PDF；改用 Node 的 `fetch()` 直接下载文件到本地、用 `pdf-parse` 提取文本，再检索。KiCad 官方库现为 GitLab 上「一个符号/封装一个文件」的结构（旧 `kicad.github.io` HTML 文档页与 GitLab master **不同步**，见 §12 警告）。

---

## 1. BQ24072 完整引脚表（RGT, VQFN-16）

来源：SLUS810N **Table 7-1. Pin Functions**（PDF 第 7–9 页）https://www.ti.com/lit/ds/symlink/bq24072.pdf
引脚图来源：SLUS810N **Figure 7-1**（PDF 第 7 页）；交叉核对：KiCad `Battery_Management:BQ24072RGT`。

| Pin | Name | datasheet I/O | 功能类型 | 功能（一句话） | 家族差异（重要） |
|---|---|---|---|---|---|
| **1** | `TS` | I | Analog Input | 外部 NTC 热敏电阻输入；内部 `INTC` 电流源（75 µA typ）流过外部电阻形成 VTS，用于电池包温度监测 | 全家族一致（pin 1） |
| **2** | `BAT` | I/O | Power | 充电功率级输出 + 电池电压检测输入，接电池正极；对 VSS 并 4.7–47 µF 陶瓷电容 | 全家族一致 |
| **3** | `BAT` | I/O | Power | 同上（与 pin 2 内部同节点，双焊盘走流） | 全家族一致 |
| **4** | `CE` | I | Digital Input | 充电使能，**低有效**；拉高关断充电（此时 OUT 仍有效、支持 battery supplement）；内部 ~285 kΩ 下拉 | 全家族一致 |
| **5** | `EN2` | I | Digital Input | 输入限流配置（配合 EN1，见表 7-2）；内部 ≈285 kΩ 下拉，**不可悬空** | 全家族一致 |
| **6** | `EN1` | I | Digital Input | 输入限流配置；内部 ≈285 kΩ 下拉，**不可悬空** | 全家族一致 |
| **7** | `PGOOD` | O | Digital Output (open-drain) | 电源正常指示；有效输入源时拉低到 VSS，否则高阻 | 全家族一致 |
| **8** | `VSS` | – | Power (GND) | 地；必须与 thermal pad 及系统地相连 | 全家族一致 |
| **9** | `CHG` | O | Digital Output (open-drain) | 充电状态指示；充电中拉低，充满/充电禁用时高阻；故障时约 2 Hz 闪烁 | 全家族一致 |
| **10** | `OUT` | O | Power | 系统供电输出（power-path 输出）；对 VSS 并 4.7–47 µF | 全家族一致（但**调压点不同**，见 §2） |
| **11** | `OUT` | O | Power | 同上（与 pin 10 同节点） | 全家族一致 |
| **12** | `ILIM` | I | Analog Input | 输入限流编程：ILIM 到 VSS 接 1100 Ω–8 kΩ | 全家族一致 |
| **13** | `IN` | I | Power | 输入电源（AC adapter / USB 口）；对 VSS 并 1–10 µF | 全家族一致（**最高工作输入电压不同**，见 §2） |
| **14** | `TMR` | I | Analog Input | 预充/快充安全定时器编程（18–72 kΩ），接 VSS 关闭全部定时器，悬空用默认值 | 全家族一致 |
| **15** | `TD` | I | Digital Input | **仅 BQ24072/BQ24073**：拉高关闭充电终止；内部 ~285 kΩ 下拉 | ⚠️ **同一 pin 15 在 '74 是 `ITERM`、在 '75/'79 是 `SYSOFF`** |
| **16** | `ISET` | I/O | Analog Input/Output | 快充电流编程（590 Ω–8.9 kΩ）；充电时该脚电压正比于实际充电电流，可作电流监测 | 全家族一致 |
| **EP/17** | `Thermal Pad` | – | Power (GND) | 裸露热焊盘，**与 VSS 引脚内部电气相连**；PCB 上必须接到与 VSS 相同电位（KiCad 官方符号把它编号为 17 并映射为 VSS） | 全家族一致 |

**NC 引脚：没有。** 16 个引脚全部有定义，无 NC。封装只有这 16 pin + 裸露热焊盘。
来源：SLUS810N Table 7-1（引脚表无任何 NC 项）；KiCad 符号 `BQ24072RGT` 只定义 pin 1–16 + pin 17（pad，隐藏，passive，名为 VSS）。

**⚠️ 你在需求里列的几个名字在本器件上不存在：**
- `PRETERM` / `PRE-TERM`：**不存在**。预充电流不可编程，由内部系数决定（`IPRECHG = KPRECHG/RISET`，见 §4）。
- `TERM`：**不存在**。BQ24072 用 `TD`（pin 15）关闭终止；可调终止电流是 **BQ24074** 的 `ITERM`（也是 pin 15）。
- `OUTP`：**不存在**。系统输出就叫 `OUT`，占 pin 10 与 11 两个焊盘。
- `SYSOFF`：**BQ24072 上没有**（它是 BQ24075/BQ24079 的 pin 15）。
来源：SLUS810N Table 7-1、Table 6-1（Device Comparison Table）。

**引脚图（Top View，RGT0016B，16 Pins）** —— 来源 SLUS810N Figure 7-1：
```
       16     15     14     13
      ISET   TD    TMR    IN
  1 TS ┌──────────────────────┐ 12 ILIM
  2 BAT│                      │ 11 OUT
  3 BAT│      Thermal Pad     │ 10 OUT
  4 CE └──────────────────────┘  9 CHG
        5      6      7      8
       EN2    EN1   PGOOD   VSS
```
（BQ24075/BQ24079 的 Figure 7-3 位置相同，只是 pin 15 丝印为 `SYSOFF`。）

---

## 1b. 原理图接线清单（可直接照着画）

| Pin | 网络 | 元件/接法 | 依据 |
|---|---|---|---|
| 1 `TS` | `TS` | 正常：10 kΩ NTC（103AT-2）到 GND；**停用温度检测：单个 10 kΩ 1% 电阻到 GND** | §3 |
| 2, 3 `BAT` | `VBAT` | 接电池正极 + **4.7 µF**（范围 4.7–47 µF）到 GND；两脚短接 | §9 |
| 4 `CE` | `CE` | 低 = 充电使能；**不可悬空**（内部 285 kΩ 下拉）。不需要 MCU 控制时直接接 GND | Table 7-1 |
| 5 `EN2` | `EN2` | 见 §5 真值表；**不可悬空** | Table 7-2 |
| 6 `EN1` | `EN1` | 见 §5 真值表；**不可悬空** | Table 7-2 |
| 7 `PGOOD` | `PGOOD` | 开漏：1 k–100 kΩ 上拉到逻辑电源，或 1.5 kΩ + LED 到 `OUT`；不用可悬空 | Table 7-1 |
| 8 `VSS` | `GND` | 必须接地（与 thermal pad 同电位） | Table 7-1 |
| 9 `CHG` | `CHG` | 同 PGOOD，开漏 | Table 7-1 |
| 10, 11 `OUT` | `VSYS` | 系统供电轨 + **4.7 µF**（范围 4.7–47 µF）到 GND；两脚短接 | §9 |
| 12 `ILIM` | `ILIM` | **总要放电阻到 GND**（USB500 场景可放 1.6 kΩ；ILIM 模式按 §5 算） | §5 |
| 13 `IN` | `VBUS_USB` | USB-C VBUS（A4/A9/B4/B9 并联）+ **1 µF**（1–10 µF，**必须 < 10 µF**）到 GND | §5/§9/§11 |
| 14 `TMR` | `TMR` | 46.4 kΩ 到 GND（6.25 h）；悬空 = 默认 5 h/30 min；接 GND = 关闭定时器 | §6 |
| 15 `TD` | `TD` | 低 = 启用终止（默认，可接 GND）；**高 = 关闭终止**（注意同时会关闭安全定时器，并可能关闭 TS）；**不可悬空** | §7 |
| 16 `ISET` | `ISET` | 按 §4 选 1% 电阻到 GND（0.5 A→1.78 kΩ，1 A→887 Ω，1.5 A→590 Ω）；**悬空 = 禁止充电** | §4 |
| EP/17 | `GND` | 热焊盘，**必须焊接**并接到 GND 平面（多过孔、大铜面） | §10 |
| USB-C `A5`/`B5` | `CC1`/`CC2` | 各接 **5.1 kΩ（±10%）到 GND**，**不得短接** | §11.2 |
| USB-C `SH`×4 | `GND` | 外壳直接接 PCB 地平面 | §11.3 |

---

## 2. 家族差异（BQ24072 / 73 / 74 / 75 / 79）— 最容易画错的地方

来源：SLUS810N **Table 6-1 Device Comparison Table**（PDF 第 6 页）https://www.ti.com/lit/ds/symlink/bq24072.pdf

| 器件 | VOVP | VBAT(REG) | VOUT(REG)（OUT 调压点） | VDPPM | 特有功能脚 | 数据手册标注封装 |
|---|---|---|---|---|---|---|
| **BQ24072** | 6.6 V | 4.2 V | **VBAT + 225 mV**（文本第 9.3.4.1 节写作 "200 mV above BAT"；电气表给 150/225/270 mV min/typ/max） | VO(REG) − 100 mV | `TD` | RGT0016C |
| BQ24073 | 6.6 V | 4.2 V | 4.4 V | VO(REG) − 100 mV | `TD` | — |
| BQ24074 | **10.5 V** | 4.2 V | 4.4 V | VO(REG) − 100 mV | `ITERM` | — |
| BQ24075 | 6.6 V | 4.2 V | 5.5 V | 4.3 V | `SYSOFF` | RGT0016C |
| BQ24079 | 6.6 V | **4.1 V** | 5.5 V | 4.3 V | `SYSOFF` | RGT0016B |

**关键结论（画原理图前必读）：**
1. **pin 15 是三种不同功能**：`TD`('72/'73) / `ITERM`('74) / `SYSOFF`('75,'79)。原理图符号若用通用 16 脚符号，务必确认 pin 15 的网络名。
2. **`IN` 最高工作电压**：'72/'73/'75/'79 = 4.35–6.4 V；'74 = 4.35–10.2 V（绝对最大 26 V，超过 OVP 只是暂停工作）。用 5 V USB 供电时 '72 完全够用。
3. **OUT 调压点**：'72 的 OUT 跟随电池（VBAT + 225 mV typ，VBAT < 3.2 V 时钳在 3.4 V），**不是**固定 4.4 V。若你的系统需要 4.4 V 固定轨，那是 '73/'74；若需要 5.5 V，那是 '75/'79。
4. **封装后缀在文档内自相矛盾**：Figure 7-1/7-2 标注 "BQ24072, BQ24073 RGT0016B Package"，而 Table 6-1 写 BQ24072 → RGT0016C；Figure 7-3 写 "BQ24075 RGT0016C / BQ24079 RGT0016B"。订货信息（Orderable Addendum）只写 `VQFN (RGT) | 16`。**结论：物理上是同一个 3×3 mm VQFN-16（RGT），KiCad 官方符号关联的封装是 `Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm`**（来源：KiCad 符号属性 `Footprint`，见 §0 链接）。RGT0016B/C 的差异未在数据手册中说明 → 标 `UNVERIFIED`。

---

## 3. `TS` 引脚（温度检测）— 全部数值

来源：SLUS810N **8.5 Electrical Characteristics → BATTERY-PACK NTC MONITOR**（PDF 第 13 页）、**9.3.6 Battery Pack Temperature Monitoring**（PDF 第 29–30 页）、**Table 7-1 TS 行**。

| 参数 | 数值（min / typ / max） | 单位 | 条件 |
|---|---|---|---|
| `INTC` NTC 偏置电流（TS 输出电流） | **72 / 75 / 78** | µA | VIN > UVLO 且 VIN > VBAT + VIN(DT) |
| `VHOT` 高温跳变点 | **270 / 300 / 330** | **mV**（不是 %VIN！） | Battery charging，VTS **falling** |
| `VHYS(HOT)` 高温迟滞 | 30 | mV | VTS 从 VHOT 回升 |
| `VCOLD` 低温跳变点 | **2000 / 2100 / 2200** | **mV** | Battery charging，VTS **rising** |
| `VHYS(COLD)` 低温迟滞 | 300 | mV | VTS 从 VCOLD 回落 |
| `tDGL(TS)` 温度故障去抖 | 50 | ms | 检测到故障 → 关断充电 |
| `VDIS(TS)` 判定"未使用温度检测"的阈值（'72/'73） | **VIN − 200** | mV | TS 悬空 → 被内部电流源顶到接近 VIN，超过该阈值即判定 TS 未使用（关闭 TS 功能） |

**→ 直接回答你的问题：阈值是绝对电压（mV），不是 VIN 的百分比。** 工作窗口 = 2.1 V（冷端）到 0.3 V（热端），中间是允许充电区间。

**→ 关闭温度检测（不用 NTC）的官方做法：单个 10 kΩ 电阻，从 TS 接到 VSS。不是分压器。**
原文（Table 7-1 TS 行）："For applications that do not use the TS function, connect a **10-kΩ fixed resistor from TS to VSS** to maintain a valid voltage level on TS."
原文（9.3.6 节）："For applications that do not require the TS monitoring function, connect a **10-kΩ resistor from TS to VSS** to set the TS voltage at a valid level and maintain charging."
原文（10.2.2.3 TS Function，设计示例）："Use a 10-kΩ NTC thermistor in the battery pack (103AT-2). For applications that do not require the TS monitoring function, connect a **10-kΩ resistor from TS to VSS**…"
数学上也自洽：75 µA × 10 kΩ = **0.75 V**，落在 0.3 V…2.1 V 窗口内。
（**注意**：并不是"TS 必须永远接 10 kΩ NTC"。NTC 是正常用法，固定 10 kΩ 是官方给出的停用方法。）

**扩展温度窗口（可选）**：加 `Rs`（与 NTC 串联到 TS）和 `Rp`（TS 到 VSS 并联），公式见 SLUS810N 式 (8)(9)，其中 `VH` = 0.3 V nom、`VC` = 2.1 V nom、`ITS` = 75 µA nom，NTC 型号 Semitec 103AT-4。Table 9-3 给出 6 组 1% 标准值，例如 `RCOLD = 33890 Ω(−5 °C)`、`RHOT = 3021 Ω(60 °C)` → `Rs = 1100 Ω`、`Rp = 140 kΩ`。原文明确："The temperature window cannot be tightened more than using only the thermistor connected to TS, it can only be **extended**."

**⚠️ 与 `TD` 的交互（BQ24072 特有）**：9.3.5.3 节 —— "Battery pack temperature sensing (TS pin functionality) is **disabled if the TD pin is high and the TS pin is unconnected or pulled up to VIN**." 即 TD 拉高（关闭终止）且 TS 悬空/上拉到 VIN 时，温度检测也一起失效。

---

## 4. `ISET` 引脚（快充电流编程）

来源：SLUS810N 8.3 Recommended Operating Conditions（PDF 第 10 页）、8.5 Electrical Characteristics（第 12–13 页）、9.3.5 Battery Charging（第 25 页）、10.2.2.2.1（第 34 页）。

**公式（数据手册式 (2)）**：
```
ICHG = KISET / RISET
KISET = 890 AΩ (typ)，797 (min) / 975 (max)        ← 8.5 节
RISET 有效范围 = 590 Ω … 8900 Ω                    ← 8.3 节（注：1% 精度电阻）
ICHG 可编程范围 = 100 mA … 1500 mA
```

**你要的 0.5 A / 1.0 A / 1.5 A 电阻值**（用 KISET = 890 AΩ typ 计算；「标准值」列是我按 E96 选的，数据手册只给了 590 Ω / 8.9 kΩ 边界值）：

| 目标 ICHG | 计算 RISET = 890/I | 建议标准值 | 说明 |
|---|---|---|---|
| 0.5 A | 1780 Ω | **1.78 kΩ**（E96；1.8 kΩ/E24 也行 → 0.494 A） | |
| 1.0 A | 890 Ω | **887 Ω**（E96 → 1.003 A）或 **910 Ω**（E24 → 0.978 A） | 1% 精度 |
| 1.5 A | 593.3 Ω | **590 Ω**（E48/E96） | 590 Ω 正是数据手册给出的**下限**，对应 890/590 = 1.508 A；再小会超出器件能力 |

（标准值系列归属是我按 IEC 60063 系列选的，非数据手册原文；数据手册只给出 590 Ω 与 8.9 kΩ 两个边界值。）

**配套公式：**
- 预充电流：`IPRECHG = KPRECHG / RISET`，`KPRECHG = 70 / 88 / 106 AΩ`（typ 88）→ 约等于 ICHG 的 9.9%（**没有 PRETERM 引脚**，预充电流不可单独编程）。
- 电流监测输出：`VISET = ICHARGE / 400 × RISET`（ISET 输出电流是充电电流的 1/400 (±10%)）。
- 若 `ICHG` 编程值大于输入限流，电池不会按 ICHG 充，而是按 `IIN(MAX)`（减去 OUT 上的负载电流）充；此时充电定时器会按比例放慢。
- **`ISET` 悬空 = 禁止充电**（Table 7-1 原文："Charging is disabled if ISET is left unconnected."）。

---

## 5. `ILIM` 引脚（输入限流）

来源：SLUS810N **式 (1)**（9.3.4.1.1 之前，PDF 第 21 页）、8.5 节（第 12 页）、Table 7-1/7-2、10.2.2.2.2（第 34 页）。

**公式：**
```
IIN-MAX = KILIM / RILIM
KILIM = 1610 AΩ (typ)  条件 ILIM = 500 mA…1.5 A；min 1500 / max 1720
KILIM = 1525 AΩ (typ)  条件 ILIM = 200 mA…500 mA；min 1330 / max 1720
RILIM 有效范围 = 1100 Ω … 8000 Ω      （编程范围 200 mA … 1500 mA）
```

**先看 EN1/EN2 表（Table 7-2）——很多设计根本不需要 ILIM 电阻：**

| EN2 | EN1 | 限制 IN 引脚最大输入电流 |
|---|---|---|
| 0 | 0 | 100 mA（USB100 模式） |
| 0 | 1 | **500 mA（USB500 模式，USB 2.0 默认电流，最常用）** |
| 1 | 0 | **由 ILIM 到 VSS 的外部电阻决定** |
| 1 | 1 | Standby（USB suspend） |

**USB 供电设计的推荐值：**
- 只想符合 USB 2.0 默认 500 mA：`EN2 = 0, EN1 = 1`（USB500），此时限流由内部设定，**理论上不需要 ILIM 电阻**。
- **但强烈建议无论如何都放一颗 ILIM 电阻**：数据手册 8.5 节有 "**ILIM, ISET SHORT-CIRCUIT DETECTION (CHECKED DURING STARTUP)**"（`ISC` = 1.3 mA 电流源 / `VSC` = 520 mV 判据），并在 Table 7-1 ILIM 行写明 "**Leaving ILIM unconnected disables all charging**"。两句话的组合意味着**悬空 ILIM 有可能在启动自检时被判为异常而禁止充电**（且该自检是否在 USB100/USB500 模式下也生效，文档没有写清 → §Uncertain 第 3 条）。**工程上：永远放 ILIM 电阻**，或严格按 Figure 10-1 的接法。
- 想用 1.5 A 输入：`EN2 = 1, EN1 = 0`，`RILIM = 1610/1.5 ≈ 1073 Ω` → 选 **1.07 kΩ**（E96），留余量可选 1.1 kΩ（= 1.46 A typ）。
- 数据手册自己的设计示例：目标 `IIN(MAX) = 1.3 A`，它取 **KILIM = 1550 AΩ**（示例文字写 1550，注意与电气表 typ 1610 不同）→ 算得 1.192 kΩ → 选 **1.18 kΩ**；同例 `RISET = 1.13 kΩ`（800 mA）、`RTMR = 46.4 kΩ`（6.25 h）、CHG/PGOOD 各串 **1.5 kΩ + LED**。
- 输入电容有硬性上限：USB-IF inrush 要求硬启动电容 ≤ 10 µF（9.3.4.1 节），**IN 端电容必须 < 10 µF**。
- `VIN-DPM`（仅在 USB100/USB500 模式生效）= 4.35 / 4.5 / 4.63 V：输入跌到该阈值时限流自动下调，防止把劣质 USB 源拉崩。

---

## 6. `TMR` 引脚（安全定时器）

来源：SLUS810N 8.5 节 BATTERY CHARGING TIMERS（PDF 第 13 页）、9.3.5.6 Dynamic Charge Timers（PDF 第 27 页）、10.2.2.2.4（PDF 第 34 页）。

**公式：**
```
tPRECHG = KTMR × RTMR
tMAXCHG = 10 × KTMR × RTMR
KTMR = 48 s/kΩ (typ)，36 (min) / 60 (max)
RTMR 有效范围 = 18 kΩ … 72 kΩ
```

**TMR 悬空（不接）= 使用内部默认定时器：**

| 条件 | 预充安全定时器 tPRECHG | 快充安全定时器 tMAXCHG |
|---|---|---|
| `TMR` 悬空 | 1440 / **1800** / 2160 s（typ **30 min**） | 14400 / **18000** / 21600 s（typ **5 h**） |
| 18 kΩ < RTMR < 72 kΩ | RTMR × KTMR | 10 × RTMR × KTMR |
| `TMR` 接 VSS | **关闭全部安全定时器** | 同左 |

**示例**：要 6.25 h 快充定时器 → `RTMR = (6.25 × 3600) / (10 × 48) = 46.8 kΩ` → 选 **46.4 kΩ**。
**行为**：DPPM / VIN-DPM / 热调节导致充电电流下降时，定时器按电流减小比例同步放慢；定时器到期而电池仍未到 VLOWV（预充）或电流未降到 ITERM（快充）→ 故障，**CHG 以约 2 Hz 闪烁**；故障由 CE 翻转、输入掉电、进出 USB suspend 或 OVP 事件清除。定时器可用 CE 或 EN1/EN2 进/出 suspend 复位。

---

## 7. 终止（TERM / termination）

来源：SLUS810N 8.5 节 ITERM（PDF 第 13 页）、9.3.5.2（第 27 页）、9.3.5.3 Termination Disable（第 27 页）、Table 9-2（第 28 页）。

**BQ24072 的终止电流是内部固定的，不能调：**

| 模式 | 终止阈值（typ） | min / max |
|---|---|---|
| USB500 或 ISET 模式（EN1, EN2 不同时为低） | **0.1 × ICHG** | 0.09 × ICHG / 0.11 × ICHG |
| USB100 模式（EN1 = EN2 = 低） | **0.033 × ICHG** | 0.027 × ICHG / 0.040 × ICHG |

**要"可调终止电流"必须换 BQ24074**（`ITERM` = pin 15，`RITERM` 0–15 kΩ）：
`ITERM = 0.03 × RITERM / RISET`（USB500 / ISET 模式）；`ITERM = 0.01 × RITERM / RISET`（USB100 模式）；最大可编程到快充电流的 50%；`ITERM` 悬空 = 用内部默认 10%。数据手册示例：ITERM 目标 110 mA，`RITERM = 110 mA × 1.13 kΩ / 0.030 = 4.143 kΩ` → 选 **4.12 kΩ**。

**BQ24072 如何"关闭终止"：把 `TD`（pin 15）拉高。**
- 原文："Connect TD high to disable charger termination. Connect TD to VSS to enable charger termination. TD is **checked during startup only** and cannot be changed during operation."（Table 7-1；9.3.5.3 同）
- TD 内部 ~285 kΩ 下拉，**不可悬空**。
- 关闭终止后的行为（9.3.5.3 原文要点）：仍走 预充 → 快充 → CV 三阶段，然后**停留在 CV 阶段**，充电电流不终止（电流 = ICHG 或 IINmax 取小者）；**不做电池在位检测**；电流降到 ITERM 以下后 CHG 变高阻且不再拉低（除非切换输入电源或 CE）；**预充与快充安全定时器同时失效**；如上所述 TS 功能也可能失效。

---

## 8. Power-path / DPPM 行为，以及 `SYSOFF`

来源：SLUS810N 9.3.4（PDF 第 21–22 页）、9.3.5.5（第 27 页）、8.5 节 POWER PATH（第 12 页）、10.1（第 33 页）。

**确认：OUT 在 BAT 充电的同时给系统供电。** 原文（10.1 Application Information）："The BQ2407x devices **power the system while simultaneously and independently charging the battery**… The devices feature dynamic power-path management (DPPM), which **shares the source current between the system and battery charging** and automatically reduces the charging current if the system load increases."

**工作过程：**
1. 有输入源时：输入电流在「充电池」与「供 OUT 负载」之间分配；总输入电流受 EN1/EN2 或 ILIM 限制。
2. 负载增大使 OUT 跌到 `VDPPM`（'72/'73/'74 = VO(REG) − 100 mV typ）→ 进入 **DPPM 模式**，自动减小充电电流以维持 OUT。
3. 充电电流已降到 0 而负载仍超限 → OUT 继续下跌，跌破 `VBSUP1`（低于 VBAT 约 40 mV）→ 进入 **Battery Supplement 模式**，由电池补足系统电流（BAT-FET 全开，不调流；内置短路保护：VOUT 低于 VBAT 超过 `VO(SC2)` 250 mV 且持续 250 µs → 关断 OUT，60 ms 后重试）。
4. 以上 DPPM / supplement / VIN-DPM / 热调节期间，**电池终止检测被禁用**（9.3.5 原文："termination detection is disabled whenever the charge rate is reduced because of the actions of the thermal loop, the DPPM loop or the VIN-DPM loop"）。
5. 无输入源时：OUT 通过内部 FET 直接连到 BAT（`VDO(BAT-OUT)` = 50/100 mV @ IOUT = 1 A, VBAT > 3 V）；进入 sleep 模式 >20 ms 后 IN↔OUT FET 断开，输入端接地也不会放电（BAT 漏电 4.3/6.5 µA）。

**`SYSOFF`（就 BQ24072 而言：不存在）**
- `SYSOFF` 只在 **BQ24075 / BQ24079** 上（pin 15）。功能：拉高 → 关断连接电池与 OUT 的 FET Q2，把系统负载与电池断开；接适配器时充电也一并禁用；正常工作要求接 VSS；内部约 5 MΩ 上拉到 VBAT，**不可悬空**。（SLUS810N 9.3.5.5 + Table 7-1）
- **BQ24072 的 pin 15 是 `TD`。** 如果你的设计依赖"用 GPIO 切断系统与电池"，BQ24072 做不到（它只能关闭终止）；需要 SYSOFF 就选 BQ24075/79，或像本设计那样外加一个负载开关/滑动开关。

---

## 9. 数据手册推荐外部元件（典型应用，Figure 10-1 + 各节文字）

来源：SLUS810N Figure 10-1（PDF 第 33 页，主机控制充电器应用，BQ24072/BQ24073）、10.2.1 Design Requirements、10.2.2.4 CHG/PGOOD、10.2.2.5（第 34–35 页）、Table 7-1 各引脚描述。典型应用条件：`VIN = UVLO…VOVP`、`IFASTCHG = 800 mA`、`IIN(MAX) = 1.3 A`、充电温度区间 0–50 °C、6.25 h 快充定时器。

| 位置 | 数据手册取值 | 允许范围（Table 7-1 等） | 说明 |
|---|---|---|---|
| `IN` → VSS | **1 µF** | **1 µF … 10 µF** | 陶瓷；USB-IF inrush 要求硬启动电容 < 10 µF |
| `OUT` → VSS | **4.7 µF** | 4.7 µF … 47 µF | 陶瓷；大脉冲负载可加大 |
| `BAT` → VSS | **4.7 µF** | 4.7 µF … 47 µF | 陶瓷 |
| `ISET` → VSS | **1.13 kΩ**（示例，对应 800 mA） | 590 Ω … 8.9 kΩ，**1% 精度** | 数据手册注明用 1% 电阻以避免 RISET 短路测试问题 |
| `ILIM` → VSS | **1.18 kΩ**（示例，对应 1.3 A，取 KILIM = 1550） | 1100 Ω … 8 kΩ | 仅 EN2=1, EN1=0 时生效 |
| `TMR` → VSS | **46.4 kΩ**（示例，6.25 h） | 18 kΩ … 72 kΩ；悬空 = 默认 5 h / 30 min；接 VSS = 关闭 | |
| `TS` → VSS | 10 kΩ NTC（103AT-2）或 **10 kΩ 固定电阻**（停用温度检测） | — | 见 §3 |
| `CHG` 上拉/LED | **1.5 kΩ + LED 到 OUT**（示例）；或 1 kΩ–100 kΩ 上拉到逻辑电源轨 | 开漏输出，**必须**有上拉或 LED | 灌电流能力 CHG/PGOOD ≤ 15 mA（绝对最大） |
| `PGOOD` 上拉/LED | **1.5 kΩ + LED 到 OUT**（示例）；或 1 kΩ–100 kΩ 上拉到逻辑电源轨 | 同上 | 主机监控时数据手册建议约 100 kΩ 上拉 |
| 电感 | **无**（线性充电器，不含电感、不含开关） | — | 只有电容/电阻 |
| `EN1`/`EN2`/`CE`/`TD` | 必须给明确电平 | 内部 ≈285 kΩ 下拉，"Do not leave … unconnected" | 由 MCU 或电阻确定 |

**Figure 10-1 中 refdes↔数值的对应关系注意**：从 PDF 文本流中能确定存在的元件值为 `R = 1.13 kΩ / 1.18 kΩ / 46.4 kΩ / 1.5 kΩ / 1.5 kΩ`，`C = 1 µF / 4.7 µF / 4.7 µF`；但由于文本提取顺序，**哪个 refdes 对应哪个电容（C1/C2/C3 ↔ IN/OUT/BAT）未能 100% 确认**（标 `UNVERIFIED`）。设计上无影响：按上表范围分配即可（IN 用小值 1 µF，OUT/BAT 用 4.7 µF）。

---

## 10. 热设计（Thermal / 热焊盘 / 1.5 A 时的行为）

来源：SLUS810N 8.1（注 2）、8.3、8.4 Thermal Information、8.5 THERMAL REGULATION、9.3.5.8、12.1 Layout Guidelines、封装图 NOTES 第 3 条。

| 项目 | 数值/要求 | 出处 |
|---|---|---|
| 热焊盘是否必须焊接 | **必须**："The package thermal pad **must be soldered to the printed circuit board** for thermal and mechanical performance." | 封装机械图 NOTES 3（PDF 第 50 页） |
| 热焊盘电气连接 | 与 VSS 引脚**内部电气相连**；PCB 上必须接到与 VSS 相同电位；**不得**把热焊盘当作器件的主接地输入；VSS 引脚（pin 8）任何时刻都必须接地 | Table 7-1 Thermal Pad 行；12.1 节："this thermal pad is also the main ground connection for the device. Connect the thermal pad to the PCB ground connection." |
| 术语 | 数据手册称 **"thermally enhanced MLP package"**；**"PowerPAD" 一词在 SLUS810N 中并未出现**（grep 全文 0 命中）。"PowerPAD" 是 TI 对类似裸露焊盘封装的商标名，不要在本器件文档里引用该词 | 8.5/12.1；本次全文检索 |
| RθJA（结到环境） | **44.5 °C/W**（RGT, 16 pins） | 8.4 节 |
| RθJC(top) / RθJB / ψJT / ψJB / RθJC(bot) | 54.2 / 17.2 / 1.0 / 17.1 / **3.8** °C/W | 8.4 节 |
| `TJ(REG)` 热调节起点 | **125 °C** | 8.5 节 |
| `TJ(OFF)` 热关断 | **155 °C**（迟滞 20 °C） | 8.5 节 |
| 1.5 A 充电时的限制 | 绝对最大/推荐最大充电电流 **1.5 A**；注 2："The IC operational charging life is reduced to **20,000 hours when charging at 1.5 A and 125 °C**. **The thermal regulation feature reduces charge current if the IC's junction temperature reaches 125 °C; thus without a good thermal design the maximum programmed charge current may not be reached.**" | 8.1 注 2 / 8.3 注 2 |
| 热调节行为 | 超过 TJ(REG) 自动减小充电电流；若温度仍升到 TJ(OFF) → 关断输入 FET Q1、打开 Q2 让电池继续供负载；温度降 TJ(OFF-HYS) 后恢复；持续过温进入 "hiccup" 模式；**热调节期间安全定时器按电流减小比例放慢、电池终止被禁用** | 9.3.5.8 |
| 布局要点 | IN 去耦电容与 OUT 滤波电容尽量靠近芯片、走线短；小信号地与功率地单点汇合；IN/OUT 大电流路径按最大充电电流加宽 | 12.1 节 |

**工程推算（我的计算，非数据手册原文，务必自行验证）**：线性充电器功耗 `P = (VIN − VBAT) × ICHG`。若 VIN = 5.0 V、VBAT = 3.7 V、ICHG = 1.5 A → P ≈ 1.95 W；按 RθJA = 44.5 °C/W，仅结温升就约 87 °C（还没算 OUT 的 LDO 压降功耗）。**这意味着在 5 V 输入下想真正跑到 1.5 A，必须大面积铺铜/过孔阵列散热并降低环境温度，否则热调节会把电流压下来**（数据手册注 2 正是这个意思）。更现实的做法：把 ICHG 设在 0.5–1.0 A，或用 4.35–4.5 V 的输入源降低压差。

---

## 11. USB-C 受电座（USB 2.0，device/UFP，5.1 kΩ CC 下拉）

### 11.1 器件与封装

LCSC 参数（每个器件均为**一手分销商参数页**，用其 JSON API 读取）：

| 器件 | LCSC | 厂商 | 触点 | 封装/安装 | 长度 | 其他 |
|---|---|---|---|---|---|---|
| **TYPE-C-31-M-12** | [C165948](https://www.lcsc.com/product-detail/C165948.html) | Korean Hroparts Elec (HRO) | **16P** | **SMD, Surface Mount, Right Angle（卧贴，水平/顶贴）** | 7.35 mm | 20 V, −30…+80 °C, Female, 库存 221885 |
| **GT-USB-7010ASV**（你提到 "GCT"，实际厂商是 **G-Switch/品赞**） | [C2988369](https://www.lcsc.com/product-detail/C2988369.html) | G-Switch | **16P** | SMD, Right Angle | 7.35 mm | 协议标准 **USB 2.0**, Center Height **1.68 mm**, 24 V, 库存 123450 |
| **KH-TYPE-C-16P** | [C709357](https://www.lcsc.com/product-detail/C709357.html) | Kinghelm | **16P** | SMD, Right Angle | 7.81 mm | 30 V, −40…+85 °C, 库存 198575（`KH-TYPE-C-16P-T` = C709358, 7.6 mm）；厂商自家图纸是**图片版 PDF**（无法提取文字），安装数据仅到分销商级别 |
| **USB4105-xx-A**（**真正的 GCT 16P 件**，你若要 GCT 正品应选它） | — | GCT | **16P** | 图纸原文 "SMT Type, **PCB Top Mount**" | — | VBUS 5.00 A 集合 / GND 6.25 A 集合 / A5-B5 1.25 A，20 000 次；`SHELL = GND` https://gct.co/files/drawings/usb4105.pdf |

**厂商官方页面（HRO）**：`TYPE-C-31-M-12` = "8.94×7.35×3.16 mm 通用型 **16P（表面贴装式）** TYPE-C 接口"，DC 20 V **5 A**，10 000 次插拔 —— **"表面贴装式" 即 top-mount（卧贴、非沉板/mid-mount）**；HRO 的沉板 16P 是另外的 M-13/M-14/M-28 系列。来源：https://www.krhro.com/Product-Details/726.html 与 https://www.krhro.com/product/1047166038679040000-32-16.html
（HRO 自家 PDF 图纸与 krhro.com 的 PDF 直链对本环境返回 403，且 LCSC 提供的 PDF 是图片扫描件 → 尺寸/安装方式以 HRO 网页文字 + LCSC 参数 + KiCad 官方封装几何三方交叉确认，详见 §Uncertain 第 6 条。）

**KiCad 官方符号与封装（已逐一核实存在，来源：GitLab master 目录列举 + raw 文件）：**
- ✅ **原理图符号（推荐直接用这个）**：**`Connector:USB_C_Receptacle_USB2.0_16P`** — 描述 "USB 2.0-only 16P Type-C Receptacle connector"；引脚名即 A1/A4/A5/A6/A7/A8/A9/A12/B1/B4/B5/B6/B7/B8/B9/B12 + SHIELD
  https://gitlab.com/kicad/libraries/kicad-symbols/-/blob/master/Connector.kicad_symdir/USB_C_Receptacle_USB2.0_16P.kicad_sym
- ✅ **`Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12`** — https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_USB.pretty/USB_C_Receptacle_HRO_TYPE-C-31-M-12.kicad_mod
  - 描述："USB Type-C receptacle for USB 2.0 and PD"，tags `usb usb-c 2.0 pd`，属性 `attr smd`，并在 descr 中引用 HRO 原始图纸 `http://www.krhro.com/uploads/soft/180320/1-1P320120243.pdf`
  - 焊盘构成（这就是"16 pin 怎么画"的权威答案）：**16 个 SMD 焊盘，编号为 A1, A4, A5, A6, A7, A8, A9, A12, B1, B4, B5, B6, B7, B8, B9, B12**；外加 **4 个 `SH` 通孔椭圆焊盘（mechanical）** 和 **2 个 Ø0.65 mm NPTH 定位孔**（±2.89, −2.6）。
  - 触点焊盘举例：A1 (−3.25, −4.045) 0.6×1.45 mm；A4 (−2.45) 0.6×1.45；A5 (−1.25) 0.3×1.45；A6 (−0.25) 0.3×1.45（丝印外形约 ±4.7 mm 宽）
- ✅ `Connector_USB:USB_C_Receptacle_G-Switch_GT-USB-7010ASV`
- ✅ 其他同族官方封装：`USB_C_Receptacle_HCTL_HC-TYPE-C-16P-01A`、`USB_C_Receptacle_XKB_U262-16XN-4BVC11`、`USB_C_Receptacle_Palconn_UTC16-G`、`USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` 等（`Connector_USB.pretty` 共 75 个文件）
- ❌ **`KH-TYPE-C-16P`（Kinghelm）在官方库里没有同名封装** → `UNVERIFIED`（可用 `USB_C_Receptacle_HCTL_HC-TYPE-C-16P-01A` 之类的 16P 卧贴封装比对尺寸后借用，但必须自行核对焊盘位置）。
- ⚠️ **`kicad.github.io/footprints/...` 文档页与 GitLab master 不同步**（名字都不同），请以本地 KiCad 安装里的名字为准（例：开关类封装文档页写 `SW_Slide_1P2T_CK_OS102011MS2Q`，master 实为 `SW_Slide_SPDT_Straight_CK_OS102011MS2Q`）。

**top-mount 还是 mid-mount？** 这三个 16P 器件的 LCSC 安装方式一致为 "**Surface Mount, Right Angle**"（卧贴、水平贴板上表面），**不是 mid-mount（沉板/夹板）**。依据：① LCSC 参数页（上表）；② 官方 KiCad 封装的几何——全部信号焊盘在 F.Cu 顶层、外壳用 4 个通孔焊盘固定、板边不穿过连接器本体。
→ 结论：**"SMD 触点 + 通孔外壳固定脚"的混合安装、水平顶贴（right-angle / top-mount）**，这是最常用的键盘 USB-C 座形式。mid-mount 类型（如 GCT USB4105 的 MidMnt 变体）在官方库里以 `..._TopMnt_Horizontal` / `MidMnt` 明确区分。

**16P 引脚映射（所有 16P 座通用，逐脚来自 GCT 图纸 https://gct.co/files/drawings/usb4105.pdf）**：
`A1 GND · A4 VBUS · A5 CC1 · A6 Dp1 · A7 Dn1 · A8 SBU1 · A9 VBUS · A12 GND · B1 GND · B4 VBUS · B5 CC2 · B6 Dp2 · B7 Dn2 · B8 SBU2 · B9 VBUS · B12 GND` + `SHELL`
= 4×VBUS + 4×GND + CC1/CC2 + 4×USB 2.0 数据 + 2×SBU（纯 USB 2.0 应用下 SBU1/SBU2 不接）。

### 11.2 CC1/CC2 的 Rd = 5.1 kΩ 与"到底能拉多少电流"

来源：USB Type-C Spec **R2.5（March 2026）** https://usb.org/document-library/usb-type-cr-cable-and-connector-specification-release-25 ；同一批数据在 **R2.4（Oct 2024, 439 页）** 中表号与数值一致（R2.4 副本：https://community.infineon.com/gfawx74859/attachments/gfawx74859/USBEZPDTypeC/10790/1/USB%20Type-C%20Spec%20R2.4%20-%20October%202024.pdf ）。

1. **Rd 的官方值**：Table 4-28 **Sink CC Termination (Rd) Requirements** —— "**±20% resistor to GND: 5.1 kΩ, No（不能识别电源能力）, Max voltage on pin 1.32/2.18 V**"；"**±10% resistor to GND: 5.1 kΩ, Yes（可识别电源能力）, Max 2.04 V**"。即 **UFP/Sink 在 CC1 和 CC2 上各接一个 5.1 kΩ 到 GND**。
   - 规范强制两脚**各自独立**接 Rd："Both CC1 and CC2 pins shall be independently terminated to ground through Rd"（R2.4 p.180）。**绝对不要把 CC1 与 CC2 短接**（Raspberry Pi 4 的著名错误；来源为博客，**低置信度**：https://people.kernel.org/bleung/how-to-design-a-proper-usb-c-power-sink-hint-not-the-way-raspberry-pi-4 ）。
   - **想要 1.5 A / 3 A 就必须用 ±10%（即 1% 电阻）**：Microchip AN1953 p.10–11 "A **5.1 kΩ ±10%** is the only acceptable resistor if USB Type-C charging of 1.5 A @ 5 V or 3.0 A @ 5 V is to be used" http://ww1.microchip.com/downloads/en/AppNotes/00001953A.pdf
2. **源端（Source）用 Rp 广播能力**：Table 4-27 **Source CC Termination (Rp)** ——
   | 广播 | 电流源到 1.7–5.5 V | 电阻上拉到 4.75–5.5 V | 电阻上拉到 3.3 V |
   |---|---|---|---|
   | **Default USB Power** | 80 µA ±20% | **56 kΩ ±20%** | 36 kΩ ±20% |
   | **1.5 A @ 5 V** | 180 µA ±8% | **22 kΩ ±5%** | 12 kΩ ±5% |
   | **3.0 A @ 5 V** | 330 µA ±8% | **10 kΩ ±5%** | 4.7 kΩ ±5% |
3. **Sink 侧测到的电压判据**：Table 4-35（Rd 为 ±20% 时）—— `vRd-USB` = **0.277–0.612 V**；`vRd-1.5` = **0.746–1.164 V**；`vRd-3.0` = **1.369–2.042 V**；`vRd-Connected` 上限 2.181 V。
4. **Sink 允许拉多少**（4.5.2.3 各子状态）：
   - `PowerDefault.SNK`："The port shall draw **no more than the default USB power** from VBUS."（默认 USB 功率 = USB 2.0 的 **500 mA** / USB 3.2 单 lane 的 **900 mA** / USB 3.2 双 lane 的 **1500 mA**，见 Table 4-19/4-20 与 §4.6.2.1）
   - `Power1.5.SNK`："The port shall draw **no more than 1.5 A** from VBUS."（且须持续监视 vRd）
   - `Power3.0.SNK`："The port shall draw **no more than 3.0 A** from VBUS."（且须持续监视 vRd）
   - **要超过默认值，规范要求 Sink 主动监视 vRd 来判断源端广播**（4.5.2.3.1.1："If the port wants to consume more than the default USB power, it shall **monitor vRd** to determine if more current is available from the Source."）
5. **对你的设计的直接含义（重要）**：**只放两颗 5.1 kΩ、不做 CC 电压检测的设备，默认只能按 500 mA（USB 2.0 主机）来设计。**
   - 规范原话（§4.6.2.1）："The value of **Rp** establishes a voltage (vRd) on CC that is used by the Sink to determine the maximum current it may draw"；"A Sink that takes advantage of the additional current offered (e.g., 1.5 A or 3.0 A) **shall monitor the CC pins** and shall adjust its current consumption within tSinkAdj to remain within the value **advertised by the Source**."
   - 一句话：**Rd（5.1 kΩ）只是"允许被供电"的开关，真正决定能拉多少的是源端的 Rp。** 5.1 kΩ + 3 A 源 → 可拉 3 A；5.1 kΩ + 默认 USB 源 → 只能 500 mA。
   - 若你的接口是插在电脑 USB 口上充电，**ILIM 必须 ≤ 500 mA**；只有确实实现了 CC 电压检测（且源端广播 1.5 A/3 A）才可以拉更高。**这与 BQ24072 的 ILIM 设置必须一致**：`EN2=0, EN1=1`（USB500）就是与"5.1 kΩ 直连、不检测 CC"最匹配的默认设置。
   - 反过来：把 ILIM 设成 3 A 却没有 CC 检测，在默认 USB 口上会**超规范取电**（不合规，且可能把主机口拉崩）。
   - 厂商交叉核对（TI TUSB320，UFP 侧）："constantly presents pulldown resistors (Rd) on both CC pins"；其内部 Rd 可选 4.6/5.1/5.6 kΩ，默认档 500 mA(USB2.0)/900 mA(USB3.1)、1.5 A、3 A https://www.ti.com/lit/ds/symlink/tusb320.pdf

### 11.3 VBUS / GND / 外壳 / 去耦

来源：同上 USB Type-C Spec R2.5，Section 3 图注（Notes 11/14/15）与 3.4.3 图注。

| 项目 | 规定 | 出处 |
|---|---|---|
| VBUS 并联 | "**All VBUS pins shall be connected together at the USB Type-C receptacle** when it is in its mounted condition (e.g., all VBUS pins bussed together in the PCB)." → A4 / A9 / B4 / B9 全部并联 | Section 3 图注 Note 14 |
| GND 并联 | "**All Ground return pins shall be connected together** at the USB Type-C receptacle when it is in its mounted condition." → A1 / A12 / B1 / B12 全部并联 | Note 15 |
| **外壳/屏蔽** | "**The receptacle shell shall be connected to the PCB ground plane.**"（这是条文要求，直接接 PCB 地，不是"经电容/电阻"；Note 11）另：若座子有内部 EMC 屏蔽焊盘，应连到外壳；无外壳时要提供连地的手段 | Note 11 与 Section 3.2.2.3 引用 |
| VBUS 去耦（**座子/设备侧**） | 规范里出现的 "**A 10 nF bypass capacitor (minimum recommended…)**" 是给**线缆插头**（cable plug）用的，**不是**给板上受电座的强制要求 | 3.4.3 各表图注 Note 4 |
| VBUS 去耦（设备侧实际做法） | 由充电 IC 数据手册决定：**BQ24072 的 IN 端 1–10 µF（且 < 10 µF 以满足 USB-IF inrush）**；TI TUSB320 Table 8-2 也给出 UFP 侧 bulk 电容 **1–10 µF**（DFP 侧 ≥120 µF）https://www.ti.com/lit/ds/symlink/tusb320.pdf | SLUS810N Table 7-1 / 9.3.4.1；TUSB320 §8.2 |
| 挂上之前的 VBUS 电容上限 | 规范 Table 4-3：receptacle 在未进入 Attached.SNK 前 VBUS–GND 电容 **10 µF**（DRP 10 µF / 纯源 3000 µF，Table 4-2） | R2.5/R2.4 Table 4-3 |
| 0.1 µF HF bypass | 属通行工程做法；**未**在上述一手来源中找到强制条文 → 见 §Uncertain | — |
| CC 脚保护 | CC 在连接器上是 0–5.5 V 级信号；本设计只需 5.1 kΩ 到 GND。SBU1/SBU2（A8/B8）在纯 USB 2.0 应用中**悬空不接** | 由封装焊盘名与 UFP 用法确定；SBU 未使用属常规做法（**此条为工程惯例，非规范强制** → 见 §13） |

**接线速查（16P 座 → 电路）：** `A4/A9/B4/B9` → VBUS（并联）→ BQ24072 `IN` + 1 µF；`A1/A12/B1/B12` → GND（并联）；`A5` → 5.1 kΩ → GND；`B5` → 5.1 kΩ → GND；`A6/B6` → USB D+；`A7/B7` → USB D−；`A8/B8` → NC；`SH`×4 → GND（多点接地、就近打孔）。

---

## 12. SPDT 滑动开关（用于电池硬切断）

> 本节数据经独立核实，一手来源为厂商数据手册（见每行链接），已下载并提取文本；完整报告见 `research/spdt-slide-switch-battery-cutoff-facts.md`。

**⚠️ 重要更正：常见候选清单里有 2 个只有 50–100 mA，根本不能切断 2–3 A 的 LiPo 回路。**

| 器件 | DC 额定 | 安装/操作 | 脚位 | 本体 L×W×H (mm) | 能过 2–3 A? | KiCad 符号 | KiCad 官方封装 |
|---|---|---|---|---|---|---|---|
| **C&K 1101M2S3CQE2** | **6 A @ 28 V DC**（另 6 A @125 VAC / 3 A @250 VAC；Q 银触点） | THT，顶面拨动 | 3，SPDT On-None-On | 12.70 × 6.60 × 6.35，拨柄 +5.08（总高≈11.43） | ✅ **是**（3 A 有 2× 余量） | `Switch:SW_SPDT` | ❌ **官方无封装，需自绘**（端子间距 4.70 mm，端子 1.27×0.76 mm） |
| **C&K OS102011MS2QN1** | **0.1 A @ 12 V DC** | THT，顶面拨动 | 3，SPDT（BBM） | 本体 8.60 × 4.30，框高 4.70 | ❌ **否**（差 20–30 倍） | `Switch:SW_SPDT` | ✅ `Button_Switch_THT:SW_Slide_SPDT_Straight_CK_OS102011MS2Q` |
| **SHOU HAN MSK12C02**（= MSK-12C02） | **50 mA @ 12 V DC**（厂商规格书 §2.5） | **SMD 卧式（侧拨）** | 3 信号焊盘（SPDT） | 8 × 2.8 × 1.4（LCSC 参数 C431540） | ❌ **否**（差 40–60 倍；3 A 时 ≤100 mΩ 触点要耗散约 0.9 W） | `Switch:SW_SPDT` | ✅ `Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02` |
| SS12D00G3（通用型号，无单一厂商） | 3 A 250 VAC 或 28 VDC（**单一小厂页面，低置信度**） | THT 立式 | 3，1P2T | `UNVERIFIED`（拿不到图纸） | ⚠️ 纸面刚好，零余量 | `Switch:SW_SPDT` | ❌ 官方库无（`Button_Switch_SMD` 173 个 + `Button_Switch_THT` 113 个文件全查过） |

- 一手来源：C&K 1000 系列 https://www.ckswitches.com/media/1429/1000.pdf ；C&K OS 系列 https://www.ckswitches.com/media/1428/os.pdf ；SHOU HAN MSK12C02 规格书（LCSC 托管）https://datasheet.lcsc.com/datasheet/pdf/5162155576bfd231c35aa9a893d25c8c.pdf ；LCSC 参数 C431540（`https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=C431540`，本报告已独立复核其 `Current Rating = 50mA`、`Mounting Type = Surface Mount, Right Angle`）。
- **DC 与 AC 额定不可互推**：AC 每周期有 100–120 次过零灭弧，DC 没有。C&K 1000 系列就是"6 A @125 VAC 但只有 6 A @28 VDC"的典型例子。3.7–4.2 V DC 下电弧能量很低，因此**只要有明确 ≥3 A 的 28 VDC 额定**就很宽裕。
- **设计建议**：要真断 2–3 A 就用 **C&K 1101M2S3CQE2**（THT，需自绘封装，19 周货期，约 €3.4）；若坚持用 MSK12C02（已有官方封装、便宜、SMD），**只能把它当"信号"用** —— 由它去驱动一个 PMOS/负载开关，让 MOSFET 真正切断电池电流。
- **警告**：不要以为"MSK-12C02"是一个统一规格 —— 另有厂商（Switech）的 `MSK-12C02SW-NB-JC` 标 0.1 A，两者都远低于 2 A。

---

## 13. PMOS 负载开关（RGB 电源门控，ZMK ext-power）

> 本节数据来自厂商原始 PDF（本地下载 + 文本提取），并与本报告作者独立提取的 AO3401A 数据逐项对照一致。
> 一手来源：**S1** AO3401A（AOS, Rev 3.1 Dec 2023）https://aosmd.com/res/data_sheets/AO3401A.pdf ；**S2** DMG2301L（Diodes）https://www.diodes.com/assets/Datasheets/DMG2301L.pdf ；**S3** IRLML6402（Infineon/IR）https://www.infineon.com/dgdl/irlml6402pbf.pdf ；**S6** Digi-Key 状态页；**S7–S11** ZMK/开源键盘实际设计（见文末）。

### 13.1 推荐型号：**AO3401A**（SOT-23）

| 参数 | AO3401A | DMG2301L | IRLML6402 |
|---|---|---|---|
| VDS max | **−30 V** | −20 V | −20 V |
| VGS max | ±12 V | ±8 V | ±12 V |
| **VGS(th)** | **−0.5 / −0.9 / −1.3 V** @ VDS=VGS, ID=−250 µA | −0.4 (min) … −1.2 (max) V | −0.40 / −0.55 / −1.2 V |
| **RDS(on) max @ VGS = −4.5 V** | **60 mΩ**（typ 47）@ ID=−3.5 A | 120 mΩ @ ID=−2.8 A | 65 mΩ @ ID=−3.7 A |
| **RDS(on) max @ VGS = −2.5 V** | **85 mΩ**（typ 60）@ ID=−2.5 A | 150 mΩ @ ID=−2.0 A | 135 mΩ @ ID=−3.1 A |
| RDS(on) @ −10 V | 50 mΩ max（typ 41）@ ID=−4.0 A | — | — |
| **ID 连续** | **−4.0 A @ TA=25 °C；−3.2 A @ TA=70 °C**（t ≤ 10 s） | −3 A @ 25 °C 但**仅 −1 A @ 70 °C** | −3.7 A @ 25 °C；−2.2 A @ 70 °C |
| IDM 脉冲 | −27 A | −10 A | — |
| PD / RθJA | 1.4 W（t≤10 s）/ 0.9 W（稳态）；RθJA 70 typ / 90 max（t≤10 s）、**100 typ / 125 max（稳态）** °C/W | 1.5 W；RθJA 83 °C/W | — |
| 封装 | **SOT-23** | SOT-23 | Micro3/SOT-23 |
| 供货状态 | Active（Digi-Key） | Active | ⚠️ **Digi-Key Part Status = Obsolete** |
| 结论 | ✅ **推荐** | 可用但 RDS(on) 高 2 倍、70 °C 下 ID 只有 1 A | 参数不错但已停产 |

⚠️ **不要在分销商参数页抄 MOSFET 数字**：Digi-Key 把 AO3401A 写成 "44 mΩ @ 4.3 A, 10 V"、Ciss 1200 pF，而厂商数据手册是 50 mΩ @ ID=−4.0 A、Ciss 645 pF。**以厂商 PDF 为准。**

### 13.2 栅极驱动数学（Source 接 VBAT 3.7–4.2 V，负载接 Drain，GPIO 3.3 V）

`Vgs = Vgate − Vsource`：

| VBAT（Source） | GPIO = 3.3 V（HIGH） | GPIO = 0 V（LOW） |
|---|---|---|
| 4.2 V（满电） | **Vgs = −0.9 V** | **Vgs = −4.2 V** |
| 3.7 V（标称） | **Vgs = −0.4 V** | **Vgs = −3.7 V** |
| 3.0 V（快没电） | **Vgs = +0.3 V** | **Vgs = −3.0 V** |

**导通（GPIO 拉低）**：Vgs = −3.0…−4.2 V，远大于 |VGS(th)|max = 1.3 V，**沟道完全反型，能正常导通**。但注意数据手册只保证 −2.5 V 与 −4.5 V 两个点：在 −3.0…−4.2 V 区间，RDS(on) **没有规格值**，只能被 60 mΩ（−4.5 V）与 85 mΩ（−2.5 V）夹住 → **最坏要按 85 mΩ 预算，即比海报上的 60 mΩ 差最多 +42%**。

**关断（GPIO 输出 3.3 V）**：**不能保证关断。** VBAT = 4.2 V 时 |Vgs| = 0.9 V，已经**超过 AO3401A 的 VGS(th) 最小值 0.5 V** —— 最坏情况下（低阈值的那颗）栅压比阈值还高 0.4 V，器件会导通（亚阈值/弱反型）。只有 VBAT ≤ 3.7 V（0.4 V < 0.5 V）才谈得上安全。DMG2301L（−0.4 V min）与 IRLML6402（−0.40 V min）更差。
（**泄漏电流的大小未在数据手册中规定 → UNVERIFIED**；能确定的只是"关断不再有保证"。）

**结论 —— 需不需要 level shifter / 第二级 NPN/NMOS？**
- **要"导通"不需要**：3.3 V GPIO 已经把 Vgs 拉到 −3.0…−4.2 V，代价最多是 RDS(on) 从 60 mΩ 变 85 mΩ。
- **要"保证关断"则需要**（或换拓扑）：3.3 V 的栅极**永远到不了 4.2 V 的源极**。
  - ⚠️ **"栅源之间加一个上拉电阻"不能解决这个问题** —— GPIO 主动输出 3.3 V 时，上拉电阻被 GPIO 拉死，栅极仍是 3.3 V，Vgs 仍是 −0.9 V。上拉（10 k–100 kΩ）**只能**解决"MCU 复位/未上电时 GPIO 高阻"的悬空问题（此时 Vgs = 0 → 硬关断）。
  - 真正可靠的做法：**加一级反相驱动**（NPN 或 NMOS：GPIO → 基极/栅极，集电极/漏极接 PMOS 栅极，PMOS 栅极到 Source 之间加 10 k–100 kΩ 上拉）。这样 GPIO 高 = 三极管导通 = PMOS 栅极被拉到 ≈0 V = Vgs ≈ −4.2 V（开）；GPIO 低/高阻 = 上拉把栅极拉到 VBAT = Vgs = 0（**硬关断**）。逻辑整体不反相。
  - 或者**不在电池轨上做门控**：像 **nice!nano v2 那样去控制 LDO 的 EN 引脚**（见 13.4），从根本上回避 Vgs 余量问题。
  - 若坚持直驱且接受风险：把 **GPIO 配成 open-drain**（只输出低、关断时高阻）配合栅源上拉，也能得到硬关断 —— 但 ZMK 默认驱动并非如此（见 13.4）。

**体二极管方向（画错就废）**：PMOS 的体二极管 **阳极在 Drain、阴极在 Source**，只有 V_drain > V_source 时才导通。因此必须 **VBAT → Source，负载 → Drain**：关断时体二极管反偏，负载轨真正断电。
**接反（负载接 Source、VBAT 接 Drain）→ 体二极管永远正偏 → 负载永远带电，"开关"失效。**（AO3401A 数据手册规格化了该二极管：IS = −2 A，VSD = −1 V max @ IS = −1 A。）

### 13.3 用 AO3401A 跑 2 A 是否合适

`P = I² × RDS(on)`：2 A 时 **0.24 W**（按 60 mΩ）/ **0.34 W**（按 85 mΩ）。
按稳态 RθJA = 125 °C/W 上限：**ΔT ≈ +30 °C / +43 °C** → TA = 25 °C 时 TJ ≈ 55 / 68 °C；TA = 40 °C 时 TJ ≈ 70 / 83 °C，仍远低于 TJ(max) = 150 °C，也低于 2 A < ID(−4 A @25 °C / −3.2 A @70 °C) 的电流额定。
压降：0.12–0.17 V（3.7 V 轨的 3.2–4.6%）——**对 RGB LED 的亮度/颜色一致性有影响，要算进预算**。
功耗预算：数据手册 1.4 W 是 "t ≤ 10 s" 数字，**真正的连续预算是 (150 − TA)/125 ≈ 1.0 W @ TA=25 °C**；0.24–0.34 W 只占 24–34% —— **结论：纸面上 2 A 可用，但请按 85 mΩ 而不是 60 mΩ 预算；若要长期稳定 2 A，建议换更大封装/更低 RDS(on) 的器件。**

### 13.4 ZMK `ext-power` 实测细节（一手来源：ZMK 源码 + 开源键盘设计）

- ZMK 驱动 **总是** 用 `gpio_pin_set_dt(gpio, 1)` 打开，初始化为 `GPIO_OUTPUT_INACTIVE`，然后默认开启（https://raw.githubusercontent.com/zmkfirmware/zmk/main/app/src/ext_power_generic.c ）。
- **极性由 devicetree 决定，而且同一引脚在 nice!nano 两代之间是相反的**：
  - nice!nano **v1**：`control-gpios = <&gpio0 13 GPIO_ACTIVE_LOW>`
  - nice!nano **v2**：`control-gpios = <&gpio0 13 GPIO_ACTIVE_HIGH>; init-delay-ms = <50>;`
  - nRFMicro：`control-gpios = <&gpio1 9 GPIO_ACTIVE_LOW>; init-delay-ms = <50>;`
  （来源：ZMK `docs/docs/config/power.md` 与上述各板 overlay）
- **nRFMicro 的真实拓扑**（已逐网核对 `nrfmicro.kicad_sch`）：`P1.09` → 网络 `POWER_PIN` → PMOS（**AO3407**）栅极；**Source 接 nRF_VDD（3.3 V LDO 轨，不是电池轨）**；Drain = `EXT_VCC`；另有 **R9 = 2 MΩ 栅极→GND 下拉**（默认开）。→ **nRFMicro 不是"Source 接电池"的情形**；它因为 Source 只有 3.3 V，直驱毫无问题。
- **nice!nano v1 是"Source 接电池轨"的案例**：PMOS **Q1（P-Channel）**，**Source = `VBAT`**，**Drain → LDO（AP2112K-3.3）的 VIN**，栅极由 **`VBUS`(5 V) 节点**驱动，并带 **R1 = 100 kΩ 到 GND** 与肖特基 **D1**。它的 Vgs(on) = −VBAT、Vgs(off) = +0.8 V，**因此从不面对"3.3 V GPIO vs 4.2 V 电池"的问题**。
- **nice!nano v2 干脆不用 PMOS**：`EXT_VCC` 是 **XC6220B331MR** LDO 的 VOUT（VIN = `VDDH`），`POWER_PIN` 经 **10 MΩ 上拉到 VIN** 去驱动该 LDO 的 **CE** 引脚。
- ⚠️ 因此在"Source = 3.7–4.2 V 电池轨 + 3.3 V GPIO 直驱"这个具体组合下，**没有找到一个可直接抄的开源键盘先例** → 见 §Uncertain。
- ⚠️ nice!nano 原理图里 PMOS 的具体型号在公开分辨率下不可辨认 → `UNVERIFIED`。
- **固件极性怎么写**：ZMK 的 `GPIO_ACTIVE_LOW/HIGH` 只决定物理电平，驱动内部一律用逻辑 1 使能。→ **直驱 PMOS（或上拉的 LDO EN）用 `GPIO_ACTIVE_LOW`；若加了反相级（NPN/NMOS）则用 `GPIO_ACTIVE_HIGH`**；建议同时加 `init-delay-ms`（nice!nano v2 / nRFMicro 都用 50）。

---

## Uncertain / Could Not Verify

1. **RGT0016B vs RGT0016C**：SLUS810N 自身矛盾（Figure 7-1/7-2 标 BQ24072 = RGT0016B，Table 6-1 标 BQ24072 = RGT0016C）。两者的物理差异未在任何一手来源中说明。可确定的是：订货号 `BQ24072RGTT/RGTR` = **VQFN (RGT) 16 pin**，KiCad 官方符号关联 `Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm`。**UNVERIFIED**：RGT0016B/C 是否对应不同的散热焊盘尺寸。
2. **§9 中 Figure 10-1 的 refdes↔元件值对应关系**（C1/C2/C3 分别接 IN/OUT/BAT，R1/R2/R3/R4/R5 分别是哪个）未能 100% 确认——PDF 文本提取打乱了图内文字顺序。已确认的是**元件值的集合**（R: 1.13 k/1.18 k/46.4 k/1.5 k/1.5 k；C: 1 µF/4.7 µF/4.7 µF）与各引脚的允许范围。
3. **ILIM 悬空的确切后果存在文档措辞冲突**：Table 7-1 说 "Leaving ILIM unconnected disables all charging"，而 EN1/EN2 表允许用 USB100/USB500 固定档（此时按定义限流不来自 ILIM）。数据手册**没有**说明 "ILIM, ISET SHORT-CIRCUIT DETECTION (CHECKED DURING STARTUP)" 是否在 USB100/USB500 模式下也执行。**UNVERIFIED** → 结论：**总是放一颗 ILIM 电阻**（例如 USB500 场景放 1.6 kΩ ≈ 1 A 上限，不会与 500 mA 档冲突）。
4. **TS 阈值在旧修订版中是 VIN 百分比的说法**：本报告采用当前版 SLUS810N 的**绝对电压**（VHOT 300 mV / VCOLD 2100 mV）。在 2009 年的旧版（alldatasheet 上的 39 页版本）中，同一张表也是 mV 单位；但我**没有**逐版比对历史修订，**若你打算引用旧版本文档，请重新核对**。
5. **KH-TYPE-C-16P 的 KiCad 官方封装**：官方库中没有该型号同名封装（只找到 HCTL HC-TYPE-C-16P-01A 等近似件）。**UNVERIFIED**。
6. **TYPE-C-31-M-12 的机械图纸未能直接读到**：HRO 官网 PDF 直链（krhro.com）对本环境返回 403，LCSC 提供的 PDF 是**纯图片扫描件**（文本提取仅 31 字符）。安装方式/尺寸依据三方交叉：HRO 官方网页文字（"16P（**表面贴装式**）"，8.94×7.35×3.16 mm，且其沉板 16P 是独立的 M-13/M-14/M-28 系列）+ LCSC 参数页（16P / SMD / Surface Mount, Right Angle / 7.35 mm）+ KiCad 官方封装焊盘几何（信号焊盘全在顶层、外壳为 4 个通孔脚）。→「**top-mount 卧贴，非 mid-mount**」置信度**较高**，但**投板前仍建议索取厂商 DXF/图纸核对**。
7. **SBU1/SBU2 悬空**：属常规工程做法，但我**没有**在 Type-C 规范中找到"未使用 SBU 可以悬空"的强制条文。**UNVERIFIED（惯例层面）**。
8. **`GT-USB-7010ASV` 的厂商**：你写的是 GCT，但 LCSC/EasyEDA 参数显示厂商为 **G-Switch（品赞）**，且厂商标注协议标准为 USB 2.0。若要"GCT 正品"，对应型号应是 GCT 的 USB4105 系列（官方库有 `USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`）。**需你确认要买哪一个**。
9. **滑动开关 SS12D00G3 的全部数据**（额定、尺寸）：只有单一小厂营销页，无厂商图纸，**低置信度**；C&K 品牌的 `SS-12D00-G 6 E` 在 Digi-Key 已 Obsolete。**UNVERIFIED**。
10. **MSK12C02 的引脚结构冲突**：SHOU HAN 规格书 §2.4 写 "1 pole, 1 throw"，而 LCSC 参数与 KiCad 官方封装都是 SPDT 三焊盘（该规格书疑似套用了轻触开关模板，§1.1 竟写 "TACTILE SWITCH"）。50 mA 额定不受此影响。
11. **本报告未核实的项目**：USB-IF 认证/合规测试要求、PD 协商（本设计不需要，纯 5 V 受电即可）、电池保护板（PCM）规格、以及任何与 ZMK 固件层面的实现细节（除 §13.4 已列出的源码事实）。
12. **PMOS 关断状态的漏电流大小**：AO3401A / DMG2301L / IRLML6402 的数据手册**都没有规定** |Vgs| = 0.4–0.9 V 区间的漏电流。已核实的只是"**关断不再有保证**"这一定性结论；若你的 RGB 灯珠在关断后会微亮，需要实测。**UNVERIFIED**。
13. **"栅源上拉电阻"作为键盘设计惯例及其典型值**：**未找到任何使用它的开源键盘设计**。实测到的同类元件是：nRFMicro 2 MΩ 栅极→GND（下拉）、nice!nano v2 10 MΩ CE→VIN、nice!nano v1 100 kΩ→GND（那是 USB 检测下拉，不是栅源上拉）。因此本报告只把它作为**电路原理上正确**的建议，而非"业界惯例"。**UNVERIFIED（惯例层面）**。
14. **nice!nano 原理图中的 PMOS 型号**：公开分辨率的原理图 PNG 上不可辨认 → **UNVERIFIED**。
15. **分销商参数与厂商数据手册不一致**：Digi-Key 把 AO3401A 标为 "44 mΩ @ 4.3 A, 10 V"、Ciss 1200 pF，而厂商 PDF 为 50 mΩ @ ID = −4.0 A、Ciss 645 pF。**两者冲突未解决，一律以厂商 PDF 为准。**
