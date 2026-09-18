# 95 键矩阵采用 74HC595 移位寄存器驱动列

## 背景

95 键矩阵按常规做法需要 **6 行 + 18 列 = 24 个 GPIO**。
但从 ZMK 官方仓库 `app/module/boards/nicekeyboards/nice_nano/arduino_pro_micro_pins.dtsi`
解析 `pro_micro` 连接器后确认：**nice!nano v2 的 2×12 排针实际只引出 18 个 GPIO**
（官方口径的 21 GPIO 中有 3 个不在排针上）。

扣掉 RGB 数据线与 RGB 电源门控后，可用于矩阵的约 **16 个** —— **24 引脚直连不可行**。

## 考虑过的替代方案

1. **折叠矩阵**（用更多逻辑行换更少列）：已实测求解，最少可降到 **20 引脚**
   （8 行 × 12 列，20 即数学下界）。但 20 > 可用约 16，**仍不足**；
   且逻辑行多于物理行会让走线复杂度大增（列线串键数 +49%、行线需在键间反复跳），
   对「新手可复刻」的目标不利。**否决。**
2. **改用 GPIO 更多的控制器**：与 ADR-0003（双控制器兼容）冲突，且 Zephyr 下选择有限。**否决。**
3. **拆成两块控制器**：等同分体键盘，成本翻倍、双无线。**否决。**
4. **硬压列数**：18 列是数学下界（单行最多 18 键，同行 18 键必分属 18 列），压不下去。**不可行。**
5. **改用 ZMK 官方支持的 nRFMicro**：可行备选，但它放弃 SuperMini 低成本路线，且不解决本项目实际问题。
6. **Charlieplex（查理复用）**：ZMK 有 `zmk,kscan-gpio-charlieplex` 驱动，
   n 脚可驱动 n(n−1) 键，引脚数看着够（12 脚 + 1 中断脚 → 110 键）。
   ❌ **但因功耗否决**：中断模式下驱动会把**全部输出置为有效**（源码
   `kscan_charlieplex_set_all_outputs(dev, 1)`），静息时持续有电流经二极管流到
   带 `GPIO_PULL_DOWN` 的中断脚 ⇒ 约 0.33 mA（10 kΩ 下拉），**超过本项目约 20 µA 的待机预算 16 倍**。
   且 ZMK 生态里**没有任何一块板实际使用 charlieplex**。
   详见 `docs/zmk-kscan-alternatives.md` §2。
7. **Direct / Demux / Composite**：Direct 需 95 脚；Demux 同样要额外 IC 且更冷门；
   Composite 组合多个矩阵**不会减少总引脚数**。均否决。
   详见 `docs/zmk-kscan-alternatives.md` §3。

> ✅ **已穷举 ZMK 全部 6 个 keyscan 驱动**（Matrix / Direct / Demux / Charlieplex /
> Composite / Mock），无一能替代本方案。完整排查见 **`docs/zmk-kscan-alternatives.md`**。

## 决策

采用 **2 颗 74HC595 级联驱动 18 个列**，6 个行直连 MCU。
⚠️ **颗数已于 2026-09-18 修订为 3 颗**（文末修订小节）—— 2 颗是电气错误，机制与接线规则不变。

**关键依据**：ZMK **官方已内置** 74HC595 驱动并附官方文档
（`app/module/drivers/gpio/gpio_595.c`、`compatible = "zmk,gpio-595"`、
`docs/docs/hardware-integration/shift-registers.md`），因此**零自写代码**。
官方文档原文称移位寄存器是：

> "**the recommended method** of adding additional GPIO pins to MCUs and boards,
> **when a standard matrix results in an insufficient number of keys**."

## 接线规则（官方硬性要求）

> "The shift register output pins **should act as MCU outputs** in your design.
> **All MCU inputs should remain connected directly to MCU/board pins.** This is to allow
> the inputs to trigger **"interrupts"**."

⇒ `col2row` 二极管矩阵下：**列 = MCU 输出 → 走 595**；**行 = MCU 输入 → 必须直连 MCU**。

⚠️ `ngpios` 只能取 **8 / 16 / 24 / 32** ⇒ 18 列需 2 颗级联、取 **24**（官方最多支持级联 4 颗）。
⚠️ **本句的「2 颗」已被修订推翻**：18 列需 **3 颗**（24 位链、用前 18 位），见文末修订小节。

