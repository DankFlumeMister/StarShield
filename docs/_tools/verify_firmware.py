#!/usr/bin/env python3
"""verify_firmware.py — 对 firmware/ 做静态校验

因为本机没有 Zephyr SDK（无法实跑 west build），本脚本用静态检查替代，
覆盖能在本地查证的项目：

  1. shield 文件齐套（对照 ZMK 官方 shield 的必需文件清单）
  2. build.yaml 语法与引用（board/shield 名、artifact-name）
  3. .conf 里每个 CONFIG_ 符号在 ZMK 官方 Kconfig 中存在；
     + Zephyr 侧「无 default y 必须手写」的驱动开关（如 WS2812_STRIP）是否漏写
  4. .keymap 每层绑定数 == 95，且与 transform 的位置数一致
  5. DTS 花括号/尖括号/圆括号配平（剥注释后）
  6. overlay 里引用的 phandle（&spi1/&spi3/&pro_micro/&shifter）都有定义
  7. 引脚不与保留脚冲突（P0.15 蓝灯 等）
  8. 90 颗 LED / 95 键等关键数字与文档一致
"""
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHIELD = os.path.join(ROOT, "firmware", "boards", "shields", "starshield")
ZMK = os.path.join(ROOT, "research", "_clones", "zmk")
FW = os.path.join(ROOT, "firmware")

fails = []
warns = []


def check(label, ok, detail="", warn=False):
    tag = "✅" if ok else ("⚠️ " if warn else "❌")
    print(f"  {tag} {label}" + (f"   {detail}" if detail else ""))
    if not ok and not warn:
        fails.append(label)
    if not ok and warn:
        warns.append(label)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


# ── Zephyr 侧驱动开关表（3b 用）──────────────────────────────────
# compatible: (必须出现在 .conf 里的符号, 为什么必须手写)
# 这些符号定义在 Zephyr 而非 ZMK，ZMK 的 Kconfig 里查不到，且没有 default y，
# 也不依赖 devicetree 的 compatible —— 漏写不会编译失败，只在链接期报
# `undefined reference to __device_dts_ord_<N>'，极难定位（本项目 CI 第 4 次失败）。
ZEPHYR_DRIVER_CONFIG = {
    "worldsemi,ws2812-spi": (
        "WS2812_STRIP",
        "Zephyr menuconfig，无 default y；不开则 ws2812_spi.c 不编译 → 链接期 __device_dts_ord_N 未定义",
    ),
}
# 这些由 ZMK 的 Kconfig 依据 compatible 自动打开，【不该】写进 .conf。
# 反向查证 ZMK 源码确实有自动开关（两边都不写才是真错）。
ZMK_AUTO_DRIVER = {
    "zmk,gpio-595": ("app/module/drivers/gpio/Kconfig.595", "GPIO_595"),
}
ZEPHYR_OWNED = {sym for sym, _why in ZEPHYR_DRIVER_CONFIG.values()}


print("=" * 70)
print("1. shield 文件齐套")
print("=" * 70)
REQUIRED = [
    "starshield.zmk.yml", "Kconfig.shield", "Kconfig.defconfig",
    "starshield.overlay", "starshield.keymap", "starshield.conf",
    "starshield_transform.dtsi",
]
for f in REQUIRED:
    check(f, os.path.exists(os.path.join(SHIELD, f)))

print()
print("=" * 70)
print("2. build.yaml")
print("=" * 70)
try:
    import yaml
    b = yaml.safe_load(read(os.path.join(FW, "build.yaml")))
    inc = b.get("include", []) if isinstance(b, dict) else []
    check("YAML 可解析", True, f"{len(inc)} 个构建项")
    names = []
    for it in inc:
        board = it.get("board", "")
        shield = it.get("shield", "")
        art = it.get("artifact-name")
        check(f"  项 board={board} shield={shield}", bool(board) and bool(shield))
        names.append(art or f"{shield}-{board.replace('/', '_')}-zmk")
    check("artifact-name 互不重复", len(names) == len(set(names)), ", ".join(names))
except ImportError:
    check("PyYAML 可用", False, "未安装 pyyaml，跳过 build.yaml 解析", warn=True)
except Exception as e:
    check("build.yaml 可解析", False, str(e)[:80])

