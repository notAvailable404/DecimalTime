# File: decimal_time/convert.py
from decimal import Decimal, localcontext, Context, ROUND_FLOOR
from typing import Tuple, Dict, Union, Any
from .planet_profile import PlanetProfile

class DecimalTimeConverter:
    """
    Converts standard Unix timestamps to Decimal Time (Astrocycles).
    Operates with high precision using a local Decimal context.
    """
    def __init__(self, profile: PlanetProfile):
        self.profile = profile
        self.ac_len = profile.seconds_per_ac
        self.epoch_offset = Decimal(profile.epoch_offset_seconds)

    def to_elapsed_seconds(self, unix_ts: Union[int, float, Decimal]) -> Decimal:
        """
        Convert Unix timestamp to elapsed seconds since planet epoch.
        Preserves float precision by converting to string first if needed.
        """
        with localcontext() as ctx:
            ctx.prec = 50
            if isinstance(unix_ts, float):
                # Convert float to string first to avoid binary approx errors
                val = Decimal(str(unix_ts))
            else:
                val = Decimal(unix_ts)
            return val - self.epoch_offset

    def elapsed_to_ac_fraction(self, elapsed_seconds: Decimal) -> Tuple[int, Decimal]:
        """
        Convert elapsed seconds to (AC_count, fraction).
        AC_count is the integer day number (can be negative).
        fraction is always [0, 1).
        """
        with localcontext() as ctx:
            ctx.prec = 50
            # floor division gives correct negative AC count for times before epoch
            ac_count = int(elapsed_seconds // self.ac_len)
            
            # Remainder handling
            remainder = elapsed_seconds - (Decimal(ac_count) * self.ac_len)
            fraction = remainder / self.ac_len
            
            # Ensure fraction is strictly [0, 1) and handles -0.0
            fraction = fraction.normalize()
            if fraction < 0:
                 # Should theoretically not happen with floor div logic above, but safety first
                 fraction += 1
                 ac_count -= 1
            if fraction >= 1:
                fraction = Decimal(0)
                ac_count += 1
                
            return ac_count, fraction

    def to_decimal_display(self, unix_ts: Union[int, float, Decimal], places: int = 4) -> Dict[str, Any]:
        """
        Return structured display data for a given timestamp.
        """
        elapsed = self.to_elapsed_seconds(unix_ts)
        ac_count, frac = self.elapsed_to_ac_fraction(elapsed)
        
        with localcontext() as ctx:
            ctx.prec = 50
            
            # Percentage string (0..100)
            pct_val = frac * 100
            pct_str = f"{pct_val:.{places}f}"
            
            # Fraction string (0.0..0.9999)
            frac_str = f"{frac:.{places}f}"
            
            # Composite units
            # MC = 1/100, kC = 1/1000, C = 1/10000
            # Example: 0.54321 -> MC=54, kC=3, C=2
            
            # Convert to integer base units for safe extraction
            # 10,000 C per AC
            total_C = int(frac * 10000)
            
            mc = total_C // 100
            rem = total_C % 100
            kc = rem // 10
            c = rem % 10
            
            composite = {
                "MC": mc,
                "kC": kc,
                "C": c
            }

        return {
            "ac_count": ac_count,
            "fraction_str": frac_str,
            "percent_str": pct_str,
            "composite": composite
        }
