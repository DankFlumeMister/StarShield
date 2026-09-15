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
| `anisehid/hid-proxy-for-ble-keyboard` | 29 | **未声明** | ESP32-C3 + CH9329 | ❌ |
| `mosquito/ble-hid-bridge` | 8 | **未声明** | ESP32-S3 | ❌ |
| `lvntbkdmr/ble-to-hid` | 3 | **未声明** | XIAO nRF52840 | ❌ |

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
- ❓ `esp_hidh` 对 ZMK 报告描述符的兼容性（官方示例是对着自家 `esp_hid_device` 调的，
   **对真实 ZMK 键盘未验证**）。
- ❓ 上文「陷阱 3」Caps Lock 输出报告对本项目指示灯方案的实际影响。
