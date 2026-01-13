import sys
import os
import json
from datetime import datetime
from notify import send_sms
from dotenv import load_dotenv
from services.amadeus_service import AmadeusService

load_dotenv()

LAST_PRICES_FILE = "last_prices.json"

def load_last_prices():
    if os.path.exists(LAST_PRICES_FILE):
        with open(LAST_PRICES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_last_price(route: str, price: float):
    last_prices = load_last_prices()
    last_prices[route] = price
    with open(LAST_PRICES_FILE, "w") as f:
        json.dump(last_prices, f)

def price_alert_check(price: float, alert_limit: float, from_code: str, to_code: str, date: str, airline: str, phone_number: str = None):
    route = f"{from_code}->{to_code}"
    last_prices = load_last_prices()
    last_price = last_prices.get(route)

    if price < alert_limit and price != last_price:
        save_last_price(route, price)
        if phone_number:
            now = datetime.now().strftime("%H:%M")
            msg = (
                "ALERTA DE PREÇO\n"
                f"{from_code} -> {to_code}\n"
                f"Data: {date}\n"
                f"Companhia: {airline}\n"
                f"Preço: R$ {price}\n"
                f"Verificado: {now}"
            )
            send_sms(phone_number, msg)

def find_flight_prices(from_code: str, to_code: str, date: str) -> dict | None:
    """
    Busca preços na Decolar via verify_decolar.py
    Retorna um dicionário com os preços de LATAM, Gol e Azul.
    """
    try:
        service = AmadeusService()
        result = service.find_prices(from_code, to_code, date)
        if not result:
            print("⚠️ Nenhum preço encontrado")
            return None

        best_price = result["best_price"]

        return {
            "airlineName": best_price["company"],
            "bestPrice": best_price["price"],
            "allPrices": result["prices"]
        }

    except Exception as e:
        print(f"❌ Erro ao buscar preços na Decolar: {e}")
        return None

if __name__ == "__main__":
    # Teste
    sys.argv = ["main.py", "SAO", "BEL", "2026-01-23"]

    # Exemplo de execução: python main.py SAO BEL 2026-01-24 650
    if len(sys.argv) < 4:
        print("Uso: python main.py FROM TO DATE [PRICE_ALERT]")
        print("Exemplo: SAO BEL 2026-01-24 650")
        sys.exit(1)

    from_code = sys.argv[1]
    to_code = sys.argv[2]
    date = sys.argv[3]
    price_alert = float(sys.argv[4]) if len(sys.argv) > 4 else None

    result = find_flight_prices(from_code, to_code, date)

    if result is None:
        print(f"🚫 {from_code} -> {to_code} | sem resultados")
        sys.exit(0)

    airline = result.get("airlineName")
    bestPrice = result.get("bestPrice")
    allPrices = result.get("allPrices", {})

    print(f"✈️ {from_code} -> {to_code} | Data: {date}")
    for price in allPrices:
        print(f"   Companhia: {price["company"]} | Preço: R$ {price["price"]}")

    print(f"✅ Melhor preço: {airline} | R$ {bestPrice}")

    if price_alert is not None:
        price_alert_check(bestPrice, price_alert, from_code, to_code, date, airline, "+5511993130420")
        price_alert_check(bestPrice, price_alert, from_code, to_code, date, airline, "+5511993461788")
