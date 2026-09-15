# 采用 ZMK + BLE Dongle，而非原生三模

本键盘追求接近 2.4GHz 的无线手感，但所选固件 ZMK 不支持专有 2.4GHz 射频。集成 Nordic Enhanced ShockBurst（ESB）需要 fork ZMK，且 ESB 与 BLE 互斥，还要面对 Nordic Connect SDK 的许可证限制。

我们决定第一版采用标准 ZMK：Body 经 BLE 连接一块独立的 XIAO nRF52840 Dongle，Dongle 作为 BLE central 插入主机 USB。这样用户获得接近 2.4GHz 的体验，而我们无需维护 ZMK 分支。原生 2.4GHz 推迟到后续版本。

## Consequences

固件保持在上游 ZMK，用户可用 GitHub Actions 构建，ZMK Studio 开箱可用。代价是延迟约 4.25ms（而非 1–3ms），且用户需多携带一个 Dongle。
