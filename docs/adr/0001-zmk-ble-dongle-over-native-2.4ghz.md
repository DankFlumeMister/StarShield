# 采用 ZMK + BLE Dongle，而非原生三模

本键盘追求接近 2.4GHz 的无线手感，但所选固件 ZMK 不支持专有 2.4GHz 射频。集成 Nordic Enhanced ShockBurst（ESB）需要 fork ZMK，且 ESB 与 BLE 互斥，还要面对 Nordic Connect SDK 的许可证限制。

我们决定第一版采用标准 ZMK：Body 经 BLE 连接一块独立的 XIAO nRF52840 Dongle，Dongle 作为 BLE central 插入主机 USB。这样用户获得接近 2.4GHz 的体验，而我们无需维护 ZMK 分支。原生 2.4GHz 推迟到后续版本。

> 📌 **2026-09-18 复核（摘要，详见修订段末「两端都是 nRF52840」一节）**：
> 上面第一段的三个障碍需要**分级修正** —— 许可证障碍比原文写的**弱**
> （Nordic-5-Clause 允许用于 Nordic 芯片，本组合两端都是 nRF52840）；
> 「ZMK 做不了 ESB」**不成立** —— **Keychron 的官方 ZMK fork（`keychron_bpro` 分支）
> 已在商用产品上实现了第三条 ESB 输出**（Zephyr 开源控制器 + RADIO 分时复用）。
> **真正的代价**是：fork ZMK + 改 Zephyr + 自写传输/配对/跳频/省电 + 自写 Dongle 端，
> 与本项目「新手用原版 ZMK 构建」的定位冲突。
> 结论（第一版不做原生 2.4G）**维持不变**，但理由与 v2 可行性评估均已修正。

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

##### ⚠️ 但「Dongle 更快」这个说法，**强形式是错的**（必须记账）

我此前把「Dongle 能控制两端 ⇒ 更快」写得过于肯定。经核实：

- ✅ **对的部分**：蓝牙规范把连接间隔的决定权给 **Central**
  （Core 6.1 Vol 6 Part B：*"The connInterval… is set by the Initiator's Link Layer"*），
  且 ZMK 自己的 Dongle 链路确实钉在 7.5 ms。
- ❌ **错的部分（强形式）**：**ZMK 在每一个原版构建里本来就在向主机请求 7.5–15 ms** ——
  `app/Kconfig` 覆盖了 Zephyr 的默认值：`BT_PERIPHERAL_PREF_MIN_INT` 默认 **6**、
  `MAX_INT` 默认 **12**（Zephyr 自己是 24/40）。
  而且 **Linux 会接受外设发起的合法参数请求**
  （`l2cap_conn_param_update_req()` → `L2CAP_CONN_PARAM_ACCEPTED` → `hci_le_conn_update`）。
  ⇒ 「直连主机一定是慢的」**不成立**。
- 🔍 **唯一一个真实数据点**（issue #2661）：macOS 日志显示一台 ZMK Corne
  *"switching to 15.00 ms latency(0)"*，而设备侧日志是 `interval 12 latency 22`
  —— macOS 落在 ZMK 请求区间的**上沿**，没给到 7.5 ms 下限。
  ⇒ 这**提示**（但不证明）在 macOS 上钉死 min=max=7.5 ms 的 Dongle 可能确实更快。
  这是**连接参数数据，不是按键延迟**，且是单次偶发观测。
- 🔴 **根本问题：没人测过。** 「Dongle vs 直连主机」的按键延迟
  **不存在任何公开实测**；事实上**任何路径**上的 ZMK 按键到主机延迟都没有实测。
  这是**结构性缺失**而非暂时缺失：现存两套测量装置（Dan Luu 的切 USB 线接逻辑分析仪、
  Stapelberg 的驱动矩阵 + 测 Caps Lock LED 引脚）**都是有线的**，
  无法测量主机的蓝牙射频路径。

⇒ **结论：Dongle 的延迟优势属于「机制上可能、但未经测量」，不得作为选型理由。**
要拿它当理由，必须先自建测量装置（Stapelberg 的 Caps Lock LED 往返法可穿过后端 HID 输出报告，
不需要 GPIO，是可行候选）。

