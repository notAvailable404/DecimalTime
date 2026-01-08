import unittest
import datetime
from decimal import Decimal, getcontext
import time

# ASSUMPTION: The library file is named 'deci_time.py' and is in the same directory.
# If your file is 'lib.deci.time.py', please rename it or adjust this import.
import deci_time

class TestDecimalTimeCore(unittest.TestCase):
    """
    Tests core mathematical conversions and PlanetProfile logic.
    """

    def setUp(self):
        # Ensure we are testing against the canonical Earth constant
        self.earth_profile = deci_time.EARTH
        self.ac_seconds = Decimal("86400")

    def test_constants(self):
        """Verify the physics anchor."""
        self.assertEqual(self.earth_profile.seconds_per_ac, self.ac_seconds)
        self.assertEqual(self.earth_profile.name, "Earth")

    def test_ac_to_seconds_exact(self):
        """Test exact conversion from AC to SI Seconds."""
        # 1 AC -> 86400 s
        self.assertEqual(deci_time.ac_to_seconds(Decimal("1"), self.earth_profile), self.ac_seconds)
        # 0.5 AC -> 43200 s
        self.assertEqual(deci_time.ac_to_seconds(Decimal("0.5"), self.earth_profile), Decimal("43200"))
        # 0 AC -> 0 s
        self.assertEqual(deci_time.ac_to_seconds(Decimal("0"), self.earth_profile), Decimal("0"))

    def test_seconds_to_ac_exact(self):
        """Test exact conversion from SI Seconds to AC."""
        # 86400 s -> 1 AC
        self.assertEqual(deci_time.seconds_to_ac(self.ac_seconds, self.earth_profile), Decimal("1"))
        # 43200 s -> 0.5 AC
        self.assertEqual(deci_time.seconds_to_ac(Decimal("43200"), self.earth_profile), Decimal("0.5"))

    def test_precision_integrity(self):
        """
        Leetcode-style edge case: Ensure Nanocycle (1e-13 AC) precision is preserved.
        1 nC = 0.0000000000001 AC.
        """
        nano_ac = Decimal("1e-13")
        seconds = deci_time.ac_to_seconds(nano_ac, self.earth_profile)
        # 1e-13 * 86400 = 8.64e-9 seconds (8.64 nanoseconds)
        expected_seconds = Decimal("0.00000000864")
        self.assertEqual(seconds, expected_seconds)

        # Round trip
        back_to_ac = deci_time.seconds_to_ac(seconds, self.earth_profile)
        self.assertAlmostEqual(back_to_ac, nano_ac, places=20)


class TestDeciStructLogic(unittest.TestCase):
    """
    Tests the breaking down of a fractional day into MC, kC, C.
    This validates the properties of the DeciStruct class.
    """

    def test_midday_structure(self):
        """Midday (0.5) should be 50 MC, 0 kC, 0 C."""
        # 0.5 AC
        ds = deci_time.DeciStruct(sc=2026, day_of_year=1, ac_fraction=Decimal("0.5"))
        self.assertEqual(ds.mc, 50)
        self.assertEqual(ds.kc, 0)
        self.assertEqual(ds.c, 0)

    def test_complex_fraction(self):
        """
        Test a specific fraction: 0.123456...
        0.1234 AC should be:
        MC = 12 (0.12)
        kC = 3  (0.003)
        C  = 4  (0.0004)
        """
        ds = deci_time.DeciStruct(sc=2026, day_of_year=1, ac_fraction=Decimal("0.12349"))
        self.assertEqual(ds.mc, 12)
        self.assertEqual(ds.kc, 3)
        self.assertEqual(ds.c, 4)
        # Note: DeciStruct properties truncate (floor), so the '9' at the end shouldn't bump C to 5.

    def test_rollover_edge_case(self):
        """
        Test just before rollover.
        0.9999 AC
        MC should be 99
        kC should be 9
        C should be 9
        """
        ds = deci_time.DeciStruct(sc=2026, day_of_year=1, ac_fraction=Decimal("0.9999"))
        self.assertEqual(ds.mc, 99)
        self.assertEqual(ds.kc, 9)
        self.assertEqual(ds.c, 9)

    def test_small_fraction(self):
        """
        Test 0.0001 AC (1 Cycle).
        MC=0, kC=0, C=1
        """
        ds = deci_time.DeciStruct(sc=2026, day_of_year=1, ac_fraction=Decimal("0.0001"))
        self.assertEqual(ds.mc, 0)
        self.assertEqual(ds.kc, 0)
        self.assertEqual(ds.c, 1)


