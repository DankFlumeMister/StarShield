#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pcb_design.py —— B4 PCB 布局的**单一真相源**（数据，不画图）

为什么单独拆这个文件（沿用 power_design.py / control_design.py 的既有做法）：
    `.kicad_pcb` 是**派生产物**。改布局只改本文件 + 跑 gen_pcb.py，
    再由 verify_pcb.py 断言。绝不要手工改 `Starshield.kicad_pcb`。

坐标约定（KiCad PCB 坐标，Y 向下为正）：
    板左上角 = (0, 0)。
    顶部 0..SHELF_H 是「控制肩」（方案 1：单板顶部加肩），放 28 个控制/电源件；
    其下才是键区（SHELF_H + BEZEL 起）。
    键区尺寸由 `docs/_generated/matrix.json` 实测推导，**不抄文档里的 371.5 mm**
    （那是按 19.50u 算的；实测 KLE 跨度是 19.25u = 366.71 mm，见 verify_pcb.py）。

⚠️ 关键实测来源（全部来自本仓库，不猜）：
  - 键区跨度：matrix.json 的 x_u ∈ [0.25, 19.50]，y_u ∈ [0, 6.25]
  - 轴体封装原点：自画 8 档 `SW_MX_Hotswap_Optional_*` 的 bbox 中心 = 原点 + (-2.54, +5.08)
    ⇒ **封装原点 = 轴体中心 + (2.54, -5.08)**
  - 灯珠偏移：参考板 apollo87h 实测 87/87 一致 = 轴体中心 + (0, +5.08)
  - 二极管偏移：参考板实测（多数）= 轴体中心 + (-8.33, +1.19)，旋 90°；
    本项目取 (-8.50, 0)，把「离轴体孔边 7.0 mm」的余量从 0.18 提到 0.35 mm
