#!/usr/bin/env python3
"""route_freerouting.py — 用 Freerouting 对 StarShield 板子跑自动布线（B4）

为什么需要这个脚本：Freerouting 只能用绝对路径的 java 调（KiCad MCP 的
`autoroute` 工具不带 javaPath 参数，且 MCP 进程的环境变量是启动时快照的，
装完 Java 也要重启 WorkBuddy 才认），而且 DSN 在交给它之前必须做两处调整。
把这些坑一次固化，避免每次重新试。

== 前置（本机 2026-09-18 装好）==
  Java 25   D:\\Tools\\jre-25\\bin\\java.exe        （⚠️ 必须 25：freerouting 2.4.1
                                                    是 class 版本 69.0，Java 21 只认到 65.0）
  jar       C:\\Users\\admin\\.kicad-mcp\\freerouting.jar （v2.4.1，github 直连被拦，
                                                    需经 https://gh-proxy.com/ 前缀下载）

== 完整流程（DSN/SES 的导出与导入只能走 KiCad MCP，kicad-cli 没有这两个子命令）==
  1. MCP `open_board` 打开 .kicad_pcb
  2. MCP `export_dsn` 导出 DSN
  3. 本脚本：调 VLED 宽度 + （可选）摘网络 + 跑 Freerouting → 出 .ses
  4. MCP `import_ses` 把 .ses 并回板子
  5. MCP `save_board` ⚠️ **它会连「当前加载路径」一起写**，不只是你指定的 boardPath
  6. MCP `run_drc` 看结果 ⚠️ 它会往板子所在目录丢 Starshield_drc_violations.json，用完要删

== 为什么必须调 VLED 的走线宽度 ==
  板子里 VLED 是 **2.0 mm**（2–3 A 的载流要求，ADR-0007）。但 2.0 mm 宽要在
  19.05 mm 键位栅格（轴体孔占 14 mm）里连 95 个灯珠 VDD —— 实测 `-mp 30` 跑 5 分钟
  一个 pass 都完不成、内存涨到 2.4 GB。
  ⇒ 交给布线器时降到 0.25 mm（**只负责连通性**），**载流另靠铺铜/内层平面**。

== 线程数与时长（本机 16 逻辑核，实测）==
  -mt 4  → 单 pass 约 350 s；**-mt 12 → 单 pass 约 60–90 s**，建议 12。
  注意 Freerouting 会警告「多线程**优化**阶段会生成间距违规」；若最后要零违规，
  可再用 `-mt 1` 跑一轮优化。
"""
import argparse
import os
import re
import subprocess
import sys

DEFAULT_JAVA = r"D:\Tools\jre-25\bin\java.exe"
DEFAULT_JAR = r"C:\Users\admin\.kicad-mcp\freerouting.jar"


def set_class_width(text, cls_substr, width_um):
    """把某个 class 的 (width N) 改成 width_um。返回 (新文本, 替换次数)。"""
    pat = re.compile(r"(\(class [^\n]*" + re.escape(cls_substr) +
                     r"[\s\S]{0,160}?\(width )(\d+)(\))")
    return pat.subn(lambda m: f"{m.group(1)}{width_um}{m.group(3)}", text, count=1)


def drop_nets(text, names):
    """按括号配平删掉 `(net NAME ...)` 与含这些名字的 `(class ...)`（跳过字符串里的括号）。"""
    def blocks(t, head):
        out = []
        for m in re.finditer(head, t):
            j, k, depth, inq, esc, n = m.start(), m.start(), 0, False, False, len(t)
            while k < n:
                ch = t[k]
                if inq:
                    if esc:
                        esc = False
                    elif ch == "\\":
                        esc = True
                    elif ch == '"':
                        inq = False
                else:
                    if ch == '"':
                        inq = True
                    elif ch == "(":
                        depth += 1
                    elif ch == ")":
                        depth -= 1
                        if depth == 0:
                            break
                k += 1
            out.append((j, k + 1, t[j:k + 1]))
        return out

    removed = []
    for a, b, blk in reversed(blocks(text, r"\(net\s")):
        m = re.match(r'\(net\s+"?([^"\s\)]+)', blk)
        if m and m.group(1) in names:
            text = text[:a] + text[b:]
            removed.append("net:" + m.group(1))
    for a, b, blk in reversed(blocks(text, r"\(class\b")):
        flat = set(x for pair in re.findall(r'"([^"]+)"|([A-Za-z_][\w\-\.\+]*)', blk[:400])
                   for x in pair if x)
        hit = flat & set(names)
        if hit:
            text = text[:a] + text[b:]
            removed.append("class:" + ",".join(sorted(hit)))
    return text, removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dsn", help="输入 .dsn")
    ap.add_argument("ses", help="输出 .ses")
    ap.add_argument("--passes", type=int, default=16)
    ap.add_argument("--threads", type=int, default=12)
    ap.add_argument("--vled-width", type=int, default=250, help="VLED 类宽度 µm（默认 250）")
    ap.add_argument("--drop-nets", nargs="*", default=[],
                    help="从布线输入里摘掉的网络（如交给铺铜/平面承载的 GND VLED）")
    ap.add_argument("--java", default=DEFAULT_JAVA)
    ap.add_argument("--jar", default=DEFAULT_JAR)
    ap.add_argument("--keep-prepared", action="store_true", help="保留中间 DSN")
    a = ap.parse_args()

    if not os.path.exists(a.java):
        sys.exit(f"找不到 java：{a.java}（见本文件顶部说明）")
    if not os.path.exists(a.jar):
        sys.exit(f"找不到 freerouting.jar：{a.jar}")

    text = open(a.dsn, encoding="utf-8").read()
    text, n = set_class_width(text, "VLED", a.vled_width)
    print(f"VLED 宽度 -> {a.vled_width} µm（替换 {n} 处）")

    if a.drop_nets:
        text, removed = drop_nets(text, set(a.drop_nets))
        print("摘除：", removed or "（无匹配）")

    prep = os.path.splitext(a.ses)[0] + ".prepared.dsn"
    with open(prep, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

    cmd = [a.java, "-jar", a.jar, "-de", prep, "-do", a.ses,
           "-mp", str(a.passes), "-mt", str(a.threads), "-l", "en"]
    print("执行：", " ".join(cmd))
    log = os.path.splitext(a.ses)[0] + ".log"
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT).returncode
    print("freerouting 退出码:", rc)

    for line in open(log, encoding="utf-8", errors="replace").read().splitlines():
        if "Auto-routing pass" in line or "Auto-routing stage completed" in line:
            print("  ", line.strip()[:170])

    if not os.path.exists(a.ses):
        sys.exit("未生成 .ses —— 看日志：" + log)
    print(f"✅ 产出 {a.ses}（{os.path.getsize(a.ses)} 字节）")
    if not a.keep_prepared:
        os.remove(prep)
    print("下一步：MCP `import_ses` 把 .ses 并回板子（注意 save_board 的坑，见文件头）")


if __name__ == "__main__":
    main()
