# JST PH-series 2.0 mm parts — verbatim distributor attributes

Research date: 2026-09 (StarShield PCB component fact-gathering).
Rule followed: every value below was read off a page actually fetched; values are quoted verbatim.
PDFs are cited by URL only (the PDFs themselves were fetched and text-extracted locally).

## Source keys

| Key | Source | URL |
|---|---|---|
| **JST-PH** | JST official PH connector series page (product profile + specification + product list) | https://www.jst-mfg.com/product/detail_e.php?series=199 → resolves to https://www.jst-mfg.com/product/index.php?series=199&lang=2 |
| **JST-PDF** | JST official PH catalogue (PDF, not machine-readable here) | https://www.jst-mfg.com/product/pdf/eng/ePH.pdf |
| **JST-ENV** | JST official Environmental Survey page (part-number identification symbols) | https://www.jst-mfg.com/env/?lang=2 |
| **HQ** | HQ Online (NextPCB) product page — full attribute table | see per-part rows |
| **LCSC** | LCSC product data (JSON service that backs the LCSC product page) | see per-part rows |
| **DKF** | DigiKey TechForum — **NOT PRIMARY** (distributor forum, statement attributed to JST) | https://forum.digikey.com/t/jst-suffixes-lf-sn-au-s-n-m-prefixes-g-w-c-q-d/605 |
| **DKF2** | DigiKey TechForum, 2nd thread — **NOT PRIMARY** | https://forum.digikey.com/t/why-does-my-part-have-an-lf-sn-suffix-but-it-does-not-show-this-as-the-ordering-part/60889 |
| **ICZ** | ICZOOM product page for the **base** PN `B2B-PH-K-S` (legacy, stale data — see caveat) | https://en.iczoom.com/product/k07-23573041-B2B-PH-K-S.html |

LCSC page ⇄ JSON pairs used (the JSON is the data behind the page; the rendered LCSC HTML body returns
mostly site navigation, so values were taken from the JSON service and cross-checked against the parent's
cached LCSC HTML JSON-LD):

| Part | LCSC page | JSON used |
|---|---|---|
| B2B-PH-K-S(LF)(SN) | https://www.lcsc.com/product-detail/C131337.html | https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=C131337 |
| PHR-2 | https://www.lcsc.com/product-detail/C157955.html | https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=C157955 |
| SPH-002T-P0.5S | https://www.lcsc.com/product-detail/C111515.html | https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=C111515 |
| SPH-002T-P0.5L | https://www.lcsc.com/product-detail/C265456.html | https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=C265456 |
| S2B-PH-K-S(LF)(SN) | https://www.lcsc.com/product-detail/C173752.html | https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=C173752 |
| B2B-PH-SM4-TB(LF)(SN) | https://www.lcsc.com/product-detail/C160352.html | https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=C160352 |

---

## 1. B2B-PH-K-S(LF)(SN) — top-entry through-hole header, 2 circuits

### 1a. Series-level specification stated by JST (JST-PH)
Applies to the PH series; JST's own note on that page says to use the representative specification
for the same circuit count with a different part-number suffix.

| Attribute | Verbatim value | Source |
|---|---|---|
| Series | `PH connector` | JST-PH |
| Category | `Crimp Style Connectors (Wire-to-Board type)` | JST-PH |
| PC board mounting | `Through-hole, SMT` | JST-PH |
| Mating direction | `Side entry, Top entry` | JST-PH |
| Array (Insertion part) | `Single-row` | JST-PH |
| Lock | `Friction lock` | JST-PH |
| Standard | `TÜV, UL` | JST-PH |
| Intro text | `With a mounting height of 8 mm and a width of only 4.5 mm in the top-entry version, this low-profile wire-to board connector features a pitch of 2.0 mm.` | JST-PH |
| Pitch | `2 mm` | JST-PH |
| Circuit | `2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16` | JST-PH |
| Current rating | `2 A AC/DC (AWG #24)` | JST-PH |
| Voltage rating | `100 V AC/DC` | JST-PH |
| Temperature range | `-40 ℃ to +105 ℃` | JST-PH |
| Insulation resistance | `1,000 MΩ min.` | JST-PH |
| Withstanding voltage | `There shall be no breakdown or flashover while applying 800 VAC for one minute.` | JST-PH |
| Conductor size | `AWG # 32 , # 30 , # 28 , # 26 , # 24  0.032 mm2 to 0.22 mm2` | JST-PH |
| Insulation O.D. | `φ 0.5 mm to φ 1.5 mm` | JST-PH |
| Product list entry | item 19 = `B2B-PH-K-S` (representative PN; 2D-PDF `B2B-PH-K-S.pdf`) | JST-PH |

