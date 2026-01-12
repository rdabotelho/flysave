from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class FlightSearchRequest:
    from_code: str
    to_code: str
    departure_date: date
    adults: int = 1


@dataclass
class FlightPriceResult:
    airline: str
    price: float
    currency: str
    departure_date: date
    deeplink: Optional[str] = None
