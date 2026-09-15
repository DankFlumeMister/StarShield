# PMOS high-side load switch for ZMK `ext-power` RGB rail — verified facts

Primary sources used (all fetched and text-extracted locally; the raw PDFs and extracted text are **not published with this repository** — the URLs below are the citable artifacts):

| # | Source | URL |
|---|---|---|
| S1 | AOS **AO3401A** datasheet, Rev 3.1 Dec 2023 (5 pp) | https://aosmd.com/res/data_sheets/AO3401A.pdf |
| S2 | Diodes Inc **DMG2301L** datasheet, DS37540 Rev 4-2, June 2021 (7 pp) | https://www.diodes.com/assets/Datasheets/DMG2301L.pdf |
| S3 | Infineon/IR **IRLML6402** datasheet (10 pp) | https://www.infineon.com/dgdl/irlml6402pbf.pdf |
| S4 | Digi-Key AO3401A parametric page | https://www.digikey.com/en/products/detail/alpha-omega-semiconductor-inc/AO3401A/1855773 |
| S5 | Digi-Key DMG2301L-7 parametric page | https://www.digikey.com/en/products/detail/diodes-incorporated/DMG2301L-7/5768820 |
| S6 | Digi-Key IRLML6402TRPBF parametric page | https://www.digikey.com/en/products/detail/infineon-technologies/IRLML6402TRPBF/811437 |
| S7 | ZMK `ext-power` config docs | https://raw.githubusercontent.com/zmkfirmware/zmk/main/docs/docs/config/power.md |
| S8 | ZMK driver `ext_power_generic.c` | https://raw.githubusercontent.com/zmkfirmware/zmk/main/app/src/ext_power_generic.c |
| S9 | ZMK nice!nano **v1** overlay | https://raw.githubusercontent.com/zmkfirmware/zmk/main/app/boards/nicekeyboards/nice_nano/nice_nano_nrf52840_zmk_1_0_0.overlay |
| S10 | ZMK nice!nano **v2** overlay | https://raw.githubusercontent.com/zmkfirmware/zmk/main/app/boards/nicekeyboards/nice_nano/nice_nano_nrf52840_zmk_2_0_0.overlay |
| S11 | ZMK **nRFMicro** board DTS | https://raw.githubusercontent.com/zmkfirmware/zmk/main/app/boards/joric/nrfmicro/nrfmicro_nrf52840_zmk.dts |
| S12 | nRFMicro KiCad schematic (open hardware) | https://github.com/joric/nrfmicro/blob/main/hardware/nrfmicro.kicad_sch |
| S13 | nicekeyboards nice!nano pinout/schematic (manufacturer) | https://nicekeyboards.com/docs/nice-nano/pinout-schematic/ |
| S14 | nice!nano v1 schematic image (1831×1256) | https://nicekeyboards.com/static/724bec729cb82c3fb302249533b98589/111fd/schematic.png |
| S15 | nice!nano v2 schematic image (1949×1215) | https://nicekeyboards.com/static/511ae101870d00c265b84f35d5f39eda/61100/schematic_nice_nano_v2.png |
| S16 | ZMK `ext_power` behaviour docs | https://raw.githubusercontent.com/zmkfirmware/zmk/main/docs/docs/keymaps/behaviors/power.md |

---

## 1. Recommended part: **AO3401A** (Alpha & Omega Semiconductor), SOT-23

Recommended over DMG2301L and IRLML6402: only one of the three with **30 V** Vds (margin on a 4.2 V rail + inductive/ESD transients), **±12 V** Vgs rating (vs ±8 V), best max Rds(on) at Vgs = −2.5 V, highest Id and Id@70 °C, Active lifecycle status, and the datasheet itself markets it as a load switch.

> S1, Product Summary: *"The AO3401A uses advanced trench technology to provide excellent RDS(ON), low gate charge and operation gate voltages as low as 2.5V. This device is suitable for use as a load switch or other general applications."*

### Absolute maximum ratings (S1, p.1; TA = 25 °C unless noted)

