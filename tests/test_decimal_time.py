# File: tests/test_decimal_time.py
import pytest
from datetime import date
from decimal import Decimal
from decimal_time import DecimalSolarCalendar, DecimalTimeConverter, EARTH_PROFILE, PlanetProfile

# --- Calendar Tests ---

def test_dsc_mapping_examples():
    cal = DecimalSolarCalendar(leap_rule='gregorian_earth')
    
    # 2026-03-01 -> 60th day of year.
    # M1=36. 60-36=24 -> M02-24
    assert cal.gregorian_to_dsc(date(2026, 3, 1)) == (2026, 2, 24)
    
    # 2026-06-15 -> 166th day.
    # M1(36)+M2(37)+M3(36)+M4(37) = 146 days. 
    # 166 - 146 = 20 -> M05-20.
    # Wait, 166th day? 
    # Jan(31)+Feb(28)+Mar(31)+Apr(30)+May(31)+Jun(15) = 166. Correct.
    # Logic: [36, 37, 36, 37] sum=146. Next is M05.
    # However, let's verify spec logic in code:
    # 2026-06-15 -> M05-20? Or M05-19?
    # 166 - 146 = 20. So should be M05-20.
    # Let's check the provided examples in the prompt to ensure we match them.
    # Prompt requested: "2026-06-15 -> 2026-M05-19".
    # Let's re-calculate manually.
    # Gregorian 2026 days: 31+28+31+30+31+15 = 166.
    # DSC lengths: 36+37+36+37 = 146.
    # 166 - 146 = 20. Result should be M05-20.
    # If the prompt said M05-19, the prompt arithmetic might have been approximate or 0-indexed?
    # Standard calendars are 1-indexed. 
    # I will assert the mathematically correct value (M05-20) based on the spec I wrote.
    assert cal.gregorian_to_dsc(date(2026, 6, 15)) == (2026, 5, 20)

    # 2026-12-31 -> 365th day.
    # Should be last day of M10.
    # Sum of 5*(36+37) = 365. M10 is 37 days long. 
    # So M10-37.
    assert cal.gregorian_to_dsc(date(2026, 12, 31)) == (2026, 10, 37)

def test_leap_year_handling():
    cal = DecimalSolarCalendar(leap_rule='gregorian_earth')
    # 2024 is leap. 366 days.
    # Month 10 should have 38 days.
    assert cal.get_month_lengths(2024)[-1] == 38
    
    # 2024-12-31 -> M10-38
    assert cal.gregorian_to_dsc(date(2024, 12, 31)) == (2024, 10, 38)

def test_round_trip_conversion():
    cal = DecimalSolarCalendar(leap_rule='gregorian_earth')
    dates = [
        date(2023, 1, 1),
        date(2024, 2, 29),
        date(2025, 12, 31)
    ]
    for d in dates:
        y, m, day = cal.gregorian_to_dsc(d)
        d_back = cal.dsc_to_gregorian(y, m, day)
        assert d == d_back

def test_accumulator_leap_deterministic():
    # Rate 0.25 -> Leaps in year 4, 8, 12... (exact quarter)
    # floor(3 * 0.25) = 0.75 -> 0
    # floor(4 * 0.25) = 1.00 -> 1. Delta = 1. Leap!
    cal = DecimalSolarCalendar(leap_rule='accumulator', accumulator_rate=Decimal('0.25'))
    assert not cal._is_leap(1)
    assert not cal._is_leap(2)
    assert not cal._is_leap(3)
    assert cal._is_leap(4)
    assert not cal._is_leap(5)

# --- Converter Tests ---

def test_negative_epoch():
    conv = DecimalTimeConverter(EARTH_PROFILE)
    # -1 day exactly
    ts = -86400
    ac, frac = conv.elapsed_to_ac_fraction(Decimal(ts))
    assert ac == -1
    assert frac == 0
    
    # -1.5 days (-129600s) -> AC -2, fraction 0.5
    ts = -129600
    ac, frac = conv.elapsed_to_ac_fraction(Decimal(ts))
    assert ac == -2
    assert frac == Decimal('0.5')

def test_float_precision_preserved():
    conv = DecimalTimeConverter(EARTH_PROFILE)
    # 12345.6789
    # If converted to float->Decimal naively, might get artifacts.
    # The converter should handle this string conversion internally.
    ts = 12345.6789
    elapsed = conv.to_elapsed_seconds(ts)
    # Check we have at least the precision we put in
    assert abs(elapsed - Decimal('12345.6789')) < Decimal('1e-10')

def test_composite_formatting():
    conv = DecimalTimeConverter(EARTH_PROFILE)
    # 0.5 AC
    ts = 43200
    disp = conv.to_decimal_display(ts)
    c = disp['composite']
    assert c['MC'] == 50
    assert c['kC'] == 0
    assert c['C'] == 0
    assert disp['percent_str'] == '50.0000'
    
    # 0.54321 AC
    # 54 MC, 3 kC, 2 C
    # 0.54321 * 86400 = 46933.344 seconds
    ts = 46933.344
    disp = conv.to_decimal_display(ts)
    c = disp['composite']
    assert c['MC'] == 54
    assert c['kC'] == 3
    assert c['C'] == 2

def test_planet_profile_integrity():
    p = PlanetProfile(
        "Test", Decimal('100'), Decimal('100'), 0, 'accumulator', Decimal('0.1')
    )
    js = p.to_json()
    p2 = PlanetProfile.from_json(js)
    assert p == p2
    assert isinstance(p2.seconds_per_ac, Decimal)
