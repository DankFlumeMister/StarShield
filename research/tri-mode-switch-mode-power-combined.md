# Tri-mode keyboard: does ONE switch double as mode selector AND battery disconnect?

Research question: in Chinese-market 三模 (tri-mode) mechanical keyboards, does any real
product/project use a **single multi-position switch** whose positions include the
connection-mode selection (wired USB / Bluetooth / 2.4G) **and** a position that
**disconnects the battery**, such that the wired/USB position also cuts the battery?

All raw source URLs are given. "Read" = I opened the actual document/file/artefact.
"Claimed" = a page asserted it and I could not inspect the underlying artefact.

---

## EVIDENCE TABLE

| Project / Product | What the switch does exactly | Source URL | Verified how |
|---|---|---|---|
| **OSHWHub `c3h4o` CH582M 三模61 keyboard** (Chinese open-source hardware, C3H4O, 2023-06-30) | Case switch **SW2 = `MST22D18G2 125`** = **DPDT (双刀双掷), 6 pins, 两档 (2-position)**, LCSC `C2906280`. Schematic marks **pins 1 and 4 `NO_CONNECT`** → only **two live contacts per pole** (2↔3, 5↔6). Pole X (2/5) is on the **`BAT+` net** and its branch lands on the **`Q2` AO3401A + `D67` 1N5819WS** cell; pole Y (3/6) branches to the **`U9` RT9013-3.3 LDO + `R7` 100k / `C7` 1u** node. It is **not** a 3-mode selector: `README` says mode switching is done by **hotkeys** (`Fn+Print-screen`→蓝牙, `Fn+Scroll-Lock`→2.4G, `Fn+Pause`→USB). | Project page: https://oshwhub.com/c3h4o/ch582msan-mu-61jian-pan<br>Attachment ZIP: https://image.lceda.cn/attachments/2023/8/D1C3xx3Lb1qwvDJKQnESvo96oMg5zRBmYhJtdzez.zip | **Read the actual files.** Downloaded the 10 MB attachment; extracted `ProProject_CH582M三模61键盘….epro` → read `project.json`, `SYMBOL/fb97d3fc…esym`, `SHEET/…/2.esch`, `PCB/….epcb`. See raw quotes below. |
| **WCH (南京沁恒) official reference design `WCH-3MDOKBD-R0-1v3`** (the vendor reference for CH582M tri-mode keyboards) | Contains **only `SW-PB` (a push button) and `Header 2`** at the battery area — **no mode-selector switch at all**. Mode switching is entirely firmware: README hotkey table. Power is an automatic OR, not switch-selected: *"电源在接入USB时使用USB电源，未接入USB时使用电池供电"* (USB powers it when plugged; battery when unplugged). Power-gating net names present: `VBAT`, `VBAT_EN`, `USBCEK`, `BT-`. | Same OSHWHub attachment ZIP (contains `丐61配列第一版定版/3modekbd-main/`): https://image.lceda.cn/attachments/2023/8/D1C3xx3Lb1qwvDJKQnESvo96oMg5zRBmYhJtdzez.zip<br>Altium source: `3modekbd-main/hardware/WCH-3MDOKBD-R0-1v3.zip` | **Read the actual files.** `README.md`; extracted `WCH-3MDOKBD-R0-1v3.SchDoc` (Altium OLE) and parsed 17,991 Altium records — enumerated every component instance (`RECORD=1`) and every text net label (`RECORD=25`). |
| **RK (皇家克拉奇) G68** tri-mode | **TWO separate back switches.** Manual text: *"背部开关ON：另外一个开关在 B 为蓝牙模式 / 背部开关ON：另外一个开关在 G 为2.4G模式"*; *"有线模式：插入USB线到电脑，键盘强制进入有线模式，无需切换"* (plugging USB forces wired mode — **no switch position for wired**); *"请将产品背面开关调至off状态以便省电"*. → one **ON/OFF power switch** + one **B/G mode switch**. | https://blog.csdn.net/a1036884790/article/details/116975755 | **Read the manual text** (CSDN reproduction of the shipped 说明书). |
| **御斧 Y68** tri-mode | **TWO separate switches** — a power switch plus a separate thumb-wheel mode selector. *"细节上，开关跟模式切换分离。模式切换利用推杆滚轮方案"*, and the power switch is next to the Type-C port *"旁边则是电源开关以及接收器收纳槽"*. Reviewer's directly on-point analysis: *"虽然切换到有线模式，但只要开关处于ON档，按下任意键它还是会亮灯，并不能看作是关闭电源。站在使用层面，如果把有线模式同时定义成关机，对于那些习惯关闭电源的用户来说，要更方便一些。"* → **in wired mode the battery is still connected and the board is still live**; the reviewer treats "make wired mode also mean OFF" as a *wish*, i.e. **not** the design. | https://www.inwaishe.com/archiver/tid-30872.html | **Read the review text** (direct quote). Not a teardown/schematic — no PCB inspection. |
| **WOB RAINY75** tri-mode | **Not combined.** *"坏消息，电源开关藏在Capslock下面，好消息，模式切换是用FN组合键完成"* → hidden **power-only** switch + **FN hotkey** mode switching. | https://www.inwaishe.com/archiver/index.php?action=tid&value=33825 | **Read the review text** (direct quote). |
| **Darmoshark 达摩鲨 Top75** tri-mode | **Not combined.** *"当电源开关拨到OFF时，插线优先进入有线模式，无需切换"* — a single **power** switch (OFF is a global power cut), and wired mode is triggered by **cable insertion**, not by a switch position; 2.4G/BT by `FN+Q`/`FN+E/R/T`. | http://www.inwaishe.com/archiver/index.php?action=tid&value=34530 | **Read the review/manual text** (looks like transcribed manual copy). |
| **MCHOSE 迈从 K980** tri-mode | **Not combined.** *"有线模式…打开键盘底部的电源开关就能用。如果需要连接电脑，记得底部还有一个MAC向USB的转换线开关"*; Bluetooth/2.4G entered by long-pressing `FN`+arrow / `FN+H`. → bottom **power switch** + a separate small **MAC/USB converter switch** + **hotkeys** for BT/2.4G. | https://page.sm.cn/blm/node-page-new-995/index?id=28_0f9bff34109b4171ad5e4e3f055fd5b4 | **Read the article text.** (AI-ish summary page; treated as *claimed*, consistent with the pattern.) |
| **七彩虹 COLORFUL KB8PRO** tri-mode | **Not combined.** *"前部是模式切换开关、指示灯以及Type C接口"* and in teardown *"充电电路和键盘模式开关都在这块子PCB上"*. Mode logic split across **two chips**: `WB32F` (USB wired) + `EP2110` (BT/2.4G RF) — so mode selection is a **logic/GPIO** function, not a power-path function. | https://www.weistang.com/portal.php?mod=view&aid=25642&page=3 and `…&page=4` | **Read the review text** (teardown narration + captions). No schematic; no switch part number. |
| **雷神 ThundeRobot VIC84** tri-mode — *best candidate* | Rear slider described as *"其中一个分别是连接模式/开关，只要档位拨动到关档位，键盘就会强制关机，哪怕用的是有线模式"* → a connection-mode selector that **includes an OFF détente**, and OFF **force-powers-off even in wired mode**. | in外设: http://www.inwaishe.com/archiver/index.php?action=tid&value=31526<br>mirror: https://www.163.com/dy/article/HKKURV870530P1BL.html | **Claimed only** — prose in a forum teardown review. **No photo of the switch or its pins was readable**, no schematic, no official manual found. The sentence is ambiguous ("其中一个" = "one of them", implying ≥2 sliders) and never says the OFF position *disconnects the battery*. |
| **雷神 ThundeRobot Zero75** tri-mode | Two distinct controls: *"键盘左侧配备了独立金属滚轮和三模切换开关"*, and *"旁边则是电源开关以及接收器收纳槽"* (next to it are the **power switch** and the dongle storage) — i.e. **power switch and mode switch are separate**. The mode switch is mode-only: *"容易拨动过头，直接从蓝牙模式切换到2.4G无线模式"* (no OFF mentioned on it). | http://www.inwaishe.com/archiver/index.php?action=tid&value=33584 | **Read the review text** (direct quotes). |
| **雷神 ZERO75 (磁轴, unrelated model)** | Switch is `WORK`/`GAME` — a **2-position typing-mode** switch, nothing to do with power or connectivity. Good example of why "侧边开关" text alone proves nothing. | https://max.book118.com/html/2025/0923/5200021034012333.shtm | **Read the manual text.** |