| Parameter | Symbol | Value | Note |
|---|---|---|---|
| Drain-Source Voltage | VDS | **−30 V** | |
| Gate-Source Voltage | VGS | **±12 V** | |
| Continuous Drain Current | ID | **−4 A @ TA = 25 °C**; **−3.2 A @ TA = 70 °C** | |
| Pulsed Drain Current | IDM | **−27 A** | datasheet note C: *"Repetitive rating, pulse width limited by junction temperature TJ(MAX)=150 °C"* |
| Power Dissipation | PD | **1.4 W @ TA = 25 °C**; **0.9 W @ TA = 70 °C** | note B: *"PD is based on TJ(MAX)=150 °C, using ≤ 10s junction-to-ambient thermal resistance"* |
| Junction/storage temp | TJ, TSTG | −55 to 150 °C | |

Thermal (S1 p.1): RθJA **t ≤ 10 s: 70 typ / 90 max °C/W**; **steady-state: 100 typ / 125 max °C/W** (note A: 1 in² FR-4, 2 oz Cu, still air, TA = 25 °C). RθJL 63 typ / 80 max °C/W.
Body diode (S1 p.2): IS max continuous **−2 A**; VSD **−0.7 typ / −1 V max @ IS = −1 A, VGS = 0 V**.

### Electrical characteristics (S1, p.2, "Electrical Characteristics (TJ=25 °C unless otherwise noted)")

| Parameter | Symbol | Min | Typ | Max | Unit | Test condition |
|---|---|---|---|---|---|---|
| Gate Threshold Voltage | VGS(th) | **−0.5** | **−0.9** | **−1.3** | V | VDS = VGS, ID = −250 µA |
| Static Drain-Source On-Resistance | RDS(ON) | — | 41 | **50** | mΩ | VGS = −10 V, ID = −4.0 A |
| " (TJ = 125 °C) | RDS(ON) | — | 62 | 75 | mΩ | VGS = −10 V, ID = −4.0 A |
| " | RDS(ON) | — | 47 | **60** | mΩ | **VGS = −4.5 V, ID = −3.5 A** |
| " | RDS(ON) | — | 60 | **85** | mΩ | **VGS = −2.5 V, ID = −2.5 A** |
| On-state drain current | ID(ON) | — | — | −27 | A | VGS = −10 V, VDS = −5 V |
| Drain-Source Breakdown Voltage | BVDSS | −30 | — | — | V | ID = −250 µA, VGS = 0 V |

Dynamic (S1 p.2): Ciss 645 pF, Coss 80 pF, Crss 55 pF @ VGS = 0 V, VDS = −15 V, f = 1 MHz. Qg(4.5 V) = **7 nC**, Qg(10 V) = 14 nC @ VGS = −10 V, VDS = −15 V, ID = −4.0 A.

**Package: SOT23** (S1 p.1 top-view drawing; Ordering/package page). Digi-Key lists supplier device package **SOT-23-3**, package/case *3-SMD, SOT-23-3 Variant*, Part Status **Active** (S4).

> ⚠ **Discrepancy, flagged:** Digi-Key's parametric table (S4) lists *"Rds On (Max) @ Id, Vgs: 44 mOhm @ 4.3A, 10V"* and *"Input Capacitance (Ciss) (Max) @ Vds: 1200 pF @ 15 V"*, whereas the datasheet (S1) says **50 mΩ max @ 4.0 A, 10 V** and **Ciss 645 pF typ**. Use the datasheet values. Digi-Key's *"Id 4A (Ta)"*, *"Vgs(th) (Max) 1.3V @ 250µA"*, *"Vgs (Max) ±12V"*, *"Vdss 30V"*, *"Pd 1.4W (Ta)"*, *"Drive Voltage (Max Rds On, Min Rds On) 2.5V, 10V"* all agree with S1.

### Candidate comparison (all max values, from primary datasheets)