### 1b. Distributor attribute table (HQ)
Source: https://www.hqonline.com/product-detail/wire-to-board-connectors-jst-b2b-ph-k-s-lf--sn--2500219066

| Attribute | Verbatim value |
|---|---|
| Mfr Part # | `B2B-PH-K-S(LF)(SN)` |
| Description | `Wire to Board Connectors 1x2P Direct Insertion P:2mm` |
| Product Type | `Connectors / Wire to Board Connectors` |
| Insulation Height | `0.236"（6.00mm）` |
| Height | `6.00mm` |
| Size | `5.90 x 4.50mm` |
| Spacing | `2.00mm` |
| Rated Voltage | `100V` |
| Rated Current | `2A` |
| Contact Material | `Brass` |
| Contact Coating | `Tin` |
| Operating Temperature | `-25℃~+85℃` |
| Storage Temperature | `-25~+85℃` |
| Flammability Grade Of Materials | `UL94V-0` |
| Number of Positions | `2Pin` |
| Number of Rows | `Single row` |
| Number Of Pins Per Row | `2` |
| Pin Structure | `1x2P` |
| Male And Female | `Male` |
| Connector Type | `Joint` |
| Fastening Type | `Latch Lock` |
| Installation Type | `Direct Insertion` |
| Package / Case | `DIP,P=2mm` |
| Series | `PH` |
| Colour | `White` |
| Moisture Sensitivity Level (MSL) | `1 (Unlimited)` |
| Application Level | `Consumer` |

### 1c. Distributor attribute table (LCSC, C131337)
Source: https://www.lcsc.com/product-detail/C131337.html (data: `.../productCode=C131337`)

| Attribute | Verbatim value |
|---|---|
| Title / MPN | `JST B2B-PH-K-S(LF)(SN)` |
| productNameEn | `CONN HEADER TH 2POS 2mm` |
| Description / Intro | `Connector Header 2 position 2mm Pitch 2A Through Hole -25℃~+85℃` |
| Connector Type | `Through Hole` |
| Package standard | `Through Hole,P=2mm` |
| Reference Series | `PH` |
| Pitch | `2mm` |
| Number of PINs | `2P` |
| Number of PINs Per Row | `2` |
| Number of Rows | `1` |
| Pin Structure | `1x2P` |
| Voltage Rating (Max) | `100V` |
| Current Rating | `2A` |
| Contact Material | `Brass` |
| Contact Plating | `Tin` |
| Plastic Material | `PA66` |
| Flame Retardant Rating | `UL94V-0` |
| Colour | `White` |
| Operating Temperature | `-25℃~+85℃` |
| Supplementary Features | `K Pin` |
| X-Length of Bottom Edge on Board (Spacing Line) | `5.9mm` |
| RoHS fields (`authenticationList` / `isRohsCert`) | `null` — this SKU carries no RoHS badge on LCSC |

### 1d. Legacy/stale third-party table for the base PN (ICZ) — use with care
The ICZOOM page is for `B2B-PH-K-S` (no suffix) and its own data says `Part Status: Obsolete` and
`Lead Free Status / RoHS Status: Contains lead / RoHS non-compliant`, `Contact Finish: Tin-Lead`.
It is useful **only** for the geometry rows, and it does **not** describe the `(LF)(SN)` ordering PN:

