# 控制器 footprint 同时兼容 nice!nano v2 与 SuperMini nRF52840

nice!nano v2（约 200 元）是参考模块；SuperMini 克隆板（约 20 元）在 ZMK 中功能等价，但睡眠漏电约 700µA（拆除一颗 5.6KΩ 电阻可修复），且 LED 颜色相反。

我们把 PCB 控制器焊盘设计为两者通用：标准 2×12 通孔 + Mill-Max 插座（对应 nice!nano 引脚），SuperMini 多出的 3 个 GPIO 不布线。

## Consequences

用户可自选模块；教程可提供「拆一颗电阻」的预算路线。代价是板子略大，丝印需标注兼容性说明。
