# 3000mAh 3.7V 单节 LiPo 软包电池 — 尺寸调研报告

**用途**：DIY 无线机械键盘 3D 打印外壳的内部空间规划。
**关键输出**：L × W × **T（厚度）** mm。
**调研日期**：2026-09。
**方法**：只用实际抓取到的页面数据。凡是没能从真实商品页/数据表核实到的数字，一律标 `UNVERIFIED`，不猜测。

> **一句话结论**：3000mAh 单节软包锂电的**典型厚度是 8.5–10.0 mm，众数 9 mm**。
> 6 mm 只在"细长高倍率"电芯上出现（如 6.0 × 45.5 × 135 mm）；3.2 mm 只在"大平板"电芯上出现（3.2 × 68 × 100 mm）。
> **给 3D 外壳留厚度请按 ≥ 10.5–11 mm 设计**（理由见第 3 节：型号是标称值，实物带 PCM 后普遍更大）。

---

## 1. 候选电池总表

尺寸列已统一整理为 **L × W × T (mm)**；`*` 表示页面原始书写顺序不同，已在备注中标注原文。

| # | Model / Listing | Capacity | L × W × T (mm) | Protection | Connector | Price | Source URL |
|---|---|---|---|---|---|---|---|
| 1 | **Adafruit #2011** Lithium Ion Battery 3.7V 2000mAh | 2000mAh ±2%, 3.7V, LiPoly | **60 × 36 × 7**（原文 `60mm x 36mm x 7mm / 2.4" x 1.4" x 0.3"`） | ✅ 内置保护电路（过充 / 过放至 3.0V / 输出短路）；**无热敏电阻** | **JST-PH 2-pin**（原厂正品） | **$12.50**（1–9）；$11.25（10–99）；$10.00（100+）；In stock | https://www.adafruit.com/product/2011 |
| 2 | **Adafruit #328** Lithium Ion Polymer Battery 3.7v 2500mAh | 2500mAh (~10Wh), 3.7V, LiPoly | **60 × 50 × 7.3**（原文 `Size: 1.9" x 2.3" x 0.29" (50mm x 60mm x 7.3mm)` — 原文顺序为 L×W×T 但写作 50/60） | ✅ 内置（过充 / 过放 ~2.8V / 短路） | **JST-PH 2-pin**（原厂正品） | **$14.95**（1–9）；$13.46；$11.96；In stock | https://www.adafruit.com/product/328 |
| 3 | **SparkFun PRT-13855** "Lithium Ion Battery - 2Ah" | 2000mAh (2Ah), 3.7V | **60 × 54 × 5.8**（原文 `Dimensions: 0.25x2.1x2.4" (5.8x54x60mm)` → 0.25"=T, 2.1"=W, 2.4"=L） | ✅ 内置 over-voltage / over-current / minimum-voltage 保护 | **JST-PH 2-pin**（2mm 间距） | **$19.41** | 现售页 https://www.sparkfun.com/lithium-ion-battery-2ah.html （**页面正文抓取被截断**）；数据取自 SparkFun 官方教程 https://learn.sparkfun.com/tutorials/battery-technologies/lithium-polymer 与授权经销商 https://elmwoodelectronics.ca/collections/sparkfun/products/13855 |
| 4 | **SparkFun PRT-08483** Polymer Lithium Ion Battery 2000mAh（旧款/已停售） | 2000mAh, 3.7V | **60 × 54 × 5.8**（原文同上 `5.8x54x60mm`） | ✅ 内置（over voltage / over current / minimum voltage） | **JST-PH 2-pin**（2mm 间距） | Pre-Order（RSD 标价，**UNVERIFIED**） | https://012lab.com/en-gb/product/sparkfun/polymer-lithium-ion-battery-2000-mah （授权经销商，页脚注明"Original SparkFun product description and images used with Sparkfun permission"） |
| 5 | **BatterySpace PL-6045135-10C**（Product #4404）"High Power Polymer Li-Ion Cell: 3.7V 3000 mAh" | **3000mAh** 标称 (11.1Wh), 3.7V, Polymer Li-Ion | **135 × 45.5 × 6.0**（原文 `Dimension(LxWxH) with tolerance +/- 1 mm \| 135mm x 45.5mm x 6.0mm`） | ❌ **不含**。页面明确要求："We must use a protection IC (PCB)…" 裸电芯 | ❌ 未列出（裸电芯） | **$17.83**（1–4）；$17.29 / $16.93 / $16.58 / $16.04 阶梯；"Limited Time Sale" | https://www.batteryspace.com/highpowerpolymerli-ioncell37v3000mah6045135-10c111wh30arate.aspx |
| 6 | **BatterySpace CU-JAS427**（Product #6606）"Polymer Li-Ion Battery Pack: 3.7V 3000mAh (703562-2C)" | **3000mAh** (11.1Wh) = **2 × 1500mAh 并联**, 3.7V | **65 × 36 × 13**（原文 `Dimension (LxWxH) \| 65x36x13 mm (±1.5 mm)`）— **13mm 因两片叠放** | ✅ **外置 PCB (5A)** 装在电池组上（过充/过放/短路）+ 1× 10K NTC | ❌ **裸线**：`6" 22AWG Red/Black/White` | **$39.68**；Build to order，交期 5 工作日，需 hazmat 费 | https://www.batteryspace.com/polymer-li-ion-battery-pack-3-7v-3000mah-11-1wh-5a-rate.aspx |
| 7 | **BatterySpace PL-605060-2C**（Product #4357，2000mAh — 型号编码佐证样本） | 2000mAh 标称 / 2050mAh nominal, 3.7V | **60.5 × 50.5 × 6**（原文 `Dimension(LxWxH) with tolerance ±1 mm \| 60.5mm x 50.5mm x 6mm`） | ❌ 不含；"You must use a protection IC (PCB)" | ❌ 未列出（裸电芯） | **$14.49**；$14.05 / $13.76 / $13.47 / $13.04 阶梯；In Stock | https://www.batteryspace.com/Polymer-Li-Ion-Cell-3.7V-2000mAh-605060-2C-7.4Wh-4A-rate.aspx |
| 8 | **Jauch Quartz LP103450JH**（德国原厂，经 Digi-Key 分销） | **1900mAh** 标称 (7.03Wh), 3.7V, Lithium-Ion Polymer | **52 × 34.5 × 10.8**（波兰语原文 `Obudowa: 52x34,5x10,8mm` = 外壳尺寸） | ✅ **PCM** 随附（标题 `... Lithium Polymer Battery PCM Wires 70mm`） | ❌ 无连接器，**2 根 70mm 引线** | 未标价（`Towar dostępny na zamówienie` = 可订货）→ **UNVERIFIED** | https://jauch.com.pl/produkt/lp103450jh |
| 9 | **Shenzhen Tcbest 103665** 3.7V 3000mAh Li Polymer Battery | **3000mAh**, 3.7V | **65 × 36 × 10**（原文 `Specification: 10*36*65mm`；规格表 `Battery Size 10*36*65(mm)`） | ❌ 该 SKU 未列 → **UNVERIFIED** | ❌ 未列 → **UNVERIFIED** | **$0.82**，**Min Order 500 Pieces** | https://www.madeinchina.com/mall/show-103665-3-7V-3000mAh-3-7V-Li-Polymer-Battery_11720.html |
| 10 | **LCSC / 立创商城 FLYOUNG FLY.984065.3000**（LCSC p/n C5358465） | **3000mAh**, 3.7V, 聚合物锂电池 | **9.8 × 40 × 65** ← **由型号推导，页面未印尺寸** | 页面未列 → **UNVERIFIED** | 页面未列 → **UNVERIFIED** | **¥29.56 起**（JLC 图页）；镜像站 ¥31.234 (1+) / ¥29.9827 (10+) | https://item.szlcsc.com/6169038.html ；https://item.szlcsc.com/product/jpg_6169038.html ；镜像 https://www.dlchip.net/product/2691358.html |
| 11 | **Shenzhen Blumoti BMP 系列 3000mAh**（10 个型号，中国原厂） | 3000mAh, 3.7V（BMP854065DT 为 3.8V） | 逐型号见下方第 2 节表格：**T 从 3.2 到 9.8 mm** | 页面通则："**Protection Circuit: PCB/PCM**, including overcharge, over-discharge, overcurrent, and short-circuit protection" | 页面未列具体连接器 → **UNVERIFIED** | 未标价（B2B 询价）→ **UNVERIFIED** | https://www.blumoti-battery.com/lithium-battery-cell/standard-lipo-battery/3-7-v-lipo-battery-3000mah.html |
| 12 | **AFTERTECH 103665 3000mAh**（Amazon.it 第三方 listing，**非一级来源**） | 3000mAh (3Ah), 3.7V, LiPo | **65 × 36 × 10**（标题原文含 `65x36x10mm`） | ✅ **CON BMS**（含 BMS 保护板） | ✅ **CONNETTORE JST PHR 02**（JST-PH 2.0，2 pin） | 检查时 "Nessuna offerta in evidenza disponibile"（无在售报价）→ **UNVERIFIED** | https://www.amazon.it/dp/B0DND6941R |
| 13 | **Taobao 商品页** | — | — | — | — | — | ❌ **抓取失败**：`https://item.taobao.com/item.htm?id=675432109876` 返回 HTTP 200 但正文为空（JS/登录墙），与任务说明一致。**无 Taobao 数据**。 |