### 2026-09-18 复核：键盘与 Dongle **都是 nRF52840** 时，原生 2.4G（ESB）可行吗？

**触发**：用户指出「键盘芯片（nice!nano v2）本来就是 Nordic nRF52840，Dongle 若也用 nRF52840，
两端同芯片，是不是就能直接用 Nordic 的 2.4G 了」。这个观察是对的，逼出一次理由复核。

#### ✅ 原文三个障碍的分级修正

| 原文障碍 | 复核结论 |
| --- | --- |
| 「ESB 与 BLE 互斥」 | ⚠️ **部分成立**：两栈共用 RADIO 外设，**运行时并发**需要 MPSL 仲裁；但本项目**三档开关天然互斥**（ADR-0009），可在上电时按档位二选一初始化 ⇒ 该障碍**有便宜的绕法**（代价见下） |
| 「需要 fork ZMK」 | ⚠️ **措辞不准**：ZMK 支持 west module，不必 fork；但必须**在键盘端写一个大自定义模块**（见下）—— 实质负担不变 |
| 「NCS 许可证限制」 | ❌ **对本研究组合不成立**：Nordic-5-Clause 的限制是「只能用于 Nordic 芯片」，本组合**两端都是 nRF52840** ⇒ 满足。风险点变为：将来若把该固件移植到非 Nordic 芯片，这份代码不能跟着走 |

⇒ **`decisions.md` 里「障碍是法律而非技术」一句按此修正**：法律障碍仅对「两端都是 Nordic 芯片」的组合不成立；
真正的障碍是工程与维护。

#### 🔴 真正的障碍：ZMK 没有 ESB 传输路径，且全世界零先例

ESB（Enhanced ShockBurst）只是一个**链路层**，要把它变成「键盘 ↔ Dongle 的按键通道」，
键盘端必须新增一个自定义模块，至少包含：

1. **传输挂载**：ZMK 的按键输出路径只有两条 —— BLE HID（HOGP）与 USB。
   ESB 要做第三条：把 HID 报告从 ZMK 的行为管线接出来、打包、发走；
2. **配对 / bond**：ESB 没有 BLE 那套 SMP，地址与密钥交换要**自己设计**，且 Dongle 端实现同一套；
3. **跳频 / 抗干扰**：ESB 只有固定信道；自适应跳频要自己做（Nordic 的 Gazel 库有 AFH，仍是 Nordic 系许可、仅限 Nordic 芯片）；
4. **省电调度** —— **最难的一层**。BLE 的连接间隔 / latency 由控制器自动管；
   ESB 下「键盘何时睡、何时听、如何被唤醒、唤醒后多久能发」全部自己写。
   商业键盘「1 ms 延迟 + 数月续航」正是厂商在这层手工调出来的结果；
5. **与三档开关的联动**：若靠「档位互斥、上电决定」绕开 MPSL，则 ZMK 在启动时
   无条件初始化 BLE —— 要把 BLE 启动做成条件化（本身又是对 ZMK 的改动）；
   若要**运行时**切档，就得引入 MPSL 多协议仲裁。

且全世界没有「ZMK + ESB」的先例 ~~（本次再查仍是零）~~
⚠️ **本句已修正（2026-09-18）——「零先例」是错的**：本仓库的调研报告
`zmk-tri-mode-community-precedent.md` §4a–4c 早已记录了**三个** ZMK + ESB 的实现，
其中 **Keychron 的官方 ZMK fork 是一个商用在售、非分体、单镜像、运行时三档切换**的完整反例。
详见下节。修正后的表述是：**先例存在（Keychron，商用级），但没有一个是可直接照搬的
「上游 ZMK + 独立模块」形态 —— 全部要么 fork ZMK + 改 Zephyr，要么不成熟**。
与 ADR-0009「键盘侧零自定义固件」「新手可复刻」的定位冲突这一结论不变。

#### ⭐ 更正依据：Keychron 的 ZMK fork 就是「专门做 Nordic 2.4G 的 ZMK 分支」（用户记忆正确）

