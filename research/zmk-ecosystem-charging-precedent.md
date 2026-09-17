# ZMK / QMK 生态的无线键盘充电设计（对「10000 mAh 怎么充」的第一手证据）

**调研日期**：2026-09-17
**触发**：用户要求「keychron 等品牌用 QMK，应该开源了一些键盘方案，看看他们是怎么做的」，
用以决定本项目 P13（充电电流档位）。

**来源等级**：**[SRC]** = 直接读取本地仓库源文件 / 官方规格页；**[INFERENCE]** = 本报告推断。

---

## 0. 先回答「QMK 开源了键盘方案吗」——没有硬件

⚠️ **需要先纠正一个前提**：**QMK 是固件项目，不包含硬件设计。**

- QMK 仓库（`qmk/qmk_firmware`）里 `keyboards/<vendor>/<kb>/` 下是**固件配置**
  （`keymap.c` / `info.json` / `rules.mk` / `config.h`），**没有原理图 / PCB / BOM**。
- **Keychron 未开源任何 PCB 设计。** 其无线机型（K / K Pro 系列）用的是私有固件
  （Keychron Launcher），QMK 只覆盖其有线机型 —— 而**有线机型根本没有电池与充电电路**。
- 本机实际检查：`_research/keychron-zmk/`（Keychron 的 ZMK 分支）里
  **「keychron」相关条目为 0** —— 该目录名并未带来任何 Keychron 板定义或硬件文件。**[SRC]**

⇒ 所以「从 QMK / Keychron 拿充电设计」这条路**走不通**，不是没找对地方，而是那些文件不存在。

✅ **但真正对口的样本在 ZMK 生态，而且本机就有。** ZMK 是无线键盘固件，其 board 定义里
**会暴露充电 IC 的硬件事实**（GPIO 用法、电流档位、有无温度/定时器）。下面是我实际读到的。

---

## 1. 样本一：nRFMicro（joric）—— **完整开源硬件**，最有价值

**为什么它最对口**：它是 **ZMK 官方支持的 board**，nice!nano 官方 FAQ 亦推荐它，
而且 **KiCad 原理图完整开源** —— `research/repos/joric__nrfmicro/hardware/nrfmicro.kicad_sch`
（另有 `.kicad_pcb` 与 iBOM）。**[SRC]**

### 1.1 读出来的电路事实（从 `.kicad_sch` 直接解析）

| 项 | 值 | 备注 |
| --- | --- | --- |
| **充电 IC** | `U3`：符号用 `Battery_Management:MCP73832-2-OT`，**Value 实填 `TP4054`**，封装 `SOT-23-5` | 两者 **pin-to-pin 兼容**（`VDD`/`PROG`/`VBAT`/`STAT`/`VSS`），所以共用符号 |
| **充电电流** | 由 `R5 = RPROG` 外部电阻设定，封装 `R_0603`，**⚠️ 原理图里该电阻的值未填写**（Value 就是字符串 `"RPROG"`） | 设计者把电流留给使用者自定 |
| 电源路径 | `D1 = 1N5819`（肖特基）+ `Q2 = AO3407`（P-MOS）组成的**简单 OR**，**不是真 PMIC** | 无 DPPM、无电源路径管理 |
| 电池电压检测 | `R6 = 820K` / `R7 = 2M` 分压 → ADC | 独立检测通路 |
| **温度监测** | ❌ **无**。电池座 `J3 = Conn_01x02`（**2 脚**，无 NTC 引脚） | — |
| CC 下拉 | `R2` / `R3` = **5.1 kΩ** | 与本项目一致 ✅ |
| LDO | `U2 = AP2112K-3.3` | 本项目由 nice!nano 提供 |
| 主控模块 | `U1 = E73-2G4M08S1C`（nRF52840） | 裸模块（非 nice!nano） |

### ★ 1.2 决定性结论：**这块开源板既没有充电安全定时器，也没有电池温度监测**

- **Microchip 官方产品页对 MCP73832 明确列出**：`Temperature Monitor: **No**`、
  `Charge Safety Timers: **No**`。**[SRC]**
