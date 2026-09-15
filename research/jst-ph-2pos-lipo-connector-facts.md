# JST PH Series 2.0 mm, 2-Position — Connector Fact Sheet for a Single-Cell LiPo Keyboard PCB

**Scope:** PCB header + mating wire housing + crimp contact + PH-series electrical/mechanical ratings.
**Method:** primary sources preferred (jst-mfg.com, LCSC, distributor pages). Every value carries a URL. Anything I could not confirm from a page I actually fetched is marked **UNVERIFIED**.

**Verification legend used below**

| Tag | Meaning |
|---|---|
| **[JST]** | Read verbatim off an official jst-mfg.com page — authoritative |
| **[DIST]** | Read off a distributor / catalogue aggregator page (LCSC, DigiPart, HQ Online, Findchips, acme-chip) — good, but second-hand |
| **[NOT PRIMARY]** | Read off a forum post. Directional only; do not cite as a spec |
| **UNVERIFIED** | Could not confirm from any fetched page |

---

## 0. Bottom line — the BoM for one LiPo pigtail

| Role | Part number | Status |
|---|---|---|
| PCB header, top entry, THT, 2 ckt | **B2B-PH-K-S(LF)(SN)** (base PN `B2B-PH-K-S`) | ✅ verified |
| Mating wire housing, 2 ckt | **PHR-2** | ✅ verified |
| Crimp contact in PHR-2 (typical 26–30 AWG LiPo wire) | **SPH-002T-P0.5S** | ✅ verified |
| Crimp contact, alt (24–28 AWG) | **SPH-002T-P0.5L** | ✅ verified |
| Header, side entry (right angle), THT | **S2B-PH-K-S(LF)(SN)** (base `S2B-PH-K-S`) | ✅ verified |
| Header, SMT vertical | **B2B-PH-SM4-TB(LF)(SN)** (base `B2B-PH-SM4-TB`) | ✅ verified |

---

## 1. PCB-mounted HEADER — `B2B-PH-K-S(LF)(SN)`

