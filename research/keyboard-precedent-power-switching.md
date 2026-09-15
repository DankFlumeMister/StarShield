# 真实键盘工程先例：电池物理断电 与 RGB LED 供电门控

本文件回答两个问题：(P1) 真实无线键盘怎么实现电池物理断电开关；(P2) 真实项目怎么门控 RGB LED 供电（ZMK `ext-power`）。
所有结论来自**可下载/可核对的一手文件**：KiCad `.kicad_sch`（纯文本 S-expression）、厂商原理图、ZMK devicetree/Kconfig/驱动源码、厂商文档。
单位、器件型号、datasheet 术语保留英文；凡未核实的进入文末 `## Uncertain / Could Not Verify`。

状态：🟢 已完成 P1/P2（草稿阶段的 R1、R2 两项待补已补齐；R3/R4 仍开放，见 §8）。

> ⚠️ **归属更正（2026-09）**：下文所称「ZMK 设计指南」的原作者是 **`ebastler`**
> （[`ebastler/zmk-designguide`](https://github.com/ebastler/zmk-designguide)，★494，最后更新 2024-07）。
> 本文做网表还原时用的是它的一份 **2022 年 fork 快照**
> （`Croktopus/zmk-designguide`，★2，最后更新 2022-10），下文 URL 指向该 fork。
> **两者原理图内容不同**（上游 470,802 B vs fork 348,045 B），引用时请以上游为准。
>
> 另经复核确认：**该指南没有任何模式开关** —— 原理图里不存在 `BT` / `2.4G` / `MODE` 网络标签，
> 唯一的电源开关是 `SW1`（值为 `PWR`，接 `BQ24075` 的 `SYSOFF`）。
> ⇒ **它不是「一个开关同时管模式与电源」的先例**，本文亦从未如此声称。

---

## 0. 方法（哪些是第一手核验，哪些只是 devicetree）

为本次调研写了两个工具，并对抓到的原理图做**引脚级网表还原**（wire / junction / label / global_label / power symbol 并查集），因此下文的 “A 脚接某网络” 是从文件里读出来的，不是看图猜的：

- `kisch.js` — KiCad 6/7/8 `.kicad_sch` 网表提取器（`--sym REF` / `--net NAME` / `--grep` / `--bom`）
- `pngcrop.js` + 厂商 PNG — 对 nice!nano v1/v2 原理图做裁切 + 5～7× 整数放大逐字读图（原图 1831×1256 / 1949×1215）

> ℹ️ 这两个工具是本次调研的一次性脚本，**未随本仓库发布**；但它们做的事情（解析 `.kicad_sch` 文本、
> 放大原理图图片读数）用 KiCad 自带功能或任意图片查看器都能手动复现，结论不依赖工具本身。

| 被解析的原始文件 | 关键核验结果 |
| --- | --- |
| `nrfmicro.kicad_sch`（joric/nRFMicro） | Q2(AO3407) 的 S/G/D、R9(2M) 去向、J3 电池座 → `VBAT` 全部还原 |
| `totem_0_3.kicad_sch`（GEIGEIGEIST/TOTEM） | PSW1 `SW_SPDT` 三个端点网络、`BAT+` 焊盘、XIAO `BAT` 脚全部还原 |
| `sweep-mini.kicad_sch`（davidphilipbarr/Sweep） | 该变体**无**电源开关、**无**电池接口（排除性结论） |
| `PCB/left.kicad_sch`（inpudiy/KOMETA） | 电池符号、开关 PS_L1、`YS-SK6812MINI-E`、控制器 `VCC`/`RAW` 脚全部还原 |
| `designguide-schematic.kicad_sch`（Croktopus/zmk-designguide） | 245 网络；SW1/SW2/Q1..Q4/R24/R25/R26/U3(BQ24075) 全部还原（信息量最大的一份） |

只到 devicetree 级别（硬件未公开）的项目，我在表中单独标注，不用于反推拓扑。

---

## 1. 真实项目总表（13 项，含 5 项网表级核验）

「开关接线」栏：**电池路径** = 开关串在电池与系统/充电器之间，承载全部负载电流；**控制路径** = 开关只切芯片使能/关断脚，只承载 µA 级电流。

| # | 项目 | MCU | RGB | 电池 | 电源开关怎么接 | 原理图可见器件 | 来源 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | **nice!nano v2**（商业控制器） | nRF52840 | 有（被门控 3.3V 脚） | 有（JST + 两个 `BATTERY+` 焊盘） | 板上无开关，开关在键盘 PCB 上、**电池路径**（见 §9 不确定项 2） | 充电器 **BQ24075**（`SYSOFF` 直接接 GND，**没用**）；**XC6220B331MR** LDO（3.3V/1A）`CE` 被 P0.13 + **R9 10 MΩ 上拉到 VIN** 控制 | [v2 原理图 1949px](https://nicekeyboards.com/static/511ae101870d00c265b84f35d5f39eda/61100/schematic_nice_nano_v2.png)、[pinout 文档](https://nicekeyboards.com/docs/nice-nano/pinout-schematic/) |
| 2 | **nice!nano v1** | nRF52840 | 有（`EXT_VCC`） | 有 | 同 #1（外部开关） | **Q2 P-Channel MOSFET**（型号图上不可辨）：`S=VDD_NRF`(3.3V)、`D=EXT_VCC`、`G=POWER_PIN`(P0.13) + **R9 2 MΩ 下拉到 GND**；Q1 P-FET 做 USB/电池 power path（`G=VBUS`）；LDO=**AP2112K-3.3** | [v1 原理图 1831px](https://nicekeyboards.com/static/724bec729cb82c3fb302249533b98589/111fd/schematic.png) |
| 3 | **nRFMicro**（joric，开源） | nRF52840(E73) | 有（`EXT_VCC`→Pro Micro VCC 脚） | 有（J3） | **无任何电源开关**，电池直进 `VBAT` | **Q2=AO3407**：`S=nRF_VDD`(AP2112K 3.3V)、`D=EXT_VCC`、`G=P1.09`、**R9=2 MΩ 下拉到 GND**；U3=TP4054；U2=**AP2112K-3.3** | [hardware/nrfmicro.kicad_sch](https://github.com/joric/nrfmicro/blob/main/hardware/nrfmicro.kicad_sch)、[ZMK board dts](https://github.com/zmkfirmware/zmk/blob/main/app/boards/joric/nrfmicro/nrfmicro_nrf52840_zmk.dts) |
| 4 | **TOTEM 0.3** | Seeed XIAO BLE | 无 | 有（±焊盘） | **电池路径**：`BAT+` 焊盘 → `VBAT_L` → **PSW1 (C–B)** → `BAT+_L` → XIAO `BAT`(pin19) | PSW1=`Switch:SW_SPDT`；仓库提供 **`MSK12C02.STEP`** → 实物即 MSK12C02 系列（50 mA 级） | [PCB/totem_0-3/totem_0_3.kicad_sch](https://github.com/GEIGEIGEIST/TOTEM/blob/main/PCB/totem_0-3/totem_0_3.kicad_sch)、[目录含 MSK12C02.STEP](https://github.com/GEIGEIGEIST/TOTEM/tree/main/PCB/totem_0-3) |
| 5 | **KOMETA** | nice!nano / SuperMini | 有（`YS-SK6812MINI-E`，VDD 接控制器 `VCC` 脚） | 有（焊接盘） | **电池路径**：`PW_L1`(BAT+) → `PS_L1` → `RAW_L` → 控制器 `RAW`(pin24) | BOM 明列 **MSK12C02 Slide Switch** | [PCB/left.kicad_sch](https://github.com/inpudiy/KOMETA/blob/main/PCB/left.kicad_sch)、[README/BOM](https://github.com/inpudiy/KOMETA) |
| 6 | **ZMK 硬件设计指南参考设计**（作者亦为 marbastlib 维护者） | nRF52840 模块（holyiot 18010 / moko mk08a） | 有（WS2812C_2020 underglow + **门控**） | 有（JST PH / J3 / J4） | **两种都画了**：① 简易版 SW2 串**电池路径**（`+BATT`↔`J3.1`）；② 进阶版开关接 **BQ24075 `SYSOFF`**（公共端=SYSOFF；一端经 R4 100 kΩ 上拉到 `+BATT`=关断；另一端 GND=开机），**只走 µA**；另加 **Q2 2N7002** 在插 USB 时把 `SYSOFF` 拉低，保证插电仍能充电 | SW1/SW2 footprint=`marbastlib-various:SW_MSK12C02-HB`；Q1/Q3=**AO3401A**；Q2/Q4=**2N7002**；R24 10 kΩ、R25 100 Ω、R26 10 kΩ；保护 U4=**DW01A**+FS8205；电量计 U9=**MAX17048** | [readme.md](https://github.com/Croktopus/zmk-designguide/blob/main/readme.md)、[designguide-schematic.kicad_sch](https://github.com/Croktopus/zmk-designguide/blob/main/designguide-schematic/designguide-schematic.kicad_sch) |
| 7 | **MoErgo Glove80**（商业，per-key WS2812） | nRF52840 | 有 | 有 | 硬件未公开；固件侧 `EXT_POWER` 的 net 注释直写 **`/* WS2812_CE */`**（芯片使能脚），`GPIO_ACTIVE_HIGH`，`init-delay-ms=100` | 器件未公开 | [glove80_lh.dts](https://github.com/zmkfirmware/zmk/blob/main/app/boards/moergo/glove80/glove80_lh.dts)、[MoErgo 扩展电子文档](https://docs.moergo.com/glove80-user-guide/appendix-more-customizations/) |
| 8 | **Kinesis Advantage360 Pro** | nRF52840 | 有 | 有 | 硬件未公开 | `EXT_POWER`=`&gpio0 13 GPIO_ACTIVE_HIGH` | [adv360pro.dtsi](https://github.com/zmkfirmware/zmk/blob/main/app/boards/kinesis/adv360pro/adv360pro.dtsi) |
| 9 | **polarityworks BT60/BT65/BT75**（60%/65%/75% 无线 + RGB underglow） | nRF52840 | 有 | 有 | 硬件未公开 | `EXT_POWER`=`&gpio0 13 GPIO_ACTIVE_HIGH` | [ckp.dtsi](https://github.com/zmkfirmware/zmk/blob/main/app/boards/polarityworks/common/ckp.dtsi) |
| 10 | **splitkb Aurora 系列**（Corne/Sofle v2/Lily58/Sweep/Helix，per-key SK6812MINI-E + nice!nano） | nice!nano / Liatris | 有 | 有 | 文档原文：开关 “**fully disconnect the battery from the microcontroller**” ＝**电池路径**串联；LED 轨由控制器被门控的 VCC/3.3V 脚供电 | 型号未公开（schematic PDF 为曲线化矢量，无可提取文本） | [Power switches](https://docs.splitkb.com/product-guides/aurora-series/build-guide/power-switch)、[Per-key RGB](https://docs.splitkb.com/product-guides/aurora-series/build-guide/per-key-rgb) |
| 11 | **BlueMicro840** | nRF52840 | 有 | 有 | 硬件未取得 | `EXT_POWER`=`&gpio0 12 GPIO_ACTIVE_HIGH` | [dts](https://github.com/zmkfirmware/zmk/blob/main/app/boards/jpconstantineau/bluemicro840/bluemicro840_nrf52840_zmk.dts) |
| 12 | **Puchi BLE**（keycapsss） | nRF52840 | 有 | 有 | 硬件未取得；引脚/极性与 nRFMicro 同 | `EXT_POWER`=`&gpio1 9 GPIO_ACTIVE_LOW` | [dts](https://github.com/zmkfirmware/zmk/blob/main/app/boards/keycapsss/puchi_ble/puchi_ble_nrf52840_zmk.dts) |
| 13 | **MechWild Pillbug** | nRF52840 | 有 | 有 | 硬件未取得 | `EXT_POWER`=`&gpio1 7 GPIO_ACTIVE_LOW`，`init-delay-ms=50` | [dts](https://github.com/zmkfirmware/zmk/blob/main/app/boards/mechwild/pillbug/pillbug_nrf52840_zmk.dts) |
| 14 | **nice!60**（nicekeyboards 60%） | nRF52840 | 有 | — | 硬件未取得 | `EXT_POWER`=`&gpio0 5 **GPIO_ACTIVE_LOW**`（与 nice!nano v2 相反） | [dts](https://github.com/zmkfirmware/zmk/blob/main/app/boards/nicekeyboards/nice60/nice60_nrf52840_zmk.dts) |

---

## 2. P1 结论一：主流做法＝开关串在电池路径，**必须承载全部电流**

有物理开关的板子（TOTEM、KOMETA、Aurora、设计指南简易版）全是同一接法：**开关串在电池正极与控制器 BAT/RAW 输入之间**。TOTEM、KOMETA 是网表级确证。

设计指南作者把这件事写成了明文结论（原文）：

> “`SW2` is a simple power switch to cut the battery from the system – … **In addition, the switch has to withstand the entire battery current** – finding a sufficiently small footprint switch that can take up to 500 mA (or, in the case of our example, 250 mA) can prove difficult.”
> —— [zmk-designguide readme.md · Simple implementation](https://github.com/Croktopus/zmk-designguide/blob/main/readme.md)

即：**没有「开关只走睡眠电流」这条约定**（在串联接法下它是错的）。串联开关要同时承受：
1. 系统运行电流（MCU + 传感器 + OLED/屏幕）；
2. **LED 轨电流**（只要 LED 由控制器被门控的 VCC/3.3V 脚供电，nice!nano/KOMETA/Aurora 都属于这种）；
3. **充电电流**（充电时电流经 BAT 脚流入电池，同样穿过该开关）——设计指南提到的 “up to 500 mA” 就是这一项。

**这条对本项目（P1）的直接影响**：StarShield 若把 MSK12C02（50 mA）串进电池路径，在 RGB 全开（理论 3.4 A / 70% 灰阶 2.4 A，见 `docs/power-architecture.md` §5.1）时会远超额定；即便只算系统电流也仅剩 2× 余量。

## 3. P1 结论二：唯一的「小开关切大电流」实证＝切充电器 `SYSOFF`（控制路径）

设计指南进阶版把开关接到 **BQ24075 的 `SYSOFF`**（网表实测）：

```text
SW1 (footprint SW_MSK12C02-HB, 即 MSK12C02)
   pin B(公共) → SYSOFF        pin A → R4 100 kΩ → +BATT      pin C → GND
Q2 = 2N7002 (NMOS): G ← R5 100 Ω ← +5V(USB)，R8 10 kΩ 下拉；S = GND；D = SYSOFF
```

作者原文：

> “It also has a very useful ‘sysoff’ feature, that **can be used to switch the battery off without the whole battery current passing through the microswitch**.”
> “If `SYSOFF` is connected to VBAT, the chip completely cuts the battery from the rest of the schematic. … it would not charge even when plugged in in this mode … That's what Q2 is for. Q2 will pull `SYSOFF` to GND as soon as the board is plugged in for charging … **Unlike the simple implementation, this switch does not have any significant current flowing through it, and can be chosen a lot smaller.**”
> —— [readme.md · Advanced implementation](https://github.com/Croktopus/zmk-designguide/blob/main/readme.md)

**控制电流量级**：常态经 100 kΩ 上拉到 `+BATT` → 4.2 V 时约 **42 µA**；对已核验额定 **DC 12 V / 50 mA** 的 MSK12C02（[SHOU HAN 规格书 · LCSC C431540](https://datasheet.lcsc.com/datasheet/pdf/5162155576bfd231c35aa9a893d25c8c.pdf?productCode=C431540)，见本仓库 `spdt-slide-switch-battery-cutoff-facts.md`）余量约 1000×。

**代价（作者自己点出的坑）**：`SYSOFF` 拉高会同时**禁用充电**，忘在 off 档就充不进电 → 用 Q2 在 USB 插入时强行拉低解决。
**TI datasheet 侧（本仓库已按 SLUS810N 核验，`bq24072-power-path-verified-facts.md`）**：`SYSOFF` 仅 BQ24075/BQ24079 有（pin 15），内部约 **5 MΩ 上拉到 VBAT**，正常工作要求接 VSS、**不可悬空**；`SYSOFF` 高 → 断开连接电池与 OUT 的 FET，且接适配器时充电一并禁用。**BQ24072 的 pin 15 是 `TD`，没有 SYSOFF，做不到这件事。**

## 4. P1 结论三：真实项目用的开关料号

| 型号 | 额定（DC） | 真实项目中的使用 |
| --- | --- | --- |
| **MSK12C02**（SHOU HAN） | **12 V DC / 50 mA**（规格书 §2.5） | **TOTEM**（仓库带 `MSK12C02.STEP`）、**KOMETA**（BOM 明列）、**ZMK 设计指南**（footprint `SW_MSK12C02-HB`） |
| C&K **OS102011MS2QN1** | 0.1 A @ 12 V DC | 常见 THT 替代（本仓库已核验） |
| C&K **1101M2S3CQE2** | **6 A @ 28 V DC** | 目前唯一在 2–3 A 下有余量的滑动开关（本仓库已核验，无官方 KiCad footprint） |

**结论：真实无线键盘界事实默认使用 50 mA 级的 MSK12C02**——在没有大电流 LED 轨的板子上（TOTEM）或**只走控制信号**时（设计指南 SYSOFF 方案）完全合适；一旦 LED 电流走同一路径就是明确的超额定使用。

## 5. P1 结论四：没有人用「P-FET + 小开关」切电池主电流（但有等价思想）

- 我**没有找到任何键盘项目**用分立 P-FET + 小开关切电池主电流。核验到的电池侧 FET 只有两类用途：
  - **power path（USB 优先）**：nice!nano v1 的 **Q1 P-FET**（网表/读图：`S=+VSW`、`D=+BATT`、**`G=+5V`(VBUS)**，非 GPIO）+ 肖特基 `D2`；设计指南 **Q1 AO3401A**（网表：`G=+5V, S=+VSW, D=+BATT`）。这不是电源开关。
  - **保护**：设计指南 `DW01A + FS8205` 双 MOSFET 串在电池负极与地之间（欠压/过流保护），不是用户开关。
- 「小开关只切控制信号」的思想在真实项目里**存在，但落地方式是切 `SYSOFF`**（§3），不是自建 MOSFET 负载开关。若 StarShield 想用这条路（BQ24072 无 SYSOFF），就得自己补一颗 P-FET——见 §7 建议。

---

## 6. P2：RGB LED 供电门控（ZMK `ext-power`）

### 6.1 ZMK 侧语义（先定语义，否则极性无从解释）

- binding：`compatible = "zmk,ext-power-generic"`，属性 `control-gpios`（“List of GPIOs which should be active to enable external power”）与 `init-delay-ms`（[zmk,ext-power-generic.yaml](https://github.com/zmkfirmware/zmk/blob/main/app/dts/bindings/zmk,ext-power-generic.yaml)）。
- 驱动逐行核对（[ext_power_generic.c](https://github.com/zmkfirmware/zmk/blob/main/app/src/ext_power_generic.c)）：
  - `enable` → `gpio_pin_set_dt(gpio, 1)` = 写**逻辑有效电平**；`GPIO_ACTIVE_LOW` 时物理输出低。
  - `init` → 先 `GPIO_OUTPUT_INACTIVE`，**随后立刻 `ext_power_enable()`（上电默认开）**，之后 settings 载入可关闭（状态跨重启保存）。
  - PM `SUSPEND` → disable；`RESUME` → enable。
- Kconfig（[app/Kconfig](https://github.com/zmkfirmware/zmk/blob/main/app/Kconfig)）：`ZMK_EXT_POWER`；`ZMK_RGB_UNDERGLOW_EXT_POWER` = **"RGB underglow toggling also controls external power"**（关灯顺手断电，建议开）；软关机 `ZMK_PM_SOFT_OFF`（深睡唤醒靠 `DT_HAS_ZMK_GPIO_KEY_WAKEUP_TRIGGER`）。

### 6.2 极性 ↔ 物理拓扑对照（关键表，来自 #1/#2/#3/#6 的硬件核验）

| devicetree 极性 | 物理含义 | 对应拓扑 | 真实实例 |
| --- | --- | --- | --- |
| `GPIO_ACTIVE_LOW` | 拉**低**＝开电；GPIO 的“关”态是物理 **3.3 V** | P-FET 高边开关，**S 接已稳压 3.3 V 轨**，D 接 LED 轨，G 直连 GPIO + 下拉电阻（默认开） | nRFMicro(`&gpio1 9`)、nice!nano v1(`&gpio0 13`)、Puchi BLE(`&gpio1 9`)、Pillbug(`&gpio1 7`)、nice!60(`&gpio0 5`) |
| `GPIO_ACTIVE_HIGH` | 拉**高**＝开电 | ① LDO/load switch 的 **EN/CE 脚**；② **NMOS 反相级 + P-FET**（GPIO→NMOS 栅；NMOS 漏极拉 P-FET 栅；P-FET 栅经电阻上拉到源轨） | ① nice!nano v2（XC6220 `CE`）、Glove80（`WS2812_CE`）；② ZMK 设计指南（Q4 2N7002 + Q3 AO3401A） |

> ⚠️ **重要观察：没有任何键盘项目把 P-FET 源极放在（4.2 V 级）电池轨、栅极直接由 3.3 V GPIO 驱动。**
> 直接由 GPIO 驱动 P-FET 的项目，**全部**把源极放在 **3.3 V 稳压轨**（nRFMicro 的 `nRF_VDD`、nice!nano v1 的 `VDD_NRF`）—— 这正是在规避你算出的 `Vgs(off) = −0.9 V` 问题。
> 唯一一个栅极被驱动到电池轨电位的 P-FET（nice!nano v1 的 Q1），驱动源是 **VBUS 5 V**，不是 GPIO。
> 这也意味着：**ADR-0005 里「固件拉高该引脚即切断 LED 供电」的表述，只在「源极在 3.3 V 轨」时成立**；若按 ADR-0007 让 LED 吃电池轨，极性必须翻成 `GPIO_ACTIVE_HIGH` 并加反相级（或换带 EN 的负载开关）。

### 6.3 三种真实存在的门控拓扑

**拓扑 A —— P-FET 串在 3.3 V 稳压轨（GPIO 直驱，`ACTIVE_LOW`）**
- nRFMicro 网表实测：`Q2=AO3407`，`S=nRF_VDD`（AP2112K 输出）、`D=EXT_VCC`（→ 键盘 LED 轨）、`G=P1.09`、`R9=2 MΩ` 栅极→**GND**（下拉＝默认导通）。
- nice!nano v1 同构：P-FET（型号不可辨）`S=VDD_NRF`、`D=EXT_VCC`、`G=P0.13` + 2 MΩ 到 GND；官方文档原话：“P0.13 on VCC shuts off the power to VCC when you set it to high — This saves on battery immensely for LEDs of all kinds that eat power even when off”。
- **代价**：LED 只能拿 3.3 V → 与本项目 LED 的 3.7 V 下限冲突（ADR-0007），**不能照抄**。

**拓扑 B —— 门控 LDO 的 CE/EN 脚（`ACTIVE_HIGH`）＝ nice!nano v2 现行方案**
- 读图实测：`U3 = XC6220B331MR`（Torex XC6220，3.3 V / 1 A），`VIN=VDDH`、`VOUT=EXT_VCC`（= nice!nano `3.3V` 脚）、**`R9=10 MΩ` 从 VIN 上拉到 `CE`（默认开）**、`POWER_PIN`(P0.13) 直接接 `CE` → **拉低即断电**；对应 `GPIO_ACTIVE_HIGH`。
- 优点：关断时 LED 轨是**高阻**，不存在给栅极找电位的问题；一颗器件同时完成稳压 + 门控。
- Glove80 的 `WS2812_CE` 说明商业板也走“使能脚”这一路（器件未公开）。

**拓扑 C —— NMOS 反相级 + P-FET，栅极经 10 kΩ 上拉到源轨（`ACTIVE_HIGH`）＝ 保住 LED 全电压的唯一实证**
- 设计指南网表实测：
  - `Q3 = AO3401A`(P-FET)：`D=+VSW`（系统轨）、`S=UG_PWR`（LED 轨）、`G` 与 `R24.2`/`Q4.3` 同网；
  - `R24 = 10 kΩ`：一端 `+VSW`，一端 Q3 栅极（上拉，默认关）；
  - `Q4 = 2N7002`(NMOS)：`G` 与 `R26.1`(10 kΩ→GND)、`R25.1`(100 Ω) 同网；`S=GND`；`D=Q3 栅极`；
  - `R25` 另一端 = `UG_EN` → nRF52840 **P0.10**。
- 作者原文：“If the LEDs are turned off, `UG_EN` is low, therefore the gate of `Q4` is low, and the gate of `Q3` is high – this leads to no current flowing anywhere in the circuit. Once `UG_EN` is high, so is the gate of `Q4`, which in turn pulls the gate of `Q3` low.”
- ⚠ **该文件的器件朝向有问题，照抄要翻过来**：它把 `S` 放在负载侧（`UG_PWR`）、`D` 放在电源侧（`+VSW`）。P-MOSFET 体二极管是 **anode = drain、cathode = source**，因此关断时体二极管**正偏**（`+VSW → UG_PWR`），LED 轨会被抬到约 `VSW − 0.7 V`，与作者“完全无电流”的说法在原理上不符（是否因 WS2812C 在 ~3.0–3.5 V 欠压而实际电流很小，我无法核实）。
  **正确朝向：S 接电源轨、D 接负载轨** —— 这也正是 nice!nano v1 的 Q1 与 nRFMicro 的 Q2 的朝向（源极在电源侧）。

### 6.4 devicetree 原文（可直接对照）

```dts
/* nice!nano v2 —— LDO CE 型（拓扑 B） */
EXT_POWER {
    compatible = "zmk,ext-power-generic";
    control-gpios = <&gpio0 13 GPIO_ACTIVE_HIGH>;
    init-delay-ms = <50>;
};

/* nRFMicro —— P-FET 在 3.3V 轨（拓扑 A） */
EXT_POWER {
    compatible = "zmk,ext-power-generic";
    control-gpios = <&gpio1 9 GPIO_ACTIVE_LOW>;
    init-delay-ms = <50>;
};

/* Glove80 —— 使能型器件（拓扑 B 类） */
EXT_POWER {
    compatible = "zmk,ext-power-generic";
    control-gpios = <&gpio0 31 GPIO_ACTIVE_HIGH>; /* WS2812_CE */
    init-delay-ms = <100>;
};
```

注意：**节点名必须是 `EXT_POWER`**（各文件均有注释 “Node name must match original "EXT_POWER" label to preserve user settings.”），改名会让用户已保存的开关状态失效。

---

## 7. 对 StarShield 的建议（结合 ADR-0002/0005/0007 与本项目已核验数字）

约束回顾（项目内部文件）：LED = `SK6812MINI-E`(LCSC C5149201)，**工作电压 3.7–5.5 V**（`docs/power-architecture.md` §5.1、ADR-0007），且 ADR-0007 已决定**电池直供**；ADR-0005 决定用 PMOS 门控；充电器 BQ24072（ADR-0002，**无 SYSOFF**）。

### 7.1 LED 轨门控（P2）——推荐「设计指南拓扑 C 的修正版」

因为 ADR-0007 要求 LED 吃电池轨（3.7–4.2 V），**拓扑 A/B（3.3 V 轨）都不可用**（会让 LED 低于标称下限）。可行方案：

1. **首选：NMOS 反相 + P-FET 在电池轨上**（先例：ZMK 设计指南 Q3/Q4，`ACTIVE_HIGH`）
   - `Q_gate = 2N7002`（NMOS）：`S=GND`，`G` 经 100 Ω 接 GPIO（P0.x），10 kΩ 下拉到 GND；
   - `Q_led = AO3401A`（P-FET）：**`S=电池轨`，`D=LED 轨`**（把设计指南的 S/D 翻正，理由见 §6.3 拓扑 C），栅极经 **10 kΩ 上拉到 `S`**，由 NMOS 漏极拉低；
   - devicetree：`control-gpios = <&gpio0 N GPIO_ACTIVE_HIGH>;`，并同时修正 ADR-0005 中「拉高＝切断」的表述（反相后是**拉高＝接通**）；
   - 该结构在 4.2 V 电池下 `Vgs(off) = 0 V`（**保证关断**），`Vgs(on) ≈ −4.2 V`（充分导通），彻底消除你发现的 −0.9 V 问题。
   - ⚠ AO3401A 的电流能力（datasheet 已核验）：`ID = −4 A@25 °C / −3.2 A@70 °C`、`RDS(on) max = 85 mΩ @ VGS=−2.5 V`、SOT-23 `PD = 0.9 W@70 °C`。你的 LED 轨理论峰值 3.4 A（70% 灰阶 2.4 A，`docs/power-architecture.md` §5.1）：2.4 A 时 `P = I²R ≈ 0.49 W`（可接受但偏热），3.4 A 时 ≈ 0.98 W（**超** 0.9 W 限值）。**要么固件限流/限亮度，要么换更大封装的低 Rds(on) P-FET（型号我未核验，见 §9.8）**。
2. **备选：改用带 EN 的负载开关 / 带 CE 的 LDO 给 LED 供电**（nice!nano v2 思路，`ACTIVE_HIGH`）——但需选输出 ≥3.7 V 的型号才能满足 ADR-0007；若选 3.3 V 输出则与 ADR-0007 冲突，需要重新决策。
3. **固件**：`CONFIG_ZMK_RGB_UNDERGLOW_EXT_POWER=y`（Kconfig 原文 “RGB underglow toggling also controls external power”）；记住 ZMK 上电默认把 ext-power 打开。
4. **数据线电平提醒**：设计指南原文 “**SK6812MINI need 3.4 V for a logical high**”，3.3 V GPIO 达不到；作者给了 **TXB0101** 电平转换示例，并说 SK6812MINI “should work without one too, though out-of-spec”。本项目 LED 属这一类，建议评估。

### 7.2 电池开关（P1）

1. **不要**把 MSK12C02 串进电池路径（50 mA vs 2.4–3.4 A）。真实项目之所以敢用，是因为要么没有大电流 LED 轨（TOTEM），要么只走控制信号（设计指南 SYSOFF 版）。
2. **推荐：MSK12C02 只走控制信号 + P-FET 负载开关串在电池路径**（思想来自设计指南 §3，器件朝向来自 nRFMicro/nice!nano v1）：
   - `Q_bat` P-FET：**`S=电池正极`，`D=系统（BQ24072 的 BAT/系统轨）`**，体二极管 anode=drain → 关断时反向截止，不会经体二极管漏到负载；
   - 栅极 **100 kΩ 上拉到 `S`** → 默认 `Vgs = 0`，**可靠关断**；
   - MSK12C02（SPDT）：公共端=栅极；一档接 GND（`Vgs=−Vbat` → 导通）；另一档接 `S`（`Vgs=0` → 关断）。开关电流 ≈ 4.2 V/100 kΩ ≈ **42 µA**（对 50 mA 额定＝1000× 余量）；
   - 电流能力按 P-FET 复核（同 §7.1 的 AO3401A 限制）。
   - 副作用与串联接法相同：**开关关闭时无法充电**（设计指南原文 “the board will also be unable to charge as long as it is flicked off”）。若要在关闭状态下插 USB 也能充电，需要 USB 检测旁路（设计指南用 Q2 2N7002，但那依赖 SYSOFF）。
3. **另一条路：直串一颗 6 A 级滑动开关** —— C&K **1101M2S3CQE2**（6 A@28 V DC，THT，12.7×6.6×11.4 mm，**无官方 KiCad footprint**）。与 TOTEM/KOMETA/Aurora 同构，只是换大电流器件。
4. **若可改充电器**：换 **BQ24075**（同族、同 RGT VQFN-16 封装，pin 15 = SYSOFF）即可照抄 §3 的官方参考设计（MSK12C02 + 100 kΩ + 2N7002 自动插电充电）。BQ24072 的 pin 15 是 `TD`，**做不到**。

### 7.3 一句话回答「只走睡眠电流」这个约定

- 串联在电池路径（TOTEM / KOMETA / Aurora / 设计指南简易版）→ **假**：要扛系统 + LED + 充电电流，设计指南原文明确要求 “withstand the entire battery current”。
- 只切 `SYSOFF` 或某个使能脚（设计指南进阶版）→ **真**：≈42 µA（100 kΩ @4.2 V），MSK12C02 这类 50 mA 小开关绰绰有余。
- 具体到 nice!nano 架构：LED 轨来自被门控的 3.3 V 脚，而电池开关在这条链的**最上游**（电池→开关→充电器 BAT/power path→VDDH→LDO→LED），所以**亮灯时开关必须承载 LED 电流**；只有把开关挪到 `SYSOFF`/EN 这类旁路位置，才只走 µA。

---

## 8. 上一轮草稿的修正与遗留

- ✅ 草稿 §2「nRFMicro 把 PMOS 放在 LDO 之后」**结论正确**，用网表还原再次确证（`S=nRF_VDD`、`D=EXT_VCC`、`R9=2 MΩ→GND`、`G=P1.09`），并补上了同类实证 nice!nano v1。
- ✅ 草稿待补项 **R1（带电池 + RGB 的板子怎么门控 LED 轨）**：已答，见 §6.3/§6.4（三条拓扑 + 极性对照表 + 四个真实板子的 devicetree）。
- ✅ 草稿待补项 **R2（物理断电开关的料号与额定）**：已答，见 §3/§4（MSK12C02 三家在用；SYSOFF 控制路径方案；C&K 1101M2S3CQE2 为 6 A 级替代）。
- ⚠ 需修正的项目内部表述：**ADR-0005 的“固件拉高该引脚＝切断 LED 供电”只在源极位于 3.3 V 轨时成立**；在 ADR-0007 的电池直供方案下必须加反相级并把极性改为 `GPIO_ACTIVE_HIGH`（§6.2/§7.1）。
- 📌 仍未做（与本次问题无关，保留）：R3 移位寄存器矩阵、R4 ≥60% 无线键盘的行列分配。

---

## 8b. 补充核实（从原厂 datasheet 与 KiCad 官方库独立核验）

以下三项是在本报告基础上**独立复核**的结果，用于修正/补强本报告的结论。

### 8b.1 ✅ SK6812MINI-E 的数据线电平：本设计**不需要** level shifter（与指南措辞不同）

本报告引用设计指南的「SK6812MINI need 3.4 V for a logical high」。
下载 **`SK6812MINI-E` 原厂规格书**（LCSC C5149201 的 PDF，819 KB）并抽取文本后，得到精确规格：

```text
工作电压 / Chip input voltage   VDD   3.7 ~ 5.0 ~ 5.5  V
VIH                             VIH   0.65 × VDD          V      ← 是比例，不是固定 3.4 V
VIL                             VIL   0.3 × VDD           V
静态功耗                         IDD   0.6 mA (VDD=4.5V)
输出驱动电流                     IDOUT 10 / 12 / 14.5 mA (VDD=5.0V)
```

**关键：设计指南的「3.4 V」是按 VDD=5 V 反推的（0.65 × 5 = 3.25），并不适用于本设计。**
本项目 LED **由电池直供（ADR-0007）**，所以 VDD 就是电池电压。逐点预算：

| VDD（电池） | VIH = 0.65×VDD | 3.3 V GPIO 余量 | 结论 |
| --- | --- | --- | --- |
| 5.0 V | 3.250 V | +0.050 V | ⚠️ 边缘（这正是指南提到 5 V 轨的情形） |
| 4.2 V（满电） | 2.730 V | **+0.570 V** | ✅ |
| 4.0 V | 2.600 V | +0.700 V | ✅ |
| 3.8 V | 2.470 V | +0.830 V | ✅ |
| 3.7 V（标称最低） | 2.405 V | **+0.895 V** | ✅ |

⇒ **本设计不需要 TXB0108/TXB0101 之类的 level shifter。**
指南的警告针对的是「LED 接 5 V、MCU 跑 3.3 V」的情形；**电池直供反而让这个问题消失**。
（⚠️ 反过来说：**不能**给 LED 加 5 V 升压，否则电平余量会掉到 50 mV。）

### 8b.2 ✅ BQ24072/73/74/75/79 **封装完全相同**，可视为 drop-in 互换

从 KiCad 官方符号库核验（`Battery_Management.kicad_sym`）：

| 型号 | Footprint | pin 15 功能 |
| --- | --- | --- |
| `BQ24072RGT` | `VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm` | `TD` |
| `BQ24073RGT` | 同上 | — |
| `BQ24074RGT` | 同上 | `ITERM` |
| **`BQ24075RGT`** | **同上** | **`SYSOFF`** ✅ |
| `BQ24079RGT` | 同上 | — |

⇒ **本报告 §3 推荐的「小开关切 `SYSOFF`」方案对本项目是可行的** ——
只需把 U1 从 `BQ24072` 换成 **`BQ24075`（同厂、同封装、同引脚数）**，PCB 与其余外围电路基本不动。
⚠️ 但仍需复核 `BQ24075` 的 `EN1/EN2` 输入限流配置与本项目取值的兼容性（本报告 §9.9 已列为待核验）。

### 8b.3 ⚠️ 对「必须承载全部电流」这一结论的补强与一处修正

- ✅ **补强**：本报告 §2 的核心结论（串联开关必须承载全部电流）**成立且关键**。
  据此重新审视本项目数字：LED 峰值 2.4 A（70% 灰阶）会**全部流过**串联开关，
  所以 `MSK12C02`（50 mA）差 **48 倍**，`OS102011MS2QN1`（0.1 A）差 **24 倍**。
  ⇒ **「用固件限制 RGB 亮度」救不活小开关**；要么换 6 A 机械开关，要么走 `SYSOFF`/负载开关路线。
- ⚠️ **修正本报告 §7 的一处风险提示**：本报告提到 AO3401A 在 3.4 A 时超封装耗散限值 —— 复核计算：
  `P = Rds(on) × I²`，取已核验的 **85 mΩ @ Vgs=−2.5 V**（不是标称 60 mΩ）：

  | RGB 电流 | 门控自身耗散 | AO3401A 限值 @70 °C | 结论 |
  | --- | --- | --- | --- |
  | 1.0 A | 0.085 W | 0.9 W | ✅ 轻松 |
  | 2.4 A（70% 灰阶） | 0.490 W | 0.9 W | ✅ 可用（余量 1.8×） |
  | 3.4 A（理论满亮） | 0.983 W | 0.9 W | ❌ **超限** |

  ⇒ 结论与本报告一致：**必须限制 RGB 峰值电流**（建议固件限到 ~1 A），
  或改用更大封装 / 更低 Rds(on) 的 P-FET。

---

## 9. Uncertain / Could Not Verify

1. **nice!nano v1 的 Q2/Q1 P-FET 型号**：厂商只发布 PNG（最大 1831 px），器件值字样不可辨；只能确认是 “P Channel” MOSFET。**型号 UNVERIFIED**。
2. **nice!nano 的电池开关具体接在哪两个焊盘**：v2 原理图里 J2 的 pin 14/15 两个 global label **都叫 `VBAT`**（放大 7× 逐字确认），若二者同网，跨接它们的外部开关在电气上无效；pinout 图上两个焊盘也都标 `BATTERY+`。因此“开关跨接两个 BATTERY+ 焊盘”这一流行说法**我未能在原理图上验证成功**，它与“开关串在电池路径”的一般结论存在冲突。**建议用万用表实测（TOTEM/KOMETA 的串联接法是网表级确证的，可直接借鉴）。**
3. **splitkb Aurora 的开关器件型号**：官方原理图 PDF 为曲线化矢量（文本不可提取），文档未写型号。**UNVERIFIED**；“开关串电池路径 + LED 由被门控 VCC 供电”来自文档文字与 Aurora 系列 devicetree，非网表。
4. **Glove80 / Kinesis ADV360 Pro / polarityworks BT60/65/75 的具体器件**：硬件未公开。Glove80 的 net 注释 `WS2812_CE` 是唯一拓扑线索。**拓扑 UNVERIFIED**。
5. **ZMK 设计指南 LED 门控的体二极管问题**：我给出的“关断时体二极管正偏、LED 轨仍被抬到 `VSW−0.7 V`”是基于器件朝向 + 标准 P-MOSFET 体二极管极性的**推理**，未实测；作者声称“no current flowing anywhere”。两者是否矛盾、以及 WS2812C 在 ~3 V 下漏电是否真的可忽略，**UNVERIFIED**。
6. **LED 静态电流数值**：设计指南写 “~1 mA per LED even when off”，本项目实测 0.6 mA/颗（95 颗 57 mA，`docs/power-architecture.md` §5.1）。我**没有**从 LED datasheet 核实这两个数字（设计指南引用的 [WS2812C-2020 V1.2](https://cdn.sparkfun.com/assets/e/1/0/f/b/WS2812C-2020_V1.2_EN_19112716191654.pdf) 未下载核验）。
7. **其它常见键盘项目**：Corne(crkbd)、Sofle、Lily58、Chocofi、Klor、Zodiark、Reviung、Ferris、Hummingbird、Jian、Sweep 各变体 —— 实际取得的 KiCad 中，crkbd v4 / Sofle v2 / Lily58 公开 PCB 都是**有线**版本（无电池、无电源开关，LED 由 RAW 供电，不涉及门控）；Sweep Mini 该变体无开关无电池；Ferris 0.2 原理图是 **KiCad 5 旧格式 `.sch`**，本文的解析方法不支持，未核验。其余项目**未能找到可信的一手原理图**。它们在架构上多为 nice!nano 方案，LED 轨大概率接在被门控的 VCC 脚上，但**未逐一验证**。
8. **3 A 档 P-FET 的具体替代型号**：本文只给出已核验的 AO3401A / DMG2301L / IRLML6402 数据与“AO3401A 在 2.4–3.4 A 下已接近或超出封装耗散限值”的计算，**未推荐任何未核验型号**。
9. **`SYSOFF` 的“插电自动上电”是否对本项目适用**：设计指南的 Q2 旁路是在 BQ24075 上验证的；若 StarShield 改用 BQ24075，需同时复核 EN1/EN2 输入限流配置与该指南给出的取值（指南取 500 mA 档）。

---

## 10. 已核实的源文件清单

下表是本文所有结论的一手来源。**这些文件本身未随本仓库发布**（多为第三方原理图与厂商文档，
存在许可证与体积问题），请按下表的 URL 自行获取后核对。

| 来源 URL | 说明 |
| --- | --- |
| https://github.com/joric/nrfmicro/blob/main/hardware/nrfmicro.kicad_sch | nRFMicro 原理图 |
| https://github.com/GEIGEIGEIST/TOTEM/blob/main/PCB/totem_0-3/totem_0_3.kicad_sch | TOTEM 0.3 原理图 |
| https://github.com/davidphilipbarr/Sweep/blob/main/Sweep%20Mini/sweep-mini.kicad_sch | Sweep Mini 原理图 |
| https://github.com/inpudiy/KOMETA/blob/main/PCB/left.kicad_sch | KOMETA 原理图 |
| https://github.com/Croktopus/zmk-designguide/blob/main/designguide-schematic/designguide-schematic.kicad_sch | ZMK 设计指南原理图（本文信息量最大的一份） |
| https://github.com/Croktopus/zmk-designguide/blob/main/readme.md | 上述指南正文 |
| nice!nano v2 / v1 厂商原理图（1949 / 1831 px） | 厂商发布页（放大逐字读图） |
| https://github.com/zmkfirmware/zmk （`app/src/ext_power_generic.c`、`app/Kconfig`） | ZMK ext-power 实现 |
| https://github.com/zmkfirmware/zmk/tree/main/app/boards | nRFMicro、nice!nano v1/v2、nice!60、BlueMicro840、Puchi BLE、Pillbug、Glove80、ADV360 Pro、polarityworks ckp 各板 devicetree |
| https://docs.splitkb.com/product-guides/aurora-series | build-guide/power-switch、build-guide/per-key-rgb、schematics/aurora-corne 各子页；另含 `aurora_corne_rev1.pdf` |

> 网表还原所用的解析脚本（`kisch.js` 等）为本次调研的一次性工具，**未随仓库发布**。
> 复现方法：`.kicad_sch` 是可读的 S-expression 文本，按 wire / junction / label /
> global_label / power symbol 做并查集即可还原网络，也可直接用 KiCad 打开查看。
