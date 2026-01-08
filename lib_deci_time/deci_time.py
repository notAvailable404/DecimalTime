"""
This software is provided AS-IS.
This library is an experimental demonstration of a Decimal Time system.
It is not intended for real-world or production use.
The implementation relies on Python’s standard `time` module for conversions.
For real systems, a low-level implementation (C/C++) would be required.
See DECIMAL_TIME.md for the formal specification.
"""

import time as _sys_time
import datetime
from decimal import Decimal, Context, localcontext, ROUND_HALF_UP, ROUND_FLOOR
from dataclasses import dataclass
from typing import Optional, Union, NamedTuple

# -----------------------------------------------------------------------------
# Configuration & Constants
# -----------------------------------------------------------------------------

# High precision decimal context template (used via localcontext(profile.ctx))
_GLOBAL_CTX = Context(prec=50)

# Canonical Constants (Earth Standard)
AC_SECONDS_EARTH = Decimal("86400")

# -----------------------------------------------------------------------------
# Data Structures
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class PlanetProfile:
    """
    Defines the physical constants for a specific planetary context.
    The default is Earth (1 AC = 86,400 SI seconds).
    """
    name: str
    seconds_per_ac: Decimal
    ctx: Context = _GLOBAL_CTX

    def __post_init__(self):
        # ensure seconds_per_ac is Decimal
        # object.__setattr__ used because dataclass is frozen
        if not isinstance(self.seconds_per_ac, Decimal):
            object.__setattr__(self, "seconds_per_ac", Decimal(str(self.seconds_per_ac)))


# Default Profile
EARTH = PlanetProfile("Earth", AC_SECONDS_EARTH)


class DeciStruct(NamedTuple):
    """
    The Decimal Time equivalent of time.struct_time.

    Fields:
      - sc: int -> Solar Cycle (year)
      - day_of_year: int -> 1..365/366
      - ac_fraction: Decimal -> fraction of current Astrocycle (0 <= f < 1)
    """
    sc: int
    day_of_year: int
    ac_fraction: Decimal

    @property
    def mc(self) -> int:
        """Megacycles (0-99). 1 MC = 0.01 AC. Truncated (floor)."""
        return int((self.ac_fraction * Decimal(100)).to_integral_value(rounding=ROUND_FLOOR))

    @property
    def kc(self) -> int:
        """Kilocycles (0-9). single digit after MC (floor)."""
        rem = (self.ac_fraction * Decimal(100)) - Decimal(self.mc)
        return int((rem * Decimal(10)).to_integral_value(rounding=ROUND_FLOOR))

    @property
    def c(self) -> int:
        """Cycles (0-9). single digit after kC (floor)."""
        return int(((self.ac_fraction * Decimal(10000)) % 10).to_integral_value(rounding=ROUND_FLOOR))

    @property
    def total_ac(self) -> Decimal:
        return self.ac_fraction

    def __repr__(self):
        # Show a readable representation with controlled precision
        with localcontext(self._dec_ctx()) as ctx:
            ctx.prec = 12
            acf = +self.ac_fraction
            return (f"DeciStruct(sc={self.sc}, day={self.day_of_year}, "
                    f"ac={acf:.6f}, mc={self.mc}, kc={self.kc}, c={self.c})")

    def _dec_ctx(self):
        # Provide a context for pretty printing (uses global ctx)
        return _GLOBAL_CTX

# -----------------------------------------------------------------------------
# Core API (Mirrors time module, decimal-aware)
# -----------------------------------------------------------------------------

def time(profile: PlanetProfile = EARTH) -> Decimal:
    """
    Return the current Decimal Time as Decimal number of Astrocycles (AC)
    since the Unix epoch (1970-01-01T00:00:00 UTC).

    Note: returns Decimal to preserve precision; use localcontext(profile.ctx)
    for arithmetic.
    """
    # Use nanoseconds to preserve full precision
    t_ns = _sys_time.time_ns()
    with localcontext(profile.ctx):
        t_sec = Decimal(t_ns) / Decimal('1000000000')
        t_ac = t_sec / profile.seconds_per_ac
        return +t_ac  # apply context precision

def sleep(ac: Union[float, Decimal], profile: PlanetProfile = EARTH) -> None:
    """
    Sleep for `ac` Astrocycles on the given profile. Internally converts to SI seconds
    and calls time.sleep(float_seconds). Using Decimal prevents intermediate float rounding
    until the actual system call.
    """
    if not isinstance(ac, Decimal):
        ac = Decimal(str(ac))
    with localcontext(profile.ctx):
        seconds = ac * profile.seconds_per_ac
        # Convert to float for system sleep; note this may lose precision for very small durations
        _sys_time.sleep(float(seconds))

def _to_decimal_seconds(seconds_input: Optional[Union[float, Decimal]]) -> Decimal:
    """
    Convert an input seconds (float/int/Decimal) to Decimal seconds preserving precision.
    If input is None returns current time in Decimal seconds using time_ns().
    """
    if seconds_input is None:
        # current time in ns
        t_ns = _sys_time.time_ns()
        return Decimal(t_ns) / Decimal('1000000000')
    if isinstance(seconds_input, Decimal):
        return seconds_input
    # For floats/ints, convert via str to preserve printed representation
    return Decimal(str(seconds_input))

