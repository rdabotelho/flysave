from app.core.models import FlightSearchRequest

class FlightSearchService:

    def __init__(self, providers: list):
        self.providers = providers

    def search(self, request: FlightSearchRequest):
        results = []

        for provider in self.providers:
            try:
                results.append(provider.get_lowest_price(request))
            except Exception as e:
                print(f"Erro em {provider.__class__.__name__}: {e}")

        return sorted(results, key=lambda r: r.price)
