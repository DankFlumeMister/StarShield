# SPDT Slide Switches for a 3.7 V LiPo Hard-Cutoff — Verified Facts

Scope: physically disconnect a 3000 mAh 1S LiPo (3.0–4.2 V DC, nominal 3.7 V) at **≥ 2 A, ideally 3 A**.
Method: manufacturer datasheets (downloaded and text-extracted), distributor parametric pages, and the official KiCad
library sources of truth (GitLab master repo tree + raw `.kicad_mod` files) cross-checked against `kicad.github.io`.

**Headline result:** two of the three suggested candidates are rated **50–100 mA** and cannot be used. Only the
C&K **1000 series** has a published DC rating (6 A @ 28 V DC) that meets the requirement.

---

## 0. KiCad symbol availability (applies to every switch below)

Official symbol library `Switch` — verified on [kicad.github.io/symbols/Switch](https://kicad.github.io/symbols/Switch):

| Symbol | Description (as published) |
|---|---|
| `Switch:SW_SPDT` | "Switch, single pole double throw"; keys `switch single-pole-double-throw spdt ON-ON` |
| `Switch:SW_SPDT_MSM` | "Switch, single pole double throw, center OFF position" — ON-OFF-ON (use if you want a real OFF) |
| `Switch:SW_SP3T` | three-position SP3T (not needed here) |

These are **generic** symbols, not part-specific, so they apply to all four switches. There is **no** part-specific
SPDT-slide *symbol* in the official library.

---

## 1. C&K 1101M2S3CQE2 — **the only candidate that meets the spec**

| Item | Value | Source |
|---|---|---|
| Exact P/N / Mfr | **1101M2S3CQE2**, C&K (C&K Components, now a Littelfuse brand) | [C&K 1000 Series datasheet, rev. CM.05/30/25](https://www.ckswitches.com/media/1429/1000.pdf) |
| Family | 1000 Series Miniature Slide Switches | same |
| Part-number decode | `1101` = SP On-None-On (SPDT); `M2` = PC mount without tabs; `S3` = actuator 0.200 in high; `C` = PC thru-hole termination; `Q` = silver contacts; `E` = epoxy seal; `2` = black actuator | same (ordering table p.2) |
| Body L×W×H | **12.70 × 6.60 × 6.35 mm** | same — drawing captioned *"Part number shown: 1101M2S3CQE2"* |
| Actuator protrusion | **5.08 mm** (S3 = .200" high) → ≈ **11.43 mm total above PCB** — matches distributor "H11,4 mm" | same; [Rutronik24](https://www.rutronik24.de/produkt/ck/1101m2s3cqe2/4261660.html) |
| Pin pitch / terminal | terminal spacing **4.70 mm** (dim. ".185 TYP."); terminals 1.27 mm wide × 0.76 mm thick; 3 terminals numbered 1/2/3 | datasheet drawing; Rutronik24 "Pinabstand 4.7 mm" |
| Travel | 2.41 mm | datasheet drawing |
| **Current rating (DC)** | **6 A @ 28 V DC** — Q (silver) contact material | datasheet p.1: *"Q contact material: 6 amps @ 125 V AC or 28 V DC, 3 amps @ 250 V AC."* |
| AC rating | 6 A @ 125 V AC; 3 A @ 250 V AC (UL) | same |
| Contact resistance | **< 10 mΩ typ. initial @ 2–4 V DC, 100 mA** | same |
| Insulation / dielectric | 10⁹ Ω min; 1,000 Vrms min @ sea level | same |
| Life | **40,000 make-and-break cycles at full load** (G/Q/S contact material); 100,000 for B/P | same |
| Operating temp | −30 °C to 65 °C | same |
| Mounting / actuation | **Through-hole** (PC thru-hole, straight), **top-actuated** (vertical slider) | same; [Rutronik24](https://www.rutronik24.de/produkt/ck/1101m2s3cqe2/4261660.html) "THT / PCB / Straight" |
| Pin count / configuration | **3-pin SPDT**, On-None-On (no centre OFF) | same |
| Materials | case diallyl phthalate (DAP) UL 94 V-0; nylon actuator; coin-silver Q contacts silver plated; epoxy terminal seal; UL file E42363 | same |
| Availability | Rutronik24 €3.41 @ qty 1, mfr lead time 19 weeks, origin Vietnam; also Farnell/element14 ("6A 125VAC"), Newark, TME ("3A/250VAC; 6A/28VDC") | [Rutronik24](https://www.rutronik24.de/produkt/ck/1101m2s3cqe2/4261660.html); [TME](https://www.tme.com/in/en/details/1101m2s3cqe2/slide-switches/c-k/); [Farnell URL slug](https://be.farnell.com/en-BE/c-k-components/1101m2s3cqe2/switch-spdt-6a-125vac/dp/1437697) |
| KiCad symbol | `Switch:SW_SPDT` ✔ | [kicad.github.io/symbols/Switch](https://kicad.github.io/symbols/Switch) |
| **KiCad footprint** | **NONE — no official footprint exists for the C&K 1000 series.** Verified by complete enumeration of `Button_Switch_SMD.pretty` (173 files) and `Button_Switch_THT.pretty` (113 files) on master. | [SMD tree](https://gitlab.com/api/v4/projects/kicad%2Flibraries%2Fkicad-footprints/repository/tree?path=Button_Switch_SMD.pretty&per_page=100&page=1) / [THT tree](https://gitlab.com/api/v4/projects/kicad%2Flibraries%2Fkicad-footprints/repository/tree?path=Button_Switch_THT.pretty&per_page=100&page=1) |

**Closest official footprints and what would have to change** — the nearest official SPDT slide footprints are
`Button_Switch_THT:SW_Slide_SPDT_Straight_CK_OS102011MS2Q` (vertical THT: 3 pads on **2.00 mm** pitch, 0.8 mm drills,
1.5 mm mounting holes, 8.60 × 4.30 mm body) and `Button_Switch_THT:SW_Slide_SPDT_Angled_CK_OS102011MA1Q`. Neither is
usable as-is: the 1000 series needs **4.70 mm** terminal spacing, 1.27 × 0.76 mm terminals, a 12.70 × 6.60 mm body and
no 1.5 mm mounting holes. **A custom footprint must be drawn from the datasheet dimensions above.**

Sibling option: the same datasheet ordering table offers `1103` = **SP On-Off-On**, i.e. `1103M2S3CQE2` gives a true
centre-OFF with identical ratings, body and terminals ([datasheet](https://www.ckswitches.com/media/1429/1000.pdf)).
Stock for that exact ordering code was **not** verified.

---

## 2. C&K OS102011MS2QN1 — fails the current requirement

| Item | Value | Source |
|---|---|---|
| Exact P/N / Mfr | **OS102011MS2QN1**, C&K | [C&K OS Series datasheet, rev. CM.06/16/25](https://www.ckswitches.com/media/1428/os.pdf) |
| **Current rating (DC)** | **0.1 A @ 12 V DC** | datasheet: *"Notes: Contact Rating: 0.1A @ 12 VDC"* on the OS102011MS2QN1 page |
| Contact resistance | **20 mΩ or less** | datasheet p.1 |
| Insulation / dielectric | 100 MΩ min @ 500 VDC; 500 VAC for 1 minute | same |
| Life | **10,000 cycles** (mechanical & electrical) | same |
| Operating temp | −40 °C to 85 °C | same |
| Body / pin geometry | body **8.60 × 4.30 mm**; frame height **4.70 mm**; tail length **2.80 mm**; travel **2.00 mm**; **3 × Ø0.80 mm** terminal holes on **2.00 mm** pitch; **2 × Ø1.50 mm** mounting holes spanning 8.20 mm | datasheet dimension drawing for OS102011MS2QN1 |
| Mounting / actuation | **Through-hole**, vertical (PC thru-hole), **top-actuated**; non-shorting (break-before-make) | datasheet part list: *"SPDT, 2mm travel, Vertical, PC Thru-hole, Frame H=4.7mm, Tail L=2.8mm, Non shorting"* |
| Pin count / configuration | **3-terminal SPDT**; connected terminals 1-2 (pos.1) / 2-3 (pos.2) | datasheet switch-function table |
| Availability | Digi-Key CKN9565-ND, active, 14 weeks lead time; −30…70 °C and 10,000 cycles also confirmed there | [Digi-Key](https://www.digikey.com/en/products/detail/c-k/OS102011MS2QN1/411602) |
| KiCad symbol | `Switch:SW_SPDT` ✔ | [kicad.github.io/symbols/Switch](https://kicad.github.io/symbols/Switch) |
| **KiCad footprint** | **EXISTS**: `Button_Switch_THT:SW_Slide_SPDT_Straight_CK_OS102011MS2Q` — descr *"CuK miniature slide switch, OS series, SPDT"*, cites `ckswitches.com/media/1428/os.pdf`, `attr through_hole`. Geometry matches the datasheet exactly (0.8 mm drills, 2.00 mm pitch, 2 × 1.5 mm mounting holes 8.2 mm apart, 8.60 × 4.30 mm body). | [raw .kicad_mod](https://gitlab.com/kicad/libraries/kicad-footprints/-/raw/master/Button_Switch_THT.pretty/SW_Slide_SPDT_Straight_CK_OS102011MS2Q.kicad_mod) |
| Right-angle sibling | `Button_Switch_THT:SW_Slide_SPDT_Angled_CK_OS102011MA1Q` ↔ part `OS102011MA1QN1` | [THT tree](https://gitlab.com/api/v4/projects/kicad%2Flibraries%2Fkicad-footprints/repository/tree?path=Button_Switch_THT.pretty&per_page=100&page=1) |

**Naming warning:** the footprint is named for variant `OS102011MS2Q`, the part is `OS102011MS2QN1`, and
`kicad.github.io/footprints/Button_Switch_THT` lists it under a *different, older* name:
`SW_Slide_1P2T_CK_OS102011MS2Q` (and the right-angle one as `SW_CuK_OS102011MA1QN1_SPDT_Angled`). Check the exact name
inside your own KiCad install. See §6.

---

## 3. SHOU HAN MSK12C02 (a.k.a. MSK-12C02) — fails the current requirement

| Item | Value | Source |
|---|---|---|
| Exact P/N / Mfr | **MSK12C02**, SHENZHEN SHOUHAN TECHNOLOGY CO., LTD (深圳市首韩科技有限公司) | [SHOU HAN "SPECIFICATION MSK12C02", Version A/0, dated 2024.12.14](https://datasheet.lcsc.com/datasheet/pdf/5162155576bfd231c35aa9a893d25c8c.pdf?productCode=C431540) (PDF; retrieved via Node) |
| **Current rating (DC)** | **12 V DC, 50 mA** — datasheet §2.5: *"开关工作额定值：DC 12V，50mA（有效值） / Ratings: 12V DC, 50mA (effective value)"* | same |
| Contact resistance | **≤ 100 mΩ** (measured 5 V/10 mA DC or ≥1 kHz AC) | datasheet §3.1 |
| Insulation / dielectric | ≥ 100 MΩ @ 100 V DC/1 min; 250 V AC (50/60 Hz) 1 min, no breakdown/flashover | datasheet §3.2–3.3 |
| Life | 10,000 operations, no load, 60/min (contact resistance ≤500 mΩ after) | datasheet §6.1 |
| Travel / force | 1.6 ± 0.2 mm full travel; operating force 150 ± 100 gf | datasheet §4.1–4.2 |
| Operating temp | −20 °C to +70 °C (storage −30 °C to +80 °C) | datasheet §1.2–1.3 |
| Dimensions | **L 8 mm × W 2.8 mm × H 1.4 mm**; package string "SMD,8x2.8mm" | [LCSC C431540 parametric API](https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=C431540) (Mounting Type "Surface Mount, Right Angle"; Switch Height 1.4 mm; Length 8 mm; Width 2.8 mm; Termination "SMD(SMT) Tab") |
| Mounting / actuation | **SMD, right-angle (side-actuated)** — LCSC "Surface Mount, Right Angle" (卧贴) | same |
| Pin count / configuration | 3 signal pads (SPDT per LCSC "Key Attributes: SWITCH SLIDE SPDT SMD"). Datasheet §2.4 says *"Contact arrangement: 1 pole, 1 throw"* — see §6 for this conflict. | datasheet §2.4; LCSC |
| Availability | LCSC C431540, 190,780 in stock, MOQ 10, reel 3000 | LCSC API |
| KiCad symbol | `Switch:SW_SPDT` ✔ | [kicad.github.io/symbols/Switch](https://kicad.github.io/symbols/Switch) |
| **KiCad footprint** | **EXISTS**: `Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02` — descr *"SPDT Surface Mount Slide Switch, right-angle"*, tags `MSK-12C02 MSK12C02 MSK12C02-HB`, `attr smd` | [raw .kicad_mod](https://gitlab.com/kicad/libraries/kicad-footprints/-/raw/master/Button_Switch_SMD.pretty/SW_SPDT_Shouhan_MSK12C02.kicad_mod) |

**Official footprint geometry** (for reference, from the `.kicad_mod`): body on F.Fab **6.70 × 2.80 mm**; courtyard
**8.90 × 5.95 mm**; 3 roundrect signal pads 0.6 × 1.3 mm at (x, y) = pad1 (−2.25, −1.95), pad2 (+0.75, −1.95),
pad3 (+2.25, −1.95) → **pitch p1–p2 = 3.00 mm, p2–p3 = 1.50 mm**; 4 × "SH" shield pads 1.05 × 0.7 mm at x = ±3.675,
y = ±1.1; **2 × NPTH Ø0.85 mm** at (±1.5, 0); slider/actuator region marked on the **+Y** side (Fab lines x 0.15→1.45,
y 1.4→2.85). Added to master 2025-08-03 (commit `cfc022c1`, MR 3732) —
[commit history](https://gitlab.com/api/v4/projects/kicad%2Flibraries%2Fkicad-footprints/repository/commits?path=Button_Switch_SMD.pretty%2FSW_SPDT_Shouhan_MSK12C02.kicad_mod&per_page=5).

---

## 4. SS12D00G / SS12D00G3 — meets the number on paper, but weakly sourced

| Item | Value | Source |
|---|---|---|
| Exact P/N / Mfr | "SS12D00G3" — **no single manufacturer**; a generic Chinese part number. A C&K-branded `SS-12D00-G 6 E` is listed by Digi-Key but as **Obsolete** with no published rating. | [Digi-Key SS-12D00-G 6 E](https://www.digikey.com/en/products/detail/c-k/SS-12D00-G-6-E/13281696) |
| **Current rating** | vendor claim: **3 A 250 VAC or 28 VDC; 5 A 125 VAC** | [Dongguan Fvwin "SS12D00G3" product page](https://www.led-tact-switch.com/showroom/ss12d00g3-toggle-switch-2-position-spdt-1p2t-3-pin-pcb-panel-mini-vertical-slide-switch.html) |
| Contact resistance | 10 mΩ max | same |
| Insulation / dielectric | 1,000 MΩ min; AC 1,500 V for 1 min | same |
| Life | 10,000 cycles | same |
| Body dimensions | **UNVERIFIED** — no drawing obtained from any source | — |
| Mounting / actuation | through-hole, vertical PCB mount (vendor states 3-pin vertical) | same |
| Pin count / configuration | **1P2T (SPDT), 3 pin**; functions offered ON-ON, (ON)-ON, ON-OFF-ON etc. | same |
| KiCad symbol | `Switch:SW_SPDT` ✔ (or `SW_SPDT_MSM` for ON-OFF-ON) | [kicad.github.io/symbols/Switch](https://kicad.github.io/symbols/Switch) |
| **KiCad footprint** | **NONE.** No `SS12D00`/`SS-12D00` footprint exists anywhere in `Button_Switch_SMD` (173 files) or `Button_Switch_THT` (113 files). Closest official SPDT slide footprints are the C&K OS-series pair in §2 — geometry does not match (2.00 mm pitch, 0.8 mm drills, mounting holes), so a **custom footprint is required**, and the vendor drawing must be obtained first because dimensions are unverified. | [SMD tree](https://gitlab.com/api/v4/projects/kicad%2Flibraries%2Fkicad-footprints/repository/tree?path=Button_Switch_SMD.pretty&per_page=100&page=1) / [THT tree](https://gitlab.com/api/v4/projects/kicad%2Flibraries%2Fkicad-footprints/repository/tree?path=Button_Switch_THT.pretty&per_page=100&page=1) |

---

## 5. Summary table

| Part (Mfr) | Rating (DC) | Mount / actuation | Pins | Body L×W×H (mm) | ≥2 A? | Official KiCad symbol | Official KiCad footprint |
|---|---|---|---|---|---|---|---|
| **C&K 1101M2S3CQE2** | **6 A @ 28 V DC** (6 A @ 125 VAC / 3 A @ 250 VAC) | THT, top-actuated | 3, SPDT On-None-On | 12.70 × 6.60 × 6.35; actuator +5.08 (≈11.43 total) | **YES (3× margin at 2 A, 2× at 3 A)** | `Switch:SW_SPDT` ✔ | ✗ none — custom needed |
| **C&K OS102011MS2QN1** | **0.1 A @ 12 V DC** | THT, top-actuated | 3, SPDT BBM | body 8.60 × 4.30; frame H 4.70 | **NO — 20–30× undersized** | `Switch:SW_SPDT` ✔ | ✔ `Button_Switch_THT:SW_Slide_SPDT_Straight_CK_OS102011MS2Q` (name caveat) |
| **SHOU HAN MSK12C02** | **50 mA @ 12 V DC** | SMD, right-angle (side) | 3 pads (SPDT per LCSC) | 8 × 2.8 × 1.4 (LCSC) | **NO — 40–60× undersized** | `Switch:SW_SPDT` ✔ | ✔ `Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02` |
| SS12D00G3 (generic) | 3 A 250 VAC or 28 VDC *(vendor, unverified)* | THT, top-actuated | 3, 1P2T | UNVERIFIED | Marginal (zero margin at 3 A) | `Switch:SW_SPDT` ✔ | ✗ none — custom needed |
| C&K 1103M2S3CQE2 | 6 A @ 28 V DC (same family) | THT, top-actuated | 3, SPDT **On-Off-On** | same as 1101 | YES | `Switch:SW_SPDT_MSM` ✔ | ✗ none — custom needed |
| *(reference, rejected)* C&K CAS-120A | 0.1 A @ 6 V DC | SMD, curved leads | 3, SPDT On-On | — | NO | `Switch:SW_SPDT` ✔ | ✔ `Button_Switch_SMD:Nidec_Copal_CAS-120A` |
| *(reference, rejected)* E-Switch EG1218 | 0.2 A @ 30 V DC | THT | 3, SPDT On-On | — | NO | `Switch:SW_SPDT` ✔ | ✗ (EG1271/EG1224 footprints exist) |

CAS-120A and EG1218 ratings: [TME CAS-120A](https://www.tme.eu/ae/en/details/cas-120a/slide-switches/nidec-copal-electronics/), [TME EG1218](https://www.tme.com/do/en/details/eg1218/slide-switches/e-switch/); CAS-120A also [RS](https://int.rsdelivers.com/product/nidec-components/cas-120a/copal-electronics-surface-mount-dip-switch-spdt-ma/1796964) ("100 (Non-Switching) mA, 100 (Switching) mA"). Neither is suitable.

---

## 6. Battery-cutoff verdict and the DC-vs-AC caveat

**Voltage side is a non-issue.** A 1S LiPo presents at most 4.2 V DC. Every candidate's voltage rating (6 V–28 V DC)
exceeds that. **Current is the binding constraint.**

- **C&K 1101M2S3CQE2 — ADEQUATE.** Published **6 A @ 28 V DC** gives 2× margin at 3 A and ~3× at 2 A, at 4.2 V max.
  Contact resistance < 10 mΩ typ. means ≈ 0.09 W dissipated in the switch at 3 A, and 40,000 full-load cycles.
- **C&K OS102011MS2QN1 — NOT ADEQUATE.** 0.1 A @ 12 V DC is 20–30× below 2–3 A.
- **SHOU HAN MSK12C02 — NOT ADEQUATE.** 50 mA @ 12 V DC is 40–60× below 2–3 A. Its ≤100 mΩ contact resistance
  would dissipate up to ≈0.9 W at 3 A inside an 8 × 2.8 × 1.4 mm SMD package — a failure, not a derating.
- **SS12D00G3 — MARGINAL and poorly evidenced.** The 3 A @ 28 V DC figure leaves zero margin and comes from one
  small vendor's marketing page with no obtainable mechanical drawing.

**Caveat about switching DC vs AC.** A switch's AC rating must never be used to infer its DC capability. On AC the
current passes through zero 100–120 times per second (50/60 Hz), giving the arc an opportunity to extinguish at every
zero crossing; a DC arc has no such current zero and must be broken by opening the gap fast and far enough. The
practical rule stated by the switch manufacturer: *"Do not use it for load switching unless the manufacturer publishes
a DC rating at your voltage and current. The absence of a rating means the part has not been verified for that duty."*
Source: [Swiclick, "Why DC Switch Ratings Are Lower Than AC Ratings"](https://www.swiclick.com/dc-vs-ac-switch-ratings/)
— a switch manufacturer's application-engineering article, authored by their Application Engineer (see confidence note
in §7). The same article notes slide switches are especially affected because contact transfer speed depends on how
fast the hand moves.

The primary datasheets bear this out directly: the C&K 1000 series is rated **6 A @ 125 V AC but only 6 A @ 28 V DC**
(same current, far lower voltage class), and the C&K OS series is **0.1 A @ 12 V DC** despite a 500 VAC dielectric
withstand. At 3.7–4.2 V DC the arc energy is very low, so a part carrying an explicit 28 V DC / ≥3 A rating has ample
margin — but the rating must be the **published DC** one.

**Design consequences:** the recommended C&K 1000 series is through-hole, 12.70 × 6.60 × 11.43 mm, costs ~€3.41 at
qty 1 with a 19-week factory lead time, and has **no official KiCad footprint**, so a footprint must be drawn from the
datasheet drawing (3 terminals at 4.70 mm spacing, terminals 1.27 × 0.76 mm). If board area is tight, the honest
alternatives are (a) accept the SS12D00G3-class part with unverified ratings, or (b) keep a 50 mA-class part such as
the MSK12C02 purely as a *signal* to a load-switch/MOSFET and let the MOSFET break the battery current — the
KiCad footprint for that option already exists.

---

## 7. UNVERIFIED / lower confidence

1. **SHOU HAN MSK12C02 pin configuration conflicts.** The manufacturer spec says *"Contact arrangement: 1 pole, 1 throw"*
   (§2.4), while LCSC classifies it as `Circuit: SPDT` and the official KiCad footprint provides 3 signal pads. The
   datasheet appears to be a reused template — §1.1 also states *"This specification is applied to the requirements for
   TACTILE SWITCH (MECHANICAL CONTACT)"*, which is clearly wrong for a slide switch. Treat the SPDT classification as
   **lower confidence**; the 50 mA / 12 V DC rating is unaffected.
2. **MSK12C02 length discrepancy.** LCSC gives Length = 8 mm; the official KiCad footprint's F.Fab body is 6.70 mm
   (courtyard 8.90 mm). Unresolved — the actuator/terminal extent may account for it, but the manufacturer drawing page
   was not text-extractable. Width (2.8 mm) and height (1.4 mm) agree.
3. **A second, *different* MSK-12C02 spec exists.** A third-party vendor (Switech) publishes an `MSK-12C02SW-NB-JC` sheet
   rated **DC 12 V, 0.1 A** with 70 mΩ max contact resistance and 10,000 cycles —
   [switech1978.com](https://www.switech1978.com/lb/msk-csw-nb-jc-pins-smd-slide-switch-with-positioning-pins-used-to-control-the-switching-of-electrical-functions-1054.html).
   That is a **different vendor's variant** of the same generic family and is **lower confidence** for the SHOU HAN part;
   both figures (50 mA and 100 mA) fail the requirement anyway. Do not treat "MSK-12C02" as one specification.
4. **All SS12D00G3 data is lower confidence.** Single small-vendor page, no manufacturer datasheet, no mechanical
   drawing, no dimensions; the part number is generic and ratings vary between sellers. The C&K-branded
   `SS-12D00-G 6 E` is **Obsolete** at Digi-Key with no published rating.
5. **C&K OS102011MS2QN1 vs the KiCad footprint variant.** The footprint encodes variant `OS102011MS2Q`; the part is
   `OS102011MS2QN1`. Dimensions were cross-checked successfully between the datasheet drawing (OS102011MS2QN1: 3 ×
   Ø0.80 mm at 2.00 mm pitch, 2 × Ø1.50 mm mounting holes, body 8.60 × 4.30 mm, frame H 4.70 mm, tail 2.80 mm) and the
   `.kicad_mod`, but C&K has not been seen to state that the `N1` suffix is dimensionally identical. **Medium confidence.**
6. **kiCad.github.io docs pages lag the GitLab master repo, and footprint names differ.** The docs pages
   (footer *"Last updated on 02 September 2025"*) use older names — `SW_Slide_1P2T_CK_OS102011MS2Q`,
   `SW_CuK_OS102011MA1QN1_SPDT_Angled`, `SW_E-Switch_EG1271_DPDT`, `SW_CuK_JS202011AQN_DPDT_Angled` — while master uses
   `SW_Slide_SPDT_Straight_CK_OS102011MS2Q`, `SW_Slide_SPDT_Angled_CK_OS102011MA1Q`, `SW_E-Switch_EG1271_SPDT`,
   `SW_CK_JS202011AQN_DPDT_Angled`. The docs page also **omits** `SW_SPDT_Shouhan_MSK12C02` (added to master 2025-08-03)
   and several other master-only footprints. Why the docs lag is **not verified** (no release branch was found via the
   GitLab branches API — all branches returned were feature branches). **Always confirm the exact footprint name inside
   your own KiCad installation.**
7. **One docs-page spelling could not be independently confirmed:** `kicad.github.io/footprints/Button_Switch_SMD`
   renders `SW_SPDT_CK-JS102011SAQN` (hyphen) where the repo filename is `SW_SPDT_CK_JS102011SAQN.kicad_mod`
   (underscore). The repo filename is authoritative.
8. **C&K HTML product pages are unreachable.** `ckswitches.com` product pages and `littelfuse.com` both return
   403/Access-Denied (Akamai). All C&K data above therefore comes from the **PDF datasheets** (downloaded via the
   Littelfuse asset CDN redirect) and from distributor parametric pages — not from C&K's HTML pages.
9. **`1103M2S3CQE2` (On-Off-On version) availability is UNVERIFIED** — verified only as an ordering option in the
   datasheet ordering table, not as stocked inventory.
10. **Contact resistance of OS102011MS2QN1** is published in the datasheet (20 mΩ or less) but was **not** listed on
    Digi-Key; the datasheet is the source of record.
11. The AC-vs-DC explanation in §6 is from a switch manufacturer's engineering article (Swiclick), not a tier-1
    manufacturer or a standards body. The physics is standard and is corroborated by the primary datasheet rating pairs,
    but the citation itself is **medium confidence**.

## 8. Method / environment notes

- PDF datasheets were retrieved with Node.js `fetch` (browser User-Agent) and text-extracted with `pdf-parse`;
  PDFs cannot be read by ordinary web-page fetching. `ckswitches.com/media/*.pdf` now 302-redirects to Littelfuse's asset CDN, which serves
  the PDFs successfully when redirects are followed programmatically.
- LCSC product parameters were obtained from its JSON endpoint
  `https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=<code>` (the HTML product page is unreliable).
- Digi-Key blocks ordinary page fetching (Cloudflare) but its parametric tables were read through the microlink extraction proxy
  before that proxy hit its daily rate limit.
- Official KiCad library state was established from the GitLab master repo (tree API + raw `.kicad_mod` files), which is
  authoritative and was treated as such wherever it disagreed with the `kicad.github.io` HTML docs.