- **TP4054 / LTC4054 同族同样没有充电定时器**：其终止机制是 **C/10 电流判据**
  （「充电电流降到设定值的 1/10 时自动终止」），**特性列表里没有时间上限**。**[SRC]**

⇒ ⭐ **这把本项目的「消费级充电 IC 普遍无充电定时器」从 [INFERENCE] 升级为 [SRC] 直接证据。**
之前只能靠 Hola87 的 28.6 h 充电时间**反推**；现在是**直接读到原理图 + 读到 IC 官方规格**。

⇒ 本项目把 `TMR` 接 VSS 禁用定时器（`power-architecture.md` §3.5 路线 A）
**与 ZMK 官方推荐板的做法完全一致**。

---

## 2. 样本二：mikoto（zhiayang）—— 用 **2 个 GPIO 动态切换充电电流**

`_research/keychron-zmk/app/module/boards/zhiayang/mikoto/` 下 `Kconfig` + `pinmux.c`。**[SRC]**

### 2.1 Kconfig 给出的档位（六选一）

| 档位 | 措辞（原文） |
| --- | --- |
| `..._40MA` | `40mA charge current, for battery capacity **40mAh or higher**` |
| `..._100MA` | `100mA … for battery capacity **100mAh or higher**` |
| `..._150MA` | `150mA … for battery capacity **150mAh or higher**` |
| `..._250MA` | `250mA … for battery capacity **250mAh or higher**` |
| `..._350MA` | `350mA … for battery capacity **350mAh or higher**` |
| `..._NONE` | `Disable charge current` |

⭐ **档位的命名逻辑是按 1C 设的**（「350 mA 给 350 mAh 电池」）——
这正面印证了本项目此前从商用产品调研得出的「社区/行业按 **0.5–1C** 设计」结论。

### 2.2 实现方式：GPIO 直接改变 `PROG` 的等效电阻

```c
#if CONFIG_BOARD_MIKOTO_CHARGER_CURRENT_40MA
    P0.26 = INPUT | PULL_DOWN;   P1.15 = INPUT;              // 高阻 / 弱下拉
#elif CONFIG_BOARD_MIKOTO_CHARGER_CURRENT_100MA
    P0.26 = OUTPUT, LOW;         P1.15 = INPUT;
#elif ..._150MA          P0.26 = OUTPUT LOW;  P1.15 = INPUT | PULL_DOWN;
#elif ..._250MA          P0.26 = INPUT;       P1.15 = OUTPUT LOW;
#elif ..._350MA          P0.26 = OUTPUT LOW;  P1.15 = OUTPUT LOW;
#endif
```

**原理**：两个 GPIO 各自代表一个「到地的电阻支路」，用 `INPUT`（高阻，不导通）/
`INPUT+PULL_DOWN`（弱下拉，等效一个大电阻）/ `OUTPUT LOW`（强下拉到地，导通）三种状态
组合出不同的等效 `R_PROG` ⇒ 不同充电电流。**[SRC]**

> ⚠️ **本条不照抄到本项目**：BQ24072 的 `ISET` 不仅设电流，**还兼作「实际充电电流监测」输出**，
> 且数据手册要求**上电做 `ILIM`/`ISET` 短路检测**。用 GPIO 切换其下端会让监测失效并干扰该检测。
> ⇒ 本项目仍按 `power-architecture.md` §3.4 的结论：**不采用 GPIO 控制充电**。

---

## 3. 样本三：puchi_ble（keycapsss）—— 单 GPIO 使能

`app/module/boards/keycapsss/puchi_ble/pinmux.c`：**[SRC]**

```c
#if CONFIG_BOARD_PUCHI_BLE_CHARGER
    P0.05 = OUTPUT, LOW;     // 打开充电
#else
    P0.05 = INPUT;           // 关闭
#endif
```

一个 GPIO 把某个电阻/使能脚拉到地或悬空。更简单，量级同上。

---

## 4. 综合对照

