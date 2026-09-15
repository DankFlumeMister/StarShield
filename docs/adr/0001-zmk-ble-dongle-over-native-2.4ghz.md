# 采用 ZMK + BLE Dongle，而非原生三模

本键盘追求接近 2.4GHz 的无线手感，但所选固件 ZMK 不支持专有 2.4GHz 射频。集成 Nordic Enhanced ShockBurst（ESB）需要 fork ZMK，且 ESB 与 BLE 互斥，还要面对 Nordic Connect SDK 的许可证限制。

我们决定第一版采用标准 ZMK：Body 经 BLE 连接一块独立的 XIAO nRF52840 Dongle，Dongle 作为 BLE central 插入主机 USB。这样用户获得接近 2.4GHz 的体验，而我们无需维护 ZMK 分支。原生 2.4GHz 推迟到后续版本。

## Consequences

固件保持在上游 ZMK，用户可用 GitHub Actions 构建，ZMK Studio 开箱可用。代价是延迟约 4.25ms（而非 1–3ms），且用户需多携带一个 Dongle。

## 修订（2026-09）：Dongle 的形态收紧为「BLE HID 主机」

本 ADR 原文只写了「Dongle 作为 BLE central」，**没有指定它的实现形态**。
在实现三档模式开关（ADR-0009）时发现这个空白是**决定性的**，故在此收紧。

### 不能用 ZMK 官方的「分体 Dongle」形态

ZMK 官方文档描述的 dongle 做法是：Dongle 作为**分体键盘的 central**（用 mock kscan），
键盘编译成**分体从机**。这条路对本项目**不可用**，三条一手证据：

