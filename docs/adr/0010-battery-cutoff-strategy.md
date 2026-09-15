# P7：电池物理断电方案

**状态：🟢 已决定（用户）—— 方案已定，实现细节待定**
**日期：2026-09**
**关联：ADR-0002（BQ24072 充电）、ADR-0009（三档模式开关，本 ADR 复用它兼作电源开关）**

> 用户决定：**不设独立电池开关，用三档拨片的「有线」档兼作电源开关。**
> 待定项：`DP3T` 料号（方式 1）或方式 2 隐患的规避与实测。

## 问题

需要给键盘一个「关断电池」的手段（日常关闭 + 长期存放）。难点在于**开关装在哪**：

- 若串在**电池主回路**，它必须承载整机电流。95 颗 LED 按厂家建议 70% 灰阶约 **2.4 A**，
  理论满亮 **3.4 A**（`docs/power-architecture.md` §5.2）。
- 而常见微型贴片拨动开关 **`MSK12C02`** 的额定是 **12 V DC / 50 mA**
  （原厂规格书 §2.5 原文 "Ratings: 12V DC, 50mA (effective value)"，**已核实**）
  ⇒ **超额定 48 倍**。

`BQ24072` **没有 `SYSOFF` 引脚**（pin 15 是 `TD`），所以无法用芯片断开电池 —— 这是 P7 存在的原因。

## 社区实证（全部网表级核实）

| 做法 | 实例数量 | 说明 |
| --- | --- | --- |
| **小开关直接串电池路径**（超额定使用） | **12+ 块板** | TOTEM、KOMETA、ZMK 硬件设计指南、Ladniy/TK44、yumagulovrn/dao-choc-ble、KLOR、KLOTZ、uninarf、chocopi、ergonautkb/one、chitin、Sweep Bling LP、taira |
| **开关切 `BQ24075` 的 `SYSOFF`**（开关只走 µA） | **3 个独立实现** | ZMK 硬件设计指南、**kurtis-lew/Conejo**、**ebastler/osprey** |
| **P-FET 串电池主回路 + 小开关驱动栅极** | **0** | 核验到的电池侧 P-FET 栅极一律由 USB VBUS、MCU GPIO 或经 N-FET 驱动，**没有一个由拨动开关驱动** |
| **集成负载开关 IC**（TPS22910 之类） | **0** | 30+ 仓库范围内未发现 |

### 关键量化事实

| 项 | 数值 | 来源 |
| --- | --- | --- |
| `MSK12C02` 额定 | 12 V DC / **50 mA**（有效值）；寿命 20000 次 | 原厂规格书（深圳首韩，rev A/0 2015-03-26） |
| `BQ24075` 睡眠时 BAT 脚电流 `IBAT(PDWN)` | **4.3 µA 典型 / 6.5 µA 最大** | TI SLUS810N |
| **SYSOFF 断开后的 BAT 漏电专门指标** | **数据手册中不存在** | TI SLUS810N（"10 µA" 是 §9.4.1 的举例叙述，**不是规格**） |
| SYSOFF 内部上拉 | 约 5 MΩ（悬空约 0.84 µA） | TI SLUS810N |
| **`SYSOFF` 输入阈值** | **`V_IL` 最大 0.4 V；`V_IH` 最小 1.4 V / 最大 6 V；绝对最大 −0.3…7 V** | TI SLUS810N ⇒ **3.3 V 逻辑可直驱，无需电平转换** |
| `SYSOFF` 拉高时 `/CHG` 的行为 | *"The `/CHG` output remains low when SYSOFF is high."* | TI SLUS810N §9.3.5.5 |
| ⚠️ 反向发现 | **nice!nano v2 用 BQ24075，却把 SYSOFF 硬接 GND**，断电改走门控 LDO 的 CE | 官方原理图 |
| ✅ TI 官方应用笔记 | **SLUAA18**《Achieving Ship Mode With the BQ24075/76/78/79》（2021-11），专讲本问题 | TI；datasheet 图 10-13 亦题名 *"Using BQ24075 or BQ24079 to **Disconnect the Battery From the System**"* |