print()
print("=" * 70)
print("3. .conf 里的 CONFIG 符号是否真实存在于 ZMK")
print("=" * 70)
kconfig_text = ""
for dirpath, _dirs, files in os.walk(ZMK):
    for fn in files:
        if fn.startswith("Kconfig"):
            try:
                kconfig_text += read(os.path.join(dirpath, fn)) + "\n"
            except Exception:
                pass
defined = set(re.findall(r'^\s*(?:menu)?config\s+([A-Z0-9_]+)', kconfig_text, re.M))
check("已加载 ZMK Kconfig", len(defined) > 300, f"{len(defined)} 个符号")

conf = read(os.path.join(SHIELD, "starshield.conf"))
used = re.findall(r'^(CONFIG_[A-Z0-9_]+)=', conf, re.M)
# 下面这些符号属于 Zephyr 而非 ZMK，在本机（无 Zephyr 源码）查不到，
# 交给 3b 按 devicetree compatible 反查，见文件顶部 ZEPHYR_DRIVER_CONFIG 的说明。
for sym in used:
    bare = sym[len("CONFIG_"):]
    if bare in ZEPHYR_OWNED:
        check(f"  {sym}", True, "Zephyr 符号，由 3b 按 compatible 校验")
        continue
    check(f"  {sym}", bare in defined, "" if bare in defined else "ZMK Kconfig 中不存在")

print()
print("=" * 70)
print("3b. Zephyr 侧驱动开关：该手写的有没有漏写")
print("=" * 70)
# ⚠️ 上面的 3 只检查「符号在 ZMK Kconfig 里存在」，覆盖不到 Zephyr 原生驱动开关。
#    曾经的翻车（CI 第 4 次失败）：overlay 里写了 worldsemi,ws2812-spi，
#    CONFIG_ZMK_RGB_UNDERGLOW=y 也开了，但没写 CONFIG_WS2812_STRIP=y。
#    ZMK 的 underglow 只 select LED_STRIP（上层 API），底层驱动开关是 Zephyr 的
#    menuconfig WS2812_STRIP —— 它没有 default y、也不看 devicetree 的 compatible，
#    结果 ws2812_spi.c 根本没进编译，设备结构体没生成，链接期才炸：
#    undefined reference to `__device_dts_ord_129'。
#    注意与 ZMK 自己的 595 驱动对比：Kconfig.595 写了
#    `default $(dt_compat_enabled,$(DT_COMPAT_ZMK_GPIO_595))`，所以它是自动开的。
#    两者行为不同 —— 下面把「必须手写」和「会自动开」分开断言。
ov_text = read(os.path.join(SHIELD, "starshield.overlay"))
for compat, (sym, why) in ZEPHYR_DRIVER_CONFIG.items():
    if compat not in ov_text:
        continue
    check(f"  {compat} → .conf 里有 CONFIG_{sym}=y",
          re.search(rf'^CONFIG_{sym}=y\s*$', conf, re.M) is not None,
          why)
for compat, (rel, sym) in ZMK_AUTO_DRIVER.items():
    if compat not in ov_text:
        continue
    kc = read(os.path.join(ZMK, rel))
    check(f"  {compat} → ZMK 自动开启 {sym}",
          "default $(dt_compat_enabled" in kc,
          "ZMK 源码里应有 default $(dt_compat_enabled,...)，否则该驱动永远不编译")

print()
print("=" * 70)
print("4. keymap 每层绑定数 == 95")
print("=" * 70)
km = read(os.path.join(SHIELD, "starshield.keymap"))
km_nc = re.sub(r"/\*.*?\*/", " ", km, flags=re.S)
for layer in ["default_layer", "fn_layer"]:
    m = re.search(layer + r"\s*\{(.*?)bindings\s*=\s*<(.*?)>;", km_nc, re.S)
    if not m:
        check(f"{layer} 找到", False)
        continue
    binds = re.findall(r"&\w+", m.group(2))
    check(f"  {layer} 绑定数 = {len(binds)}", len(binds) == 95)

tf = read(os.path.join(SHIELD, "starshield_transform.dtsi"))
tf_nc = re.sub(r"/\*.*?\*/", " ", tf, flags=re.S)
mapm = re.search(r"map\s*=\s*<(.*?)>;", tf_nc, re.S)
rc = re.findall(r"RC\(\s*(\d+),\s*(\d+)\)", mapm.group(1)) if mapm else []
check(f"transform 条目数 = {len(rc)}", len(rc) == 95)
cells = set((int(a), int(b)) for a, b in rc)
check(f"transform 矩阵格唯一 = {len(cells)}", len(cells) == 95, "无冲突")

