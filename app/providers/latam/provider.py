from app.core.interfaces import AirlineProvider
from core.models import FlightSearchRequest, FlightPriceResult
from app.utils.browser import get_browser
from app.providers.latam import selectors, parser
from app.config.settings import PAGE_TIMEOUT, CURRENCY


class LatamProvider(AirlineProvider):

    BASE_URL = "https://www.latamairlines.com/br/pt"

    def get_lowest_price(self, request: FlightSearchRequest) -> FlightPriceResult:
        search_url = self._build_url(request)

        playwright, browser = get_browser()
        page = browser.new_page()

        page.goto(search_url)
        page.wait_for_selector(selectors.PRICE, timeout=PAGE_TIMEOUT)

        prices_text = page.locator(selectors.PRICE).all_inner_texts()

        browser.close()
        playwright.stop()

        lowest_price = parser.extract_lowest_price(prices_text)

        return FlightPriceResult(
            airline="LATAM",
            price=lowest_price,
            currency=CURRENCY,
            departure_date=request.departure_date,
            deeplink=search_url
        )

    def _build_url(self, request: FlightSearchRequest) -> str:
        return (
            f"{self.BASE_URL}/voos?"
            f"origin={request.from_code}"
            f"&destination={request.to_code}"
            f"&outbound={request.departure_date.isoformat()}"
            f"&adults={request.adults}"
        )
