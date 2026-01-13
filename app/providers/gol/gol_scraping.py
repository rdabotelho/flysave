from playwright.sync_api import sync_playwright
import re
from datetime import datetime
import time

def extract_prices(page) -> float:
    """Extrai o preço do primeiro card secundário da Gol"""
    # espera o primeiro card secundário
    page.wait_for_selector("b2c-card-secondary-details", timeout=60000)
    first_card = page.locator("b2c-card-secondary-details").first

    # espera o tgr-currency renderizar
    currency_span = first_card.locator("div.price-value tgr-currency span.tgr-currency__price__label").first
    currency_span.wait_for(timeout=60000)

    # pega todos os spans filhos e o último geralmente é o número
    spans = currency_span.locator("span")
    count = spans.count()
    if count == 0:
        print("⚠️ Nenhum span encontrado dentro do preço")
        return None

    price_text = spans.nth(count - 1).text_content().strip()

    if not price_text:
        print("⚠️ Preço não encontrado")
        return None

    # extrai número
    match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})", price_text)
    if match:
        return float(match.group(1).replace(".", "").replace(",", "."))

    print("⚠️ Preço não conseguiu ser convertido")
    return None

def handle_gol_error(page) -> bool:
    """Detecta se a GOL retornou algum erro de busca."""
    if page.locator("text=Ops, não encontramos voos").count() > 0:
        print("⚠️ GOL não retornou voos")
        return True
    if page.locator("text=Atenção").count() > 0 and \
       page.locator("text=Não foi possível concluir o acesso").count() > 0:
        print("⚠️ Gol bloqueou a busca ou deu erro intermitente")
        return True
    return False

def format_gol_url(from_code: str, to_code: str, departure_date: str) -> str:
    """Constrói a URL de busca da GOL diretamente."""
    dt = datetime.strptime(departure_date, "%Y-%m-%d")
    ida = dt.strftime("%d-%m-%Y")  # GOL usa dd-mm-yyyy

    url = (
        f"https://b2c.voegol.com.br/compra/busca-parceiros?"
        f"pv=br&tipo=DF&de={from_code}&para={to_code}&"
        f"ida={ida}&ADT=1&ADL=0&CHD=0&INF=0&voebiz=0"
    )
    return url

def get_gol_lowest_price(from_code, to_code, departure_date, retries=5):
    """Retorna o menor preço da Gol, com retry automático"""
    attempt = 0
    while attempt < retries:
        attempt += 1
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=False,  # True se quiser rodar em background
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
                url = format_gol_url(from_code, to_code, departure_date)
                page.goto(url, timeout=60000)

                # Cookies (se aparecer)
                try:
                    page.click("[id='onetrust-accept-btn-handler']", timeout=3000)
                except:
                    pass

                # espera 10 segundos para a página renderizar
                page.wait_for_timeout(10000)

                # verifica erros intermitentes
                if handle_gol_error(page):
                    browser.close()
                    print(f"Tentativa {attempt} falhou, tentando novamente...")
                    time.sleep(5)
                    continue

                # captura preço
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
    price = get_gol_lowest_price("SAO", "BEL", "2026-01-24")
    #price = get_gol_lowest_price("BEL", "SAO", "2026-01-30")
    print("Menor preço GOL:", price)
