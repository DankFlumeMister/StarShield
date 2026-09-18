# 矩阵折叠分析与引脚预算（已实测）

本文件回答三个问题：

1. **矩阵能否折叠**（用更多逻辑行换更少列，从而减少 GPIO）？ → ✅ 能，最多省 4 个引脚（24 → 20）。
2. **折叠后能否直连 nice!nano v2**？ → ❌ **不能**（20 > 实测可用的约 16）。
3. **那矩阵问题怎么解决**？ → ✅ **74HC595，且 ZMK 官方原生支持**（见第 4 节，**已定稿**）。

状态：✅ **矩阵引脚问题已解决**（结论见第 4 节）。脚本可复现：`docs/_tools/fold-matrix.mjs`

> ⚠️ **本文件第 4 节更正了一个我先前的错误结论**：我曾写「ZMK 无内置支持，需自写移位寄存器驱动」，
> 实际 ZMK **官方已内置 74HC595 驱动并附官方文档**。详见 §4.1。

---

## 1. 折叠的电气模型（关键，前几版分析都错在模型上）

**矩阵列 = 物理 x 槽位**（开关中心 X 坐标）。两把键可以共用一根列线，**当且仅当它们不在同一逻辑行**。

⇒ **同一逻辑行内，所有键的物理 x 槽位必须互不相同。**

由此区分两个此前被混为一谈的概念：

| 概念 | 含义 | 本项目 |
| --- | --- | --- |
| **物理行** | 键在键盘上排成的一横排 | **6 行**（固定，由布局决定） |
| **逻辑行**（矩阵行） | 我们指派给键的矩阵行号 | **可自由选择**，不必等于物理行 |

> ⚠️ **「同一逻辑行」与「同一物理行」不是一回事。** 这是折叠的全部空间所在：
> 把同一个物理行里的键**拆到多个逻辑行**，就换来更少的列。
> 反过来，同一个物理列上的多把键必须分到**不同**逻辑行（否则同格短路）。

**可行性判据**：方案 (R 逻辑行, C 列) 可行 ⟺ 能把 95 键分成 R 组，每组 ≤ C 键，且组内 x 槽位互异。

### 1.1 硬下界

| 下界 | 来源 | 值 |
| --- | --- | --- |
| R ≥ 5 | 同一 x 槽位上最多有 **5** 把键（实测：x 槽位重数分布为 1把×48、2把×10、3把×3、4把×2、**5把×2**） | R ≥ 5 |
| C ≥ ⌈95/R⌉ | 矩阵格数 R·C 必须 ≥ 95 | 随 R 变化 |

⇒ R=5 时 C ≥ 19 → **24 引脚**（这就是当前方案的引脚数下限来源）

---

## 2. 实测结果（`fold-matrix.mjs`，含独立验证）

脚本对每个 R 求最小可行 C，并**独立复核**「无格冲突、无行超载」。

| 方案 | 引脚 | 逻辑行 | 列 | 利用率 | 相对当前 |
| --- | --- | --- | --- | --- | --- |
| **当前（已实现，网表已校验）** | **24** | 6 | 18 | 88.0% | — |
| 6 行 × 16 列 | 22 | 6 | 16 | 99.0% | 省 2 |
| **7 行 × 14 列** | **21** | 7 | 14 | 96.9% | 省 3 |
| **8 行 × 12 列** | **20** | 8 | 12 | 99.0% | 省 4 |
| 9 行 × 11 列 | 20 | 9 | 11 | 96.0% | 省 4 |
| 10 行 × 10 列 | 20 | 10 | 10 | 95.0% | 省 4 |
| 11 行 × 9 列 | 20 | 11 | 9 | 96.0% | 省 4 |
| 12 行 × 8 列 | 20 | 12 | 8 | 99.0% | 省 4 |

**✅ 结论：折叠可行，最少 20 引脚（比当前方案省 4 个）。**

---

## 3. ❌ 但折叠**不足以**直连 nice!nano v2

这是本节最重要的结论。20 引脚 **看起来** 小于 nice!nano 官方的 21 GPIO，但实际不可行。

### 3.1 实际可用的排针引脚只有 18 个（实测）

从 **ZMK 官方仓库** `app/boards/arm/nice_nano/arduino_pro_micro_pins.dtsi`（v0.3 分支）解析
`pro_micro` 连接器的 gpio-map，去重后得到**实际引出到 Pro Micro 排针的引脚**：

| Pro Micro 标号 | GPIO | | Pro Micro 标号 | GPIO |
| --- | --- | --- | --- | --- |
| D0 | P0.8 | | D10/A10 | P0.9 |
| D1 | P0.6 | | D14 | P1.11 |
| D2 | P0.17 | | D15 | P1.13 |
| D3 | P0.20 | | D16 | P0.10 |
| D4/A6 | P0.22 | | D18/A0 | P1.15 |
| D5 | P0.24 | | D19/A1 | P0.2 |
| D6/A7 | P1.0 | | D20/A2 | P0.29 |
| D7 | P0.11 | | D21/A3 | P0.31 |
| D8/A8 | P1.4 | | | |
| D9/A9 | P1.6 | | | |

