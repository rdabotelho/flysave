# verify_azul.py
from playwright.sync_api import sync_playwright
import re
from datetime import datetime
import time

def extract_prices(page) -> float:
    """Extrai o preço do primeiro voo listado na Azul"""
    page.wait_for_selector("az-flight-card", timeout=60000)
    first_card = page.locator("az-flight-card").first

    # espera o preço renderizar
    price_span = first_card.locator("span[class*='currency-price']").first
    price_span.wait_for(timeout=60000)

    price_text = price_span.text_content().strip()
    if not price_text:
        print("⚠️ Preço não encontrado")
        return None

    match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})", price_text)
    if match:
        return float(match.group(1).replace(".", "").replace(",", "."))
    print("⚠️ Preço não conseguiu ser convertido")
    return None

def handle_azul_error(page) -> bool:
    """Detecta erros da Azul"""
    if page.locator("text=Atenção").count() > 0 and \
       page.locator("text=Não foi possível concluir o acesso").count() > 0:
        print("⚠️ Azul bloqueou a busca ou deu erro intermitente")
        return True
    return False

def format_azul_url(from_code, to_code, departure_date):
    """Constrói a URL da Azul"""
    dt = datetime.strptime(departure_date, "%Y-%m-%d")
    ida = dt.strftime("%m/%d/%Y")  # Azul usa MM/DD/YYYY
    url = (
        f"https://www.voeazul.com.br/br/pt/home/selecao-voo?"
        f"c[0].ds={from_code}&c[0].std={ida}&c[0].as={to_code}"
        f"&p[0].t=ADT&p[0].c=1&p[0].cp=false&f.dl=3&f.dr=3&cc=BRL"
    )
    return url

def get_azul_lowest_price(from_code, to_code, departure_date, retries=3):
    """Retorna o menor preço da Azul com proteção anti-bot"""
    attempt = 0
    while attempt < retries:
        attempt += 1
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=False,  # Azul geralmente exige False
                    slow_mo=100,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-features=IsolateOrigins,site-per-process",
                        "--disable-site-isolation-trials",
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

                # Bypass detection: override webdriver property
                context.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => false})"
                )

                page = context.new_page()
                url = format_azul_url(from_code, to_code, departure_date)
                page.goto(url, timeout=60000)

                # Cookies
                try:
                    page.click("[id='onetrust-accept-btn-handler']", timeout=3000)
                except:
                    pass

                # espera a página renderizar
                page.wait_for_timeout(10000)

                if handle_azul_error(page):
                    browser.close()
                    print(f"Tentativa {attempt} falhou, tentando novamente...")
                    time.sleep(5)
                    continue

                price = extract_prices(page)
                browser.close()
                if price is not None:
                    return price

                print(f"Tentativa {attempt} não encontrou preço, tentando novamente...")
                time.sleep(5)

        except Exception as e:
            print(f"Erro na tentativa {attempt}: {e}")
            time.sleep(5)

    print("Não foi possível obter o preço após várias tentativas")
    return None

if __name__ == "__main__":
    price = get_azul_lowest_price("SAO", "BEL", "2026-01-24")
    print("Menor preço AZUL:", price)