本仓库 `zmk-tri-mode-community-precedent.md` §4c（此前会话经 GitHub API 逐项核实）记录了
**`Keychron/zmk`**（zmkfirmware/zmk 的 org fork，49★/73 fork，2022-07 建，最近推送 2026-09-04）：

- **B 系列代码在 `keychron_bpro` 分支**（不在 main）；
- **2.4GHz 是 nRF52840 自己的射频跑 ESB**，作为 ZMK 的**第三条输出**：
  `app/Kconfig` 定义 `ZMK_NRF_24G_ECB`（"enabel nordic 24g ecb"，`select NRFX_TIMER2`）
  与 `ESB_*` 符号，`ZMK_NRF_24G` default y；存在 `app/src/24G/` 目录（内容未读 → UNVERIFIED）；
- 键位里出现**上游 ZMK 不存在的输出键码**：`&out OUT_24G`、`OUT_BLE`、`OUT_CHG` 等
  ⇒ Keychron 扩展了 outputs 行为，加了真正的第三传输；
- 模式开关**不是** ZMK 的 physical-layout 机制，而是 `keychron.dts` 里
  `zmk,kscan-gpio-direct` 的 GPIO 触点（mac/win、bt、**24g**、charging、charge-done）——
  **与我们 ADR-0009 的 SP3T 读法同类**；
- 🔴 关键工程细节：`0001-esb-nrf-fix.patch` **改的是 Zephyr**，不是 app ——
  `subsys/bluetooth/controller/ll_sw/nordic/lll/lll.c`（用动态中断重接 `RADIO_IRQn`）、
  `drivers/usb/device/usb_dc_nrfx.c`、`bas.c`
  ⇒ **他们的 2.4G 栈与 Zephyr 自家的开源 BLE 控制器分时复用同一颗 RADIO**
  —— 这意味着 Keychron **没有**用 NCS 的闭源 SoftDevice Controller，而是
  Zephyr 开源控制器 + nrfx 级别的 ESB（`select NRFX_TIMER2`）。许可处境与
  「NCS 更严格许可」的官方拒绝理由**不是一回事**（⚠️ 该许可结论本身 UNVERIFIED）；
- **不是分体模式**：无 `zmk,kscan-mock`、无 `CONFIG_ZMK_SPLIT`，单镜像
  `west build -s app -b keychron -DSHIELD=keychron_b1_us`，BLE 直连与 2.4G **共存于一个固件、
  无需重刷**（读自 DT/Kconfig/keymap，未上机验证）；
- **Dongle 侧 UNVERIFIED**：未找到任何 dongle 固件；线索是 `Keychron/zmk` 有 `rtl8762g` 分支、
  Keychron org 有 `hal_realtek` ⇒ **其接收器很可能是 Realtek 方案，不是 Nordic**（未证实）。
  ⇒ 即便走 Keychron 路线，**我们的 Dongle 仍要自己写**。

#### 其他 ZMK + ESB 尝试（同报告 §4a/§4b + 2026-09-18 二轮深挖）

##### ⭐ `badjeff/zmk-feature-split-esb` —— 用户记忆中的那个「专门做 Nordic 的 ZMK 分支」

**这是目前最完整的开源 ZMK + Nordic ESB 实现**，形态是 **west module**（不必 fork ZMK 本体）：

- 原理：用 **NCS 的 ESB 实现** 替换 ZMK 分体传输（`CONFIG_ZMK_SPLIT_ESB=y`），
  并用 **MPSL（多协议服务层）** 做射频时间片仲裁 —— **BLE 与 ESB 真正共存于一颗 nRF52840**
  （其工作基于 `ncs-esb-ble-mpsl-demo`）；
- 依赖：NCS 的 ESB + MPSL（Nordic 组件，限 Nordic 芯片 —— 我们两端都是 Nordic，满足），
  ⚠️ 但需要**作者 fork 的 NCS**（`sdk-nrf v3.1-branch+zmk-fixes`）才能过 CMake 校验；
