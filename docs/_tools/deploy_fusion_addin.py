"""deploy_fusion_addin.py — 把外壳脚本装成 Fusion **add-in** 并设为开机自动运行。

依据（本机证据，不是猜的）：Fusion 安装目录里多个内置 add-in 的清单都写着
    "type": "addin", "id": "<guid>", "runOnStartup": true, "autodeskProduct": "Fusion"
（例：`API/InternalAddins/ElectronicsPackageGenerator/*.manifest`）
⇒ 用户 add-in 放 `%APPDATA%\\Autodesk\\Autodesk Fusion 360\\API\\AddIns\\`，
  清单带 `runOnStartup: true`，**Fusion 每次启动就会执行 run(context)**。

同时会把先前那个未文档化的 `MyScripts/Autorun` 尝试**撤掉**（避免重复执行或启动报错），
但保留 `MyScripts/StarShieldCase/` 的**脚本**副本 —— 万一自动运行失败，
用户可在「实用程序 → 脚本和加载项 → 脚本」里手动 Run。

用法：python docs/_tools/deploy_fusion_addin.py [--remove]
"""
import json
import os
import shutil
import sys
import uuid

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = r"D:/StarShield/hardware/case/fusion_build_case.py"
NAME = "StarShieldCase"
PROFILE = os.path.join(os.environ["APPDATA"], "Autodesk", "Autodesk Fusion 360")
ADDIN_DIR = os.path.join(PROFILE, "API", "AddIns", NAME)
SCRIPT_DIR = os.path.join(PROFILE, "MyScripts", NAME)
AUTORUN_DIR = os.path.join(PROFILE, "MyScripts", "Autorun", NAME)

MANIFEST = {
    "autodeskProduct": "Fusion",
    "type": "addin",
    "id": "7c1f0a34-2b6e-4d51-9c6a-3f8e2d4b7a10",
    "author": "StarShield",
    "description": {"": "StarShield 底壳参数化建模：读 hardware/case/case_inputs.json，"
                         "建底壳两件并导出 STEP/STL"},
    "version": "1.0.0",
    "runOnStartup": False,   # ⚠️ 启动阶段跑重活会把 Fusion 跑崩（2026-09-21 实测），故关闭
    "supportedOS": "windows|mac|linux",
    "editEnabled": True,
}

if "--remove" in sys.argv:
    for d in (ADDIN_DIR, SCRIPT_DIR, AUTORUN_DIR):
        if os.path.isdir(d):
            shutil.rmtree(d)
            print("已删除", d.replace(PROFILE, "…"))
    info = os.path.join(PROFILE, "PythonAutorunModuleinfo")
    json.dump({"enabledModules": [], "lastAppInstallTime": 0},
              open(info, "w", encoding="utf-8", newline="\n"))
    print("已清空 Autorun 列表")
    sys.exit(0)

# 1) add-in（自动运行）
os.makedirs(ADDIN_DIR, exist_ok=True)
shutil.copy2(SRC, os.path.join(ADDIN_DIR, NAME + ".py"))
with open(os.path.join(ADDIN_DIR, NAME + ".manifest"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(MANIFEST, f, indent=2, ensure_ascii=False)

# 2) 脚本副本（手动兜底）
os.makedirs(SCRIPT_DIR, exist_ok=True)
shutil.copy2(SRC, os.path.join(SCRIPT_DIR, NAME + ".py"))
with open(os.path.join(SCRIPT_DIR, NAME + ".manifest"), "w", encoding="utf-8", newline="\n") as f:
    m = dict(MANIFEST)
    m.update({"type": "script", "runOnStartup": False, "id": str(uuid.uuid4())})
    json.dump(m, f, indent=2, ensure_ascii=False)

# 3) 撤掉 Autorun 那份未文档化的尝试
if os.path.isdir(AUTORUN_DIR):
    shutil.rmtree(AUTORUN_DIR)
    print("已撤掉 MyScripts/Autorun 副本")
json.dump({"enabledModules": [], "lastAppInstallTime": 0},
          open(os.path.join(PROFILE, "PythonAutorunModuleinfo"), "w", encoding="utf-8", newline="\n"))

print("add-in  →", ADDIN_DIR.replace(PROFILE, "…"))
print("脚本副本 →", SCRIPT_DIR.replace(PROFILE, "…"))
print("runOnStartup =", MANIFEST["runOnStartup"], "| id =", MANIFEST["id"])