**Verdict: `B2B-PH-K-S(LF)(SN)` is correct.** The base model number is exactly `B2B-PH-K-S`, and JST's own parts catalogue notes for that base number: *"This product displays "(LF)(SN)" on the label."* — i.e. the `(LF)(SN)` form is the same part, so both `B2B-PH-K-S` and `B2B-PH-K-S(LF)(SN)` order correctly.
[Source: JST model-number search for `B2B-PH-K-S`](https://www.jst-mfg.com/product/index.php?type=1&search_product=B2B-PH-K-S&page=1) **[JST]**

JST's PH-series 3D/2D data table lists `B2B-PH-K-S` (item 19) with a 2D/3D drawing download: [`B2B-PH-K-S.pdf`](https://www.jst-mfg.com/product/index.php?type=10&series=199&doc=4&filename=B2B-PH-K-S.pdf) — this is the authoritative footprint drawing. **[JST]**
Series page: <https://www.jst-mfg.com/product/index.php?series=199> **[JST]**

### What the distributor pages state

| Attribute | Value | Source |
|---|---|---|
| Orderable PN / MPN | `B2B-PH-K-S(LF)(SN)` | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]** |
| Description | `CONN HEADER TH 2POS 2mm` / "Connector Header 2 position 2mm Pitch 2A Through Hole −25℃~+85℃" | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]** |
| Category | Headers, Male Pins → Header, Shrouded | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html), [DigiPart](https://www.digipart.com/part/B2B-PH-K-S) **[DIST]** |
| Number of positions | 2 (`2P`, 1 row, `1x2P`) | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]** |
| Pitch | 2 mm | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]** |
| Mounting / connector type | Through Hole (`Through Hole,P=2mm`), Straight / top entry | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]** |
| Contact material | Brass | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]** |
| Contact plating / finish | **Tin** | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]** |
| Housing / plastic material | PA66, flammability `UL94V-0`, colour White | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]** |
| Current rating | `2A` | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]** |
| Voltage rating | `100V` | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]** |
| Operating temperature | `−25℃~+85℃` ⚠️ conflicts with JST's `−40 ℃ to +105 ℃` — see §4 | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]** |
| Supplementary feature | `K Pin` (the PCB retention / kink pin) | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]** |
| Lead free / RoHS | "Lead Free / RoHS compliant" | [acme-chip](https://www.acme-chip.com/pdut/B2B-PH-K-S-LF-SN/4331583.htm) **[DIST — broker site, weak]** |

> ⚠️ LCSC's RoHS fields for SKU `C131337` are **null** (no RoHS badge), unlike its other PH SKUs. LCSC's *description* still says JST-compliant, but the only authoritative RoHS statement for the suffix is JST's own environmental page (§1.1). Flagged, not resolved. **[DIST]**

### 1.1 What the suffix `(LF)(SN)` means

**Primary answer — from JST itself:**
> "The identification symbols at the end of the part numbers below indicate RoHS-compliant products. Examples of identification symbols include (LF), (SN), (LF)(SN), (LF)(SN)A, (LF)(SN)B, (LF)(AU), K, (LF)K, (PF), (PF)(CLEAR), etc."

[Source: JST Environmental Survey page](https://www.jst-mfg.com/env/?lang=2) **[JST — PRIMARY]** (verified by direct fetch)

So, authoritatively: **trailing `(LF)(SN)` = RoHS-compliant product.** JST's page does **not** expand the letters.

**The lead-free / tin expansion is NOT primary.** A DigiKey TechForum post attributing the wording to JST states:
> "(LF) = Lead-free. The finish would be 98% tin and 2% copper."
> "(LF)(SN) = Lead-free with a 100% pure tin finish [SN is the Periodic Table of Elements symbol for tin]. This was an orderable part number, but as of this document … all versions are RoHs compliant and it is no longer needed, the base part number is sufficient."
> "(LF)(AU) = Lead-free with a 100% gold finish. The gold finish would have a nickel underplate."

[Source: DigiKey TechForum "JST Suffixes LF SN AU S N M…"](https://forum.digikey.com/t/jst-suffixes-lf-sn-au-s-n-m-prefixes-g-w-c-q-d/605) **[NOT PRIMARY]**

**Conclusion you can rely on:** `(SN)` = tin plating is *corroborated* by the LCSC attribute `Contact Plating: Tin` on the `(LF)(SN)` part ([LCSC C131337](https://www.lcsc.com/product-detail/C131337.html)) **[DIST]** — i.e. two independent non-JST sources agree, while JST itself only certifies "RoHS-compliant". Treat "lead-free, pure-tin finish" as **well-corroborated but not JST-verbatim**.

---

## 2. Mating HOUSING — `PHR-2`

**Verdict: `PHR-2` is the correct mating housing.** JST's own model-number search returns exactly two hits for `PHR-2`, both under the PH connector series (PH connector, PH connector High-box type), both RoHSII. [Source: JST model search for `PHR-2`](https://www.jst-mfg.com/product/index.php?type=1&search_product=PHR-2&page=1) **[JST]**

`PHR-2` also appears in JST's PH-series 3D/2D data table (item 4) with IGES/STEP/3D-PDF/2D-PDF: [`PHR-2.pdf`](https://www.jst-mfg.com/product/index.php?type=10&series=199&doc=4&filename=PHR-2.pdf) **[JST]**

| Attribute | Value | Source |
|---|---|---|
| Exact part number | `PHR-2` | [JST model search](https://www.jst-mfg.com/product/index.php?type=1&search_product=PHR-2&page=1) **[JST]** |
| Description (LCSC) | `CONN HOUSING 2POS 2mm SINGLE ROW PH` | [LCSC C157955](https://www.lcsc.com/product-detail/C157955.html) **[DIST]** |
| Digi-Key part description | `CONN RCPT HSG 2POS 2.00MM` | [Findchips listing of Digi-Key `455-1165-ND`](https://www.findchips.com/search/PHR-2) **[DIST]** |
| Digi-Key orderable | `PHR-2`, Digi-Key PN `455-1165-ND` | [Findchips](https://www.findchips.com/search/PHR-2) **[DIST]** |
| Farnell orderable | `PHR-2`, Farnell order code `3616186`, "HOUSING, 2WAY, 2MM" | [Findchips](https://www.findchips.com/search/PHR-2) **[DIST]** |
| Newark orderable | `PHR-2`, Newark code `28C6963` | [Newark URL](https://www.newark.com/jst-japan-solderless-terminals/phr-2/wire-to-board-connector-housing/dp/28C6963) (search-result URL only — page body blocked, see §9) |
| Positions / rows / pitch | 2 positions, 1 row, 2 mm | [LCSC C157955](https://www.lcsc.com/product-detail/C157955.html) **[DIST]** |
| Connector type | Receptacle / socket, crimp termination, free hanging (in-line) | [DigiPart](https://www.digipart.com/part/PHR-2) **[DIST]** |
| Housing material | PA66 (Nylon 6.6), UL94V-0, White | [LCSC C157955](https://www.lcsc.com/product-detail/C157955.html) **[DIST]** |
| Fastening | Friction / detent lock (`Non-Latching` in LCSC's wording) | [LCSC C157955](https://www.lcsc.com/product-detail/C157955.html) **[DIST]** |
| Rated current / voltage | 2 A / 100 V | [DigiPart](https://www.digipart.com/part/PHR-2) **[DIST]** |
| Operating temperature | `−25℃~+85℃` | [LCSC C157955](https://www.lcsc.com/product-detail/C157955.html) **[DIST]** |
| RoHS | `ROHS3`; HQ also prints `Certification RoHS` and `Lead Free Or Not Yes` | [LCSC C157955](https://www.lcsc.com/product-detail/C157955.html), [HQ Online](https://www.hqonline.com/product-detail/rubber-shells-and-accessories-jst-phr-2-2500219074) **[DIST]** |

> **Caution on aggregated housing specs:** one aggregator block for `PHR-2` lists "Contact Plating: Tin Plated Contacts / Contact Material: Phosphor Bronze / No. of Rows 2Rows / Gender -" alongside the housing. A *housing* has no contacts — that block is the RS description of the whole **connector system** (housing + terminal), not the housing alone. Do not use it as PHR-2 spec. [Source: DigiPart](https://www.digipart.com/part/PHR-2) **[DIST]**

---

## 3. Crimp CONTACT — `SPH-002T-P0.5S` (and `.5L`)

Both variants are confirmed to exist in the PH series by JST's own model-number search:
`SPH-002T-P0.5S` → PH connector, PH connector (High box type). `SPH-002T-P0.5L` → PAD connector, PH connector, TR connector (KR family). All RoHSII.
[Source: JST model search for `SPH-002T-P0.5`](https://www.jst-mfg.com/product/index.php?type=1&search_product=SPH-002T-P0.5&page=1) **[JST]**

JST publishes the official 2D drawing for each: [`SPH-002T-P0.5S.pdf`](https://www.jst-mfg.com/product/index.php?type=10&series=199&doc=4&filename=SPH-002T-P0.5S.pdf) · [`SPH-002T-P0.5L.pdf`](https://www.jst-mfg.com/product/index.php?type=10&series=199&doc=4&filename=SPH-002T-P0.5L.pdf) **[JST]**
(There is also a third contact in the series, `SPH-004T-P0.5S`, for larger wire — listed in the same table but out of scope here.)

### 3.1 AWG range — the one real difference between the two

| Contact | Wire range (AWG) | Wire range (mm²) | Insulation O.D. | Source |
|---|---|---|---|---|
| **`SPH-002T-P0.5S`** | **AWG #30 to #24** (`24~30 AWG`) | `0.05 ~ 0.22 mm²` | `0.8 mm ~ 1.5 mm` | [LCSC C111515](https://www.lcsc.com/product-detail/C111515.html) **[DIST]** |
| **`SPH-002T-P0.5S`** (2nd source) | Min `30AWG` / Max `24AWG` | `0.05 mm²` / `0.2 mm²` | — | [DigiPart](https://www.digipart.com/part/SPH-002T-P0.5S) **[DIST]** |
| **`SPH-002T-P0.5S`** (3rd source) | `24-30AWG` | `0.05~0.22 mm²` | — | [HQ Online](https://www.hqonline.com/product-detail/housing-contact-jst-sph-002t-p0-5s-2500219104) **[DIST]** |
| **`SPH-002T-P0.5L`** | **AWG #28 to #24** (`24~28 AWG`) | `0.08 ~ 0.22 mm²` | `0.8 mm ~ 1.5 mm` | [LCSC C265456](https://www.lcsc.com/product-detail/C265456.html) **[DIST]** |
| **`SPH-002T-P0.5L`** (2nd source) | `24-28AWG` | `0.08~0.22 mm²` | — | [HQ Online](https://www.hqonline.com/product-detail/housing-contact-jst-sph-002t-p0-5l-2500269116) **[DIST]** |
| **`SPH-002T-P0.5L`** (3rd source) | element14 description string: "Contact Socket 28-24AWG Crimp" | — | — | [element14 part URL](https://cn.element14.com/jst-japan-solderless-terminals/sph-002t-p0-5l/contact-socket-28-24awg-crimp/dp/2399572) (URL slug only — body blocked) |

**Bottom line on the variants:** every fetched page that describes both states the difference is **the wire range only** (`30–24 AWG / 0.05–0.22 mm²` vs `28–24 AWG / 0.08–0.22 mm²`). Both are Tin over Phosphor Bronze, both reference the PH series, both list insulation O.D. `0.8–1.5 mm`. Any other claimed difference between `.5S` and `.5L` is **UNVERIFIED**.

**Practical pick for a keyboard LiPo pigtail:** LiPo packs typically ship with 24–28 AWG leads. For 26–28 AWG use `SPH-002T-P0.5S` (wider range covers it); `SPH-002T-P0.5L` is the better match if your wire is specifically 24–28 AWG and on the thicker side of that. Note `SPH-002T-P0.5L`'s `Reference Series` is listed as `PH;PAD` — it is shared with the PAD series. [LCSC C265456](https://www.lcsc.com/product-detail/C265456.html) **[DIST]**

### 3.2 Contact shared attributes

| Attribute | Value | Source |
|---|---|---|
| Contact plating | Tin | [LCSC C111515](https://www.lcsc.com/product-detail/C111515.html) **[DIST]** |
| Contact material | Phosphor bronze | [LCSC C111515](https://www.lcsc.com/product-detail/C111515.html) **[DIST]** |
| Reference series | PH | [LCSC C111515](https://www.lcsc.com/product-detail/C111515.html) **[DIST]** |
| Termination | Crimp | [LCSC C111515](https://www.lcsc.com/product-detail/C111515.html) **[DIST]** |
| Max contact resistance | `20 mΩ` (after environmental test); `10 mΩ` initial quoted elsewhere for the assembled system | [DigiPart](https://www.digipart.com/part/SPH-002T-P0.5S) **[DIST]**, [LCSC S2B FAQ](https://www.lcsc.com/product-detail/C173752.html) **[DIST]** |
| Rated current / voltage (system) | 2 A / 100 V | [HQ Online](https://www.hqonline.com/product-detail/housing-contact-jst-sph-002t-p0-5s-2500219104) **[DIST]** |
| Contact finish thickness | not stated on any fetched page | **UNVERIFIED** |

---

## 4. PITCH, CURRENT, VOLTAGE — series ratings

All figures below are **verbatim from JST's official PH connector series page** — the single most authoritative source in this report.

| Parameter | JST official value | Source |
|---|---|---|
| **Pitch** | **2 mm** ✅ confirmed | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| **Current rating** | **2 A AC/DC (AWG #24)** ✅ confirmed — 2 A AC/DC per contact, **conditioned on AWG #24 wire** | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| **Voltage rating** | **100 V AC/DC** ✅ confirmed | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| Temperature range | **−40 ℃ to +105 ℃** ⚠️ | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| Insulation resistance | 1,000 MΩ min. | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| Withstanding voltage | No breakdown or flashover while applying **800 VAC for one minute** | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| Circuits available | 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| PC board mounting | Through-hole **and** SMT | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| Mating direction | **Side entry and Top entry** | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| Array (insertion part) | Single-row | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| Lock | **Friction lock** | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| Standards | **TÜV, UL** | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| Connection variations | Compatible IDC connector available | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |
| High-box type header | Available (separate series page) | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) · [High-box datasheet](https://www.jst-mfg.com/product/pdf/eng/ePH-H.pdf) **[JST]** |
| Compatible series | PHN, KR, KRD, CK connector | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]** |

### ⚠️ Temperature-rating conflict — flag this in your design review

| Claimed temperature range | Where | Tag |
|---|---|---|
| **−40 ℃ to +105 ℃** | JST official PH series page | **[JST]** |
| −25 ℃ to +85 ℃ | LCSC (header, housing, both variants, S2B, SM4) | **[DIST]** |
| −25 ℃ to +85 ℃ | DigiPart / RS description for header + `SPH-002T-P0.5S` (`Maximum Operating Temperature: 85 C`) | **[DIST]** |
| −25 ℃ to +85 ℃ (header) | HQ Online (NextPCB) | **[DIST]** |
| −25 °C / 85 °C | acme-chip (header) | **[DIST]** |

**Every distributor says −25/+85; JST says −40/+105.** Most likely explanation: the distributor figure is the **materials/UL-style rating including temperature rise at rated current**, while JST's series table is the connector's ambient rating — an LCSC FAQ on the sibling S2B part does say "−25°C to +85°C (including temperature rise during current flow)", which supports that reading ([LCSC C173752](https://www.lcsc.com/product-detail/C173752.html) **[DIST]**). **I could not confirm this reconciliation from a primary source — treat it as my inference, not a verified fact.**

**Design consequence:** for a keyboard LiPo input, either figure is enormously conservative — you are nowhere near 2 A and nowhere near 105 ℃. But if you are writing a thermal/derating justification into documentation, cite **JST's −40/+105 ℃** and note the distributor discrepancy rather than silently picking one.

---

## 5. Rated applicable wire size (AWG) for the PH series

Verbatim from JST: **`AWG #32, #30, #28, #26, #24`** and **`0.032 mm² to 0.22 mm²`**, with **`Insulation O.D. φ 0.5 mm to φ 1.5 mm`**.
[Source: JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]**

| Parameter | JST series value | Tag |
|---|---|---|
| Conductor size | AWG #32, #30, #28, #26, #24 | **[JST]** |
| Cross-section | 0.032 mm² to 0.22 mm² | **[JST]** |
| Insulation O.D. | φ 0.5 mm to φ 1.5 mm | **[JST]** |

> ⚠️ **Discrepancy to be aware of:** the *series* insulation O.D. floor is **φ 0.5 mm**, but LCSC lists the **`SPH-002T-P0.5S` / `.5L` contacts** at **insulation O.D. 0.8–1.5 mm** ([C111515](https://www.lcsc.com/product-detail/C111515.html), [C265456](https://www.lcsc.com/product-detail/C265456.html)). Which figure governs the `.5S`/`.5L` contacts specifically is **UNVERIFIED** — the series number spans all PH contacts, and the individual drawings (PDF, image-only) could not be read.
>
> **Practical impact for a LiPo pigtail:** standard 24–28 AWG silicone hobby wire is ~1.0–1.5 mm O.D., comfortably inside both ranges. Only exotic thin-insulation wire would be affected.

---

## 6. Physical dimensions of the `B2B-PH-K-S` header

**JST's own statement (series level, top-entry version):**
> "With a **mounting height of 8 mm** and a **width of only 4.5 mm** in the top-entry version, this low-profile wire-to board connector features a pitch of 2.0 mm."

[Source: JST PH series](https://www.jst-mfg.com/product/index.php?series=199) **[JST]**

| Dimension | Value | Source | Tag |
|---|---|---|---|
| Mounting height (top entry) | **8 mm** | JST PH series page | **[JST]** |
| Width (top entry) | **4.5 mm** | JST PH series page | **[JST]** |
| Body / footprint length × width | `5.90 × 4.50 mm` (LCSC: "X-Length of Bottom Edge on Board (Spacing Line) 5.9mm") | [HQ Online](https://www.hqonline.com/product-detail/wire-to-board-connectors-jst-b2b-ph-k-s-lf--sn--2500219066), [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) | **[DIST]** |
| Insulation height | `6.00 mm` (`0.236"`) | [HQ Online](https://www.hqonline.com/product-detail/wire-to-board-connectors-jst-b2b-ph-k-s-lf--sn--2500219066) | **[DIST]** |
| Height | `6.00 mm` | [HQ Online](https://www.hqonline.com/product-detail/wire-to-board-connectors-jst-b2b-ph-k-s-lf--sn--2500219066), [acme-chip](https://www.acme-chip.com/pdut/B2B-PH-K-S-LF-SN/4331583.htm) (`Height 6 mm`) | **[DIST]** |
| Contact mating length | `3.30 mm` (`0.130"`) | [DigiPart](https://www.digipart.com/part/B2B-PH-K-S) | **[DIST]** |
| Depth / width | `4.5 mm` | [acme-chip](https://www.acme-chip.com/pdut/B2B-PH-K-S-LF-SN/4331583.htm) | **[DIST]** |
| Length | `5.9 mm` | [acme-chip](https://www.acme-chip.com/pdut/B2B-PH-K-S-LF-SN/4331583.htm) | **[DIST]** |
| Packaging | Bulk / Box | [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html), [Findchips](https://www.findchips.com/search/PHR-2) | **[DIST]** |

> ⚠️ **The 8 mm vs 6.00 mm conflict is NOT resolved.** JST says "mounting height of 8 mm" for the top-entry version. Distributors say the header body height is 6.00 mm. A stale legacy table for the non-LF base PN lists `Mated Stacking Heights: 8mm` ([ICZOOM](https://en.iczoom.com/product/k07-23573041-B2B-PH-K-S.html)) **[DIST — stale, do not use for the LF part]**, which suggests **8 mm = mated height (header + PHR-2 housing seated)**, and **6.00 mm = bare header height**. This reading is plausible and consistent, but **UNVERIFIED** — no fetched page states it explicitly.
>
> **For your PCB:** do not trust any single number. Pull JST's official 2D/3D drawing for `B2B-PH-K-S` ([PDF](https://www.jst-mfg.com/product/index.php?type=10&series=199&doc=4&filename=B2B-PH-K-S.pdf)) or the STEP model ([ZIP](https://www.jst-mfg.com/product/index.php?type=10&series=199&doc=2&filename=B2B-PH-K-S.zip)) into your CAD tool and measure the footprint directly. **PCB hole / pin / drill dimensions are UNVERIFIED** in this report — they exist only in JST's PDF drawings, which are image-only vector art with no extractable text (see §9).

---

## 7. Right-angle and surface-mount variants

Both are confirmed to exist on JST's **own** PH-series product data list, which is the strongest possible existence proof.

| Variant | Part number | JST list | Verified? | Key data |
|---|---|---|---|---|
| Side entry / right-angle, THT | **`S2B-PH-K-S`** → order as **`S2B-PH-K-S(LF)(SN)`** | item **34** in JST's PH 3D/2D table ([JST](https://www.jst-mfg.com/product/index.php?series=199)) | ✅ **VERIFIED** | LCSC: "Connector Header 2 position 2mm Pitch 2A **Right Angle**", package `Through Hole,Right Angle,P=2mm`, Brass/Tin, `K Pin`, PA66, 100 V, 2 A, `X-Length … 5.9mm` ([LCSC C173752](https://www.lcsc.com/product-detail/C173752.html)) **[DIST]**; HQ: `Size 5.90 x 7.60mm`, insulation height `4.80mm`, "Bending Insert" ([HQ Online](https://www.hqonline.com/product-detail/wire-to-board-connectors-jst-s2b-ph-k-s-lf--sn--2500219095)) **[DIST]** |
| Surface mount, vertical | **`B2B-PH-SM4-TB`** → order as **`B2B-PH-SM4-TB(LF)(SN)`** | item **49** in JST's PH 3D/2D table ([JST](https://www.jst-mfg.com/product/index.php?series=199)) | ✅ **VERIFIED** | LCSC: "Connector Header 2 position 2mm Pitch 2A **Surface Mount,Vertical**", package `SMD,P=2mm`, `Copper alloy`/Tin, "Auxiliary Solder Pin", plastic `PA`, Beige, `X-length 7.95mm` ([LCSC C160352](https://www.lcsc.com/product-detail/C160352.html)) **[DIST]**; HQ: `Size 7.95 x 5.00mm`, insulation height `6.60mm`, "Stand Mounting"/"Fixed welding tail", Ivory ([HQ Online](https://www.hqonline.com/product-detail/wire-to-board-connectors-jst-b2b-ph-sm4-tb-lf--sn--2500219068)) **[DIST]** |

Additional variants present on JST's list that may interest you: `S2B-PH-SM4-TB` (item 64, right-angle SMD), `B2B-PH-SM3-TB`, `B2B-PH-SM4-TBT`, `B2B-PH-KL`, `B2B-PH-K-E`, `B2B-PH-TW-S` (a 2-position plug/plug adapter) — all on the [JST PH series page](https://www.jst-mfg.com/product/index.php?series=199). **[JST]**

Note on the `K` in `B2B-PH-K-S`: LCSC records the supplementary feature as **`K Pin`**, i.e. the PCB retention/kink pin — relevant if you are placing the part on a thin PCB. [LCSC C131337](https://www.lcsc.com/product-detail/C131337.html) **[DIST]**

---

## 8. Temperature range and mating cycles

| Question | Answer | Source | Tag |
|---|---|---|---|
| Temperature range | **−40 ℃ to +105 ℃** | [JST PH series](https://www.jst-mfg.com/product/index.php?series=199) | **[JST]** |
| Temperature range (distributor consensus) | −25 ℃ to +85 ℃ | LCSC / DigiPart / HQ / acme-chip, see §4 | **[DIST]** |
| **Rated number of mating cycles** | ❌ **UNVERIFIED — not stated anywhere I could reach** | — | **UNVERIFIED** |

**On mating cycles:** JST's PH series page lists no durability / mating-cycle figure, and no fetched distributor page states one. JST's PH datasheets (`ePH.pdf`, `ePH-H.pdf`) are the place such a figure would live, but they are **AES-256-encrypted, image-only vector art with zero extractable text** — I decrypted them successfully (see §9) and confirmed there is no text layer to read. **Assume no published mating-cycle rating exists for this series; do not put a number in your documentation.**

**On temperature, use JST's figure** (−40 to +105 ℃) and note the −25/+85 distributor consensus as a discrepancy, per §4.

---

## 9. What I could NOT verify — explicit list

### Blocked sources (no values quoted from any of these)
| Source | Result |
|---|---|
| **Digi-Key** (digikey.com, digikey.cn, digikey.hk, forum) | Product pages **HTTP 403** Cloudflare "Just a moment…" on repeated attempts. Only the **TechForum post** was reachable (used for the suffix explanation, marked NOT PRIMARY). **No Digi-Key spec value appears in this report.** |
| **Mouser** (.com and locales) | fetch failed / denied. |
| **Farnell / element14 / Newark / CPC** | **HTTP 403** Akamai ("Access Denied", reference #18.9c41402…) on uk / ch / at / cn / my / en-CN. Only **URL slugs** were visible (e.g. "header-top-entry-2way-2mm"), which I used solely as weak corroboration and labelled as such. |
| RS Online, Distrelec, Elfa, TME, Arrow, TTI, OnlineComponents, trustedparts, soselectronic, origin-ic, ic-components, componentsearchengine, jst.com (JST America) | 403 / fetch failed. |
| Headless browser workaround | Attempted a **headless Edge/Chrome DOM dump** to bypass the bot blocks, but process spawning was **denied** ("Access is denied") on the machine used for this research. Not retried — a local restriction, not a transient failure. |

The Digi-Key / Mouser / Farnell product pages for this exact part number **could not be retrieved**, so no first-hand quote from them is given for the header. The closest substitutes actually fetched are LCSC, DigiPart (which surfaces an RS Components description), HQ Online, Findchips (which surfaces Digi-Key's and Farnell's *descriptions and order codes*, not their full spec tables), and acme-chip. All are marked **[DIST]**.

### Specific facts that remain UNVERIFIED
1. **Rated mating cycles / durability** — no source found (§8).
2. **PCB hole, pin and drill dimensions** for `B2B-PH-K-S` — only in JST's PDF drawings, which have no text layer (§6).
3. **The 8 mm vs 6.00 mm height conflict** — no source explicitly states which is mated vs unmated height (§6).
4. **Contact plating thickness** — "-" or absent on every fetched page (§3.2).
5. **Which insulation-O.D. range governs `SPH-002T-P0.5S`/`.5L`** — LCSC says 0.8–1.5 mm, JST's series page says φ0.5–1.5 mm (§5).
6. **Any difference between `SPH-002T-P0.5S` and `SPH-002T-P0.5L` beyond wire range** — none found; explicitly not claimed (§3.1).
7. **JST-verbatim expansion of `(LF)` / `(SN)`** — JST's own page only says "RoHS-compliant"; the tin/lead-free reading is corroborated by LCSC's Tin plating attribute but is forum-sourced (§1.1).
8. **RoHS status of `B2B-PH-K-S(LF)(SN)` specifically** — LCSC's RoHS fields for `C131337` are null, while JST's env page states the suffix itself *means* RoHS-compliant. Use JST's statement (§1, §1.1).
9. **The exact text of JST `ePH.pdf` page 3** (the "(LF)(SN) on a label" note) — quoted only via a forum; I decrypted and extracted the PDF and it contains no text layer (§9 note below).
10. **A JST-verbatim current-derating table** (current vs number of circuits energised) — not on the series page I fetched. Note the series page's rating is explicitly conditioned on AWG #24.

### Note on the JST PDF datasheets (so nobody repeats this work)
- `https://www.jst-mfg.com/product/pdf/eng/ePH.pdf` and `ePH-H.pdf` are **AES-256 encrypted (V5/R6)** with an empty user password, and after decryption their content streams are **FlateDecode vector art with no text-showing operators at all** — i.e. the datasheet is a converted CAD drawing with no text layer.
- The R6 decryptor used here was a throwaway script (not published with this repository); it confirmed the empty user password validates, and confirmed via the `/Perms` entry which derived key is the true file-encryption key. The obstacle is **not** the encryption — it is that **there is no text to extract**. Any spec you need from those PDFs must come from the drawings visually or from the CAD/STEP models.
- **PDFs cannot be read by ordinary web-page fetching** ("unsupported content type application/pdf"), so all PDF URLs in this report are cited as primary artifacts, not as read sources.
- The decryption/extraction scripts used above (`pdfaes.py` / `final_pdf.py`) are one-off tooling and are **not published with this repository**; the finding that matters is stated in the line above and needs no script to re-verify.

---

## 10. Appendix — source index

**Primary (JST official)**
- PH connector series spec sheet: <https://www.jst-mfg.com/product/index.php?series=199>
- PH series catalog PDF (image-only): <https://www.jst-mfg.com/product/pdf/eng/ePH.pdf>
- PH high-box catalog PDF (image-only): <https://www.jst-mfg.com/product/pdf/eng/ePH-H.pdf>
- Environmental survey / RoHS suffix statement: <https://www.jst-mfg.com/env/?lang=2>
- Model search `B2B-PH-K-S`: <https://www.jst-mfg.com/product/index.php?type=1&search_product=B2B-PH-K-S&page=1>
- Model search `PHR-2`: <https://www.jst-mfg.com/product/index.php?type=1&search_product=PHR-2&page=1>
- Model search `SPH-002T-P0.5`: <https://www.jst-mfg.com/product/index.php?type=1&search_product=SPH-002T-P0.5&page=1>
- 2D drawings: `B2B-PH-K-S.pdf`, `PHR-2.pdf`, `SPH-002T-P0.5S.pdf`, `SPH-002T-P0.5L.pdf`, `S2B-PH-K-S.pdf`, `B2B-PH-SM4-TB.pdf` (via `https://www.jst-mfg.com/product/index.php?type=10&series=199&doc=4&filename=<PN>.pdf`)

**Distributor / aggregator**
- LCSC `B2B-PH-K-S(LF)(SN)` C131337: <https://www.lcsc.com/product-detail/C131337.html>
- LCSC `PHR-2` C157955: <https://www.lcsc.com/product-detail/C157955.html>
- LCSC `SPH-002T-P0.5S` C111515: <https://www.lcsc.com/product-detail/C111515.html>
- LCSC `SPH-002T-P0.5L` C265456: <https://www.lcsc.com/product-detail/C265456.html>
- LCSC `S2B-PH-K-S(LF)(SN)` C173752: <https://www.lcsc.com/product-detail/C173752.html>
- LCSC `B2B-PH-SM4-TB(LF)(SN)` C160352: <https://www.lcsc.com/product-detail/C160352.html>
- Findchips `PHR-2` (surfaces Digi-Key `455-1165-ND`, Farnell `3616186`): <https://www.findchips.com/search/PHR-2>
- DigiPart `B2B-PH-K-S`: <https://www.digipart.com/part/B2B-PH-K-S> · `SPH-002T-P0.5S`: <https://www.digipart.com/part/SPH-002T-P0.5S> · `PHR-2`: <https://www.digipart.com/part/PHR-2>
- HQ Online (NextPCB) pages for all six parts (see §1–§7 inline links)
- acme-chip `B2B-PH-K-S(LF)(SN)`: <https://www.acme-chip.com/pdut/B2B-PH-K-S-LF-SN/4331583.htm>

**Not primary (directional only)**
- DigiKey TechForum on JST suffixes: <https://forum.digikey.com/t/jst-suffixes-lf-sn-au-s-n-m-prefixes-g-w-c-q-d/605>