| Part | Vds max | Vgs max | VGS(th) min/typ/max @ test | RDS(ON) max @ −4.5 V | RDS(ON) max @ −2.5 V | Id cont. | Pulsed | Pd / RθJA | Package | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| **AO3401A** (S1) | **−30 V** | **±12 V** | −0.5 / −0.9 / **−1.3 V** @ VDS=VGS, ID=−250 µA | **60 mΩ** @ ID=−3.5 A (47 typ) | **85 mΩ** @ ID=−2.5 A (60 typ) | **−4 A @25 °C**, −3.2 A @70 °C | **−27 A** | 1.4 W @25 °C / RθJA ss 125 max °C/W | SOT23 | Active (S4) |
| DMG2301L (S2) | −20 V | ±8 V | −0.4 / n.s. / **−1.2 V** @ VDS=VGS, ID=−250 µA | **120 mΩ** @ ID=−2.8 A (no typ) | **150 mΩ** @ ID=−2.0 A (no typ) | −3 A @25 °C, **−1 A @70 °C** | −10 A | 1.5 W / RθJA 83 °C/W | SOT23 | Active (S5) |
| IRLML6402 (S3) | −20 V | ±12 V | −0.40 / −0.55 / **−1.2 V** @ VDS=VGS, ID=−250 µA | **65 mΩ** @ ID=−3.7 A (50 typ) | **135 mΩ** @ ID=−3.1 A (80 typ) | −3.7 A @25 °C, −2.2 A @70 °C | −22 A | 1.3 W @25 °C / RθJA 75 typ, 100 max °C/W | Micro3™ (SOT-23) | **Obsolete (S6)** |

S2 additionally: VGSS ±8 V, IDM −10 A, IS (body diode, t<5 s) −0.75 A, PD 1.5 W, RθJA 83 °C/W (1"×1" FR-4, 2 oz Cu, single sided), VSD max −1.2 V @ IS = −0.75 A, Ciss 476 pF / Coss 53 pF / Crss 45 pF @ VDS=−10 V, Qg 5.5 nC @ VGS=−4.5 V.
S3 additionally: IDM −22 A, IS (body diode) −1.3 A, PD 0.8 W @70 °C, linear derating 0.01 W/°C, EAS 11 mJ, VSD max −1.2 V @ IS=−1.0 A, Ciss 633 pF / Coss 145 pF / Crss 110 pF, Qg 8.0 typ / 12 max nC @ VDS=−10 V, VGS=−5.0 V, low profile <1.1 mm.

**Rds(on) penalty, −2.5 V vs −4.5 V (max values):** AO3401A ×1.42 (+42 %, +25 mΩ) · DMG2301L ×1.25 (+25 %, +30 mΩ) · IRLML6402 **×2.08 (+108 %, +70 mΩ)**.

---

## 2. Gate-drive math (source at Vbat, 3.3 V GPIO, load on drain)

Topology: **SOURCE = Vbat (3.0–4.2 V)**, **DRAIN = RGB rail**, **GATE = GPIO**, Rgs between gate and source.

Vgs = Vgate − Vsource:

| Vbat | GPIO HIGH (3.3 V) → Vgs | GPIO LOW (0 V) → Vgs |
|---|---|---|
| 4.2 V (full) | **−0.9 V** | **−4.2 V** |
| 3.7 V (nominal) | **−0.4 V** | **−3.7 V** |
| 3.0 V (nearly empty) | **+0.3 V** | **−3.0 V** |

**Is the FET fully enhanced?** Turning **on**: yes, comfortably — at GPIO LOW, |Vgs| = 3.0–4.2 V, far above |VGS(th)| ≤ 1.3 V, so the channel is well inverted. But it is **not driven at the datasheet's −4.5 V test point**: at Vbat = 4.2 V you get −4.2 V (just short), and at Vbat = 3.0 V you only get −3.0 V, i.e. **between the −4.5 V and −2.5 V spec points**. The datasheet specifies no Rds(on) at −4.2 V or −3.0 V, so the guaranteed max is **bounded by 60 mΩ (the −4.5 V max) and 85 mΩ (the −2.5 V max)** for AO3401A — a 1.0×–1.42× penalty versus the headline −4.5 V number. The part is therefore only *partially* enhanced at end-of-discharge, and it gets worse as the battery drains (Rds(on) rises exactly when you are least able to afford the drop).

