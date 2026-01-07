# DECIMAL TIME — Specification

Date: 2026-01-06

## Abstract

This document defines **Decimal Time**: a coherent, metric-aligned system of time units anchored to the planetary day (the *Astrocycle*, `AC`) and extended both downward (pure decimal subdivisions) and upward (counted astronomical cycles). The goal is a scientifically precise, human-friendly, and programmatically convenient specification suitable for computational use, UI displays, and scientific conversion.

---

## Design principles

1. **Single physical anchor** — the system is anchored to the mean solar day.
   - `1 Astrocycle (AC) = 1 mean solar day` (by definition for the system). For conversion to SI, 1 AC = 86,400 seconds.

1. **Pure decimal below the day** — every sub-day unit is an exact power-of-ten fraction of 1 AC. This ensures infinite divisibility and clean prefixing (kilo/mega/milli etc.).

2. **Counted cycles above the day** — astronomical units (year, millennium) are integer counts of AC. They are *not* exact decimal fractions of AC because astronomical periods are not integer powers of ten; instead they are represented as counts or averages and may carry ranges.

3. **Separation of concerns** — keep the day as the physical, timekeeping anchor; use decimalization for human/computational convenience. This mirrors SI thinking (physical constants and exact defined units vs. counted phenomena).

4. **Human legibility** — noon is exactly the midpoint of the day. In the canonical display, `50` (or `0.500`) denotes midday. No AM/PM ambiguity.

---

## Symbols and naming conventions

- `AC` — *Astrocycle* — base unit (1 day)
- Lowercase/uppercase prefix conventions follow SI-like prefixes adapted to the context: `MC` (Megacycle), `kC` (Kilocycle), `C` (Cycle), `mC` (Millicycle), `µC` (Microcycle), `nC` (Nanocycle), etc.
- Astronomical upward units use clear names: `SC` (Solar Cycle, ≈ 1 year), `StC` (Stellar Cycle, commonly 1_000 SC), `GC` (Galactic Cycle, commonly 1_000 StC), etc.
- When ambiguity exists, prefer explicit notation: `AC` for days, `SC(yr)` for solar cycles in years.

---

## Canonical sub-day unit table (exact)

All sub-day units are defined as exact decimal fractions of an Astrocycle (AC).

```csv
unit,symbol,meaning,base_unit_AC,seconds_per_unit
Astrocycle,AC,1 planetary day,1,86400
Megacycle,MC,1/100 AC,1e-2,864
Kilocycle,kC,1/1_000 AC,1e-3,86.4
Cycle,C,1/10_000 AC,1e-4,8.64
Decimillacycle,dmC,1/100_000 AC,1e-5,0.864
Centimillacycle,cmC,1/1_000_000 AC,1e-6,0.0864
Millicycle,mC,1/10_000_000 AC,1e-7,0.00864
Microcycle,µC,1/10_000_000_000 AC,1e-10,8.64e-06
Nanocycle,nC,1/10_000_000_000_000 AC,1e-13,8.64e-09

# (extendable: pico-, femto-, atto-, etc., via -3 or -10 exponents as desired)
```

Notes:
- The table intentionally mirrors SI prefix semantics but with decimal exponents chosen so that `100` Megacycles = `1` AC and `10_000` Cycles = `1` AC. You may extend the chain arbitrarily downward by multiplying exponents of ten.

---

## Day-level and upward cycles (counted units; approximate)

Astronomical cycles are integer counts of AC. Because the Earth's orbit and calendar mechanics include leap days and fractional tropical years, express these upward units as integer counts and optionally as averages or ranges.

```csv
unit,symbol,meaning,base_unit_AC,notes
Solar Cycle,SC,1 planetary orbit (year),~365.2422,average tropical year ≈ 365.2422 AC
Solar Cycle (integer),SCi,1 planetary orbit (year),365–366,calendar years (Julian/Gregorian) vary by leap rules
Decasolar Cycle,DaSC,10 SC,~3652.422,approx (10 × avg year)
Hectosolar Cycle,HSC,100 SC,~36524.22,approx
Kilosolar Cycle,kSC,1_000 SC,~365242.2,approx
Stellar Cycle,StC,1_000 SC,~365_000–366_000,nominal: 1_000 years as counted cycles
Galactic Cycle,GC,1_000 StC (1_000_000 SC),~3.65e8 AC,nominal: 1_000_000 years

# When precision matters, use Julian Day / Modified Julian Day or direct AC -> seconds conversion.
```

Recommendations:
- **For programmatic uses where a scalar is required**, use the astronomical average (e.g., 365.2422 AC per SC). Declare this explicitly.
- **For human/legal/registry uses**, use integer counts and calendar dates.

---

## Conversion rules

### AC ↔ SI (seconds)
```
1 AC = 86,400 s
1 s = 1 / 86,400 AC ≈ 1.1574074074074074e-5 AC
```

### Derived conversions (examples)
```
1 MC = 0.01 AC = 864 s = 14 min 24 s
1 kC = 0.001 AC = 86.4 s
1 C  = 0.0001 AC = 8.64 s
1 mC = 8.64 ms
1 µC = 8.64 µs
1 nC = 8.64 ns
```

### Speed of light (exact SI constant → Decimal Time)
Using `c = 299,792,458 m/s` and `1 AC = 86,400 s`:

```
c (meters per Astrocycle) = 299,792,458 * 86,400 ≈ 25,902,068,371,200 m/AC
c ≈ 2.59020683712 × 10^13 m/AC
```