| Attribute | Verbatim value | Source |
|---|---|---|
| Insulation Height | `0.236 (6.00mm)` | ICZ |
| Contact Length - Post | `0.134 (3.40mm)` | ICZ |
| Overall Contact Length | `0.333 (8.45mm)` | ICZ |
| Contact Mating Length | `0.130" (3.30mm)` | ICZ |
| Mated Stacking Heights | `8mm` | ICZ |
| Insulation Material | `Polyamide (PA66), Nylon 6/6` | ICZ |
| Contact Finish / Material | `Tin-Lead` / `Brass` | ICZ |
| Mounting Type / Termination | `Through Hole` / `Press-Fit, Solder` | ICZ |
| Pitch - Mating | `0.079 (2.00mm)` | ICZ |
| Shrouding | `Shrouded - 4 Wall` | ICZ |
| Fastening Type | `Detent Lock` | ICZ |
| Current Rating (Amps) / Voltage Rating | `2A` / `100V` | ICZ |
| Operating Temperature | `-25°C ~ 85°C` | ICZ |
| Material Flammability Rating | `UL94 V-0` | ICZ |
| Part Status | `Obsolete` | ICZ |

### 1e. Direct answers for part 1
| Asked | Answer | Source |
|---|---|---|
| (a) description/title | HQ: `Wire to Board Connectors 1x2P Direct Insertion P:2mm`; LCSC: `CONN HEADER TH 2POS 2mm` / `Connector Header 2 position 2mm Pitch 2A Through Hole -25℃~+85℃` | HQ, LCSC |
| (b) positions | `2Pin` / `2P` / JST series `Circuit 2…16` | HQ, LCSC, JST-PH |
| (c) pitch | `2.00mm` / `2mm` / JST `2 mm` | HQ, LCSC, JST-PH |
| (d) mounting type | `Direct Insertion`, `DIP,P=2mm` / `Through Hole`, `Through Hole,P=2mm` | HQ, LCSC |
| (e) contact material | `Brass` | HQ, LCSC |
| (f) contact finish | `Tin` | HQ, LCSC |
| (g) dimensions | HQ `Size 5.90 x 4.50mm`, `Height 6.00mm`, `Insulation Height 0.236"（6.00mm）`; LCSC `X-Length of Bottom Edge on Board (Spacing Line) 5.9mm`; JST `mounting height of 8 mm … width of only 4.5 mm in the top-entry version` | HQ, LCSC, JST-PH |
| (h) current / voltage | `2A` / `100V` (distributors); JST `2 A AC/DC (AWG #24)` / `100 V AC/DC` | HQ, LCSC, JST-PH |
| (i) operating temperature | `-25℃~+85℃` (both distributors) **vs** JST series `-40 ℃ to +105 ℃` — CONFLICT | HQ, LCSC, JST-PH |
| (j) lead free / RoHS / tin | `Contact Coating: Tin` (HQ), `Contact Plating: Tin` (LCSC); **no fetched page spells out "lead free" or "RoHS" for this PN**; LCSC RoHS fields are `null` | HQ, LCSC |

---

## 2. PHR-2 — 2-circuit wire housing (mates the header)

| Attribute | Verbatim value | Source |
|---|---|---|
| Mfr Part # | `PHR-2` | HQ, LCSC |
| Description (HQ) | `Rubber shell spacing P=2.00mm 2Pin (1x2)` | https://www.hqonline.com/product-detail/rubber-shells-and-accessories-jst-phr-2-2500219074 |
| Description (LCSC) | `CONN HOUSING 2POS 2mm SINGLE ROW PH` / `Connector Housing 2 Position 2mm Pitch Single Row PH Series PA66 -25℃~+85℃` | https://www.lcsc.com/product-detail/C157955.html |
| Spacing / Pitch | `2.00mm` / `2mm` | HQ, LCSC |
| Number of Positions | `2Pin` (`Number of PINs Per Row: 2`, `Holes Structure: 1x2P`, `Pin Structure: 1x2P`) | HQ, LCSC |
| Number of Rows | `Single row` / `1` | HQ, LCSC |
| Connector Type | `Socket` | HQ |
| Installation Type | `Free Hanging` | HQ |
| Housing / Plastic Material | `PA66` | HQ, LCSC |
| Rated Voltage | `100V` | HQ |
| Rated Current | `2A` | HQ |
| Operating Temperature | `-25℃~+85℃` | HQ, LCSC |
| Storage Temperature | `-25~+85℃` | HQ |
| Size | `5.80 x 4.50mm` | HQ |
| Height | `6.40mm` | HQ |
| Colour | `White` | HQ, LCSC |
| Certification | `RoHS` | HQ |
| Lead Free Or Not | `Yes` | HQ |
| Country of Origin | `Japan` | HQ |
| Part Status | `Active` | HQ |
| With Locker / With Wings / Row Spacing (LCSC) | `Non-Latching` / `Without Fins` / `-` | LCSC |
| Flammability (LCSC) | `UL94V-0` | LCSC |
| LCSC certification | `ROHS3 认证` (`isRohsCert: true`, `rohsCertType: ROHS3`) | LCSC |
| JST official listing | `PHR-2` is product #4 of the PH series 3D/2D data list | JST-PH |

