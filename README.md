[![License: CC0-1.0](https://licensebuttons.net/l/zero/1.0/88x31.png)](http://creativecommons.org/publicdomain/zero/1.0/)
# File: README.md
# Decimal Time & DSC Reference Implementation

A production-ready reference implementation for **Decimal Time** (anchored to the local planetary day) and the **Decimal Solar Calendar (DSC)**. 

This project demonstrates a mathematically pure base-10 time system suitable for scientific simulation and off-world colonies (e.g., Mars), including a deterministic leap-year strategy for arbitrary orbital periods.

> This software is provided AS-IS. The author will not maintain this repository after release. This project is purely demonstrative; see DECIMAL_TIME.md for the formal specification.

## Quick Start

```bash
# Install
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .[dev]

# Run Demo
decimal-time demo

# Run Tests
pytest
```
Demo:<br>
<img width="941" height="508" alt="demo" src="https://github.com/user-attachments/assets/040af6e5-a877-42c9-97e8-893f74859d8b" />

Help:<br>
<img width="941" height="508" alt="help" src="https://github.com/user-attachments/assets/384becd8-a5cf-4f97-82de-0ad492433e42" />

Live clock:<br>
<img width="941" height="508" alt="live-watch-clock" src="https://github.com/user-attachments/assets/52eb9124-2b58-4989-816d-e5f3d4f175f1" />

Unit tests pass:<br>
<img width="941" height="508" alt="unit-tests-pass" src="https://github.com/user-attachments/assets/93ecac63-0581-4674-aa2a-819c53f3db69" />
<br>
<img width="1920" height="1080" alt="screenshot" src="https://github.com/user-attachments/assets/f3068459-0c00-4052-a3be-22c1af76ec43" />
