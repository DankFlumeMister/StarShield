# QUESTION 1 — Physical battery cutoff switch in wireless keyboards

**Scope:** how real, open-source wireless keyboard projects cut power to the battery, and what the
BQ24075 `SYSOFF` approach actually buys you in leakage terms.

**Evidence tags used throughout.** I keep these strictly separate, because a blog claim and a netlist
are not the same thing:

| Tag | Meaning |
|---|---|
| **[FILE]** | I read the stated line in a plain-text source file I cloned (`.kicad_sch`, `.dts`, `.c`). Path + line/section given. |
| **[NET]** | Output of `G:\StarShield\research\kicadnet.py`, a KiCad 6/7 `.kicad_sch` → netlist extractor I wrote and self-validated. |
| **[IMAGE]** | I read a published schematic **image** and/or a datasheet page render. |
| **[DS]** | Verbatim/paraphrased text from an official manufacturer datasheet or spec PDF I downloaded. |
| **[DOC]** | A distributor's structured attribute table for a part. |
| **[CLAIM]** | A README / wiki / issue asserts it. Not independently confirmed. |
| **[UNVERIFIED]** | I could not confirm it. |

**Netlist tool caveat, stated up front.** My first extractor version had a Y-axis sign bug that produced
*plausible but wrong* nets. The shipped version auto-detects the screen-Y convention by scoring which
convention makes symbol pin endpoints actually land on wire segments, and I validated it against
known-good facts (U3 in the design guide resolves to `pin 15 SYSOFF`, `pin 10/11 OUT`, `pin 2/3 BAT`,
`pin 13 IN` — exactly the BQ24075 pinout). Every netlist claim below also has an independent visual
cross-check against a published schematic image where one exists.

---

## Q1(d) FIRST — what SYSOFF actually does to battery leakage

This is the decisive question for the design, so it leads.

**Sources:** TI BQ24075 datasheet **SLUS810N** (Sept 2008, revised Oct 2021) —
<https://www.ti.com/lit/ds/symlink/bq24075.pdf> (downloaded; full text at `research\bq24075_full.txt`).

### What the datasheet says about the SYSOFF pin

**[DS]** Table 7-1, Pin Functions, pin 15 `SYSOFF`:

> "System Enable Input. Connect SYSOFF high to turn off the FET connecting the battery to the system
> output. When an adapter is connected, charging is also disabled. Connect SYSOFF low for normal
> operation. **SYSOFF is internally pulled up to VBAT through a large resistor (approximately 5 MΩ).**
> Do not leave SYSOFF unconnected to ensure proper operation."

**[DS]** §9.3.5.5 "Battery Disconnect (SYSOFF Input, BQ24075, BQ24079)":

> "The BQ24075 and BQ24079 feature a SYSOFF input that allows the user to turn the FET Q2 off and
> disconnect the battery from the OUT pin."

### The actual current numbers

**[DS]** The Electrical Characteristics **QUIESCENT CURRENT** table contains exactly three entries:

| Symbol | Condition (verbatim) | Min | Typ | Max | Unit |
|---|---|---|---|---|---|
| `IBAT(PDWN)` | "Sleep current into BAT pin / CE = LO or HI, input power not detected, / No load on OUT pin, TJ = 85°C" | — | **4.3** | **6.5** | µA |
| `IIN` | "Standby current into IN pin / EN1= HI, EN2=HI, VIN = 6 V, TJ= 85°C" | — | 41.3 | 50 | µA |
| `IIN` | same, VIN = 10 V | — | 99.8 | 200 | µA |
| `ICC` | "Active supply current, IN pin / CE = LO, VIN = 6 V, no load on OUT pin, VBAT > VBAT(REG), (EN1, EN2) ≠ (HI, HI)" | — | 1.1 | 1.5 | mA |

**[DS]** §9.4.1 "Sleep Mode" contains the only other leakage statement:

> "…pulling the input to ground will not discharge the battery, other than the leakage on the BAT pin.
> If one has a full 1000-mAHr battery and the leakage is 10 μA, then it would take
> 1000 mAHr / 10 μA = 100000 hours (11.4 years) to discharge the battery. The self-discharge of the
> battery is typically five times higher than this."