#### ✅ 更正：`SYSOFF` 上并不存在「两股力量打架」

我此前把「100 kΩ 上拉 vs NMOS 下拉」描述成需要解决的冲突。**这是错的**：

- 100 kΩ 是**无源上拉**，NMOS 是**无源下拉** —— 二者构成**分压器**，不是两个源在对顶。
- `V(SYSOFF) = 4.2 V × Rds(on) / (100 kΩ + Rds(on)) ≈` **84 µV**，
  **比 `V_IL(max) = 0.4 V` 还低约 5000 倍** ⇒ NMOS 导通时 `SYSOFF` 稳稳定为低。
- 漏电 ≈ 42 µA（经 100 kΩ）+ 0.84 µA（经内部 5 MΩ）⇒ 等效约 98 kΩ。

#### 🔴 由此推出一条硬约束：`2N7002` 那颗「插 USB 强制拉低」的管子是**必须的，不是可选**

TI 原话（SLUAA18）：*"When VIN is plugged in, the system is powered and **SYSOFF can be pulled low
using the GPIO to keep the battery connected to the output for charging**."*

⇒ **没有它，「关机档 + 插着 USB」会静默地永远充不进电**，而用户看到的只是「插了线但不充电」。
这正是参考设计里那颗 `2N7002` 的唯一职责。**TI 用整篇应用笔记讲这件事。**

#### ⚠️ 极性脚注（反直觉，容易接反）

`SYSOFF` **高 = ship mode / 断开电池 / 同时禁用充电** —— 与「开关拨到 ON 应该是高」的直觉相反。

#### 社区实现远不止 3 个

用 `gh search code "SYSOFF" --extension kicad_sch` 扫到 **25+ 个项目**，其中键盘相关的包括：
`zhiayang/mikoto`（全局标签 `CHARGE_CTRL_1/2`，逻辑电平充电控制）、
`jncronin/gk`（`PWRCTRL1..3`、`PWR_WKUP1`）、
`crides/fissure`（用 **`AO3400A`** 而非 `2N7002`，同拓扑不同件）、
`ebastler/osprey`、`PumaFPV/PMK`、`rianadon/Cosmos-Keyboard-PCBs`、
`kurtis-lew/Conejo`、`JonasLindinger/MicroPad`、`Spaceboards/SpaceboardsHardware` 等。

⚠️ **未发现**任何项目在 MOSFET 漏极串电阻、加二极管、或采用其它冲突消解拓扑；
**也未发现**任何「振荡/电平不定」的失效记录 ⇒ 该拓扑本身是稳的。

## 各方案评估

> 下文四个方案中，**方案甲（`&soft_off`）与方案丙（6 A 机械开关）未被采纳**；
> 最终决策基于**方案乙的 `SYSOFF` 机制**，但把开关**与 ADR-0009 的模式开关合并**（见上文决策）。
> 方案丁（自建 P-FET 负载开关）因零先例被否决。

### 甲：不加电池开关，改用 ZMK `&soft_off` + 存放时拔 JST

- ZMK 官方把 soft-off 定义为 *"an alternative to using a hardware switch to physically cut power"*，
  功耗 *"comparable to the deep sleep state"*；**也明确说了** *"Power is **not** technically removed from the entire system"*。
- **零硬件成本、零超额定问题**；代价是「关机」后仍有约 20 µA 级漏电，且**不是电气断开**。
- 长期存放靠拔 JST 插头（DIY 键盘的常规做法）。

### 乙：换 `BQ24075` + 小开关切 `SYSOFF` ✅ **推荐**