---

## 3. SPH-002T-P0.5S — crimp contact

| Attribute | Verbatim value | Source |
|---|---|---|
| Mfr Part # | `SPH-002T-P0.5S` | HQ, LCSC |
| Description (HQ) | `Rubber shell terminal 24-30AWG` | https://www.hqonline.com/product-detail/housing-contact-jst-sph-002t-p0-5s-2500219104 |
| Description (LCSC) | `CONN TERM 24~30AWG CRIMP TIN` / `Connector Terminal PH Tin 24~30 AWG Crimp` | https://www.lcsc.com/product-detail/C111515.html |
| Wire Gauge - AWG | `24-30AWG` / `24~30` | HQ, LCSC |
| Wire Gauge - mm² | `0.05~0.22mm²` / `0.05~0.22` | HQ, LCSC |
| Insulation OD | `0.8mm~1.5mm` (LCSC only) | LCSC |
| Contact Material | `Phosphor Bronze` / `Phosphor bronze` | HQ, LCSC |
| Contact Coating / Plating | `Tin` | HQ, LCSC |
| Rated Voltage / Current | `100V` / `2A` | HQ |
| Operating Temperature | `-25℃~+85℃` | HQ |
| Installation Type | `Free Hanging` | HQ |
| Size / Height | `5.70 x 1.50mm` / `2.08mm` | HQ |
| Series | `PH` | HQ, LCSC |
| Packaging (LCSC) | `Tape & Reel (TR)`, min. packet 8000 | LCSC |
| LCSC certification | `ROHS3 认证` | LCSC |
| JST official listing | `SPH-002T-P0.5S` is product #2 of the PH series list (2D-PDF drawing available) | JST-PH |
| JST series-level wire data | `AWG # 32 , # 30 , # 28 , # 26 , # 24  0.032 mm2 to 0.22 mm2`; `Insulation O.D. φ 0.5 mm to φ 1.5 mm` | JST-PH |
| Farnell page (body NOT retrieved, 403) | slug states `contact-socket-30-24awg-crimp` — UNVERIFIED | https://uk.farnell.com/jst-japan-solderless-terminals/sph-002t-p0-5s/contact-socket-30-24awg-crimp/dp/2524012 |

---

## 4. SPH-002T-P0.5L — crimp contact (other variant)

| Attribute | Verbatim value | Source |
|---|---|---|
| Mfr Part # | `SPH-002T-P0.5L` | HQ, LCSC |
| Description (HQ) | `Rubber shell terminal 24-28AWG` | https://www.hqonline.com/product-detail/housing-contact-jst-sph-002t-p0-5l-2500269116 |
| Description (LCSC) | `CONN TERM 24~28AWG CRIMP TIN` / `Connector Terminal PH PAD Tin 24~28 AWG Crimp` | https://www.lcsc.com/product-detail/C265456.html |
| Wire Gauge - AWG | `24-28AWG` / `24~28` | HQ, LCSC |
| Wire Gauge - mm² | `0.08~0.22mm²` / `0.08~0.22` | HQ, LCSC |
| Insulation OD | `0.8mm~1.5mm` (LCSC only) | LCSC |
| Contact Material | `Phosphor Bronze` / `Phosphor bronze` | HQ, LCSC |
| Contact Coating / Plating | `Tin` | HQ, LCSC |
| Rated Voltage / Current | `100V` / `2A` | HQ |
| Operating Temperature | `-25℃~+85℃` | HQ |
| Size / Height | `5.70 x 1.50mm` / `2.08mm` | HQ |
| Series | `PH` (LCSC Reference Series field: `PH;PAD`) | HQ, LCSC |
| LCSC certification | `ROHS3 认证` | LCSC |
| JST official listing | `SPH-002T-P0.5L` is product #3 of the PH series list | JST-PH |
| Farnell page (body NOT retrieved, 403) | slug states `contact-socket-28-24awg-crimp` — UNVERIFIED | https://uk.farnell.com/jst-japan-solderless-terminals/sph-002t-p0-5l/contact-socket-28-24awg-crimp/dp/2399572 |