---

## RAW QUOTES FROM ARTEFACTS I READ DIRECTLY

**1. Switch is a DPDT, 2-position, 6-pin part** (from the extracted `project.json`, device
`3fc6cc28c7214a7b9990ddf2027acd43`):

```
"title": "MST22D18G2 125",
"LCSC Part Name": "拨动开关/两档立式 6脚贴片 柄长2.0mm 大六立贴 9.1*3.5mm",
"Supplier Part": "C2906280",
"Manufacturer": "SHOU HAN(首韩)",
"Manufacturer Part": "MST22D18G2 125",
"Current Rating (DC)": "100mA",   "Voltage Rating (DC)": "12V",
"Circuit": "双刀双掷",   "Mounting Style": "立贴",   "Mechanical Life": "10000",
```

**2. Symbol has 6 pins in two rows of 3, each row end-labelled A / B** (from
`SYMBOL/fb97d3fcb7cf4df98a13c3532ae96f26.esym`):

```
["TEXT","e3",-13,15.98611,0,"A",...]   ["TEXT","e4",6,19.98611,0,"B",...]
["TEXT","e5",-13,-24.26389,0,"A",...]  ["TEXT","e6",6,-29.01389,0,"B",...]
["PIN","e13",1,1,-20,30,10,270,...]  NAME=1     ["PIN","e17",...0,30...] NAME=2   ["PIN","e21",...20,30...] NAME=3
["PIN","e25",1,1,-20,-30,10,90,...]  NAME=4     ["PIN","e29",...0,-30...] NAME=5   ["PIN","e33",...20,-30...] NAME=6
```