"""
import json
import os

U = 19.05           # 1u = 19.05 mm（MX 标准，与参考板实测行距交叉验证过）
BEZEL = 4.0         # G2 已定：键区四周留边 4 mm/边
SHELF_H = 24.0      # 方案 1：F 行上方加的控制肩高度（改这里即可切换方案）

# --- 键区（由 matrix.json 推导，勿手改）--------------------------------------
X_U_MIN, X_U_MAX = 0.25, 19.50
Y_U_MIN, Y_U_MAX = 0.0, 6.25
KEY_W = (X_U_MAX - X_U_MIN) * U        # 366.7125
KEY_H = (Y_U_MAX - Y_U_MIN) * U        # 119.0625
KEY_X0 = BEZEL                          # x_u = 0.25 处的板坐标
KEY_Y0 = SHELF_H + BEZEL                # y_u = 0    处的板坐标

BOARD_W = KEY_W + 2 * BEZEL             # 374.7125
BOARD_H = SHELF_H + KEY_H + 2 * BEZEL   # 151.0625

# --- 轴体封装原点相对轴体中心的偏移（8 档实测一致）----------------------------
SW_ORIGIN_DX = 2.54
SW_ORIGIN_DY = -5.08

# --- 二极管 / 灯珠 相对轴体中心的偏移与旋转（参考板实测）----------------------
DIODE_DX, DIODE_DY, DIODE_ROT = -8.50, 0.0, 90.0
LED_DX, LED_DY, LED_ROT = 0.0, 5.08, 0.0

# --- 安装孔（G3：8 个 / M2 自攻 / NPTH）---------------------------------------
# 全部落在「键区块」四周 2 mm 处，避开键区（孔边离键区 ≥0.9 mm），
# 且都在定位板轮廓内 ⇒ PCB 与定位板共用同一组孔位。
HOLE_FP = "MountingHole:MountingHole_2.2mm_M2"
_HOLE_INSET = 2.0
HOLES = [
    (f"H{i + 1}", round(x, 4), round(y, 4))
    for i, (x, y) in enumerate([
        (BOARD_W - _HOLE_INSET, _HOLE_INSET + SHELF_H * 0 + 60.0),   # 右 上
        (BOARD_W - _HOLE_INSET, 110.0),                              # 右 下
        (_HOLE_INSET, 60.0),                                         # 左 上
        (_HOLE_INSET, 110.0),                                        # 左 下
        (_HOLE_INSET, BOARD_H - _HOLE_INSET),                        # 底 左
        (BOARD_W * 1 / 3, BOARD_H - _HOLE_INSET),                    # 底 中左
        (BOARD_W * 2 / 3, BOARD_H - _HOLE_INSET),                    # 底 中右
        (BOARD_W - _HOLE_INSET, BOARD_H - _HOLE_INSET),              # 底 右
    ])
]

# --- 控制/电源 28 件在「控制肩」内的摆放 --------------------------------------
# 键区铺满、放不下（背面净空仅约 11 mm < 排针 18.78 mm），故走方案 1 的加肩。
# 排针旋转 90° 后长轴沿 X（31.48 × 3.54），两列相距 15.24 mm（Pro Micro 间距）。
# 值 = (x, y, rot)；全部 F.Cu。
CONTROL = {
    # nice!nano v2 排针（两条 1×12）
    "J3A": (40.00, 4.38, 90.0),
    "J3B": (40.00, 19.62, 90.0),
    # 三档模式开关（ADR-0009）—— **2026-09-19 用户定：移到右上角**
    # ⚠️ 代价：开关到 nice!nano 的 MODE0/1/2 三条线（J3A.5 / J3B.10 / J3B.8）从 ~35 mm
    #    变成 ~320 mm。开关本身只走 µA 级信号，电气上无碍；三条线在顶肩里走，空间充裕。
    "SW96": (360.00, 6.00, 0.0),
    # 3 × 74HC595（ADR-0008 修订：3 颗才够 18 列）
    "U2": (95.00, 12.00, 0.0),
    "U3": (110.00, 12.00, 0.0),
    "U4": (125.00, 12.00, 0.0),
    "C4": (95.00, 20.50, 0.0),
    "C5": (110.00, 20.50, 0.0),
    "C6": (125.00, 20.50, 0.0),
    # 电源（BQ24072 充电 + 电池 + RGB 门控）
    # ⚠️ **2026-09-19 用户定：USB 充电口移到左上角**（原在 x=210 的顶肩中部）。
    #    y = 5.5：USB-C 的插口需要露出板边（壳体上沿开缺口），但**焊盘必须留在板内**
    #    （原取 4.8 时焊盘离板边仅 0.03 mm，DRC copper_edge_clearance 报 error 且会被切掉）。
    #    x = 15：顶肩最左端，避开左缘（焊盘要到 x ≥ 0.5）与 J3A（x ≥ 24.26）。
    # ⇒ **R1 / R2（USB-C 的 CC 下拉）与 F1 随之左移**，紧贴连接器：
    #    CC 走线必须短，否则属于 USB-C 的坏实践。U1 及其余电源件仍在原位（x 252+）。
    #    ⚠️ 代价：VBUS 从 F1（x≈18.5）到 U1（x=252）变成 ~230 mm 长线（0.8 mm 宽、1 A，电气无碍）。
    "J1": (15.00, 5.50, 0.0),      # USB-C（左上角）：开口朝板外（-Y），焊盘离板边 ≥0.5 mm
    "R1": (12.00, 12.50, 0.0),     # CC1 5.1k（随 USB-C 左移，紧贴连接器）
    "R2": (12.00, 16.00, 0.0),     # CC2 5.1k（随 USB-C 左移）
    "F1": (18.50, 12.50, 0.0),     # 2 A hold PTC（P15）；随 USB-C 左移（装在 VBUS 侧）
    "U1": (252.00, 10.00, 0.0),    # BQ24072
    "C1": (260.00, 6.00, 0.0),
    "C2": (260.00, 14.00, 0.0),
    "C3": (268.00, 14.00, 0.0),
    "R3": (276.00, 6.00, 0.0),     # ILIM 1.6k
    "R4": (276.00, 14.00, 0.0),    # ISET 887
    "R5": (284.00, 6.00, 0.0),     # TS 10k（温测禁用）
    "R6": (284.00, 14.00, 0.0),    # 充电 LED 限流
    "D96": (292.00, 14.00, 0.0),   # 充电指示 LED
    "R7": (300.00, 6.00, 0.0),     # Q1 栅极上拉
    "R8": (300.00, 14.00, 0.0),    # Q2 栅极下拉
    "R9": (308.00, 6.00, 0.0),     # RGB_PWR_EN 串阻
    "Q1": (316.00, 6.00, 0.0),     # AO3401A（高边 P-MOS）
    "Q2": (316.00, 14.00, 0.0),    # 2N7002（反相级）
    "J2": (332.00, 10.00, 0.0),    # 电池座 JST-PH
}

# --- 定位板（G6：纳入第一版）--------------------------------------------------
# 与 PCB 同源：只覆盖键区（不含控制肩，否则 SP3T 开关与 USB-C 会被盖住），
# 外扩到与 PCB 同宽 ⇒ 与 PCB 共用同一组安装孔。
PLATE_X0, PLATE_Y0 = 0.0, SHELF_H
PLATE_W, PLATE_H = BOARD_W, BOARD_H - SHELF_H
PLATE_CUTOUT = 14.0    # MX 标准定位板开孔 14 × 14 mm

# --- 网络类（VLED 是唯一 2–3 A 路径，必须加宽）--------------------------------
# ⚠️ ADR-0007：RGB 由电池直供、不加升压 ⇒ VLED 是低阻抗大电流路径。
# ⚠️ 间距取值受「封装自身焊盘间隙」约束，实测（kicad-cli pcb drc）：
#    QFN-16 0.5mm 间距的焊盘间隙只有 0.229 mm、USB-C 座只有 0.200 mm
#    ⇒ 设 0.25 会让**封装自带**的间隙报 clearance error。故统一取 0.2（= 8 mil）。
NET_CLASSES = {
    "Default": dict(trace_width=0.25, via_diameter=0.6, via_drill=0.3, clearance=0.2),
    "VLED": dict(trace_width=2.0, via_diameter=1.2, via_drill=0.6, clearance=0.25),
    "Power": dict(trace_width=0.8, via_diameter=0.8, via_drill=0.4, clearance=0.2),
}
# 归属 Power 类的网（VLED 单独成类；GND 走铺铜）
POWER_NETS = {"OUT", "VBUS", "VCHG_IN", "VBAT"}


def load_matrix(root):
    """读 docs/_generated/matrix.json（几何唯一权威的派生数据）。"""
    p = os.path.join(root, "docs", "_generated", "matrix.json")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def key_center(e):
    """matrix.json 条目 → 轴体中心 (mm)。阶梯键的轴心固定在 centerX_u = 18.75u。"""
    cx = KEY_X0 + (e["centerX_u"] - X_U_MIN) * U
    cy = KEY_Y0 + (e["y_u"] + e["h_u"] / 2.0) * U
    return cx, cy


def switch_origin(e):
    """轴体封装的放置坐标（封装原点在引脚上，不在轴体中心）。"""
    cx, cy = key_center(e)
    return cx + SW_ORIGIN_DX, cy + SW_ORIGIN_DY