**⇒ 排针实际引出 18 个 GPIO。**

> ⚠️ **18 与官方「21 GPIO」的差异需要解释**：nicekeyboards 官方原文为
> 「3 extra GPIO pins offering a total of 21 GPIO pins」，即**另外 3 个 GPIO 不在这 2×12 排针上**
> （官网页脚图为图片，无法用文本方式进一步确认其位置）。
> 因此 **仅靠排针/插座可安全使用的引脚是 18 个**；要用到那 3 个需要额外焊接，不适合新手复刻。

### 3.2 18 个引脚里还有必须让出的

| 用途 | 引脚 | 依据 | 是否可省 |
| --- | --- | --- | --- |
| 电池电压 ADC | P0.04（AIN2） | 官方：「不能作其他用途」 | ❌ 不可省（但**不在排针上**，见下） |
| ZMK 串口/日志 UART | P0.8 (RX) / P0.6 (TX) | `nice_nano-pinctrl.dtsi` | ✅ 可省（禁掉串口） |
| I2C（屏幕等） | P0.17 (SDA) / P0.20 (SCL) | 同上 | ✅ 可省（第一版不装屏幕） |
| SPI（RGB 数据常用） | P1.13 (SCK) / P0.10 (MOSI) / P1.11 (MISO) | 同上 | 🟡 若用 SPI 驱动 LED，需留 1 个（MOSI） |
| RGB 数据线 | 任意 1 个 GPIO | 设计需要 | ❌ 不可省 |
| RGB 电源门控 | 任意 1 个 GPIO（或直接用 P0.13 控 VCC） | ADR-0005 | ❌ 不可省 |

### 3.3 引脚预算结论

```text
排针可用 GPIO                     18
减：RGB 数据线                    −1   → 17
减：RGB 电源门控                  −1   → 16
（串口、I2C 全部禁用来腾引脚）
                                  ────
可用于矩阵的引脚                  ≈ 16

折叠后矩阵最少需要                  20
                                  ────
缺口                               −4  ❌ 仍不够
```

**⇒ 即使把矩阵折叠到最优的 20 引脚，nice!nano v2 的排针也接不下（可用约 16）。**

### 3.4 结论

| 方案 | 能否在 18 引脚内实现 95 键 |
| --- | --- |
| 6×18 直连（24 引脚） | ❌ 差 8 |
| 折叠到 20 引脚 直连 | ❌ 差 4 |
| 折叠到 16 引脚 直连 | 数学下界就是 20（R=5 时 C≥19），**不可能** |
| **6×18 + 74HC595 移位寄存器** | ✅ **可行**（矩阵占 6 行引脚 + 3 个移位寄存器控制脚 = 9，余量充足） |

**⇒ 74HC595（或同类移位寄存器）不是「过度设计」，而是本项目的必要方案。**

---

## 4. ✅ 最终结论：74HC595，而且 **ZMK 官方原生支持**

### 4.1 关键更正：ZMK **已内置** 74HC595 驱动（不是我先前说的「需自写」）

⚠️ 我此前在 `docs/matrix-assignment.md` 里写「ZMK 无内置支持，需自写移位寄存器扫描驱动」——
**这是错的**。核实 ZMK 官方仓库后确认：

| 官方资源 | 路径 | 说明 |
| --- | --- | --- |
| 驱动源码 | `app/module/drivers/gpio/gpio_595.c` | 官方维护 |
| Kconfig | `app/module/drivers/gpio/Kconfig.595` | `GPIO_595`，依 `zmk,gpio-595` 兼容项自动启用 |
| 设备树绑定 | `app/module/dts/bindings/gpio/zmk,gpio-595.yaml` | `ngpios` 必须是 **8 / 16 / 24 / 32** |
| **官方文档** | `docs/docs/hardware-integration/shift-registers.md` | 标题即「Configuring Shift Registers」 |

**官方文档原文**（重要，逐句对照）：

> 「Shift registers are **the recommended method** of adding additional GPIO pins to MCUs and boards,
> **when a standard matrix results in an insufficient number of keys**. They are recommended because
> they simultaneously have **very low power consumption** and are quite cheap.」
>
> 「The shift register output pins **should act as MCU outputs** in your design. **All MCU inputs should
> remain connected directly to MCU/board pins.** This is to allow the inputs to trigger **"interrupts"**
> on the MCU, upon which it will begin scanning the keys.」
>
> 「You most likely will need to **rearrange your matrix to maximize the use of shift register output pins**,
> in order to reduce the total number of GPIO pins connected to the MCU. For example, a **9 column 5 row**
> `col2row` matrix could be rearranged to use **16 columns and 3 rows**.」
>
> 「ZMK allows you to **daisy-chain up to four** shift registers.」

### 4.2 据此，本项目的矩阵方案（已可定稿）

官方规则：**移位寄存器只能当「输出」，MCU 的输入脚必须直连**。
在 `col2row` 二极管矩阵中，**列 = MCU 输出**（接二极管阳极），**行 = MCU 输入**。