- **封装完全相同**（`VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm`，pin 15 = `SYSOFF`）⇒ **drop-in 替换，PCB 不动**。
- 开关只走 **≈42 µA**（4.2 V / 100 kΩ），对 50 mA 额定余量 **约 1000 倍**。
- 标准接线（三份实现一致）：
  ```
  SPDT 公共端 → SYSOFF
    一档 → GND            （开机）
    另一档 → 100 kΩ → VBAT（关机）
  Q = 2N7002 (NMOS)：D→SYSOFF，S→GND，栅极经 100 Ω 接 USB +5V，10 kΩ 下拉
    ⇒ 插入 USB 时强制拉低 SYSOFF，否则「关机档」下插电也充不进电
  ```
- **残留漏电 4.3 µA 在实用上等同于断开**：3000 mAh ÷ 4.3 µA ≈ **82 年**。
  ⇒ 「不是电气隔离」这一点对**存放**目的而言无关紧要；
  真正的差别只在**维修安全**（电池仍与充电 IC 相连）与**文档诚实性**上。
- **代价**：需补一颗 `2N7002`；`SYSOFF` 拉高会同时禁用充电（须靠 `2N7002` 解决）；
  换型号后需复核 `BQ24075` 的 `EN1/EN2` 限流取值。

### 丙：保留 `BQ24072` + 6 A 机械开关串电池路径

- **唯一能真正电气断开**的方案。`C&K 1101M2S3CQE2`（**6 A @ 28 VDC**）。
- 代价：12.70 × 6.60 × 6.35 mm、穿孔插件（THT）、**无官方 KiCad 封装需自制**、占用面板面积。

### 丁：自建 P-FET 负载开关串电池路径

- 可行且理论优雅，但**零键盘先例**（30+ 仓库确认），且需自己算 `Rds(on)`、栅极驱动与体二极管方向。
- 对「新手可复刻」目标不利。**不推荐。**

## 决策（用户决定）：有线档兼作电源开关

**不设独立的电池开关。** 三档拨片开关的**「有线」档同时切断电池**：

| 档位 | 模式（刀 A） | 电池（`SYSOFF`） | 插着 USB | 拔掉 USB |
| --- | --- | --- | --- | --- |
| **有线** | `&out OUT_USB` | **拉高 → 断开** | 有线键盘 + 充电 | **整机断电 = 关机** |
| 2.4G | `OUT_BLE` + `BT_SEL 1` | 拉低 → 接通 | 电池 + 充电 | 电池供电，走 Dongle |
| 蓝牙 | `OUT_BLE` + `BT_SEL 0` | 拉低 → 接通 | 电池 + 充电 | 电池供电，直连主机 |

⇒ **「拨到有线档」即为关机。**

**前提**：充电 IC 由 `BQ24072` **换成 `BQ24075`**
（两者**封装完全相同** `VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm`，pin 15 由 `TD` 变为 `SYSOFF`
⇒ **drop-in 替换，PCB 布局不动**）。`BQ24072` 没有 `SYSOFF`，做不到本决策。

这个组合能成立，靠的是参考设计里那颗 `2N7002` 的固有行为：
`SYSOFF` 拉高会**同时禁用充电**，而 `2N7002` 在**插入 USB 时强制把 `SYSOFF` 拉低** ⇒
插上线就能充、能当有线键盘用；**拔掉线才真正断电**。

**收益**：只需要**一个**开关（ADR-0009 的模式开关），不占额外面板面积，
且用户心智模型简单 —— 「有线档 = 关机」。

### 实现方式（方式 1 已找到可用料号）

**方式 1：`DP3T`（双刀三档）** —— 刀 A 走模式、刀 B 切 `SYSOFF`