Per common decimal subunits:
```
c ≈ 2.59020683712 × 10^11 m/MC
c ≈ 2.59020683712 × 10^10 m/kC
c ≈ 2.59020683712 × 10^9 m/C
c ≈ 2.5902068 × 10^6 m/mC
c ≈ 2.5902068 × 10^3 m/µC
c ≈ 2.5902068 m/nC
```

This shows a useful coincidence: **a nanocycle (`nC`) corresponds to ∼8.64 ns**, and light travels **~2.59 m** in that interval.

---

## Canonical display formats and human semantics

Two mutually-equivalent display approaches are valid. Choose one as your human UI convention.

1. **Percentage-style (0–100)**
   - Range: `0` (start of day, midnight) → `100` (end of day, next midnight; usually displayed as `0` of next day)
   - Midday: `50`
   - Example times: `10` ≈ 02:24, `25` ≈ 06:00, `75` ≈ 18:00, `90` ≈ 21:36

2. **Fraction-style (0.000–1.000)**
   - Range: `0.000` → `1.000`
   - Midday: `0.500`
   - Equivalent to percentage / 100.

3. **Composite multi-prefix format (AC.MC.kC.C)**
   - Example: `AC.MC.kC.C` displays the day fraction broken into progressive decimal prefixes. This is especially useful for UI readouts and serialization.
   - Example `50.00` (percentage) maps to `0.5000` (fraction) or `0 AC .50 MC` depending on formatting choice.

4. **ISO-like timestamp recommendation**
   - `YYYY-MM-DD AC.FFFF` where `FFFF` is the fractional AC expressed to the desired precision (e.g., 4-6 digits). Example: `2026-01-06 0.5000 AC` → 2026-01-06 at midday.

---

## Implementation guidance (Python-focused)

### Representations
- Use exact decimal fractions for sub-day units (Python `decimal.Decimal` recommended for precise string output).
- Represent astronomical cycles as either ranges or averages (floats are acceptable with explicit documentation).

### Example data structure (CSV-ready)

Produce a CSV file where each row lists: `unit, symbol, meaning, base_unit_AC, seconds_per_unit, seconds_per_unit_exact_bool`.

### Example generator (conceptual snippet)

```python
from decimal import Decimal, getcontext
getcontext().prec = 30

AC_IN_SECONDS = Decimal('86400')

prefixes = [
    ('Megacycle', 'MC', Decimal('1e-2')),
    ('Kilocycle', 'kC', Decimal('1e-3')),
    ('Cycle', 'C', Decimal('1e-4')),
    ('Millicycle', 'mC', Decimal('1e-7')),
    ('Microcycle', 'µC', Decimal('1e-10')),
    ('Nanocycle', 'nC', Decimal('1e-13')),
]

rows = []
for name, sym, frac in prefixes:
    seconds = (AC_IN_SECONDS * frac)
    rows.append((name, sym, f"{frac} AC", str(frac), str(seconds)))

# write out CSV or print
```

This approach gives exact decimal strings suitable for programmatic consumption.

### Edge cases
- Do not attempt to encode leap seconds in the core `AC` definition; treat leap seconds as calendar/system-level adjustments.
- When converting historical timestamps, use Julian Day or UTC conversions as authoritative.

---

## Use cases and recommendations

- **User interface / UX**: show day fractions as `0–100` or `0.000–1.000` depending on audience. Use `AC.MC.kC.C` for technical displays.
- **Computers / Logging**: store internal time as `seconds since epoch` (Unix time) but expose Decimal Time as a derived display and interchange format. Offer conversion helpers in libraries.
- **Embedded / hardware**: quartz oscillators and atomic references map very well to the decimal subdivisions; e.g., a microcycle (8.64 µs) is easily measured by high-frequency timers.
- **Science / Astronomy**: retain traditional astronomical epochs and use Decimal Time for readability — do not replace Julian Day as the canonical astronomical timestamp without compelling reasons.

---

## Appendix A — Quick reference CSV (compact)

```csv
unit,symbol,meaning,base_unit_AC,seconds_per_unit
Astrocycle,AC,1 planetary day,1,86400
Megacycle,MC,1/100 AC,0.01,864
Kilocycle,kC,1/1_000 AC,0.001,86.4
Cycle,C,1/10_000 AC,0.0001,8.64
Millicycle,mC,1/10_000_000 AC,1e-7,0.00864
Microcycle,µC,1e-10 AC,1e-10,8.64e-06
Nanocycle,nC,1e-13 AC,1e-13,8.64e-09
Solar Cycle,SC,1 orbit (year),~365.2422,31558149.76
Stellar Cycle,StC,1_000 SC (~1_000 years),~365242.2,3.155814976e10
Galactic Cycle,GC,1_000 StC (~1_000_000 years),~3.652422e8,3.155814976e13
```

Notes: the `seconds_per_unit` field for SC/StC/GC uses the average tropical year multiplier for the sample numeric scalar. Use ranges for calendar-exact semantics.

---

## Versioning and governance

- This document is a *working specification*. If used in software or published externally, assign semantic versioning (e.g., `Decimal Time Spec v0.1`), and record conversion constants (e.g., `AC_IN_SECONDS`) with explicit numeric precision.
- If a team adopts this, maintain a changelog and a short rationale paragraph for any breaking change.

---

## Closing notes

Decimal Time as specified here is intentionally pragmatic: it is physically anchored, computationally friendly, and linguistically clear. It removes AM/PM ambiguity, makes midday a trivially computable `50` or `0.5`, and produces neat mappings between human concepts and machine-readable decimal fractions. It preserves astronomical realities by treating years and longer cycles as counted phenomena while making every duration below one day exact and base-10 friendly.
