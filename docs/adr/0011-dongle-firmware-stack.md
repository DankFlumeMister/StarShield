# Dongle 固件技术栈：ESP32-S3 + ESP-IDF 官方 HID 示例

**状态：🟢 已决定（用户 2026-09）—— 第一版做 Dongle；优先复用官方/社区组件**
**日期：2026-09**
**关联：ADR-0001 修订（Dongle 形态 = BLE HID 主机）、ADR-0009（三档开关的「2.4G」档即本 Dongle）**

## 背景与约束

ADR-0009 的三档开关要求「2.4G」档 = 键盘经 BLE 连一块 USB Dongle。
该 Dongle 必须自己充当 **BLE central + HID-over-GATT 客户端**，再以 **USB HID** 转发给主机
（ZMK 没有 HID 主机能力，见 ADR-0001 修订）。

**用户要求：多做社区方案，不要自己写。**

但这条要求撞上一个硬约束 —— 见下。

## 🔴 决定性的约束：小尺寸 Dongle 的开源实现**全部不可合法复用**

| 项目 | ★ | 许可证 | 平台 | 能否用 |
| --- | --- | --- | --- | --- |
| `hirosatosou/roba-ble-hid-bridge` | 2 | **NOASSERTION**：bridge 固件为 `LicenseRef-Nordic-5-Clause`（派生自 NCS 例程，且**限制芯片**） | nRF52840 | ❌ |
| `ShiniNet/zmk-usb-bridge` | 1 | **未声明** | nRF52840 | ❌ |
| `anisehid`/`xia0`/`hid-proxy-for-ble-keyboard` | 29 | **未声明**（同项目疑似换过组织名，待核） | ESP32-C3 + CH9329 | ❌ |
| `mosquito/ble-hid-bridge` | 8 | **未声明** | ESP32-S3 | ❌ |
| `lvntbkdmr/ble-to-hid` | 3 | **未声明** | XIAO nRF52840 | ❌ |
| `duronald/hid-proxy-for-ble-keyboard` | — | **未声明**（`xia0` 项目的 ESP32-S3 fork） | **ESP32-S3 单芯片** | ❌ |
| `yaochao128/esp_hid_host2` | — | **未声明** | ESP32 全系（含 S3） | ❌ |

> 📌 **2026-09-18 补充调研（应「社区有没有 ESP32-S3 做 Dongle 的先例」之问）**：
> 上面最后三行是本轮新增。**架构先例是确凿的** ——
> - **`duronald/hid-proxy-for-ble-keyboard`**：自述 *"now for esp32s3 and without any needed extra parts"*，
>   键盘连 ESP32-S3，S3 同时对电脑枚举为 USB HID 设备 —— 代码正是
>   **官方 `esp_hid_host` + `tusb_hid` 两块拼起来的**，与 **ADR-0011 选定的架构完全一致**；
> - **`yaochao128/esp_hid_host2`**：官方 `esp_hid_host` 示例 + TinyUSB HID 设备类的组合，
>   明确列出支持 **ESP32-S3**；
> - ⭐ **`xia0/hid-proxy-for-ble-keyboard`（ESP32-C3 + CH9329 版）自述
>   *"This was tested on following keyboards: zmk based keyboards"***
>   ⇒ **「ESP-IDF `esp_hid_host` 能正常对接真实 ZMK 键盘」已有社区实测自述**。
>   这直接命中本项目最大的未验证项（见下「未决 / 未核实」第 5 条），风险大幅下降 ——
>   但**仍需自测**（自述不等于可复现的测试报告，且版本会漂移）。
>
> 这些项目的**代码仍然不可复制**（许可证未声明/不兼容），但「架构有人跑通过」这一事实
> 与代码许可无关，价值是实打实的。另外 `xia0` 项目的几个设计细节值得当**思路参考**
> （照思路不照代码）：按 **HID service UUID `0x1812` + Appearance `0x03C1`（键盘）** 过滤扫描目标、
> LESC Just Works 配对、用 NVS 记住已配对键盘地址、用 LED 闪烁模式区分「扫描新设备 /
> 扫描已知设备 / 已连接」三种状态。

**未声明许可证 = 默认保留所有权利**，不能复制、修改或分发。
本项目是 **CERN-OHL-S-2.0**，若 Dongle 固件抄自无许可代码，整个开源许可链就断了
（这正是本项目此前重建过一次仓库的原因）。

**可合法复用的 MIT 方案只有树莓派系**（见下文备选），**都不是拇指 Dongle**：

