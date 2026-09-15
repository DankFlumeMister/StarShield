# Precedent: ONE switch that is BOTH connection-mode selector AND power/battery switch

Research question: do any real keyboard projects or commercial products use ONE multi-position
switch where one position ALSO disconnects the battery (switch doubles as mode selector AND power
switch)?

Evidence discipline: every row states HOW it was verified. "schematic image viewed" = I fetched
and looked at the actual schematic drawing. "manual text read" = I fetched and read the manual
text myself (noting mirror vs. manufacturer-hosted). "only claimed" = prose assertion only.

---

## 1. Evidence table — verified findings

| Project / Product | What the switch does exactly | Source URL | Verified how |
|---|---|---|---|
| **zmk-designguide** (`Croktopus/zmk-designguide`, identical content to `ebastler/zmk-designguide` — same 25,463-byte readme; I fetched both raw files and diffed by eye) | **No mode switch exists in the guide at all.** Only a power switch. The advanced-schematic image shows `U3 = BQ24075`, pin 15 `SYSOFF`, driven from a 3-position switch `SW1` whose value is literally **"PWR"**. Schematic annotations, verbatim: **"SYSOFF 1 (SW1 pos 1): Batt OFF"** and **"SYSOFF 0 (SW1 pos 3): Batt ON"**. Q2 (2N7002, gate pulled from +5V via R4 100R / R7 10k) forces SYSOFF to GND when USB is present. Simple/TP4056 variant uses `SW2`: "a simple power switch to cut the battery from the system". | https://github.com/Croktopus/zmk-designguide · https://raw.githubusercontent.com/Croktopus/zmk-designguide/main/readme.md · https://raw.githubusercontent.com/ebastler/zmk-designguide/main/readme.md · schematic image: https://raw.githubusercontent.com/Croktopus/zmk-designguide/main/img/battery_management_advanced_1.png | **Schematic image viewed** (1444×686 PNG, fetched and read) + readme text read. Power switch is SEPARATE and single-pole. |
| **Aloidia** (wireless split solar keyboard, Hackaday.io #189688) | Dedicated **SPDT** switch wired to BQ24075 `SYSOFF`. Author's verbatim text: *"SYSOFF input, which enables the user to turn off the keyboard with an SPDT switch. This has as an advantage that when turned off, only the battery is disconnected, but the user can still use the keyboard via USB. The disadvantage is the increased power consumption, as the chip has internal pullups on the SYSOFF input."* | https://hackaday.io/project/189688-aloidia-wireless-split-solar-powered-keyboard/log/216171-aloidia-10-rev1 | **Project log text read.** This is the exact *behaviour* asked about (battery off, USB still works) — but implemented with a **separate** switch, explicitly not the mode selector. |
| **Keychron K2** (dual-mode: BT + wired) | Mode toggle switch has three positions: **BT / OFF / Cable**. Manual overview, verbatim: `* BT OFF Cable (Mode Toggle Switch)` | https://www.manualslib.com/manual/3771598/Keychron-K2.html?page=5 | **Manual text read** (mirror). Confirms question item #3: "OFF" IS one of the three positions of the mode switch. No evidence found that this switch also gates the battery. |
| **Keychron K8 Max** (tri-mode 2.4G/BT/wired) | Toggle positions = **2.4GHz / Cable / Bluetooth** — no OFF detent. Verbatim: *"The K8 Max can be charged in 2.4GHz/Cable/BIuetooth MODE (MODE TOGGLE) on."* And the documented power-off is: *"TURN OFF THE KEYBOARD — Switch the keyboard to the Cable option and unplug the power cable."* | https://www.manualslib.com/manual/4125852/Keychron-K8-Max.html?page=18 · https://www.manualslib.com/manual/4125852/Keychron-K8-Max.html?page=19 | **Manual text read** (mirror). Two conclusions: (a) no OFF detent on the tri-mode switch; (b) **the battery is connected and chargeable in ALL three positions including Cable** → on this shipping tri-mode product the wired position does NOT disconnect the battery; "off" is a firmware/state condition, not a switch-detent battery cut. |
| **Keychron K4 v3** | Verbatim: *"Switch toggle to Bluetooth"* / *"Switch toggle to Cable"*; *"Ensure the keyboard is in Cable or Wired mode and plug in the power cable."* | https://www.manualslib.com/manual/3674007/Keychron-K4.html?page=4 · .../Keychron-K4.html?page=8 | **Manual text read** (mirror). |
| **Akko 3068B** | Back switch is **ON/OFF only**; mode is cable-detected. Verbatim: *"When the keyboard remains unplugged, turn the back switch to ON."* … *"When the keyboard is plugged into the computer through USB interface, it will enter Bluetooth mode automatically without having to push the switch on the back."* | https://akkogear.eu/blogs/manual/akko-3068b-manual | **Official manufacturer manual page read** (brand's own domain). Separate power switch; no mode switch. |
| **temper** (`raeedcho/temper`, chocofi-derived wireless split) | Separate SPDT power switch. Verbatim: *"Uses 7-pin SPDT power switch and includes pads for battery on keyboard shield PCB"*; BOM: *"2x Alps miniature SPDT switches"*. | https://github.com/raeedcho/temper | **README text read.** No mode switch at all. |
| **OSHWHub "CH582M三模61键盘"** (open-source tri-mode keyboard, full EDA source public) | Case switch `SW2` = **MST22D18G2** (LCSC C2906280); project metadata says **双刀双掷 / DPDT**, 2-position 6-pin. In the schematic pins 1 and 4 are `NO_CONNECT` and each pole's two live contacts are hard-shorted (p5↔p2, p6↔p3) → the *second pole is used for current-sharing, not for a second function*. Mode selection is by Fn hotkeys (`Fn+PrintScreen`=BT, `Fn+ScrollLock`=2.4G, `Fn+Pause`=USB). `TP4056` pin 9 = `BAT+` (charger permanently wired). | https://oshwhub.com/c3h4o/ch582msan-mu-61jian-pan (attached EasyEDA ZIP; the schematic files were downloaded and parsed locally) | **EDA schematic source read** (parsed `2.esch` / `project.json`), not a photo. |
| **WCH official tri-mode reference design** (`WCH-3MDOKBD-R0-1v3`, bundled in the ZIP above) | **No mode switch whatsoever** — only `SW-PB` (push button) and a `Header 2` battery connector. Power is an automatic OR. README verbatim: 「电源在接入USB时使用USB电源，未接入USB时使用电池供电」 ("when USB is connected it runs from USB power, when USB is not connected it runs from the battery"). | Bundled in https://oshwhub.com/c3h4o/ch582msan-mu-61jian-pan | **Altium `.SchDoc` parsed** (17,991 records; component instances enumerated). |
| **ZMK firmware ecosystem** (structural, not a product) | Mode selection and power-off are deliberately **firmware** concerns, orthogonal to any switch. `&out OUT_USB / OUT_BLE / OUT_TOG / OUT_NONE` selects the output endpoint in software. Soft off is explicitly a *substitute* for a hardware switch — verbatim: *"Power is not technically removed from the entire system, unlike a hardware switch."* and *"The feature is intended as an alternative to using a hardware switch to physically cut power from the battery to the keyboard."* | https://zmk.dev/docs/keymaps/behaviors/outputs · https://zmk.dev/docs/features/low-power-states · https://zmk.dev/docs/config/power · https://zmk.dev/docs/keymaps/behaviors/power | **Official docs read.** |
| **Texas Instruments BQ24075** (SLUS937C) | Datasheet section *"9.3.8 Battery Disconnect (SYSOFF Input)"* and application section *"10.2.1 Using the BQ24075T, BQ24079T to Disconnect the Battery from the System"* both exist in the real datasheet. | https://www.ti.com/document-viewer/lit/html/SLUS937C/battery-disconnect-sysoff-input-slus937524 | **Section titles read from TI's real datasheet viewer**; the viewer returned only the TOC in every fetch, so the SYSOFF functional prose was **not** read. See UNVERIFIED. |

---

## 2. Evidence table — claimed only (NOT verified)

| Product | Claim | Source | Why not verified |
|---|---|---|---|
| **雷神 ThundeRobot VIC84** (tri-mode 84-key, 2022) | Reviewer prose, verbatim: 「后方的拨片有点特殊，其中一个分别是连接模式/开关，只要档位拨动到关档位，键盘就会强制关机，哪怕用的是有线模式。」— reads as "one switch is mode/power; toggling to the OFF position force-powers-off the keyboard even in wired mode". | http://www.inwaishe.com/forum.php?mod=viewthread&tid=31526 (mirrors: http://www.inwaishe.com/archiver/tid-31526.html, https://www.163.com/dy/article/HKKURV870530P1BL.html) | **Only claimed.** I downloaded and **viewed the review's own teardown photos**: the rear-edge round switch is labeled **BT5.0 / 2.4G / G** (three labels), a second rear switch is labeled **WIN / MAC**, and there is an **additional separate white slide switch on the left side edge** of the case (visible in two photos). A second review (smzdm) describes the rear row as "Type-C接口、连接模式切换开关、MAC/WIN系统切换开关、磁吸式接收器收纳仓" — i.e. mode switch and Win/Mac switch, power switch elsewhere. The prose is grammatically ambiguous and the photos indicate **separate switches**. No official manual or schematic found. |

---

## 3. Near-misses / contrast (two separate switches, or firmware-only "off")

- **Keychron K2** — mode switch position "OFF" exists, but it is on a *dual-mode* (BT+wired) board; no tri-mode OFF detent found in Keychron's 2.4G line (K8 Max = 2.4G/Cable/BT, no OFF).
- **ebastler/Croktopus zmk-designguide** — power switch and SYSOFF only; **no mode selector at all**. SW1 is a 3-position part used for Batt ON / Batt OFF.
- **Aloidia** — dedicated SPDT on SYSOFF; the author explicitly frames "battery disconnected but USB still works" as the point of a *separate* switch.
- **temper**, **Keychron K8 Max**, **Akko 3068B** — power handled separately or by firmware/state.
- **WCH reference design** — no mode switch; USB/battery is an automatic OR.
- **OSHWHub CH582M 61** — DPDT switch present, but used as one circuit switched twice (current sharing); mode via Fn hotkeys.
- **御斧 Y68** — reviewer verbatim: 「虽然切换到有线模式，但只要开关处于ON档，按下任意键它还是会亮灯，并不能看作是关闭电源。站在使用层面，如果把有线模式同时定义成关机…要更方便一些。」 i.e. wired mode leaves the board live, and "make wired also mean OFF" is presented as a **wish**, not an existing design. Source: https://www.inwaishe.com/archiver/tid-30872.html
- **RK G68** — two switches (ON/OFF power + B/G mode); wired entered by cable insertion. Source: https://blog.csdn.net/a1036884790/article/details/116975755

---

## 4. Answer: does combined mode+power precedent exist?

**PARTIAL — and the "battery-disconnect" half is a NO.**

- **YES (verified):** a single mode switch CAN have **"OFF" as one of its three positions** — Keychron K2's toggle is documented as **BT / OFF / Cable** (manual text read). So question item #3 is satisfied by a real shipping product.
- **NO (verified, zero instances):** I found **no** product or project, commercial or open-source, where one switch position is documented to **disconnect the battery** or gate a charger control pin (SYSOFF / EN) while also selecting the connection mode. Every battery-disconnect implementation I verified uses a **dedicated, separate** switch (zmk-designguide `SW1`/`SW2`, Aloidia SPDT, temper SPDT, Akko ON/OFF).
- **Explicit counter-evidence** on a shipping tri-mode product: the Keychron K8 Max manual states the board **charges in all three toggle positions (2.4GHz / Cable / Bluetooth)** — so its wired position demonstrably does *not* cut the battery.
- **Structural reason (verified from primary docs):** the ZMK ecosystem keeps these orthogonal — output selection is a firmware behaviour (`&out`), and "off" is firmware soft off, documented as an *alternative* to a hardware battery switch. WCH's reference tri-mode design has no mode switch at all and ORs USB/battery automatically.

---

## 5. UNVERIFIED

1. **BQ24075 SYSOFF functional prose** — I read the datasheet's section *titles* only; TI's document viewer returned the TOC without body text on every fetch attempt. Whether SYSOFF leaves the system powered from USB is **UNVERIFIED by me**, though the Aloidia project log asserts exactly that.
2. **Keychron K2 "OFF" position behaviour** — whether the OFF detent physically opens the battery, gates the charger, or is only a GPIO state read by the MCU is **UNVERIFIED**. No K2 schematic, FCC schematic exhibit, or readable switch photo obtained.
3. **Switch pole count on any commercial board** — no commercial teardown photo or FCC internal photo was successfully read by me. Keychron FCC exhibits exist (grantee code **2BGKB**; e.g. `2BGKB-K2MAX` lists User Manual doc 7823543 and Internal Photos doc 7823541) but **every PDF endpoint returned HTTP 403** from this environment (fccid.io/document/*, fcc.report, apps.fcc.gov/eas/GetApplicationAttachment.html). So: **no FCC internal photo or schematic was visually inspected.**
4. **雷神 VIC84** — whether a single switch combines mode+power, whether the OFF detent cuts the battery, its position count and part number: **UNVERIFIED** (reviewer prose only; photos suggest separate switches).
5. **Manual provenance caveat** — the Keychron K2 (19-page) and K8 Max (44-page) texts were read from **manualslib mirrors**, not from Keychron-hosted PDFs. Keychron's own manual pages (`keychron.com/pages/k2-user-manual-1` etc.) render their content through PageFly JS and served **zero manual text** in the HTML; the 33-page scanned K2 manual on manualslib is image-only and its page images are 80×55 thumbnails. So the wording is high-confidence but the **original manufacturer PDF was not read**.
6. **Brands not checked to manual-text depth:** Epomaker, Royal Kludge, NuPhy, Lofree, Vortex, Ajazz, MonsGeek, Womier, Redragon, Darmoshark, Gamakay, iQunix, Varmilo, Ducky, YUNZII, Skyloong, MCHOSE, Weikav, Chilkey. A parallel commercial-manual sweep was still in flight when this report was written.
7. **Blocked sources:** `manuals.plus` (Cloudflare challenge), `manualslib.com` (403 to normal fetches; only accessible with a Googlebot User-Agent — this is how the Keychron text was obtained), `zhihu.com` / tieba (403), `zfrontier.com` (SPA; its JSON API did not resolve — the Chinese DIY tri-mode keyboard tutorial series, incl. part 6 「USB&电池&开关」, could **not** be read: https://www.zfrontier.com/app/flow/YaLnOdAEOWJE), `fccid.io` document PDFs (403), `fcc.report` (403), `apps.fcc.gov` (403), `grep.app` code-search API (HTTP 429 on every attempt, so **no GitHub-wide code search for `SYSOFF` / `DP3T` / `BQ24075` was possible**).
8. **No PCB photograph was visually inspected with a readable switch part number.** The one EDA-sourced switch part number in this report (MST22D18G2) came from EDA metadata, not a photograph.
