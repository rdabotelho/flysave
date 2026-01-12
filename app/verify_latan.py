from playwright.sync_api import sync_playwright
import re
from datetime import datetime

def extract_prices(page) -> float:
    # espera até que o texto 'brl' apareça
    page.wait_for_selector("[data-testid='display-currency-wrapper'] span:has-text(\"brl\")", timeout=60000)

    # pega o texto
    price_text = page.locator("[data-testid='display-currency-wrapper'] span:has-text('brl')").first.inner_text()

    # extrai o número
    match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})", price_text)
    if match:
        return float(match.group(1).replace(".", "").replace(",", "."))

    print("Preço não encontrado")
    return None

def handle_latam_error(page) -> bool:
    if page.locator("text=A busca está demorando mais que o normal").count() > 0:
        print("⚠️ LATAM bloqueou a busca")
        return True
    return False

def format_latam_url(from_code: str, to_code: str, departure_date: str) -> str:
    """
    Constrói a URL de busca da LATAM.
    departure_date: YYYY-MM-DD
    """
    # converte para formato ISO com hora 03:00:00.000Z
    dt = datetime.strptime(departure_date, "%Y-%m-%d")
    outbound_iso = dt.strftime("%Y-%m-%dT03%%3A00%%3A00.000Z")  # %3A é ':'

    url = (
        f"https://www.latamairlines.com/br/pt/oferta-voos?"
        f"origin={from_code}&destination={to_code}&"
        f"outbound={outbound_iso}&"
        f"adt=1&chd=0&inf=0&trip=OW&cabin=Economy&redemption=false&"
        f"sort=RECOMMENDED"
    )
    return url

def get_latam_lowest_price(from_code, to_code, departure_date):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # <-- agora não abre o browser
            slow_mo=150,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        context = browser.new_context(
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        url = format_latam_url(from_code, to_code, departure_date)
        page.goto(url, timeout=60000)

        # Cookies (se aparecerem)
        for selector in [
            "[data-testid='cookies-politics-button--button']",
            "[data-testid='button-close-login-incentive']"
        ]:
            try:
                page.click(selector, timeout=3000)
            except:
                pass

        if handle_latam_error(page):
            browser.close()
            return None

        price = extract_prices(page)
        browser.close()
        return price

if __name__ == "__main__":
    #price = get_latam_lowest_price("SAO", "BEL", "2026-01-24")
    price = get_latam_lowest_price("BEL", "SAO", "2026-01-30")
    print("Menor preço LATAM:", price)