- 两种拓扑（README 数据，未实测）：
  | 拓扑 | 延迟 | 功耗 |
  | --- | --- | --- |
  | **纯 ESB Dongle**（dongle 只走 USB，键盘半↔dongle 走 ESB） | **最低 1 ms** | TX 长期略低于 BLE（不保持连接） |
  | **BLE + ESB 并存**（central 用 BLE 连主机，半用 ESB 连 central） | 7.5 + 1 ms | central **7.5 mA @4.0 V**（纯 BLE 仅 0.65 mA）；且连上主机后**没有足够射频资源再做广播**，central 只能配一台 BLE 主机 |
- 🔴 **对本项目的根本限制**：它是 **split transport** —— 替换的是分体键盘「半 ↔ central」的链路。
  **我们的 95 键是单体键盘，没有「半」**。要用它，就得把键盘建成 ZMK **split peripheral**、
  把 Dongle 建成 split central —— 那正是 ADR-0001 否掉的**分体 Dongle 模式**
  （键盘离开 Dongle 变砖、键盘端 USB HID 编译不进去、角色编译期定死；
  第三方 `aroum/zmk-enki42-dongle` 的对比表也明说：该模式下插 USB 到键盘半**只能是充电**）；
  且 peripheral 端要 `CONFIG_ZMK_BLE=n` ⇒ 键盘自己也做不了蓝牙直连。
- 许可：模块本体许可**待核实**（badjeff 的模块多为 MIT，本次搜索页未显示 LICENSE）；
  其依赖的 NCS ESB/MPSL 为 Nordic-5-Clause（限 Nordic 芯片）。

> 📌 附带收获：`aroum/zmk-enki42-dongle` 的 README 有一张「三种 Dongle 路线」对比表
> （原生 BLE / badjeff ESB / Keychron 2.4G），并证实 **Keychron 的 ESB 是预编译二进制
> `lib_nrf_esb_24G.a`**（joric 的 nrfmicro wiki 亦如此记载），
> 且其 dongle 固件与接收器原理图闭源 ⇒ **Keychron 路线无法移植到 DIY 硬件** ——
> 这把上一轮「Keychron ESB 栈许可未核实」的疑问**收口了：是闭源 blob，不可复用**。

| 项目 | 形态 | 成熟度（⭐ 2026-09-18 晚经 GitHub API 实测星数） |
| --- | --- | --- |
| **`badjeff/zmk-feature-split-esb`** | **west module**：ESB 替换分体链路（MPSL 与 BLE 共存） | **55★ / 18 fork**（本类最高星）；无顶层 LICENSE，per-file SPDX = ZMK 部分 MIT + NCS 部分 Nordic-5-Clause（见 `kmobs` fork 说明）；仅适用**分体**键盘 |
| **`efogdev/zmk-esb-endpoint`** ⭐⭐ | **ESB 作为输出端点（endpoint），不是 split —— 单体键盘可用** | 5★、活跃（2026-09-13 推送）、**MIT**（vendored Nordic ESB 为 Nordic-5-Clause）；⚠️ **只按 ZMK v0.3.0 测过**（与本项目钉的版本一致！）。**详见 ADR-0011 附录 E** |
| `GammaKinematics/zmk-feature-esb_transport` | ZMK(STM32 主控) → UART → **nRF52805 协处理器跑 ESB** → nRF52840 dongle | 0★，MIT，TODO 密集 |
| `Keychron/zmk`（`keychron_bpro`） | **单体**键盘 + 第三条 ESB 输出（运行时切档） | 商用级，但 ESB 是**闭源 blob `lib_nrf_esb_24G.a`**、dongle 闭源 ⇒ 不可移植 |
| `voltaire-toledo/submod-zmk` | Keychron B1 Pro 的重打包 fork（MIT） | 0★，2.4G 是否真实 UNVERIFIED |
| 生态外围 | `damex/zmk-feature-split-esb`（8★，MIT，活跃）· `greengrocer98/zmk_esb_dongle` 与 `esb-transport-library`（ESB dongle 实现）· `pekorali/zmk-cyn-sofle`（Sofle + ESB dongle）· `Rapter2310/roard-split-ergo`（3× nice!nano + ESB） | 「ZMK + ESB」已形成小生态，不是孤例 |

