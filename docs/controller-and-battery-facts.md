# 控制器与电池事实（已核实）

本文件汇总影响硬件决策的**已核实事实**，来源为一手资料（厂商官方页、官方仓库、JST/TI 文档）。
**未核实项一律标注 `❓ UNVERIFIED`，不得当作数据使用。**

状态：🟡 部分完成（关键项已核实；TS 引脚参数等硬阻塞项待人工查 TI 文档）

> 完整调研过程与逐条来源见 `research/starshield-hardware-facts.md` 与
> `research/lipo-3000mah-dimensions-report.md`（含全部候选清单与 UNVERIFIED 清单）。

---

## 1. 控制器 GPIO 预算 —— 本项目的硬约束

### 1.1 实测/官方数据

| 项目 | nice!nano v2 | SuperMini nRF52840 |
| --- | --- | --- |
| **GPIO 总数** | **21 个** ✅ 官方措辞：「3 extra GPIO pins offering a total of 21 GPIO pins」（另 3 个不占 2×12 主排针） | ❓ UNVERIFIED（无官方 datasheet） |
| 主排针布局 | 2×12 @ 2.54mm、列距 15.24mm（旁证已升级：marbastlib 社区封装 + 零售商「2x 12-pin headers」双重一致，2026-09-19；**仍待 B6 实物卡尺定案**，清单见 `nice-nano-physical-verification.md`） | 同（旁证） |
| 板厚 | **3.2 mm**（mid-mount USB-C） | ❓ UNVERIFIED |
| 电池电压 ADC | **P0.04 (AIN2)**，官方明确「不能作其他用途」 | **P0.24**（原理图错标为 P0.04） |
| VCC 门控 | **P0.13 置高可切断 VCC**（官方说明用于省掉 LED 静态功耗） | 存在 NPQ2/NBD1/NPR7 电源路径电路 |
| 休眠电流 | **18 µA**（quiescent 15 µA + 3 µA，ZMK 官方用 Nordic Power Profiler Kit 实测） | 批次差异极大：好板 **4 µA**，差板 **60 µA** |
| 板载充电 | 有，两档：约 100 mA / 约 500 mA（焊 boost 跳线）。官方建议电池 ≤2000mAh | 有，充电电流 ❓ UNVERIFIED |
| ZMK 官方支持 | ✅ 支持。**board id 随分支不同**：`main` 用 `nice_nano//zmk`；`v0.3` 用 `nice_nano_v2` | ❌ **ZMK 官方零支持**（穷举 `app/boards/` 无 ebyte/supermini/e73） |

### 1.2 ⚠️ 结论：矩阵无法直连，且**折叠矩阵也救不回来**

矩阵需要 **24 个 GPIO**（见 `docs/matrix-assignment.md`）。

**关键修正**：nice!nano v2 官方口径的 21 GPIO 里，**实际引出到 2×12 排针的只有 18 个**。
从 **ZMK 官方 v0.3 分支** `app/boards/arm/nice_nano/arduino_pro_micro_pins.dtsi`
解析 `pro_micro` 连接器的 gpio-map 并去重，得到排针引脚（Pro Micro 标号 → GPIO）：

`D0→P0.8  D1→P0.6  D2→P0.17  D3→P0.20  D4→P0.22  D5→P0.24  D6→P1.0  D7→P0.11
 D8→P1.4  D9→P1.6  D10→P0.9  D14→P1.11  D15→P1.13  D16→P0.10  D18→P1.15  D19→P0.2
 D20→P0.29  D21→P0.31`
（编号 D11/D12/D13/D17 空缺）

**⇒ 排针 18 个 GPIO**；扣掉 RGB 数据线与 RGB 电源门控后，**可用于矩阵的约 16 个**。

**并且已专门验证「折叠矩阵」这条退路**（完整分析见 `docs/matrix-folding-analysis.md`）：

| 方案 | 引脚 | 结果 |
| --- | --- | --- |
| 当前 6 行 × 18 列 | 24 | 已实现、网表已校验 |
| 折叠到 8 行 × 12 列（数学最优） | **20** | ✅ 电气可行，但 |
| 可用引脚（18 排针 − RGB 2 个） | 约 16 | ❌ **20 > 16，仍不足** |

**⇒ 移位寄存器（74HC595 等）是本项目的必要方案，不是过度设计。**

### 1.3 SuperMini 的双重问题（不只是引脚）

1. **ZMK 官方不支持** → 需自行维护 board 定义（`zmk keyboard new` 或 zmk module），
   与「新手可复刻」「上游 ZMK」的目标冲突。