def gmtime(seconds: Optional[Union[float, Decimal]] = None,
           profile: PlanetProfile = EARTH) -> DeciStruct:
    """
    Convert seconds since Unix epoch (SI seconds) to DeciStruct in UTC.
    If seconds is None, uses current time.
    """
    sec_dec = _to_decimal_seconds(seconds)
    dt = _timestamp_to_datetime(sec_dec, tz=datetime.timezone.utc)
    return _datetime_to_decistruct(dt, profile)

def localtime(seconds: Optional[Union[float, Decimal]] = None,
              profile: PlanetProfile = EARTH) -> DeciStruct:
    """
    Convert seconds since Unix epoch to DeciStruct in local system timezone.
    """
    sec_dec = _to_decimal_seconds(seconds)
    # Use system local timezone
    dt = _timestamp_to_datetime(sec_dec, tz=None).astimezone()
    return _datetime_to_decistruct(dt, profile)

def strftime(fmt: str, t: DeciStruct) -> str:
    """
    Format a DeciStruct using a limited set of directives:
      %Y -> Solar Cycle (year)
      %j -> Day of year (001..366)
      %A -> Astrocycle fraction (default 6 decimals)
      %M -> Megacycle (00..99)
      %K -> Kilocycle (0..9)
      %C -> Cycle (0..9)
      %p -> Percent of day (0.00..100.00)

    Note: This intentionally avoids full strftime to keep the demo focused.
    """
    # Use Decimal local context for formatting calculations
    with localcontext(_GLOBAL_CTX):
        ac_str = format(t.ac_fraction, 'f')
        # Limit default ac_str to 6 decimals for readability
        if '.' in ac_str:
            whole, frac = ac_str.split('.', 1)
            frac = frac[:6].ljust(6, '0')
            ac_str = whole + '.' + frac
        mc_str = f"{t.mc:02d}"
        kc_str = f"{t.kc:d}"
        c_str = f"{t.c:d}"
        pct = (t.ac_fraction * Decimal(100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        pct_str = f"{pct:.2f}"

    out = fmt
    out = out.replace("%Y", str(t.sc))
    out = out.replace("%j", f"{t.day_of_year:03d}")
    out = out.replace("%A", ac_str)
    out = out.replace("%M", mc_str)
    out = out.replace("%K", kc_str)
    out = out.replace("%C", c_str)
    out = out.replace("%p", pct_str)
    return out

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _timestamp_to_datetime(ts: Decimal, tz=None) -> datetime.datetime:
    """
    Convert Decimal seconds since epoch into a timezone-aware datetime (with microsecond precision).
    tz: timezone or None (system local)
    """
    if not isinstance(ts, Decimal):
        ts = Decimal(str(ts))
    sec_int = int(ts // 1)
    frac = ts - Decimal(sec_int)
    micros = int((frac * Decimal('1000000')).to_integral_value(rounding=ROUND_HALF_UP))
    # Build dt from integer seconds, then replace microsecond
    dt = datetime.datetime.fromtimestamp(sec_int, tz=tz)
    return dt.replace(microsecond=micros)

def _datetime_to_decistruct(dt: datetime.datetime, profile: PlanetProfile) -> DeciStruct:
    """Internal helper to convert a python datetime to DeciStruct."""
    # Year and day-of-year come straight from the datetime
    sc = dt.year
    day_of_year = dt.timetuple().tm_yday

    with localcontext(profile.ctx):
        secs_whole = Decimal(dt.hour * 3600 + dt.minute * 60 + dt.second)
        micros = Decimal(dt.microsecond) / Decimal('1000000')
        seconds_in_day = secs_whole + micros
        frac = seconds_in_day / profile.seconds_per_ac

        # Clamp into [0, 1) to avoid exact 1.0
        if frac >= 1:
            frac = (Decimal(1) - Decimal('1e-20'))
        if frac < 0:
            frac = Decimal(0)

    return DeciStruct(sc=sc, day_of_year=day_of_year, ac_fraction=frac)

def to_iso_decimal(t: DeciStruct, precision: int = 6) -> str:
    """
    Produce a simple ISO-like timestamp: YYYY-DDD AC.FFFF
    (YYYY and day-of-year plus AC fraction)
    """
    with localcontext(_GLOBAL_CTX):
        frac_q = t.ac_fraction.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)
        return f"{t.sc}-{t.day_of_year:03d} {frac_q} AC"

# -----------------------------------------------------------------------------
# Unit Conversion Utilities
# -----------------------------------------------------------------------------

def ac_to_seconds(ac: Union[Decimal, float, int], profile: PlanetProfile = EARTH) -> Decimal:
    if not isinstance(ac, Decimal):
        ac = Decimal(str(ac))
    with localcontext(profile.ctx):
        return ac * profile.seconds_per_ac

def seconds_to_ac(sec: Union[Decimal, float, int], profile: PlanetProfile = EARTH) -> Decimal:
    if not isinstance(sec, Decimal):
        sec = Decimal(str(sec))
    with localcontext(profile.ctx):
        return sec / profile.seconds_per_ac

# -----------------------------------------------------------------------------
# Demo / Quick tests
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Demo: current AC since epoch
    now_ac = time()
    print(f"Current Decimal Timestamp (AC since epoch): {now_ac}")

    local = localtime()
    print(f"Local Decimal Time (ISO-like): {to_iso_decimal(local)}")
    print("Canonical Display:", strftime("%Y-%j %A (%p)", local))
    print("Composite:", strftime("AC.%M.%K.%C", local))