### What makes .5L different from .5S — as stated on fetched pages
The **only** difference any fetched page states is the applicable wire range:

| | SPH-002T-P0.5S | SPH-002T-P0.5L |
|---|---|---|
| HQ Online description | `Rubber shell terminal 24-30AWG` | `Rubber shell terminal 24-28AWG` |
| HQ wire range | `24-30AWG`, `0.05~0.22mm²` | `24-28AWG`, `0.08~0.22mm²` |
| LCSC wire range | `24~30`, `0.05~0.22` | `24~28`, `0.08~0.22` |
| LCSC Reference Series | `PH` | `PH;PAD` |

Everything else that both pages list (contact material `Phosphor Bronze`, coating `Tin`, `100V`, `2A`,
`-25℃~+85℃`, size `5.70 x 1.50mm`, height `2.08mm`, series `PH`, MSL 1) is **identical**.
No fetched page states a plating, geometry, insulation-OD, or packaging difference →
any other claimed difference is **UNVERIFIED**.

---

## 5. S2B-PH-K-S(LF)(SN) — side-entry (right-angle) through-hole header

Exists: confirmed on JST's own PH series product list (item 34, `S2B-PH-K-S`) and on two distributors.

| Attribute | Verbatim value | Source |
|---|---|---|
| Mfr Part # | `S2B-PH-K-S(LF)(SN)` | HQ, LCSC |
| Description (HQ) | `Wire to Board Connectors 1x2P Bending Insert P:2mm` | https://www.hqonline.com/product-detail/wire-to-board-connectors-jst-s2b-ph-k-s-lf--sn--2500219095 |
| Description (LCSC) | `CONN HEADER TH R/A 2POS 2mm` / `Connector Header 2 position 2mm Pitch 2A Right Angle -25℃~+85℃` | https://www.lcsc.com/product-detail/C173752.html |
| Connector Type | `Bending Insert` / `Right Angle`; package `Through Hole,Right Angle,P=2mm` | HQ, LCSC |
| Insulation Height | `0.189"（4.80mm）` | HQ |
| Height | `4.80mm` | HQ |
| Size | `5.90 x 7.60mm` | HQ |
| Spacing / Pitch | `2.00mm` / `2mm` | HQ, LCSC |
| Rated Voltage / Current | `100V` / `2A` | HQ, LCSC |
| Contact Material | `Brass` | HQ, LCSC |
| Contact Coating / Plating | `Tin` | HQ, LCSC |
| Operating Temperature | `-25℃~+85℃` | HQ, LCSC |
| Flammability | `UL94V-0` | HQ, LCSC |
| Positions / Rows / Pin Structure | `2Pin` / `Single row` / `1x2P` | HQ, LCSC |
| Fastening Type | `Latch Lock` | HQ |
| Colour | `White`; LCSC plastic `PA66` | HQ, LCSC |
| LCSC extras | `Supplementary Features: K Pin`; `X-Length of Bottom Edge on Board (Spacing Line): 5.9mm`; `ROHS3 认证` | LCSC |
| JST official listing | item 34 = `S2B-PH-K-S` | JST-PH |

---

## 6. B2B-PH-SM4-TB(LF)(SN) — surface-mount header

Exists: confirmed on JST's own PH series product list (item 49, `B2B-PH-SM4-TB`) and on two distributors.