2. **ZMK 官方支持的 nRFMicro（joric/nrfmicro）是正规替代品** —— 它在 ZMK 官方仓库内有第一方
   board 定义（`app/boards/joric/nrfmicro/`），nice!nano 官方 FAQ 亦推荐它。
   ⚠️ 「能刷 nice!nano 固件」≠「被 ZMK 支持」：克隆板实测待机 1.40–1.90 mA。
3. **共享 footprint 的三个真实差异**：
   - ① 引脚数 21 vs 18，额外脚不占主排针；
   - ② **电池 ADC 脚不同**（P0.04 vs P0.24）→ 同一根走线无法同时正确读取两者电量，需 **0Ω 跳线**二选一；
   - ③ 板厚/外形差异未验证，共享插座有机械干涉风险。
   （此差异需更新 ADR-0003。）

---

## 2. 电池

### 2.1 关键结论：3000mAh 的厚度与占位面积可互换

> 🔴 **2026-09-17 更新：容量已改为 2×5000 mAh 并联（10000 mAh）。**
> 本节关于「3000 mAh」的厚度谱**保留作历史记录**；下方「推荐 605080 路线 / 电池仓
> 6.5 × 51 × 84 mm / 机壳深度 ≥8.5–9 mm」**已作废**。新规格与采购要求见
> `docs/power-architecture.md` **§3.5 / §3.6**，要点：
> - 单块 5000 mAh 参考规格 **`LP955465` = 9.5 × 54 × 66 mm、100 g、18.5 Wh**，自带 PCM + JST PHR-2
> - 两块**并排**总占位约 **10.5 × 110 × 68 mm** ⇒ **机壳深度由 ≥8.5–9 mm 改为 ≥11 mm**
> - ⚠️ 必须买**一体化 1S2P 单 PCM 包**；两块各自带保护板的电芯直接并联会出问题（互充 + 阈值失配）
> - ⚠️ nice!nano 官方「建议电池 ≤2000mAh」**不适用于本设计** —— 那是针对它**板载**充电器
>   （100 / 500 mA）的建议；本项目用自画的 BQ24072，该限制不成立

任务假设「3000mAh 有一个典型厚度」是**不成立**的。实测/官方数据显示：

| 厚度路线 | 占位面积 | 实例 |
| --- | --- | --- |
| **6.0 mm** | 约 4100 mm²（50.5 × 82.5） | VCELL `VP605080`（含保护板，6.2 × 50.5 × 82.5） |
| **8.5–9.8 mm** | 2400–3900 mm² | Blumoti `BMP` 系列约 15 个型号；**9 mm 是紧凑外形下的众数** |
| **10 mm** | 约 2340 mm²（36 × 65） | Tcbest / AFTERTECH `103665` |
| 13 mm ❌ | — | 2 × 1500mAh 叠层，不建议 |

- **任何路线都做不到 5 mm。**
- **推荐 605080 路线**（键盘横向空间比深度好找）：电池仓开槽约 **6.5 × 51 × 84 mm**，
  **机壳深度 ≥ 8.5–9 mm**。若用 40 × 65 紧凑电芯则深度需 ≥ 11 mm。
- ⚠️ **型号数字是标称最小值，实物更大**：Jauch `LP103450JH` 型号写 10、实测 **10.8 mm**；
  保护板使总长 **+1~2 mm**。**所有厚度均为厂商标称，无第三方实测 → 必须实物卡尺复测。**

### 2.2 采购现实

- **Adafruit 不卖 3000mAh 单节软包**，上限 2500 mAh（#328，50 × 60 × 7.3 mm，$14.95，JST-PH，含保护）。
- **SparkFun 上限 2 Ah**（PRT-13855，60 × 54 × 5.8 mm，$19.41，JST-PH）。
- **要 3000mAh 只能走中国原厂或 BatterySpace**；且中国 3000mAh 软包**普遍不预装 JST-PH**
  → 采购需指定压接，或自购 `PHR-2` + `SPH-002T-P0.5S`。

### 2.3 BQ24072 充电电流核算（ADR-0002 相关）

- 容量 **10 Ah** 下，芯片可编程上限 **1.5 A ÷ 10 Ah = 0.15C**，远在 LiPo 理想区间
  （厂商标称标准充电 0.5C–1C）之内 ⇒ **电芯侧完全不构成限制**。
