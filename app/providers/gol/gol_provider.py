
from providers.flight_provider import FlightProvider
from typing import Optional, Dict
from providers.gol.gol_scraping import get_gol_lowest_price

class GolProvider(FlightProvider):

    def find_flight_prices(self, from_code: str, to_code: str, date: str) -> Optional[Dict]:
        price = get_gol_lowest_price(from_code, to_code, date)
        return {
            "company": "GOL",
            "price": price
        }