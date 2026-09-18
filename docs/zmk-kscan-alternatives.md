# ZMK 全部 keyscan 驱动排查：为什么仍选 74HC595

本文件回答一个问题：**ZMK 有没有「不用移位寄存器」的方案能装下 95 键？**

状态：✅ 已排查完毕（结论：有替代驱动，但都不适用于电池供电的 95 键键盘）

**方法**：稀疏浅克隆 ZMK 官方仓库（`git clone --filter=blob:none --sparse`），
在本地穷举全部 kscan 驱动、绑定、文档与所有 shield/board 配置。

---

## 1. ZMK 的 keyscan 驱动全集

从 `app/module/drivers/kscan/Kconfig` 逐一列出（共 6 个）：

| 驱动 | compatible | 引脚模型 | 能否装下 95 键 |
| --- | --- | --- | --- |
| **Matrix** | `zmk,kscan-gpio-matrix` | R 行 + C 列 | ✅ 但需 **24 引脚**（6×18）→ 排针只有 18 |
| **Direct** | `zmk,kscan-gpio-direct` | 每键 1 脚 | ❌ 需 **95 引脚** |
| **Demux** | `zmk,kscan-gpio-demux` | 输入 + 输出（外接模拟开关） | ❌ 见 §3 |
| **Charlieplex** | `zmk,kscan-gpio-charlieplex` | n 脚驱动 n(n−1) 键 | ⚠️ **引脚够，但功耗不可行** → §2 |
| **Composite** | `zmk,kscan-composite` | 组合多个 kscan | 🟡 见 §3，不减少总引脚 |
| **Mock** | `zmk,kscan-mock` | 测试用 | ❌ 与硬件无关 |

---

## 2. Charlieplex：引脚数够，但**功耗上不可行**（决定性否决）

### 2.1 引脚数学（ZMK 官方文档原文）

> - With `interrupt-gpios` unset, this allows **n pins to drive n\*(n-1) keys**.
> - With `interrupt-gpios` set, n pins will drive **(n-1)\*(n-2) keys**,
>   but provide much improved power handling.

| 方案 | 引脚数 | 可驱动键数 | 是否 ≥95 |
| --- | --- | --- | --- |
| 11 脚 + 中断 | 12 | (11−1)×(11−2) = **90** | ❌ 差 5 |
| **12 脚 + 中断** | **13** | (12−1)×(12−2) = **110** | ✅ |
| 11 脚 + 轮询 | 11 | 11×10 = 110 | ✅（但见 §2.2） |

⇒ 走中断的话需要 **12 个查理复用脚 + 1 个中断脚 = 13 个引脚**（比 595 方案的 11 个还多 2 个）。

### 2.2 ❌ 否决理由：静息功耗高出 3 个数量级

**证据来自驱动源码本身**（`app/module/drivers/kscan/kscan_gpio_charlieplex.c`）：

```c
static int kscan_charlieplex_interrupt_enable(const struct device *dev) {
    int err = kscan_charlieplex_interrupt_configure(dev, GPIO_INT_LEVEL_ACTIVE);
    if (err) { return err; }
    // While interrupts are enabled, set all outputs active so an pressed key will trigger
    return kscan_charlieplex_set_all_outputs(dev, 1);   // ← 把【全部】输出置为有效
}
```

**机制**：等待按键时，驱动把**所有查理复用输出脚都置为有效**，
按键按下时电流经二极管流到中断脚，把中断脚拉起来触发 IRQ。
中断脚按官方文档要求配 **`GPIO_PULL_DOWN`**。

⇒ **静息时存在持续的直流电流**：`active 输出 → 二极管 → 中断脚 → 下拉电阻 → GND`。
该电流由下拉电阻决定，**即使没有键按下也不会消失**（这正是它能立刻感知按键的原因）。

**量级估算**（假设典型 10 kΩ 下拉，输出 3.3 V）：

| 下拉电阻 | 静息电流 |
| --- | --- |
| 10 kΩ | ≈ **0.33 mA** |
| 100 kΩ | ≈ **33 µA** |
| 1 MΩ | ≈ **3.3 µA** |

对比本项目的目标：**整机待机约 20 µA**（nice!nano v2 官方实测 18 µA）。
⇒ 查理复用的静息电流会**单独吃掉甚至超过整个待机预算**，
与 ADR-0005（省电）和「关闭时以月计」的续航目标**直接冲突**。

⚠️ 若不用中断（`interrupt-gpios` 留空）则改为**持续轮询**：
驱动会把全部引脚当输出/输入反复扫，CPU 无法进入深度睡眠，**更耗电**。

### 2.3 为什么常规矩阵没有这个问题

`zmk,kscan-gpio-matrix` 的默认模式是**中断驱动**：
行作为输出拉低、列作为输入带上拉，**没有按键时列不被拉低 ⇒ 无电流**；
有按键时列被拉低才触发中断。所以静息电流可以做到接近 0（µA 级）。
（`CONFIG_ZMK_KSCAN_MATRIX_POLLING` 默认 `n`，即不轮询。）