| 项目 | ★ | 许可证 | 平台 |
| --- | --- | --- | --- |
| `bahaaador/bluetooth-usb-peripheral-relay` | **334** | **MIT** | 树莓派 Zero 2 W（Go） |
| `quaxalber/bluetooth_2_usb` | 89 | **MIT** | 树莓派（Python） |
| `tadakado/zmk-ble-mouse-host` | 4 | **MIT** | ZMK 模块（**仅鼠标**） |

## 决策

**采用 ESP32-S3 + ESP-IDF 官方组件拼装**，而不是移植任何第三方 Dongle 工程：

| 环节 | 用什么 | 许可 |
| --- | --- | --- |
| BLE HID 主机（扫描/连接/配对/**接收 HID 报告**） | **ESP-IDF 官方示例 `examples/bluetooth/esp_hid_host`**（组件 `esp_hid` 的 `esp_hidh`） | **Apache-2.0** ✅ |
| USB HID 设备（向主机枚举为键盘） | **ESP-IDF 官方示例 `examples/peripherals/usb/device/tusb_hid`**（TinyUSB） | **Apache-2.0** ✅ |
| 连接参数固定、灯效/指示灯转发等 | 自己写少量胶水 | 本项目 |

**为什么这仍然算「用社区方案」**：我们**不自己实现 BLE 协议栈、GATT 客户端或 USB 栈** ——
这三块全部是 Espressif 官方维护的组件与示例。
需要自写的只有「把 `esp_hidh` 收到的报告转发给 TinyUSB」这一段胶水。

**证据**：官方 `esp_hid_host` 示例自述（已核对 v5.3.1 README）：

> *"the HID host will scan the surrounding Bluetooth HID device and try to connect…
> the HID host will dump the HID device information and **can receive the data sent by the HID device**"*
> 支持目标含 **`ESP32-S3`**。

⇒ 最难的一步（BLE HID 客户端）官方已给出可运行示例。

## 为什么选 ESP32-S3 而不是 nRF52840

| 判据 | ESP32-S3 | nRF52840 |
| --- | --- | --- |
| 许可证 | ✅ **Apache-2.0 全链** | ❌ 有可跑的方案（roba），但**固件必然落在 Nordic-5-Clause**（NCS），与 CERN-OHL-S 冲突 |
| USB | ✅ 原生 USB OTG | ✅ 有 |
| 官方 HID 主机示例 | ✅ `esp_hid_host` | ⚠️ NCS 有 `central_hids` 例程（但即许可证问题来源） |
| 与键盘控制器同生态 | ❌ 不同（键盘是 nRF52840） | ✅ 相同 |

⇒ **许可证优先级高于生态一致性。**

## 已知的实现陷阱（来自社区实践，必须记账）

1. 🔴 **`CONFIG_BT_GATTC_NOTIF_REG_MAX` 默认只有 5** ——
   不少键盘会注册 8+ 个 notification 订阅，默认值会**静默丢弃键盘的 INPUT report 订阅，
   导致按键完全不响应**。⇒ **必须调大**（社区实践用 16）。
   这类「静默失败」最难排查，务必先配好。
2. ⚠️ **配对方式**：ZMK 硬选 `BT_SMP_SC_PAIR_ONLY`（要求 LESC），
   而 `CONFIG_ZMK_BLE_PASSKEY_ENTRY` **默认关** ⇒ 走 **Just Works**，
   Dongle 无需显示/键盘。**不要开启 passkey entry**
   （ZMK 的 `passkey_display` 回调是被注释掉的，只能输入不能显示）。
   注：官方 `esp_hid_host` 示例日志里出现 numeric comparison 配对，
   那是示例自身的配置，**需改成 Just Works**。
3. ⚠️ **Caps Lock 等 LED 输出报告可能无法转发**（roba 的限制来自 `CONFIG_ENABLE_HID_INT_OUT_EP=n`）。
   本项目若指示灯由 ZMK 自身状态驱动则不受影响，**待确认**。
4. ⚠️ **重新配对需两端清 bond**（Dongle 侧 + 键盘 `&bt BT_CLR`），只清一端会 key-mismatch。
5. ⚠️ 低延迟要靠「固定连接参数」：参考 roba 的做法 ——
   central 钉 `min=max=7.5 ms, latency 0`，并**拒绝**键盘发来的变慢请求
   （ZMK 键盘自身请求的是 15 ms / latency 30）。
   ⚠️ 但「Dongle 比直连主机更快」**从未被实测**（见 ADR-0001 修订），
   **不得作为选型理由**。

## 备选方案（若不接受自写胶水）

**树莓派 Zero 2 W + `bahaaador/bluetooth-usb-peripheral-relay`（MIT，★334）**
—— 真正零固件开发，插卡即用。代价：
- ❌ 不是拇指 Dongle（Pi Zero 约 65 × 30 mm，需外壳与 USB 线）
- ❓ **BLE(HOGP) 键盘兼容性未明确**：该项目 README 只写 *"Bluetooth keyboards and mice"*，
  未提 BLE / HOGP。它依赖 Linux BlueZ 暴露输入设备，理论上 BLE HID 可行，**但未验证**。
- ✅ 优点是**可以先拿它验证整条架构**，再决定是否投入 ESP32 固件

⇒ **建议：第一版并行推进** —— 先用树莓派方案把「键盘→Dongle→主机」整条链路验证通，
再用 ESP32-S3 做拇指版。两者都符合许可证要求。

## 未决 / 未核实

- ❓ 第一版是否真的**并行**做树莓派验证（见上「建议」）。
- ❓ ESP32-S3 具体型号与 USB 连接器形式（USB-A 公头直插 vs Type-C + 线）。
- ❓ Dongle 的外壳与复位/Bond 清除按钮布置。
- 🟡 ~~`esp_hidh` 对 ZMK 报告描述符的兼容性（官方示例是对着自家 `esp_hid_device` 调的，
   **对真实 ZMK 键盘未验证**）~~
   **⇒ 2026-09-18 风险下调**：社区项目 `xia0/hid-proxy-for-ble-keyboard` 自述
   *"tested on following keyboards: zmk based keyboards"*，且其代码正是基于官方
   `esp_hid_host` 示例（见上文补充调研）⇒ 「ESP-IDF HID 主机 ↔ 真实 ZMK 键盘」已有社区实测先例。
   **仍需自测**（自述不可复现、版本会漂移），但已从「完全未知」降为「有先例待复核」。
   ⇒ 配套建议不变：C5 一开始就买 ESP32-S3 最小系统板，第一时间跑通这一环。
- ❓ 上文「陷阱 3」Caps Lock 输出报告对本项目指示灯方案的实际影响。

## 附录 A：功耗对比 —— ESP32-S3 vs nRF52840（2026-09-18，应「哪种更省电」之问）

**结论先行：nRF52840 确实省电得多（约 5–10 倍），但这个差异不构成换芯片的理由** ——
① Dongle 是插在电脑 USB 口上取电的，两者都远低于端口 500 mA 的能力；
② 许可证约束是**一票否决**项，不随功耗结论翻转。

### 数据手册级指标

| 指标 | ESP32-S3（Espressif 数据手册） | nRF52840（Nordic 数据手册 / 官方工具） |
| --- | --- | --- |
| BLE 发射 @0 dBm（100% 占空） | **187–189 mA** | **4.8–6.4 mA**（DC/DC @3 V；Nordic 新口径 6.4） |
| BLE 接收 | **93 mA** | **4.6–6.4 mA** |
| CPU 空闲（射频关闭） | modem-sleep 80 MHz **10.5–18.4 mA**（160 MHz 14–21；240 MHz 20–28） | System ON 睡眠 **1.5 µA**；CPU 64 MHz **3.2–5.6 mA** |
| USB 已枚举、空闲 | —（未查到单列值，需实测） | **+2.7 mA**（Nordic 官方 Power Profiler 工具值） |
| 深睡 | 7–25 µA | 0.4–1.5 µA |

### 平均电流估算（BLE HID 主机，CI 7.5 ms / latency 0）—— 🟡 **[估算]，未实测**

| | ESP32-S3 | nRF52840 |
| --- | --- | --- |
| 射频事件（约 5% 占空 × ~100 / ~6 mA） | ≈5–9 mA | ≈0.3–0.5 mA |
| CPU 基线（事件间） | ≈10–18 mA（modem-sleep） | ≈0.15 mA（CPU 只在事件时跑） |
| USB 活跃 | 含在上面 | **≈2.7 mA（占大头）** |
| **合计量级** | **约 15–25 mA** | **约 3–3.5 mA** |

### 为什么这个差异对本项目影响很小

- Dongle 由 **USB 总线供电**：15–25 mA ≈ 0.05–0.08 W（3.3 V），远低于端口 500 mA 上限；
  对笔记本电池也可忽略。发热同样可忽略（小壳里 0.1 W 量级）。
- **真正影响续航的是键盘侧**（nice!nano，用电池），而键盘侧功耗主要由**连接参数**决定，
  与 Dongle 用哪颗芯片无关。⚠️ 反向提醒：ADR-0011 的低延迟做法是 central 把
  **CI 钉在 7.5 ms / latency 0** 并拒绝键盘变慢的请求 —— 这会让**键盘**的射频每 7.5 ms 醒一次，
  键盘功耗显著上升。对照：Nordic 官方口径下 nRF52840 peripheral「已连接、无数据」仅 **19.25 µA**
  （那是在长间隔下）⇒ **延迟 vs 键盘续航是一个独立于芯片选择的取舍点**，值得在 C5 实现时留一个
  可调参数（例如允许 latency 4，按一次 7.5 ms 间隔变成「最多 4 个间隔不回话」）。
- 若想在 Espressif 家族里找更省电的替代：ESP32-C6 / H2 的 BLE 电流明显更低
  （C6 TX 78–82 mA、H2 24 mA），但它们**没有 USB OTG**（只有 USB Serial/JTAG，不能枚举成 HID 设备）
  ⇒ **ESP32-S3 仍是该家族里唯一能同时满足「BLE 主机 + USB HID 设备」的选择**。

### 结论

**维持 ADR-0011 的选择（ESP32-S3）不变。** 功耗差异真实存在但被「总线供电」这个事实稀释；
许可证约束则不可绕过。若日后出现「Dongle 需要电池供电」的新需求，再重新评估（届时 nRF52840
方案仍受 Nordic-5-Clause 阻塞，需另找合规实现）。

## 附录 B：市面上的 Dongle 都用什么芯片（2026-09-18，应「看看别人的 dongle 用什么」之问）

### B.1 量产键盘的 2.4G 接收器：**专有协议 + 同厂商配套 SoC**

量产三模/双模键盘的接收器**几乎不是 BLE HID 主机**，而是与键盘端共享同一套
**专有跳频协议 + 配对**的收发器 —— 这正是它们能做到 1 ms 级延迟、免配对即插即用的原因，
也是「必须成对买」的原因。主流供应商（来源：Telink 数据手册自述用途 + 国产 PCBA 方案商综述）：

| 厂商 | 代表芯片族 | 关键事实 |
| --- | --- | --- |
| **Telink（泰凌微）** —— 国产量产键鼠的主流 | `TLSR8208` / `8355` / `8373` / `8666` / TLSR9 | 数据手册**自述用途**就是「无线键盘、无线鼠标、无线 USB dongle」；官方提供 **Dongle 参考设计**（`TLSR8208ADG56D`）；`TLSR8208` 同时支持 **BLE 5.3 + 2.4G 私有双栈**、USB FS、**键盘扫描 8×18 矩阵** |
| **Nordic** | nRF52 系列（`52810/52820/52832/52833/52840`） | 中高端无线外设多用；支持 2.4G 专有协议栈 + BLE |
| **TI** | `CC254x` / `CC264x` | 较老方案，仍在入门产品里出现 |
| Realtek / 杰理 / 中科蓝讯 等 | — | 多见于入门价位 |

**功耗参照**（Telink 官方数字，可直接对比我们的估算）：
`TLSR8666` **Dongle 模式 27 mA**、鼠标 8 mA、suspend 16 µA、深睡 1 µA；
`TLSR8208` RX 9.1 mA / TX@0 dBm 9.5 mA（LDO）、休眠 0.55–1.3 µA。
⇒ **USB 供电的 dongle 耗 20–30 mA 属行业常态** —— 附录 A 里 ESP32-S3 估的 15–25 mA 并不异常。

### B.2 开源/DIY 的 BLE HID 主机 Dongle：样本少，集中在两类芯片

（样本 = ADR-0011 正文调研过的那几个，许可证见正文表格）

| 平台 | 项目 | 备注 |
| --- | --- | --- |
| **nRF52840** | `roba-ble-hid-bridge`、`ShiniNet/zmk-usb-bridge`、`lvntbkdmr/ble-to-hid` | 都靠 Nordic NCS 的 central 例程 ⇒ 固件落在 **Nordic-5-Clause**，不可复用 |
| **ESP32-S3** | `mosquito/ble-hid-bridge` | 未声明许可证；架构与我们相同 |
| **ESP32-C3 + `CH9329`** | `anisehid/hid-proxy-for-ble-keyboard` | C3 没有 USB OTG，所以外挂一颗 **专用 USB HID 芯片** 来当 USB 设备 —— 多一颗 IC 换 USB 栈免开发 |
| **树莓派** | `bahaaador/…`（MIT）、`quaxalber/…`（MIT） | 唯二许可证干净的，但体积大（用户已否决，见 C6） |

### B.3 结构性结论

1. **「BLE HID 主机式 Dongle」在量产界没有先例。** 不是做不出来，而是量产产品的键盘端固件
   也是自家写的，不必迁就「标准 BLE HID」，直接走专有协议更省电、延迟更低、BOM 更便宜。
2. **我们走 BLE HID 主机是 ZMK 生态约束下的必然**（ADR-0001：ZMK 只发标准 BLE HID）——
   这与「大电池找不到开源先例」是同一类结构性事实：**量产特征的开源先例天然不存在**。
3. **Telink 能不能给我们用？** 芯片便宜、支持 BLE master + USB，SDK 公开在 GitHub/Gitee 且
   `tc_ble_sdk` 仓库标注 **Apache-2.0**，还带 **HID dongle 参考应用**。
   ⚠️ **但 BLE/RF 协议栈本体是闭源预编译库**：`proj_lib/*.a`（如 `liblt_8267.a`），
   官方手册原文 *"Since this folder is supplied in the form of library files (e.g. liblt_8267.a),
   the source files are **not open to users**."* ⇒ 与 CERN-OHL-S 的开源链存在冲突，
   且该库只跑在 Telink 芯片上。（2026-09-18 核实，取代此前「按私有授权处理」的假设）

### B.4 对本项目的意义

**维持 ADR-0011（ESP32-S3 + ESP-IDF 官方示例）不变。**
- 专有协议路线在许可证上同样不通（Telink/Nordic SDK 都不可复用），且要 fork/自写整条 2.4G 栈；
- ESP32-S3 路线的两个官方组件都是 Apache-2.0，是**唯一全链合规**的选择；
- 功耗（附录 A）与成本（S3 模组几十元级）都不构成反对理由。

## 附录 C：能不能换成 Telink、像商业键盘那样共享专有跳频协议？（2026-09-18 评估）

**结论：不建议第一版换。** 分三层说明。

### C.1 根本障碍：「共享协议」要求**两端**都跑这套协议，而键盘端被钉死了

商业键盘之所以省事，是因为**键盘端和 Dongle 用同一家芯片**（Telink↔Telink），
跳频表、配对、省电调度全是厂商现成的。本项目的结构是：

```text
键盘端 = nice!nano v2（nRF52840）+ ZMK   ←—— ADR-0001/0003/0009 已定，且实物零
Dongle 端 = 待定（现 ESP32-S3）
```

- Telink 的 2.4G 栈是**只跑在 Telink 芯片上的预编译库**（`proj_lib/*.a`，源码不开放），
  **键盘端（nRF52840）根本用不上** ⇒ 「Dongle 换 Telink」换不来商业键盘那套现成协议。
- 协议得**自己从零写**（包格式 / 跳频表 / 配对与密钥交换 / 重传 / 省电调度），且**两端都要写**。
- 写完还得**塞进 ZMK**：ZMK 的按键输出路径只有 BLE HID（HOGP）和 USB 两条，
  没有「自定义 2.4G 传输」的挂载点 ⇒ 这是一次大规模自定义固件，直接违背
  **ADR-0009 的「键盘侧零自定义固件」**与项目「新手可复刻」的定位。
- 若把键盘端也换成 Telink = 放弃 ZMK 与 nice!nano 生态，等于项目重来
  （ADR-0001 已明确：真 2.4GHz **推迟到后续版本** —— 这个判断仍然成立）。

### C.2 收益有更便宜的替代；还有一项负收益

| 专有协议的收益 | BLE HID 主机路线的对应替代 |
| --- | --- |
| 1 ms 级延迟 | central 钉 **7.5 ms CI** + 拒绝键盘变慢请求（roba 同做法）——对键盘而言 7.5 ms 已是主流无线水平 |
| 更低功耗 | **BLE slave latency**（附录 A 已记为 C5 的可调参数） |

**负收益**：专有协议把键盘**锁死在自家 Dongle 上** —— 接收器丢失/损坏，2.4G 档即报废
（商业键盘同样有这个问题，只能买原厂配件）。而 BLE HID 主机路线下，
键盘随时能连手机 / 平板 / 电脑蓝牙 / 任何 BLE 主机 —— 对**开源可复刻**的项目，这是实打实的价值。

### C.3 单看「Dongle 端换 Telink」：可行，但被工程风险压过

`TLSR8208` 支持 **BLE master + USB FS**，SDK 仓库 Apache-2.0，官方还有 **HID dongle 参考应用**
—— 作为**现有架构（BLE HID 主机）下的 Dongle 芯片**它完全可行，且更便宜、更省电（~10 mA 量级）。
与 ESP32-S3 的真实取舍：

| | ESP32-S3 | TLSR8208 |
| --- | --- | --- |
| 所需的两块（BLE HID 主机 + USB HID 设备） | ✅ **官方现成示例**（`esp_hid_host` + `tusb_hid`） | 🟡 要自己在 SDK 里拼（有 HID dongle 参考，但非现成组合） |
| 协议栈形态 | 源码 / 官方组件 | ⚠️ **闭源预编译库 `proj_lib/*.a`**（源码不开放） |
| 工具链 | GCC + ESP-IDF（生态大、教程多） | TelinkIoTStudio（厂商 IDE，社区小） |
| 成本 / 功耗 | 稍高 | 更低 |

⇒ **第一版维持 ESP32-S3**（工程风险最低、全链许可最干净）；**若日后要降 Dongle BOM 成本，
Telink 值得重新评估**，前提是先解决 `proj_lib/*.a` 闭源库与 CERN-OHL-S 的相容性问题。

## 附录 D：还有没有更优的 Dongle 方案？（2026-09-18 第二轮搜寻）

### D.1 ⭐ 重量级发现：`jfedor2/hid-remapper` 的蓝牙固件（nRF52840 路线）

**这是目前找到的、成熟度最高的同类先例**：

- ★**1.4k**、40 个 release、**持续维护**（最近 2025-06）；
- **软件 MIT**（可合法复用！这是与所有 ESP32 个人项目最大的差别）、硬件 CC BY 4.0；
- 蓝牙固件 = **nRF52840 作 BLE central + HOGP client + USB HID 键鼠聚合** —— 与本项目 Dongle
  功能**完全同构**；官方直接支持 **Seeed XIAO nRF52840** / Adafruit Feather nRF52840，
  **提供现成 UF2**（构建用 NCS v2.2：`nordicplayground/nrfconnect-sdk:v2.2-branch`）；
- 深层架构（DeepWiki 概览）：`bt_scan`（区分「已绑定地址」与「新设备」的扫描过滤）→
  `bt_hogp`（HID over GATT，多连接数组）→ `report_q/descriptor_q` → USB HID 栈；
  LED 状态机 + 用户开关配对/清 bond —— 这些交互设计都是现成参考。

**附带一个 B 路线的完整先例**：`lvntbkdmr/ble-to-hid`（XIAO nRF52840、NCS v2.6、
BLE central + HOGP + USB HID 键盘、**明确对接 Corne 无线键盘**（Corne 主流跑 ZMK）、
7.5–15 ms BLE 间隔 + 1 ms USB 轮询、passkey 配对 + flash 存 bond）—— 其 README 的
模块划分（`ble_central` / `hogp_client` / `usb_hid` / `hid_bridge`）本身就是一份实现大纲。

### D.2 路线对比：ESP32-S3（现选） vs nRF52840 + NCS/HOGP

| 维度 | **ESP32-S3 + ESP-IDF（现选）** | nRF52840 + NCS（`BT_HOGP` + USB HID） |
| --- | --- | --- |
| 许可链 | ✅ **全链 Apache-2.0** | ⚠️ 项目代码 MIT，**但依赖 NCS 的 Nordic 组件**：SoftDevice Controller 为**闭源二进制**、`bt_hogp`/`bt_gatt_dm` 为 Nordic 库。Nordic-5-Clause 限制「只能用于 Nordic 芯片」——用在本项目的 nRF52840 Dongle 上**是允许的**，但会给 CERN-OHL-S 项目引入非开放依赖，需逐文件标注许可（这正是当初选 ESP32-S3 的原因） |
| 先例成熟度 | 官方示例 + 个人项目 fork ×2（无许可） | ⭐ **知名、活跃维护、MIT、带现成固件与文档** |
| ZMK 兼容性 | `xia0` 项目自述 tested on ZMK | hid-remapper 社区广泛用于无线键盘；`ble-to-hid` 明确对接 Corne |
| 功耗 | 15–25 mA | **~3 mA**（USB 占 2.7 mA）——对 USB 供电无所谓，发热更低 |
| 硬件成本 | S3 模组，几十元级 | XIAO nRF52840 / PCA10059，几十元级（相当） |
| 开发工作量 | 两块官方示例拼装 | 要自己写桥（但 **MIT 代码可合法抄** hid-remapper） |
| 工具链 | ESP-IDF | NCS + west（更重，但本项目已熟 Zephyr） |

### D.3 一个被忽略的「零开发」兜底：通用蓝牙适配器

本项目的键盘**本身就是标准 BLE HID 设备** —— 对「主机没有蓝牙」的场景，
**任何 ¥20 级的通用蓝牙 USB 适配器（CSR8510 等）+ 键盘的蓝牙档**就是零固件成本的解。
自制 Dongle 的真正价值不在「让没蓝牙的主机能用」，而在：
① 三档开关的**完整体验**；② **即插即用**（免配对管理，bond 存在 dongle 里）；
③ 可复刻的**开源** Dongle。⇒ 应写进教程：没有蓝牙的主机也可以先用通用适配器顶上。

### D.4 其余路线复核（均已排除）

| 路线 | 排除原因 |
| --- | --- |
| ESP32-C6 / H2 | 无 USB OTG（只有 USB Serial/JTAG），不能枚举成 HID 设备 |
| RP2040 / RP2350 | 无 BLE 射频 |
| Telink TLSR8208 | 栈本体闭源（附录 B）；可行但工程风险高 |
| ZMK 分体 central | ADR-0001 已否（键盘离开 Dongle 变砖） |
| 真 2.4G 专有协议 | 附录 C：键盘端（ZMK）无法承载，收益有 BLE 替代 |

### D.5 结论

**第一版维持 ESP32-S3 不变** —— 许可链最干净、官方示例直接对口、ZMK 兼容性有先例。
**但把「nRF52840 + NCS HOGP」正式记录为 B 方案**：如果将来发现 ESP32-S3 在配对健壮性 /
多连接 / 延迟上不达标，切到这条路线的代价是「改用 XIAO nRF52840 + 参考 hid-remapper（MIT）」，
不是从零开始。另外 **hid-remapper 的现成 UF2 还有一个零开发用途**：
刷进一块 XIAO nRF52840 即可立刻实测「ZMK 键盘 ↔ BLE HID 主机」这一环（若愿意花几十元）——
这是比树莓派便宜得多的验证途径，是否做由你决定。

## 附录 E：🔴 重大新发现 —— `efogdev/zmk-esb-endpoint`（单体键盘可用的 ESB 方案，2026-09-18 晚）

**触发**：用户坚持「还有一个专门做 Nordic 2.4G 的高星 ZMK 分支」⇒ 经 GitHub API 全量检索
`zmk+esb`（按星排序），除 55★ 的 `badjeff/zmk-feature-split-esb`（**仅分体**）外，
发现 **`efogdev/zmk-esb-endpoint`** —— 一个**正好命中本项目全部约束**的方案：

### E.1 它是什么

- ZMK **west module**，把 ESB 实现为**第三条输出端点（endpoint）**，**不是 split transport**
  ⇒ **单体（unibody）键盘可用**，明确不支持分体 —— 恰好是我们的形态（95 键单体）；
- **复用最后一个 BLE 配置文件槽位作为开关**：选中该 profile 时 ESB 接管射频、USB/BLE HID 静默；
  切到其他 profile 时 BLE 恢复 ⇒ **三档开关（ADR-0009）天然映射**：
  有线 = USB、蓝牙 = profile 0..N-2、2.4G = 最后一个 profile，**运行时切换、免重刷**；
- ⭐ **只在 ZMK v0.3.0 上测试过** —— 与本项目 `west.yml` 钉住的版本**完全一致**；
- 许可：模块 **MIT**；vendored 的 Nordic ESB 源文件为 **LicenseRef-Nordic-5-Clause**
  （限 Nordic 芯片 —— 我们键盘是 nRF52840，满足；且这是**源码可见**的 NCS 组件，不是闭源 blob）；
- Dongle 端：**协议已文档化**（`zmk_esb/protocol.h`：BEACON / PAIR_REQ / PAIR_RESP /
  HID_REPORT / DISCONNECT；HID 报文体直接用 ZMK 的 `zmk_hid_*_report_body`，dongle 加 report-id
  前缀即可直送 USB HID），配对含 6 字节 `device_id` 验证；**官方提供参考 dongle 固件**
  （`efogtech/endgame-trackball-firmware/dongle-1k-firmware`，1 kHz 轮询）。

### E.2 风险与代价（必须如实列出）

| # | 风险 | 严重度 |
| --- | --- | --- |
| 1 | **只按 nRF52833 调优**；nRF52840（nice!nano v2）作者自述「应该能工作但不确定」——PPI 掩码、VTOR 向量表补丁（假定 64 向量）、TIMER2 占用都要核对 ⇒ **移植与实测是我们自己的活** | 🔴 高（但两家同属 nRF52 族，RADIO/PPI 架构相同） |
| 2 | 5★、单维护者、无 release ⇒ **长期维护风险**（我们钉 v0.3.0 可缓解——它就是在 v0.3.0 上测的） | 🟡 中 |
| 3 | **无端到端延迟 / 功耗数据**（只有射频时序参数）⇒ 「1 ms / 更省电」目前是**推断** | 🟡 中 |
| 4 | Dongle 端 PRX 固件要自己写（有参考实现）⇒ 与现选方案的工作量相当，但**换了芯片族** | 🟡 中 |
| 5 | 强耦合 ZMK 内部（接管 `RADIO_IRQn`、链接器包装 BLE 广播函数）⇒ **升级 ZMK 版本时可能碎**（我们已钉版本，影响可控） | 🟡 中 |
| 6 | 键盘端不再是「纯原版 ZMK」——多了一个 module（modules 是 ZMK 的正规扩展机制，教程可写，但与 ADR-0009「零自定义固件」的字面承诺有出入） | 🟢 低 |

### E.3 两条 v1 路线对比（最终决策表）

| 维度 | **方案 A（现选）：ESP32-S3 BLE HID 主机** | **方案 B（新候选）：nRF52 ESB** |
| --- | --- | --- |
| 键盘端 | 原版 ZMK，零改动 | 原版 ZMK + `zmk-esb-endpoint` module（MIT） |
| Dongle 硬件 | ESP32-S3（不同厂商） | **nRF52840**（与键盘同族，如 XIAO nRF52840） |
| Dongle 固件 | `esp_hid_host` + `tusb_hid`（官方示例） | ESB PRX + USB HID（协议已文档化 + 参考固件） |
| 「2.4G」的真实含义 | BLE（连接间隔下限 7.5 ms） | **真·专有 2.4G**（ESB，理论 1 ms 级，未实测） |
| 许可 | ✅ 全链 Apache-2.0 | 🟡 module MIT + vendored ESB 为 Nordic-5-Clause（限 Nordic 芯片，本组合满足） |
| 与键盘的同族性 | ❌ 不同 | ✅ 同为 Nordic/Zephyr |
| 先例 | 官方示例 + `xia0`（ZMK 实测）+ hid-remapper | 模块本身即先例（v0.3.0 实测）；但无商用产品、无第三方复现记录 |
| 主要风险 | 「2.4G」名不副实；延迟下限 7.5 ms | 🔴 nRF52840 移植未验证；单维护者模块；无性能数据 |
| 教程复杂度 | 低（用户 fork 键盘仓即可） | 中（用户要同时构建键盘 + dongle 两个固件，且含第三方 module） |

### E.4 决策状态：✅ **已定（用户 2026-09-18）：先验证再定**

两个方案都**可行且有先例**，取舍是真实的：
- **要「真 2.4G、低延迟、两端同芯片、与商业键盘同构」** ⇒ 方案 B；
- **要「工程风险最低、全链 Apache-2.0、先例最多」** ⇒ 方案 A（现选）。

⭐ **用户拍板：先验证再定。** 验证的唯一核心问题 = **模块能否移植到 nRF52840**
（作者只按 nRF52833 调优；需核对 PPI 掩码 / VTOR 向量表 / TIMER2 / HFXO）。
可执行计划（物料 ≈ 2 块 XIAO nRF52840、步骤、5 条通过判据、回退路径）
见 **`docs/esb-endpoint-validation.md`**，挂待办 **C7**。
- 通过 ⇒ Dongle 定为 **nRF52840 ESB PRX + USB HID**（方案 B）；
- 失败 ⇒ 维持 **ESP32-S3 BLE HID 主机**（方案 A），损失仅一块开发板；
- **B2（键盘控制板子图）不受影响，可并行推进**；Dongle 部分在出结果前不定型。
