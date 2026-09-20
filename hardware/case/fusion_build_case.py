# -*- coding: utf-8 -*-
"""StarShield 底壳 —— Fusion 360 参数化建模脚本（Python API，在 **Fusion 内部**运行）。

设计依据（全部来自工程文档，不是自由发挥）：
  - **PCB 是上盖**、**底壳按约等分两件**（缝落在键位列边界）：`docs/hardware-geometry.md` §3.1（G4）
  - 侧壁 2 mm、外扩 4 mm/边；M2 **热熔螺母**柱 φ6.4 / 孔 3.0×5.0：`docs/case-benchmark.md` §2.3（2× 规则）
  - 8 个 M2 安装孔（NPTH φ2.2，H1–H8）：从板文件提取
  - 三处开孔坐标：`docs/nice-nano-physical-verification.md` §6.7
  - 电池仓左右各 10.5 × 56 × 68、机壳深 ≥11 mm：`docs/power-architecture.md` §3.6（G5）
  - 板下 15.0 = 座 **1.8**（Kailh 原厂图纸，非假设）+ 压边 2.0 + 电池 10.5 + 余量 0.7；
    板面 +5.0 / 板厚 1.5 / 开孔 14×14 取 Cherry MX 图纸：`docs/case-benchmark.md` §2.1–§2.3
  - 倾角 5.5°、脚垫 Ø8×3、缝销 Ø4×8、压边过线缺口 3.0：`docs/case-benchmark.md` §2.4–§2.6
    （**已定值，v2 才建几何**；本脚本里作为参数声明）

几何输入：`hardware/case/case_inputs.json`（`docs/_tools/extract_case_inputs.py` 生成）
参数预检：`docs/_tools/preflight_case.py`（全绿才动手）

⚠️ 单位：Fusion 内部长度单位是厘米；本脚本参数用 mm，统一经 `mm()` 换算。

## 2026-09-21 的重要修正（首次运行把 Fusion 跑崩了，教训在此）

首版**每个小体都新建一个构造平面 + 草图 + 拉伸**（8 柱 + 8 底孔 + 24 个电池压边 ⇒ 40+ 特征），
且**沿用了旧的 body 代理**（SWIG 代理在特征重建后会失效）。结果是 add-in 在启动阶段
把 Fusion 跑崩（`CER` 目录留下崩溃报告）。
⇒ 现在改为：**一次草图装多个轮廓 ⇒ 一个特征搞定一批**（总特征数 ~7），
并在**每个特征之后重新获取 body**。运行也更稳更快。

产物：
  hardware/case/out/StarShield-case.step            整件
  hardware/case/out/StarShield-case-A.stl / -B.stl  分件（切片用）
  hardware/case/out/preview-iso.png                 等轴视口截图（前-右-上）
  hardware/case/out/preview-top.png                 **俯视**截图（屏幕右=+X、屏幕上=+Y，验朝向用）
  hardware/case/out/build.log                       运行日志（逐步 + 体积自检 + 方向自检 + 字符俯视图）

离线预检：`python .workbuddy/scratch/check_plan.py`（打桩 adsk，不开 Fusion 就能验坐标朝向）
"""
import json
import os
import traceback

import adsk.core
import adsk.fusion

ROOT_DIR = r"D:\StarShield"
CASE_DIR = os.path.join(ROOT_DIR, "hardware", "case")
OUT_DIR = os.path.join(CASE_DIR, "out")
INPUTS = os.path.join(CASE_DIR, "case_inputs.json")
LOG = os.path.join(OUT_DIR, "build.log")