### 2.4 辅证：**ZMK 生态里没有任何一块板实际使用 charlieplex**

在 ZMK 官方仓库中穷举全部 shield 与 board 的 `.dts/.dtsi/.overlay/.keymap/.conf`：

```text
引用 charlieplex 的文件（全部 7 个）：
  app/module/drivers/kscan/CMakeLists.txt          ← 构建
  app/module/drivers/kscan/Kconfig                 ← 配置
  app/module/drivers/kscan/kscan_gpio_charlieplex.c ← 驱动实现
  app/module/dts/bindings/kscan/zmk,kscan-gpio-charlieplex.yaml ← 绑定
  docs/docs/config/kscan.md                        ← 文档
  docs/docs/config/layout.md                       ← 文档
  docs/docs/development/contributing/pull-requests.md ← 提交信息示例里的字样

实际使用它的 shield/board 配置：0 个
```

⇒ 它是**有实现、有文档，但生态里无人使用**的驱动。

---

## 3. 其余驱动为何不可行

### 3.1 Direct（每键 1 脚）
95 键 = 95 引脚。**不可能。**

### 3.2 Demux
`input-gpios` + `output-gpios`，需外接模拟多路复用器。引脚数取决于外接芯片，
且**同样需要额外的 IC** —— 既然都要加 IC，595 有 ZMK 官方驱动与大量先例，
**没有理由选更冷门的 demux**。另：`polling-interval-msec` 默认 25 ms，同样是轮询式。

### 3.3 Composite（组合多个 kscan）
可以让「主键区」「小键盘」「导航簇」各自用独立矩阵，`row-offset`/`col-offset` 错开。

⚠️ **但它不减少总引脚数**：若把键盘拆成 k 个独立矩阵，
总引脚 = Σ(每个矩阵的行数 + 列数)，**≥ 单个整合矩阵的引脚数**。
先用 `docs/_tools/fold-matrix.mjs` 验证过：无论怎么拆，
下界仍是 **R·C ≥ 95** 且同行键数决定列数下界，最优即 20 引脚（8×12）——
**仍超过排针可用的约 16**。

> 📌 注：595 方案本身与 composite **不冲突**——`zmk,gpio-595` 就是一个 GPIO 控制器，
> `kscan-gpio-matrix` 直接引用它的引脚即可，**不需要 composite**。

---

## 4. 顺带印证：ZMK 官方对「矩阵不够用」的标准答案就是移位寄存器

官方文档 `docs/docs/hardware-integration/shift-registers.md` 开篇：

> "Shift registers are **the recommended method** of adding additional GPIO pins to MCUs and boards,
> **when a standard matrix results in an insufficient number of keys**.
> They are recommended because they simultaneously have **very low power consumption** and are quite cheap."

这句话逐字对应本项目的情形。而 charlieplex 虽在 ZMK 中有实现，
其**中断模式会引入持续静息电流**（§2.2），与官方推荐 595 时强调的
「very low power consumption」正好相反。

---

## 5. 最终对比

| 方案 | 引脚 | 额外 IC | 静息功耗 | 生态先例 | 结论 |
| --- | --- | --- | --- | --- | --- |
| 矩阵直连 | 24 | 无 | ✅ µA 级 | 大量 | ❌ 排针不够（18） |
| 折叠后直连 | 20 | 无 | ✅ µA 级 | 无 | ❌ 仍不够（可用约 16） |
| **Charlieplex（中断）** | **13** | **无** | ❌ **约 0.33 mA，超待机预算 16 倍** | **0 块** | ❌ **否决** |
| Charlieplex（轮询） | 11 | 无 | ❌ 更差（CPU 无法深睡） | 0 块 | ❌ 否决 |
| Direct | 95 | 无 | — | — | ❌ 不可能 |
| Demux | 取决于芯片 | 需 | 🟡 轮询式 | 极少 | ❌ 不如 595 |
| **矩阵 + 74HC595** | **11** | 2 颗（约 0.6 元；⚠️ 后修订为 **3 颗**，ADR-0008 修订小节） | ✅ µA 级 | **大量** | ✅ **采用（ADR-0008）** |

**结论：排查了 ZMK 全部 6 个 keyscan 驱动，没有一个能替代 74HC595 方案。**
ADR-0008 的决策维持不变。

---

## 6. 复现方法

```powershell
# research/_clones/ 未随仓库发布，需自行创建
cd <仓库根目录>/research
mkdir _clones -Force | Out-Null; cd _clones
git clone --depth 1 --filter=blob:none --sparse https://github.com/zmkfirmware/zmk.git zmk
cd zmk
git sparse-checkout set app/boards app/module docs/docs

# 穷举 charlieplex 引用
Get-ChildItem -Recurse -File | Select-String -Pattern 'charlieplex' -List

# 检查是否真有 shield 在用
Get-ChildItem -Recurse -File -Include *.dts,*.dtsi,*.overlay,*.keymap,*.conf |
  Select-String -Pattern 'charlieplex'
```
