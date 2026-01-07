# File: decimal_time/calendar.py
from datetime import date, timedelta
from typing import List, Tuple
from decimal import Decimal, localcontext
import math

class DecimalSolarCalendar:
    """
    Implements the Decimal Solar Calendar (DSC) mapping.
    10 months per year, alternating 36/37 days.
    Leap day added to Month 10.
    """
    
    # Non-leap year pattern: [36, 37, 36, 37, 36, 37, 36, 37, 36, 37] -> Sum 365
    BASE_MONTH_LENGTHS = [36, 37] * 5

    def __init__(self, leap_rule: str = 'gregorian_earth', accumulator_rate: Decimal | None = None):
        self.leap_rule = leap_rule
        self.accumulator_rate = accumulator_rate
        
        if self.leap_rule == 'accumulator' and self.accumulator_rate is None:
            raise ValueError("accumulator_rate must be provided when leap_rule is 'accumulator'")

    def _is_leap(self, year: int) -> bool:
        """Determine if a year is a leap year based on the rule."""
        if self.leap_rule == 'gregorian_earth':
            return (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))
            
        elif self.leap_rule == 'accumulator':
            # Stateless deterministic rule:
            # leaps_until_Y = floor(Y * rate)
            # is_leap = (leaps_until_Y - leaps_until_Y-1) == 1
            rate = self.accumulator_rate
            with localcontext() as ctx:
                ctx.prec = 50
                prev_leaps = math.floor(Decimal(year - 1) * rate)
                curr_leaps = math.floor(Decimal(year) * rate)
                return (curr_leaps - prev_leaps) == 1
        
        elif self.leap_rule == 'none':
            return False
            
        else:
            raise ValueError(f"Unknown leap rule: {self.leap_rule}")

    def get_month_lengths(self, year: int) -> List[int]:
        lengths = self.BASE_MONTH_LENGTHS.copy()
        if self._is_leap(year):
            lengths[-1] += 1  # Month 10 gets the extra day
        return lengths

    def gregorian_to_dsc(self, g_date: date) -> Tuple[int, int, int]:
        """
        Convert Gregorian Date to (Year, Month, Day).
        Note: Assumes Year 1 DSC aligns with Year 1 Gregorian for simplicity in this demo.
        """
        year = g_date.year
        # Compute day of year (1-based)
        start_of_year = date(year, 1, 1)
        day_of_year = (g_date - start_of_year).days + 1
        
        lengths = self.get_month_lengths(year)
        
        current_day_count = 0
        for month_idx, length in enumerate(lengths):
            month_num = month_idx + 1
            if day_of_year <= current_day_count + length:
                day_num = day_of_year - current_day_count
                return (year, month_num, day_num)
            current_day_count += length
            
        raise ValueError(f"Date out of bounds for year {year}")

    def dsc_to_gregorian(self, year: int, month: int, day: int) -> date:
        """Convert DSC (Year, Month, Day) to Gregorian Date."""
        if not (1 <= month <= 10):
            raise ValueError("Month must be 1..10")
            
        lengths = self.get_month_lengths(year)
        month_len = lengths[month - 1]
        
        if not (1 <= day <= month_len):
            raise ValueError(f"Day {day} out of range for Month {month} (max {month_len})")
            
        # Sum days in preceding months
        day_of_year = sum(lengths[:month-1]) + day
        
        # Create date
        try:
            return date(year, 1, 1) + timedelta(days=day_of_year - 1)
        except ValueError as e:
            raise ValueError(f"Resulting date invalid: {e}")
