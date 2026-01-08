"""
Example 03: Custom Planet Profiles
----------------------------------
1. Define a PlanetProfile (e.g., Mars).
2. Get the time on that planet.
3. Compare Earth AC vs Mars AC.
"""

import sys
import os
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import deci_time

def main():
    # Define Mars (Sol) parameters
    # 1 Sol approx 24h 39m 35.244s = 88775.244 SI seconds
    MARS_SOL_SECONDS = Decimal("88775.244")
    
    mars_profile = deci_time.PlanetProfile(
        name="Mars", 
        seconds_per_ac=MARS_SOL_SECONDS
    )
    
    print(f"--- Configuration ---")
    print(f"Earth Day: {deci_time.EARTH.seconds_per_ac} seconds")
    print(f"Mars Sol:  {mars_profile.seconds_per_ac} seconds")

    print(f"\n--- Time Comparison ---")
    # Get 'now' (UTC) for both profiles
    # Note: 'localtime' uses the system timezone offset, but scales the day length
    
    earth_time = deci_time.localtime(profile=deci_time.EARTH)
    mars_time  = deci_time.localtime(profile=mars_profile)
    
    print("Time on Earth (Local):")
    print(deci_time.to_iso_decimal(earth_time))
    print(deci_time.strftime("Day Progress: %p%", earth_time))
    
    print("\nTime on Mars (Local equivalent):")
    print(deci_time.to_iso_decimal(mars_time))
    print(deci_time.strftime("Day Progress: %p%", mars_time))

    print("\n--- Explanation ---")
    print("Note that the Solar Cycle (Year) and Day of Year are currently")
    print("derived from Earth calendars in this library implementation.")
    print("Only the time-of-day (AC fraction) is scaled to the planetary day length.")

if __name__ == "__main__":
    main()