| Attribute | Verbatim value | Source |
|---|---|---|
| Mfr Part # | `B2B-PH-SM4-TB(LF)(SN)` | HQ, LCSC |
| Description (HQ) | `Wire to Board Connectors 1x2P Stand Mounting P:2mm` | https://www.hqonline.com/product-detail/wire-to-board-connectors-jst-b2b-ph-sm4-tb-lf--sn--2500219068 |
| Description (LCSC) | `CONN HEADER SMD 2POS 2mm` / `Connector Header 2 position 2mm Pitch 2A Surface Mount,Vertical -25℃~+85℃` | https://www.lcsc.com/product-detail/C160352.html |
| Installation Type / Package | `Stand Mounting`, `SMD,P=2mm` / `Surface Mount,Vertical` | HQ, LCSC |
| Insulation Height | `0.260"（6.60mm）` | HQ |
| Height | `6.60mm` | HQ |
| Size | `7.95 x 5.00mm` | HQ |
| Spacing / Pitch | `2.00mm` / `2mm` | HQ, LCSC |
| Rated Voltage / Current | `100V` / `2A` | HQ, LCSC |
| Contact Material | `Copper Alloy` / `Copper alloy` | HQ, LCSC |
| Contact Coating / Plating | `Tin` | HQ, LCSC |
| Operating Temperature | `-25℃~+85℃` | HQ, LCSC |
| Flammability | `UL94V-0` | HQ, LCSC |
| Positions / Rows / Pin Structure | `2Pin` / `Single row` / `1x2P` | HQ, LCSC |
| Fastening Type | `Latch Lock` | HQ |
| Characteristic (HQ) | `Fixed welding tail`; LCSC: `Supplementary Features: Auxiliary Solder Pin` | HQ, LCSC |
| Colour | `Ivory` / LCSC `Color: Beige`, plastic `PA` | HQ, LCSC |
| LCSC extras | `X-Length of Bottom Edge on Board (Spacing Line): 7.95mm`; `ROHS 认证` | LCSC |
| JST official listing | item 49 = `B2B-PH-SM4-TB` | JST-PH |

---

## 7. What "(LF)(SN)" means on a JST part number