**Turning off: this is the real problem.** With the gate pinned at 3.3 V and the source at 4.2 V, |Vgs| = **0.9 V** — which is *above* the AO3401A's **minimum** threshold of 0.5 V (S1). The datasheet bounds VGS(th) only between −0.5 V and −1.3 V, so a worst-case (low-threshold) part sits **0.4 V above threshold** and is *not guaranteed off*; it will conduct subthreshold current into the RGB rail. The situation only becomes safe once Vbat ≤ 3.7 V (|Vgs| = 0.4 V < 0.5 V min threshold). DMG2301L (min −0.4 V) and IRLML6402 (min −0.40 V) are **worse**, not better. *The datasheet does not specify subthreshold leakage versus Vgs, so the magnitude of that leakage is UNVERIFIED — only the fact that off-state is not guaranteed is verified.*
(At Vbat = 3.0 V the gate is 0.3 V *above* the source; that is a mild forward gate bias, still inside the ±12 V rating, but it confirms the "HIGH = off" assumption is only approximately true.)

**Standard circuit, and what is actually verified:**
- ZMK exposes exactly one control node: `compatible = "zmk,ext-power-generic"`, `control-gpios` = *"List of GPIOs which should be active to enable external power"*, plus `init-delay-ms` (S7).
- The driver sets the pin to its **logical ACTIVE** level to enable: `ext_power_generic_enable()` calls `gpio_pin_set_dt(gpio, 1)`; `ext_power_generic_init()` configures the pin `GPIO_OUTPUT_INACTIVE` and then **enables by default** (state is persisted in settings) (S8).
- Therefore the **GPIO drives the control node directly, with no buffer/level shifter**, and the devicetree polarity decides whether that means a logic HIGH or LOW:
  - nice!nano v1: `control-gpios = <&gpio0 13 GPIO_ACTIVE_LOW>;` (S9)
  - nice!nano v2: `control-gpios = <&gpio0 13 GPIO_ACTIVE_HIGH>; init-delay-ms = <50>;` (S10)
  - nRFMicro: `control-gpios = <&gpio1 9 GPIO_ACTIVE_LOW>; init-delay-ms = <50>;` (S11)
- nice keyboards' own documentation confirms direct GPIO gating of the rail: *"P0.13 on VCC shuts off the power to VCC when you set it to high — This saves on battery immensely for LEDs of all kinds that eat power even when off"* (S13).

> **UNVERIFIED / lower confidence — the "gate-to-source pull-up" convention.** I could **not** verify a keyboard design that uses a pull-up from gate to source. What the two ZMK-supported open designs actually do is different:
> - **nRFMicro** (open hardware, KiCad): PMOS **Q2 = AO3407**, **SOURCE = `nRF_VDD`** (the 3.3 V LDO rail, not the raw battery), **DRAIN = `EXT_VCC`**, gate net `POWER_PIN` = nRF52840 **P1.09**, and **R9 = 2 MΩ from gate to GND** (pull-*down*, i.e. default ON). Verified by tracing the `.kicad_sch` wire list: `(wire (xy 135.255 115.57)→(xy 140.335 115.57)→(xy 141.605 115.57))` reaches the gate pin, `(xy 140.335 115.57)→(xy 140.335 120.015)` reaches R9, `(xy 140.335 127.635)→(xy 140.335 129.54)` reaches GND (S12). This matches S11's `&gpio1 9` exactly.
> - **nice!nano v2** (manufacturer schematic): the cut-off is **not a PMOS at all** — `EXT_VCC` is the VOUT of **U3 = XC6220B331MR** (VIN = `VDDH`, the battery/system rail), and `POWER_PIN` drives the LDO's **CE** pin through **R9 = 10 MΩ to VIN** (pull-up to the unswitched rail, default ON) (S15).
> - **nice!nano v1** (manufacturer schematic): the PMOS **Q1 "P Channel"** **does** have its **source on the battery rail `VBAT`** and its **drain into the LDO (U3 = AP2112K-3.3) VIN**, gate driven directly from the `VBUS` node with **R1 = 100 kΩ to GND** and a Schottky **D1** from `VBUS` to the LDO VIN (battery/USB power-path switch) (S14). No level shifter and no NPN stage — but note its gate is driven by **VBUS (5 V)**, so Vgs(off) = +0.8 V (hard off) and Vgs(on) = −Vbat (fully enhanced); **it never faces the 3.3 V-GPIO-vs-4.2 V-battery problem.** The PMOS part number is **not legible** at the published image resolution (UNVERIFIED).
>
> Engineering reasoning (not a cited vendor/design claim): a 100 kΩ gate-to-source resistor is the conventional way to force Vgs = 0 while the MCU pin is high-Z during reset/boot, so the rail defaults OFF. It **cannot** fix the −0.9 V off-state when the GPIO is actively driven to 3.3 V, because it cannot pull the gate above the GPIO's own high level.