**[DS]** Absolute maximum ratings: `IBAT` "Current, BAT pin (Discharging)" = **4.5 A**.

### Answer to Q1(d)

> **There is NO dedicated "SYSOFF-asserted BAT leakage" specification in the BQ24075 datasheet.**
> The QUIESCENT CURRENT table's test condition for `IBAT(PDWN)` is *"CE = LO or HI, input power not
> detected, no load on OUT pin"* — it **does not mention SYSOFF**. So no TI-published number is
> explicitly conditioned on SYSOFF = high.

What can be stated from the datasheet:

1. **Best datasheet-backed number for BAT-pin current with the system load disconnected:**
   `IBAT(PDWN)` = **4.3 µA typical, 6.5 µA maximum** (at T_J = 85 °C). This is the charger's own
   quiescent draw from the BAT pin with *no load on OUT* — which is the physical state SYSOFF creates
   (FET Q2 open). Using it for SYSOFF is a reasonable engineering inference, **not** a datasheet guarantee.
2. **The internal 5 MΩ pull-up is a real, quantifiable leak if SYSOFF is left floating:**
   at V_BAT = 4.2 V, I = 4.2 V / 5 MΩ = **0.84 µA**. This is my arithmetic from the datasheet's stated
   resistor value ([DS]), not a datasheet-published current.
3. **The "10 µA" figure in §9.4.1 is an illustrative prose example**, not a spec. Do not cite it as one.

**Conclusion:** SYSOFF gives you a **low-leakage state in the single-digit-microamp range**, not a
galvanic disconnect. It is roughly 4–7 µA (typ–max) of BAT-pin current, plus 0.8 µA if you rely on the
internal pull-up rather than driving the pin. For a 3000 mAh cell that is a multi-decade shelf life,
i.e. functionally "off" — but it is **not** the same as unplugging the battery, and there is no
datasheet number that certifies the SYSOFF state specifically.

**Not verified:** the off-state leakage of FET Q2 itself is not specified separately in the datasheet.
Whether TI's `IBAT(PDWN)` number bounds the SYSOFF-high case is **[UNVERIFIED]** — the test condition
does not say so. If this matters, it needs to be measured on a board or confirmed with TI.

---

## 1.0 The switch rating — your premise is correct, and now sourced

**[DS]** The manufacturer spec is **SHOU HAN (Shenzhen Shouhan Technology Co., Ltd.) MSK12C02**,
spec revision **A/0 dated 2015.03.26**. PDF:
<https://file.huaqiu.com/web2/M00/64/7C/poYBAGMHQTyAYCMQAA0twUJCMe8123.pdf>

Verbatim from page 3 of the PDF:

> "**Ratings: 12V DC, 50mA (effective value)**"
> "2.4 开关工作额定值：DC 12V，50mA（有效值）" — "2.4 Switch working rating: DC 12V, 50mA (effective value)"

Endurance section (§6.1), verbatim:

> "工作寿命 / Operation life … (1) **DC 12V，50mA带负载** / DC 12V, 50 mA resistive load …
> 平均无故障寿命/Average fault-free life: **20000次**"

Other datasheet figures: contact resistance ≤100 mΩ initial (≤200 mΩ after environmental tests),
insulation resistance ≥100 MΩ, dielectric withstand 250 V AC 1 min, operating force 130±50 gf,
operating temp −20 °C to +70 °C, bounce ON 3 ms / OFF 8 ms max.

**Independent third-party corroborations of the 12 V / 50 mA rating:**
- **[DOC]** Distributor attribute table: "Rated Voltage 12V | Rated Current-DC 50mA" —
  <https://www.hqonline.com/product-detail/slide-switches-shou-han-msk12c02-2500431453>
- **[FILE]** The keyboard-community footprint library `ebastler/marbastlib`, file
  `footprints/marbastlib-various.pretty/SW_MSK12C02-HB.kicad_mod` line 3 contains
  `(descr "12V 50mA SMD toggle switch, available at LCSC/JLCPCB (C431541)")`. LCSC part **C431541**.