**Primary source (JST itself), verbatim — JST-ENV (https://www.jst-mfg.com/env/?lang=2):**
> `2. Product Part Numbers`
> `The identification symbols at the end of the part numbers below indicate RoHS-compliant products.`
> `Examples of identification symbols include (LF), (SN), (LF)(SN), (LF)(SN)A, (LF)(SN)B, (LF)(AU), K, (LF)K, (PF), (PF)(CLEAR), etc.`

⇒ Officially confirmed by JST: a trailing `(LF)(SN)` marks a **RoHS-compliant product**.
⇒ That JST page does **not** expand `LF` = lead-free or `SN` = tin. No other JST page I could fetch does.

**Distributor forum statement attributed to JST — NOT PRIMARY (DKF):**
Source: https://forum.digikey.com/t/jst-suffixes-lf-sn-au-s-n-m-prefixes-g-w-c-q-d/605
> `JST has offered the following information regarding these suffixes.`
> `Prefixed characters indicate the factory of origin while suffixed characters may indicate RoHS compliance and/or internal JST changes …`
> `(LF) = Lead-free. The finish would be 98% tin and 2% copper.`
> `(LF)(SN) = Lead-free with a 100% pure tin finish [SN is the Periodic Table of Elements symbol for tin]. This was an orderable part number, but as of this document … all versions are RoHs compliant and it is no longer needed, the base part number is sufficient.`
> `(LF)(AU) = Lead-free with a 100% gold finish [AU is the Periodic Table of Elements symbol for gold]. The gold finish would have a nickel underplate.`
> `(G) = Shanghai, China   (W) = Indonesia   (C) = Waukegan, Illinois, USA   (Q) = Korea   (D) = Malaysia` … `If there is no character prefixed to the part number, the country of origin is Japan`

**Second, more recent DigiKey forum thread — NOT PRIMARY (DKF2):**
Source: https://forum.digikey.com/t/why-does-my-part-have-an-lf-sn-suffix-but-it-does-not-show-this-as-the-ordering-part/60889
> `(LF)(SN) = Lead-free with a 100% pure tin finish [SN is the Periodic Table of Elements symbol for tin]. This was an orderable part number, but as of this document all versions are RoHs compliant and it is no longer needed, the base part number is sufficient to order but the (LF)(Sn) will still show on the label.`
> `See also the datasheet, page 3, note 1 which states: Note: 1. This product displays (LF)(SN) on a label.`

⚠️ That quoted "page 3, note 1" is on the JST datasheet **JST-PDF**
(https://www.jst-mfg.com/product/pdf/eng/ePH.pdf), which is the primary source for the note — but
I could **not** open the PDF to read it myself (PDFs are not readable by ordinary page fetching), so the note text
is a distributor's quotation, not a value I verified first-hand.

---

## COULD NOT VERIFY

1. **Digi-Key product pages — never retrieved.** `digikey.com` (product 926701) returned HTTP 403
   `Just a moment...` (Cloudflare) on three separate attempts; `digikey.in` also 403.
   No Digi-Key attribute value is quoted anywhere above.
2. **Mouser — never retrieved.** `mouser.com`, `mouser.in`, `mouser.de`, `eu.mouser.com` all failed
   (fetch error / `Access Denied` page).
3. **Farnell / element14 / Newark / CPC — never retrieved.** HTTP 403 Akamai `Access Denied` on
   `uk.`, `fi.`, `ch.`, `at.`, `in.element14.com`, `cpc.farnell.com`; `newark.com` fetch failed.
   Only URL **slugs** were observed (e.g. `header-top-entry-2way-2mm` for B2B-PH-K-S(LF)(SN),
   `connector-header-tht-r-a-2mm-2way` for S2B, `connector-header-smt-2mm-2way` for B2B-PH-SM4-TB);
   these are search-result URL text, **not** verified page content.
4. **RS Online / Distrelec / Elfa / TME / Arrow / TTI / OnlineComponents / trustedparts — all blocked**
   (403 or cross-origin redirect to rs-online.com).
5. **A single manufacturer-stated 3-axis body envelope (L × W × D)** was not found on any fetched HTML
   page. What is available is a composite: distributors give footprint+height (`5.90 x 4.50mm`,
   `Height 6.00mm` for the top-entry header), while JST's page gives `mounting height of 8 mm and a
   width of only 4.5 mm`. **The 8 mm figure conflicts with the distributors' 6.00 mm**; 8 mm matches
   ICZOOM's `Mated Stacking Heights: 8mm`, i.e. it is probably the mated height, not the bare header
   height — but no fetched page states this explicitly. UNRESOLVED.
6. **PCB hole / pin dimensions (drill diameter, pin cross-section).** Not stated on any fetched HTML
   page; they live only in JST drawings (PDFs, e.g. `B2B-PH-K-S.pdf`) which I cannot read.
7. **Contact finish thickness** (µin/µm): ICZOOM lists `Contact Finish Thickness: -` and no other fetched
   page states a value. UNVERIFIED.
8. **Per-contact insulation O.D. for SPH-002T-P0.5S / .5L.** LCSC states `0.8mm~1.5mm`; JST's page states
   the series-level `φ 0.5 mm to φ 1.5 mm`. Which range applies to the `-002T-` contact specifically is
   UNVERIFIED.
9. **"Lead free" / "RoHS" in words for the header part numbers.** HQ Online prints `Certification: RoHS`
   and `Lead Free Or Not: Yes` only on its **PHR-2** page; its header pages (B2B-PH-K-S(LF)(SN),
   S2B, B2B-PH-SM4-TB) carry no such row. LCSC marks PHR-2/SPH-002T-P0.5S/SPH-002T-P0.5L/S2B-PH-K-S(LF)(SN)
   as ROHS3 and B2B-PH-SM4-TB(LF)(SN) as ROHS, but the **B2B-PH-K-S(LF)(SN)** SKU's RoHS fields are `null`.
   The only authoritative "RoHS" statement for these suffixes is JST-ENV, which identifies the suffix
   symbols as RoHS-compliant markers (§7).
10. **SPH-002T-P0.5S vs SPH-002T-P0.5L differences other than wire range** — see §4. UNVERIFIED.
11. **The JST `ePH.pdf` note text** quoted in §7 — PDF not readable; quoted from a distributor forum.