- ✅ **2026-09-18 定稿：`R_ISET` = 887 Ω ⇒ ICHG ≈ 1.0 A（0.10C）**。
  依据是**商用同容量（≥5000 mAh）键盘的实测充电区间 0.035–0.163C**（见
  `research/large-battery-keyboard-charging-current.md` 与 `power-architecture.md` §3.7）。
  耗散 (5−3.7)×1.0 = **1.3 W**；按 JEDEC 板 `RθJA` = 44.5 °C/W 估 `Tj` ≈ 83 °C，低于 125 °C 门限。
- `K_ISET = 890`（TI SLUA947A）→ R_ISET：1.5 A = 593 Ω / 1.0 A = **887 Ω** / 0.5 A = 1.78 kΩ。
- 🔴 **安全定时器仍是硬约束**：`tMAXCHG` 最长 = **7.2 / 9.6 / 12 h**（min/typ/max），
  而 1.0 A 充满 10 Ah 仍需约 **10 h** ⇒ 落在 9.6–12 h 边缘 ⇒ **`TMR` 接 VSS 禁用定时器**。
  详见 `docs/power-architecture.md` §3.5 / §3.7。

### 2.4 TS 温度检测引脚 —— ✅ 已解决（2026-09-17）

> **下方内容为当时的阻塞记录。** 现已解除：TS 阈值与「禁用温测」的合法接法都从
> TI SLUS810N 正文取得了（`V_HOT` ≈ 300 mV / `V_COLD` ≈ 2100 mV，内部 75 µA 偏置，
> 配 10 kΩ 恰对应 0–50 °C）。本项目取 **`R5` = 10 kΩ 到 VSS 禁用温测**。
> 四个方案的完整对比见 `docs/bq24072-pinout.md` §3.4 与 `docs/power-architecture.md` §3.3。

- ✅ 已确认：BQ24072 有 **NTC thermistor input**，特性为「BAT temp thermistor monitoring
  (hot/cold profile)」；TI 有应用笔记 **SPVA059**；**10k NTC 可用**（需配 R_S / R_P）。
- ❌ **未取得**：TS 的 `V_HOT`/`V_COLD` 阈值、`I_BIAS`、以及「用固定电阻禁用温度监测的具体阻值」。
- **根因**：PDF 无法通过网页抓取读取，命令行网络访问受限，各 datasheet 站点 403。
- **必须人工做**：浏览器打开 TI `SPVA059` 与 `bq24072.pdf` (SLUS810N) §7 `TS` 行 + §9.3.6。
- **保守做法**：按 SPVA059 配一颗真 10k NTC 贴电池表面。
  ⚠️ Adafruit 大容量电池**明确不带 NTC**，热敏必须自己加。
- 另：TI 官方措辞是「hot/cold profile」，**未使用「JEITA」一词** —— 文档中应改写。

### 2.5 JST-PH 2.0 连接器（✅ JST 原厂页确认）

| 项目 | JST 官方值 |
| --- | --- |
| Pitch | **2 mm** |
| 额定电流 | **2 A AC/DC（AWG #24 条件）** |
| 额定电压 | 100 V AC/DC |
| 温度范围 | **−40 ℃ ~ +105 ℃**（⚠️ 与分销商冲突，见下） |
| 适用线规 | **AWG #32–#24**（0.032–0.22 mm²），绝缘外径 φ0.5–1.5 mm |
| 认证 / 锁扣 | **TÜV、UL** / friction lock |
| 插合总高 | **8.0 mm**（原厂原文 mounting height of 8 mm；top-entry 宽 4.5 mm） |

**料号（均已从 JST 原厂数据表确认）：**

| 用途 | 料号 | 分销商号 |
| --- | --- | --- |
| 板端针座（直插立式） | **`B2B-PH-K-S(LF)(SN)`** | LCSC `C131337` |
| 板端针座（**侧插/直角**，省高度） | **`S2B-PH-K-S(LF)(SN)`** | LCSC `C173752`（2A Right Angle, THT, 5.9×7.6mm, 高 4.8mm） |
| 板端针座（**SMT 立式**） | **`B2B-PH-SM4-TB(LF)(SN)`** | LCSC `C160352`（SMD Vertical, 7.95×5.0mm, 高 6.6mm） |
| 线端胶壳 | **`PHR-2`** | LCSC `C157955`；Digi-Key `455-1165-ND` |
| 压接端子（**推荐**） | **`SPH-002T-P0.5S`** | LCSC `C111515` — **AWG #30–#24** |
| 压接端子（窄线规） | `SPH-002T-P0.5L` | LCSC `C265456` — AWG #28–#24 |