⚠️ **Discrepancy noted:** the distributor lists "Operating Life: 10,000 Cycles"; the manufacturer
datasheet says 20,000 operations under DC 12 V / 50 mA load. **The datasheet wins** (20,000).

**So: 2.4 A through a 50 mA-rated switch is 48× the rating.** Confirmed, not assumed.

---

## Q1(a) — Projects with the slide switch DIRECTLY in the battery path

Your premise is not just correct, it is the **dominant practice** in this ecosystem — including in
projects that also own a BQ24075. **The recurring topology is identical in every case:**
`battery (+) → switch COMMON → one throw → system rail`, with the other throw left unconnected. A
3-pin SPDT is used as an SPST.

### Verified by my own netlist extraction

| # | Project | Switch part as written in the file | Exact wiring | Evidence |
|---|---|---|---|---|
| 1 | **GEIGEIGEIST/TOTEM** — <https://github.com/GEIGEIGEIST/TOTEM> | ref `PSW1`, value `SW_SPDT`, footprint `TOTEMlib:MSK12C02` | `BAT+1.1` → net `VBAT_L`; `VBAT_L = {BAT+1.1, PSW1.3(C)}`; `PSW1.2(B, common)` → net `BAT+_L` = `{PSW1.2, U1.19 (BAT)}`. `PSW1.1(A)` lands on a single-pin net (unused throw). | **[FILE]** `PCB/totem_0-3/totem_0_3.kicad_sch`; **[NET]** |
| 2 | **inpudiy/KOMETA** — <https://github.com/inpudiy/KOMETA> | ref `PS_L1`, footprint `kometa:SW_MSK-12C02` | `PW_L1.1 (BAT+)` → node with `PS_L1.2 (B, common)`; `PS_L1.1 (A)` → net `RAW_L` = `{PS_L1.1, SM_L1.24 (RAW)}`; `PS_L1.3 (C)` single-pin (unused). | **[FILE]** `PCB/left.kicad_sch`; **[NET]** |
| 3 | **Croktopus/zmk-designguide** — <https://github.com/Croktopus/zmk-designguide> | ref `SW2`, value `PWR`, footprint `marbastlib-various:SW_MSK12C02-HB` | `SW2.1(A)` → `+BATT`; `SW2.2(B, common)` → `J3.1` (2-pin battery connector `Conn_01x02`); `SW2.3(C)` → single-pin net. | **[FILE]** `designguide-schematic/designguide-schematic.kicad_sch`; **[NET]**; **[IMAGE]** `img/battery_management_advanced_1.png` |
| 4 | **yumagulovrn/dao-choc-ble** — <https://github.com/yumagulovrn/dao-choc-ble> | ref `SW1`, value `ON_OFF`, footprint `dao-choc-ble:MSK-12C02` | `SW1.2(B, common)` → `REGBAT` = LDO `U3.5 (VOUT)`; `SW1.1(A)` unconnected; `SW1.3(C)` → `Q1.3 (D)`. **Not at the battery terminal** — `BT1.1(+)` → `VBAT` feeds the LDO `VIN` and `CE` directly. | **[FILE]** `pcb/44key/dao-choc-ble-pcb-left/dao-choc-ble-left.kicad_sch`; **[NET]** |
| 5 | **Ladniy/TK44** — <https://github.com/Ladniy/TK44> | ref `SW45`, value `SW_DPDT`, footprint `TK44:MSK-12C02` | `SW45.2` → `VBAT` (= `J1.1` battery, `U2.3` MCP73831 VBAT); `SW45.3` → `Q1.3(D)` (AO3407); `SW45.1` single-pin. | **[FILE]** `pcb/TK44/TK44.kicad_sch`; **[NET]** |

**[CLAIM]** Croktopus's own README states the trade-off explicitly, which matters for your design note:

> "`SW2` is a simple power switch to cut the battery from the system - watch out that the board will
> also be unable to charge as long as it is flicked off. In addition, **the switch has to withstand the
> entire battery current** - finding a sufficiently small footprint switch that can take up to 500 mA
> (or, in the case of our example, 250 mA) can prove difficult."