⇒ **把 18 个列放到移位寄存器，6 个行直连 MCU。** 我们现有的 6×18 分配**不需要改动**。

```text
star_shield.overlay（示意，最终版待写）

&spi1 {
    status = "okay";
    cs-gpios = <&pro_micro 16 GPIO_ACTIVE_LOW>;   /* 片选，任选一个空闲脚 */
    shifter: sr595@0 {
        compatible = "zmk,gpio-595";
        status = "okay";
        gpio-controller;
        spi-max-frequency = <200000>;
        reg = <0>;
        #gpio-cells = <2>;
        ngpios = <24>;        /* 2 颗 74HC595 级联 = 16 位；取 24 亦可（见下） */
    };
};

kscan0: kscan_0 {
    compatible = "zmk,kscan-gpio-matrix";
    diode-direction = "col2row";
    /* 6 个行：直连 MCU（输入，可触发中断） */
    row-gpios = <&pro_micro 4 GPIO_ACTIVE_HIGH>, ... ;   /* 6 个 */
    /* 18 个列：全部走移位寄存器输出 */
    col-gpios = <&shifter 0 GPIO_ACTIVE_HIGH>, ... ;     /* 18 个 */
};
```

⚠️ **`ngpios` 只能取 8 / 16 / 24 / 32**（绑定里是 enum）。
18 列需要 **至少 24**（或 16 不够用）⇒ **用 2 颗 74HC595 级联、`ngpios = <24>`**。
同理若采用折叠后的 16 列方案，2 颗级联 `ngpios = <16>` 即可。

> ⚠️ **2026-09-18 修订**：本节「2 颗」的推算有电气错误 —— 2 颗只有 16 个输出位，
> `ngpios=24` 时 bit16/17 会被推出链尾丢失。18 列需 **3 颗**。
> 完整论证见 **`docs/adr/0008` 修订小节**（此处保留原文作历史记录）。

### 4.3 引脚预算（用实测的 18 个排针引脚）

| 用途 | 引脚数 | 是否直连 MCU |
| --- | --- | --- |
| 矩阵 6 行 | 6 | ✅ 直连（官方要求输入直连） |
| 74HC595 的 SPI：MOSI / SCK / CS | 3 | ✅ 直连 |
| RGB 数据线 | 1 | ✅ 直连 |
| RGB 电源门控 | 1 | ✅ 直连 |
| **小计** | **11** | |
| **排针可用（实测）** | **18** | |
| **余量** | **7** | 可留作电池 ADC、软关机唤醒脚、扩展 |

✅ **引脚充足，方案成立。** 这也从正面回答了「为什么折叠矩阵不是必须的」——
走 595 路线后引脚有余量，没必要为了省 4 个引脚去牺牲走线整齐度。

### 4.4 代价（如实记录）

| 项 | 内容 |
| --- | --- |
| 元件 | **2 颗 74HC595**（SOP-16，约 0.3 元/颗）+ 每颗一颗 100 nF 去耦 —— ⚠️ 已修订为 **3 颗**（ADR-0008 修订小节） |
| 引脚 | 3 个（MOSI/SCK/CS） |
| 固件 | ✅ **零自写代码**：官方驱动 + 官方文档，devicetree 配置即可 |
| 功耗 | 官方称「very low power consumption」 |
| 占用 | SOP-16 封装，2 颗约 10×6 mm 面积 |
| 走线 | 列的 18 根线集中到 595 输出，**比折叠方案规整得多** |

---

## 5. 参考基线 Apollo87H 的矩阵（实测，用于对照）

顺带解析了 Apollo87H 的矩阵网络，作为「同规模键盘」的对照数据：

| 项目 | Apollo87H 实测 |
| --- | --- |
| 矩阵网络 | **`R0`–`R5` × `C0`–`C16`** |
| 矩阵规模 | **6 行 × 17 列 = 102 格** |
| 键数 | 87（利用率 **85.3%**） |
| 所需 GPIO | **23**（6 + 17） |
| 控制器 | **STM32 系列**（网络名含 `E_PA14`/`E_PB13`/`E_PC10`/`PB2{slash}BOOT1`/`PA9`） |
| 模块接口 | `PinHeader_1x16_P2.54mm`（**16 针模块位**） |
| LED 供电 | 87 颗 SK6812MINI 全部接 `5V`（来自 USB VBUS） |

⚠️ **对照结论**：Apollo87H **不是**无线电池键盘，而是**有线 USB 供电的 STM32 板**，
通过 16 针模块位获得充足 GPIO，**根本没有引脚压力**，因此它用最朴素的
「6×17 直连矩阵 + 5V 直供 LED」就完事了。

⇒ **它的做法对本项目没有参考价值**（这正是我之前误以为它是无线键盘的地方）。
本项目受 nice!nano 排针 18 引脚的硬约束，必须走 595 路线。

## 6. 复现方法

```powershell
cd <仓库根目录>
node docs\_tools\fold-matrix.mjs                    # 折叠分析
node docs\_tools\scan-zmk-repos.mjs                 # 枚举 ZMK 官方仓库结构（脚本自行联网拉取，不入库）
```
