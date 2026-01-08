"""
Example 02: Math and Conversions
--------------------------------
1. Convert SI Seconds -> Astrocycles.
2. Convert Astrocycles -> SI Seconds.
3. Proper use of Decimal for precision.
"""

import sys
import os
from decimal import Decimal

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import deci_time

def main():
    print("--- 1. Conversions ---")
    
    # Scenario: How long is 5 minutes in Decimal Time?
    minutes = 5
    si_seconds = minutes * 60
    
    # Convert scalar seconds to AC
    duration_ac = deci_time.seconds_to_ac(si_seconds)
    
    print(f"{minutes} minutes ({si_seconds}s) = {duration_ac:.6f} AC")
    
    # Scenario: How many seconds is 25 Megacycles?
    # 25 MC = 0.25 AC
    mc_val = Decimal("0.25")
    duration_sec = deci_time.ac_to_seconds(mc_val)
    print(f"25 MC ({mc_val} AC) = {duration_sec} seconds")

    print("\n--- 2. Precision Warning ---")
    
    # WARNING: Do not use standard floats for Decimal Time arithmetic if you can help it.
    # Floating point errors accumulate quickly when dealing with 1e-13 (Nanocycles).
    
    val_float = 0.0000000001  # Standard float
    val_dec   = Decimal("0.0000000001") # Python Decimal
    
    print(f"Float input:   {val_float:.20f}")
    print(f"Decimal input: {val_dec:.20f}")
    
    ac_from_float = deci_time.seconds_to_ac(val_float)
    ac_from_dec   = deci_time.seconds_to_ac(val_dec)
    
    # Notice the garbage digits at the end of the float conversion
    print(f"Result (Float):   {ac_from_float}") 
    print(f"Result (Decimal): {ac_from_dec} (Clean)")

    print("\n--- 3. Arithmetics ---")
    # Adding 10 kC to current time
    now = deci_time.time()
    future = now + Decimal("0.01") # + 10 kC (which is 1 MC, or 0.01 AC)
    
    print(f"Now:    {now}")
    print(f"Future: {future}")

if __name__ == "__main__":
    main()