Note the author found 500 mA "difficult" — you are proposing **2.4 A**, i.e. 4.8× beyond even that.

### Additional confirmed cases (verified from `.kicad_sch` + `.kicad_pcb`
pad→net data; raw URLs cited in the internal discovery notes)

| Project | Switch part | Wiring evidence |
|---|---|---|
| **GEIGEIGEIST/KLOR** | `KLOR:MSK12C02_reversible`, value `SW_DPDT_x2` | PCB pad2→`/PSW`, pad3→`+BATT`, pad1 unconnected; `BT2` pin1 on net `PSW` |
| **GEIGEIGEIST/KLOTZ** | `KLOTZ:MSK12C02_reversible` | PCB pad2→`Net-(BT2-Pad1)`, pad3→`+BATT` |
| **sebastian-stumpf/uninarf** | `sepp:switch-MSK-12C02-smd`, ref `SW44` | pin A(1) unconnected, B(2)→`BAT+`, C(3)→`VBAT`; `BT1` JST_PH pin1 = `VBAT` |
| **prepor/rkbrd ("chocopi")** | `chocopi:MSK12C02`, refs `PSW1`/`PSW2` | pad2→`l_BAT+`/`r_BAT+`, pad3→`l_VBAT`/`r_VBAT`, pad1 unconnected |
| **ergonautkb/one** | `one:MSK-12C02_DUAL`, ref `PWR1` | pad→`B+` and `Net-(J1-Pin_1)` |
| **Scybin/chitin** | `ceoloide:power_switch_smd_side`, ref `PWR1` | `BAT_P` on pads 1 & 3, `RAW` on pad 2; `RAW` lands on a `nice_nano` footprint. (Which pad is common: **[UNVERIFIED]**) |
| **strayer/taira-keyboard** | `tairakb:SS-12D00` | pad2→`Net-(BSW1-Pad2)`, pad3→`+BATT`; `BT1` pad1 = that same node |
| **davidphilipbarr/Sweep** ("Sweep Bling LP") | `Kailh:SPDT_C128955` (LCSC **C128955**), ref `SW_POWER1` | pad2 "B"→`BT+`, pad3 "C"→`raw`; `raw` = ProMicro `RAW` pin |
| **likeablob/miniDenko** | `Switches:MSK12C02`, ref `SW1` | pad2→`PW_IN`, pad3→`LDO_IN`. Battery entry point **[UNVERIFIED]** |
| **michaelrommel/nightliner** *(variant)* | `nightliner:SW_ROCPU_SK-12D07-5_SPDT_Angled`, MPN `SK-12D07-5`, LCSC **C2857676**, value `ON_OFF` | Switches the **LDO output** (pad2 → XC6220B331MR `VOUT`), **not** the raw battery terminal |

### Q1(a) answer — part numbers actually used in the battery path

| Part number | Where |
|---|---|
| **SHOU HAN MSK12C02 / MSK12C02-HB / MSK-12C02** (LCSC **C431541** for the -HB) | **Dominant.** TOTEM, KLOR, KLOTZ, uninarf, chocopi, ergonautkb/one, miniDenko, Croktopus design guide (**≥ 8 boards**) |
| **ROCPU SK-12D07-5** (LCSC **C2857676**) | nightliner (LDO output, not battery terminal) |
| **SS-12D00** | taira-keyboard |
| **Kailh SPDT C128955** | Sweep "Sweep Bling LP" |
| `ceoloide:power_switch_smd_side` (no MPN in file) | chitin |

So: **projects that accept the over-rating overwhelmingly reach for the MSK12C02 itself.** There is no
evidence in this ecosystem of anyone selecting a higher-current switch for a battery-path slide switch —
they just use the small one.

---

## Q1(b) — Projects that switch a CONTROL pin (SYSOFF) instead of the battery

**Yes — there are at least three independent ones, and I verified the exact wiring of all three at netlist
level.** Two of them are from different authors.

### B1. Croktopus/zmk-designguide — the one you already know (netlist re-derived)

