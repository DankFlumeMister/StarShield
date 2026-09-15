# 采用 Per-key RGB，并以外部电源开关门控供电

用户要求每键独立发光，并能像商业键盘一样用组合键控制颜色/灯效/亮度。

RGB 是无线键盘的最大功耗源：95 颗可寻址 LED 即使不发光，芯片待机也可能持续消耗约 95mA，是主控深度睡眠电流（约 20µA）的数千倍。若不处理，3000mAh 电池会被待机漏电迅速耗尽。

我们决定：保留 per-key RGB，但在 LED 供电回路上串联一颗 PMOS 晶体管，由主控 GPIO 控制（ZMK external power control）。RGB 关闭或键盘进入深度睡眠时，固件拉高该引脚，物理切断 LED 供电，使其功耗接近零。

## Considered Options

- 不做 RGB：续航最佳，但不满足用户需求。
- 做 RGB 但不做电源门控：待机漏电约 95mA，电池在闲置时数天内耗尽，不可接受。
- 仅做底光（underglow）而非 per-key：功耗与布线都更简单，但不满足"每键独立发光"。

## Consequences

满足灯效需求且不牺牲待机续航；代价是 PCB 增加一颗 PMOS 及控制走线，固件需配置 ext-power 与闲置自动关闭。RGB 全开时续航仍以小时计，属预期内取舍。

## 勘误与补充（2026-09）

本 ADR 的**决策不变**（保留 per-key RGB + 电源门控），但原文有两处表述需更正。
触发原因是随后 ADR-0007 决定「LED 由电池直供」，改变了门控电路的前提。

### 勘误 1：待机漏电数字

原文「约 95mA」是估计值。实测 `SK6812MINI-E` 静态电流为 **0.6 mA/颗**，
95 颗 = **57 mA**（见 `docs/power-architecture.md` §5.1）。
结论不变（必须门控），但**引用时应采用 57 mA**。

### 勘误 2：极性描述只在一种拓扑下成立 —— ⚠️ 重要

原文「固件**拉高**该引脚，物理切断 LED 供电」**只在 P-FET 源极接 3.3 V 稳压轨时成立**。

本项目按 ADR-0007 让 LED 吃**电池轨（3.7–4.2 V）**，此时：

```text
P-FET 源极 = 4.2 V（满电），栅极最高只能被 3.3 V GPIO 拉到 3.3 V
⇒ Vgs = −0.9 V
而 AO3401A 的 VGS(th) 范围为 −0.5 V ~ −1.3 V，RDS(ON) 仅在 VGS ≤ −2.5 V 下规定
⇒ −0.9 V 落在亚阈值区，数据手册未规定该点行为，【不能保证关断】
```

⇒ **极性必须翻转为 `GPIO_ACTIVE_HIGH`，并加一级 NMOS 反相。**
加栅源上拉电阻**不能**解决：GPIO 推挽输出会把栅极钳在 3.3 V，上拉拉不过它。

> ⚠️ **诚实性说明**：上述「功能性失效」推论有数据手册的阈值侧支撑，
> 但**失效量级未经实测，也没有任何项目如此记载** ⇒ 标记 `❓ UNVERIFIED`。
> 第一版投板后**必须实测**该引脚的关断漏电。

### 补充：三种真实拓扑与应照抄的参考

社区实证（网表级核实）存在三种拓扑，**本项目只能用第三种**：

| 拓扑 | 实例 | 极性 | 源极位置 | 本项目可用？ |
| --- | --- | --- | --- | --- |
| A 直驱 P-FET | nRFMicro（Q2 `AO3407`）、nice!nano v1 | `ACTIVE_LOW` | **3.3 V 轨** | ❌ LED 需 ≥3.7 V |
| B 门控 LDO 使能脚 | nice!nano v2（XC6220 `CE`）、sasodoma SuperMini | `ACTIVE_HIGH` | — | ❌ 同上，且与 ADR-0007 冲突 |
| **C NMOS 反相 + P-FET** | **kurtis-lew/Conejo**、ZMK 硬件设计指南 | `ACTIVE_HIGH` | 电池轨 | ✅ **唯一可行** |

**关键结论：没有任何键盘项目把 P-FET 源极放在 4.2 V 电池轨、栅极直接由 3.3 V GPIO 驱动**
（30+ 仓库范围内核实）。凡是 GPIO 直驱 P-FET 的项目，**全部**把源极放在 3.3 V 稳压轨 ——
正是在绕开勘误 2 的问题。

> ⚠️ **归属更正（2026-09）**：本文所称「ZMK 硬件设计指南」的**原作者是 `ebastler`**
> （[`ebastler/zmk-designguide`](https://github.com/ebastler/zmk-designguide)，★494）。
> 本项目早期调研引用并做网表还原的是它的一份 **2022 年 fork 快照**
> （`Croktopus/zmk-designguide`，★2），两者**原理图内容不同**
> （470,802 B vs 348,045 B）。引用时请以上游 `ebastler` 为准。
> 该指南**没有任何模式开关**（无 BT/2.4G/MODE 网络标签），
> 其唯一的电源开关是 `SW1`（值为 `PWR`，接 `BQ24075` 的 `SYSOFF`）——
> ⇒ 它**不是**「一个开关同时管模式与电源」的先例。

### ⚠️ 照抄哪一个：选 **Conejo**，不要照抄 ZMK 硬件设计指南

**体二极管方向**：P-MOSFET 体二极管 **阳极在漏极**，因此导通方向是 `D → S`。
正确的高边开关接法是 **源极接电源轨、漏极接负载轨**。

- ✅ 方向正确：**Conejo Q3**（`S=VDDH` 电源、`D=EXT_PWR` 负载）、nRFMicro Q2、nice!nano v1 Q2
- ⚠️ 方向存疑：**ZMK 硬件设计指南 Q3** 把 `S` 放在负载侧（`UG_PWR`）、`D` 放在电源侧（`+VSW`），
  两份独立提取与仓库自带的渲染图在引脚号上一致 ⇒ **不是解析错误**；
  但未能排除「KiCad 符号的 S/D 引脚名与实际 SOT-23 不符」这一可能，
  故**标记待 EE 复核而非断言为缺陷**。该设计的 README 声称
  *"completely cut supply voltage ... no current flowing anywhere in the circuit"*，
  在体二极管正偏的接法下**该说法不成立**。

⇒ **本项目照抄 Conejo 的接法**（同拓扑、方向正确）：

```text
Q_p (AO3401A)：S → 电池轨（LED 供电来源），D → LED 轨，G → 经 10 kΩ 上拉到 S
Q_n (2N7002) ：S → GND，G → 经 100 Ω 接 MCU GPIO + 10 kΩ 下拉，D → Q_p 栅极
```

**详见** `research/keyboard-precedent-power-switching.md`、
`research/Q2_ext_power_gating_report.md`（子代理交付，含逐条引脚级来源）。
