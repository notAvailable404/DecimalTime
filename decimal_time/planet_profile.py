# File: decimal_time/planet_profile.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal
import json
from typing import Optional, Dict, Any

@dataclass
class PlanetProfile:
    """
    Configuration for a planet's time system.
    
    Attributes:
        planet_name: Human-readable name (e.g., "Earth", "Mars").
        seconds_per_ac: Length of one Astrocycle (mean solar day) in SI seconds.
        year_in_acs: Average orbital period in local days (AC).
        epoch_offset_seconds: Unix timestamp (SI seconds) representing the planet's Time Zero.
        leap_rule: Strategy for leap years ('gregorian_earth', 'accumulator', 'none').
        accumulator_rate: If leap_rule is 'accumulator', the fractional day added per orbit.
    """
    planet_name: str
    seconds_per_ac: Decimal
    year_in_acs: Decimal
    epoch_offset_seconds: int = 0
    leap_rule: str = "gregorian_earth"
    accumulator_rate: Optional[Decimal] = None

    def __post_init__(self):
        # Ensure Decimal types
        if not isinstance(self.seconds_per_ac, Decimal):
            self.seconds_per_ac = Decimal(str(self.seconds_per_ac))
        if not isinstance(self.year_in_acs, Decimal):
            self.year_in_acs = Decimal(str(self.year_in_acs))
        if self.accumulator_rate is not None and not isinstance(self.accumulator_rate, Decimal):
            self.accumulator_rate = Decimal(str(self.accumulator_rate))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, serializing Decimals as strings."""
        data = asdict(self)
        data['seconds_per_ac'] = str(self.seconds_per_ac)
        data['year_in_acs'] = str(self.year_in_acs)
        if self.accumulator_rate is not None:
            data['accumulator_rate'] = str(self.accumulator_rate)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PlanetProfile:
        """Create from dictionary."""
        return cls(
            planet_name=data['planet_name'],
            seconds_per_ac=Decimal(str(data['seconds_per_ac'])),
            year_in_acs=Decimal(str(data['year_in_acs'])),
            epoch_offset_seconds=int(data.get('epoch_offset_seconds', 0)),
            leap_rule=data.get('leap_rule', 'gregorian_earth'),
            accumulator_rate=Decimal(str(data['accumulator_rate'])) if data.get('accumulator_rate') else None
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> PlanetProfile:
        return cls.from_dict(json.loads(json_str))

# Default Profiles
EARTH_PROFILE = PlanetProfile(
    planet_name="Earth",
    seconds_per_ac=Decimal('86400'),
    year_in_acs=Decimal('365.2422'),
    epoch_offset_seconds=0,
    leap_rule='gregorian_earth'
)

MARS_PROFILE = PlanetProfile(
    planet_name="Mars",
    seconds_per_ac=Decimal('88775.244'),
    year_in_acs=Decimal('668.5921'),
    epoch_offset_seconds=0, # Placeholder
    leap_rule='accumulator',
    accumulator_rate=Decimal('0.5921')
)