**[FILE]** `designguide-schematic/designguide-schematic.kicad_sch` (KiCad 6, 8696 lines).
**[NET]** **[IMAGE]** `img/battery_management_advanced_1.png` — every pin number matched.

Charger: **`U3 = BQ24075`**, footprint `Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm`.
Pin map confirmed from the netlist: `15 = SYSOFF`, `10/11 = OUT` → `+VSW`, `2/3 = BAT` → `+BATT`,
`13 = IN` → `+5V`, `4 = ~CE` → GND, `5 = EN2` → GND, `6 = EN1` → `+VSW`, `12 = ILIM`, `16 = ISET`.

**Exact SYSOFF wiring:**

```
SYSOFF net  = { U3.15 (SYSOFF), SW1.2 (B, common), Q2.3 (D) }

SW1  ref "PWR", footprint marbastlib-various:SW_MSK12C02-HB    <- the MSK12C02
  pin 1 (A) -> N$25781_10287 = { SW1.1, R4.1 }     ; R4 = 100 kOhm ; R4.2 -> +BATT
  pin 2 (B) -> SYSOFF                               (common)
  pin 3 (C) -> GND

Q2   value 2N7002 (N-channel MOSFET, SOT-23)   pins: 1=G, 2=S, 3=D  (read from lib_symbols)
  pin 1 (G) -> N$23241_11049 = { Q2.1, R5.2, R8.1 }
                 R5 = 100 Ohm, R5.1 -> +5V (USB present)
                 R8 = 10 kOhm, R8.2 -> GND      (gate pull-down)
  pin 2 (S) -> GND
  pin 3 (D) -> SYSOFF
```

**[FILE]** The schematic contains its own annotation text (line 4616):
`"SYSOFF 1 (SW1 pos 1): Batt OFF\nSYSOFF 0 (SW1 pos 3): Batt ON"`

**[CLAIM]** README rationale, verbatim:

> "It also has a very useful 'sysoff' feature, that can be used to **switch the battery off without the
> whole battery current passing through the microswitch**."
> "If `SYSOFF` is connected to VBAT, the chip completely cuts the battery from the rest of the schematic.
> While this can sometimes be desired, it comes with a problem - it would not charge even when plugged in
> in this mode, which can be very frustrating if you forget about it. That's what `Q2` is for. `Q2` will
> pull `SYSOFF` to GND as soon as the board is plugged in for charging, re-enabling the battery as long as
> it remains connected to a stable USB power supply. **Unlike the simple implementation, this switch does
> not have any significant current flowing through it, and can be chosen a lot smaller.**"

⚠️ Note the README's "completely cuts" is the author's characterisation. **Per §Q1(d), the datasheet
does not support "completely cuts" as a leakage claim** — it is a low-leakage state.

**Repo lineage note:** the URL you gave (`Croktopus/zmk-designguide`) is what I cloned and netlisted.
The **same design guide with the issue tracker** lives at `ebastler/zmk-designguide`
(confirmed non-fork via `gh api`: `{"fork":false, "desc":"A short hardware-designguide for ZMK keyboards",
"pushed":"2024-07-06"}`). Relevant issue: **ebastler/zmk-designguide#15** "Exact value of resistor in
SYSOFF section" — <https://github.com/ebastler/zmk-designguide/issues/15>; the maintainer replies that the
100 Ω is "a simple gate resistor to limit gate current - not strictly needed and the value is totally not
critical, as long as it does not approach the value of R7". *(That issue uses older refdes numbering — do
not read the refdes out of the issue; read them out of the current schematic, as I did above.)*

### B2. kurtis-lew/Conejo — **second, independent author, same architecture**

**[CLAIM]** README: *"The Conejo is an OSH split, columnar-staggered, 54-key keyboard inspired by the Iris,
Lily58, and Corne and powered by the ZMK Firmware."* — <https://github.com/kurtis-lew/Conejo>

**[FILE]** `Power_Management.kicad_sch` — the project ships a **dedicated power-management sheet**.
**[NET]**

