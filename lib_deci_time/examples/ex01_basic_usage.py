"""
Example 01: Basic Usage
-----------------------
1. Get the current decimal time.
2. Parse the DeciStruct object.
3. Format time strings.
"""

import sys
import os
import time as sys_time

# Boilerplate to import 'deci_time.py' from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import deci_time

def main():
    print("--- 1. Current Time ---")
    # Get current time as a raw Decimal (Astrocycles since Epoch)
    now_ac = deci_time.time()
    print(f"Raw AC timestamp: {now_ac}")

    # Get local time as a structured object (DeciStruct)
    local = deci_time.localtime()
    print(f"\n--- 2. DeciStruct Breakdown ---")
    print(f"Solar Cycle (Year): {local.sc}")
    print(f"Day of Year:        {local.day_of_year}")
    print(f"AC Fraction:        {local.ac_fraction} (0.0 to 1.0)")
    print(f"Megacycles (MC):    {local.mc} (0-99)")
    print(f"Kilocycles (kC):    {local.kc} (0-9)")
    print(f"Cycles (C):         {local.c}  (0-9)")

    print(f"\n--- 3. Formatting ---")
    # Standard formats
    print(f"ISO-like:           {deci_time.to_iso_decimal(local)}")
    
    # Custom formatting using strftime
    # %A = fractional AC, %M = MC, %K = kC, %C = Cycle
    fmt = "%Y-%j @ %M:%K:%C"
    print(f"Custom Template:    {fmt}")
    print(f"Result:             {deci_time.strftime(fmt, local)}")

    print(f"\n--- 4. Sleeping ---")
    print("Sleeping for 1 Kilocycle (approx 86.4 seconds? No, wait...)")
    print("Correction: 1 kC = 0.001 AC = 86.4 seconds.")
    print("That is too long for a demo. Let's sleep for 1 Cycle (8.64 seconds).")
    
    start = sys_time.time()
    # deci_time.sleep takes Astrocycles. 0.0001 AC = 1 Cycle.
    deci_time.sleep(0.0001) 
    end = sys_time.time()
    
    print(f"Slept for {end - start:.4f} SI seconds.")

if __name__ == "__main__":
    main()