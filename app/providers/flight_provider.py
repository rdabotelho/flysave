from abc import ABC, abstractmethod
from typing import Optional, Dict

class FlightProvider(ABC):

    @abstractmethod
    def find_flight_prices(
        self,
        from_code: str,
        to_code: str,
        date: str
    ) -> Optional[Dict]:
        pass