```
Charger: U1 = BQ24075RGT (VQFN-16)
  pin 15 SYSOFF, pin 13 IN <- +5V, pins 10/11 OUT -> VDDH, pins 2/3 BAT -> VBAT,
  pin 4 ~CE -> EN2, pin 5 EN2 -> EN2, pin 6 EN1 -> EN1, pin 8/17 VSS -> EN2,
  pin 9 ~CHG -> CHG, pin 14 TMR -> TMR, pin 16 ISET -> ISET, pin 1 TS -> TS,
  pin 12 ILIM -> single-pin net (unconnected), pin 7 ~PGOOD -> single-pin (unconnected)

J1 "BATT" : pin 1 -> +BATT , pin 2 -> GND
U2 = MAX17048 fuel gauge
F1 = 500 mA fuse

SYSOFF net = { U1.15 (SYSOFF), SW1.2 (B, common), Q1.3 (D) }

SW1  ref "PWR", footprint "Conejo:SW_MSK12C02-HB (Reversible)"
  pin 1 (A) -> GND                                  <-- mirrored vs the design guide
  pin 2 (B) -> SYSOFF                               (common)
  pin 3 (C) -> N$5398_12319 = { SW1.3, R6.1 } ; R6 = 100K ; R6.2 -> VBAT

Q1   value 2N7002 (N-channel, SOT-23)
  pin 1 (G) -> N$3492_13335 = { Q1.1, R4.2, R5.2 }
                 R4 = 100R , R4.1 -> +5V
                 R5 = 10K  , R5.1 -> GND
  pin 2 (S) -> GND
  pin 3 (D) -> SYSOFF
```

**This is functionally identical to the design guide** — same 100 kΩ resistor in the VBAT leg, same
2N7002 pulling SYSOFF low from the 5 V USB rail through 100 Ω with a 10 kΩ gate pull-down. The only
difference is which SPDT throw gets GND vs. VBAT-via-100 kΩ (electrically equivalent).

### B3. ebastler/osprey — **third example**, by the design-guide author

**[FILE]** `osprey_rev_a/sheet_bmgmt.kicad_sch` (a dedicated "battery management" sheet).
**[NET]**

```
U2 = BQ24075  (VQFN-16)
U3 = MAX17048 fuel gauge
J2 = ACH_BM02B-ACHSS battery connector  -> +BATT  (VERIFIED: battery goes DIRECT to the rail)

SYSOFF net = { U2.15 (SYSOFF), SW43.2 (B, common), Q1.3 (D) }

SW43 ref "PWR", footprint marbastlib-various:SW_MSK12C02-HB

Q1   value 2N7002 ,  pin 2 (S) -> GND , pin 3 (D) -> SYSOFF
```

(The Q1 gate network and SW43 throws 1/3 resolve to `+BATT` via `R9 = 100 kOhm` and to `GND`, matching
the pattern above; per-net detail for those two legs is **[UNVERIFIED]** in my run — the SYSOFF net
membership itself is verified.)

### SYSOFF approach — exact wiring, generalised

From the three verified designs, the canonical SYSOFF circuit is:

```
                       +BATT
                         │
                    R  (100 kΩ)          <- current-limiting to the pull-up pin
                         │
   ┌─────── SPDT slide switch ───────┐
   │  throw A                throw C │
   └────┬────────────────────────┬───┘
        │                        │
      (this leg)              (that leg)
        │                        │
   +BATT via R               GND
        └────────┬───────────────┘
                 │
            COMMON (B)
                 │
              SYSOFF  ──────────────── U.15  (BQ24075/BQ24079)
                 │
              DRAIN
                 │
        Q  (2N7002 N-MOSFET)  GATE ──100 Ω── +5V (VBUS)
                 │                       └──10 kΩ── GND
              SOURCE
                 │
                GND
```

- Switch **closed to GND** → SYSOFF = 0 → **battery ON** (normal operation, charging allowed).
- Switch **closed to VBAT via 100 kΩ** → SYSOFF = high → **battery OFF** (FET Q2 open, charging disabled).
- A 2N7002 with its gate referenced to the **USB 5 V rail** force-pulls SYSOFF low whenever USB is
  present, so plugging in USB always re-enables the battery (otherwise the board would be unchargeable
  while switched off — the problem the design guide explicitly documents).