---

## 3. Is a level shifter / second NPN-NMOS stage required?

**Not required to turn the FET ON**, **required (or a different topology) to guarantee it OFF.**

- **ON (GPIO LOW):** works directly. Vgs = −3.0 to −4.2 V, |Vgs| ≫ |VGS(th)|max = 1.3 V. No shifter, no NPN. Penalty vs the −4.5 V spec is bounded by the −2.5 V column: AO3401A 60 → **85 mΩ max** worst case (see table above); a level shifter would buy back at most 25 mΩ.
- **OFF (GPIO HIGH):** *not* guaranteed. Vgs = −0.4 V (VBAT 3.7 V) to −0.9 V (VBAT 4.2 V), against a VGS(th) spread of −0.5 to −1.3 V (AO3401A). At VBAT = 4.2 V a minimum-threshold part is 0.4 V above threshold and conducts. A level shifter or a small NMOS/NPN whose drain pulls the gate **to the source rail** would give Vgs = 0 V and a guaranteed off state (it also inverts the logic, so ZMK's `control-gpios` polarity flips to `GPIO_ACTIVE_HIGH`). The alternative used in production — see nice!nano v2 (S15) — is to drop the series PMOS entirely and gate an LDO with an enable pin, which gives a true high-impedance off state.
- **Practical middle ground:** keep the source on the **3.3 V regulated rail** (exactly what nRFMicro does, S12/S13) so the gate can reach the source potential. That removes the entire problem — but then you are no longer switching the raw battery rail.

**Body-diode direction — load goes on the DRAIN.** A P-channel MOSFET's body diode is the p(drain)–n(body/source) junction: **anode = drain, cathode = source**; it conducts only when V_drain > V_source. With **source = Vbat and drain = load**, V_source > V_drain in normal operation, so the diode is **reverse-biased and blocks** — the RGB rail stays unpowered when the FET is off. If you reversed the part (source = load, drain = battery), the diode would be forward-biased and the rail would be permanently powered through it, defeating `ext_power`. Both datasheets spec the diode explicitly as the integral body diode — S1: `IS` *Maximum Body-Diode Continuous Current* = −2 A and `VSD` = −0.7 typ / −1 V max @ IS = −1 A, VGS = 0 V; S3 names it directly: *"IS Continuous Source Current (Body Diode) – MOSFET symbol showing the integral reverse p-n junction diode."* (The anode/cathode orientation itself is standard PMOS construction; the datasheets establish the diode and its ratings, not the orientation in words.)
*Verified in silicon:* nice!nano v1 puts **VBAT on the PMOS source** and the load (LDO VIN) on the **drain**, with the USB path feeding that same drain node through D1 (S14) — the exact arrangement above.

---

## 4. Suitability for ~2 A continuous (AO3401A)

P = I²·R, at I = 2 A:

| Condition | Rds(on) used | P = I²R | ΔT with RθJA(ss) = 125 °C/W max | TJ at TA = 25 °C | TJ at TA = 40 °C |
|---|---|---|---|---|---|
| Vgs = −4.5 V (datasheet spec) | 60 mΩ max | **0.24 W** | **+30 °C** | 55 °C | 70 °C |
| Vgs = −2.5 V (datasheet spec) | 85 mΩ max | **0.34 W** | **+42.5 °C** | 67.5 °C | 82.5 °C |
| Actual Vgs (−3.0 to −4.2 V) | 60–85 mΩ (bounded) | 0.24–0.34 W | +30 to +42.5 °C | 55–67.5 °C | 70–82.5 °C |

Against the ratings: Id = −4 A @ 25 °C and −3.2 A @ 70 °C (S1), so 2 A is inside the current rating at both temperatures; TJ stays well below the 150 °C limit.

**But the SOT-23 caveat matters.** PD = **1.4 W is a ≤10 s figure** at TA = 25 °C (datasheet note B), i.e. it uses the *t ≤ 10 s* RθJA of 90 °C/W max — not the steady-state 125 °C/W max. The honest continuous budget is (150 − TA)/125: **≈1.0 W at 25 °C ambient, ≈0.88 W at 40 °C**. So 0.24–0.34 W uses **24–34 %** of the continuous budget — acceptable, but the die sits **30–43 °C above ambient** and the datasheet's headline −4 A assumes a 1 in² 2 oz-copper board (note A) that a keyboard PCB will not match. Also, the 0.12–0.17 V drop at 2 A is a 3.2–4.6 % rail sag on a 3.7 V rail, which shifts LED colour/brightness.

**Verdict:** AO3401A is **acceptable for ~2 A continuous** on paper (thermal margin exists, current rating is met), with three caveats: (a) Rds(on) is not guaranteed at the actual Vgs — budget 85 mΩ, not 60 mΩ; (b) the FET is **not guaranteed off** at VBAT > 3.7 V with a 3.3 V gate (see §3); (c) for a sustained 2 A RGB load, prefer a lower-Rds(on) / bigger package (DFN, SO-8, SOT-23-6) or parallel two SOT-23s. For the far more typical 0.3–1 A RGB load the AO3401A is comfortable.

---

## 5. Bonus finding worth flagging to the firmware side

ZMK's `ext-power` is **polarity-configurable**, and the polarity differs between the two official nice!nano hardware revisions with the *same* GPIO: v1 uses `GPIO_ACTIVE_LOW` (S9) and v2 uses `GPIO_ACTIVE_HIGH` (S10), because v1's cut-off is a PMOS/switch while v2's is an LDO enable pin. ZMK's driver always enables with `gpio_pin_set_dt(gpio, 1)` and configures the pin `GPIO_OUTPUT_INACTIVE` at init before enabling by default (S8) — so the devicetree flag, not the driver, decides the physical level. Any new board must set `GPIO_ACTIVE_LOW` if the gate is driven directly by the GPIO of a PMOS/LDO-enable that is pulled up, and `GPIO_ACTIVE_HIGH` if a second inverting stage is added.

---

## UNVERIFIED / lower confidence — consolidated

1. **A gate-to-source pull-up resistor as the "standard keyboard circuit", and its typical value — UNVERIFIED.** No open-hardware keyboard design using it was found. Verified pull resistors instead: **2 MΩ gate→GND** (nRFMicro, S12), **10 MΩ CE→VIN** (nice!nano v2, S15), **100 kΩ →GND** on the gate-drive node (nice!nano v1, S14). The 100 kΩ figure matches nice!nano v1's R1, but its function there is a USB-detect node pull-down, not a gate-to-source pull-up.
2. **Magnitude of subthreshold/off-state leakage at |Vgs| = 0.4–0.9 V — UNVERIFIED** (not specified in S1/S2/S3). Only the qualitative conclusion (off not guaranteed at VBAT = 4.2 V, because |Vgs| can exceed |VGS(th)|min) is verified from S1.
3. **PMOS part number on nice!nano v1/v2 — UNVERIFIED** (not legible at published schematic image resolution; only "Q1 / P Channel" on v1 is readable).
4. **nRFMicro's `nRF_VDD` rail voltage** is the output of an AP2112K-3.3 LDO per the schematic net labels (S12); the source of the ext-power PMOS is therefore a **3.3 V** rail, **not** the 3.7–4.2 V battery rail. So nRFMicro is *not* a verified example of the exact "source on the battery rail + 3.3 V GPIO" combination. nice!nano v1 *is* a verified "source on VBAT" PMOS high-side switch, but its gate is driven by VBUS (5 V), not a 3.3 V GPIO.
5. **Digi-Key vs datasheet discrepancy on AO3401A** (44 mΩ @ 4.3 A, 10 V and Ciss 1200 pF vs 50 mΩ @ 4.0 A, 10 V and 645 pF) — unresolved; datasheet values preferred (S1 vs S4).
6. Lower-confidence/aggregator-only corroboration of AO3401A page-2 text (matching S1 exactly, but a transcription rather than the PDF): https://www.rlocman.cn/datasheet/pdf.html?di=173933&p=1