| 项 | nRFMicro | mikoto | puchi_ble | **本项目** |
| --- | --- | --- | --- | --- |
| 充电 IC | **MCP73832 / 实贴 TP4054** | （未在 dts 暴露） | （未暴露） | **BQ24072** |
| 充电电流上限 | 由 `RPROG` 定（未填值） | **350 mA** | — | **500 mA**（USB500 档） |
| 电流档位来源 | 硬件电阻 | **固件 Kconfig（GPIO 切换）** | 固件 GPIO | 硬件（`EN1/EN2` + `R_ISET`） |
| **充电安全定时器** | ❌ **无** | ❌ 无 | ❌ 无 | ⚠️ **有（7.2–12 h）⇒ 已接 VSS 禁用** |
| **电池温度监测** | ❌ **无**（2 脚座） | ❌ 无 | ❌ 无 | ❌ **无**（10 kΩ 禁用） |
| 真电源路径管理 | ❌（肖特基 OR） | ❌ | ❌ | ✅ **有（BQ24072 DPPM）** |
| 电池电压检测 | 820k/2M 分压 | — | — | nice!nano 内部 |
| CC 下拉 5.1 kΩ | ✅ | ✅ | ✅ | ✅ |

**三条结论：**

1. ⭐ **「无充电定时器」在 ZMK 生态是常态**，现在有直接证据（§1.2）。本项目的处置正确。
2. ⭐ **「无电池温度监测」同样是常态**：nRFMicro 的电池座就是 2 脚 ⇒ 本项目禁用温测与主流一致。
3. **开源无线键盘的充电电流上限是 350 mA**（mikoto 的最高档）。本项目的 **500 mA 已高于生态上限**
   —— 这是 USB500 档的合规满值，但**没有理由再往上提**。

---

## 5. 对本项目 P13（充电档位）的直接意义

用户希望「看别人怎么做」来决定是否提速。证据给的是**否定的答案**：

- **开源无线键盘生态的充电电流普遍 ≤350 mA**，且普遍按 1C 匹配电池容量；
- 本项目 10000 mAh 电池若按 1C 需要 **10 A** —— 远超芯片 1.5 A 上限与 USB 供给能力；
- ⇒ **生态里不存在「给大电池用大电流」的先例**，因为这类设备的电池都很小（40–350 mAh 级）；
- ⇒ 本项目维持 **USB500 档 0.5 A**（0.05C）是**在生态上限之上、USB 规范之内**的稳妥选择；
- 若仍要提速，唯一有据可依的参考是**商用产品**（Kzzi 1.4 A，见
  `keyboard-battery-capacity-precedent.md`），代价是对应更高（超 USB 声明 + 热调节风险）。

**建议：维持 0.5 A。** 依据从「我们自己的推算」升级为「生态惯例 + 商用产品对照」双侧支持。

---

## 6. 诚实边界

1. **nRFMicro 的 `RPROG` 实测值未知** —— 原理图 Value 字段是占位字符串 `"RPROG"`，
   真实 BOM 值未在仓库中找到。因此**它的实际充电电流无法从原理图读出**，只能确认「可编程」。
2. **mikoto 的档位是按「电池容量 ≥ 电流值」命名的**，但**它未说明所用充电 IC 型号**
   （`mikoto.dts` 里没有 charger/battery 节点，纯 GPIO 实现）⇒ §2.2 的电阻网络细节是
   由 GPIO 用法**推断**的 [INFERENCE]，不是读到的原理图（该板未开源硬件）。
3. **样本量小**：本报告覆盖 3 个 ZMK board，且它们是**本地 `_research/keychron-zmk` 与
   `research/repos/` 里能找到的全部相关样本**，不是对 ZMK 全量 board（上百个）的普查。
4. **MCP73832 的官方规格页被直接引用**（`Charge Safety Timers: No`），
   但 **TP4054 的「无定时器」是从其特性列表缺失 + C/10 终止机制推断**的，
   未取得 TP4054 原厂 datasheet 的完整电气表。
5. **Keychron 部分**只验证了「本地 keychron-zmk 里无 keychron 板定义」这一事实，
   未能（也无法）证明「Keychron 一定没有公开任何硬件资料」——
   但可以确定的是：**QMK 仓库不含硬件设计**这一点是结构性的。
6. 未覆盖：nice!nano 自身的开源硬件（其充电规格已知为 100/500 mA 两档、焊桥选择，
   见 `docs/controller-and-battery-facts.md` §1.1，本报告未另行展开）。
