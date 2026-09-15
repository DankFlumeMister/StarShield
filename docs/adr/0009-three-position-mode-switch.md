# 用三档拨片开关选择连接模式（2.4G / 蓝牙 / 有线）

**状态：🟢 已决定（用户）—— 机制已定，实现细节待定**
**日期：2026-09**
**取代：ADR-0001 中「Dongle 作为 ZMK 分体 central」的隐含假设（见「对 ADR-0001 的影响」）**
**关联：ADR-0010 —— 本开关的「有线」档**兼作电源开关**（切 `SYSOFF`），因此两者必须一起设计**

## 背景

目标是**一个三档拨片开关**，直接切换键盘的连接模式：

1. **2.4G** —— 走 USB Dongle（本项目用 BLE 模拟「2.4G 体验」，非原生 2.4GHz 射频）
2. **蓝牙** —— 键盘直连主机蓝牙
3. **有线** —— 键盘自己的 USB-C

设计要求是「拨到哪档就是哪个模式」，不靠组合键、不靠重新刷固件。

## 关键前置发现：开关能选「输出」，选不了「角色」

ZMK 的开关机制只能切换**输出目标（USB / BLE）**与 **BLE 配对位**。
它**无法**切换设备的 **central / peripheral 角色** —— 这是官方跟踪中的开放需求
（issue [#2885](https://github.com/zmkfirmware/zmk/issues/2885)，2025-03 提出，至今无 PR）。

⇒ **推论（决定整个架构）**：Dongle **不能**采用 ZMK 官方的「分体 central」形态。
若采用，键盘必须编译成分体从机，而分体从机：

- 不能作为独立蓝牙键盘广播（官方原文："will not advertise as pairable BLE keyboards"）
- 连 USB HID 都被 Kconfig 排除（`config ZMK_USB` → `depends on (!ZMK_SPLIT || (ZMK_SPLIT && ZMK_SPLIT_ROLE_CENTRAL))`）
- **离开 Dongle 即变砖**（官方原文："The keyboard becomes unusable without the dongle"）

⇒ **Dongle 必须是「BLE HID 主机」形态**：键盘保持标准 ZMK 蓝牙键盘，
Dongle 自己去当 BLE central 连键盘，再转成 USB HID 给主机。
这样「Dongle」在键盘眼里**只是一个普通蓝牙主机**，三档全部变成 ZMK 原生能力。

> ⚠️ **代价**：ZMK **没有** HID 主机能力（源码中搜不到 `hog_client` / `BT_HIDS_CLIENT`），
> 所以 Dongle 固件**不是 ZMK**，是独立固件项目。详见「后果」。

## 决策

采用 **SP3T 三档开关 + 上游原生的开关读取机制**，键盘侧**零自定义代码**：

```dts
/* 1. 开关每档一个 GPIO；公共端接 GND —— 由驱动管理上下拉，DT 里【不要】写 pull 标志 */
kscan_sp3t_toggle: kscan_sp3t_toggle {
    compatible = "zmk,kscan-gpio-direct";
    toggle-mode;
    input-gpios
    = <&gpio0 9  GPIO_ACTIVE_LOW>   /* 档 0：有线 */
    , <&gpio0 10 GPIO_ACTIVE_LOW>   /* 档 1：蓝牙 */
    , <&gpio0 11 GPIO_ACTIVE_LOW>   /* 档 2：2.4G（Dongle） */
    ;
};

/* 2. 用 sideband 把档位映射到行为 —— 与 keymap 解耦，用户改键/Studio 改键都不会破坏它 */
/ {
    macros {
        ZMK_MACRO(mode_bt_host, bindings = <&out OUT_BLE &bt BT_SEL 0>)
        ZMK_MACRO(mode_dongle,  bindings = <&out OUT_BLE &bt BT_SEL 1>)
    };

    endpoint_sideband_behaviors {
        compatible = "zmk,kscan-sideband-behaviors";
        auto-enable;
        kscan = <&kscan_sp3t_toggle>;

        col0: col0 { column = <0>; bindings = <&out OUT_USB>; };
        col1: col1 { column = <1>; bindings = <&mode_bt_host>; };
        col2: col2 { column = <2>; bindings = <&mode_dongle>; };
    };
};
```

### 档位映射

| 档位 | 绑定 | 含义 |
| --- | --- | --- |
| 0 | `&out OUT_USB` | **有线**：走键盘自己的 USB-C |
| 1 | `&out OUT_BLE &bt BT_SEL 0` | **蓝牙**：直连主机（配对位 0） |
| 2 | `&out OUT_BLE &bt BT_SEL 1` | **2.4G**：连 Dongle（配对位 1） |

`&out` 的选择会**持久化到 flash**（官方文档），与「开关位置 = 持久模式」的直觉一致。

## 依据（全部为一手核实）

| 事实 | 来源 |
| --- | --- |
| `zmk,kscan-gpio-direct` 有 `toggle-mode` 属性；一档一个 GPIO；DT 里不写 pull | `app/module/dts/bindings/kscan/zmk,kscan-gpio-direct.yaml`（**已在 v0.3.0 逐行核对**） |
| 上下拉**由驱动动态管理**：选中档不加内部上下拉（由开关硬接 GND），未选中档按极性加上拉/下拉 | `app/module/drivers/kscan/kscan_gpio_direct.c` 的 `kscan_gpio_get_extra_flags()` 与 `kscan_inputs_set_flags()`（**已读源码**）。本项目用 `GPIO_ACTIVE_LOW` ⇒ 未选中的档被上拉到 3.3 V。**这个细节是 ADR-0010「方式 2」的依据与风险来源** |
| `zmk,kscan-sideband-behaviors` 存在，支持 `auto-enable`，且**不受 keymap 影响** | `app/dts/bindings/kscan/zmk,kscan-sideband-behaviors.yaml`（v0.3.0 核对） |
| **ZMK 上游自带 SP3T 参考实现**：档 0→`&out OUT_USB`、档 1→`BLE+BT_SEL 0`、档 2→`BLE+BT_SEL 1` | `app/boards/shields/zmk_uno/zmk_uno.overlay`（v0.3.0 核对，**照抄即可**） |
| 该特性由 **ZMK 创始人 Pete Johanson** 提需求（issue [#980](https://github.com/zmkfirmware/zmk/issues/980)），原文即「switch primary output, or BT profile」 | issue #980（2023-08-29 关闭，由 PR [#1305](https://github.com/zmkfirmware/zmk/pull/1305) 实现，2022-05-19 合入） |
| **量产商品在用同一套机制**：Kinesis mWave（$119.95）「Profile Switch」三档 | `KinesisCorporation/MWave-zephyr-module`（产品页 + 开源模块，**已抽验 keymap 确认接线一致**） |
| 开关状态在**开机时读取**，关机期间拨动也能正确识别 | ZMK 官方 kscan 文档 |

## 引脚预算影响

| 项 | 之前 | 现在 |
| --- | --- | --- |
| 矩阵行 | 6 | 6 |
| 595 SPI（MOSI/SCK/CS） | 3 | 3 |
| WS2812 数据 | 1 | 1 |
| RGB 门控（P8） | 1 | 1 |
| **模式开关** | — | **+3** |
| **合计 / 可用** | 11 / 18 | **14 / 18** |
| **余量** | 7 | **4** |

⇒ 余量从 7 降到 4，仍然够用，但**后续不能再大手大脚加 GPIO**。

## 风险与未决项

- 🔴 **开关料号尚未确定，且受 ADR-0010 影响**：本 ADR 的机制只需要**单刀** `SP3T`；
  但 ADR-0010 决定「有线档兼作电源开关」，若走其**方式 1** 就需要**双刀** `DP3T`
  （`MSK12C02` 是单刀，不够用）。**两件事必须一起选型。**
  若走 ADR-0010 的**方式 2**（`SP3T` + 一颗晶体管），则「有线档」那个 GPIO
  **同时承担「模式选择」与「电源控制」两个职责**，调试时两者会一起失效。
- 🔴 **开放 bug [#2674](https://github.com/zmkfirmware/zmk/issues/2674)（未修复）**：
  sideband 在**开机时**触发 endpoint + 蓝牙宏，**电池供电下会崩**（USB 供电不崩）。
  Kinesis 的对策是随产品带一份改过 init priority 的 `kscan_sideband_behaviors.c`
  （`POST_KERNEL` → `APPLICATION`）。
  ⇒ **必须二选一**：(a) 同样引入一份本地修补的驱动；或 (b) 设计上避开触发条件。
  **这是采用本方案的主要代价，必须在投板前实测确认。**
- 🟡 参考设计用了 `&adv_mode ADV_OFF/ADV_ON` 在有线档关掉蓝牙广播（省电）。
  那是 Kinesis 自写的 behavior（非上游），约 30 行。第一版**可以不做**。
- ⚠️ **不能指望这个开关切换 Dongle/直连之外的角色** —— 见上文 issue #2885。
- ❓ **未实测**：本项目尚未在实物上验证该配置。SP3T 开关的选型（额定电流在此处无关，
  只需 µA 级）与封装需在 PCB 阶段确定。

## 对 ADR-0001 的影响

ADR-0001 决定「Body 经 BLE 连 Dongle，**Dongle 作为 BLE central**」。
本 ADR 与该决定**不冲突，但收紧了实现方式**：Dongle 不能是 ZMK 分体 central，
必须是独立的 BLE HID 主机固件。ADR-0001 需据此修订（见其修订段）。

## 后果

**收益**
- 三档物理切换，符合用户构想，且**键盘侧零自定义固件**
- 复用上游参考实现（`zmk_uno`），有量产商品先例，不是探索性方案
- **键盘离开 Dongle 仍可用**（蓝牙 / 有线两档），规避了 ZMK 官方 dongle 方案的最大风险
- sideband 与 keymap 解耦 ⇒ 用户改键位、用 ZMK Studio 改键都不会破坏模式开关

**代价**
- Dongle 需要**独立固件**（BLE central + HID client + USB HID），不是 ZMK
- 占用 3 个 GPIO，余量降到 4
- 需处理开放 bug #2674
- 固件由「上游 ZMK 直出」变为「上游 ZMK + 一份修补的驱动」，
  与「钉版本、零维护」的初衷有张力
