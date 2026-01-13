from providers.latam.latam_provider import LatamProvider
from providers.gol.gol_provider import GolProvider
from providers.azul.azul_provider import AzulProvider

class FlightPriceService:

    def __init__(self):
        self.providers = [
            LatamProvider(),
            GolProvider(),
            AzulProvider()
       ]

    def find_prices(
        self,
        from_code: str,
        to_code: str,
        date: str
    ) -> dict:

        results = []

        for provider in self.providers:
            try:
                result = provider.find_flight_prices(from_code, to_code, date)
                if result and "price" in result and result["price"] is not None:
                    results.append(result)
            except Exception as e:
                pass

        if not results:
            return {"error": "Nenhum preço encontrado"}

        best_price = min(results, key=lambda x: x["price"])

        return {
            "from": from_code,
            "to": to_code,
            "date": date,
            "best_price": best_price,
            "prices": results
        }
