# USB-C receptacle — verified facts (device-side / UFP, charging + USB 2.0 data, 5.1 kΩ CC pulldowns)

All spec quotes below are from **USB Type-C® Cable and Connector Specification, Release 2.4 (October 2024), 439 pp.**
I downloaded the PDF and extracted its text locally (PDF text extraction, printed page numbers given). Copy read:
`https://community.infineon.com/gfawx74859/attachments/gfawx74859/USBEZPDTypeC/10790/1/USB%20Type-C%20Spec%20R2.4%20-%20October%202024.pdf`
Official landing page (points to the USB-IF Document Library): `https://www.usb.org/usb-type-cr-cable-and-connector-specification`
Local artifacts for re-grepping (not committed): `research/usbc-spec-r2.4.pdf` / `research/usbc-spec-r2.4.txt`

---

## 1. Connector parts

**Pin map of a 16P USB 2.0 Type-C receptacle** (identical in every 16P part below — GCT's own drawing lists it pin by pin):
A1 GND, A4 VBUS, A5 CC1, A6 Dp1, A7 Dn1, A8 SBU1, A9 VBUS, A12 GND, B1 GND, B4 VBUS, B5 CC2, B6 Dp2, B7 Dn2, B8 SBU2, B9 VBUS, B12 GND, plus SHELL.
→ **16 contacts = 4×VBUS + 4×GND + CC1/CC2 + 2×SBU + 4×USB 2.0 data.** SBU1/SBU2 (A8/B8) exist on the 16P part and stay **NC** for USB 2.0. Source: GCT drawing, p.1 pin table — https://gct.co/files/drawings/usb4105.pdf

| Part | Brand (as listed by LCSC) | LCSC | Contacts | Mount | SMD vs THT | KiCad symbol | KiCad footprint | EasyEDA |
|---|---|---|---|---|---|---|---|---|
| `TYPE-C-31-M-12` | Korean Hroparts Elec (HRO) | [C165948](https://www.lcsc.com/product-detail/C165948.html) | **16P** ("CONN RCPT Type-C 16POS SMD") | **Surface-mount, right-angle = top-mount** ([LCSC](https://www.lcsc.com/product-detail/C165948.html)); HRO's own page: "8.94×7.35×3.16 mm 通用型 **16P（表面贴装式）**TYPE-C接口", DC 20 V 5 A, 10 000 cycles ([krhro.com](https://www.krhro.com/Product-Details/726.html)) | **Hybrid: SMD contacts + through-hole shell stakes.** Official KiCad footprint has 16 `smd roundrect` pads (A1,A4,A5,A6,A7,A8,A9,A12,B1,B4,B5,B6,B7,B8,B9,B12) on F.Cu, **4 `thru_hole oval` pads named `SH`** (shell), 2 non-plated Ø0.65 mm locating holes, `(attr smd)` — [raw .kicad_mod](https://gitlab.com/api/v4/projects/21601606/repository/files/Connector_USB.pretty%2FUSB_C_Receptacle_HRO_TYPE-C-31-M-12.kicad_mod/raw?ref=master) | `Connector:USB_C_Receptacle_USB2.0_16P` — descr. "USB 2.0-only 16P Type-C Receptacle connector" ([raw .kicad_sym](https://gitlab.com/api/v4/projects/21545491/repository/files/Connector.kicad_symdir%2FUSB_C_Receptacle_USB2.0_16P.kicad_sym/raw?ref=master)) | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` (official lib; footprint `descr` links the HRO drawing) | LCSC page shows "EDA Models → EasyEDA"; model verified via EasyEDA API: title `TYPE-C-31-M-12`, uuid `df8405e2fa0e40a984c435ad4c8d5cf3`, owner LCSC ([API](https://easyeda.com/api/products/C165948/components)) |
| `GT-USB-7010ASV` | **G-Switch** — *not* GCT | [C2988369](https://www.lcsc.com/product-detail/C2988369.html) | **16P** | SMD, Right Angle, center height 1.68 mm, 24 V ([LCSC](https://www.lcsc.com/product-detail/C2988369.html)) | Hybrid (same structure: 16 SMD signal pads + 4 `SH` thru-hole stakes) | use the 16P symbol above | `Connector_USB:USB_C_Receptacle_G-Switch_GT-USB-7010ASV` (descr "USB Type C, right-angle, SMT", datasheet = LCSC C2988369) — [raw .kicad_mod](https://gitlab.com/api/v4/projects/21601606/repository/files/Connector_USB.pretty%2FUSB_C_Receptacle_G-Switch_GT-USB-7010ASV.kicad_mod/raw?ref=master) | EasyEDA model offered by LCSC (page shows "EDA Models → EasyEDA") |
| `USB4105-xx-A` | **GCT** (Global Connector Technology) — the real GCT 16P part | (GCT direct; dist. Newark `USB4105-GF-A`) | **16P** | "USB Type C Receptacle for USB 2.0 — **SMT Type, PCB Top Mount**" ([GCT drawing p.1](https://gct.co/files/drawings/usb4105.pdf)) | SMT contacts; **shell stake length selectable 0.95 / 0.60 / 1.20 mm** (through-hole stakes) | use the 16P symbol above | `Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` ([lib tree listing](https://gitlab.com/api/v4/projects/21601606/repository/tree?path=Connector_USB.pretty&per_page=100&ref=master)) | — |
| `KH-TYPE-C-16P` | kinghelm (Shenzhen Kinghelm) | [C709357](https://www.lcsc.com/product-detail/C709357.html) | **16P** ("CONN RCPT Type-C 16POS SMD R/A") | SMD, Right Angle ([LCSC](https://www.lcsc.com/product-detail/C709357.html)); distributor adds 8.94×7.55 mm, H=3.26 mm, "Horizontal Mounting" ([HQonline](https://www.hqonline.com/product-detail/usb-connectors-kinghelm-kh-type-c-16p-2500342682)) | not verified from a readable drawing (see UNVERIFIED) | use the 16P symbol above | **No official KiCad footprint.** KiCad's only "16P" third-party one is `USB_C_Receptacle_HCTL_HC-TYPE-C-16P-01A` (different brand, [listing](https://gitlab.com/api/v4/projects/21601606/repository/tree?path=Connector_USB.pretty&per_page=100&ref=master)) | EasyEDA model verified via [API](https://easyeda.com/api/products/C709357/components) (title `KH-TYPE-C-16P`, uuid `7083d9afdc7d4d24a2e54126331c8e1f`) |

Extra part facts worth having:
- **GCT USB4105 current ratings** (drawing p.1): "5.00 A collectively for VBUS pins", "6.25 A collectively for GND pins", 1.25 A for A5/B5, 20 000 mating cycles, 48 V DC, 240 W, shell pins labelled **SHELL = GND** — https://gct.co/files/drawings/usb4105.pdf
- **HRO ratings** (own page): DC 20 V / 5 A, contact resistance ≤50 mΩ, 10 000 cycles, 0.5–2.0 kgf — https://www.krhro.com/Product-Details/726.html
- **HRO is not mid-mount here**: HRO's 沉板 (mid-mount) 16P family is M-13 (0.8 mm) / M-14 (0.75 mm) / M-28; `TYPE-C-31-M-12` is listed as 表面贴装式 (surface mount) — https://www.krhro.com/product/1047166038679040000-32-16.html
- Kinghelm also sells a **mid-mount** 16-contact variant, `KH-TYPE-C-W.CB1.6-16P` ("沉板安装、16 触点") — https://www.kinghelm.com.cn/applicationDetail/16819
- Kinghelm markets `KH-TYPE-C-16P` specifically for dual-mode mechanical keyboards — https://www.kinghelm.com.cn/newDetail/16293

---

## 2. CC1 / CC2 for a UFP (sink) — exact values and what they mean

### 2.1 Rd value and tolerance
Spec Table 4-28 **Sink CC Termination (Rd) Requirements** (printed p. 244):

| Rd implementation | Nominal value | Can detect power capability? | Max voltage on pin |
|---|---|---|---|
| ± 20 % voltage clamp | 1.1 V | No | 1.32 V |
| ± 20 % resistor to GND | **5.1 kΩ** | **No** | 2.18 V |
| ± 10 % resistor to GND | **5.1 kΩ** | **Yes** | 2.04 V |

Notes to that table: "This is the total equivalent resistance into the Sink CC pin including all internal resistances." Source: https://community.infineon.com/gfawx74859/attachments/gfawx74859/USBEZPDTypeC/10790/1/USB%20Type-C%20Spec%20R2.4%20-%20October%202024.pdf (p. 244)

- **Both CC pins, independently**: "Both CC1 and CC2 pins shall be **independently** terminated to ground through Rd" (Attached/Unattached.SNK requirements) and "The port shall provide an Rd as specified in Table 4-28 on both the CC1 and CC2 pins"; the Sink functional model (Figure 4-9) is "The Sink terminates both CC1 and CC2 to GND using pull-down resistors" — same spec, pp. 165, 180, 210.
- **±10 % is the version you want** if you ever want >500 mA: Microchip AN1953 §3.2: "An upstream facing port must connect a valid **Rp pull-down** [sic] resistor to GND (or optionally, a voltage clamp) to both CC1 and CC2 pins. **A 5.1 kΩ ± 10 % is the only acceptable resistor if USB Type-C charging of 1.5 A @ 5 V or 3.0 A @ 5 V is to be used.**" — http://ww1.microchip.com/downloads/en/AppNotes/00001953A.pdf (p. 10–11). The ±20 % Rd cannot read the source's advertisement, so a ±20 %-Rd sink must stay at default current.
- Build with two separate 5.1 kΩ resistors, one per CC pin. Shorting CC1+CC2 is the classic failure (Raspberry Pi 4: with e-marked cables the charger sees Rd/Rd… and supplies 0 V) — https://people.kernel.org/bleung/how-to-design-a-proper-usb-c-power-sink-hint-not-the-way-raspberry-pi-4 (**blog → lower confidence**, but it reproduces spec Figure 4-9 / §4.5.1.3.2 and matches the spec text above).

### 2.2 Who advertises what (this is the part people get wrong)
**Rd never advertises anything.** Rd = 5.1 kΩ is a fixed sink termination: it tells the source "a sink is attached" and creates a divider so the *sink* can read vRd. The **source's Rp** advertises capability. Spec §4.6.2.1: "The Source adjusts Rp (or current source) to advertise which of the three current levels it supports… **The value of Rp establishes a voltage (vRd) on CC that is used by the Sink to determine the maximum current it may draw.**" (p. 227)

Spec Table 4-27 **Source CC Termination (Rp) Requirements** (p. 243):

| Source advertisement | Current source to 1.7–5.5 V | Resistor pull-up to 4.75–5.5 V | Resistor pull-up to 3.3 V ± 5 % |
|---|---|---|---|
| Default USB Power | 80 µA ± 20 % | **56 kΩ ± 20 %** (56 kΩ ± 5 % inside cable plugs) | 36 kΩ ± 20 % |
| **1.5 A @ 5 V** | 180 µA ± 8 % | **22 kΩ ± 5 %** | 12 kΩ ± 5 % |
| **3.0 A @ 5 V** | 330 µA ± 8 % | **10 kΩ ± 5 %** | 4.7 kΩ ± 5 % |

So: **a 5 V/3 A-capable source advertises with Rp = 10 kΩ** (or 330 µA) — there is no "3 A Rd". Your device's Rd stays 5.1 kΩ in all cases.

### 2.3 What a UFP with Rd = 5.1 kΩ may draw
- By default (source advertising Default USB Power): **500 mA for USB 2.0**, 900 mA for USB 3.2 single-lane, 1 500 mA for USB 3.2 dual-lane. Spec Table 4-20 & §4.6.2.1 (pp. 226–227): "Default is the as-configured for high-power operation current value as defined by the USB Specification (500 mA for USB 2.0 ports; 900 mA or 1 500 mA for USB 3.2 ports…)". A keyboard with a 16P USB 2.0 receptacle is a USB 2.0 device ⇒ **500 mA** budget (100 mA before configuration comes from USB 2.0 itself, not verified here).
- Sink power sub-states (§4.5.2.3, pp. 200–202): `PowerDefault.SNK` → "shall draw no more than the default USB power from VBUS"; `Power1.5.SNK` → "shall draw no more than **1.5 A** from VBUS"; `Power3.0.SNK` → "shall draw no more than **3.0 A** from VBUS".
- The sink must track the advertisement: "A Sink that takes advantage of the additional current offered (e.g., 1.5 A or 3.0 A) shall **monitor the CC pins** and shall adjust its current consumption within tSinkAdj to remain **within the value advertised by the Source**." (p. 227)
- ⇒ **Correct statement:** with Rd = 5.1 kΩ on both CC pins your device may draw up to **3 A only from a source that is actually advertising 3 A** (Rp = 10 kΩ / 330 µA); from a 1.5 A-advertising source it is capped at 1.5 A; from a default source 500 mA (USB 2.0). The 5.1 kΩ Rd enables it; it does not cause it.
- If you implement Rd as a **±10 %** resistor you can *detect* the level (needed to legally use it). Sink-side detection windows, Table 4-36 (Rd ± 10 %, p. 252): vRd-USB **0.277–0.612 V**, vRd-1.5 **0.746–1.164 V**, vRd-3.0 **1.369–2.042 V**, connect/disconnect threshold 2.043 V. If you only ever want 500 mA, a plain ±20 % 5.1 kΩ resistor pair is sufficient and legal — but then you must **not** draw more than default.
- Cross-check, manufacturer: TI TUSB320 datasheet §7.3.2 "Type-C Current Mode" — default advertisement 500 mA (USB 2.0) / 900 mA (USB 3.1), medium 1.5 A, high 3 A; UFP mode "constantly presents pulldown resistors (Rd) on both CC pins" and reads the DFP's advertisement — https://www.ti.com/document-viewer/TUSB320/datasheet/GUID-3BF156CA-3E11-436F-8D41-07D491DBA492 and …/GUID-162A538F-935C-45CA-AAD3-38C04C82CA2B ; TI's own Rd spec: "RCC_D Pulldown resistor when in UFP or DRP mode: 4.6 / **5.1** / 5.6 kΩ (min/typ/max)" = 5.1 kΩ ±10 % — https://www.ti.com/lit/ds/symlink/tusb320.pdf (§6.5)
- Microchip AN1953 Table 6/7 repeats the same Rp/Rd table (56 k/22 k/10 k; 5.1 kΩ ±10 %) — http://ww1.microchip.com/downloads/en/AppNotes/00001953A.pdf

---

## 3. VBUS pins, GND pins, decoupling

**Bus the pins — it is a spec requirement, not a style choice.** Spec §3.2.1 "Interface Definition", notes to Figure 3-1 (printed p. 47):

- Note 14: "**All VBUS pins shall be connected together at the USB Type-C receptacle when it is in its mounted condition (e.g., all VBUS pins bussed together in the PCB).**"
- Note 15: "**All Ground return pins shall be connected together at the USB Type-C receptacle when it is in its mounted condition (e.g., all Ground return pins bussed together in the PCB).**"
- (Notes 12/13 say the same for the plug.) Same text repeated in the connector tables, p. 67/69: "All VBUS pins shall be connected together within the USB Type-C plug and shall be connected together at the USB Type-C receptacle connector when the receptacle is in its mounted condition (e.g., all VBUS pins bussed together on the PCB)."
- Practical consequence for a 16P part: tie A4/A9/B4/B9 → VBUS, and A1/A12/B1/B12 → GND, as wide copper. (This also matches the connector's own ratings: VBUS contacts are rated 5 A *collectively*, GND 6.25 A collectively — GCT drawing, https://gct.co/files/drawings/usb4105.pdf)

**Decoupling (device side):**
- Manufacturer primary: TI TUSB320, Table 8-2 "USB2 Bulk Capacitance Requirements" — DFP: 120 µF min; **UFP: 1 µF min, 10 µF max**, and "When operating the TUSB320 device in an UFP mode, a bulk capacitance between 1 to 10 μF is required. In this particular case, a 1-µF capacitor was chosen." — https://www.ti.com/lit/ds/symlink/tusb320.pdf (§8.2, pp. 21–25; note the 100 nF caps in that design are on VDD, not VBUS)
- Spec side, the sink's pre-attach capacitance is capped: Table 4-3 VBUS Sink Characteristics — "VBUS Capacitance **10 µF** — Capacitance between VBUS and GND pins on receptacle when not in Attached.SNK" (p. 153). Related: Table 4-2 caps a DRP's unsourced VBUS capacitance at 10 µF (source-only ports 3000 µF), p. 152.
- Cable-side, not your PCB: legacy-adapter cable plugs are required to carry a **10 nF ± 20 %** VBUS/GND bypass capacitor ("A bypass capacitor is required between the VBUS and ground pins in the USB Type-C plug side of the cable. The bypass capacitor shall be 10nF ± 20 % …", spec Table 3-2/3-3 notes, pp. 63, 65, 68, 71). Useful only as a reminder that 10 nF is the *cable* value, not the receptacle value.
- Net: put **1–10 µF bulk (e.g. 4.7 µF or 10 µF) + a 0.1 µF at the receptacle VBUS pins**, keeping the total at the connector ≤10 µF before attach. The 0.1 µF HF bypass is standard practice, **not** something I found in the spec or in TI's text here (see UNVERIFIED).

---

## 4. Shell / shield grounding

- **Direct to PCB ground, per spec — no capacitor/resistor specified.** Spec §3.2.1 note 11 (p. 47): "**The receptacle shell shall be connected to the PCB ground plane.**" That is the only normative statement about the shell's grounding; a search of the whole spec text for "ferrite" and for shell+capacitor language found no requirement to isolate the shell via a capacitor or resistor.
- EMC guidance in the same document (§3.10.1, p. 145): "The receptacle shell **should** have sufficient connection points to the system PCB GND plane with apertures as small as possible… Figure 3-79 illustrates an example with multiple solder tails to connect the receptacle shell to system PCB GND", and "The receptacle connectors **should** be connected to metal chassis or enclosures through grounding fingers, screws, or any other way to manage EMC."
- The connector vendor treats the shell as a ground contact: GCT's USB4105 drawing lists `SHELL  GND` in both the A-side and B-side pin tables — https://gct.co/files/drawings/usb4105.pdf
- Bonus, same notes list: for full-featured receptacles a mid-plate is required and "The mid-plate shall be connected to the PCB ground with at least two grounding points" (note 2, p. 46). GCT's 16P part lists a stainless-steel mid plate, so its stakes/mid-plate are all GND-bound.
- ⇒ For this keyboard: tie all `SH` stakes (and the THT shell stakes in the KiCad footprint) straight to the GND plane with the shortest, widest connection you can. Isolating the shell through a cap/resistor is **not** required by the Type-C spec and I could not verify any primary source that asks for it (see UNVERIFIED).

---

## UNVERIFIED / lower confidence

1. **KH-TYPE-C-16P (Kinghelm) mount style & mechanics — NOT verified from a readable primary drawing.** Kinghelm's own datasheet PDF (https://www.kinghelm.net/upload/file/20220513/KH-TYPE-C-16P.pdf) is a 1-page **image-only** drawing: text extraction returned only "深圳市金航标电子有限公司 WWW.BDS666.COM / KH-TYPE-C-16P" — no dimensions, no pad data. Kinghelm's product page renders specs via JS (only the title "KH-TYPE-C-16P, USB Type-C Connector" was retrievable: https://www.kinghelm.net/productDetail/12239448). The 16P / SMD / R-A / 30 V figures come from **LCSC** ([C709357](https://www.lcsc.com/product-detail/C709357.html)) and the 8.94×7.55 mm / H 3.26 mm from a distributor ([HQonline](https://www.hqonline.com/product-detail/usb-connectors-kinghelm-kh-type-c-16p-2500342682)) → treat as **distributor-grade, lower confidence**; do not cut a board from it without the real drawing.
2. **HRO TYPE-C-31-M-12 mechanical drawing not read directly.** `krhro.com`'s datasheet PDF returned **HTTP 403** (both the vendor-embedded copy and the URL in KiCad's footprint `descr`), and LCSC's datasheet is also behind Cloudflare for direct fetches. The "16P / surface-mount / top-mount / pads + 4 shell stakes" conclusion rests on: HRO's own product page text (表面贴装式), LCSC parametric data ("Surface Mount, Right Angle"), and the **official KiCad footprint** pad layout. Cross-check against the HRO PDF before production.
3. **`GT-USB-7010ASV` is not a GCT part.** LCSC lists the manufacturer as **G-Switch** (Asian brand), and KiCad's footprint is named `..._G-Switch_GT-USB-7010ASV`. The task's premise "GT-USB-7010ASV (GCT)" is wrong. GCT's comparable part is **USB4105-xx-A** (verified from GCT's own drawing).
4. **Shell-to-ground via capacitor/resistor: no primary source found.** The Type-C spec requires a plain connection to the PCB ground plane (note 11); the "1 MΩ ∥ 4.7 nF" style shell isolation often quoted for USB is *not* established by anything I could fetch. The TI E2E thread "TUSB320EVM: Type-C Connector Shield/Shell Grounding Methods" (https://e2e.ti.com/support/interface-group/interface/f/interface-forum/1572741/tusb320evm-type-c-connector-shield-shell-grounding-methods) is Cloudflare-blocked (**HTTP 403**) from this environment — content unverified.
5. **HRO / Kinghelm "top mount vs mid-mount" wording**: both vendors sell several mechanically different 16P receptacles. Verified only that the *specific* parts above are described as surface-mount/R-A (HRO, Kinghelm) or "SMT Type, PCB Top Mount" (GCT); the mid-mount 16P variants have distinct part numbers (HRO M-13/M-14/M-28; Kinghelm KH-TYPE-C-W.CB1.6-16P / KH-TYPE-C-W.SMT-16P).
6. **USB 2.0 unconfigured 100 mA limit** — not verified in any source I fetched; not relied on above.
7. Spec version caveat: I read **Release 2.4 (Oct 2024)**. Rd/Rp values, the VBUS/GND bussing notes and the shell note are the same in earlier releases I could sample (Release 1.3 quotes seen in indexed copies), but if you must cite a specific compliance revision, cite R2.4 as read here.