> ⚠️ **本节结论已第三次修正（2026-09-18 晚）**：`efogdev/zmk-esb-endpoint` 推翻了
> 「ZMK + ESB 没有单体键盘可用方案」——**单体、输出端点形态、MIT、且按本项目钉住的 v0.3.0 测试**，
> 四个条件全中。剩余风险（nRF52840 移植未验证、单维护者、无延迟/功耗数据、dongle 要自己写）
> 与新旧两条路线的完整对比见 **ADR-0011 附录 E**。
> **第一版选型的最终判断移交用户**：方案 A = ESP32-S3 BLE HID 主机（现选）；
> 方案 B = nRF52 ESB（键盘 `zmk-esb-endpoint` 模块 + nRF52840 dongle）。

#### 这对结论的影响（已按此更新）

1. **「ZMK 做不了 ESB」这个说法不成立** —— Keychron 用
   「Zephyr 开源控制器 + RADIO 分时复用 + 扩展 outputs 行为」做到了商用级。
   ⇒ v2 选项从「零先例、自己趟」升级为「**有商用先例与实现路线图**」。
2. **但第一版的结论不变**，因为代价结构没变，反而被 Keychron 的做法量化了：
   要做的事 = **fork ZMK + 打 Zephyr 补丁（改控制器中断）+ 写 `app/src/24G/` 传输 +
   自设计配对/跳频/省电 + 自己写 Dongle 端** —— 这是厂商级工程，
   且我们的教程前提（用户用**原版 ZMK** 经 GitHub Actions 构建、钉 v0.3.0）会被完全打破。
3. **许可仍有一道未核实的坎**：Keychron 的 ESB 栈源码（`app/src/24G/`）与其 patch
   均未声明许可 ⇒ 思路可参考、**代码不可抄**；我们自己实现时要弄清
   「Zephyr 开源控制器 + nrfx（Apache-2.0）+ 自写 ESB」能否做到全链 MIT/Apache ——
   若能，v2 的许可障碍就真正消失。
4. **触发条件不变**：v1 实测延迟不达标（ADR-0001 要求先建测量装置），
   且接受「键盘端从此维护一条自定义无线链路」。

#### 收益量化与决策

- ESB 能把空口延迟从 BLE 的 **7.5 ms** 压到 **~1 ms**。
  但按本 ADR 的硬规则：**所有延迟数字都是推算，从未实测**（见上节）——
  v1 先用 BLE Dongle 拿到真实测量，才知道 7.5 ms 是不是真问题。
  对打字而言 7.5 ms 与 1 ms 的差别大概率不可感知（商用无线键盘普遍 7.5–15 ms）。
- **决策：第一版维持 BLE HID 主机 Dongle；原生 2.4G（ESB）作为 v2 立项候补**，
  触发条件 = v1 实测延迟不达标 + 愿意承担「自维护一条无线链路」的长期成本。
- **与 Dongle 芯片选择的关系**：这条复核**不改变** ESP32-S3 的选择 ——
  「dongle 用不用 nRF52840」与「能不能上 ESB」是两件事：
  nRF52840 Dongle 的价值在 B 方案（BLE HID 主机 + HOGP，见 ADR-0011 附录 D），
  ESB 则**始终需要键盘端的 ZMK 模块**，与 Dongle 用哪颗芯片无关。

#### 💡 顺带一个重要发现：Dongle 的核心卖点之一可以免费拿到

Dongle 常被宣传的好处是「能进 BIOS / 不需要配对」。但 **BIOS 场景一条线就解决了**：
`CONFIG_ZMK_USB_BOOT=y`（USB Boot Protocol 支持）。

⇒ **Dongle 真正独有、且无法用线替代的价值只剩一条：在「没有蓝牙的机器」上无线使用。**
这个价值比第一眼看上去窄得多，**应在决定是否投入 Dongle 固件开发前明确它对本项目是否必要。**

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
