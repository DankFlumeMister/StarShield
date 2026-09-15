# StarShield

[![Build firmware](https://github.com/DankFlumeMister/StarShield/actions/workflows/build.yml/badge.svg)](https://github.com/DankFlumeMister/StarShield/actions/workflows/build.yml)

**一个开源、全自定义、面向新手教程的无线机械键盘。**

目标是一把 **95 键紧凑全尺寸**单体键盘：键盘本体经 **BLE** 连接一个 USB Dongle，
Dongle 插在主机上，从而获得接近 2.4GHz 的无线体验。硬件设计、固件与教程全部开放。

> ⚠️ **项目仍在设计阶段，尚无硬件实物。** 本 README 如实标注每一项的完成度，
> 未验证的内容不会写成已完成。

---

## 目标

- **95 键紧凑全尺寸**单体键盘（含独立小键盘与导航键簇）
- **无线优先**：Body（键盘本体）作为 BLE peripheral，Dongle 作为 BLE central
- **USB-C 有线备用**：充电 + 有线模式
- **ZMK Studio** 浏览器实时改键
- **Per-key RGB**：95 颗独立发光，组合键控制开关/亮度/颜色/灯效
- **硬件开源**，新手可复刻
- 控制器模块同时兼容 **nice!nano v2** 与 **SuperMini nRF52840**（低成本路线）

## 系统架构

```text
┌─────────────────────────────┐        ┌──────────────────┐      ┌────────┐
│        键盘 Body             │        │      Dongle      │      │  主机   │
│                             │        │                  │      │        │
│  nice!nano v2 (peripheral)  │──BLE──▶│ XIAO nRF52840    │─USB─▶│  PC    │
│   ├─ 95 键矩阵 6 行 × 18 列   │        │   (central)      │      │        │
│   │    ├─ 6 行直连 MCU       │        └──────────────────┘      └────────┘
│   │    └─ 18 列由 2×74HC595  │
│   ├─ BQ24072 充电 + 电源路径管理 │
│   ├─ 3000mAh LiPo（无断电开关）  │
│   └─ 95 颗 SK6812MINI-E + 门控   │
└─────────────────────────────┘
```

**关键技术选择**（完整理由见 `docs/adr/`）：

| 主题 | 选择 |
| --- | --- |
| 固件 | ZMK（基于 Zephyr RTOS） |
| 无线方案 | BLE Dongle（**非**原生 2.4GHz，见 [ADR-0001](docs/adr/0001-zmk-ble-dongle-over-native-2.4ghz.md)） |
| 矩阵驱动 | **2 颗 74HC595 级联**驱动 18 列（见 [ADR-0008](docs/adr/0008-matrix-via-74hc595-shift-register.md)） |
| 充电 | BQ24072，线性充电 + 电源路径管理，做在主 PCB |
| RGB 供电 | **电池直供**，不加 5V 升压（见 [ADR-0007](docs/adr/0007-rgb-powered-directly-from-battery.md)） |
| 许可 | CERN-OHL-S-2.0 |

---

## 当前状态

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 产品与硬件设计决策 | ✅ 已完成 | 11 条 ADR + 完整决策日志 |
| 键位几何 | ✅ 已核验 | 95 键、19.50u × 6.25u（371.5 × 119.1 mm） |
| 95 键矩阵分配 | ✅ 已完成 | 6 行 × 18 列，18 列达数学下界 |
| PCB 原理图（矩阵部分） | ✅ 已完成 | **网表校验 10 项全通过、ERC 0 error** |
| PCB 原理图（电源/RGB/控制板） | 🔴 未完成 | 拓扑与元件取值已定，待画图 |
| 固件配置 | 🟡 已写出 | shield 全套 + 95 键映射，**静态校验通过** |
| 固件编译验证 | ✅ **已通过** | GitHub Actions 用 ZMK v0.3.0 实跑 `west build`，产出可烧录的 `.uf2` |
| PCB 布局 / 外壳 / BOM / 教程 | 🔴 未开始 | |

### 已产出的设计文档

| 文档 | 内容 |
| --- | --- |
| [`docs/decisions.md`](docs/decisions.md) | 完整决策日志 |
| [`docs/adr/`](docs/adr/) | 架构决策记录 0001–0011 |
| [`docs/hardware-geometry.md`](docs/hardware-geometry.md) | 键位几何基准（含一次错误测量的教训） |
| [`docs/matrix-assignment.md`](docs/matrix-assignment.md) | 95 键矩阵行列分配 + 网表校验 |
| [`docs/matrix-folding-analysis.md`](docs/matrix-folding-analysis.md) | 为什么必须用移位寄存器（含引脚预算推导） |
| [`docs/zmk-kscan-alternatives.md`](docs/zmk-kscan-alternatives.md) | ZMK 全部 6 个 keyscan 驱动排查 |
| [`docs/power-architecture.md`](docs/power-architecture.md) | 电源树、电流预算、选型 |
| [`docs/bq24072-pinout.md`](docs/bq24072-pinout.md) | 充电 IC 引脚与元件取值 |
| [`docs/controller-and-battery-facts.md`](docs/controller-and-battery-facts.md) | 控制器/电池/JST 已核实事实 |
| [`firmware/README.md`](firmware/README.md) | 固件引脚分配权威表 + 踩坑记录 |

---

## 仓库结构

```text
.
├── docs/                     设计文档、决策记录、生成/校验脚本
│   ├── adr/                  架构决策记录 0001–0011
│   ├── _tools/               可复现的生成与校验脚本
│   └── _generated/           脚本产物
├── firmware/                 ZMK 固件配置
│   ├── build.yaml            构建矩阵
│   └── boards/shields/starshield/
├── hardware/
│   ├── pcb/
│   │   ├── StarShield/       KiCad 工程（95 键矩阵原理图）
│   │   └── TEST1/            练习工程
│   └── case/                 3D 打印外壳（待开始）
├── research/                 调研报告（结论性，逐条带来源）
├── sketch/                   键盘布局图（KLE 格式，几何唯一权威）
└── tutorials/                新手教程（待开始）
```

---

## 自己跑一遍

本项目全部设计产物由脚本生成，且**可复现**（重跑不会产生差异）。

```bash
# 需要：Node.js、Python 3、KiCad（命令行工具 kicad-cli）
node docs/_tools/matrix-assign.mjs      # 矩阵分配
node docs/_tools/gen_transform.mjs      # 键盘映射表 + 物理布局
node docs/_tools/gen_keymap.mjs         # 键位映射
python docs/_tools/gen_matrix_sch.py    # 生成 KiCad 原理图

# 校验
python docs/_tools/verify_netlist.py    # 网表电气校验（10 项）
python docs/_tools/verify_firmware.py   # 固件静态校验
```

> 若 `kicad-cli` 不在 PATH 上，可用环境变量指定：
> `export KICAD_CLI=/path/to/kicad-cli`

KiCad 工程：用 KiCad 打开 `hardware/pcb/StarShield/Starshield.kicad_pro`。

### 构建固件

固件由 CI 自动构建（ZMK 版本钉在 `firmware/west.yml` 的 `v0.3.0`，上游变更新不会悄悄破坏构建）。
**已实测通过**，产物为两个可烧录的 UF2：

| 文件 | 用途 |
| --- | --- |
| `starshield-body.uf2` | 键盘本体固件 |
| `starshield-settings-reset.uf2` | 清空设置（刷完再刷本体固件，用于恢复出厂状态） |

获取方式：进入 [Actions](https://github.com/DankFlumeMister/StarShield/actions/workflows/build.yml)
→ 选最新一次成功的 run → 页面底部 **Artifacts** → 下载 `starshield-firmware`。

> ⚠️ 这些 UF2 **尚未在真实硬件上烧录验证过** —— 能编译不等于能用。
> 等 PCB 打样后会补上实测记录。

自己触发一次构建：Actions 页面 → **Run workflow**（工作流带 `workflow_dispatch`）。

---

## 已知限制（重要，请勿误读完成度）

- **没有任何硬件实物。** 所有结论均基于设计推导、厂商 datasheet 与仿真级校验。
- **固件已能编译出 `.uf2`，但从未烧进真板子跑过。** 编译通过只说明配置自洽，
  不代表按键定义、RGB 时序、电源门控在实物上正确 —— 这些都必须等 PCB 打样后实测。
- **原理图只画了矩阵部分**，电源与 RGB 子图尚未绘制。
- **引脚分配的机械尺寸未用实物核对。** nice!nano 排针的 pitch 与每边引脚数
  来自 ZMK 官方设备树定义与 Pro Micro 标准旁证，**投板前必须用实物卡尺复核**。
- 外壳必须分件打印：键区宽 **371.5 mm**，超过常见 256 mm 打印床。
- 以下三项**已有推荐方案但尚未确认**（详见 [ADR-0009](docs/adr/0009-three-position-mode-switch.md)、[ADR-0010](docs/adr/0010-battery-cutoff-strategy.md)）：
  - **连接模式开关**：三档拨片（2.4G / 蓝牙 / 有线），单刀 `SP3T`。
    方案用 ZMK 上游原生机制（`toggle-mode` + sideband behaviors），**键盘侧零自定义固件**；
    但 Dongle 必须是「BLE HID 主机」形态，**其固件不是 ZMK，是一块独立的开发量**。
  - **不设电池断电开关**：电池始终接通，「关机」= 拨到有线档 + 拔掉 USB 线，
    再由 ZMK 深睡接手；长期存放拔电池插头。
    这是跟随成熟三模产品（Keychron 等）的做法，也回避了「小开关要扛 2.4 A」的难题。
  - **RGB 门控关断拓扑**：电池满电时 3.3 V GPIO 无法保证关断源极在 4.2 V 轨的高边 PMOS，
    需加一级 NMOS 反相（`GPIO_ACTIVE_HIGH`）。⚠️ 该失效的量级未经实测，标记为未核实。

---

## 参与

项目仍在早期。如果你对以下方向感兴趣，欢迎开 issue 讨论：

- 95 键布局的定位板/外壳设计
- 电源子图（BQ24072 充电 + 电源路径）复核
- 实物打样后的固件实测（矩阵扫描、RGB、电源门控、休眠电流）

## 许可证

本项目采用 **CERN-OHL-S-2.0**（强互惠开源硬件许可证），全文见 [LICENSE](LICENSE)。

任何人可商业使用、修改和分发本设计，但**衍生产品必须同样以 CERN-OHL-S-2.0 开源，
并公开完整设计文件**。