| 证据 | 出处 |
| --- | --- |
| *"The keyboard becomes **unusable without the dongle**"*；从机 *"will not present as keyboard devices when connected over USB and will not advertise as pairable BLE keyboards"* | ZMK Dongle 官方文档（v0.3.0 核对了 `docs/docs/development/hardware-integration/dongle.mdx`） |
| `config ZMK_USB` → `depends on (!ZMK_SPLIT \|\| (ZMK_SPLIT && ZMK_SPLIT_ROLE_CENTRAL))` —— **分体从机连 USB HID 都编译不进去** | `app/Kconfig` |
| 角色由编译期 CMake 参数（`-DCONFIG_ZMK_SPLIT_ROLE_CENTRAL=n`）决定，改回需**重新刷固件**；运行时切换角色是开放需求 issue [#2885](https://github.com/zmkfirmware/zmk/issues/2885)（至今无 PR） | Dongle 官方文档 + issue #2885 |

⇒ 采用分体形态会**同时失去「蓝牙」与「有线」两个模式**，ADR-0009 的三档开关无从实现。

### 采用的形态：Dongle 作为独立 BLE HID 主机

键盘**保持标准 ZMK 蓝牙键盘**（不进分体模式）。Dongle 自己去当 BLE central 连接键盘，
再以 USB HID 转发给主机。这样 Dongle 在键盘眼里只是一个普通蓝牙主机，
三个模式全部落回 ZMK 原生能力（详见 ADR-0009）。

**代价（必须记账）**：

- ⚠️ **ZMK 没有 HID 主机能力** —— 源码中搜不到 `hog_client` / `BT_HIDS_CLIENT`。
  因此 **Dongle 固件不是 ZMK，是独立的固件工程**（不进 ZMK 的 build matrix）。
  ✅ **但不必从零写** —— 已有至少 4 个开源实现可读可改，详见下节。
- ✅ **收益**：键盘**离开 Dongle 仍可用**（蓝牙 / 有线两档），
  消除了原方案「丢 Dongle 即变砖」的风险。
- ✅ 三条腿都是 BLE ⇒ 切模式**不需要整机重启**
  （对比：Keychron 的 2.4G 机型因两套射频栈互斥，切模式要 `app_system_reset()` 整机重启）。

### Dongle 固件：架构有先例，但**代码不能抄**（许可证问题）

⚠️ **本节曾写「不必从零写固件」——该结论是错的，已更正。**

**架构本身确已被实现**，且满足我们的前提（键盘跑**未修改的**原版 ZMK）：

**最强先例：`hirosatosou/roba-ble-hid-bridge`**（nRF52840 + NCS/Zephyr）

- README 原文（**已亲自核对**）：*"runs **unmodified** stock ZMK — all the work is in the dongle."*
- 明确描述了我们设想的三档用法：Dongle 只是*"just one host profile, allowing you to
  switch between the dongle and direct BLE using `&bt BT_SEL`"*
- 技术机制**已从作者的实际 `prj.conf` 逐行核实**：
  ```c
  CONFIG_BT_HOGP=y                          /* HID over GATT 客户端 */
  CONFIG_BT_CENTRAL=y
  CONFIG_BT_GAP_AUTO_UPDATE_CONN_PARAMS=n   /* 不采纳对端"想变慢"的请求 */
  CONFIG_BT_USER_PHY_UPDATE=y               /* 显式请求 2M PHY */
  CONFIG_USB_HID_POLL_INTERVAL_MS=1
  ```
  即：Dongle 作为 central 把连接间隔**钉在 7.5 ms（min=max=6）、slave latency 0**
  并拒绝变慢请求 ⇒「两端都可控」这个低延迟机制是**真实存在且已实现**的。
- ⚠️ 但作者只说 *"faster than direct BLE"* 是**主观感受，无测量数据、无方法学、无样本量**
  ⇒ 标记 `❓ 未测量`，不得当作结论。
- ⚠️ 已知限制（作者自述）：**Caps Lock 之类的 LED 输出报告无法转发**
  （`CONFIG_ENABLE_HID_INT_OUT_EP=n`，没有中断 OUT 端点）；
  当前硬编码适配 roBa 的报告描述；重新配对需**两端都清 bond**。

#### 🔴 致命细节：**没有一个是可抄的开源许可证**

| 项目 | 硬件 | 许可证 |
| --- | --- | --- |
| `hirosatosou/roba-ble-hid-bridge` | nRF52840 | bridge 固件为 **`LicenseRef-Nordic-5-Clause`**（派生自 NCS `central_hids` 例程）；其 LICENSE 文件自述 *"**the Nordic 5-Clause license restricts the chip**"* |
| `ShiniNet/zmk-usb-bridge` | nRF52840 | **未声明** |
| `anisehid/hid-proxy-for-ble-keyboard` | ESP32-C3 + CH9329 | **未声明** |
| `lvntbkdmr/ble-to-hid` | XIAO nRF52840 | **未声明** |
| `mosquito/ble-hid-bridge` | ESP32-S3 | **未声明** |

**未声明许可证 = 默认保留所有权利**，不能合法复制、修改或分发。
⇒ **这些项目只能「参考思路」，代码必须自己写。**

⚠️ 而且 Nordic-5-Clause **正是 ZMK 拒绝原生 2.4GHz 的同一条许可证**
（见本 ADR 修订段末）。若 Dongle 固件也落在 NCS 上，本项目就会染上同一个问题：
**Dongle 固件将不是开源许可**，与 CERN-OHL-S-2.0 的项目定位冲突。

#### ✅ 许可证干净的实现路径：ESP32 + ESP-IDF 自带的 BLE HID Host

**已核实**：ESP-IDF 的 `components/esp_hid` 自带 HID Host：

```
include/esp_hidh.h          HID Host API
include/esp_hidh_gattc.h    BLE HID over GATT 客户端
include/esp_hidh_nimble.h   NimBLE 后端
SPDX-License-Identifier: Apache-2.0     （ESP-IDF 整体亦为 Apache-2.0）
```

⇒ 用 **ESP32-S3（原生 USB OTG）+ `esp_hidh`（BLE HID 客户端）+ TinyUSB（USB HID）**
可以做出**全程 Apache-2.0** 的 Dongle，**绕开 Nordic 许可证**。
代价是这份固件要自己写（工作量大头在 USB HID 描述符与连接参数固定上）。

#### 成品适配器：**不存在通用型**（更正我上一版的建议）

⚠️ 上一版写「可零成本先买成品适配器验证构想」——**该建议不成立**：

- 通用「蓝牙转 USB」适配器这个品类**基本不存在 BLE HOGP 键盘版**；
  经典品类是 **Classic BT（CSR BlueCore）+ `hid2hci.exe`**，不是 BLE。
  （0xf8.org 2014 年的调查结论：这类适配器 *"next to impossible to find"*。）
- `Handheld Scientific BT-500/600` 方向**相反**：把**有线**键鼠变成蓝牙，不是我们要的。
- 唯一在售的相关产品是 **beekeeb 的 Prospector ZMK dongle**（约 ¥5,480），
  但它走的是**分体 central 模式**（需要给键盘刷从机固件），
  正是本节要避开的路线。**不是我们的方案。**

⇒ **结论：保持「原版 ZMK + 三个模式都不刷固件」这条路，市面上没有现成适配器可替代，
Dongle 固件必须自研。** 这是本项目一块**确定要投入的固件工作量**，不再有捷径。

#### ✅ 但可以先用树莓派零成本验证整个构想（替代我上一版错误的「买适配器」建议）

`quaxalber/bluetooth_2_usb` —— 树莓派（BlueZ + USB gadget），把蓝牙键鼠转成 USB HID。
**89★、31 个 release、最新 v4.0.0**，是所有方案里成熟度最高的。
它不是拇指大小的 Dongle（需要一台 Pi），但**非常适合在投入自研固件之前先验证整条架构**。

#### 低延迟机制（有 ZMK 维护者的数字，但**均为计算值，非实测**）

- ZMK 官方 Dongle 文档：加 Dongle 只多 *"about 1ms from the extra USB hop"*，
  同时把一条 BLE 跳换成 USB 跳，使其余部分的平均延迟**下降 6.5 ms**。
- ZMK 维护者 **Nicell** 在 issue #1265 给出：Dongle 模式平均约 **4.25 ms**
  （0.5 ms USB @1000 Hz 轮询 + 3.75 ms BLE @7.5 ms 周期）。
- **roba 的实际做法比「固定参数」更硬**：`main.c` 里 `BT_LE_CONN_PARAM_INIT(6, 6, 0, 400)`
  （7.5 ms、latency 0），并且 `roba_le_param_req()` **直接拒绝**键盘的变慢请求
  （`if (param->latency > 0 || param->interval_max > 6) return false;`）。
  作者指出**键盘自己请求的是 15 ms / latency 30** ——
  ⇒ **Dongle 是在强行覆盖键盘自身的省电偏好**。这是「两端可控」的具体机制。
- ⚠️ **所有延迟数字都是计算或主观感受，没有任何项目公布过示波器/逻辑分析仪实测。**

#### ⚠️ 一个会让人白掉头发的实现陷阱（来自 anisehid 的 ESP32 实践）

ESP-IDF 的 `CONFIG_BT_GATTC_NOTIF_REG_MAX` **默认只有 5**，但
*"many keyboards (Keychron K2 HE for example) register 8+ notification subscriptions;
the IDF default of 5 silently drops the keyboard INPUT report subscription
so no keystrokes flow."* ⇒ **必须调大（他用 16）。**
这类「静默丢订阅、按键完全不响应」的坑在自研固件时必然要踩一遍，先记下来。

#### 一条值得关注、但今天还不能用的路

`tadakado/zmk-ble-mouse-host` 是一个 **ZMK 模块**，让**键盘自己**成为 BLE central + HOGP 主机，
且其 Kconfig `select BT_CENTRAL / BT_OBSERVER / BT_GATT_CLIENT`，
**不要求 `CONFIG_ZMK_SPLIT`** ⇒ **单体内键盘不存在 central/peripheral 的编译期冲突**。

⇒ 这意味着理论上**可以不要 Dongle 那颗 MCU**：键盘自己就能当主机。
**但目前只支持鼠标**（GAP appearance `0x3C2`），键盘版尚不存在，
且这是一个真正的 ZMK 模块开发工作量。**记为后续版本的可能方向，第一版不采用。**

**配对不是障碍**（一手核实，来自 ZMK 源码）：

- ZMK 的 `app/Kconfig` 硬选 `BT_SMP_SC_PAIR_ONLY` ⇒ 要求 **LE Secure Connections**，
  Dongle 必须支持 LESC（NCS 的 `CONFIG_BT_HOGP` 例程支持）。
- `CONFIG_ZMK_BLE_PASSKEY_ENTRY` **默认 `n`** ⇒ 走 **Just Works**，Dongle 无需显示/键盘。
  ⇒ **不要开启它。**
- ⚠️ 注意：ZMK 的 `passkey_display` 回调是**被注释掉的**（`app/src/ble.c`：
  `// .passkey_display = auth_passkey_display,`）—— ZMK **只能输入 passkey、不能显示**。
  一旦启用 `PASSKEY_ENTRY`，就必须由 Dongle 侧显示 6 位码（走 USB CDC 串口可行）。

**ZMK 上游的态度（不是技术性否决）**：issue #1420「Pure USB receiver dongle」于 2025-01
被关闭，**理由只是维护者转向了分体方案**（*"Now that #2525 documents adding a dongle, I'll close this."*）；
HOGP-client 路线**从未被以技术理由否决**。维护者 petejohanson 在 #2395 中表示
HOGP client 应当是 **module 而非核心**。另见仍开放的 #2885（运行时切 central/peripheral）。

### 待决

- ❓ **Dongle 固件技术栈**：**倾向 ESP32-S3 + ESP-IDF `esp_hidh`**（全程 Apache-2.0，
  避开 Nordic-5-Clause），代价是自研工作量；
  vs nRF52840 + NCS（有 roBa 的完整机制可参考，但代码不能抄、且固件将是 Nordic 非开源许可）。
- ❓ **Dongle 硬件选型**：ESP32-S3（原生 USB OTG，许可证干净）
  vs Seeed XIAO nRF52840（ADR 原选择，且与键盘控制器同生态）。
  ⇒ **该选择现在由许可证与技术栈决定，不再只是硬件偏好。**
- ❓ `firmware/build.yaml` 中被注释掉的 Dongle 构建项需按本修订重新设计
  —— 注意 Dongle **不跑 ZMK**，因此它**不进 ZMK 的 build matrix**，
  而是独立固件工程（若选 ESP32 则连工具链都不同）。
- ❓ **Caps Lock 等 LED 输出报告无法经 Dongle 转发**（roBa 的限制来自
  `CONFIG_ENABLE_HID_INT_OUT_EP=n`）。需确认这是否影响本项目的指示灯方案
  —— 本项目的 Caps Lock 提示若由 ZMK 自身状态驱动则不受影响，**待核实**。

> 本修订**不改变** ADR-0001 的核心决策（用 BLE Dongle 而非原生 2.4GHz 射频）。
> 原生 2.4GHz 被否决的理由在本轮调研中**得到加强**：
> Keychron 的实现依赖闭源二进制（`lib_nrf_esb_24G.a` 标注 `LicenseRef-Nordic-5-Clause`、
> Realtek `libppt_sync_master.a`），ZMK 官方 FAQ 亦以许可证理由明确拒绝
> （*"Nordic's proprietary 2.4GHz low level protocols requires use of the Nordic Connect SDK,
> which is licensed with a more restrictive license than ZMK's MIT license."*）。
> ⇒ **障碍是法律而非技术**，本项目不应为此 fork ZMK。