- ✅ **`B2B-PH-K-S` 与 `B2B-PH-K-S(LF)(SN)` 是同一颗料**（原厂备注：*This product displays "(LF)(SN)" on the label.*），两种写法都能订。
- ✅ **`(LF)(SN)` 后缀 = 符合 RoHS**（JST 官方环境调查页原文：「indicate RoHS-compliant products」）。
  原厂**未**展开字母含义；「无铅/纯锡」的解释来自第三方转述，仅有立创「Contact Plating: Tin」佐证 → 定性为**良好佐证，非原厂原文**。
- ⚠️ **2 A 额定条件是 AWG #24** → pigtail 请指定 **AWG #24**；用 #26/#28 会降低实际载流。
- ⚠️ **温度范围存在未解决矛盾**：JST 原厂 **−40~+105 ℃** vs **所有**分销商一致 **−25~+85 ℃**。
  推测分销商为带载/UL 式额定，**未证实**。引用时写原厂值并注明差异。
- ⚠️ **高度 8 mm vs 6.00 mm**：原厂写 8 mm，分销商写裸针座 6.00 mm。
  推断 8 mm = **插合总高**（针座 + PHR-2 就位），**无页面如此说明**。
  → **机壳按 8 mm 保守留高，并以 JST 官方 STEP 模型确认。**
- ❌ **插拔寿命（mating cycles）：任何来源均未给出 → 文档中不得出现此数字。**

**PCB 焊盘/孔径/针脚尺寸 = ❓ UNVERIFIED**，只存在于 JST 的 PDF 图纸里。
⚠️ **踩坑记录**：JST 的 datasheet PDF（`ePH.pdf` / `ePH-H.pdf`）**内容流是纯图像矢量图、无文字绘制算子**，
任何 PDF 文本抽取都取不到尺寸；且 PDF 无法通过网页抓取读取。
→ **正确做法：导入 JST 官方 STEP 模型到 CAD 量测**
`https://www.jst-mfg.com/product/index.php?type=10&series=199&doc=2&filename=B2B-PH-K-S.zip`

**采购动作**：① pigtail 指定 **AWG #24**；② **直接买预压接好的 `PHR-2` + `SPH-002T-P0.5S` 成品**，不要手工压接。

---

## 3. 对既有决策的影响（需要更新 ADR）

| ADR | 影响 | 处置 |
| --- | --- | --- |
| ADR-0002（BQ24072） | 充电电流建议与 `R_ISET` 取值；TS 引脚方案 | ✅ **已补充**（ADR-0002 已加勘误；取值见 `docs/power-architecture.md` §3.1） |
| ADR-0003（双控制器兼容 footprint） | nice!nano v2 = 21 GPIO；SuperMini **ZMK 官方不支持**；电池 ADC 脚冲突需 0Ω 跳线 | ✅ **已修订并决策**：第一版按 nice!nano v2 设计并保证；SuperMini 降级为「焊盘兼容、不保证」 |
| ADR-0005（RGB 门控） | ✅ 得到强支撑：nice!nano 官方说明 **P0.13 置高可切断 VCC**，正是为省 LED 静态功耗 | ✅ 已印证 |
| ~~新增 ADR（待写）~~ | ~~矩阵引脚方案：直连 vs 74HC595 移位寄存器~~ | ✅ **已落地：ADR-0008（74HC595）** |

---

## 4. 待办

| 编号 | 待办 | 性质 |
| --- | --- | --- |
| C1 | 人工查 TI SPVA059 + SLUS810N 补 TS 引脚参数 | 需人工（PDF 不可达） |
| C2 | ~~决策矩阵引脚方案~~ ✅ **已定**：74HC595 移位寄存器，见 **ADR-0008** | 已完成 |
| ~~C3~~ | ~~修订 ADR-0003（SuperMini 不支持 ZMK / ADC 脚冲突）~~ | ✅ **已完成**（ADR-0003 已加「修订」+「决策」两节） |
| C4 | 采购实物：1× nice!nano v2 + 2–3 个不同货源 SuperMini + 1× Adafruit #328 作对照，卡尺 + 万用表实测 | 需采购 |
| C5 | 索要 605080 完整规格书与实物卡尺厚度，确认能否出厂压接 JST-PH 2.0 | 需与供应商沟通 |
| C6 | 定稿电池型号与电池仓尺寸（解除外壳阻塞） | 🟡 **容量已定（2×5000 mAh 并联，2026-09-17）**；剩采购落地与电池仓尺寸重定 ⇒ `power-architecture.md` P17 / P18 |