# ---- 参数（mm；与 docs/_tools/preflight_case.py 必须一致）----
# 取值依据：docs/case-benchmark.md（商业键盘规格书 + 社区方案 + 器件原厂图纸）
P = {
    "wall": 2.0, "floor": 2.5, "clearance": 0.3, "depth": 15.0, "lip": 4.5,
    # 板下 15.0 = 插拔座 1.8（Kailh 图纸，板下占高）+ 压边 2.0 + 电池 10.5 + 余量 0.7
    # M2 **热熔螺母**柱（旧的自攻柱 φ5.0/底孔1.7 不适于反复拆装；2× 规则 ⇒ φ6.4/孔3.0/深5.0）
    "boss_od": 6.4, "boss_pilot": 3.0, "boss_pilot_depth": 5.0,
    "bat_w": 56.0, "bat_l": 68.0, "bat_t": 10.5, "bat_inset": 8.5,
    "clip": 2.0, "clip_len": 12.0, "clip_arm": 12.0,
    "seam_x": 189.70,
    # --- 已定值但 **v2 才建几何**（见 case-benchmark §7）：倾角 5.5°、脚垫 Ø8×3、缝销 Ø4×8、过线缺口 3.0
    "tilt_deg": 5.5, "foot_dia": 8.0, "foot_h": 3.0,
    "seam_pin_dia": 4.0, "seam_pin_len": 8.0, "seam_pin_clear": 0.2,
    "clip_notch_w": 3.0,
}
OPENINGS = [
    {"name": "充电 USB-C (J1)", "kind": "front", "center": 15.0, "w": 11.0},
    {"name": "模块 USB-C", "kind": "left", "center": 17.8, "w": 10.0},
    {"name": "三档开关 SW96", "kind": "front", "center": 33.0, "w": 8.0},
]

_fh = None


def log(*a):
    msg = " ".join(str(x) for x in a)
    if _fh:
        _fh.write(msg + "\n")
        _fh.flush()
    print(msg)


def mm(v):
    return v / 10.0


def VI(v):
    return adsk.core.ValueInput.createByReal(mm(v))


def Pt(x, y):
    return adsk.core.Point3D.create(mm(x), mm(y), 0)


def plane_at(root, z):
    pi = root.constructionPlanes.createInput()
    pi.setByOffset(root.xYConstructionPlane, VI(z))
    return root.constructionPlanes.add(pi)


def rect(sk, x0, y0, x1, y1):
    L = sk.sketchCurves.sketchLines
    a, b = Pt(x0, y0), Pt(x1, y0)
    c, d = Pt(x1, y1), Pt(x0, y1)
    L.addByTwoPoints(a, b)
    L.addByTwoPoints(b, c)
    L.addByTwoPoints(c, d)
    L.addByTwoPoints(d, a)


_YB = [0.0, 0.0]      # 板 y 包围盒（run() 里填真值），供 YF 使用


def YF(y):
    """板 y（KiCad 画布 y **向下**）→ 模型 Y（Fusion 俯视 +Y 向上）。

    依据（2026-09-21 修正；首版就错在这里，见 handoff §10.2 第 57 条）：
      - KiCad 的 **F.Cu 视图 = 从上往下看装好的键盘**（PCB 就是上盖、F.Cu 朝上）；
      - KiCad 屏幕「向下」这个方向，在模型里就是 −Y ⇒ **板 y 必须取反**：
            Y_model = (by0 + by1) − y_board
      - X **不取反**：板 x 小的一侧 = 键盘左侧（模块 USB-C 从板 x=0 那面壁伸出去）。
    数值自查（本机实测数据）：开口在板 y = 0 / 17.8 ⇒ 模型 Y = 151.1 / 133.3（**上边**）；
      8 个安装孔在板 y = 60…149.06 ⇒ 模型 Y = 91.1…2.0（**下边**）。
    ❌ 漏掉取反的后果：模型整体在 Y 上镜像，三处开口跑到键盘「前下边」、
      螺丝柱跟着镜像 —— 与 PCB 布局左右上下全对不上（用户一眼看出「开口应该在左上角」）。
    """
    return (_YB[0] + _YB[1]) - y


def YR(y0, y1):
    """把一对**板 y** 换算成模型 Y 的**升序**区间 (小, 大)。"""
    a, b = YF(y0), YF(y1)
    return (a, b) if a <= b else (b, a)


