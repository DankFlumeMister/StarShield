# StarShield 硬件事实调研报告（Task A / Task B）

> 调研方式：仅采信可 fetched 的一手来源（原厂 datasheet / 官方文档 / 官方 GitHub / 分销商商品页）。
> 凡未能从一手来源确认者，一律标注 **UNVERIFIED**。
> 采集时间基准：本报告写作时点。价格与库存会变动，请复核。

---

# Task A — LiPo 电池候选

## A.0 关键结论速览（先看这个）

1. **3000mAh 单节软包没有"一个"厚度 —— 厚度与占位面积可互换，这是本次调研最重要的发现。** 已核实的 3000mAh 厚度谱横跨 **3.2 mm 到 10.8 mm（约 3.4 倍）**：
   - **6.0 mm** 可做到，但需要 **~4100 mm²** 占位（实测 `605080` = 6.0 × 50 × 82.5 mm 含保护板；`6045135` = 6.0 × 45.5 × 135 mm）。
   - **常见"矮胖方块"外形（W 36–57 × L 48–69 mm）下，厚度集中在 8.5–10.0 mm，众数 9 mm。**
   - **结论取决于你的机壳更缺深度还是更缺面积。** 键盘通常横向空间比深度好找 → **建议走 605080 路线（6 mm 薄、50 × 82.5 mm 大占位）**，机壳深度可压到 **≥8.5–9 mm**；若必须用 40 × 65 mm 一类紧凑占位，则必须接受 **10–11 mm 深度**。
   - 无论哪条路线，**型号数字是标称最小值，实物（含 PVC 皮 + 保护板 + 引线）会更大**：Jauch `LP103450JH` 型号含"10"，实测 **10.8 mm**；保护板还会使**总长 +1~2 mm** 并在出线端形成**局部凸起**。
2. **BQ24072 的 1.5A 最大充电电流 = 0.5C（3000mAh）**，处于 LiPo 常规安全区间（0.5C–1C），**不超限**。
3. 3000mAh 电芯的**厂商自己标称的快速充电电流就常为 1500mA**，与 BQ24072 满档正好匹配。
4. **所有 3000mAh 候选都带保护板（PCM）**，但**保护板是独立小 PCB**，与电芯一起包在 PVC 热缩皮内 —— 不是"集成在电芯内部"。这会额外增加长度（典型 +2 mm）。
5. 连接器：**没有找到任何 3000mAh 现货使用 JST-PH 2.0**。国际零售（Adafruit）用 **JST-PH 2.0**；中国市场的大容量软包普遍是**裸线**或 1.25mm Micro-JST。**这一点与项目"JST-PH 2.0"的假设冲突，需要采购时指定或自行压接。**

---

## A.1 候选电池表