class TestTimeConversions(unittest.TestCase):
    """
    Tests gmtime, localtime, and strftime.
    Uses known Unix timestamps to verify correctness.
    """

    def test_epoch_start(self):
        """Unix Epoch: 1970-01-01 00:00:00 UTC."""
        ts = 0
        ds = deci_time.gmtime(ts)
        
        self.assertEqual(ds.sc, 1970)
        self.assertEqual(ds.day_of_year, 1)
        self.assertEqual(ds.ac_fraction, Decimal("0"))
        self.assertEqual(ds.mc, 0)

    def test_exact_midday_1970(self):
        """
        1970-01-01 12:00:00 UTC.
        12 hours * 3600 = 43200 seconds.
        """
        ts = 43200
        ds = deci_time.gmtime(ts)
        
        self.assertEqual(ds.sc, 1970)
        self.assertEqual(ds.day_of_year, 1)
        # 0.5 exactly
        self.assertEqual(ds.ac_fraction, Decimal("0.5"))

    def test_end_of_day_clamping(self):
        """
        The library clamps 23:59:59.999... to < 1.0.
        Let's test 1970-01-01 23:59:59 UTC.
        """
        ts = 86399 # One second before midnight
        ds = deci_time.gmtime(ts)
        
        self.assertEqual(ds.sc, 1970)
        self.assertEqual(ds.day_of_year, 1)
        
        # Fraction should be 86399 / 86400
        expected = Decimal("86399") / Decimal("86400")
        self.assertAlmostEqual(ds.ac_fraction, expected, places=10)
        
        # MC check: 0.99998... -> MC 99
        self.assertEqual(ds.mc, 99)

    def test_leap_year_handling(self):
        """
        2024 was a leap year. Feb 29 exists.
        Verify day_of_year logic.
        2024-02-29 12:00:00 UTC.
        """
        dt = datetime.datetime(2024, 2, 29, 12, 0, 0, tzinfo=datetime.timezone.utc)
        ts = dt.timestamp()
        
        ds = deci_time.gmtime(ts)
        self.assertEqual(ds.sc, 2024)
        # Jan(31) + Feb(29) = 60th day
        self.assertEqual(ds.day_of_year, 60)
        self.assertEqual(ds.ac_fraction, Decimal("0.5"))

    def test_strftime_formatting(self):
        """Test the custom format specifiers."""
        # Construct a synthetic struct for deterministic testing
        # 2026-050, 0.505050... (Midday + small offset)
        # 0.505050 -> MC 50, kC 5, C 0
        ds = deci_time.DeciStruct(sc=2026, day_of_year=50, ac_fraction=Decimal("0.505050"))
        
        # Test %Y %j
        self.assertEqual(deci_time.strftime("%Y-%j", ds), "2026-050")
        
        # Test %A (Astrocycle) - logic in lib pads/truncates to 6 digits?
        # The lib code says: frac[:6].ljust(6, '0')
        # 0.505050 -> "0.505050"
        self.assertIn("0.505050", deci_time.strftime("%A", ds))
        
        # Test %M (Megacycle)
        self.assertEqual(deci_time.strftime("%M", ds), "50")
        
        # Test %p (Percent) -> 50.51 (rounded half up)
        self.assertEqual(deci_time.strftime("%p", ds), "50.51")
        
        # Test Composite
        # MC 50, kC 5, C 0
        self.assertEqual(deci_time.strftime("%M.%K.%C", ds), "50.5.0")


class TestPlanetProfiles(unittest.TestCase):
    """
    Tests utilizing a non-Earth planet profile.
    Example: Mars (Sol) ~ 88775.244 seconds.
    """

    def test_mars_time(self):
        mars_day_seconds = Decimal("88775.244")
        mars = deci_time.PlanetProfile("Mars", mars_day_seconds)
        
        # Test midpoint of a Mars Sol
        half_sol_seconds = mars_day_seconds / 2
        
        # Convert half sol seconds to AC using Mars profile
        ac = deci_time.seconds_to_ac(half_sol_seconds, mars)
        
        # Should be exactly 0.5 AC (Mars AC)
        self.assertEqual(ac, Decimal("0.5"))
        
        # Cross check: 43200 earth seconds is NOT 0.5 Mars AC
        earth_half_day = Decimal("43200")
        mars_ac = deci_time.seconds_to_ac(earth_half_day, mars)
        
        # 43200 / 88775.244 ≈ 0.4866...
        self.assertLess(mars_ac, Decimal("0.5"))
        self.assertGreater(mars_ac, Decimal("0.48"))

if __name__ == '__main__':
    unittest.main()