# QUESTION 2 — RGB LED power gating (ZMK `ext-power`) in real keyboards

**Scope:** which MOSFET/topology real ZMK keyboards use to gate the LED rail, what devicetree polarity
each requires and why, and what the ecosystem documents about the P-FET body-diode pitfall.

**Evidence tags** (same convention as the Question 1 report):

| Tag | Meaning |
|---|---|
| **[FILE]** | Read the stated line in a plain-text source file I cloned. Path/section given. |
| **[NET]** | Output of my KiCad `.kicad_sch` → netlist extractor `research\kicadnet.py`. |
| **[IMAGE]** | Read a published schematic **image** or a datasheet page render. |
| **[DS]** | Official manufacturer datasheet text I downloaded. |
| **[CLAIM]** | A README / wiki / issue asserts it. Not independently confirmed. |
| **[INFERENCE]** | My own circuit reasoning layered on verified facts. Explicitly not a file reading. |
| **[UNVERIFIED]** | Could not confirm. |

Pinned ZMK revision for all firmware citations: commit `9ebbeff0a8b69a42f14aec022cdf16c7a107b9e0`.

---

## 2.0 Two corrections to commonly cited facts, established first

**Correction A — the ZMK driver path.** `app/drivers/` **does not exist** in current ZMK `main`. The driver
is **`app/src/ext_power_generic.c`**. Anyone grepping `app/drivers/ext_power/` finds nothing.
<https://raw.githubusercontent.com/zmkfirmware/zmk/main/app/src/ext_power_generic.c>

**Correction B — nice!nano v2's 10 MΩ resistor is a PULL-UP, not a pull-down.** (I initially mis-stated
this in an interim note; corrected here from a high-zoom read of the official schematic.) See §2.3.

---

## 2(a) Real ZMK boards: part numbers and actual devicetree polarity

### The authoritative polarity semantics — read from ZMK's own source

**[FILE]** `app/src/ext_power_generic.c`:

```c
static int ext_power_generic_enable(const struct device *dev) {
    ...
        if (gpio_pin_set_dt(gpio, 1)) {          // line 65
static int ext_power_generic_disable(const struct device *dev) {
    ...
        if (gpio_pin_set_dt(gpio, 0)) {          // line 80
static int ext_power_generic_init(const struct device *dev) {
    ...
        if (gpio_pin_configure_dt(gpio, GPIO_OUTPUT_INACTIVE)) {   // line 155
```

**[FILE]** The GPIOs come from a full `gpio_dt_spec` (line 191: `GPIO_DT_SPEC_GET_BY_IDX`), so the
**devicetree polarity flag is honoured**. `gpio_pin_set_dt(spec, 1)` sets the **logical active** level;
Zephyr inverts the electrical level when the pin was configured `GPIO_ACTIVE_LOW`
(`z_impl_gpio_pin_set()`: `if (data->invert & BIT(pin)) value = (value != 0) ? 0 : 1;`;
`gpio_pin_configure()`: `if ((flags & GPIO_ACTIVE_LOW) != 0) data->invert |= BIT(pin);`).

**[FILE]** ZMK's docs agree in words — `docs/docs/config/power.md`: `control-gpios` = *"List of GPIOs which
should be **active** to enable external power"*.

> **Therefore:**
> **`GPIO_ACTIVE_HIGH` → power ON = pin driven HIGH.**
> **`GPIO_ACTIVE_LOW`  → power ON = pin driven LOW.**

**[FILE]** Two behavioural facts worth designing around:
- `ext_power_generic_init()` configures `GPIO_OUTPUT_INACTIVE` and then *immediately* enables. That window
  is microseconds — **the DT flag does not guarantee a defined rail state during MCU boot.** External
  gate / CE pull resistors are what cover that.
- `ext_power_settings_commit()` does `data->status = true; ext_power_enable(dev);` when no persisted
  setting exists ⇒ **external power is ON by default out of the box.**
- `PM_DEVICE_ACTION_SUSPEND` → disable, `PM_DEVICE_ACTION_RESUME` → enable.
- `control-gpios` is a real **array** (multi-GPIO supported; `DT_INST_FOREACH_PROP_ELEM_SEP`).

### The table — all 16 active `control-gpios` declarations in ZMK `main`

Mechanical sweep over `app/boards/**` (`app/boards/**/*.dts|.dtsi|.overlay`, comments excluded):
**16 active lines in 16 files, plus 1 commented-out.** All confirmed against each directory's
authoritative `<board>.zmk.yml` `type:` field.

Raw URL pattern: `https://raw.githubusercontent.com/zmkfirmware/zmk/main/<path>`

