from abc import ABC, abstractmethod
from .models import FlightSearchRequest, FlightPriceResult


class AirlineProvider(ABC):

    @abstractmethod
    def get_lowest_price(
        self,
        request: FlightSearchRequest
    ) -> FlightPriceResult:
        pass
