# 控制器 footprint 同时兼容 nice!nano v2 与 SuperMini nRF52840

nice!nano v2（约 200 元）是参考模块；SuperMini 克隆板（约 20 元）在 ZMK 中功能等价，但睡眠漏电约 700µA（拆除一颗 5.6KΩ 电阻可修复），且 LED 颜色相反。

我们把 PCB 控制器焊盘设计为两者通用：标准 2×12 通孔 + Mill-Max 插座（对应 nice!nano 引脚），SuperMini 多出的 3 个 GPIO 不布线。

## Consequences

用户可自选模块；教程可提供「拆一颗电阻」的预算路线。代价是板子略大，丝印需标注兼容性说明。

## 修订（2026-09）：SuperMini 路线**降级为不保证**（原前提有两处错误）

原文把 SuperMini 描述为「在 ZMK 中功能等价」。**该前提不成立**，两处已核实的问题：

1. 🔴 **SuperMini 不被 ZMK 官方支持。**
   ZMK 官方仓库没有 SuperMini 的板级定义，它是靠**蹭 nice!nano 的板定义**
   （同一 nRF52840 + 相同排针）才能跑起来。这意味着**上游一旦改动 nice!nano 定义，
   SuperMini 可能无声失效**，而本项目无法为此负责。
2. 🔴 **电池 ADC 脚冲突。**
   SuperMini 的电池电压检测脚与 nice!nano 的**不是同一个引脚**
   （nice!nano 走 `VDDH` 内部测量；SuperMini 用独立 ADC 脚）。
   ⇒ 同一块 PCB 不可能同时正确测量两种模块的电池电压，
   **需要一颗 0 Ω 跳线（或焊盘选择）来切换**。
   「拆一颗 5.6 kΩ 电阻修睡眠漏电」是**第三个**独立差异。

## 决策（用户 2026-09）

**第一版按 nice!nano v2 设计并保证其正确性；SuperMini 仅为「焊盘兼容、不保证」。**

- PCB 焊盘保持 2×12 通孔 + Mill-Max 插座，SuperMini 物理上能插
- **电池电压检测按 nice!nano 接法布线**，SuperMini 的 ADC 脚**不接**（保持未布线）
- 丝印与文档必须写明：**SuperMini 未经本项目验证，电池电量显示不可用**
- ⚠️ 不得在教程中把 SuperMini 作为「省钱等价方案」推荐

**理由**：本项目面向新手，「看起来能省钱、实际电池显示不对且可能随上游失效」
是最糟的组合。宁可明确不支持，也不要给一个半可用的选项。

> 相关取证：`docs/controller-and-battery-facts.md` 第 1.3 节。