def rectY(sk, x0, x1, y0, y1):
    """矩形：**x 用模型坐标、y 用板坐标**（内部自动 YF 取反并排成升序）。

    ⚠️ 凡是用到「板的 y」的几何（板框外扩、安装孔、侧壁开孔、电池仓）都必须走这里，
    不要再直接往 rect() 里写裸 y —— 少转一处就是整片镜像，且肉眼看几何看不出来。
    """
    a, b = YR(y0, y1)
    rect(sk, x0, a, x1, b)


def circle(sk, cx, cy, dia):
    sk.sketchCurves.sketchCircles.addByCenterRadius(Pt(cx, cy), mm(dia / 2.0))


def do_extrude(root, body, operation, depth, z, name, min_loops=1):
    """用**当前草图的闭合轮廓**拉伸（一个特征 = 一批几何）。

    ⚠️ `min_loops` 用来避开「被围住的实心区」：若草图里若干矩形拼成一个**闭合环**，
    Fusion 会把「环带」和「环内被围住的区域」都算成轮廓 —— 若一起拉伸，
    本该做成**环形压边**的电池仓会被填成**实心块**（首次成功运行就踩了：
    体积从 194.2 跳到 302.2 cm³，比设计值多出 8 倍，日志体积自检抓到的）。
    ⇒ 环带轮廓有 2 个 loop（外圈 + 内圈），实心区只有 1 个 ⇒ 传 `min_loops=2` 即可只要环带。
    """
    sk = root.sketches.item(root.sketches.count - 1)
    profs = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        pr = sk.profiles.item(i)
        if pr.profileLoops.count >= min_loops:
            profs.add(pr)
    if profs.count == 0:
        raise RuntimeError("草图里没有满足条件的闭合轮廓（min_loops=%d）：%s" % (min_loops, name))
    ei = root.features.extrudeFeatures.createInput(profs, operation)
    ei.setDistanceExtent(False, VI(depth))    # 官方标注「已废弃」但明确说明继续兼容；改新 API 风险更大
    if body is not None:
        ei.participantBodies = [body]
    feat = root.features.extrudeFeatures.add(ei)
    log("     · 特征 %s：%d 个轮廓（≥%d 环），深度 %.2f" % (name, profs.count, min_loops, depth))
    return feat


def vol(root):
    b = get_body(root)
    return b.volume if b else 0.0


def check_delta(name, before, after, lo, hi):
    """体积自检：某步的体积增量应落在 [lo, hi] cm³ 内，否则说明几何被画错。
    ⚠️ 这道闸门抓到过一次真实缺陷：电池压边把「环带 + 被围住的实心区」一起拉伸，
    体积多增了 8 倍（108 而非 13 cm³）⇒ 压边成了实心块、电池根本放不进去。"""
    d = after - before
    bad = not (lo <= d <= hi)
    log("    %s 体积增量 %.2f cm³（期望 %.1f–%.1f）%s"
        % ("❌" if bad else "✅", d, lo, hi, "← 异常，几何可能有误" if bad else ""))
    return d


def get_body(root):
    """每次特征之后**重新获取** body —— SWIG 代理会失效（首版崩溃的元凶之一）。"""
    if root.bRepBodies.count == 0:
        return None
    return root.bRepBodies.item(0)