**3. Pins 1 and 4 are explicitly unused** (from `SHEET/…/2.esch`, lines 3669–3672):

```
["ATTR","e17376","e17260e13","NO_CONNECT","yes",0,0,1875,1670,0,"st1",0]
["ATTR","e17377","e17260e25","NO_CONNECT","yes",0,0,1875,1610,0,"st1",0]
```

**4. The four live contacts are hard-wired as two paralleled 2-throw poles**
(same file; SW2 anchor (1895,1640), pin screen positions p1(1875,1610) p2(1895,1610)
p3(1915,1610) p4(1875,1670) p5(1895,1670) p6(1915,1670)):

```
["WIRE","e17365",[[1895,1730,1895,1670],[1830,1730,1825,1730],[1830,1730,1830,1715],[1895,1670,1895,1610],[1895,1730,1830,1730]],"st12",0]
   -> ties SW2 p5(1895,1670) to SW2 p2(1895,1610)   [pole X, both live contacts shorted = one circuit switched twice]
   -> branch (1895,1730)-(1830,1730)-(1830,1715); the BAT+ net port is anchored at (1830,1675)
      and Q2 = AO3401A sits at (1820,1695), D67 = 1N5819WS at (1805,1730)
["WIRE","e17374",[[1980,1665,1980,1670],[1980,1670,1915,1670],[2035,1665,2035,1655],[2035,1665,2020,1665],[2020,1665,1980,1665],[1980,1665,1980,1625],[2035,1625,2025,1625],[2035,1635,2035,1625],[2025,1625,1980,1625],[1915,1610,1915,1670]],"st12",0]
   -> ties SW2 p6(1915,1670) to SW2 p3(1915,1610)   [pole Y, likewise shorted]
   -> branch to (2035,1625)-(2035,1665) and (2020,1665)-(1980,1665);
      U9 = RT9013-3.3GB sits at (2075,1645), R7 = 100k at (2025,1605), C7 = 1u at (2020,1685)
```

