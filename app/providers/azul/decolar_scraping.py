from playwright.sync_api import sync_playwright
import re
from datetime import datetime

def extract_prices_decolar(page) -> dict:
    """
    Retorna os preços dos voos diretos por companhia aérea na Decolar.
    Pega **apenas o preço do voo direto** (primeiro preço da lista).
    Exemplo: {"LATAM": 608, "Gol": 646, "Azul": 1505}
    """
    page.wait_for_selector("div.matrix-2.matrix-airlines", timeout=60000)
    
    container = page.locator("div.matrix-2.matrix-airlines div.matrix-airlines-container")
    airlines = container.locator("airlines-matrix-airline")
    
    result = {}
    for i in range(airlines.count()):
        airline_block = airlines.nth(i)
        
        # nome da companhia
        try:
            name = airline_block.locator("div.airline-name span").inner_text().strip()
        except:
            continue
        
        # pega apenas o primeiro preço da lista (linha voo direto)
        try:
            first_price_text = airline_block.locator("li.priceItem.price span.amount.price-amount").first.inner_text()
            price = float(first_price_text.replace(".", "").replace(",", "."))
            result[name] = price
        except:
            result[name] = None

    # garante que LATAM, Gol e Azul estejam no dicionário
    for airline in ["LATAM", "Gol", "Azul"]:
        if airline not in result:
            result[airline] = None

    return result

def handle_decolar_error(page) -> bool:
    # verifica mensagens de erro ou bloqueio
    if page.locator("text=Ops! Não encontramos voos").count() > 0:
        print("⚠️ Decolar não encontrou voos")
        return True
    if page.locator("text=A busca está demorando").count() > 0:
        print("⚠️ Decolar bloqueou a busca")
        return True
    return False

def format_decolar_url(from_code: str, to_code: str, departure_date: str) -> str:
    """
    Constrói a URL de busca da Decolar.
    departure_date: YYYY-MM-DD
    """
    dt = datetime.strptime(departure_date, "%Y-%m-%d")
    date_str = dt.strftime("%Y-%m-%d")
    url = (
        f"https://www.decolar.com/shop/flights/results/oneway/"
        f"{from_code}/{to_code}/{date_str}/1/0/0"
        f"?from=SB&di=1&reSearch=true"
    )
    return url

def get_decolar_lowest_price(from_code, to_code, departure_date):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # alterar para True se quiser sem UI
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

        url = format_decolar_url(from_code, to_code, departure_date)
        page.goto(url, timeout=60000)

        prices = extract_prices_decolar(page)
        browser.close()
        return prices

if __name__ == "__main__":
    #prices = get_decolar_lowest_price("SAO", "BEL", "2026-01-24")
    prices = get_decolar_lowest_price("BEL", "SAO", "2026-01-30")
    print("Menores preços Decolar:", prices)
