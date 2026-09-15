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
  因此 **Dongle 固件不是 ZMK，是独立的固件项目**。
  这把「零固件开发」的初衷改成了「一块额外的固件工作量」。
- ✅ **收益**：键盘**离开 Dongle 仍可用**（蓝牙 / 有线两档），
  消除了原方案「丢 Dongle 即变砖」的风险。
- ✅ 三条腿都是 BLE ⇒ 切模式**不需要整机重启**
  （对比：Keychron 的 2.4G 机型因两套射频栈互斥，切模式要 `app_system_reset()` 整机重启）。

### 待决

- ❓ Dongle 固件是自己写（nRF52840 / ESP32 做 BLE central + HID client + USB HID），
  还是先买一个成品「蓝牙转 USB」适配器验证整个构想。
  **成品适配器与 ZMK 键盘的兼容性尚未核实。**
- ❓ Dongle 的硬件选型（原 ADR 提到 Seeed XIAO nRF52840）与 `firmware/build.yaml` 中
  被注释掉的 Dongle 构建项，需按本修订重新设计。

> 本修订**不改变** ADR-0001 的核心决策（用 BLE Dongle 而非原生 2.4GHz 射频）。
> 原生 2.4GHz 被否决的理由在本轮调研中**得到加强**：
> Keychron 的实现依赖闭源二进制（`lib_nrf_esb_24G.a` 标注 `LicenseRef-Nordic-5-Clause`、
> Realtek `libppt_sync_master.a`），ZMK 官方 FAQ 亦以许可证理由明确拒绝
> （*"Nordic's proprietary 2.4GHz low level protocols requires use of the Nordic Connect SDK,
> which is licensed with a more restrictive license than ZMK's MIT license."*）。
> ⇒ **障碍是法律而非技术**，本项目不应为此 fork ZMK。
