# StarShield 固件配置（ZMK）

状态：🟡 **设计稿 + 静态校验通过**（⚠️ **尚未实跑 `west build`** —— 本机缺 Zephyr SDK）

目标板：**nice!nano v2**
⚠️ **ZMK board id 随分支不同**（已核实）：
- `v0.3` release 分支 → **`nice_nano_v2`**（本仓库当前采用）
- `main` 分支 → **`nice_nano//zmk`**（main 上**没有** `nice_nano_v2`）

---

## 1. 目录结构

```text
firmware/
├── build.yaml                          构建矩阵
├── README.md                           本文件
└── boards/shields/starshield/
    ├── starshield.zmk.yml              shield 元数据（供 ZMK 识别）
    ├── Kconfig.shield                  SHIELD_STARSHIELD 注册
    ├── Kconfig.defconfig               键盘名等默认项
    ├── starshield.overlay              kscan / 595 / WS2812 / ext-power
    ├── starshield_transform.dtsi       ← 生成：物理布局 + 95 键映射表
    ├── starshield.keymap               ← 生成：Base / FN 两层，各 95 条绑定
    └── starshield.conf                 Kconfig
.github/workflows/build.yml             构建工作流（读取 firmware/build.yaml）
```

重新生成（幂等，重跑后 git 无差异）：

```powershell
cd <仓库根目录>
$env:PYTHONIOENCODING='utf-8'
node docs\_tools\matrix-assign.mjs     # 矩阵分配 -> docs/_generated/matrix.json
node docs\_tools\gen_transform.mjs     # -> starshield_transform.dtsi（物理布局 + 映射表）
node docs\_tools\gen_keymap.mjs        # -> starshield.keymap
python docs\_tools\verify_firmware.py  # 静态校验（本机可跑，替代实机构建）
```

---

## 2. 引脚分配（权威表）

依据：`docs/adr/0008-matrix-via-74hc595-shift-register.md`。
来源：ZMK 官方 `arduino_pro_micro_pins.dtsi` 与 `nice_nano-pinctrl.dtsi`。

| 用途 | Pro Micro 脚 | GPIO | 备注 |
| --- | --- | --- | --- |
| 矩阵行 R0 | D4/A6 | P0.22 | 直连 MCU（官方要求输入直连） |
| 矩阵行 R1 | D5 | P0.24 | |
| 矩阵行 R2 | D6/A7 | P1.00 | |
| 矩阵行 R3 | D7 | P0.11 | |
| 矩阵行 R4 | D9/A9 | P1.06 | |
| 矩阵行 R5 | D8/A8 | P1.04 | |
| 595 MOSI | D16 | P0.10 | `&spi1` |
| 595 SCK | D15 | P1.13 | `&spi1` |
| 595 片选（RCLK） | D19/A1 | P0.02 | `cs-gpios` |
| WS2812 数据 | D1 | P0.06 | `&spi3` MOSI |
| RGB 电源门控 | D10/A10 | P0.09 | `EXT_POWER` → NMOS 反相级 |
| 模式开关档 0（有线） | **D2** | **P0.17** | C1：`kscan_sp3t_toggle` MODE0（ADR-0009） |
| 模式开关档 1（蓝牙） | **D14** | **P1.11** | C1：MODE1 ⚠️ 已把 `&spi1` 的 MISO 覆盖掉（板级默认占 P1.11，595 只写不需要） |
| 模式开关档 2（2.4G） | **D18/A0** | **P1.15** | C1：MODE2 |
| **合计占用** | **14 / 18** | | **余量 4** |

**空闲引脚**：D0 (P0.8)、D3 (P0.20)、D20/A2 (P0.29)、D21/A3 (P0.31)

⚠️ 注意事项：
- **P0.13 是 nice!nano 的 VCC 门控脚**，本设计未占用（改用 P0.09 驱动外部门控电路）
- **P0.15 是蓝灯**，不要占用
- **595 与 WS2812 必须用不同的 SPI 外设**（两者都是 SPI 从设备）
- 原厂 UART 在 P0.08 / P0.06 —— **P0.06 已被 WS2812 占用**，故不启用串口日志
- 🔴 **`&spi1` 的 pinctrl 在本 shield 覆盖掉了 MISO**：nice!nano 板级 `spi1_default` 含
  `SPIM_MISO = P1.11`，而 C1 把 D14(P1.11) 定为模式开关 MODE1 ⇒ 冲突。595 是**只写**器件，
  MISO 不接，故 shield 里显式只保留 SCK + MOSI（`starshield.overlay` 的 `&pinctrl` 覆盖块）。
  换板（非 nice!nano）时需重新核对该覆盖。

---

## 3. 关键配置项与依据

| 项 | 值 | 依据 |
| --- | --- | --- |
| `ngpios` | **24** | 绑定限定只能 8/16/24/32；18 列需 **3 颗**级联（⚠️ 2026-09-18 修订：原「2 颗」电气不成立 —— 2 颗仅 16 输出位，bit16/17 会被推出链尾丢失；原理图见 `control/control.kicad_sch`） |
| `diode-direction` | **`col2row`** | 与 `docs/matrix-assignment.md` 的二极管方向一致 |
| `EXT_POWER` 节点名 | **必须叫 `EXT_POWER`** | 官方文档：否则用户已保存的设置会丢失 |
| `control-gpios` 极性 | **`GPIO_ACTIVE_HIGH`** | 经 NMOS 反相级后逻辑非反相（见 `power-architecture.md` §5.4） |
| `chain-length` | **95** | 95 颗 per-key LED |
| `color-mapping` | **GRB** | SK6812MINI-E 为 GRB 顺序 |
| `CONFIG_ZMK_RGB_UNDERGLOW_BRT_MAX` | **30** | ⚠️ 硬件电流护栏：30% × 95 颗 ≈ 1.0 A（见 `power-architecture.md` §5.2） |