- 刀 B：公共端 → `SYSOFF`；有线档 → 经 100 kΩ → `VBAT`（断开）；另两档 → `GND`（接通）。
- ✅ **纯机械触点，无歧义、无漏电路径**，最稳。
- ✅ **料号已核实存在且可买**：

  | 候选 | 规格 | 采购 |
  | --- | --- | --- |
  | **SHOU HAN `MST23D19G2`** ✅ **首选** | 2 刀 3 档（8 脚 = 2 公共 + 6 掷），SMD 立贴，**12.95 × 3.55 × 3.5 mm**，100 mA @ 12 V，10000 次，−25…+70 °C | **LCSC C431545**，常规在库、带 `SMT扩展库` 标签 ⇒ **可直接进 JLC 贴片 BOM** |
  | Alps Alpine `SSSS224500` | 2 刀 3 档，回流焊 SMD，13.0 × 3.5 × 3.5 mm，0.3 A @ 6 V，10000 次，−40…+85 °C | LCSC C470522，但**无报价/库存阶梯**，Alps MOQ 1400/5600 ⇒ 视为订货件 |
  | C&K `AYZ0203AGRLC` | DP3T，ON-ON-ON，SMD 鸥翼，0.1 A 12 V | Digi-Key 401-2015-1、Farnell 2319975；**LCSC 无货**；尺寸未核实 |
  | G-Switch `SS-23D07-G040` | THT，12.7 × 7 × 8.7 mm，300 mA 50 V | LCSC C54305659 |

- ⚠️ **尺寸代价（不是 drop-in）**：SMD `DP3T` 约 **13.0 × 3.5 × 3.5 mm**，
  而常见 `MSK12C02` 的实际本体是 **8 × 2.8 × 1.4 mm**
  （**更正**：不是「约 3.0 × 1.5 mm」——那 1.5 mm 是**手柄高度**，LCSC 商品页写明）。
  ⇒ **长约 +5 mm、高约 +2.1 mm**，面板开孔与 PCB 占位都需相应调整。
- ⚠️ **必须自己画封装**：**官方 KiCad 库中没有任何 DP3T/2P3T 封装**
  （已用 GitLab API 枚举 `Button_Switch_SMD.pretty` 与 `Button_Switch_THT.pretty` 确认；
  仅有的多档滑动开关封装是 `SW_SP3T_PCM13`、`SW_Slide_SP3T_Straight_CK_OS103012MU1QP1`、
  `SW_Slide-03_Wuerth-WS-SLTV`）。
  ⚠️ **陷阱**：KiCad **有** `Switch:SW_DP3T` **符号**，但那只是符号不是封装 ——
  社区里确有项目引用了该符号却挂了 **DPDT** 的 land pattern。
  可复用社区封装：`HalfSweet/Kicad_Lib` → `My Switch.pretty/SW-SMD_MST23D19G2.kicad_mod`。

**方式 2：`SP3T` + 一颗 NMOS** —— 用「有线」档的 GPIO 节点去驱动 `SYSOFF`

- 原理（**已从 ZMK 驱动源码核实**，`app/module/drivers/kscan/kscan_gpio_direct.c`）：
  ```c
  static gpio_flags_t kscan_gpio_get_extra_flags(const struct gpio_dt_spec *gpio, bool active) {
      if (!active) {
          return ((BIT(0) & gpio->dt_flags) ? GPIO_PULL_UP : GPIO_PULL_DOWN);
      }
      return 0;   /* 选中的那档【不加任何内部上下拉】 */
  }
  ```
  `BIT(0)` 即 `GPIO_ACTIVE_LOW` ⇒ 在本项目配置下：
  **选中的档**（有线）不加内部上下拉，由开关公共端**硬接到 GND** ⇒ 节点 **0 V**；
  **未选中的档** 被 `GPIO_PULL_UP` 拉到 **3.3 V**。

- ✅ **更正：不需要 PNP/PMOS，一颗 NMOS 就够。**
  我此前写的隐患（`Veb = 0.9 V` 使 PNP 误导通）**是用错器件造成的**。
  改用 NMOS 后：栅极 = 该节点，源极 = GND，漏极 = `SYSOFF`（带 100 kΩ 上拉到 `VBAT`）：
  - 无线档：节点 3.3 V ⇒ `Vgs = 3.3 V` > `Vth`（2N7002 约 0.8–1.5 V）⇒ **导通** ⇒ `SYSOFF` 拉低 ⇒ 电池接通 ✓
  - 有线档：节点 0 V ⇒ `Vgs = 0` ⇒ **截止** ⇒ 100 kΩ 把 `SYSOFF` 拉到 `VBAT` ⇒ 电池断开 ✓
  - 而且 `SYSOFF` 的输入阈值很宽松（见下）：`V_IL` 最大 **0.4 V**、`V_IH` 最小 **1.4 V**，
    ⇒ **3.3 V 逻辑可以直接驱动，无需电平转换**。