| # | Path | `control-gpios` (verbatim) | type | Hardware topology (where I verified it) |
|---|---|---|---|---|
| 1 | `app/boards/nicekeyboards/nice_nano/nice_nano_nrf52840_zmk_1_0_0.overlay` | `<&gpio0 13 GPIO_ACTIVE_LOW>` | board | **nice!nano v1 — direct P-FET (i).** See §2.2-i **[IMAGE]** |
| 2 | `app/boards/nicekeyboards/nice_nano/nice_nano_nrf52840_zmk_2_0_0.overlay` | `<&gpio0 13 GPIO_ACTIVE_HIGH>` | board | **nice!nano v2 — LDO CE gating (iii).** Same pin, flipped polarity **[IMAGE]** |
| 3 | `app/boards/joric/nrfmicro/nrfmicro_nrf52840_zmk.dts` | `<&gpio1 9 GPIO_ACTIVE_LOW>` | board | **Direct P-FET (i)**, AO3407 **[NET]** |
| 4 | `app/boards/joric/nrfmicro/nrfmicro_nrf52833_zmk.dts` | `<&gpio1 9 GPIO_ACTIVE_LOW>` | board | same family |
| 5 | `app/boards/joric/nrfmicro/nrfmicro_nrf52840_flipped_zmk.dts` | `<&gpio1 9 GPIO_ACTIVE_HIGH>` | board | mirrored-footprint variant — **polarity flipped in firmware only**; I did not obtain its schematic to confirm a hardware difference. **[UNVERIFIED]** |
| 6 | `app/boards/joric/nrfmicro/nrfmicro_nrf52840_zmk_1_3_0.overlay` | `<&gpio1 9 GPIO_ACTIVE_LOW>` | board rev | — |
| 7 | `app/boards/keycapsss/puchi_ble/puchi_ble_nrf52840_zmk.dts` | `<&gpio1 9 GPIO_ACTIVE_LOW>` | board | [UNVERIFIED] schematic |
| 8 | `app/boards/jpconstantineau/bluemicro840/bluemicro840_nrf52840_zmk.dts` | `<&gpio0 12 GPIO_ACTIVE_HIGH>` | board | [UNVERIFIED] schematic |
| 9 | `app/boards/zhiayang/mikoto/mikoto_nrf52840_zmk.dts` | `<&gpio0 13 GPIO_ACTIVE_HIGH>` | board | [UNVERIFIED] schematic |
| 10 | `app/boards/mechwild/pillbug/pillbug_nrf52840_zmk.dts` | `<&gpio1 7 GPIO_ACTIVE_LOW>` | board | [UNVERIFIED] schematic |
| 11 | `app/boards/nicekeyboards/nice60/nice60_nrf52840_zmk.dts` | `<&gpio0 5 GPIO_ACTIVE_LOW>` | board (full keyboard) | [UNVERIFIED] schematic |
| 12 | `app/boards/polarityworks/common/ckp.dtsi` | `<&gpio0 13 GPIO_ACTIVE_HIGH>` | board (BT60/65/75) | [UNVERIFIED] schematic |
| 13 | `app/boards/kinesis/adv360pro/adv360pro.dtsi` | `<&gpio0 13 GPIO_ACTIVE_HIGH>` | board (commercial) | [UNVERIFIED] schematic |
| 14 | `app/boards/moergo/glove80/glove80_lh.dts` | `<&gpio0 31 GPIO_ACTIVE_HIGH>; /* WS2812_CE */` | board (commercial) | the `/* WS2812_CE */` comment suggests **an enable-pin topology (iii)**, but no Glove80 schematic obtained → **[UNVERIFIED]** |
| 15 | `app/boards/moergo/glove80/glove80_rh.dts` | `<&gpio0 19 GPIO_ACTIVE_HIGH>; /* WS2812_CE */` | board | note **different pin per half** |
| 16 | `app/boards/shields/zmk_uno/zmk_uno.dtsi` | `<&arduino_header 1 GPIO_ACTIVE_LOW>` (node `rgb_power`) | **shield** (the only one) | [UNVERIFIED] |
| — | `app/boards/shields/zmk_uno/zmk_uno.dtsi` | `//  control-gpios = <&arduino_header 1 GPIO_ACTIVE_LOW>;` **commented out** | shield | precedes `// Commented out until we add more powerful power domain support` |

Boards that also set **`CONFIG_ZMK_RGB_UNDERGLOW_EXT_POWER=y`** (the RGB◄►ext-power tie-in):
`adv360pro_left/right`, `polarityworks bt60_2_0_0 / bt65 / bt75`, `glove80_lh / glove80_rh` defconfigs.
`CONFIG_ZMK_EXT_POWER` itself is never set explicitly — it defaults to **y**.

### The single most instructive data point in this whole question

**[FILE]** Two files in ZMK's own repo, **same pin `&gpio0 13`, opposite polarity**:

```
nice_nano_nrf52840_zmk_1_0_0.overlay :  control-gpios = <&gpio0 13 GPIO_ACTIVE_LOW>;
nice_nano_nrf52840_zmk_2_0_0.overlay :  control-gpios = <&gpio0 13 GPIO_ACTIVE_HIGH>;
```