⚠️ **ZMK 已迁移到 physical-layout 模型**（官方 `docs/hardware-integration/physical-layouts.md`）：
旧的 `chosen { zmk,matrix-transform = ... }` 已不再使用，改为
`chosen { zmk,physical-layout = &physical_layout0; }`，
由 `physical_layout0` 聚合 **kscan + matrix transform + 按键物理位置（`keys`）**。
本项目的 `keys` 属性由 KLE 坐标 ×100（centi-keyunit）自动生成，**同时为 ZMK Studio 铺路**。

---

## 4. 已完成 / 未完成

**已完成（静态校验通过，见 `docs/_tools/verify_firmware.py`）**
- ✅ shield 文件齐套（7 个）
- ✅ `.conf` 中每个 `CONFIG_` 符号均对照 ZMK 官方 Kconfig 核实存在
- ✅ Zephyr 侧「必须手写」的驱动开关无遗漏（3b 检查，防 Bug 5 复发）
- ✅ keymap 两层各 95 条绑定，位置号 0..94 连续
- ✅ transform 95 条、矩阵格唯一（无冲突）
- ✅ DTS 括号/注释配平
- ✅ overlay 引用的 phandle 全部有定义
- ✅ 595 与 WS2812 用不同 SPI 外设
- ✅ 未占用 P0.13 / P0.15

**已完成（真机外验证）**
- ✅ **GitHub Actions 实跑 `west build` 成功**（ZMK v0.3.0），产出
  `starshield-body.uf2`（379,392 B / 741 个 UF2 块）与
  `starshield-settings-reset.uf2`（92,672 B / 181 块），
  两块均已校验 UF2 魔数、familyID = `0xADA52840`（nRF52840）、
  写入地址落在 nRF52 应用区 `0x00026000` 起。
  工作流：`.github/workflows/build.yml`

**未完成**
| 编号 | 待办 |
| --- | --- |
| F1 | ✅ ~~实跑一次 `west build`~~ → **已完成，见上** |
| F2 | 🔴 投板前用实物核对 nice!nano 排针的 pitch 与每边脚数 |
| F3 | 🔴 USB Dongle（BLE central）的 shield 配置尚未设计（`build.yaml` 中已注释掉） |
| F4 | 🟡 决定 ZMK config 是否独立成仓库 |
| F5 | 🟡 是否启用 ZMK Studio（physical layout 已就绪，需再加 RPC 配置） |
| F6 | 🔴 **烧进真板子实测**（编译通过 ≠ 能用；按键映射、RGB、电源门控都要实测） |

---

## 5. 踩坑记录（生成脚本）

| # | 现象 | 根因 | 修复 |
| --- | --- | --- | --- |
| 1 | keymap 整张键位错位 | **DTS 里 bindings 的书写顺序就是位置号顺序**；我按「小键盘/主键区」分组输出，打乱了顺序 | 改为严格按位置号 0..94 顺序输出，另加断言校验连续性 |
| 2 | `starshield_transform.dtsi` DTS 语法崩坏 | 键帽标签 `*`（小键盘乘号）与 `/`（除号）在注释里拼成 **`*/`，提前闭合注释**，`8 \| (/9 */` 变成代码 | 生成器加注释消毒函数 `c()`：`*/`→`* /`、`/*`→`/ *` |
| 3 | transform 节点标签未生效 | 用了 `&default_transform { ... }` —— 那是 **fragment 覆写**，对**尚未定义的新标签无效** | 改为节点定义形式 `default_transform: keymap_transform_0 { ... }` |
| 4 | overlay 用了过时的 chosen 属性 | ZMK 已迁移到 **physical-layout** 模型 | 改为 `zmk,physical-layout = &physical_layout0` |
| 5 | Actions 链接期报 `undefined reference to '__device_dts_ord_129'`，指向 rgb_underglow.c | devicetree 完全正确，但 **Zephyr 的 `menuconfig WS2812_STRIP` 没有 `default y`、也不看 compatible**，必须手写 `CONFIG_WS2812_STRIP=y`。不开 → `ws2812_spi.c` 不参与编译 → `drivers__led_strip` 库没有源文件 → 设备结构体从未生成 | `.conf` 加 `CONFIG_WS2812_STRIP=y`；并把这类「Zephyr 侧必须手写」的开关做进 `verify_firmware.py` 的 3b 检查 |

> ⚠️ 第 2 条与之前 KiCad 生成器踩过的「键位标签以反斜杠结尾导致语法非法」是**同一类坑**：
> **把自由文本嵌进代码或注释时必须消毒。** 键盘键帽标签天然含 `*` `/` `\` `"` 等符号，
> 任何生成器都要处理。

> ⚠️ 第 5 条的教训是**别把「编译通过」当成「配置正确」**：
> 缺一个 Kconfig 开关不会在编译期报错，只在链接期以一个 `__device_dts_ord_N` 数字的形式爆出来。
> 对比 ZMK 自己的 595 驱动 —— `Kconfig.595` 写了 `default $(dt_compat_enabled,...)` 所以自动开；
> 而 Zephyr 的 WS2812 驱动不会自动开。**同仓同类的两个驱动，行为可以完全不同，必须逐个查源码。**
