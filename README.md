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