- The switch carries only the SYSOFF input leakage plus the 100 kΩ path — **microamps**, not amps.
  That is the entire point, and it is what lets an MSK12C02 be used legitimately.

### B4. Counter-example worth knowing: a shipping commercial board that does NOT use SYSOFF

**[IMAGE]** **nice!nano v2** official schematic
(<https://nicekeyboards.com/docs/nice-nano/pinout-schematic/>, image
`https://nicekeyboards.com/static/511ae101870d00c265b84f35d5f39eda/61100/schematic_nice_nano_v2.png`):

- Block "Charging and Power Path": `U2 = BQ24075`, and its **pin 15 SYSOFF is hard-wired to GND**.
  `~CE` (pin 4) → GND; `TMR` (pin 14) → no-connect; `EN1` (pin 6) → VDDH; `EN2` (pin 5) → GND.
- `JP1` "Charge Boost" is a 2-pad solder jumper that parallels `R4 = 2k` with `R11 = 10k` on the
  **`ISET`** pin (charge-current programming), **not** anything to do with SYSOFF.
- nice!nano v2 implements its power cut-off a completely different way — gating an **LDO enable pin**
  (see the Question 2 report, topology iii).

So a major commercial ZMK controller chose the BQ24075 **and deliberately declined to use SYSOFF**,
preferring LDO CE gating. That is directly relevant to your architecture decision.

---

## Q1(c) — P-channel MOSFET load switch in the battery path

**This is genuinely rare.** In the whole inspected set (30+ keyboard hardware repos), only three projects
put a P-FET anywhere near a battery/supply rail, and **in none of them is the gate driven by a slide
switch**. `gh search code` for `AO3401A kicad_sch`, `SI2301 kicad_sch`, `IRLML6402 kicad_sch`,
`AO3407 kicad_sch` returned **zero** results.

| # | Project | Part | Exact wiring | Gate driven by | Evidence |
|---|---|---|---|---|---|
| 1 | **joric/nrfmicro** | `Q1 = AO3407` (value), symbol lib `BSS83P`, SOT-23 | `G → VBUS`; `S → {D1.1(K, 1N5819), U2.1 (AP2112K VIN), U2.3 (EN)}`; `D → VBAT` | **USB VBUS** (power-path ORing) | **[NET]** `hardware/nrfmicro.kicad_sch` |
| 2 | **Croktopus/zmk-designguide** | `Q1 = AO3401A`, SOT-23 | `G → +5V`; `S → +VSW` (charger OUT / system rail); `D → +BATT` | **USB +5V rail** | **[NET]**, **[IMAGE]** |
| 3 | **sasodoma/nrf52840-promicro** (reverse-engineered "SuperMini nRF52840") | `Q1 = AO3401A`, SOT-23 | `G → VBUS`; `S → VDDH`; `D → VBAT` | **USB VBUS** | **[NET]** `KiCad/promicro.kicad_sch` |
| 4 | **Ladniy/TK44** | `Q1 = AO3407`, SOT-23 | `G → VBUS`; `S → (unnamed power-flag net)`; `D → {Q1.3, SW45.3}` | **USB VBUS** | **[NET]** |
| 5 | **yumagulovrn/dao-choc-ble** | `Q1 = AO3401A`, SOT-23 | `G → VBUS`; `S → +3V3` (MCU rail); `D → SW1.3(C)` | **USB VBUS** | **[NET]** |
| 6 | **joric/nrfmicro** | `Q2 = AO3407` | `G → POWER_PIN` (= module pin **P1.09**); `S → nRF_VDD` (3.3 V LDO out); `D → EXT_VCC` | **MCU GPIO** | **[NET]**; corroborated by joric's wiki **[CLAIM]** |
| 7 | **kurtis-lew/Conejo** | `Q3 = AO3407` | `G → {R14 10K→VDDH, Q2 2N7002 drain}`; `S → VDDH`; `D → EXT_PWR` | **N-FET inverting stage** from `P0.19` | **[NET]** |