def draw_plan(ox0, ox1, oy_lo, oy_hi, hole_pts, open_rects, bat_rects, seam_x,
              gw=96, gh=18):
    """把模型俯视图画成**字符图**写进日志（上 = +Y = 键盘后侧，左 = −X）。

    ⚠️ 为什么必须有它：整片镜像 / 朝向错这类缺陷，**等轴截图里根本看不出来**
    （首版就是：开口落在键盘前下边，图上看只是「角落不对」，说不清对错）。
    字符图直接把模型坐标画出来并标明哪边是 +Y ⇒ 判据无歧义，也不需要开图。
    """
    g = [[" "] * gw for _ in range(gh)]
    for c in range(gw):
        g[0][c] = "-"
        g[gh - 1][c] = "-"
    for r in range(gh):
        g[r][0] = "|"
        g[r][gw - 1] = "|"

    def put(x, y, ch):
        c = int(round((x - ox0) / (ox1 - ox0) * (gw - 1)))
        r = int(round((oy_hi - y) / (oy_hi - oy_lo) * (gh - 1)))    # 行 0 = 最大 Y
        if 0 <= c < gw and 0 <= r < gh:
            g[r][c] = ch

    def box(x0, x1, y0, y1, ch, n=80):
        for i in range(n + 1):
            put(x0 + (x1 - x0) * i / n, y0, ch)
            put(x0 + (x1 - x0) * i / n, y1, ch)
            put(x0, y0 + (y1 - y0) * i / n, ch)
            put(x1, y0 + (y1 - y0) * i / n, ch)

    for (px, py) in hole_pts:
        put(px, py, "H")
    for (x0, x1, y0, y1) in open_rects:
        box(x0, x1, y0, y1, "O")
    for (x0, x1, y0, y1) in bat_rects:
        box(x0, x1, y0, y1, "b")
    sc = int(round((seam_x - ox0) / (ox1 - ox0) * (gw - 1)))
    for r in range(gh):
        if 0 < sc < gw - 1:
            g[r][sc] = "|"

    log("    ┌─ 模型俯视字符图（上 = +Y = 键盘后侧、左 = −X；H 安装孔 / O 开口 / b 电池仓 / | 分件缝）")
    for r in range(gh):
        log("    │ " + "".join(g[r]))
    log("    └─ 每格 ≈ %.1f mm（横）× %.1f mm（纵）；开口应出现在**上边与左端**"
        % ((ox1 - ox0) / (gw - 1), (oy_hi - oy_lo) / (gh - 1)))