print()
print("=" * 70)
print("5. DTS 括号配平（剥注释）")
print("=" * 70)
# 注意：像键盘那样键帽标签里带括号（如 `(/9` `)/0`）时，注释剥除必须换成空格占位，
# 否则注释内的括号会被误算。这里用等长空格替换，保持行结构。
for f in ["starshield.overlay", "starshield_transform.dtsi"]:
    t = read(os.path.join(SHIELD, f))
    body = re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), t, flags=re.S)
    body = re.sub(r"//[^\n]*", "", body)
    cb = body.count("{") - body.count("}")
    ab = body.count("<") - body.count(">")
    pb = body.count("(") - body.count(")")
    detail = f"{{}}={cb} <>={ab} ()={pb}"
    check(f"  {f}  {detail}", cb == 0 and ab == 0 and pb == 0)
    if pb != 0:
        for i, l in enumerate(body.splitlines(), 1):
            if l.count("(") != l.count(")"):
                print(f"        L{i}: {l.strip()[:100]}")

print()
print("=" * 70)
print("6. overlay 引用的 phandle 是否有定义")
print("=" * 70)
ov = read(os.path.join(SHIELD, "starshield.overlay"))
ov_nc = re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), ov, flags=re.S)
# 本文件 + 其本地 include 一起算作「已定义」
combined = ov_nc
for inc in re.findall(r'#include\s+"([^"]+)"', ov_nc):
    p = os.path.join(SHIELD, inc)
    if os.path.exists(p):
        sub = read(p)
        combined += "\n" + re.sub(r"/\*.*?\*/", lambda m: " " * len(m.group(0)), sub, flags=re.S)
refs = set(re.findall(r"&([a-z_][a-z0-9_]*)", combined))
labels = set(re.findall(r"^\s*([a-z_][a-z0-9_]*)\s*:", combined, re.M))
overrides = set(re.findall(r"^\s*&([a-z_][a-z0-9_]*)\s*\{", combined, re.M))
BOARD = {"spi1", "spi3", "pinctrl", "pro_micro", "gpio0", "gpio1", "adc",
         "gpiote", "usbd", "flash0", "reg0", "reg1", "key_physical_attrs"}
check("physical_layout0 已定义", "physical_layout0" in labels)
check("default_transform 已定义", "default_transform" in labels)
for r in sorted(refs):
    ok = (r in labels) or (r in overrides) or (r in BOARD)
    check(f"  &{r}", ok, "" if ok else "既非本 shield 定义，也不在板级白名单")

print()
print("=" * 70)
print("7. 关键数字与引脚安全")
print("=" * 70)
check("chain-length = 95（LED 数）", "chain-length = <95>" in ov)
check("ngpios = 24（3 颗 595 级联；2026-09-18 修订，原 2 颗驱动不了 18 列）", "ngpios = <24>" in ov)
check("diode-direction = col2row", 'diode-direction = "col2row"' in ov)
check("列数 18", len(re.findall(r"<&shifter\s+\d+", ov)) == 18,
      f"实得 {len(re.findall(r'<&shifter', ov))}")
check("行数 6", len(re.findall(r"<&pro_micro\s+\d+\s+\(", ov)) == 6,
      f"实得 {len(re.findall(r'<&pro_micro', ov)) - 1}（已扣除 cs-gpios）")
check("EXT_POWER 节点名正确", "EXT_POWER {" in ov, "ZMK 要求此名以保留用户设置")
check("未占用 P0.15（蓝灯）", "0 15" not in ov)
check("未占用 P0.13（VCC 门控）", "0 13" not in ov)

print()
print("=" * 70)
print("8. 595 与 WS2812 使用不同 SPI 外设（否则两个从设备冲突）")
print("=" * 70)
spi595 = "&spi1" in ov
spi_rgb = "&spi3" in ov
check("595 在 &spi1 且 RGB 在 &spi3", spi595 and spi_rgb, f"spi1={spi595} spi3={spi_rgb}")

print()
print("=" * 70)
if fails:
    print(f"结论：❌ 未通过（{len(fails)} 项失败）")
    for f in fails:
        print("   -", f)
    if warns:
        print(f"（另有 {len(warns)} 项警告）")
    sys.exit(1)
print("结论：✅ 全部静态校验通过")
if warns:
    print(f"（{len(warns)} 项警告，见上）")
sys.exit(0)