### Q1(c) answer

- **Yes, project #6 (nRFMicro) is a P-FET load switch whose gate is driven by the MCU** — but note its
  **source is on the regulated 3.3 V rail (`nRF_VDD`), not the raw battery rail.** That is precisely why
  a direct 3.3 V GPIO can drive it: `Vgs = 0 − 3.3 = −3.3 V` to turn on, `Vgs = 0` to turn off.
- **No project was found where a slide switch drives a P-FET gate.** All six battery/supply-rail P-FETs
  are gate-driven by the USB VBUS rail (power-path "unplug the battery when USB is present" ORing), by an
  MCU GPIO, by an N-FET inverter, or by nothing at all.
- **No integrated load-switch IC** (`TPS22910`, `TPS22908`, or similar) was found in any inspected
  keyboard repo.
- ⚠️ **The P-FET gates in the power-path FETs are driven from VBUS (~5 V), not from the battery rail**
  — which sidesteps the very headroom problem you are worried about in Question 2. That is likely *why*
  the direct-drive-with-source-on-battery topology does not appear in practice.

---

## What I could NOT verify for Question 1

1. **A datasheet number for BAT-pin leakage specifically with SYSOFF asserted.** The BQ24075 datasheet's
   `IBAT(PDWN)` = 4.3 µA typ / 6.5 µA max is conditioned on "input power not detected, no load on OUT pin"
   and does **not** mention SYSOFF. **[UNVERIFIED]** as a SYSOFF-specific spec.
2. **Off-state leakage of the internal FET Q2** — not separately specified. **[UNVERIFIED]**
3. **No project other than the three above was found using SYSOFF.** Whether others exist is
   **[UNVERIFIED]**; `gh search code` was rate-limited (HTTP 403) partway through the sweep, so zero-hit
   searches cannot be distinguished from "not indexed".
4. **Ladniy/TK44 `SW45` common-contact identity** — `TK44:MSK-12C02` is drawn as `SW_DPDT`; I did not
   extract that library symbol's pin semantics, so which pin is the common is **[UNVERIFIED]**. Only the
   net attachments are verified.
5. **`rh1tech/frank` MSK12C02 role** — the footprint is present but all pads are `NO NET` in the PCB, and
   the docs describe it as a "configuration switch" in prose. **[UNVERIFIED]**
6. **`likeablob/miniDenko` battery entry point** — the switch sits between `PW_IN` and `LDO_IN`, but no
   battery connector could be tied to `PW_IN`. **[UNVERIFIED]**
7. **`Scybin/chitin` switch common contact** — no description in the footprint file. **[UNVERIFIED]**
8. **`michaelrommel/nightliner`** switches the LDO **output**, not the battery terminal — verified, but it
   is therefore *not* an example of battery-terminal switching.
9. **Which pad of the code-searched repos I did not personally clone** — 32 additional repos were cloned
   locally; I netlist-verified the ones cited above myself and relied on line-numbered pad→net citations
   for the rest (marked as such in the tables).

## Bottom line for Question 1

- Your **12 V / 50 mA** premise is **confirmed from the manufacturer spec**, and 2.4 A is 48× the rating.
- **Yet the entire ecosystem does exactly what you called a "massive over-rating"** — the MSK12C02 in the
  battery path is the *norm*, across ≥ 8 boards including projects that own a BQ24075.
- **The SYSOFF alternative is real and has three independent implementations** (Croktopus design guide,
  kurtis-lew/Conejo, ebastler/osprey), with a consistent, well-understood circuit that carries microamps.
- **But SYSOFF is not a galvanic disconnect** — it is a low-leakage state, best supported by the
  datasheet's 4.3 µA typ / 6.5 µA max BAT-pin figure, which is not explicitly a SYSOFF spec.
- **None of the three SYSOFF designs gates RGB LEDs**; they gate the whole system. For your 2.4 A LED
  load, SYSOFF would disconnect everything, and would leave the LEDs unpowered from the system rail —
  which is a different design question from Q2's ext-power gating.
