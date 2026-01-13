import os
import requests
from collections import defaultdict
from providers.amadeus.amadeus_auth import AmadeusAuth

class AmadeusProvider:

    FLIGHT_OFFERS_ENDPOINT = "/v2/shopping/flight-offers"

    def __init__(self):
        self.base_url = os.getenv("AMADEUS_BASE_URL")
        self.auth = AmadeusAuth()

    def find_flight_prices(
        self,
        from_code: str,
        to_code: str,
        date: str,
        adults: int = 1,
        airlines: list[str] | None = None
    ) -> list[dict]:

        token = self.auth.get_token()

        params = {
            "originLocationCode": from_code,
            "destinationLocationCode": to_code,
            "departureDate": date,
            "adults": adults,
            "max": 50
        }

        if airlines:
            params["includedAirlineCodes"] = ",".join(airlines)

        response = requests.get(
            f"{self.base_url}{self.FLIGHT_OFFERS_ENDPOINT}",
            headers={
                "Authorization": f"Bearer {token}"
            },
            params=params,
            timeout=15
        )

        response.raise_for_status()
        offers = response.json().get("data", [])

        best_by_airline = defaultdict(lambda: None)

        for offer in offers:
            price = float(offer["price"]["total"])
            currency = offer["price"]["currency"]
            itineraries = offer["itineraries"]

            first_segment = itineraries[0]["segments"][0]
            airline = first_segment["carrierCode"]

            current = best_by_airline.get(airline)

            if current is None or price < current["price"]:
                best_by_airline[airline] = {
                    "provider": "amadeus",
                    "company": airline,
                    "price": price,
                    "currency": currency,
                    "itineraries": itineraries
                }

        return list(best_by_airline.values())