### 表外补充：Adafruit / SparkFun 均无 3000mAh 单节软包

- **Adafruit**：`https://www.adafruit.com/category/574`（Batteries 分类页，已抓取）完整列出其 LiPo 产品线：100 / 150 / 350 / 400 / 420 / 500 / 1200 / **2000** / **2500** / 4400 / 6600 / 10050 mAh。**没有任何 3000mAh 单节软包**；单节软包最大为 **2500mAh (#328)**。2200mAh 为**圆柱**电池 (#1781)，4400/6600mAh 为多节并联包。
- **SparkFun**：`https://learn.sparkfun.com/tutorials/battery-technologies/lithium-polymer`（SparkFun 官方教程，已抓取）列出其 3.7V LiPo 软包产品线及价格：40mAh $7.14 (PRT-13852)、110mAh $7.53 (PRT-13853)、400mAh $7.98 (PRT-13851)、850mAh $13.61 (PRT-13854)、1500mAh IEC62133 $15.95 (PRT-26059)、**2Ah $19.41 (PRT-13855)**。**没有任何 3000mAh 单节软包**；最大为 **2Ah**。
- ⚠️ **抓取限制说明**：`sparkfun.com` 商品详情页**正文被截断**（页面巨型导航栏占满配额，技术参数区不可达）；Wayback Machine 与 r.jina.ai 代理均失败。因此上表 #3/#4 的尺寸数字来自 **SparkFun 授权经销商逐字转载的 SparkFun 原文**，而非 sparkfun.com 本体。若需 100% 一级来源，请人工打开 `https://www.sparkfun.com/lithium-ion-battery-2ah.html` 核对。
- ⚠️ **Digi-Key / Mouser 抓取失败**：`digikey.com`（含 product-highlight 页）返回 **HTTP 403 Cloudflare**；`mouser.com` 搜索页 fetch 直接失败；`robotshop.com` / `core-electronics.com.au` / `onlinecomponents.com` 均 403。故**未能**从 Digi-Key/Mouser 取得 3000mAh 软包的一手规格。

---

## 2. 中国原厂 3000mAh 全尺寸谱（Blumoti，10 个型号）

来源：https://www.blumoti-battery.com/lithium-battery-cell/standard-lipo-battery/3-7-v-lipo-battery-3000mah.html
页面上这张表**直接给出 Thickness / Width / Length 三列**，是本次最有价值的厚度证据：

| Model NO. | Capacity | Nom.V | Cathode | **Thickness** | Width | Length | Energy Density |
|---|---|---|---|---|---|---|---|
| BMP3268100DT | 3000mAh | 3.7V | LCO | **3.2 mm** | 68 mm | 100 mm | 510 Wh/L |
| BMP855769DT | 3000mAh | 3.7V | NCM | **8.5 mm** | 57 mm | 69 mm | 332 Wh/L |
| BMP854065DT | 3000mAh | **3.8V** | LCO | **8.5 mm** | 40 mm | 65 mm | 516 Wh/L |
| BMP895049DT | 3000mAh | 3.7V | LCO | **8.9 mm** | 50 mm | 49 mm | 509 Wh/L |
| BMP904860DT | 3000mAh | 3.7V | NCM | **9 mm** | 48 mm | 60 mm | 428 Wh/L |
| BMP904560DT | 3000mAh | 3.7V | NCM | **9 mm** | 45 mm | 60 mm | 457 Wh/L |
| BMP905148DT | 3000mAh | 3.7V | LCO | **9 mm** | 51 mm | 48 mm | 504 Wh/L |
| BMP904356DT | 3000mAh | 3.7V | LCO | **9 mm** | 43 mm | 56 mm | 512 Wh/L |
| BMP905048DT | 3000mAh | 3.7V | LCO | **9 mm** | 50 mm | 48 mm | 514 Wh/L |
| BMP984554DT | 3000mAh | 3.7V | NCM | **9.8 mm** | 45 mm | 54 mm | 466 Wh/L |

**同页通则规格（原文）**：Nominal Voltage 3.7V；Charging Voltage 4.2V；Discharge Cut-off 2.75V / 3.0V；Nominal Capacity 3000mAh (0.2C discharge)；**Standard Discharge Rate 0.2C–1C (0.6A–3A)，1C–10C can be customized**；**Standard Charging Rate 0.5C–1C (1.5A–3A)**；**Protection Circuit: PCB/PCM**；Operating 0–45°C charge / −20–60°C discharge；cycle life >600 cycles >80%。
另有 Quick Datasheet PDF：`/uploads/46514/files/Quick-Datasheet-BMP122580-3000mAh-3.7V.pdf`（注：型号 BMP122580 未出现在上表，属另一 SKU）。

---

## 3. 关键工程问题：3000mAh 单节 LiPo 的典型厚度是多少？

### 3.1 实测到的厚度分布（全部来自上面已抓取的页面）

| 厚度 | 对应型号 | 占位面积 (W × L) | 备注 |
|---|---|---|---|
| **3.2 mm** | Blumoti BMP3268100DT | 68 × 100 mm | 极扁平大板，面积换取厚度 |
| **5.8 mm** | SparkFun PRT-13855 / PRT-08483（2000mAh） | 54 × 60 mm | 容量只有 2000mAh |
| **6.0 mm** | BatterySpace PL-6045135-10C（**3000mAh**） | 45.5 × 135 mm | **细长条 + 10C 高倍率** |
| 6.0 mm | BatterySpace PL-605060-2C（2000mAh） | 50.5 × 60.5 mm | 容量只有 2000mAh |
| **7.0 mm** | Adafruit #2011（2000mAh） | 36 × 60 mm | 容量只有 2000mAh |
| **7.3 mm** | Adafruit #328（2500mAh） | 50 × 60 mm | 容量只有 2500mAh |
| **8.5 mm** | Blumoti BMP855769DT（3000mAh） | 57 × 69 mm | |
| **8.5 mm** | Blumoti BMP854065DT（3000mAh, 3.8V） | 40 × 65 mm | |
| **8.9 mm** | Blumoti BMP895049DT（3000mAh） | 50 × 49 mm | |
| **9.0 mm** ×5 | Blumoti BMP9048/9045/9051/9043/9050 系列（3000mAh） | 43–51 × 48–60 mm | **众数** |
| **9.8 mm** | Blumoti BMP984554DT（3000mAh） | 45 × 54 mm | |
| **9.8 mm** | LCSC FLY.984065.3000（3000mAh） | 40 × 65 mm | 由型号推导，页面未印 |
| **10 mm** | Tcbest 103665（3000mAh） | 36 × 65 mm | 25C 高倍率 |
| **10 mm** | Amazon AFTERTECH 103665（3000mAh） | 36 × 65 mm | 含 BMS + JST-PH |
| **10.8 mm** | Jauch LP103450JH（1900mAh） | 34.5 × 52 mm | 型号标称"10"，实物 10.8 |
| **13 mm** | BatterySpace CU-JAS427（3000mAh = 2×1500 叠层） | 36 × 65 mm | **两片叠放，厚度翻倍** |

### 3.2 结论：是 ~5mm、~6mm、~8mm 还是 ~10mm？

**答案：~10 mm（更精确地说 8.5–10.0 mm，众数 9 mm）。**

- **~5 mm：不是 3000mAh 的典型值。** 本次唯一一条 5.5mm/3000mAh 的说法来自搜索摘要里的 **EEMB LP555590HB 3.7V 3000mAh**，但 `eemb.com` 对本次抓取返回 **HTTP 500 / DNS 失败**，Wayback 亦失败 → **该 5.5mm 数字标记为 UNVERIFIED**。已核实的最薄 3000mAh 是 **3.2 mm**，但那是 68 × 100 mm 的大平板，不是常规方块。
- **~6 mm：可行，但要以"细长 + 高倍率"为代价。** 已核实 BatterySpace PL-6045135-10C 为 **6.0 × 45.5 × 135 mm**，是 10C 高倍率动力型电芯——细长条形状在键盘外壳里未必好放（135mm 长）。
- **~8 mm：存在。** Blumoti 有两个 8.5 mm 型号（40×65、57×69）。
- **~10 mm：最常见。** 9 mm 出现 5 次、9.8 mm 出现 2 次、10 mm 出现 2 次。
- **厚度差异幅度**：本次 3000mAh 样本从 **3.2 mm 到 10.8 mm**，跨度约 **3.4 倍**。但如果限制在"常规方块外形（W 36–57、L 48–69）"，厚度集中在 **8.5–10.0 mm**，极差仅 **1.5 mm**。也就是说：**想变薄必须显著放大长宽**（薄 ⇄ 大 的取舍），不能指望同尺寸下随意选厚度。

### 3.3 ⚠️ 给 3D 打印外壳的直接建议

**按 ≥ 10.5–11 mm 的内部净厚度预留**，理由（均有页面证据）：

1. **型号是"标称最小厚度"，实物更大。** Jauch **LP103450JH** 型号含"10"，页面实测尺寸为 **52 × 34.5 × 10.8 mm** —— 厚了 **0.8 mm**。
2. **PCM/BMS + 引线会额外占长（和局部厚度）。** Blumoti 明确写道：*"The bare 103450 cell is about 10 × 34 × 50mm. With a protection board, wires, or connector, it may be slightly longer."* 以及 *"With a protection board, wires, or connector, the total length may be around 51–52mm."* —— 即在标称长度上 **再 +1~2 mm**。
3. **保护板位置决定局部凸起。** SparkFun 官方教程说明：*"almost all LiPo batteries have a small safety circuit built into the top of the cell... The protection circuit board is usually under the yellow Kapton tape where the wires are connected."* 即 PCM 通常在**电芯顶部（出线端）**，那一段厚度会高于电芯本体。
4. **绝不要用"两片叠起来凑 3000mAh"的方案。** BatterySpace 703562-2C ×2 方案：单体 7.0 mm，**叠层后 13 mm**。
5. **公差要算进去。** BatterySpace 明示 `tolerance ±1 mm`（单体）/ `±1.5 mm`（叠层包）；Adafruit 标 `±2%`（容量）。

**推荐做法**：先按 **10.5–11 mm × W+1.5 mm × L+3 mm** 开槽；若最终选用 9 mm 档（Blumoti BMP90xxxxDT 系列）则可收紧到 10 mm 槽深。**必须等实物到手用卡尺复测后再定版**，因为本次所有"厚度"数字都是厂商标称值，非第三方实测。

---

## 4. LiPo 型号命名规则（前导数字 = 厚度）

### 4.1 规则

标准软包锂电型号为 **6 位数字**（超长型号可到 7 位），格式：

```
[T T] [W W] [L L]     例如 103450 → 10 mm 厚 × 34 mm 宽 × 50 mm 长
                                   605060 → 6.0 mm 厚 × 50 mm 宽 × 60 mm 长
```

- **前导数字（第 1–2 位）= 厚度**
  - 厚度 **≥ 10 mm**：两位直接是整毫米数 → `10` = 10 mm，`12` = 12 mm。
  - 厚度 **< 10 mm**：两位是"整毫米 + 十分位" → `60` = **6.0** mm、`98` = **9.8** mm、`32` = **3.2** mm、`85` = **8.5** mm。
  - 这正是"**前导数字编码厚度**"的确切含义，也是为什么 `60` 必须读成 6.0 而不是 60。
- **第 3–4 位 = 宽度**（整毫米）
- **末尾位 = 长度**（整毫米；≥100 mm 时用 3 位）

即 **首 2 位 = 厚度**（当厚度是两位数毫米时就是字面值，否则隐含小数点）；这就是"前导数字编码厚度"的确切做法。

### 4.2 明确写出该规则的来源（已实际抓取）

1. **Shenzhen Blumoti Energy Co., Ltd.（中国原厂）** — https://www.blumoti-battery.com/lithium-battery-cell/standard-lipo-battery/103450-1800mah-lithium-ion-polymer-battery.html
   > "The **'103450'** size measures approximately **10mm thick, 34mm wide, and 50mm long**."
   > "The **model number '103450'** refers to the cell size: about **10mm thick, 34mm wide, and 50mm long**. With a protection board, wires, or connector, the total length may be around 51–52mm."
   → **明确陈述规则的来源。**

2. **Blumoti 3000mAh 型号表自证**：`BMP3268100DT` = 3.2 × 68 × 100 mm；`BMP984554DT` = 9.8 × 45 × 54 mm；`BMP904860DT` = 9.0 × 48 × 60 mm —— 型号数字逐位对应 厚度/宽度/长度。
   → https://www.blumoti-battery.com/lithium-battery-cell/standard-lipo-battery/3-7-v-lipo-battery-3000mah.html

3. **BatterySpace（美国 AA Portable Power Corp.）** — 部件号 ↔ 尺寸直接对照：
   - 部件号 `PL-605060-2C` → 页面规格 `Dimension(LxWxH) ... **60.5mm x 50.5mm x 6mm**`
     https://www.batteryspace.com/Polymer-Li-Ion-Cell-3.7V-2000mAh-605060-2C-7.4Wh-4A-rate.aspx
   - 部件号 `PL-6045135-10C` → 页面规格 `**135mm x 45.5mm x 6.0mm**`
     https://www.batteryspace.com/highpowerpolymerli-ioncell37v3000mah6045135-10c111wh30arate.aspx
   - 系列内还可见 `425085-2C`（4.2×50×85）与 `325085-2C`（3.2×50×85）。
   → **型号 = 厚度|宽度|长度 的直接实证。**

4. **Jauch Quartz（德国）LP103450JH** — 型号 `10|34|50`，页面实测 `52 × 34,5 × 10,8 mm`。
   https://jauch.com.pl/produkt/lp103450jh

5. **Adafruit 自家数据表文件名**（旁证）：#2011 的 UN38.3 报告文件名为 `2011_LP803860+UN38.3.pdf`（`LP803860` → 8.0 厚），#328 的数据表为 `LP785060+2500mAh+3.7V+20190510.pdf`（`LP785060` → 7.8 厚）。
   https://www.adafruit.com/product/2011 ，https://www.adafruit.com/product/328

### 4.3 该规则的已知例外 / 陷阱

- **标称 ≠ 实测**：型号是标称/最小厚度，含 PCM 的成品普遍更大（Jauch 10 → 10.8 mm；Adafruit LP803860 标称 8.0 → 页面标 7 mm；两侧不一致，说明上游厂商标注习惯不统一）。
- **另有一套"电池尺寸码"写法**用于圆柱电池（如 `18650` = 18mm 直径 × 65.0mm 长），与软包 `TTWWLL` 规则不同，勿混淆。
- **同一型号数字在不同厂商可能对应不同容量**：`103665` 有 3000mAh/25C 版本（Tcbest、AFTERTECH），而 `103450` 常见为 1800mAh。**尺寸码不编码容量**。
- ⚠️ **未能验证的来源**：EEMB 官方 FAQ 页 `https://www.eemb.com/faq-6`（标题为 "Meaning of EEMB Lithium Polymer Battery Part Number"）本次抓取返回 **HTTP 500**，其具体措辞**未能核实**，故不作为引用依据。

---

## 5. 未验证项清单（UNVERIFIED）

| 项目 | 状态 |
|---|---|
| EEMB LP555590HB 3000mAh 的 5.5 mm 厚度 | **UNVERIFIED** — `eemb.com` 返回 HTTP 500 / DNS 失败，Wayback 失败；仅见搜索摘要标题 |
| EEMB FAQ 对型号规则的表述 | **UNVERIFIED** — 页面 HTTP 500 |
| SparkFun PRT-13855 在 sparkfun.com 本体的尺寸原文 | **部分** — sparkfun.com 商品页抓取被截断；数字来自官方教程 + 授权经销商逐字转载 |
| Digi-Key / Mouser 上任何 3000mAh 软包的一手规格 | **UNVERIFIED** — digikey.com HTTP 403（Cloudflare）；mouser.com fetch 失败 |
| LCSC FLY.984065.3000 的实际尺寸/保护板/连接器 | **UNVERIFIED** — 页面只给型号与价格，尺寸由型号规则推导为 9.8 × 40 × 65 mm |
| KAMCY 3000mAh（LCSC MRO 3588029）全部参数 | **UNVERIFIED** — 页面为 JS 渲染，抓取返回空正文 |
| Tcbest 103665 的保护板 / 连接器 / 充电电流 | **UNVERIFIED** — 页面未列 |
| 上表 #3/#5/#6/#8 的充电/放电电流以外的倍率细节 | 见各条目；未列者标 UNVERIFIED |
| Amazon AFTERTECH 103665 的价格 / 重量 / 充放电倍率 | **UNVERIFIED** — 检查时无可售报价，listing 未列 |
| 各候选的"实物实测"厚度 | **UNVERIFIED** — 全部为厂商标称值，无第三方实测 |

---

## 6. 对下一阶段的建议动作

1. **优先拿 9 mm 档样品**：Blumoti `BMP904560DT`（9 × 45 × 60）或 `BMP984554DT`（9.8 × 45 × 54）在键盘外壳里占位最友好（45 宽 × 54–60 长）。
2. **要现成带保护板 + JST-PH 的即插即用件**：走 `103665` 路线（Tcbest / AFTERTECH，65 × 36 × 10 mm，含 BMS + JST-PH 2.0），这是本次唯一"3000mAh + 内置保护 + JST-PH + 尺寸明确"的组合。但**供应商需另找可控渠道**（Made-in-China MOQ 500；Amazon listing 当前无货）。
3. **要一级来源背书**：BatterySpace PL-6045135-10C 是唯一从美系正规商家页面拿到完整规格的 3000mAh 单体（$17.83，6.0mm，但 135mm 长、无保护板、未过 UN38.3、标注"prototype only"）。
4. **不要指望 Adafruit / SparkFun 提供 3000mAh**：两家单节软包上限分别为 2500mAh (#328) 与 2000mAh (PRT-13855)。若坚持用这两家，需接受 2000–2500mAh 容量或用多节方案。
5. **外壳可先按 11 mm 槽深出第一版**，等样品卡尺实测后再收紧 —— 这是成本最低的迭代顺序。
