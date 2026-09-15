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

### Dongle 固件：**已有多个开源实现，键盘侧保持原版 ZMK 不改**

⚠️ 上一版把这里写成「待决：自己写还是买成品」并高估了成本。经调研，**这条架构不新颖，
已被反复实现**，且全部满足我们的前提（键盘跑**未修改的**原版 ZMK）。

**最强先例：`hirosatosou/roba-ble-hid-bridge`**（Raytac MDBT50Q-CX-40 / nRF52840，NCS + Zephyr）

- README 原文（**已亲自核对**）：*"runs **unmodified** stock ZMK — all the work is in the dongle."*
- 且**明确描述了我们设想的三档开关用法**：Dongle 只是*"just one host profile, allowing you to
  switch between the dongle and direct BLE using `&bt BT_SEL`"*
- Dongle 作 BLE central 连键盘 → 转 USB HID；带 bond 清除按钮（长按 3 s），
  且文档指出**必须两端都清**（Dongle 按钮 + 键盘 `&bt BT_CLR`）
- 自述优势：*"Deterministic low latency. The dongle is always the central and pins the [link]"*

**其他实现**（均已核对仓库存在与自述）：

| 项目 | 硬件 | 备注 |
| --- | --- | --- |
| `ShiniNet/zmk-usb-bridge` | nRF52840 | 专为「ZMK 键盘 → 专用 USB 接收器」，**附对真机（LaLapadGen2）的验证日志** |
| `anisehid/hid-proxy-for-ble-keyboard` | ESP32-C3 + CH9329 | ★29（最多星）。README 原文 *"Tested with: **ZMK-based keyboards**, Keychron K2 HE"* |
| `lvntbkdmr/ble-to-hid` | **Seeed XIAO nRF52840** | 为无线 Corne 而写 —— **正好是 ADR-0001 原定的 Dongle 硬件** |
| `mosquito/ble-hid-bridge` | ESP32-S3 | 最多同时接 4 个 BLE 外设，通用 HID Report Map 解析 |

⇒ **不必从零写固件**，有多个可读、可改的现成实现，其中两个的硬件就是我们的候选。

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

- ❓ **选哪个现成实现作为起点**（倾向 `roba-ble-hid-bridge`，理由最贴合且文档最全）。
- ❓ **Dongle 硬件选型**：XIAO nRF52840（原 ADR 的选择，且有 `lvntbkdmr` 先例）
  vs Raytac MDBT50Q-CX-40（roba 的选择）。
- ❓ `firmware/build.yaml` 中被注释掉的 Dongle 构建项需按本修订重新设计
  —— 注意 Dongle **不跑 ZMK**，因此它**不进 ZMK 的 build matrix**，
  而是独立固件工程。
- 💡 **可零成本先验证整个构想**：买一个现成的 BLE-HID→USB 适配器，
  让键盘当普通蓝牙键盘连它，验证「Dongle 档」体验，再决定是否自制。

> 本修订**不改变** ADR-0001 的核心决策（用 BLE Dongle 而非原生 2.4GHz 射频）。
> 原生 2.4GHz 被否决的理由在本轮调研中**得到加强**：
> Keychron 的实现依赖闭源二进制（`lib_nrf_esb_24G.a` 标注 `LicenseRef-Nordic-5-Clause`、
> Realtek `libppt_sync_master.a`），ZMK 官方 FAQ 亦以许可证理由明确拒绝
> （*"Nordic's proprietary 2.4GHz low level protocols requires use of the Nordic Connect SDK,
> which is licensed with a more restrictive license than ZMK's MIT license."*）。
> ⇒ **障碍是法律而非技术**，本项目不应为此 fork ZMK。