- 🔴 **但方式 2 有一个方式 1 没有的启动死锁问题（以下是我的推导，标注为待验证）**：
  系统完全断电时（有线档、未插 USB），MCU 不供电 ⇒ 3.3 V 轨消失 ⇒
  **驱动给节点加的内部上拉也消失，节点浮空** ⇒ NMOS 栅极电位不确定。
  此时 100 kΩ 把 `SYSOFF` 拉高 ⇒ 电池保持断开 ⇒ **系统永远起不来**。
  （用户从「有线」拨回「无线」时就会撞上这个状态。）
  要救就得给栅极加一个「始终存在」的上拉，而唯一始终存在的轨是 `VBAT` ——
  但那会让 MCU 引脚承受 4.2 V（超出 3.3 V GPIO 的绝对最大额定），
  改成分压则**持续漏电约 21 µA，等于把待机电流翻倍**（本项目目标约 20 µA）。

  ⇒ **结论：方式 1 不仅更简单，而且没有这两个问题**（机械触点是纯被动的，
  不需要 MCU 供电来维持状态）。**故推荐方式 1。**

**方式 3（TI 官方文档记载，本项目不采用）：由 MCU GPIO 直接驱动 `SYSOFF`**

TI 应用笔记 **SLUAA18**《Achieving Ship Mode With the BQ24075…》记载了这条：
*"a few resistors, a push-button, and a FET that is controlled through an MCU General Purpose
Input/Output (GPIO)"*，并说明 *"When VIN is plugged in, the system is powered and **SYSOFF can be
pulled low using the GPIO** to keep the battery connected to the output for charging."*

本项目不采用，因为它把「关机」变成固件职责 —— 固件跑飞或卡死时无法断电，
与「物理开关」的初衷相反。**记为已知替代方案。**

**倾向**：若 `DP3T` 能买到合适封装，**优先方式 1**（机械方案不会在无线档意外断电）；
否则用方式 2，但必须把上述隐患当**一级风险**对待。

## 记账（不得含糊）

⚠️ **这不是电气隔离。** `SYSOFF` 给的是**低漏电态**（`IBAT(PDWN)` ≈ **4.3 µA 典型**），
电池仍与充电 IC 相连。说明文档必须写明。

对**存放**目的，4.3 µA 实际等同于断开（3000 mAh ÷ 4.3 µA ≈ **82 年**）；
真正的差别只在**维修安全**（拆机时电池仍带电）与**文档诚实性**上。

## 引脚预算

`SYSOFF` 是芯片引脚，**不占 MCU GPIO**。本决策对 ADR-0009 的引脚预算（14/18）**无影响** ——
但**如果 `SYSOFF` 的断开由「有线档」那一档的 GPIO 兼任（方式 2），
该 GPIO 就同时承担「模式选择」与「电源控制」两个职责**，
调试时需注意这两件事会一起失效。

## 未决 / 未核实

- ⚠️ **未实测**：本方案未在实物上验证；`2N7002` 的插电检测分压取值需按实际 USB 电压核算。
- ❓ **`DP3T` 微型开关的可用料号与封装**（方式 1 的唯一采购风险）。
- ❓ **方式 2 的晶体管误导通隐患**（`Veb = 0.9 V`）如何规避，需设计 + 实测。
- ❓ `BQ24075` 的 `EN1/EN2` 输入限流取值是否需调整（本项目目标 0.5–1.0 A 充电）。
- ❓ `MSK12C02` 的 20000 次寿命对「每天开关一次」约 55 年，够用；但**反复快速拨动**的机械耐久未测。