> ⚠️ Geometric note: the BAT+ net-port anchor (1830,1675) lies on the **x=1830 vertical run**
> (y 1715→1730) only via the segment `[1830,1730,1830,1715]`, i.e. the net port is placed at the
> *end* of that stub. I am therefore reporting pole X as **on/adjacent to the BAT+ node and the
> Q2/D67 cell**, and pole Y as **at the U9 RT9013 LDO input node (R7/C7)**. Whether the net port
> makes a hard junction on that stub, and which AO3401 pin each pole reaches, is
> **not fully resolved** (see UNVERIFIED #2).

Net labels present on the same schematic sheet, with their net-port anchor coordinates:
`BAT+` at (2290,1915), (2130,1890) and **(1830,1675 — the one beside SW2)**;
`+5V` at (2180,1920), (1985,1875), (2515,1860), (2635,1815), (1760,1730);
`+3.3V` at (275,2015), (2180,1650), (1195,1645); `VDCIA`; `BLUE_TOOTH` at (2750,705) and
(2960,705); `2.4G` at (2750,650) and (2960,650). Note `BLUE_TOOTH`/`2.4G` are anchored far
away (~x2750/2960, near the MCU) — **not** at SW2 (x≈1895).

**5. The battery is permanently wired to the charger, NOT switched to the charger**
(from the same schematic, resolved pin nets): `U4 (TP4056).9 -> BAT+`. So the charger always
sees the cell; the switch cannot be gating charge current.

**6. The vendor reference design has no mode switch.** WCH README hotkey table:

```
| Fn+Print-screen | 切换至蓝牙模式 |
| Fn+Scroll-Lock  | 切换至2.4G模式 |
| Fn+Pause        | 切换至USB模式  |
```

and, on power:
```
电源在接入USB时使用USB电源，未接入USB时使用电池供电。
```

**7. RK G68 manual (two switches):**
```
有线模式：插入USB线到电脑，键盘强制进入有线模式，无需切换
背部开关ON：另外一个开关在 B 为蓝牙模式
背部开关ON：另外一个开关在 G 为2.4G模式
请将产品背面开关调至off状态以便省电
```

---

## ANSWER

**NO — for combined "mode + battery disconnect" in the wired position.**
**PARTIAL / UNCERTAIN — for "OFF is simply one position of the mode switch".**

1. **Wired/USB position that also disconnects the battery: NOT FOUND.** In every case I could
   actually inspect (OSHWHub schematic, WCH reference, RK G68 manual, 御斧 Y68, RAINY75,
   Top75, K980, KB8PRO), **wired/USB mode is entered by plugging in the cable, not by a switch
   position**, and the battery stays electrically present. 御斧 Y68 states this outright: with
   the switch ON, wired mode still lights up on keypress and *"并不能看作是关闭电源"*.
   The WCH reference design does exactly what the question asks about but in **silicon**:
   *"电源在接入USB时使用USB电源，未接入USB时使用电池供电"* — an automatic USB/battery OR,
   with `VBAT_EN`/`USBCEK` as control nets. That is the opposite of a switch doing it.

2. **"OFF/关机 as one of the switch positions": YES, this pattern exists — but the switch
   carries OFF + the *connection* modes, not the battery disconnect for the wired case.**
   * **雷神 VIC84** (best candidate): a connection-mode selector that includes an OFF détente,
   and OFF force-powers-off *"哪怕用的是有线模式"* (even in wired mode). ⚠️ But this is
   **claimed in review prose only** — no schematic, no readable switch photo, no official manual.
   * **Darmoshark Top75**: single power switch where OFF is a global cut, but wired mode is
     cable-triggered and the 2.4G/BT selection is on hotkeys — so it is NOT a 3-mode+OFF switch.
   * **RK G68**: OFF is on a *separate* switch from the B/G mode switch.

3. **Is the case switch a 2-pole part?** In the one case I could verify at part level, **yes** —
   but for *current-sharing*, not for combining mode+power. `MST22D18G2` is **`双刀双掷` (DPDT)**,
   and the designer **left pins 1 and 4 `NO_CONNECT`**, paralleling both poles onto the same two
   nets. So a 2-pole switch here is **not** evidence of combined mode+power: it is one circuit
   switched twice.

**Most likely reason the combined design is rare:** mainstream tri-mode boards use a
**two-chip architecture** (wired/USB MCU + separate BT/2.4G RF SoC, as documented in the
KB8PRO teardown: `WB32F` for USB, `EP2110` for BT/2.4G). Mode selection is therefore a
**GPIO/firmware** decision, while power is a **power-path** decision on a separate rail —
so the two naturally end up on different switches.

---

## NEAR-MISSES (two separate switches, explicitly documented)

| Product | Switch A | Switch B | Source |
|---|---|---|---|
| **RK G68** | back `ON`/`OFF` = **power only** | second back switch `B`/`G` = **Bluetooth / 2.4G only** | https://blog.csdn.net/a1036884790/article/details/116975755 |
| **御斧 Y68** | dedicated **power switch** (ON/OFF) | separate **thumbbwheel/推杆滚轮** mode selector | https://www.inwaishe.com/archiver/tid-30872.html |
| **MCHOSE 迈从 K980** | bottom **power switch** | separate **MAC↔USB** switch; BT/2.4G by `FN` hotkeys | https://page.sm.cn/blm/node-page-new-995/index?id=28_0f9bff34109b4171ad5e4e3f055fd5b4 |
| **WOB RAINY75** | **power switch hidden under CapsLock** | **FN hotkeys** for mode | https://www.inwaishe.com/archiver/index.php?action=tid&value=33825 |
| **Darmoshark Top75** | single **power switch** (OFF = global cut) | `FN+Q` / `FN+E/R/T` for 2.4G / BT | http://www.inwaishe.com/archiver/index.php?action=tid&value=34530 |
| **雷神 Zero75** | **mode-only** 三模切换开关 (no OFF) | 独立金属滚轮 (volume/lighting) | http://www.inwaishe.com/archiver/index.php?action=tid&value=33584 |
| **WCH reference design** | `SW-PB` **push button** (power related) | **no mode switch** — firmware hotkeys only | OSHWHub attachment (README) |
| **OSHWHub CH582M 61** | `SW2` DPDT (2-position: battery ⇄ other) | **no mode switch** — firmware hotkeys only | https://oshwhub.com/c3h4o/ch582msan-mu-61jian-pan |

---

## EXPLICIT "UNVERIFIED" LIST

1. **Whether 雷神 VIC84's OFF détente physically opens the battery** — UNVERIFIED. The claim
   *"只要档位拨动到关档位，键盘就会强制关机，哪怕用的是有线模式"* is review prose. I could not
   obtain the official VIC84 manual, a switch part number, or a legible switch photo. Whether it
   is a 4-position (OFF/2.4G/BT/wired) or 3-position switch is UNVERIFIED.
2. **The complete power-OR topology of the OSHWHub CH582M 61 board** — PARTIALLY VERIFIED.
   The 10 power-path components (`Q2 AO3401A`, `U10 AO3401`, `D67 1N5819WS`, `U9 RT9013-3.3`,
   `U7 电池盒接口`, `SW2`, `U4 TP4056`, `TYPEC…`, `1N5819WS`, `32.768K`) are **EDA "Reuse Block"
   instances carrying no `Symbol` attribute** in the schematic, so their individual pin geometry
   could not be resolved programmatically (a `Symbol`-driven resolver returned 314 pins, none of
   them for these 10 parts). I verified: SW2's own six pin positions, that pins 1 & 4 are
   `NO_CONNECT`, that the two live contacts of each pole are hard-shorted by wires, the nets
   those wires reach, and `U4 (TP4056).9 = BAT+`. The **exact role of the 1N5819WS + AO3401
   pair, and which AO3401 terminal each pole lands on, is inferred from part choice and
   adjacency, not read from a net list** → treat as UNVERIFIED. The project's `.epcb` has
   `PAD_NET` records for only 167 of the components and does **not** cover these reuse blocks.
3. **Whether `BLUE_TOOTH` / `2.4G` net ports are thrown by SW2** — UNVERIFIED, and the
   evidence points away from it. Those net ports are anchored at (2750,705)/(2960,705) and
   (2750,650)/(2960,650) — roughly 900 units away in x from SW2 at (1895,1640) — and the README
   says mode is switched by hotkeys. So they are almost certainly **not** on SW2. Not proven
   either way, because SW2's poles resolve to unlabelled wires.
4. **Any Chinese brand manual that literally prints `OFF` as a label on a 3-mode selector** —
   UNVERIFIED / NOT FOUND. I looked at RK G68, MCHOSE K980, 雷神 ZERO75, and multiple teardown
   write-ups; none printed a switch legend with OFF + all three modes.
5. **The WCH reference design's per-pin power-path connectivity** — UNVERIFIED. The `.PcbDoc`
   netlist stream could not be decoded (the OLE `Data` streams are opaque binary; the only
   readable wide-string stream, 8,558 bytes, holds designators/part numbers, not nets). I read
   the **net *names*** (`VBAT`, `VBAT_EN`, `USBCEK`, `BT-`) as schematic text labels only.
6. **Whether `USBCEK`/`VBAT_EN` actually gate the battery** — UNVERIFIED (names + presence
   only; the gates themselves are in the undecoded block instances).
7. **Bilibili teardown videos / Zhihu articles / 什么值得买 teardowns** — NOT ACCESSED.
   zhihu.com returned HTTP 403, bilibili was not reachable for frame-level inspection,
   tieba.baidu.com returned a security check (403), manuals.plus returned a bot challenge,
   smzdm wiki returned an empty page. **No PCB photo was visually inspected in this research;
   the OSHWHub switch part number came from EDA metadata, not from a photograph.**
8. **Any 客制化 (custom group-buy) single-switch design** — NOT FOUND / UNVERIFIED.
   I did not exhaustively search Chinese group-buy platforms for this specific topology.

---

## SOURCE URLs (raw)

- https://oshwhub.com/c3h4o/ch582msan-mu-61jian-pan
- https://image.lceda.cn/attachments/2023/8/D1C3xx3Lb1qwvDJKQnESvo96oMg5zRBmYhJtdzez.zip
- https://atta.szlcsc.com/upload/public/pdf/source/20211019/449AD4EDF23AADA7A5C4E3C063EDBB30.pdf (MST22D18G2 datasheet link from project.json — **not opened**)
- https://blog.csdn.net/a1036884790/article/details/116975755 (RK G68 三模说明书)
- https://www.inwaishe.com/archiver/tid-30872.html (御斧 Y68)
- https://www.inwaishe.com/archiver/index.php?action=tid&value=33825 (WOB RAINY75)
- http://www.inwaishe.com/archiver/index.php?action=tid&value=34530 (Darmoshark Top75)
- http://www.inwaishe.com/archiver/index.php?action=tid&value=31526 (雷神 VIC84)
- https://www.163.com/dy/article/HKKURV870530P1BL.html (雷神 VIC84 mirror)
- http://www.inwaishe.com/archiver/index.php?action=tid&value=33584 (雷神 Zero75)
- https://www.weistang.com/portal.php?mod=view&aid=25642&page=3 (七彩虹 KB8PRO details)
- https://www.weistang.com/portal.php?mod=view&aid=25642&page=4 (七彩虹 KB8PRO teardown)
- https://page.sm.cn/blm/node-page-new-995/index?id=28_0f9bff34109b4171ad5e4e3f055fd5b4 (迈从 K980)
- https://max.book118.com/html/2025/0923/5200021034012333.shtm (雷神 ZERO75 磁轴手册, WORK/GAME)
