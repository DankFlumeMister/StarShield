# ESB 端点验证计划（`efogdev/zmk-esb-endpoint` → nRF52840）

> **目的**：在投入 Dongle 硬件/固件之前，用最小成本回答一个问题——
> **`zmk-esb-endpoint` 模块能否在我们的硬件组合上跑通端到端按键？**
> 结论直接决定 Dongle 架构走方案 A（ESP32-S3 BLE HID 主机）还是方案 B（nRF52 ESB）。
> 背景与两条路线对比见 `docs/adr/0011` 附录 E；本决策由用户 2026-09-18 拍板「先验证再定」。

## 0. 为什么验证点是这个

`efogdev/zmk-esb-endpoint` 是目前唯一「单体键盘 + 第三条 ESB 输出 + MIT + 按 ZMK v0.3.0 测试」
的方案，但有**一个未验证的硬风险**：作者只按 **nRF52833** 调优，nRF52840 自述「应该能工作但
不确定」。我们键盘是 nice!nano v2（nRF52840）⇒ **移植是否成立 = 本验证的核心问题**。

具体要核对的移植点（作者按 52833 假设的地方）：
1. **PPI 通道掩码**——52833 与 52840 的 PPI 均为固定分配，但被 TE/其他外设占用的通道不同；
2. **VTOR / 向量表补丁**——模块假定 `NVIC_NUM_VECTORS = 64`；52840 的向量数不同；
3. **TIMER2 占用**——确认 Zephyr/ZMK 侧没有把 TIMER2 派给别的用途；
4. **HFXO 常开**——模块在 ESB 激活期保持高频晶振，核对 52840 的功耗与实现路径；
5. `RADIO_IRQn` 接管与 BLE 控制器共存（v0.3.0 的 Zephyr BLE 控制器）。

## 1. 物料

| 物料 | 数量 | 用途 |
| --- | --- | --- |
| **nice!nano v2** | 1 | **键盘端**：跑 ZMK v0.3.0 + 模块 —— 这就是成品的键盘主控，验证完直接进成品，不浪费 |
| **Seeed XIAO nRF52840** | 1 | **Dongle 端**：跑 ESB PRX + USB HID —— 与用户既定配置一致（dongle = XIAO） |
| USB-C **数据**线 | 2 | 烧录 + dongle 接主机 |
| 面包板 / 杜邦线 / 一个按钮（可选） | 少量 | 触发测试按键；也可用 mock kscan 免硬件 |
| 一台电脑（Windows/Linux/macOS 均可） | 1 | 构建与验证 |

> 📌 **为什么不是两块 XIAO**（2026-09-18 修正）：最初按「同款板子、单价最低」默认写了 2× XIAO。
> 用户指出真实配置是「键盘 = nice!nano v2、dongle = XIAO nRF52840」——
> 验证应尽量贴近量产组合：键盘端用 **nice!nano v2**（它本来就是键盘要买的主控，
> 验证时先征用、验证后继续进成品，不产生额外浪费），dongle 端用 **XIAO nRF52840**。
> 两块板同为 **nRF52840**，对「52833 → 52840 移植」这个核心验证问题是等价的。
>
> 不需要键盘 PCB、不需要 95 键矩阵 —— 验证的是**无线链路**，不是键位。
> 键盘端的「按键」用 mock kscan 或一个接 GPIO 的按钮即可。
>
> ⚠️ 唯一的实操差异：nice!nano v2 验证期间会被**反复刷机**（移植调试要走好几轮）。
> 它和 XIAO 都有 UF2 bootloader（双击 RESET 进位拖 uf2），刷坏可救；如果手上的
> nice!nano v2 是准备直接焊进成品的，介意反复刷就另备一块，介意成本就用它。

## 2. 步骤

1. **克隆与模块接入**：`git clone -b v0.3.0 https://github.com/zmkfirmware/zmk`；
   把 `zmk-esb-endpoint` 作为 ZMK_EXTRA_MODULES / west module 接入（按其 README）。
