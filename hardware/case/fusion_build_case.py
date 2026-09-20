# -*- coding: utf-8 -*-
"""StarShield 底壳 —— Fusion 360 参数化建模脚本（Python API，在 **Fusion 内部**运行）。

设计依据（全部来自工程文档，不是自由发挥）：
  - **PCB 是上盖**、**底壳按约等分两件**（缝落在键位列边界）：`docs/hardware-geometry.md` §3.1（G4）
  - 侧壁 2 mm、外扩 4 mm/边、M2 自攻柱 φ4–5：`docs/decision-package-2026-09-18.md` §3
  - 8 个 M2 安装孔（NPTH φ2.2，H1–H8）：从板文件提取
  - 三处开孔坐标：`docs/nice-nano-physical-verification.md` §6.7
  - 电池仓左右各 10.5 × 56 × 68、机壳深 ≥11 mm：`docs/power-architecture.md` §3.6（G5）

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
  hardware/case/out/preview-iso.png                 视口截图（复核用）
  hardware/case/out/build.log                       运行日志（逐步 + 体积自检）
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
P = {
    "wall": 2.0, "floor": 2.5, "clearance": 0.3, "depth": 15.0, "lip": 4.5,
    "boss_od": 5.0, "boss_pilot": 1.7, "boss_pilot_depth": 8.0,
    "bat_w": 56.0, "bat_l": 68.0, "bat_t": 10.5, "bat_inset": 8.0,
    "clip": 2.0, "clip_len": 12.0, "clip_arm": 12.0,
    "seam_x": 189.70,
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
        ix0, iy0 = bx0 - P["clearance"], by0 - P["clearance"]
        ix1, iy1 = bx1 + P["clearance"], by1 + P["clearance"]
        ox0, oy0 = ix0 - P["wall"], iy0 - P["wall"]
        ox1, oy1 = ix1 + P["wall"], iy1 + P["wall"]
        log("内腔 %.2f × %.2f；外形 %.2f × %.2f；总高 %.2f；板下净空 %.1f"
            % (ix1 - ix0, iy1 - iy0, ox1 - ox0, oy1 - oy0, z_top, P["depth"]))

        # ① 外形（新建 body）
        sk = root.sketches.add(plane_at(root, 0))
        rect(sk, ox0, oy0, ox1, oy1)
        do_extrude(root, None, adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
                   z_top, 0, "外形")
        tray = get_body(root)
        log("① 外形体积 %.1f cm³" % tray.volume)

        # ② 挖内腔
        sk = root.sketches.add(plane_at(root, z_floor))
        rect(sk, ix0, iy0, ix1, iy1)
        tray = get_body(root)
        do_extrude(root, tray, adsk.fusion.FeatureOperations.CutFeatureOperation,
                   z_top - z_floor + 2, z_floor, "内腔")
        v2 = vol(root)
        log("② 挖腔后体积 %.1f cm³" % v2)

        # ③ 三处侧壁开孔（顶部开口的槽）—— 一个草图装 3 个矩形，一次切
        z_from = z_pcb - 1.0
        sk = root.sketches.add(plane_at(root, z_from))
        for op in OPENINGS:
            a0, a1 = op["center"] - op["w"] / 2, op["center"] + op["w"] / 2
            if op["kind"] == "front":
                rect(sk, a0, oy0 - 1, a1, iy0 + 1)
            else:
                rect(sk, ox0 - 1, a0, ix0 + 1, a1)
            log("     · 开孔 %s（%s 壁，中心 %.1f，宽 %g）" % (op["name"], op["kind"], op["center"], op["w"]))
        tray = get_body(root)
        do_extrude(root, tray, adsk.fusion.FeatureOperations.CutFeatureOperation,
                   z_top - z_from + 2, z_from, "侧壁开孔")

        # ④ 8 个 M2 柱（一次草图 8 个圆 ⇒ 一次 join）
        sk = root.sketches.add(plane_at(root, z_floor))
        for h in holes:
            circle(sk, h["x"], h["y"], P["boss_od"])
        tray = get_body(root)
        do_extrude(root, tray, adsk.fusion.FeatureOperations.JoinFeatureOperation,
                   z_pcb - z_floor, z_floor, "M2 柱 ×8")
        # ④b 底孔
        sk = root.sketches.add(plane_at(root, z_pcb - P["boss_pilot_depth"]))
        for h in holes:
            circle(sk, h["x"], h["y"], P["boss_pilot"])
        tray = get_body(root)
        do_extrude(root, tray, adsk.fusion.FeatureOperations.CutFeatureOperation,
                   P["boss_pilot_depth"] + 0.5, z_pcb - P["boss_pilot_depth"], "M2 底孔 ×8")
        check_delta("④ M2 柱与底孔", v2, vol(root), 0.5, 5.0)

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
            rect(sk, bxx - c, byy - c, bxx + P["bat_w"] + c, byy + P["bat_l"] + c)   # 外框
            rect(sk, bxx, byy, bxx + P["bat_w"], byy + P["bat_l"])                   # 内框（电池仓）
            log("⑤ 电池 %d 压边（电池仓 x %.1f..%.1f，y %.1f..%.1f；压边宽 %g）"
                % (k + 1, bxx, bxx + P["bat_w"], byy, byy + P["bat_l"], c))
        tray = get_body(root)
        v4 = vol(root)
        do_extrude(root, tray, adsk.fusion.FeatureOperations.JoinFeatureOperation,
                   P["bat_t"] + P["clip"] + 0.5, z_floor - 0.5, "电池压边（只取环带）", min_loops=2)
        check_delta("⑤ 电池压边", v4, vol(root), 5.0, 25.0)

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

        # ⑧ 视口截图
        vp = app.activeViewport
        if vp:
            try:
                vp.fit()
                png = os.path.join(OUT_DIR, "preview-iso.png")
                vp.saveAsImageFile(png, 1600, 900)
                log("⑧ 预览图 →", png)
            except Exception as e:
                log("⑧ 预览图跳过：%s" % e)
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
