
from providers.flight_provider import FlightProvider
from typing import Optional, Dict
from providers.azul.azul_scraping import get_azul_lowest_price
from providers.azul.decolar_scraping import get_decolar_lowest_price

class AzulProvider(FlightProvider):

    def get_from_decolar(self, from_code, to_code, date):
        price = get_decolar_lowest_price(from_code, to_code, date)        
        return price["AZUL"]

    def find_flight_prices(self, from_code: str, to_code: str, date: str) -> Optional[Dict]:
        #price = get_azul_lowest_price(from_code, to_code, date)
        price = self.get_from_decolar(from_code, to_code, date)        
        return {
            "company": "AZUL",
            "price": price
        }