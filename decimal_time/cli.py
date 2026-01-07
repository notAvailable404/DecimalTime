# File: decimal_time/cli.py
import argparse
import sys
import time
import csv
from datetime import datetime, date, timezone
from decimal import Decimal

from .planet_profile import EARTH_PROFILE, MARS_PROFILE
from .convert import DecimalTimeConverter
from .calendar import DecimalSolarCalendar

def cmd_demo(args):
    print("--- Decimal Time System Demo ---")
    
    # 1. Current Time (Earth)
    converter = DecimalTimeConverter(EARTH_PROFILE)
    now_ts = datetime.now(timezone.utc).timestamp()
    disp = converter.to_decimal_display(now_ts)
    
    print(f"\nCurrent Earth Decimal Time:")
    print(f"  AC Count: {disp['ac_count']}")
    print(f"  Fraction: {disp['fraction_str']} ({disp['percent_str']}%)")
    c = disp['composite']
    print(f"  Composite: {c['MC']:02d} MC . {c['kC']} kC . {c['C']} C")
    
    # 2. Calendar Conversions
    cal = DecimalSolarCalendar(leap_rule=EARTH_PROFILE.leap_rule)
    examples = [
        date(2026, 3, 1),
        date(2026, 6, 15),
        date(2026, 12, 31),
        date(2024, 12, 31) # Leap year example
    ]
    
    print("\n--- DSC Calendar Mapping Examples ---")
    for g_date in examples:
        y, m, d = cal.gregorian_to_dsc(g_date)
        print(f"  Gregorian {g_date} -> DSC {y:04d}-M{m:02d}-{d:02d}")

def cmd_csv(args):
    year = args.year
    filename = f"dsc_mapping_{year}.csv"
    cal = DecimalSolarCalendar(leap_rule=EARTH_PROFILE.leap_rule)
    start = date(year, 1, 1)
    
    # Determine total days in Gregorian year to iterate safely
    next_year = date(year + 1, 1, 1)
    total_days = (next_year - start).days
    
    print(f"Generating mapping for {year} ({total_days} days) into {filename}...")
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['gregorian_date', 'dsc_year', 'dsc_month', 'dsc_day', 'dsc_formatted'])
        
        for i in range(total_days):
            current_date = date.fromordinal(start.toordinal() + i)
            y, m, d = cal.gregorian_to_dsc(current_date)
            writer.writerow([
                current_date.isoformat(),
                y, m, d,
                f"{y:04d}-M{m:02d}-{d:02d}"
            ])
            
    print("Done.")

def cmd_watch(args):
    converter = DecimalTimeConverter(EARTH_PROFILE)
    # Update frequency: 1 kC (approx 0.864s)
    # We update slightly faster (0.1s) for UI responsiveness
    try:
        while True:
            now_ts = datetime.now(timezone.utc).timestamp()
            disp = converter.to_decimal_display(now_ts, places=4)
            c = disp['composite']
            # Clear line (ANSI) and print
            sys.stdout.write(f"\r\033[KDecimal Time: {disp['percent_str']} %  |  {c['MC']:02d}.{c['kC']}.{c['C']} (AC {disp['ac_count']})")
            sys.stdout.flush()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped.")

def cmd_test(args):
    try:
        import pytest
        sys.exit(pytest.main(["tests"]))
    except ImportError:
        print("pytest not found. Please run: pip install pytest")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Decimal Time Reference CLI")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Demo
    subparsers.add_parser('demo', help="Show demo output")
    
    # CSV
    csv_parser = subparsers.add_parser('csv', help="Generate mapping CSV for a year")
    csv_parser.add_argument('year', type=int, help="Year to map")
    
    # Watch
    subparsers.add_parser('watch', help="Live clock")
    
    # Test
    subparsers.add_parser('test', help="Run tests")
    
    args = parser.parse_args()
    
    if args.command == 'demo':
        cmd_demo(args)
    elif args.command == 'csv':
        cmd_csv(args)
    elif args.command == 'watch':
        cmd_watch(args)
    elif args.command == 'test':
        cmd_test(args)

if __name__ == "__main__":
    main()