| Model | Capacity | L x W x T (mm) | Protection | Connector | Price | Source URL |
|---|---|---|---|---|---|---|
| **VP605080** (VCELL / 深圳孚赛能源) | 3000 mAh / 3.7 V / Li-polymer | **82.5 x 50.5 x 6.2**（含保护板, 厚\*宽\*长）<br>电芯本体未单列 | 有，**独立 PCM 板**（标注"带保护板"） | 未标注（按询价定制） | 询价（工厂直供，无零售价） | http://vcellpower-battery.com/zh_cn/3.7v/3-7v-3000mah-605080-ce-certified-li-polymer-battery-.html |
| **GeB LiPol 605080** (LaskaKit SKU LA123044) | 3000 mAh / 3.7 V / Li-polymer | 见注 1（型号即 6.0\*50\*80） | 有（GeB 605080 带保护） | **JST-PH 2.0** | **218 CZK**（约 €8.7） | https://www.laskakit.cz/baterie-li-po-3-7v-3000mah-lipo/ |
| **605080 3000mAh** (UNEMETECH) | 3000 mAh / 3.7 V / Li-ion rechargeable (1S1P) | **电芯 Max 6.0 x 50.5 x 80.5**<br>**成品 Max 6.0 x 50.5 x 82.5** | 有，**独立 PCB**（标题明写 "with PCB"） | 带线 connector（未指定型号） | 询价，MOQ 5000 pcs | https://www.unemetech.com/sale-43746530-3-7v-3000mah-rechargeable-li-ion-battery-605080-with-pcb-and-wire-connector-for-electronics.html |
| **AFTERTECH 103665** (Amazon.it 第三方 listing，**非一级来源**) | 3000 mAh / 3.7 V / LiPo | **65 x 36 x 10**（标题原文含 `65x36x10mm`） | 有，**带 BMS** | **JST PHR-02（= JST-PH 2.0）** ✅ 唯一确认预装 PH 的 3000mAh | 检查时无在售报价 → **UNVERIFIED** | https://www.amazon.it/dp/B0DND6941R |
| **PL-6045135-10C** (BatterySpace #4404) | 3000 mAh / 3.7 V / 11.1 Wh / Polymer Li-Ion | **135 x 45.5 x 6.0**（±1 mm） | ❌ **不含**。页面明写"We must use a protection IC (PCB)…"（裸电芯） | ❌ 无（裸电芯） | **$17.83**（阶梯至 $16.04） | https://www.batteryspace.com/highpowerpolymerli-ioncell37v3000mah6045135-10c111wh30arate.aspx |
| **~15 个中国原厂 3000mAh 型号** (Blumoti BMP 系列) | 3000 mAh / 3.7 V（1 款 3.8 V） | **T 从 3.2 至 9.8 mm**，W 40–68，L 48–100（逐个见 A.2 表） | 通则标称 **PCB/PCM**（过充/过放/过流/短路） | 页面未列 → **UNVERIFIED** | B2B 询价 → UNVERIFIED | https://www.blumoti-battery.com/lithium-battery-cell/standard-lipo-battery/3-7-v-lipo-battery-3000mah.html |
| **Adafruit 328** — Lithium Ion Polymer Battery 3.7v 2500mAh | **2500 mAh** / 3.7 V | **50 x 60 x 7.3**（= 1.9" x 2.3" x 0.29"） | 有（"include the necessary protection circuitry"；过放截止 ~2.8V） | **genuine 2-pin JST-PH** | **$14.95** | https://www.adafruit.com/product/328 |
| **Adafruit 2011** — Lithium Ion Battery 3.7V 2000mAh | **2000 mAh** / 3.7 V | **60 x 36 x 7** | 有（过放截止 3.0V；过充/短路保护） | **2-pin JST-PH** | **$12.50** | https://www.adafruit.com/product/2011 |
| **SparkFun PRT-13855** "Lithium Ion Battery - 2Ah" | **2000 mAh** / 3.7 V | **60 x 54 x 5.8**（原文 `0.25x2.1x2.4" (5.8x54x60mm)`） | 有（over-voltage / over-current / minimum-voltage） | **JST-PH 2-pin（2mm 间距）** | **$19.41** | https://learn.sparkfun.com/tutorials/battery-technologies/lithium-polymer ⚠️ sparkfun.com 商品页正文抓取被截断，数字来自 SparkFun 官方教程 + 授权经销商逐字转载 |

**注 1**：LaskaKit 商品页的详细参数区被 Shopify 主题延迟加载，我只确认到标题 `GeB LiPol Baterie 605080 3000mAh 3.7V JST-PH 2.0`、SKU `LA123044`、价格 218 Kč、库存 51。尺寸未在可抓取文本中出现 —— 但 `605080` 这一型号本身即编码了 6.0 x 50 x 80 mm（见 A.2.3 命名规则），且与上表 VP605080 / UNEMETECH 605080 完全一致。**标称尺寸请按 6.0 x 50 x 80 mm 处理。**
**注 2（重要）**：**Adafruit 与 SparkFun 都不销售 3000mAh 单节软包。** Adafruit 电池产品线上限为 **2500 mAh（#328）**；SparkFun 上限为 **2 Ah（PRT-13855）**。（两者均已从各自官方分类页/教程页确认。）因此上表国际候选如实标注为 2000–2500 mAh。**若坚持 3000mAh，只能走中国原厂（VCELL / UNEMETECH / Blumoti / Tcbest）或 BatterySpace。**

**注 1**：LaskaKit 商品页的详细参数区被 Shopify 主题延迟加载，我只确认到标题 `GeB LiPol Baterie 605080 3000mAh 3.7V JST-PH 2.0`、SKU `LA123044`、价格 218 Kč、库存 51。尺寸未在可抓取文本中出现 —— 但 `605080` 这一型号本身即编码了 6.0 x 50 x 80 mm（见 A.2 命名规则），且与上表 VP605080 / UNEMETECH 605080 完全一致。**标称尺寸请按 6.0 x 50 x 80 mm 处理。**

### 各候选的电气参数（仅列已核实项）

**VCELL VP605080**（唯一给出完整充放电参数的来源）：
- 标称电压 3.7 V；标称容量 3000 mAh
- **快速充电电流 1500 mA；最大充电电流 3000 mA**
- 标准放电电流 600 mA；**最大持续放电电流 4500 mA**；峰值放电 9000 mA
- 充电截止 4.2 V；放电截止 2.75 V
- 重量 **约 50 g**
- 循环寿命 >700 次（厂商标称）
- 保护：**带保护板**，尺寸标注明确为"带保护板"

**Adafruit 328 (2500 mAh)**：
- 重量 **50 g**
- 厂商建议**充电电流 ≤1200 mA**（≈0.5C），"Even 500mA is a good charge rate"
- **明确注明：无内置热敏电阻（no thermistors built-in）**
- 附带官方 datasheet / UN38.3 / MSDS：`LP785060` → 7.8 x 50 x 60 mm

**Adafruit 2011 (2000 mAh)**：
- 重量 **34 g**
- Standard Charge Current **~0.2C / 0.5A**；Standard Discharge **~0.2C / 0.5A**
- 最大充电 "2A or less (500mA is best)"
- 同样**无内置热敏电阻**

> ⚠️ **对 BQ24072 设计的直接冲击**：Adafruit 两款大容量电池**都没有内置 NTC**。这意味着如果要启用 BQ24072 的 TS 温度监测，热敏电阻必须**贴在 PCB 上或外挂到电池表面**，不能指望电池自带。详见 A.3 第 3 问。

---

## A.2 工程问题 1：3000mAh 单节软包的典型厚度

### 结论（重要：这不是一个单一数字）

**厚度是"自由变量"，与占位面积可互换 —— 3000mAh 的厚度由你选择的 footprint 决定，而非由容量决定。**

| 你想要的厚度 | 需要的占位面积 | 典型实例（已核实） |
|---|---|---|
| **6.0 mm** | **~4100 mm²**（50 × 82.5 mm） | VCELL `VP605080` 6.2 × 50.5 × 82.5（含保护板）；UNEMETECH `605080` 成品 6.0 × 50.5 × 82.5 |
| **6.0 mm** | 6100 mm²（45.5 × 135 mm，细长条） | BatterySpace `PL-6045135-10C` 6.0 × 45.5 × 135（10C 高倍率） |
| **8.5–9.8 mm** | **2400–3900 mm²**（紧凑方块 40–57 × 48–69 mm） | Blumoti `BMP904560DT` 9 × 45 × 60；`BMP855769DT` 8.5 × 57 × 69；`BMP984554DT` 9.8 × 45 × 54 |
| **10 mm** | 2340 mm²（36 × 65 mm） | Tcbest / AFTERTECH `103665` 10 × 36 × 65 |
| **3.2 mm** | 6800 mm²（68 × 100 mm，大平板） | Blumoti `BMP3268100DT` 3.2 × 68 × 100 |
| **13 mm** ❌ | 2340 mm² | BatterySpace `CU-JAS427` = **2 × 1500mAh 叠层** → 厚度翻倍，**不要走这条路** |

### 回答你的四选一

- **~5 mm：错。** 3000mAh 做不到 5 mm。我唯一看到的 5.5mm/3000mAh 说法（EEMB LP555590HB）**无法核实**（厂商站 HTTP 500 / DNS 失败）。
- **~6 mm：可行，但要付面积代价。** 实测 `605080` = **6.0–6.2 mm × 50.5 × 82.5 mm**（含保护板）。**这是对键盘最友好的薄方案。**
- **~8 mm：存在**（Blumoti 8.5 / 8.9 mm 型号）。
- **~10 mm：紧凑 footprint 下的众数。** 在 W 36–57 × L 48–69 mm 的常规方块外形里，厚度集中在 **8.5–10.0 mm**（Blumoti 10 个型号中 9 mm 出现 5 次）。

**判定**：如果你问"随便买一颗 3000mAh 最可能是多厚"，答案是 **~9–10 mm**。如果你问"能做到多薄"，答案是 **6.0 mm，代价是 50 × 82.5 mm 的大占位**。**后者才是键盘该选的** —— 详见 A.2.1。

### A.2.1 为什么推荐 605080 路线

键盘机壳的横向空间（X/Y）通常比深度（Z）好找。`605080` 用 4100 mm² 面积换来 6.0 mm 厚度：
- 机壳电池仓开槽 **6.5 × 51 × 84 mm**（在成品 Max 6.0 × 50.5 × 82.5 上留 0.5/0.5/1.5 mm 装配余量）
- 电池上方为**导线弯折 + 保护板局部凸起**留 1–2 mm
- **机壳总深度可按 ≥8.5–9 mm 设计**

若改用 40 × 65 mm 的紧凑电芯（`BMP854065DT` 8.5 mm 或 `103665` 10 mm），则**机壳深度必须放到 ≥11 mm**。

### A.2.2 ⚠️ 标称 ≠ 实测：必须预留的余量

1. **型号数字是标称最小值，实物更大。** Jauch `LP103450JH` 型号含"10"（=10 mm），官方页面实测 **52 × 34.5 × 10.8 mm** —— **厚了 0.8 mm**。
2. **保护板 + 引线使总长再 +1~2 mm。** Blumoti 原文："The bare 103450 cell is about 10 × 34 × 50mm. **With a protection board, wires, or connector, it may be slightly longer**… the total length may be around **51–52mm**." UNEMETECH 也明确区分"电芯 80.5"与"成品 82.5"。
3. **保护板在出线端形成局部凸起。** SparkFun 官方教程："almost all LiPo batteries have a small safety circuit built into the top of the cell… The protection circuit board is usually under the yellow Kapton tape where the wires are connected."
4. **公差**：BatterySpace 明示 **±1 mm**（单体）/ **±1.5 mm**（叠层包）。
5. **不要用两片 1500mAh 叠层凑 3000mAh** —— 7 mm → **13 mm**。

> **落地建议**：先按 **`605080` 路线出图（槽深 9 mm）**，**实物到手用卡尺复测后再收紧**。本次所有厚度均为厂商标称值，**无第三方实测**（见文末 Uncertain）。

### A.2.3 型号命名规则（已用多个一手来源交叉验证）

软包锂电池型号为 **6 位数字**（长型号 7 位），格式 `TTWWLL`：

- **前 2 位 = 厚度**。≥10 mm 时两位即整毫米（`10` = 10 mm）；<10 mm 时两位是"整毫米 + 十分位"（`60` = **6.0** mm、`85` = **8.5** mm、`32` = **3.2** mm）。
- 第 3–4 位 = **宽度**（整 mm）；末位（或末两位）= **长度**（整 mm，≥100 mm 用 3 位）。

**验证证据（三条独立线）：**

| 型号 | 编码解读 | 实际标称尺寸 | 来源 |
|---|---|---|---|
| `LP785060`（Adafruit 328, 2500mAh） | 7.8 × 50 × 60 | **50 × 60 × 7.3**（厚度差 0.5） | https://www.adafruit.com/product/328 |
| `LP803860`（Adafruit 2011, 2000mAh） | 8.0 × 38 × 60 | **60 × 36 × 7**（宽差 2、厚差 1） | https://www.adafruit.com/product/2011 |
| `PL-605060-2C`（BatterySpace 2000mAh） | 6.0 × 50 × 60 | **60.5 × 50.5 × 6** | https://www.batteryspace.com/Polymer-Li-Ion-Cell-3.7V-2000mAh-605060-2C-7.4Wh-4A-rate.aspx |
| `605080`（VCELL / UNEMETECH, 3000mAh） | 6.0 × 50 × 80 | 电芯 **6.0 × 50.5 × 80.5**；成品 **6.0 × 50.5 × 82.5** | 见 A.1 表 |
| `LP103450JH`（Jauch, 1900mAh） | 10 × 34 × 50 | **52 × 34.5 × 10.8**（厚差 0.8） | https://jauch.com.pl/produkt/lp103450jh |
| `103450`（Blumoti 明文陈述规则） | 10 × 34 × 50 | 原文："The **'103450'** size measures approximately **10mm thick, 34mm wide, and 50mm long**." | https://www.blumoti-battery.com/lithium-battery-cell/standard-lipo-battery/103450-1800mah-lithium-ion-polymer-battery.html |

**两个陷阱**：
- **型号不编码容量。** `103665` = 3000mAh，但 `103450` = 1800–1900mAh —— 同样的编码风格，容量差近一倍。
- **圆柱电池 `18650` 是另一套规则**（18 mm 直径 × 65.0 mm 长），不要混淆。

### A.2.4 3000mAh 的通用电气规格（厂商标称通则）

来自 Blumoti 官方 3000mAh 页面（中国原厂，覆盖 10 个型号）：
- 标称 3.7 V；充电截止 **4.2 V**；放电截止 2.75 V / 3.0 V
- 标称容量 3000 mAh（0.2C 放电）
- **标准放电倍率 0.2C–1C（0.6–3 A）；1C–10C 可定制**
- **标准充电倍率 0.5C–1C（1.5–3 A）** ← **直接印证 BQ24072 的 1.5A 在标称充电区间内**
- 保护电路：**PCB/PCM**（过充 / 过放 / 过流 / 短路）
- 工作温度：充电 **0–45°C**；放电 −20–60°C
- 循环寿命 >600 次（>80% 容量保持）

来源：https://www.blumoti-battery.com/lithium-battery-cell/standard-lipo-battery/3-7-v-lipo-battery-3000mah.html

---

## A.3 工程问题 2：3000mAh 的最大推荐充电电流（C-rate）与 BQ24072 的 1.5A 是否超限

### 结论
**不超限。BQ24072 的 1.5A 对 3000mAh 正好是 0.5C，落在 LiPo 最优充电区间内。**

### 算式

```
最大可编程充电电流 I_CHG(max) = 1.5 A          [TI BQ24072 datasheet]
电池容量                C      = 3000 mAh = 3.0 Ah

1.5 A / 3.0 Ah = 0.5 C
```

### 参照基准（多源一致）

| 来源 | 对 3000mAh 的推荐/允许充电倍率 |
|---|---|
| 厂商直接标称（VCELL VP605080） | **快速充电 1500 mA**，**最大充电 3000 mA** |
| Adafruit 328 (2500 mAh) | 建议 **≤1200 mA ≈ 0.5C**；"500mA is a good charge rate" |
| Adafruit 2011 (2000 mAh) | Standard **0.2C / 0.5A**；"1 C or even less"；上限 "2A or less" |
| nice!nano 官方文档（同款 LiPo 化学体系） | "ideally the battery should be charged at around a **0.25-0.5c** charge rate… Above that (**0.5-1c**) is considered **fast charging**" |

来源：
- https://www.adafruit.com/product/328
- https://www.adafruit.com/product/2011
- https://nicekeyboards.com/docs/nice-nano/
- http://vcellpower-battery.com/zh_cn/3.7v/3-7v-3000mah-605080-ce-certified-li-polymer-battery-.html

### 判定

- **0.5C 与 VCELL 自家标称的"快速充电电流 1500 mA"完全吻合** —— 这是最强的证据：制造商认为 1500 mA 对这颗 3000mAh 电芯是正常快充，不是滥用。
- 按 nice!nano 的措辞，0.5C 是 **0.25–0.5C 理想区间**的上边界，**尚未进入 0.5–1C 的 "fast charging" 区间**，更远低于 1C 上限。
- 因此 **BQ24072 跑满 1.5A 不会超过 3000mAh 电芯的允许充电倍率**。

### 但有两个真正的约束（不是 C-rate 问题）

1. **输入源功率**。BQ24072 是**线性充电器**，1.5A 时输入需 ~1.5A 以上。标准 USB 2.0 口只有 500 mA。TI 官方应用笔记给出的配置示例是 **I_LIM = 1.5A（R_ILIM = 1.07 kΩ）+ I_CHG = 1.2A（R_ISET = 750Ω）**，而非同时满档 —— 因为线性充电器在这种压差下的**芯片自身耗散**很可观（V_IN 5V − V_BAT 3.7V = 1.3V × 1.5A ≈ **2 W**，VQFN 封装会触发 thermal regulation 自动降流）。
   来源：https://www.ti.com/document-viewer/lit/html/SLUA947A/configuring-1-2a-fast-charge-slua947741
2. **散热**。1.5A 时芯片会因 thermal regulation 自动降流，实际充不到 1.5A。**建议按 0.5–1.0A 编程**（R_ISET ≈ 890Ω–1.78kΩ），既安全又不会烧芯片。

> `K_ISET = 890`（来自 TI SLUA947A：`RISET = KISET / ICHG`）。由该公式反推：
> - I_CHG = 1.5A → R_ISET = 593 Ω
> - I_CHG = 1.0A → R_ISET = 890 Ω
> - I_CHG = 0.5A → R_ISET = 1.78 kΩ

---

## A.4 工程问题 3：BQ24072 的 TS 引脚 / NTC / JEITA

### 已核实的部分（全部来自 TI 官方页面）

| 事实 | 来源 |
|---|---|
| BQ24072 **具备 NTC 热敏电阻输入**（"NTC thermistor input"） | https://www.ti.com/product/BQ24072 |
| BQ24072 特性列表含 **"BAT temp thermistor monitoring (hot/cold profile)"** —— 即**高/低温双阈值监测**（这就是通常所说的 JEITA 式温度窗口） | https://www.ti.com/product/BQ24072 |
| Datasheet 章节 **9.3.6 "Battery Pack Temperature Monitoring"**（SLUS810N, Rev N, 2021-10）确实存在 | https://www.ti.com/document-viewer/BQ24072/datasheet/GUID-C728F510-9BA7-4FF0-B0AD-980EEB6CBF16 |
| TI 有**专门**讲该系列 TS 引脚网络设计的应用笔记 **SPVA059 "Designing the TS Pin Network for Battery Chargers with Current-Based Battery NTC Temperature Sensing"**（2026-06），适用器件列表中**明确含 BQ24072** | https://www.ti.com/document-viewer/lit/html/SPVA059 |
| SPVA059 给出的设计流程：先取电池温度阈值 → 在充电器 datasheet 中找对应的 **TS 电压阈值 V_HOT / V_COLD** → 用 NTC 的 R-T 表（或 Beta 公式 `RT = R25·e^(β(1/T − 1/T25))`）求 R_HOT / R_COLD → 用公式 2/3 算串并联补偿电阻 R_S / R_P | https://www.ti.com/document-viewer/lit/html/SPVA059/GUID-D5BAC4E0-3CDF-4678-861E-87E63B969367 |
| BQ24072T（BQ24072 的 T 版本）datasheet **SLUS937C** 同样含 9.3.12 "Battery Pack Temperature Monitoring" 章节 | https://www.ti.com/document-viewer/BQ24072T/datasheet/battery-pack-temperature-monitoring-slus9376491.html |

### 关键判定（可下结论的部分）

**"是否支持 10k NTC"** —— BQ24072 的 TS 引脚是一个**基于电流偏置的分压比较器输入**，TI 的设计流程（SPVA059）要求你**从 NTC datasheet 的 R-T 表取 R_HOT / R_COLD**，也就是**任何阻值的 NTC 都可以用，只要配上合适的 R_S / R_P 补偿电阻**。

**行业标准的 10kΩ B=3435/3950 NTC 是这颗芯片最常规的搭配**，TI 应用笔记的"Standard NTC Beta Value"示例即以此类 NTC 为准。
→ **结论：支持。10k NTC 可用，且是推荐选择。**

**"如果没有接热敏电阻会怎样"** —— ⚠️ **UNVERIFIED，请勿凭记忆设计。**

我确认了 TI 的 TS 网络设计方法论和"hot/cold profile"特性存在，但**未能取回 TS 引脚的绝对阈值电压（V_HOT / V_COLD）、内部偏置电流（I_BIAS）以及"用固定电阻替代 NTC 以禁用温度监测"的具体阻值**。

**原因（供后续跟进）**：
- TI datasheet PDF 端点 `ti.com/lit/ds/symlink/bq24072.pdf` 与 `ti.com/lit/gpn/BQ24072` 返回 `application/pdf`，**无法通过网页抓取读取**。
- 本机命令行网络访问受限（`curl` 报 `schannel: SEC_E_NO_CREDENTIALS`），无法直接下载 PDF 解析。
- TI 的 HTML document-viewer 章节正文由 JS 渲染，抓取只得到目录，正文被截断。
- alldatasheet / datasheetbank / manualshelf / icpdf / datasheetspdf 等镜像**全部返回 403（Cloudflare 人机校验）**。

**必须做的事（交付给硬件工程师）**：
请人工打开 **TI SPVA059 的 HTML 版**（`https://www.ti.com/document-viewer/lit/html/SPVA059`）与 **BQ2407x datasheet SLUS810N 第 9.3.6 节**，抄下三个数：
1. `TS` 引脚的 **V_HOT / V_COLD 阈值电压**
2. **I_BIAS**（TS 引脚偏置电流）
3. TS 引脚 **Pin Functions 表**中的原文描述 —— 通常会写明"若不需要温度监测，将 TS 接固定电阻分压到 VIN 的某个比例"或"接 VSS/VIN 会使充电器进入某状态"。

> **设计建议（保守做法，不依赖未核实信息）**：**直接按 TI SPVA059 的流程配一颗真实 10k NTC**（贴电池表面），这样既满足安全要求（LiPo 低温充电会析锂，高温会热失控），又不需要"禁用"逻辑。Adafruit 大容量电池**不带 NTC**，所以 NTC 必须自己加 —— 用一根细软线把 10k NTC 引到电池表面并用 Kapton 胶带固定。

---

## A.5 工程问题 4：JST-PH 2.0 连接器标准料号

### ✅ JST 原厂系列规格（来自 JST 官方网站，一手来源）

来源：**https://www.jst-mfg.com/product/index_sp.php?series=199** （J.S.T. Mfg. Co., Ltd. 官方 PH connector 系列页）
原厂 catalog：`https://www.jst-mfg.com/product/pdf/eng/ePH.pdf`（PDF，本环境不可解析）

| 参数 | JST 官方值 |
|---|---|
| **Pitch** | **2 mm** |
| **Current rating** | **2 A AC/DC (AWG #24)** |
| **Voltage rating** | **100 V AC/DC** |
| **Temperature range** | **−40 ℃ to +105 ℃** |
| **Circuit（可选位数）** | 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 |
| **Conductor size** | **AWG #32, #30, #28, #26, #24**（0.032 mm² – 0.22 mm²） |
| **Insulation O.D.** | φ 0.5 mm – φ 1.5 mm |
| Insulation resistance | 1,000 MΩ min. |
| Withstanding voltage | 800 VAC 1 分钟无击穿/飞弧 |
| PC board mounting | **Through-hole, SMT** |
| Mating direction | **Side entry, Top entry** |
| Array (insertion part) | Single-row（单排） |
| Lock | **Friction lock**（摩擦锁） |
| 认证标准 | **TÜV, UL** |
| 备注 | 有 high-box type header；兼容 PHN / KR / KRD / CK 连接器 |

> ⚠️ **温度范围存在未解决的矛盾**：**JST 原厂**写 **−40~+105 ℃**，而**所有分销商**（LCSC / RS-DigiPart / HQ Online / acme-chip）**一致**写 **−25~+85 ℃**。LCSC 对姊妹型号的 FAQ 提到 "including temperature rise during current flow"，暗示分销商数字可能是**带载/UL 式**额定而原厂是**环境温度**额定 —— **此为推断，UNVERIFIED。**
> **处理方式**：引用时写 **JST 原厂的 −40/+105** 并**注明该差异**，不要静默择一。（对键盘 LiPo 输入两种都极度保守，不构成实际风险。）

### 具体料号（PCB 板端 + 线端）

| 角色 | 料号 | 来源与关键参数 |
|---|---|---|
| **PCB 板端针座**（top entry, 直插, 2 pin） | **B2B-PH-K-S(LF)(SN)** | ✅ **JST 官方型号检索确认**：基础料号 `B2B-PH-K-S` 属 **PH connector 系列**，`RoHSII`，官方备注原文 **"This product displays "(LF)(SN)" on the label."** → **带与不带 `(LF)(SN)` 是同一颗料，两种写法都能订**。https://www.jst-mfg.com/product/index.php?type=1&search_product=B2B-PH-K-S&page=1<br>LCSC `C131337`（https://www.lcsc.com/product-detail/C131337.html）· 立创 https://item.szlcsc.com/142630.html<br>立创参数：1x2P，**pitch 2 mm**，**直插**，参考系列 **PH**，**额定电流 2 A**，额定电压 100 V，黄铜触头**镀锡**，PA66，**UL94V-0**，白色，**打K脚**，底边长 5.9mm |
| **线端胶壳**（mating housing） | **PHR-2** | ✅ JST 官方型号检索确认属 PH connector 系列，`RoHSII`：https://www.jst-mfg.com/product/index.php?type=1&search_product=PHR-2&page=1<br>LCSC `C157955`（https://www.lcsc.com/product-detail/C157955.html）· 立创 https://item.szlcsc.com/169303.html<br>1x2P，pitch 2 mm，PH 系列，PA66，UL94V-0，ROHS3<br>分销商订货号：**Digi-Key `455-1165-ND`**；**Farnell `3616186`** |
| **压接端子** | **`SPH-002T-P0.5S`**（覆盖 AWG #24，推荐）<br>**`SPH-002T-P0.5L`**（AWG #28–#24） | ✅ **料号已确认存在**（LCSC `C111515` / `C265456`，JST 官方目录亦可检索）。两者均为**锡镀磷青铜**、crimp、参考系列 PH<br>**两者唯一已核实的差别 = 适用线规**：<br>· `.5S` = **AWG #30–#24**（0.05–0.22 mm²），绝缘外径 0.8–1.5 mm<br>· `.5L` = **AWG #28–#24**（0.08–0.22 mm²），绝缘外径 0.8–1.5 mm<br>**其余差别 → UNVERIFIED**（未在任何页面找到） |

### 尺寸（JST 原厂描述 + 分销商分项值）

**B2B-PH-K-S(LF)(SN)**：
- Z 轴 — 板上高度 **6 mm**
- X 轴 — 板上底边长度（间距线）**5.9 mm**
- Y 轴 — 板上底边宽度 **4.5 mm**
- 商品描述原文："这是一款薄型、低矮的 2.0mm 间距连接器，**安装后高度为 8.0mm，宽度为 4.5mm**"
- 商品毛重 **0.194 g**

**PHR-2**：商品毛重 **0.078 g**；描述同上

> ✅ **JST 原厂确认宽度与外形的关键描述**：原厂页原文 "With a **mounting height of 8 mm** and a **width of only 4.5 mm** in the top-entry version"。
> ⚠️ **但 8 mm vs 6.00 mm 是个未解决的矛盾**：分销商一致给裸针座高 **6.00 mm**（JST 原厂未给分项值）。最可能的解释是 **8 mm = 插合后总高**（针座 + PHR-2 就位），**但没有任何已抓取页面如此说明 → 推断，UNVERIFIED。**
> **设计动作**：机壳按 **8 mm 插合总高保守预留**，并以 JST 官方 STEP 模型实测确认。

### `(LF)(SN)` 后缀含义 —— ✅ 已找到 JST 原厂答复

**JST 官方环境调查页原文**（https://www.jst-mfg.com/env/?lang=2）：

> "The identification symbols at the end of the part numbers below **indicate RoHS-compliant products**.
> Examples of identification symbols include **(LF)**, **(SN)**, **(LF)(SN)**, (LF)(SN)A, (LF)(SN)B, (LF)(AU), K, (LF)K, (PF), (PF)(CLEAR), etc."

→ **权威结论：尾缀 `(LF)(SN)` 是"该产品符合 RoHS"的标识符号。JST 官方并未展开这两个字母的含义。**

**"lead-free / 100% 纯锡" 的解释属于非原厂来源（但获得独立佐证）**：
- 来源：DigiKey TechForum 引用 JST 的帖子（https://forum.digikey.com/t/jst-suffixes-lf-sn-au-s-n-m-prefixes-g-w-c-q-d/605）："(LF)(SN) = Lead-free with a 100% pure tin finish [SN is the Periodic Table symbol for tin] … no longer needed, the base part number is sufficient."；"(LF) = 98% tin and 2% copper."
- **独立佐证**：立创商城对该 LF 料的参数标注 **Contact Plating = Tin（镀锡）**。
→ **处理方式：把"无铅、纯锡镀层"视为"获得良好佐证但非 JST 原文"，而把"RoHS 合规标识"视为 JST 原文已确证。**

**另一项 JST 官方确证**：基础料号 `B2B-PH-K-S` 与带尾缀的 `B2B-PH-K-S(LF)(SN)` **是同一颗料** —— JST 型号检索页备注原文："This product displays **(LF)(SN)** on the label."（https://www.jst-mfg.com/product/index.php?type=1&search_product=B2B-PH-K-S&page=1）

### 其他封装形态 —— ✅ 全部已确证（JST 官方 PH 产品数据表）

JST 官方 PH 产品数据表（产品清单）中逐项确认，**不再是"系列层面存在"的推测**：

| 形态 | 料号 | 状态 | 关键参数 |
|---|---|---|---|
| **侧插 / 直角 THT** | **`S2B-PH-K-S(LF)(SN)`** | ✅ **已确证**（JST 官方 PH 产品数据表第 34 项） | LCSC `C173752`："…2A **Right Angle**"，`Through Hole, Right Angle, P=2mm`，黄铜/镀锡，打K脚，PA66；外形 5.9 × 7.6 mm，高 4.8 mm |
| **SMT 立式** | **`B2B-PH-SM4-TB(LF)(SN)`** | ✅ **已确证**（JST 官方 PH 产品数据表第 49 项） | LCSC `C160352`："…**Surface Mount, Vertical**"，`SMD, P=2mm`，铜合金/镀锡，"Auxiliary Solder Pin"，PA；外形 7.95 × 5.0 mm，高 6.6 mm |

同表其他变体（**仅确认"存在"，规格未验证**）：`S2B-PH-SM4-TB`（直角 SMD）、`B2B-PH-SM3-TB`、`B2B-PH-SM4-TBT`、`B2B-PH-KL`、`B2B-PH-K-E`、`B2B-PH-TW-S`。

### ⚠️ 两个未解决的矛盾（勿擅自择一）

**① 温度范围：JST 原厂 −40~+105 ℃ vs 所有分销商 −25~+85 ℃**
- JST 原厂系列页：**−40 ℃ to +105 ℃**
- LCSC / DigiPart(RS) / HQ Online / acme-chip **一致**给 **−25~+85 ℃**
- LCSC 对姊妹型号 `S2B` 的 FAQ 写 "−25°C to +85°C (**including temperature rise during current flow**)" → 分销商数字可能是**带载/UL 式**额定，而 JST 给的是**环境温度**额定。**此为推断，UNVERIFIED。**
- **设计动作**：键盘 LiPo 输入两种都极度保守，不构成风险。但**引用时写 JST 的 −40/+105，并注明该差异**，不要静默择一。

**② 高度：8 mm vs 6.00 mm —— UNRESOLVED**
- JST 原厂原文："With a **mounting height of 8 mm** and a **width of only 4.5 mm** in the top-entry version"
- 分销商：`Size 5.90 × 4.50 mm`、`Height 6.00 mm`（HQ Online / LCSC / acme-chip）；DigiPart `Contact Mating Length 3.30 mm`
- **最可能的解释**：8 mm = **插合后总高**（针座 + PHR-2 就位），6.00 mm = **裸针座高度** —— **但没有任何已抓取页面如此说明，这是推断，UNVERIFIED。**
- **设计动作**：机壳按 **8 mm 插合总高**留空间（保守），并**导出 JST 官方 STEP 模型量测确认**。

### ⚠️ PCB 焊盘/孔径尺寸 = UNVERIFIED —— 必须取 JST 官方图纸

**不要相信任何分销商的单一 "height" 字段。** 请把 JST 官方 STEP 模型或 2D 图纸导入 CAD 直接量测：
**https://www.jst-mfg.com/product/index.php?type=10&series=199&doc=2&filename=B2B-PH-K-S.zip**

> **一个值得记录的踩坑经验（避免后人重试）**：JST 的 datasheet PDF（`ePH.pdf` / `ePH-H.pdf`）是 **AES-256 (V5/R6) 加密、用户口令为空**；解密后确认其内容流是**纯图像矢量图，不含任何文字绘制算子**。**障碍不是加密，而是没有文字层** —— 因此**任何 PDF 文本抽取手段都无法从 JST datasheet 取到尺寸**。另外 PDF 本身**无法通过网页抓取读取**。→ **PCB 焊盘尺寸只能走 STEP/2D 图纸路线。**

### 对 StarShield 的实操建议
- **2A / 100V 额定远高于键盘需求**（整机静态 µA 级，充电最多 1.5A）。**1.5A 充电对 2A 额定为 75% 负载 —— 在规格内但余量不宽裕**；若你保持 BQ24072 满档 1.5A，请确认连接器温升；若按建议降到 0.5–1.0A，则余量充足。
- ⚠️ **电流额定条件是 AWG #24**（JST 原文 "2 A AC/DC (AWG #24)"）。**请把 pigtail 指定为 AWG #24**；用 AWG #26/#28 会降低实际载流能力。
- **压接端子选 `SPH-002T-P0.5S`**（AWG #30–#24，覆盖面最广，含典型 24–26AWG 硅胶线）。**建议直接买预压接好的 `PHR-2` + `SPH-002T-P0.5S` 成品 pigtail**，不要手工压接。
- PCB 上放 `B2B-PH-K-S(LF)(SN)`，并**在丝印上标清正负极**（JST-PH 反插会烧板子）。
- 采购电池时注意：**中国市场 3000mAh 软包基本不预装 JST-PH**。方案二选一：(a) 向供应商指定"加 JST-PH 2.0 母头"；(b) 买裸线版 + 预压接 pigtail。

---

# Task B — 控制器模块（nice!nano v2 / SuperMini nRF52840）

## B.1 nice!nano v2

### 已核实事实

| 项目 | 值 | 来源 |
|---|---|---|
| 定位 | Pro Micro 兼容替换板（"same pinout as the Pro Micro"） | https://nicekeyboards.com/docs/nice-nano/ |
| MCU | nRF52840，**1 MB Flash / 256 KB RAM** | 同上 |
| **整板厚度** | **3.2 mm**（mid-mount USB-C，"thinner than a Pro Micro"） | 同上 + https://nicekeyboards.com/nice-nano/ |
| **GPIO 总数** | **21 个**（"3 extra GPIO pins offering a total of 21 GPIO pins"；另有资料称 23 = 21 通孔 + 2 背部焊盘，后者为第三方目录，**UNVERIFIED**） | 同上 |
| 逻辑电平 | **VCC 引脚输出 3.3 V** | 同上 |
| **板载 LiPo 充电器** | **有**。两档可选：**~100 mA**（适用于 100–500 mAh 电池）与 **~500 mA**（需焊接"boost"跳线，适用于 >500 mAh 电池）。官方注：100 mA 档实测约 **85 mA** | https://nicekeyboards.com/docs/nice-nano/ |
| 官方电池尺寸上限 | "the largest recommended size for the battery is **2000 mAh**" | 同上 |
| 官方推荐电池 | **301230**（3 mm 厚，可塞在插座的 nice!nano 下方） | 同上 |
| 电池电压检测 | **P0.04 (AIN2)** 用于 ADC 读电池电压，**不可作他用** | https://nicekeyboards.com/docs/nice-nano/pinout-schematic/ |
| VCC 通断 | **P0.13** 置高可切断 VCC 供电（省 LED 静态功耗，每个 LED 关断时仍可耗 1 mA） | 同上 |
| 其他 | 板载 32.768 kHz 晶振（RTC）；Adafruit nRF52 Bootloader（UF2 拖放刷机）；蓝色可编程 LED + 橙色充电指示 LED | https://nicekeyboards.com/docs/nice-nano/ |

### ⚠️ **引脚间距、每边引脚数 —— 为 UNVERIFIED**
### ✅ **官方 sleep 电流 —— 已找到（来自 ZMK 官方仓库的 Nordic PPK 实测）**

**引脚间距 / 引脚数**：nice!nano 官方文档只说"same pinout as the Pro Micro"，**没有给出 pin pitch 或每边引脚数的数字**。我未能从 nice!nano 官方来源确认。
- **可推断（但未从官方确认）**：Pro Micro 标准封装为**两侧各 12 个引脚（2×12），pitch 2.54 mm**。nice!nano 在 ZMK 中声明 `exposes: [pro_micro]`（即它对外提供 Pro Micro 互连标准），且板上多出的 3 个 GPIO 是**额外**的（部分为背部焊盘），**不改变 2×12 主排针布局**。**请在投板前用 nice!nano 官方 pinout 图（https://nicekeyboards.com/docs/nice-nano/pinout-schematic/ 的 `pinout-v2.png`）人工核对。**

**sleep / deep-sleep 电流**：
- ❌ **Nice Keyboards（原厂）没有发布任何 µA 级 sleep 电流数字。** 已逐一通读官方 product / FAQ / Getting Started / Pinout-Schematic 页面，均无数值，也无 datasheet 页。
- ✅ **但 ZMK 官方仓库里有实测数据**，来源是 `zmkfirmware/zmk` 的 `docs/src/data/power.js`，文件头原文：

  > "All current measurements are in micro amps. Measurements were taken on a **Nordic Power Profiler Kit**. The test device to get these values was **three nice!nanos** (nRF52840)."

| Board | 电源拓扑 | 输出 | Quiescent | 其他 quiescent | **合计（静态基线）** |
|---|---|---|---|---|---|
| `nice!nano`（v1） | LDO | 3.3 V | **55 µA** | 4 µA | **59 µA** |
| **`nice!nano v2`** | LDO | 3.3 V | **15 µA** | 3 µA | **18 µA** |
| `nice!60` | SWITCHING（η 0.95） | 3.3 V | 4 µA | 4 µA | 8 µA |

来源：https://raw.githubusercontent.com/zmkfirmware/zmk/main/docs/src/data/power.js
（该数据驱动官方 **ZMK Power Profiler**：https://zmk.dev/power-profiler ）

**这就是你要的"官方 sleep 电流"**：**nice!nano v2 = 18 µA 合计静态电流**（15 µA 稳压器静态 + 3 µA 其他）。
- ⚠️ **一个诚实的限定**：ZMK 把这组值标为 **"quiescent"（静态）**，**没有**明写"deep sleep"。但 `docs/src/components/power-estimate.js` 中该项是**不被 `(1 - percentAsleep)` 缩放**的（而 idle/typing/underglow 等项会被缩放），说明在 ZMK 自己的功耗模型里，**18 µA 就是常开/睡眠状态的地板值**。→ 因此可视为 sleep 基线，但严格说是"quiescent"，标注为 **PARTIALLY VERIFIED**。

**另有实机实测（非睡眠，而是 BLE 保持连接的 standby）**，来自 ZMK 官方 issue #2990（万用表串联电池，4.2V，Corne 分体）：

| 状态 | `CONFIG_BOARD_ENABLE_DCDC_HV=n` | `=y`（ZMK 曾设为默认） |
|---|---|---|
| 左手 standby（BLE 已连接、未按键） | **0.48 mA** | 0.60 mA |
| 右手 standby | **0.05 mA** | 0.06 mA |
| 左手按键中 | 1.10 mA | 1.58 mA |
| 右手按键中 | 0.79 mA | 1.22 mA |

来源：https://github.com/zmkfirmware/zmk/issues/2990
⚠️ issue 原文明确说明这是 **"not in sleep mode, but not typing anything either. with active bluetooth connection"** → **这是连接待机电流，不是 deep sleep**，比 18 µA 高得多属正常。该 issue 中 AliExpress nice!nano v2 克隆板在 DCDC_HV 开启时待机高达 **1.40–1.90 mA**。

---

## B.2 SuperMini nRF52840（nRF52840 ProMicro，E73-2G4M08S1C 方案）

### 已核实事实

| 项目 | 值 | 来源 |
|---|---|---|
| 板卡别名 | "The nRF52840 ProMicro board is also known as the **SuperMini** board. It's a **clone of the nice!nano board with a mix of v1 and v2 design features**." | https://raw.githubusercontent.com/sasodoma/nrf52840-promicro/main/README.md |
| **所用模块** | **Ebyte E73-2G4M08S1C** | 见下方模块参数 |
| **模块尺寸** | **13.0 x 18.0 mm**（模块本身），陶瓷天线，SMD 封装 | https://www.ebyte.com/product/444.html |
| 模块重量 | **1.0 ± 0.1 g** | 同上 |
| 模块芯片 | nRF52840-QIAAC0 / aQFN™ 73；**1024 KB Flash / 256 KB RAM**；ARM Cortex-M4；板载 32.768 kHz RTC 晶振 | 同上 |
| 模块射频 | 2360–2500 MHz；发射功率 **8 dBm**（出厂默认）；实测距离 120 m；BLE 4.2/5.0 | 同上 |
| 模块出厂状态 | **"模块出厂无程序，用户需要进行二次开发"**（无固件） | 同上 |

### ⚠️ 关于"移除/移动一个电阻以降低休眠电流"—— **前提有误，实际元凶是二极管**

任务描述里的"移除或移动一个电阻"**没有得到一手来源支持**。我在 sasodoma/nrf52840-promicro（专门逆向这块板的官方性质最强的仓库）中找到了**实际记录的修改**，**是元件替换，不是移动电阻**：

> "Some exhibit great power consumption, only **4 µA in sleep**, with EXTVCC disabled. Others had a consumption of **60 µA**… After some component swapping, I found the problem to be the **W5 marked diode**. This is supposed to be a **BAT60B Schottky diode**, with a voltage drop of 0.24 V. On the high power consumption boards I instead measured a drop of **0.7 V**, indicating a **regular silicon diode**. What's more concerning is that apparently the **reverse leakage current** of this diode was also much worse and this is what was causing the power consumption."
> —— https://raw.githubusercontent.com/sasodoma/nrf52840-promicro/main/README.md

**解读**：
- **问题元件：W5（丝印标记）位置的二极管**，设计值应为 **BAT60B 肖特基**（V_F ≈ 0.24 V）。
- 部分批次被替换成**普通硅二极管**（实测 V_F ≈ 0.7 V），其**反向漏电流**远大于肖特基，导致休眠电流从 **4 µA 恶化到 60 µA（15 倍）**。
- **"修改"实质上是把 W5 换成正确的 BAT60B 肖特基**（component swapping），**不是移除电阻**。
- **批次差异极大**：同一型号不同货源，休眠电流 4 µA ↔ 60 µA。**这是采购风险，必须实测筛选。**

### 该仓库记录的另一处已知硬件缺陷（对电池电压检测有影响）

> "The voltage divider for the battery is marked as being connected to **P0.04**… On the actual board it's connected to **P0.24** instead, which makes it **unsuitable for battery voltage measurements**. Instead you can measure the battery directly on **VDDH** pin, but the voltage will rise when USB is plugged in. To prevent this incorrect reading, you can remove the **NPQ2, NBD1 and NPR7** components, and instead **bridge pins 3 and 2 on the NPQ2 MOSFET**. This way the nRF chip will always draw power from the battery and USB will only charge the battery… The voltage on VDDH will then be the actual voltage of the battery."
> —— 同上

**注意**：这里确实出现了"remove … NPR7（一个电阻）"+"bridge NPQ2 pins 3-2"，但**这是为了修正电池电压 ADC 读数**，**不是**为了降低休眠电流。请勿混淆。

### 其他参数

| 项目 | 值 | 状态 |
|---|---|---|
| 尺寸（整板） | **UNVERIFIED**（未找到 SuperMini 整板 33 x 17.8 mm 的一手标称页；其 pinout 兼容 Pro Micro） | — |
| **引脚间距 2.54 mm** | **UNVERIFIED from primary source**。但"Pro Micro 兼容"/"clone of the nice!nano"意味着 2.54 mm，且 ZMK 社区大量用它直接插 Pro Micro 键盘 —— **强烈旁证，但非一手确认** | — |
| 引脚数 / GPIO | **UNVERIFIED** | — |
| 典型 deep-sleep 电流 | **4 µA（好批次，EXTVCC 禁用）/ 60 µA（坏批次）** —— 来自上述逆向仓库。**⚠️ 注意：这是第三方逆向实测，非厂商规格书，且样本批次差异达 15 倍** | 有来源 |
| **板载充电器** | **有**（逆向仓库记录了完整的充电 + 电源路径电路：NPQ2 MOSFET、NBD1、NPR7、USB/电池切换），**但无一手规格书** → 充电电流值 **UNVERIFIED** | 部分 |
| 3.3V 稳压器 / 输入电压 | **UNVERIFIED**。逆向仓库提到 **VDDH** 引脚、**EXTVCC** 使能位、USB 5V 与电池两路供电，说明存在电源路径与稳压，但**未给出稳压器型号、效率或输入电压范围** | — |
> **关于"3.3V 稳压器 + 输入电压"的保守工程结论**：该板使用 nRF52840 的 **VDDH/EXTVCC** 架构（与 nice!nano 同源设计），**GPIO 电平为 3.3 V**；电池直接接 **BAT/VDDH**，USB 5V 经充电器供电。**具体稳压拓扑请以你实际采购批次的原理图为准 —— 该板无官方 datasheet。**

---

## B.3 两款板能否共用一块 footprint？

### 短答：**物理上"能"，但必须按"引脚数少的一方"画，且要接受 3 个功能引脚不可用。**

### 已核实的板级定义差异（来自 ZMK 官方仓库）

ZMK 官方为 nice!nano v2 提供了两套 overlay，文件名直接暴露了 **v1 与 v2 的引脚数差异**：

| 文件 | 大小 | 含义 |
|---|---|---|
| `nice_nano_nrf52840_zmk_1_0_0.overlay` | 534 B | **nice!nano v1** 引脚映射 |
| `nice_nano_nrf52840_zmk_2_0_0.overlay` | 484 B | **nice!nano v2** 引脚映射 |
| `nice_nano_nrf52840_zmk_1_0_0_defconfig` | 343 B | |
| `nice_nano_nrf52840_zmk_2_0_0_defconfig` | 344 B | |

来源：https://api.github.com/repos/zmkfirmware/zmk/contents/app/boards/nicekeyboards/nice_nano

两个 overlay **大小不同（534 vs 484 B）** → **v1 与 v2 的引脚映射确实有差异**。这意味着"nice!nano"本身就不是单一 footprint。

### 差异点（已核实）

| 差异 | nice!nano v2 | SuperMini |
|---|---|---|
| 额外 GPIO | **v2 比 v1 多 3 个 GPIO**（官方："3 extra GPIO pins offering a total of 21 GPIO pins"）。这 3 个是**额外的**，不占用 2×12 主排针 | 基于 nice!nano 的**混合 v1/v2 设计**（"a mix of v1 and v2 design features"） |
| 电池电压 ADC | **P0.04 (AIN2)**，官方明确"can't be used for any other function" | 分压器**实际接在 P0.24**（原理图错标为 P0.04），**因此无法用于电池电压测量**；需改测 **VDDH** |
| USB | mid-mount USB-C，板厚 3.2 mm | UNVERIFIED（外形可能不同） |

来源：
- https://nicekeyboards.com/docs/nice-nano/
- https://raw.githubusercontent.com/sasodoma/nrf52840-promicro/main/README.md

### 共享 footprint 的实际答案

1. **主排针行（2×12 @ 2.54 mm）**：两者都宣称 Pro Micro 兼容，**这一层可以共用**。
   ⚠️ 但 nice!nano 官方**未给出** 2×12/2.54 mm 的数字，SuperMini 更无官方规格 —— **这是我这次未能一手核实的最大空白，投板前必须用两块实物的 pinout 图叠图确认。**
2. **物理外形（板宽/板长/孔位）**：nice!nano v2 **板厚 3.2 mm**；SuperMini 厚度 **UNVERIFIED**。**若两者 PCB 外形尺寸不同，共享插座会有机械干涉风险**（尤其 SuperMini 若有突出的 USB 或元件）。
3. **引脚多寡**：nice!nano v2 有 **21 GPIO**（含 3 个额外脚，很可能是背部焊盘）。若你的 PCB 只做 2×12 通孔，**这 3 个脚在共享 footprint 里自然无法使用** —— 对键盘矩阵通常无影响（2×12 = 24 脚已足够）。
4. **电池电压 ADC 不兼容**：v2 用 P0.04，SuperMini 用 P0.24（且原理图错标）。**同一块 PCB 无法用同一根走线同时正确读取两者电量。** 建议：要么在 PCB 上预留一个 **0Ω 跳线/双焊盘**在 P0.04 与 P0.24 之间选择；要么放弃电池电量显示。

### 建议
- **画一块"Pro Micro 兼容"的 footprint**（2×12 @ 2.54 mm），按 nice!nano v2 的 pinout 定义网络名，**额外在 SuperMini 的差异脚（P0.24）预留一个可选焊盘**。
- 插座化（socket）而非直接焊接 —— nice!nano 官方**强烈建议**用插座："It's *highly* recommended that you socket your nice!nano"。这也让"两种板互换"成为现实可行方案。
- **投板前必须做的两件事**：(a) 拿到两款实物的 pinout 图逐脚叠图；(b) 量 SuperMini 的实际 PCB 外形尺寸与元件高度。

---

## B.4 ZMK 官方支持状态

### 结论：**nice!nano v2 = 官方支持；E73 / SuperMini = 官方不支持。**

### 证据 1 — ZMK 官方 board 目录清单（完整枚举）

我通过 GitHub API 完整枚举了 `zmkfirmware/zmk` 的 `app/boards/` 目录：

```
adafruit, boardsource, interconnects, joric, jpconstantineau,
kbdfans, keebio, keycapsss, kinesis, lowprokb, makerdiary,
mechwild, moergo, native, nicekeyboards, nordic, olkb,
pierrechevalier83, polarityworks, qmk, raspberrypi, seeed,
shields, sparkfun, weact, zhiayang
```
来源：https://api.github.com/repos/zmkfirmware/zmk/contents/app/boards?ref=main

**该清单中不存在 `ebyte`、`supermini`、`promicro`、`nrf52840_promicro` 任何一项。**

逐一验证了可疑目录，均非 SuperMini/E73：
- `joric/` → 仅 **`nrfmicro`**（https://api.github.com/repos/zmkfirmware/zmk/contents/app/boards/joric?ref=main）
- `weact/` → 仅 `blackpill_f401cc`、`blackpill_f401ce`、`blackpill_f411ce`（**STM32，不是 nRF52840**）
- `zhiayang/` → 仅 `mikoto`
- `nordic/` → 仅 `nrf52840dk`、`nrf52840dongle`、`nrf5340dk`（原厂开发板）
- `seeed/` → 有，但属 Seeed 自家 XIAO 系列（E73 是 **Ebyte 亿佰特**，不是 Seeed）

### 证据 2 — nice!nano 的 board 定义（官方存在）

**目录**：`app/boards/nicekeyboards/` 仅含两个子目录：`nice60`、`nice_nano`
来源：https://api.github.com/repos/zmkfirmware/zmk/contents/app/boards/nicekeyboards

**`nice_nano` 目录完整文件清单**：
```
Kconfig.nice_nano
board.cmake
board.yml
nice_nano.zmk.yml
nice_nano_nrf52840_zmk.dts
nice_nano_nrf52840_zmk_1_0_0.overlay
nice_nano_nrf52840_zmk_1_0_0_defconfig
nice_nano_nrf52840_zmk_2_0_0.overlay
nice_nano_nrf52840_zmk_2_0_0_defconfig
pre_dt_board.cmake
```
来源：https://api.github.com/repos/zmkfirmware/zmk/contents/app/boards/nicekeyboards/nice_nano

**`board.yml` 原文**：
```yaml
board:
  extend: nice_nano
  variants:
    - name: zmk
      qualifier: nrf52840
```
来源：https://raw.githubusercontent.com/zmkfirmware/zmk/main/app/boards/nicekeyboards/nice_nano/board.yml

### ZMK board / shield 命名（供 build.yaml 使用）—— ⚠️ **分支不同，写法不同**

**这是本次调研发现的一个关键坑：`nice_nano_v2` 这个 board id 只存在于 stable 分支，不存在于 main 分支。**

#### 开发分支 `main`（post-Zephyr-hwmv2，新布局）

| 项 | 值 |
|---|---|
| **Board 名** | **`nice_nano`**（**不是** `nice_nano_v2`！main 上**没有** `nice_nano_v2` 目录或 board） |
| **Variant / qualifier** | variant `zmk`；`board.yml` 声明 `qualifier: nrf52840`，产物名为 `nice_nano_nrf52840_zmk` |
| **build.yaml 目标字符串（官方文档原文）** | **`nice_nano//zmk`**（v2，默认 revision）<br>**`nice_nano@1//zmk`**（v1） |
| **v1/v2 如何区分** | 通过 **board revision**（`1.0.0` / `2.0.0`，`default_revision: "2.0.0"`），**不是**通过 qualifier |
| **元数据文件** | `nice_nano.zmk.yml` → `id: nice_nano//zmk`，`type: board`，`exposes: [pro_micro]`，`revisions: ["1.0.0","2.0.0"]` |
| **官方 board 定义路径** | `app/boards/nicekeyboards/nice_nano/` |
| **官方文档** | https://zmk.dev/docs/customization · https://zmk.dev/docs/hardware |

#### 稳定分支 `v0.3`（用户照 release 文档走会拿到这个）

| 项 | 值 |
|---|---|
| **Board 名（v2）** | **`nice_nano_v2`** ✅ 存在（`id: nice_nano_v2`，`name: nice!nano v2`） |
| **Board 名（v1）** | `nice_nano`（`name: nice!nano v1`） |
| **定义位置** | 两者**同一目录** `app/boards/arm/nice_nano/`（v1 与 v2 是并列的 `.dts`/`.yaml`/`.zmk.yml` 文件，**没有**单独的 `nice_nano_v2` 目录） |
| **官方文档** | https://v0-3-branch.zmk.dev/docs/hardware |

> **实操建议**：**先确定你的 ZMK 配置文件用哪个分支。** 用 release（`v0.3`）→ 写 `nice_nano_v2`；用 `main` → 写 `nice_nano//zmk`。写错会直接 build 失败。

**nice!nano 家族在 ZMK 中的完整清单**：
- **Boards**：`app/boards/nicekeyboards/` 下**只有两个** —— `nice60` 与 `nice_nano`。故家族内 board 为 `nice_nano`（MCU 模块板）与 `nice60`（板载控制器整键盘）。
- **Shields**（同厂商）：`nice_view`、`nice_view_adapter`（nice!view 电子纸显示 + 转接）。
- **不存在"nice!nano shield"** —— nice!nano 是 `type: board`。

### SuperMini / E73 在 ZMK 中怎么用？

**ZMK 官方没有为 E73/SuperMini/nRF52840 ProMicro 提供 board 定义，也没有 shield 定义。** 这是**穷举后的明确否定结论**，不是猜测：

- `app/boards/` 顶层厂商目录**完整清单**：`adafruit, boardsource, interconnects, joric, jpconstantineau, kbdfans, keebio, keycapsss, kinesis, lowprokb, makerdiary, mechwild, moergo, native, nicekeyboards, nordic, olkb, pierrechevalier83, polarityworks, qmk, raspberrypi, seeed, shields, sparkfun, weact, zhiayang` —— **无 `ebyte`、无 `supermini`、无 `e73`**。
- 每个厂商下的 board 目录**逐个枚举**过，均无匹配。
- `app/boards/shields/` 中也**没有** —— 唯一含 "pro_micro" 的是两个**测试用** shield：`posix_pro_micro`、`tester_pro_micro`。
- ⚠️ **注意别混淆**：`app/boards/interconnects/pro_micro/pro_micro.zmk.yml` 是 **interconnect（引脚互连标准）定义，不是 board**。
- 官方两份 supported-hardware 列表均确认此否定：https://zmk.dev/docs/hardware （dev）· https://v0-3-branch.zmk.dev/docs/hardware （stable）

**修正一个常见误解 —— nRFMicro 是 ZMK 官方 board，不是"社区绕路方案"：**
- **`nrfmicro`（joric 的 nRFMicro）在 ZMK 官方仓库内有第一方 board 定义**：`app/boards/joric/nrfmicro/`
- dev 目标：`nrfmicro/nrf52833/zmk`、`nrfmicro/nrf52840/zmk`、`nrfmicro/nrf52840/flipped_zmk`
- v0.3 board id：`nrfmicro_11`、`nrfmicro_11_flipped`、`nrfmicro_13`、`nrfmicro_13_52833`
- 连 nicekeyboards 官方 FAQ 都把 joric 的 nRFMicro wiki 列为 nRF52840 键盘硬件参考，并称 nRFMicro "is extremely similar to the nice!nano"：
  https://nicekeyboards.com/docs/nice-nano/faq

**ZMK 官方文档记载的、硬件不受支持时的正规做法**：
1. 加一个第三方 **ZMK module**：`zmk module add <url>`（在自己的 config repo 的 `config/west.yml` 中）
2. 自己定义 board 或 shield：`zmk keyboard new`，然后按官方指南写
   - https://zmk.dev/docs/user-setup （"My keyboard isn't listed"）
   - https://zmk.dev/docs/hardware-integration/new-board
   - https://zmk.dev/docs/hardware-integration/new-shield

> **克隆板能刷 nice!nano 固件 ≠ ZMK 支持它。** 因为 SuperMini 复制了 Pro Micro footprint，所以**可以**把 `nice_nano_v2`/`nice_nano//zmk` 的固件刷进去，但 ZMK 并未为它做任何板级定义或验证 —— ZMK issue #2990 正是在这个前提下实测发现克隆板功耗远高于原厂（开启 DCDC_HV 时待机 1.40–1.90 mA）。

**"board" 与 "shield" 的实践差别**（一句话各一）：
- **Board**：完整的硬件平台定义（SoC、时钟、引脚、USB、电源），对应"一块单片机板"，`west build -b <board>` 或 build.yaml 的 `board:` 字段。
- **Shield**：叠在 board 之上的**键盘本体定义**（矩阵行列、按键映射、外设如 OLED/编码器），对应"一块键盘 PCB"，build.yaml 的 `shield:` 字段。

> 由于 SuperMini 是 nice!nano 的克隆且 footprint 兼容，**实际做法是把它当作 nice!nano 来编译**（按分支写 `nice_nano_v2` 或 `nice_nano//zmk`）。但请注意它"mix of v1 and v2 design features"，**引脚需酌情确认**，且 ZMK 官方不为它背书。

**ZMK 官方支持的板卡/盾列表页** —— ✅ **已确认存在**：
- **dev/pre-release**：https://zmk.dev/docs/hardware （页内源文件 `docs/docs/hardware.mdx`）
- **stable v0.3**：https://v0-3-branch.zmk.dev/docs/hardware

dev 页按 interconnect 分组列出复合键盘（Pro Micro 组含 `nice_nano//zmk`、`nrfmicro/nrf52840/zmk`、`adafruit_kb2040`、`boardsource_blok`、`bluemicro840`、`puchi_ble`、`proton_c`、`sparkfun_pro_micro_rp2040`、`mikoto` 等），以及板载控制器键盘（`nice60`、`planck`、`preonic`、`ferris`、`glove80_*` 等）。该页同时说明 **AVR 8-bit 板（SparkFun Pro Micro、Elite-C、Arduino Uno）不受支持**，因为 Zephyr 只面向 32/64 位。

---

# 对 StarShield 设计的直接影响（汇总结论）

| # | 结论 | 影响的设计决策 |
|---|---|---|
| 1 | 3000mAh 厚度由 footprint 决定：**6.0 mm 需 ~4100 mm²（50×82.5）**；紧凑方块（40×65）则需 **8.5–10 mm**。任何路线都**没有 5 mm** | **走 605080 路线 → 机壳深度 ≥8.5–9 mm**；若用 40×65 紧凑电芯 → 深度必须 ≥11 mm |
| 2 | 605080 = **6.0 x 50.5 x 82.5 mm（成品，含保护板）**；型号数字是标称最小值，实物 +0.3~2 mm | 电池仓开槽 **6.5 x 51 x 84 mm**；并按此出第一版图，实物卡尺复测后收紧 |
| 3 | BQ24072 的 1.5A = **0.5C @ 3000mAh，安全**（Blumoti 官方标称标准充电即 0.5C–1C = 1.5–3A） | 但**建议编程 0.5–1.0A**（R_ISET = 890Ω–1.78kΩ），避免线性充电器 2W 耗散触发 thermal regulation |
| 4 | 大容量 LiPo **不带 NTC**（Adafruit 明确声明） | **NTC 必须自己加**，贴电池表面 |
| 5 | BQ24072 支持 NTC + hot/cold profile；**10k NTC 可用** | TS 阈值/偏置电流**必须人工查 TI SPVA059 + SLUS810N §9.3.6 补齐** |
| 6 | JST-PH 全部料号已确证：板端 **`B2B-PH-K-S(LF)(SN)`**、胶壳 **`PHR-2`**、端子 **`SPH-002T-P0.5S`**；侧插 `S2B-PH-K-S(LF)(SN)`、SMT `B2B-PH-SM4-TB(LF)(SN)`。**2A AC/DC (AWG #24) / 100V / 2.0mm / TÜV+UL**；原厂"**插合高 8 mm、宽 4.5 mm**" | 机壳按 **8 mm 插合总高**留空间；**pigtail 指定 AWG #24**、端子用 `.5S`；**PCB 焊盘尺寸必须导 JST STEP 模型量测**（分销商 height 字段不可信） |
| 7 | 中国 3000mAh 软包**普遍不预装 JST-PH**（唯一确认者是非一级来源的 AFTERTECH 103665） | 采购时指定压接 JST-PH 母头，或自购 PHR-2 + SPH-002T-P0.5S |
| 8 | nice!nano v2 **官方支持**，但 **board id 随分支不同**：`main` → `nice_nano//zmk`（v1 = `nice_nano@1//zmk`）；`v0.3` → `nice_nano_v2`。**E73/SuperMini 官方不支持** | 先定分支再写 build.yaml；SuperMini 需自建 board 定义或按 nice!nano 编译 |
| 9 | nice!nano v2 静态电流 **18 µA**（ZMK 官方 Nordic PPK 实测：15+3）；连接待机 0.05–0.48 mA | 电池续航估算可用 18 µA 作睡眠地板值 |
| 10 | SuperMini 休眠电流**批次差异 4 µA ↔ 60 µA**，元凶是 **W5 二极管（应为 BAT60B 肖特基）** | **采购必须抽测休眠电流**；这不是"移电阻"能解决的 |
| 11 | nice!nano v2 = P0.04 电池 ADC；SuperMini = P0.24（原理图还错标） | 共享 footprint 需 **0Ω 跳线**二选一 |

---

# Uncertain / Could Not Verify

以下项目我**未能**从一手来源确认。请勿在正式文档中当作已核实数据使用。

## Task A — 电池

1. **BQ24072 TS 引脚的量化参数（最重要）**：绝对阈值电压 `V_HOT` / `V_COLD`、内部偏置电流 `I_BIAS`，以及"**用固定电阻替代 NTC 以禁用温度监测的具体阻值**"，**全部未能取回**。
   - 已确认存在但无法读取正文的 TI 文档：`SLUS810N` §9.3.6 "Battery Pack Temperature Monitoring"、`SLUA947A`、`SPVA059`（HTML 版正文由 JS 渲染，抓取被截断）。
   - **根因**：PDF 无法通过网页抓取取得；本机命令行网络访问受限（curl 报 `schannel: SEC_E_NO_CREDENTIALS`）；alldatasheet / datasheetbank / datasheetspdf / manualshelf / icpdf / digikey / mouser **全部返回 403 或 DNS 失败**。
   - **补充说明**：TI `BQ24072`（非 T 版）product page 的 datasheet 链接为 **SLUS810N（Rev N, 2021-10-27）**。我读到的 `SLUS937C` 章节树属于 **BQ24072T/75T/79T**（T 版本，TD 引脚行为不同），**不要把 T 版的 TD 引脚特性套到 BQ24072 上**。
2. **关于 "JEITA" 这个词**：BQ24072 官方措辞是 **"BAT temp thermistor monitoring (hot/cold profile)"**，**没有**使用 "JEITA" 一词。二者功能上相近（高低温窗口），但**"支持 JEITA"是一个未经证实的表述，应改写为"支持 hot/cold 双阈值电池温度监测"**。
3. ✅ **`(LF)(SN)` 后缀含义 —— 已解决**：JST 官方环境调查页确认"尾缀符号标识 **RoHS 合规**"（https://www.jst-mfg.com/env/?lang=2）。JST **未展开字母含义**。"无铅 / 纯锡"的解释来自非原厂来源（DigiKey TechForum 引 JST），但**获立创"Contact Plating: Tin"独立佐证** → 视为"良好佐证，非 JST 原文"。
4. ⚠️ **JST PH 温度范围数据源冲突（未解决）**：**JST 原厂**写 **−40~+105 ℃**（https://www.jst-mfg.com/product/index_sp.php?series=199），而**所有分销商**（LCSC / DigiPart-RS / HQ Online / acme-chip）**一致**写 **−25~+85 ℃**。LCSC 对姊妹型号 `S2B` 的 FAQ 提到 "including temperature rise during current flow"，暗示分销商数字是带载/UL 式额定 —— **此为推断，UNVERIFIED。引用时写 JST 的 −40/+105 并注明差异，不要静默择一。**
5. ⚠️ **JST PH 插拔寿命（mating cycles）**：**任何来源都未给出。** JST 系列页无，分销商页无，JST datasheet **无文字层**（见下）。**绝对不要在文档里写插拔寿命数字。**
6. ✅ **侧插版 `S2B-PH-K-S(LF)(SN)` 与 SMT 版 `B2B-PH-SM4-TB(LF)(SN)` —— 已确证**（JST 官方 PH 产品数据表第 34 / 49 项；LCSC `C173752` / `C160352`）。
7. ✅ **压接端子料号已确认**：`SPH-002T-P0.5S`（LCSC `C111515`，**AWG #30–#24**，0.05–0.22 mm²）与 `SPH-002T-P0.5L`（LCSC `C265456`，**AWG #28–#24**，0.08–0.22 mm²），均锡镀磷青铜。**两者唯一已核实差别 = 适用线规**；其余差别 UNVERIFIED。
7b. ⚠️ **PCB 焊盘 / 孔径 / 针脚尺寸 = UNVERIFIED**（仅存在于 JST 的 PDF 图纸中）。**必须**把 JST 官方 STEP 模型或 2D 图纸导入 CAD 量测：https://www.jst-mfg.com/product/index.php?type=10&series=199&doc=2&filename=B2B-PH-K-S.zip
7c. ⚠️ **"8 mm vs 6.00 mm" 高度矛盾未解决**：JST 原厂写 "mounting height of **8 mm**"，分销商一致写裸针座高 **6.00 mm**。推断 8 mm = 插合总高（但**无页面如此说明**）→ **机壳按 8 mm 保守设计，并以 STEP 模型确认。**
7d. ⚠️ **镀层厚度**：所有分销商页该字段均为空 → UNVERIFIED。
7e. **踩坑记录**：JST datasheet PDF（`ePH.pdf` / `ePH-H.pdf`）为 **AES-256 (V5/R6) 加密、用户口令空**；解密后确认内容流**是纯图像矢量图，无任何文字绘制算子** → **障碍是没有文字层，不是加密**。任何 PDF 文本抽取都无法从 JST datasheet 取尺寸；且 PDF 无法通过网页抓取读取。
8. **中国市场 Taobao 直采链接**：Taobao 商品页对抓取有登录/JS 墙，**未能验证任何 Taobao 链接**。表中中国来源均为**电池厂商官网**（VCELL、UNEMETECH）或**欧洲/亚洲零售页**（LaskaKit）。
8. **3000mAh 的放电电流评级**：仅 VCELL 提供了（4500 mA 持续 / 9000 mA 峰值）。**其余候选未标注。**
9. **LaskaKit / GeB 605080 的逐项尺寸与重量**（商品页参数区为延迟加载，未取到）。
10. **Adafruit 是否销售 3000mAh 软包**：**已核实为"否"**。Adafruit 官方 Batteries 分类页（https://www.adafruit.com/category/574）完整列出其 LiPo 产品线：100 / 150 / 350 / 400 / 420 / 500 / 1200 / **2000** / **2500** / 4400 / 6600 / 10050 mAh —— **单节软包最大 2500 mAh（#328）**，**没有 3000mAh**；2200mAh (#1781) 是**圆柱**电池。
11. **SparkFun 是否销售 3000mAh 软包**：**已核实为"否"**。SparkFun 官方教程（https://learn.sparkfun.com/tutorials/battery-technologies/lithium-polymer）列出其 3.7V LiPo 线：40 / 110 / 400 / 850 / 1500 / **2Ah（PRT-13855）** —— **最大 2Ah**。
    - ⚠️ 但 **`sparkfun.com` 商品详情页正文抓取被截断**（巨型导航栏占满配额），上表 SparkFun 的尺寸数字来自 **SparkFun 官方教程 + 授权经销商逐字转载的 SparkFun 原文**，而非商品页本体。**需 100% 一手来源请人工打开 https://www.sparkfun.com/lithium-ion-battery-2ah.html 核对。**
12. **Digi-Key / Mouser / RobotShop / core-electronics / onlinecomponents 的任何商品页**：**全部 403 Cloudflare 或 DNS 失败**，无法作为来源。因此**未能**从 Digi-Key/Mouser 取得 3000mAh 软包或 JST 连接器的一手规格。
12b. **所有 3000mAh 厚度数字均为"厂商标称值"，无第三方实测。** 本次没有任何一颗电池经过独立卡尺复测。已知厂商标称与实物的偏差案例：Jauch `LP103450JH` 型号写"10"、实测 10.8 mm。**定版前必须实物复测。**
12c. **`605080` 的 6.0–6.2 mm 厚度只有 3 家厂商标称**（VCELL 6.2 含保护板 / UNEMETECH 6.0 成品 / GeB-LaskaKit 型号推导）。**无独立实测，且 LaskaKit 页面参数区未取到。**
12d. **EEMB LP555590HB（5.5mm/3000mAh）的 5.5 mm 说法 UNVERIFIED** —— `eemb.com` 返回 HTTP 500 / DNS 失败，Wayback 亦失败。**未采用该数字。**
12e. **`LCSC FLY.984065.3000` 的 9.8 × 40 × 65 mm 是由型号推导，页面并未印尺寸**；其保护板与连接器信息页面亦未列。

## Task B — 控制器

13. **nice!nano v2 的精确板尺寸（长 x 宽 mm）**：官方只给出**厚度 3.2 mm**，**未给长宽**。nicekeyboards.com、splitkb、boardsource、typeractive 商品页均未在可抓取文本中列出长宽。
14. **nice!nano v2 的引脚间距（2.54 mm）与每边引脚数（2×12）**：**无一手来源**。仅有"Pro Micro 兼容"的官方表述 + ZMK 元数据 `exposes: [pro_micro]` 可作旁证。
15. **ZMK 的 15 µA / 55 µA 是否严格等于 "deep sleep" 状态**：**PARTIALLY VERIFIED**。ZMK 把它们标为 **"quiescent"（静态）**，从未写 "deep sleep"。推断依据是 `power-estimate.js` 中该项**不被 `(1 - percentAsleep)` 缩放**（而 idle/typing/underglow 等项会被缩放），说明它是常开基线。**作为睡眠地板值使用合理，但引用时应写"quiescent"而非"deep sleep"。**
16. **SuperMini 整板尺寸、引脚间距、引脚数、GPIO 数**：**全部 UNVERIFIED**（该板无官方 datasheet）。
17. **SuperMini 的板载充电器充电电流值、3.3V 稳压器型号与输入电压范围**：**UNVERIFIED**。仅从逆向仓库得知存在电源路径电路（NPQ2 / NBD1 / NPR7）与 VDDH / EXTVCC 机制。
18. **"移除或移动一个电阻以降低睡眠电流"这一说法**：**未能找到任何一手来源支持**。找到一个**相关但不同**的已记录修改（移除 **NPR7** + 短接 NPQ2 的 2/3 脚），其目的是**修正电池电压 ADC 读数**，**不是降功耗**。降功耗的实际修复是**更换 W5 位置的二极管为 BAT60B 肖特基**。
19. **ZMK issue #2990 的最终处置**：issue 状态为 `closed`（closed_by: nmunnich, 2025-07-21），**但我未确认 ZMK 是否已改掉 `CONFIG_BOARD_ENABLE_DCDC_HV` 的默认值**。issue 正文中给出了用户侧 workaround：在 board 的 `.conf` 里加 `CONFIG_BOARD_ENABLE_DCDC_HV=n`。
20. **为何 `board.yml` 写 `qualifier: nrf52840`，而发布的 `.zmk.yml` id 与官方文档 build 目标用空 qualifier（`nice_nano//zmk`）**：两个事实都有来源，**但 ZMK 未解释这一差异，原因 UNVERIFIED**。安全做法：dev 用 `nice_nano//zmk`（v1 用 `nice_nano@1//zmk`），v0.3 用 `nice_nano_v2`。
20b. **ZMK 代码库未做全文检索**：GitHub code search 需认证（`/search/code` → HTTP 401），故 E73/ebyte/supermini 的否定结论基于 `app/boards` **全部定义路径的穷举** + 两份官方硬件列表，**而非对每个文件的正全文搜索**。
20c. **未排查第三方 ZMK module**：可能存在（但无法证明存在）定义 E73/SuperMini board 的第三方 module。否定结论仅覆盖 `zmkfirmware/zmk` 本体。
20d. **joric/nrfmicro 的 README / wiki 正文未能抓取**（全部 fetch 失败）。仅确认其**在 ZMK 官方仓库内有第一方 board 定义**。搜索中出现过 oshwhub 上一个名为 `nrfmicro_E73` 的设计（非一手来源，未抓取）→ **E73-2G4M08S1C 是否被某个 nRFMicro 变体采用，UNVERIFIED。**
21. **Ebyte E73-2G4M08S1C 模块 datasheet 的完整电气参数**（休眠电流等）：我只从 ebyte.com 商品页取到尺寸/重量/射频/存储参数；**LCSC 上的 datasheet PDF 抓取失败**（`fetch failed`）。模块级 deep-sleep 电流 **UNVERIFIED**。
22. **`supermini_xs_nrf52840`**：搜索中出现 `jnsbyr/zephyr-boards` 仓库含一个 "Super Mini NRF52840 XS"（描述为 23.5mm 级别），但**这是第三方 Zephyr board 定义，不是 ZMK 官方，也不确定是否同一块板**。**未验证，未采用。**

---

## 建议的后续动作（补齐 UNVERIFIED）

1. **人工**打开 https://www.ti.com/document-viewer/lit/html/SPVA059 （HTML 版，浏览器可正常渲染）→ 抄下 BQ2407x 的 `TS` 阈值电压与 `I_BIAS`。
2. **人工**下载 https://www.ti.com/lit/ds/symlink/bq24072.pdf （SLUS810N）→ 读 §7 Pin Functions 的 `TS` 行 + §9.3.6 → 得到"禁用温度监测"的官方接法。
3. ~~人工访问 https://zmk.dev/docs/hardware~~ ✅ **已完成**：该页存在，dev 用 `nice_nano//zmk`、v0.3 用 `nice_nano_v2`。
4. **实物**：采购 1 块 nice!nano v2 + 2–3 个不同货源的 SuperMini → 卡尺量长宽厚、万用表量休眠电流、叠图比对 pinout。
5. **实物（最重要）**：向 VCELL / UNEMETECH / 立辰索取 `605080` 的**完整规格书 PDF**（含放电曲线、内阻、循环寿命、保护板参数），**并索取实物卡尺实测厚度** —— 本报告的 6.0–6.2 mm 全部是厂商标称值。同时确认能否**出厂压接 JST-PH 2.0**。
6. **实物**：Adafruit #328（2500mAh）买一颗作为**已知良好的对照样本**（尺寸/连接器/保护板都已一手确认），用它的卡尺实测值校准你对"厂商标称 vs 实物"偏差的判断。
7. **CAD**：把 JST 官方 STEP 模型导入 PCB 工具量测焊盘/孔径 —— https://www.jst-mfg.com/product/index.php?type=10&series=199&doc=2&filename=B2B-PH-K-S.zip （**JST datasheet PDF 无文字层，无法文本抽取，只能走图纸路线**）
8. **采购**：直接买**预压接好的 `PHR-2` + `SPH-002T-P0.5S` pigtail（AWG #24）**，不要手工压接。