**[IMAGE]** And I obtained both official nice!nano schematics from the manufacturer's documentation page
(<https://nicekeyboards.com/docs/nice-nano/pinout-schematic/>), which **confirms the hardware changed
between revisions**:

- **v1 schematic** (`…/724bec729cb82c3fb302249533b98589/111fd/schematic.png`, 1831 px): a P-channel
  MOSFET `Q2` between the 3.3 V LDO rail and the switched output.
- **v2 schematic** (`…/511ae101870d00c265b84f35d5f39eda/61100/schematic_nice_nano_v2.png`, 1949 px):
  a block titled **"VCC Regulator and Cut Off"** containing an LDO whose **enable pin** does the
  switching, and **no series P-FET in the output path**.

**[FILE]** nicekeyboards' own documentation text for v1, verbatim:

> "P0.13 on VCC shuts off the power to VCC when you set it to high
> - This saves on battery immensely for LEDs of all kinds that eat power even when off"

"Set it to high to shut off" ⇒ **power ON = pin LOW ⇒ `GPIO_ACTIVE_LOW`** ✔ consistent with the v1 overlay.

> ℹ️ Earlier passes independently concluded that "no readable nice!nano schematic exists
> publicly" and marked the v1→v2 mechanism **[UNVERIFIED]**. **That caveat is superseded:** the official
> rendered schematics *are* published on nicekeyboards.com and I read them directly. The mechanism is now
> primary-sourced. What remains **[UNVERIFIED]** is the v1 P-FET's *specific part number* — the official
> image does not state an MPN (joric's wiki claims `DMP2088LCP3-7`, but that is **[CLAIM]**).

---

## 2(b) The three topologies — concrete real examples

### (i) P-FET with source on the rail, gate driven directly by GPIO

#### Example 1 — joric/nrfmicro (`Q2 = AO3407`)

**[NET]** `hardware/nrfmicro.kicad_sch`:

```
Q2 = AO3407 (P-channel, SOT-23)      pins 1=G, 2=S, 3=D
  pin 1 (G) -> POWER_PIN     (net also carries module pin P1.09)
  pin 2 (S) -> nRF_VDD       (net also carries U2.5 = AP2112K-3.3 VOUT)
  pin 3 (D) -> EXT_VCC       (net also carries U4.4 = Pro Micro VCC pin = the load)
R9 = 2M : POWER_PIN -> GND   (gate pull-down)
```
**[FILE]** ZMK: `nrfmicro_nrf52840_zmk.dts` → `<&gpio1 9 GPIO_ACTIVE_LOW>`. ✔ consistent.

**[CLAIM]** joric's own wiki, verbatim (`https://raw.githubusercontent.com/wiki/joric/nrfmicro/Archive.md`):
> "Note that **P-FET needs active pin high to disable EXT_VCC** (opposite to N-FET and EXT_GND). MCU
> retains GPIO states in off mode, so it should be fine."
> "Note power mosfet gate is floating if POWER_PIN is unintialized, so you can get random voltage
> (e.g 1.7V) on EXT_VCC, that rapidly discharges to zero."
> "* Soldered 2M pull-down resistor for power output mosfet (pulls down floating gate)"

#### Example 2 — nice!nano v1 (`Q2`, P-Channel)

**[IMAGE]** official schematic, read at 6× zoom:

```
Q2  "P Channel" : pin 3 (D, top)    -> EXT_VCC
                  pin 2 (S, bottom) -> VDD_NRF      (the AP2112K-3.3 LDO output)
                  pin 1 (G)         -> POWER_PIN  ── R9 = 2M ── GND   (gate pull-down)
POWER_PIN lands on the nRF52840 port-0 pin in the P0.12–P0.14 group;
ZMK's v1 overlay (&gpio0 13) and nicekeyboards' docs ("P0.13") both identify it as P0.13.
```
**[FILE]** ZMK: `GPIO_ACTIVE_LOW` ✔ consistent.

> ### ⚠️ CRITICAL FINDING for your specific problem
> **In BOTH real direct-drive examples, the P-FET's SOURCE is on the REGULATED 3.3 V rail — not on the
> 3.7–4.2 V battery rail.**
> - nRFMicro: `S → nRF_VDD` = AP2112K-3.3 `VOUT`.
> - nice!nano v1: `S → VDD_NRF` = AP2112K-3.3 `VOUT`.
>
> That is exactly why a 3.3 V GPIO can drive them directly: `Vgs = 0 − 3.3 = −3.3 V` to turn **on**, and
> `Vgs = 0` to turn **off** — a clean, unambiguous 3.3 V of gate drive at all times, independent of
> battery voltage.
>
> **I found NO project — in 30+ inspected keyboard hardware repos — that drives a P-FET gate directly from
> a 3.3 V GPIO with the source sitting on the raw 3.7–4.2 V battery rail.** Every design that touches the
> raw battery rail instead (**a**) drives the gate from the ~5 V VBUS rail, or (**b**) uses one of the
> topologies in (ii)/(iii) below. See §2.4.
>
> Your concern — that `Vgs = 3.3 − 4.2 = −0.9 V` sits inside the AO3401A's threshold range — is
> **[DS]**-backed on the threshold side (see §2.4) and is consistent with the observed absence of that
> topology. But **"no project does it" is an observation about the corpus, not proof it fails**, and the
> failure itself is not something I measured. Marked **[UNVERIFIED]** as a functional claim.

### (ii) P-FET driven through an N-MOS inverting stage

#### Example 1 — Croktopus/zmk-designguide ("Underglow enable" block)

**[NET]** + **[IMAGE]** (repo's own `img/underglow_1.png`; every pin number matched):

```
Q3 = AO3401A  (P-ch, SOT-23)      Q4 = 2N7002 (N-ch, SOT-23)
  G -> node {Q4.3 (D), R24.2}       G -> node {R25.2, R26.1}
  S -> UG_PWR   (LED rail = load)   S -> GND
  D -> +VSW     (system supply)     D -> Q3 gate node

R24 = 10 kOhm : +VSW      -> Q3 gate        [P-FET gate pull-UP]
R25 = 100 Ohm : UG_EN     -> Q4 gate        [series gate resistor]
R26 = 10 kOhm : Q4 gate   -> GND            [N-FET gate pull-DOWN]

net UG_PWR = { Q3.2 (S), LED3..LED9 .4 (VDD), C13..C19 }   -> 7x WS2812C_2020 VDD + decoupling
net UG_EN  = { R25.1, U7.36 (pin name "P0.10"), U8.18 ("LF-P0.10/NFC2") }
```

**Control path:** `P0.10 HIGH` → Q4 on → Q3 gate pulled LOW → `Vgs = 0 − V(+VSW) < 0` → **Q3 ON**.
So **power ON = GPIO HIGH ⇒ `GPIO_ACTIVE_HIGH`.**

⚠️ `P0.10` is an **NFC pin** on nRF52840 (`P0.10/NFC2`) — using it as a GPIO requires `NFCPINS`
configuration. Also note this sheet draws the bare nRF52840 (`U7`) and an MDBT50Q module (`U8`) as
*alternative* MCU variants on one sheet, not two chips on one board.

#### Example 2 — kurtis-lew/Conejo (a real, shipped ZMK keyboard)

**[CLAIM]** README: *"The Conejo is an OSH split, columnar-staggered, 54-key keyboard inspired by the
Iris, Lily58, and Corne and powered by the ZMK Firmware."* — <https://github.com/kurtis-lew/Conejo>

**[NET]** `nRF52840.kicad_sch` + `Conejo.kicad_sch`:

```
J4 "RGB" LED header : pin1 = EXT_PWR , pin2 = LED_MOSI (data) , pin3 = GND

Q3 = AO3407 (P-ch, SOT-23)
  pin 1 (G) -> N$5398_10096 = { Q3.1, Q2.3 (D), R14.1 }
  pin 2 (S) -> VDDH          <-- SOURCE ON THE SUPPLY RAIL  ✔ correct orientation
  pin 3 (D) -> EXT_PWR       <-- DRAIN TO THE LOAD

Q2 = 2N7002 (N-ch, SOT-23)
  pin 1 (G) -> N$4636_10604 = { Q2.1, R10.2, R13.2 }
  pin 2 (S) -> GND
  pin 3 (D) -> Q3 gate node

R14 = 10K : Q3 gate node -> VDDH      [P-FET gate pull-UP to supply]
R13 = 10K : Q2 gate node -> GND       [N-FET gate pull-DOWN]
R10 = 100R: EXT_PWR_EN   -> Q2 gate   [series gate resistor]

net EXT_PWR_EN = { R10.1, U4.38 (P0.19) }    <-- the MCU GPIO
```
**Control path:** `P0.19 HIGH` → Q2 on → Q3 gate low → Q3 on → EXT_PWR live.
⇒ **`GPIO_ACTIVE_HIGH`.** (I could not locate Conejo's own ZMK overlay in its hardware repo or under
`kurtis-lew`'s public repos — the firmware-side flag for *this specific board* is **[UNVERIFIED]**, but
the hardware unambiguously requires active-high.)

> 👍 **This is the example you want.** Conejo is the only project I found that puts a **P-FET whose source
> is on the raw battery-level system rail (`VDDH`)** and solves the gate-drive headroom problem
> **structurally**, with an N-MOS inverting stage — rather than by moving the switch to a 3.3 V rail or
> an LDO enable pin. Note `VDDH` here is the **BQ24075 `OUT` rail** (pins 10/11), i.e. the power-path
> output — battery-level when running on battery.

### (iii) Gating the ENABLE pin of a 3.3 V LDO instead

#### Example 1 — nice!nano v2 (official schematic, `U3 = XC6220B331MR`)

**[IMAGE]** block "VCC Regulator and Cut Off", read at 6× zoom:

```
U3 = XC6220B331MR  (3.3 V LDO, CE = chip enable, ACTIVE HIGH)
  pin 1 VIN  <- VDDH        (BQ24075 OUT rail)
  pin 3 CE   <- POWER_PIN   (the MCU GPIO, straight in -- no FET, no inverter)
  pin 5 VOUT -> EXT_VCC     (the switched peripheral rail)
  pin 2 GND  -> GND

R9 = 10M : VDDH -> CE node  (i.e. VDDH -> POWER_PIN)   <-- PULL-UP, not pull-down
C24 = 10uF on VIN ; C25 = 4.7uF on VOUT
```
**[FILE]** ZMK v2 overlay: `<&gpio0 13 GPIO_ACTIVE_HIGH>` — CE is active-high, so active-high is correct ✔

**Why the pull-up matters [INFERENCE]:** R9 holds CE high (rail **ON**) while the MCU pin is still
high-impedance during boot. It costs 4.2 V / 10 MΩ ≈ **0.42 µA** — negligible, which is the whole reason
10 MΩ was chosen. joric's wiki documents that an earlier revision of the *equivalent* board used a 5.6 kΩ
pull-up here and **leaked ~700 µA**; replacing it with 10 MΩ brought quiescent current "from over 700 µA
to under 20 µA". That is a concrete, order-of-magnitude design lesson if you copy this block:
**the pull resistor on an enable pin is a leakage path whenever the GPIO is pulling the pin the other way.**

#### Example 2 — sasodoma/nrf52840-promicro (reverse-engineered "SuperMini nRF52840")

**[NET]** `KiCad/promicro.kicad_sch` — a real board sold in volume as a nice!nano-compatible controller:

```
U2 = ME6217 / ME6211C33M5 (SOT-23-5 LDO)
  pin 1 V_IN  -> VDDH
  pin 2 V_SS  -> GND
  pin 3 CE    -> POWER_PIN      <-- direct GPIO
  pin 4 NC    -> no_connect
  pin 5 V_OUT -> EXTVCC         (the switched rail)

NET POWER_PIN = { R4.2, U1.AD8 (pin name "P0.13"), U2.3 (CE) }
R4 = 10M : pin1 -> VDDH , pin2 -> POWER_PIN      <-- PULL-UP, same as nice!nano v2

Q1 = AO3401A : G -> VBUS , S -> VDDH , D -> VBAT   <-- power-PATH FET, NOT the ext-power switch
```
**[FILE]** ZMK `nice_nano` rev 2.0.0 = `<&gpio0 13 GPIO_ACTIVE_HIGH>` ✔ consistent.

**[CLAIM]** joric's wiki (`Alternatives.md`), verbatim: *"external 3.3V LDO with EN pin (ME6217C33M5G,
marked J2WD). Works in ZMK as nice_nano_v2."* and *"Supports VCC cutoff control (set P0.13 to low to turn
VCC off)"* — P0.13 low ⇒ rail off ⇒ active-**HIGH** ✔. And on the pull resistor: *"Earlier batches had
5.6K pull-up resistor. Setting the power pin to GND resulted in 700 uA leak… You can desolder resistor
on the picture AND/OR replace it with 10M… Later (post-April-2024) batches already have it replaced with
10M."* — matching the extracted `R4 = 10M` **exactly**. Two independent sources agree.

#### A fourth variant worth knowing (not one of your three)

**[FILE]** `oleksandrmaslov/wafer-zmk-config`, `boards/waferboard/wafer/wafer.dtsi`:
`control-gpios = <&gpio0 29 GPIO_ACTIVE_LOW>;` preceded by
`/* P0.29 -> nPM1300 GPIO0 to toggle the load switch */` — gating a **PMIC's built-in load-switch
output** rather than a discrete FET or an LDO enable. **[FILE]**, not independently hardware-verified.

---

## 2(c) What polarity each topology requires, and why

| Topology | Turn-ON condition at the gate/CE pin | Required ZMK flag | Why |
|---|---|---|---|
| **(i) P-FET, gate direct from GPIO, source on rail** | GPIO **LOW** (→ `Vgs = 0 − V_rail < 0`) | **`GPIO_ACTIVE_LOW`** | `ext_power_enable()` drives the pin *logically active*. For a P-FET the conducting state is the gate **low**, so the active state must map to electrical LOW. Verified against nRFMicro (`&gpio1 9 ACTIVE_LOW`) and nice!nano v1 (`&gpio0 13 ACTIVE_LOW`), plus joric's wiki: *"P-FET needs active pin high to disable EXT_VCC."* |
| **(ii) P-FET via N-MOS inverting stage** | GPIO **HIGH** (→ N-FET on → P-FET gate LOW) | **`GPIO_ACTIVE_HIGH`** | The inverting stage flips the sense. Conejo: `P0.19 HIGH` → `Q2` on → `Q3` gate low → `Q3` on. Design guide: `P0.10 HIGH` → `Q4` on → `Q3` gate low → `Q3` on. |
| **(iii) LDO enable pin (CE/EN)** | GPIO **HIGH** (CE is active-high on XC6220/ME6217) | **`GPIO_ACTIVE_HIGH`** | The enable pin is a logic input, not a power path, so no level-shifting is needed at all. nice!nano v2 and the SuperMini both use `&gpio0 13 ACTIVE_HIGH` with a **10 MΩ pull-up** to hold the rail ON during boot. |

**Rule of thumb [INFERENCE]:** the flag must be `GPIO_ACTIVE_HIGH` for **any** topology with an odd number
of inversions between the GPIO and the switch element's "on" state — i.e. active-high enables and
N-FET-inverter stages. It is `GPIO_ACTIVE_LOW` for a directly-driven P-FET gate.
**Get it backwards and the LEDs are simply on when they should be off** — silently, with no error.

**Consistency check that supports the model:** ZMK's own board files contain both polarities, and each one
matches the topology I verified for that board (nRFMicro LOW ↔ direct P-FET; nice!nano v1 LOW ↔ direct
P-FET; nice!nano v2 HIGH ↔ LDO CE; Conejo HIGH ↔ N-FET inverter). The nice!nano v1→v2 flip on the *same
pin* is the cleanest possible proof that the flag tracks the hardware, not the pin.

---

## 2(d) The P-FET body-diode direction pitfall

### The physics, verified from the AO3401A datasheet

**[DS]** `AO3401A`, Alpha & Omega Semiconductor, Rev 3.1 Dec 2023 —
<https://www.aosmd.com/pdfs/datasheet/AO3401A.pdf>:

> "VGS(th) Gate Threshold Voltage **-0.5  -0.9  -1.3  V**"
> "VDS Drain-Source Voltage -30 V" ; "ID (at VGS=-10V) -4.0 A"
> "RDS(ON) (at VGS=-4.5V) < 60 mΩ" ; "RDS(ON) (at VGS=-2.5V) < 85 mΩ"
> "The AO3401A uses advanced trench technology to provide excellent RDS(ON), low gate charge and
> operation gate voltages as low as 2.5V. This device is suitable for use as a **load switch** or other
> general applications."

**Your premise is confirmed on the threshold side:** minimum `VGS(th)` magnitude is **0.5 V**, so at
`Vgs = −0.9 V` a worst-case part is above threshold and conducting in the sub-threshold region. Note also
that **`RDS(ON)` is only specified at `VGS = −2.5 V` and below** — there is no guaranteed
low-resistance region anywhere near −0.9 V.

**[IMAGE]** The datasheet's own front-page device symbol shows the **body diode drawn with its anode on
the `D` line and its cathode at `S`**, i.e. for a P-channel MOSFET the intrinsic diode conducts
**DRAIN → SOURCE**. (Verified by rendering page 1 of the PDF; an independent second rendering
reached the same reading.)

**[INFERENCE]** The design rule that follows:
- **Correct high-side switch: SOURCE to the supply, DRAIN to the load.** Diode anode = drain (load),
  cathode = source (supply) → reverse-biased when the FET is off → **it blocks.**
- **Reversed (DRAIN to the supply, SOURCE to the load):** anode = drain (supply), cathode = source (load)
  → **forward-biased whenever supply exceeds load by ~0.7 V** → the load stays energised through the body
  diode even with the FET fully off. Your "switch" becomes "always on, with a diode drop."

### Projects where the orientation is CORRECT (source → supply, drain → load)

| Project | P-FET | Source | Drain |
|---|---|---|---|
| kurtis-lew/Conejo | `Q3 AO3407` | **VDDH** (system supply) | **EXT_PWR** (LED rail = load) |
| joric/nrfmicro | `Q2 AO3407` | **nRF_VDD** (3.3 V supply) | **EXT_VCC** (load) |
| nice!nano v1 | `Q2 "P Channel"` | **VDD_NRF** (3.3 V supply) | **EXT_VCC** (load) |
| sasodoma/SuperMini | `Q1 AO3401A` | **VDDH** | **VBAT** (power-path FET) |

### Primary-source project documentation of the pitfall

**[CLAIM]** joric's nRFMicro wiki, section **"Voltage drop issues"** — the clearest project-authored
statement of this failure mode I found anywhere:

> "This it the case when you use a wired configuration and power the other half via TRRS (basically via
> the EXT_VCC pin). **There's a P-MOSFET body diode on the way.** Voltage drop is about the same 0.7-1V as
> on regular diodes (it is also fairly slow). Dedicated 1N5819 (if any) would be about 0.6V."

**[CLAIM]** The same wiki records the related undefined-gate failure:
> "##### Power mosfet issue
> Note power mosfet gate is floating if POWER_PIN is unintialized, so you can get random voltage
> (e.g. 1.7V) on EXT_VCC, that rapidly discharges to zero. You need explicitly set POWER_PIN to 0 or 1 to
> enable or disable EXT_VCC."

**[CLAIM]** And the LDO-enable workaround, stated as such:
> "**The advantage of LDO is that there's EN pin so you could get rid of the power mosfet**, the
> disadvantage is that LDO doesn't work in reverse so you would need to add another schottky diode for
> the TRRS input."

### A concrete case where the drawn orientation is questionable — flagged, not asserted

**[NET]** + **[IMAGE]** `Croktopus/zmk-designguide`, "Underglow enable" block:

```
Q3 = AO3401A :  pin 2 (S) -> UG_PWR   (the WS2812 VDD rail = LOAD)
                pin 3 (D) -> +VSW     (system supply rail = loaded by BQ24075 OUT, nRF VDDH, TXB0101 VCCB)
                pin 1 (G) -> pulled UP to +VSW through R24 = 10 kOhm
```

**[CLAIM]** The repo's README claims this block *"allows us to completely cut supply voltage for the
underglow when it is disabled … this leads to no current flowing anywhere in the circuit."*

**[INFERENCE — flagged, needs human confirmation]** As drawn, `D → supply` and `S → load` is the
**reversed** orientation per §2(d), which would make the body diode **forward-biased from `+VSW` into
`UG_PWR`**, holding the LED rail at roughly `+VSW − 0.7 V` even with Q3 off. **I am NOT asserting the
design guide is broken**, and I am explicitly *not* reporting this as a defect. Two independent
extractions plus the repo's own rendered image all agree on the pin
numbers, which rules out a parsing error — but a **KiCad library symbol whose `S`/`D` pin *names* don't
match the real SOT-23 pinout** would flip the conclusion and could not be excluded with the tools
available. If this matters for your design, ask the author or simulate it. **Do not propagate "the ZMK
design guide has a body-diode bug" from this report alone.**

> Contrast this with Conejo (§2(b)-ii), which is the *same topology from a different author* but with
> `S → VDDH` / `D → EXT_PWR` — the textbook-correct orientation. The two projects differ precisely on the
> point in question.

### Where the pitfall is NOT documented

**[FILE]/[TOOL]** ZMK's GitHub tracker was searched: `gh search issues --repo zmkfirmware/zmk` for
"underglow not turning off", "ext_power off LED still", "EXT_POWER", "ext_power". **There is no ZMK issue
or discussion attributing an "ext-power won't turn off" symptom to body-diode orientation.** The 9
`ext_power` issues found concern OLED re-init (#674), behaviour locality (#1616), settings persistence
(#1599, #2406, #3155), and unrelated display failures. The community's documentation of this failure mode
lives in **joric's nRFMicro wiki**, not in ZMK's tracker.

**[UNVERIFIED]** The textbook manufacturer app note on this was **not obtained**: ON Semiconductor
`AND9093/D` "Using MOSFETs in Load Switch Applications" was retrievable only as an abstract (the PDF
returned `unsupported content type`), and TI `SLVSCM2D` §"7.3.4.9 Reverse Current Protection" was
confirmed to *exist* in the table of contents but its body is JavaScript-gated. The closest
manufacturer document I *did* fully read is TI **SSZT658** "LDO Basics: Preventing Reverse Current"
(<https://www.ti.com/lit/ta/sszt658/sszt658.pdf>), which documents the general mechanism:

> "One drawback of tying the bulk together with the source is that a parasitic body diode forms in the
> FET… In this configuration, the body diode can turn on when the output exceeds the input voltage plus
> the VF of the parasitic diode. Reverse current flow through this diode can cause device damage…"
> On the fix: "The two FETs are placed with the sources back to back… so that the body diodes face each
> other… when a reverse current condition is detected, one of the transistors will turn off and current
> cannot flow through the back-to-back diodes."

That app note is about LDO pass FETs, **not** about discrete P-FET high-side load switches — so it
supports the *mechanism*, not the specific keyboard design rule.

---

## What I could NOT verify for Question 2

1. **A verified example of a P-FET with its SOURCE on the raw 3.7–4.2 V battery rail, gate driven
   *directly* by a 3.3 V GPIO.** Not found in 30+ inspected keyboard hardware repos. The two direct-drive
   examples both have the source on a **regulated 3.3 V** rail. **[UNVERIFIED]** — and note that "no
   project does it" is a statement about the corpus, not proof that it fails.
2. **The electrical failure itself** (that `Vgs = −0.9 V` is insufficient to keep an AO3401A off) is
   **[INFERENCE]** from the datasheet's `VGS(th)` range — **not measured, and not stated by any project's
   documentation.** The datasheet alone is enough to say the part is not *guaranteed* off at −0.9 V
   (since `|VGS(th)|` may be as low as 0.5 V and `RDS(ON)` is only specified at `VGS ≤ −2.5 V`).
3. **The design guide's Q3 orientation as an actual defect** — needs human EE confirmation, for the
   reasons in §2(d).
4. **nice!nano v1's P-FET part number** — the official schematic image labels it only "P Channel" with no
   MPN. joric's wiki claims `DMP2088LCP3-7` but that is **[CLAIM]**, unverified against the board.
5. **Glove80's `/* WS2812_CE */`** — the comment and polarity are real, but no Glove80 schematic was
   obtained, so whether that is an LDO/load-switch enable or something else is **[UNVERIFIED]**.
6. **Conejo's firmware-side ext-power flag** — the hardware unambiguously requires active-high, but I did
   not locate the board's own ZMK overlay/devicetree, so its declared flag is **[UNVERIFIED]**.
7. **Boards 7–13 and 16 in the polarity table** (puchi_ble, bluemicro840, mikoto, pillbug, nice60,
   polarityworks ckp, adv360pro, zmk_uno): the devicetree lines are **[FILE]**-verified, but I did **not**
   obtain their schematics, so the *topology* behind each flag is **[UNVERIFIED]**. Note the flags split
   roughly evenly (6 HIGH / 7 LOW among boards whose topology I did not check) — do not assume a default.
8. **nrfmicro "flipped" variant** — `GPIO_ACTIVE_HIGH` where the non-flipped board is `GPIO_ACTIVE_LOW`,
   same pin. Whether that reflects a hardware change or a firmware correction is **[UNVERIFIED]**.
9. **`cormoran/zmk-driver-ext-power-transient`** is a **firmware-only** alternative driver
   (`compatible = "zmk,ext-power-transient"`, non-persistent state, example
   `control-gpios = <&gpio0 9 (GPIO_ACTIVE_LOW)>; // NFC1 on XIAO nRF52840`). No hardware precedent in it.
10. **`fruzyna/ext-power-usb` is NOT relevant** — its full netlist contains only `BT1`, two USB_A
    connectors, and an `L7805` linear regulator. Zero MOSFETs, zero ext-power circuitry.
11. **Manufacturer app notes** — ON Semi `AND9093/D` and TI `SLVSCM2D` §7.3.4.9 bodies not retrievable.
    **[UNVERIFIED]**

---

## Bottom line for Question 2

- **All three of your topologies exist in real, netlist-verifiable projects** — and I have concrete
  examples of each: **(i)** nRFMicro + nice!nano v1, **(ii)** Croktopus design guide + **kurtis-lew/Conejo**,
  **(iii)** **nice!nano v2** + sasodoma/SuperMini.
- **The answer to your headroom problem is architectural, and the ecosystem already demonstrates all three
  solutions.** Nobody drives a P-FET gate directly from a 3.3 V GPIO against a 4.2 V source. They either
  (a) put the P-FET's source on the **3.3 V rail**, (b) add an **N-MOS inverting stage** (Conejo — source
  on battery-level `VDDH`, gate driven through a 2N7002), or (c) **gate an LDO enable pin**, which is
  logic-level by construction and needs no level shifting at all.
- **nice!nano v2 — the most widely used ZMK controller — chose (c).** It uses a BQ24075 but hard-wires
  SYSOFF to GND, and cuts power by driving an `XC6220B331MR` CE pin through 10 MΩ from P0.13, with
  `GPIO_ACTIVE_HIGH`. If you want a proven, shipping precedent for gating an LED rail, **that is it.**
- **Polarity is binary and silent:** `GPIO_ACTIVE_LOW` for a directly-driven P-FET; `GPIO_ACTIVE_HIGH` for
  an N-FET inverter stage or an active-high LDO enable. Getting it backwards gives no error — just an LED
  rail that never turns off.
- **The body-diode direction pitfall is real and documented in this ecosystem** (joric's nRFMicro wiki),
  and **two projects using the same topology disagree on the orientation** — Conejo draws source→supply
  (correct), the design guide draws source→load (questionable). **If you copy a reference design, copy
  Conejo's orientation, and verify it yourself.**
- **Do not forget the pull resistor's leakage:** the enable-pin pull-up is a permanent leak whenever the
  GPIO pulls the other way. 5.6 kΩ → ~700 µA (a documented real-world bug); 10 MΩ → ~0.42 µA. Choose
  accordingly, and note the resistor is there to define the rail during MCU boot.
