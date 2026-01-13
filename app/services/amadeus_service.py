from providers.amadeus.amadeus_provider import AmadeusProvider
from typing import Dict

class AmadeusService:

    def __init__(self):
        self.providers = [
            AmadeusProvider()
        ]

    def find_prices(
        self,
        from_code: str,
        to_code: str,
        date: str
    ) -> Dict:

        all_results = []

        for provider in self.providers:
            try:
                # agora retorna lista de ofertas por companhia
                results = provider.find_flight_prices(from_code, to_code, date)
                if results:
                    all_results.extend(results)
            except Exception:
                # ignora falhas
                continue

        if not all_results:
            return {"error": "Nenhum preço encontrado"}

        # melhor preço geral
        best_price = min(all_results, key=lambda x: x["price"])

        return {
            "from": from_code,
            "to": to_code,
            "date": date,
            "best_price": best_price,
            "prices": all_results
        }
