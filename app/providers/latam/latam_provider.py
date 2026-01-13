
from providers.flight_provider import FlightProvider
from typing import Optional, Dict
from providers.latam.latam_scraping import get_latam_lowest_price

class LatamProvider(FlightProvider):

    def find_flight_prices(self, from_code: str, to_code: str, date: str) -> Optional[Dict]:
        price = get_latam_lowest_price(from_code, to_code, date)
        return {
            "company": "LATAM",
            "price": price
        }