## 引脚分配

| 用途 | 引脚 | 说明 |
| --- | --- | --- |
| 矩阵行 R0–R5 | Pro Micro **D4 / D5 / D6 / D7 / D9 / D8** | 直连 MCU（官方要求） |
| 595 SPI：MOSI | **P0.10**（D16） | `&spi1` 的 MOSI |
| 595 SPI：SCK | **P1.13**（D15） | `&spi1` 的 SCK |
| 595 片选（RCLK） | **P0.02**（D19/A1） | `cs-gpios` |
| WS2812 数据 | **P0.06**（D1） | `&spi3` 的 MOSI（ZMK 官方对 nRF52 的推荐做法） |
| RGB 电源门控 | **P0.09**（D10/A10） | `EXT_POWER` 的 `control-gpios` |
| **小计** | **11 / 18** | **余量 7 个** |

⚠️ **595 与 WS2812 必须用不同的 SPI 外设**（两者都是 SPI 从设备）：
595 用 `&spi1`，WS2812 用 `&spi3`。

## 影响

**收益**
- 保住 6×18 整齐矩阵，走线规整、可复制粘贴，对新手友好
- 引脚余量 7 个，可留作扩展
- **固件零自写代码**（官方驱动 + 官方文档）
- 成本增加极小：2 颗 SOP-16，约 0.3 元/颗，另有官方称「very low power consumption」

**代价**
- PCB 增加 2 颗 IC 与每颗一颗 100 nF 去耦电容，约 10×6 mm 面积
- 列的 18 根线集中到 595 输出后需要额外布线到 595 位置

**已产出**
- `firmware/boards/shields/starshield/starshield.overlay`（kscan / 595 / WS2812 / ext-power）
- `firmware/boards/shields/starshield/starshield_transform.dtsi`（95 键映射表，由脚本生成）
- 生成脚本 `docs/_tools/gen_transform.mjs`

## 勘误

本 ADR 立项前，`docs/matrix-assignment.md` 曾写「ZMK 无内置支持，需自写移位寄存器扫描驱动」，
**该说法是错的**（见上）。方案 A 的主要风险因此不存在，故由「倾向」升级为「采用」。

## 修订（2026-09-18，B2 画控制板子图时发现）：2 颗 → **3 颗**

**「2 颗 74HC595 驱动 18 列」在电气上不成立**，原理图落地（B2）时被证实并修正：

1. 2 颗 595 只有 **16 个物理输出位**，而矩阵有 **18 列** —— 差 2 位，不是「空闲位」能解决的结构性缺口；
2. overlay 原注释声称「ngpios=24 ⇒ 16..23 为第二颗的空闲输出」是**错的**：
   `ngpios=24` 会让驱动每轮移 **24 个时钟**（`gpio_595.c`：`nwrite = ngpios/8`），
   第 17~24 个移入的位把链上最早的数据**推出第二颗的 QH' 丢弃**
   ⇒ `&shifter 16/17`（COL16/17，小键盘区 5 键）**永远无法驱动**；
   且 CI 构建照常通过 —— 这是「编译通过 ≠ 配置正确」的又一实例（教训 10.2-7 的电气版）；
3. **位序核实**（`gpio_595.c`：`sys_cpu_to_be32` + `SPI_TRANSFER_MSB`，先移出的位最终在链尾）：
   **bit 0..7 = 第 1 颗 QA..QH；bit 8..15 = 第 2 颗；bit 16..17 = 第 3 颗 QA/QB；bit 18..23 空闲**。
   overlay 的 `col-gpios` 引用与原理图接线即按此定义。

**修订后**：3 颗 74HC595（SOP-16）级联，`ngpios = <24>` 不变；
原理图 `hardware/pcb/StarShield/control/control.kicad_sch`（由 `control_design.py` 生成）；
校验 `docs/_tools/verify_control.py`（含级联链/位序/跨图接口断言）。
overlay 注释与 `firmware/README.md` 已同步（`ngpios` 数值本身不变，固件无需重验）。

## 待办

- ⚠️ 引脚分配已在 DTS 层自洽，但 **nice!nano 的排针 pitch / 每边脚数未能从官方数字确认**
  （仅有 Pro Micro 标准旁证）→ **投板前必须用实物核对**
- 需补写 `keymap` 与构建配置（`build.yaml` / `*.conf`），并跑一次 GitHub Actions 构建验证