def run(_context):
    global _fh
    os.makedirs(OUT_DIR, exist_ok=True)
    _fh = open(LOG, "w", encoding="utf-8")
    ok = False
    try:
        app = adsk.core.Application.get()
        log("=== StarShield 底壳建模 开始 ===")
        log("Fusion", app.version)

        data = json.load(open(INPUTS, encoding="utf-8"))
        bx0, by0, bx1, by1 = data["board_outline"]["bbox"]
        holes = data["mounting_holes"]
        log("板框 %.4f × %.4f，安装孔 %d 个" % (bx1 - bx0, by1 - by0, len(holes)))

        # 文档复用：若当前就是「未保存的空白设计」就直接用，避免每跑一次多一个「无标题」
        doc = app.activeDocument
        reuse = False
        if doc is not None and getattr(doc, "dataFile", None) is None:
            try:
                d0 = adsk.fusion.Design.cast(app.activeProduct)
                if d0 is not None and d0.rootComponent.bRepBodies.count == 0:
                    reuse = True
            except Exception:
                reuse = False
        if reuse:
            design = adsk.fusion.Design.cast(app.activeProduct)
            log("复用当前空白设计:", doc.name)
        else:
            doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            design = adsk.fusion.Design.cast(app.activeProduct)
            log("新建设计文档")
        root = design.rootComponent
        # ⚠️ 不能给根组件改名（Fusion 报 "root component name cannot be changed"），
        #    首版就崩在这一行 —— 故此处不再设 root.name。

        z_floor = P["floor"]
        z_pcb = z_floor + P["depth"]
        z_top = z_pcb + 1.6 + P["lip"]

        # 坐标系：板 y 取反、x 不变 —— 换算写在模块级 YF()/rectY() 里（含依据与自查数据）。
        _YB[0], _YB[1] = by0, by1
        log("坐标系（板 → 模型）：板 y=%.2f（开口侧）→ 模型 Y=%.1f；板 y=%.2f → 模型 Y=%.1f；x 不取反"
            % (by0, YF(by0), by1, YF(by1)))

        ix0, iy0 = bx0 - P["clearance"], by0 - P["clearance"]
        ix1, iy1 = bx1 + P["clearance"], by1 + P["clearance"]
        ox0, oy0 = ix0 - P["wall"], iy0 - P["wall"]
        ox1, oy1 = ix1 + P["wall"], iy1 + P["wall"]
        log("内腔 %.2f × %.2f；外形 %.2f × %.2f；总高 %.2f；板下净空 %.1f"
            % (ix1 - ix0, iy1 - iy0, ox1 - ox0, oy1 - oy0, z_top, P["depth"]))

        # ① 外形（新建 body）
        sk = root.sketches.add(plane_at(root, 0))
        rectY(sk, ox0, ox1, oy0, oy1)
        do_extrude(root, None, adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
                   z_top, 0, "外形")
        tray = get_body(root)
        log("① 外形体积 %.1f cm³" % tray.volume)

        # ② 挖内腔
        sk = root.sketches.add(plane_at(root, z_floor))
        rectY(sk, ix0, ix1, iy0, iy1)
        tray = get_body(root)
        do_extrude(root, tray, adsk.fusion.FeatureOperations.CutFeatureOperation,
                   z_top - z_floor + 2, z_floor, "内腔")
        v2 = vol(root)
        log("② 挖腔后体积 %.1f cm³" % v2)

        # ③ 三处侧壁开孔（顶部开口的槽）—— 一个草图装 3 个矩形，一次切
        z_from = z_pcb - 1.0
        sk = root.sketches.add(plane_at(root, z_from))
        model_pos = {}
        for op in OPENINGS:
            a0, a1 = op["center"] - op["w"] / 2, op["center"] + op["w"] / 2
            if op["kind"] == "front":      # 板 y=0 那面壁 → 模型**后侧（大 Y）**
                ya, yb = YR(oy0 - 1, iy0 + 1)
                rect(sk, a0, ya, a1, yb)
                model_pos[op["name"]] = (a0, a1, ya, yb)
                log("     · 开孔 %s（板 y=0 壁）：板 x 中心 %.1f 宽 %g ⇒ 模型 x %.1f..%.1f、Y %.1f..%.1f"
                    % (op["name"], op["center"], op["w"], a0, a1, ya, yb))
            else:                          # 板 x=0 那面壁 → 模型**左端（小 X）**
                ya, yb = YR(a0, a1)
                rect(sk, ox0 - 1, ya, ix0 + 1, yb)
                model_pos[op["name"]] = (ox0 - 1, ix0 + 1, ya, yb)
                log("     · 开孔 %s（板 x=0 壁）：板 y 中心 %.1f 宽 %g ⇒ 模型 x %.1f..%.1f、Y %.1f..%.1f"
                    % (op["name"], op["center"], op["w"], ox0 - 1, ix0 + 1, ya, yb))
        tray = get_body(root)
        do_extrude(root, tray, adsk.fusion.FeatureOperations.CutFeatureOperation,
                   z_top - z_from + 2, z_from, "侧壁开孔")

        # ③b **方向自检** —— 「整体镜像 / 朝向错」这类错误肉眼看等轴几何看不出来，
        #     只能靠数值判据。判据来自板布局事实（不是我的假设）：
        #       开口在板 y=0/17.8（键盘后侧）⇒ 模型 Y 必须落在**安装孔的另一侧**；
        #       三处开口都在板左端（x ≤ 33 < 板宽/2）⇒ 模型 x 必须在小半侧。
        #     ❌ 少转一处 y，这条就会立刻报错（首版漏转时：开口 Y≈0，安装孔 Y≈2…91 ⇒ 判定失败）。
        op_ys = [model_pos[n][2] for n in model_pos] + [model_pos[n][3] for n in model_pos]
        op_xs = [model_pos[n][0] for n in model_pos] + [model_pos[n][1] for n in model_pos]
        hole_ys = [YF(h["y"]) for h in holes]
        log("    · 朝向核对：开孔 模型 Y %.1f~%.1f（应在上边）、模型 x %.1f~%.1f（应在左端）；"
            "安装孔 模型 Y %.1f~%.1f" % (min(op_ys), max(op_ys), min(op_xs), max(op_xs),
                                          min(hole_ys), max(hole_ys)))
        if min(op_ys) <= max(hole_ys):
            raise RuntimeError("方向自检失败：开孔没有落在安装孔的另一侧 ⇒ 某处 y 漏了 YF()/YR()")
        if max(op_xs) >= (bx1 - bx0) / 2.0:
            raise RuntimeError("方向自检失败：开孔跑到了板宽右半侧 ⇒ x 被误取反？")
        log("    ✅ 方向自检通过：开孔在后上/左端，与板布局一致（安装孔在下边与左右两端）")

        # ④ 8 个 M2 柱（一次草图 8 个圆 ⇒ 一次 join）
        sk = root.sketches.add(plane_at(root, z_floor))
        for h in holes:
            circle(sk, h["x"], YF(h["y"]), P["boss_od"])
        tray = get_body(root)
        do_extrude(root, tray, adsk.fusion.FeatureOperations.JoinFeatureOperation,
                   z_pcb - z_floor, z_floor, "M2 柱 ×8")
        # ④b 热熔螺母孔（M2 嵌件：孔径 3.0、深 5.0 = 螺母长 4 + 让位 1）
        sk = root.sketches.add(plane_at(root, z_pcb - P["boss_pilot_depth"]))
        for h in holes:
            circle(sk, h["x"], YF(h["y"]), P["boss_pilot"])
        tray = get_body(root)
        do_extrude(root, tray, adsk.fusion.FeatureOperations.CutFeatureOperation,
                   P["boss_pilot_depth"] + 0.5, z_pcb - P["boss_pilot_depth"], "M2 热熔螺母孔 ×8")
        check_delta("④ M2 柱与螺母孔", v2, vol(root), 1.0, 4.5)

        # ⑤ 电池仓压边：**每个电池画两个同心矩形**（外框 = 电池仓 + 压边宽，内框 = 电池仓本身）
        #    ⇒ Fusion 才会把「环带」算成一个**带孔轮廓（2 个 loop）**，内框区域是 1 个 loop。
        #    ⚠️ 别用「4 个互相重叠的矩形」拼环：那样会被切成若干单环区域，
        #    且「环内区」也是一个 1 环轮廓 ⇒ 无法用 loop 数区分，会连电池仓一起填实
        #    （2026-09-21 实测：体积多增 108 而非 13 cm³）。
        bats = [(ix0 + P["bat_inset"], (iy0 + iy1) / 2 - P["bat_l"] / 2),
                (ix1 - P["bat_inset"] - P["bat_w"], (iy0 + iy1) / 2 - P["bat_l"] / 2)]
        c = P["clip"]
        sk = root.sketches.add(plane_at(root, z_floor - 0.5))
        for k, (bxx, byy) in enumerate(bats):
            rectY(sk, bxx - c, bxx + P["bat_w"] + c, byy - c, byy + P["bat_l"] + c)   # 外框
            rectY(sk, bxx, bxx + P["bat_w"], byy, byy + P["bat_l"])                   # 内框（电池仓）
            yb0, yb1 = YR(byy, byy + P["bat_l"])
            log("⑤ 电池 %d 压边（电池仓 x %.1f..%.1f，模型 Y %.1f..%.1f；压边宽 %g）"
                % (k + 1, bxx, bxx + P["bat_w"], yb0, yb1, c))
        tray = get_body(root)
        v4 = vol(root)
        do_extrude(root, tray, adsk.fusion.FeatureOperations.JoinFeatureOperation,
                   P["bat_t"] + P["clip"] + 0.5, z_floor - 0.5, "电池压边（只取环带）", min_loops=2)
        check_delta("⑤ 电池压边", v4, vol(root), 5.0, 25.0)

        # ⑤b 把模型画成**字符俯视图**（朝向的最终判据，直接写进日志 —— 不用开图就能核对）
        draw_plan(ox0, ox1, YF(oy1), YF(oy0),
                  hole_pts=[(h["x"], YF(h["y"])) for h in holes],
                  open_rects=list(model_pos.values()),
                  bat_rects=[(bxx, bxx + P["bat_w"]) + YR(byy, byy + P["bat_l"])
                             for (bxx, byy) in bats],
                  seam_x=P["seam_x"])

        # ⑥ 沿 x = seam 剖成两件
        pi = root.constructionPlanes.createInput()
        pi.setByOffset(root.yZConstructionPlane, VI(P["seam_x"]))
        seam = root.constructionPlanes.add(pi)
        tray = get_body(root)
        si = root.features.splitBodyFeatures.createInput(tray, seam, True)
        root.features.splitBodyFeatures.add(si)
        n = root.bRepBodies.count
        log("⑥ 分件后实体数 = %d" % n)
        for i in range(n):
            bd = root.bRepBodies.item(i)
            bb = bd.boundingBox
            log("   实体 %d: %-10s 体积 %.1f cm³  包围盒 %.1f × %.1f × %.1f mm"
                % (i, bd.name, bd.volume, (bb.maxPoint.x - bb.minPoint.x) * 10,
                   (bb.maxPoint.y - bb.minPoint.y) * 10, (bb.maxPoint.z - bb.minPoint.z) * 10))

        # ⑦ 导出
        em = design.exportManager
        step = os.path.join(OUT_DIR, "StarShield-case.step")
        em.execute(em.createSTEPExportOptions(step))
        log("⑦ STEP →", step)
        for i in range(root.bRepBodies.count):
            bd = root.bRepBodies.item(i)
            stl = os.path.join(OUT_DIR, "StarShield-case-%s.stl" % ("AB"[i] if i < 2 else str(i)))
            em.execute(em.createSTLExportOptions(bd, stl))
            log("   STL →", stl)

        # ⑧ 视口截图：等轴 + **俯视**
        #    俯视图是唯一能验「朝向」的手段：相机放正上方、up = +Y ⇒ **屏幕右 = +X、屏幕上 = +Y**，
        #    可直接与 PCB 布局（KiCad F.Cu 视图）逐点对照。之前只出等轴图，朝向错了根本看不出来。
        vp = app.activeViewport
        if vp:
            boxes = [root.bRepBodies.item(i).boundingBox for i in range(root.bRepBodies.count)]
            if boxes:
                x0 = min(b.minPoint.x for b in boxes); x1 = max(b.maxPoint.x for b in boxes)
                y0 = min(b.minPoint.y for b in boxes); y1 = max(b.maxPoint.y for b in boxes)
                z0 = min(b.minPoint.z for b in boxes); z1 = max(b.maxPoint.z for b in boxes)
                ctr = adsk.core.Point3D.create((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
                wide = max(x1 - x0, (y1 - y0) / 0.5625)      # 16:9 视口：高度只占 0.5625 倍宽度

                def shoot(name, eye, up, ext, note=""):
                    try:
                        cam = vp.camera
                        cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
                        cam.isFitView = False
                        cam.target = ctr
                        cam.eye = adsk.core.Point3D.create(*eye)
                        cam.upVector = adsk.core.Vector3D.create(*up)
                        cam.viewExtents = ext
                        vp.camera = cam
                        f = os.path.join(OUT_DIR, name)
                        vp.saveAsImageFile(f, 1600, 900)
                        log("   %s → %s %s" % (name, f, note))
                    except Exception as e:
                        log("   %s 跳过：%s" % (name, e))

                shoot("preview-iso.png",
                      (ctr.x + wide, ctr.y - wide, ctr.z + wide * 0.9), (0, 0, 1), wide * 1.35,
                      "（前-右-上等轴：开口应在左上）")
                shoot("preview-top.png",
                      (ctr.x, ctr.y, ctr.z + wide * 2), (0, 1, 0), wide * 1.15,
                      "（俯视：屏幕右=+X、屏幕上=+Y；开口应在左上）")
                log("   俯视对照表：安装孔 左列 x=%.1f、右列 x=%.1f、下边一排 模型 Y=%.1f；"
                    "开口在**上边**（模型 Y %.1f..%.1f）"
                    % (min(h["x"] for h in holes), max(h["x"] for h in holes),
                       min(YF(h["y"]) for h in holes), *YR(oy0 - 1, iy0 + 1)))
        log("=== 完成 ===")
        ok = True
    except Exception:
        log("❌ 异常：\n" + traceback.format_exc())
    finally:
        if _fh:
            _fh.close()
    return ok


def stop(_context):
    pass