2. **键盘端构建**：board 用 `nice_nano_v2`（ZMK v0.3.0 的 board id，与 build.yaml 一致）；
   kscan 用 mock（或一个 GPIO 按钮）；打开模块的 Kconfig，确认 `zmk,esb-endpoint` 节点生成。
   ⚠️ **这一步预计就要动移植点 1–5**（编译错误/链接警告会先暴露一部分，
   运行期问题靠第 3 步暴露）。
3. **Dongle 端构建**：board 用 `seeeduino_xiao_ble`；先用作者的参考实现
   `efogtech/endgame-trackball-firmware/dongle-1k-firmware`（按 protocol.h 适配到 XIAO）。
4. **端到端**：键盘板触发一次按键 → 电脑上应出现该键。
5. **切换行为**：把 BLE profile 切走（`&bt BT_SEL 0` 等）→ USB/BLE 输出恢复；
   切回最后 profile → ESB 恢复。确认无死机、无键盘失效。
6. **（加分）量一次延迟**：能测就测，测不了记录「未测」——不作为通过与否的判据。

## 3. 通过判据

| # | 判据 | 结果 |
| --- | --- | --- |
| 1 | 键盘端：ZMK v0.3.0 + 模块在 **nRF52840** 上编译、烧录、启动成功 | ⬜ |
| 2 | Dongle 端：PRX 固件在 nRF52840 上运行并枚举为 USB HID | ⬜ |
| 3 | **端到端**：键盘板触发按键 → 主机收到该键 | ⬜ |
| 4 | 切换：ESB ↔ BLE/USB 双向切换正常，无死机 | ⬜ |
| 5 | 移植改动清单（PPI/VTOR/TIMER2/HFXO）已记录成文 | ⬜ |

**判定**：3 项全过 + 4 无致命问题 ⇒ **方案 B**；核心不通或移植代价远超预期 ⇒ **方案 A**。
中间态（过了但要改动过多）⇒ 把改动量报给用户再定。

## 4. 构建环境（本机现状与两条路）

- **本机没有 Zephyr SDK**（handoff §11）。两条路：
  - **A. 本地工具链（推荐）**：装 west + Zephyr SDK（下载约 1–2 GB，HTTPS 直连可用）；
    低层级移植（PPI/VTOR/链接器）迭代快。⚠️ 磁盘写入慢（~2,400 文件/分钟），
    ZMK+Zephyr 检出是数万文件，首次 west update 要有耐心。
  - **B. GitHub Actions**：fork 一个带模块的仓，push 触发构建、下载 artifact。
    零本地安装，但每轮迭代要等 CI（数分钟）——对低层级调试太慢，只适合最后验证。
- 注意 `research/_clones/zmk` 是 **main** 分支克隆，**不能**直接当 v0.3.0 构建树用
  （v0.3.0 板级在 `app/boards/arm/`，main 在 `app/module/`）。

## 5. 风险与回退

- **验证失败** ⇒ 回方案 A（ESP32-S3 BLE HID 主机），损失 = 一块 XIAO 开发板 + 若干天；
  **nice!nano v2 不受影响**——它本来就是键盘主控，直接继续当键盘用。
  键盘端无任何残留（模块不进正式固件）。
- **验证通过** ⇒ Dongle 硬件定为 **XIAO nRF52840**（与用户既定配置一致；自制小板亦可），
  固件 = ESB PRX + USB HID；键盘端在 B2/C1 里加入该 module（ZMK module 是正规扩展机制，教程可写），
  nice!nano v2 继续当键盘主控。
- **许可**：模块 MIT；vendored Nordic ESB 为 LicenseRef-Nordic-5-Clause（限 Nordic 芯片，
  本组合两端均为 Nordic，满足）——与方案 A 的全链 Apache-2.0 相比，许可清洁度略降，需在
  仓库第三方声明中写明。
- ⚠️ 无论结果如何，**B2（键盘控制板子图）不受影响**，可并行推进；
  Dongle 部分在验证出结果前不定型。

## 6. 与待办的衔接

- 本验证挂在 **C7**（新增，见 PROJECT_HANDOFF.md §9），可与 B2 并行；
- 验证通过 ⇒ C5（Dongle 固件）改为「ESB PRX + USB HID」实现路线；
- 验证失败 ⇒ C5 维持「ESP32-S3 + `esp_hid_host` + `tusb_hid`」。
