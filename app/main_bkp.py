import sys
import requests
import os
import json
from datetime import datetime
from notify import send_sms
from dotenv import load_dotenv
import uuid
import time
import random

load_dotenv()

X_REQUEST_ID = os.getenv("X_REQUEST_ID")
TRACEPARENT = os.getenv("TRACEPARENT")
X_TRACKING_CODE = os.getenv("X_TRACKING_CODE")
X_UOW = os.getenv("X_UOW")
PARAM_H = os.getenv("PARAM_H")
X_REQUESTID = os.getenv("X_REQUESTID")
COOKIE = os.getenv("COOKIE")

URL = "https://www.decolar.com/shop/flights-busquets/api/v1/web/search"

LAST_PRICES_FILE = "last_prices.json"

def find_flight_prices(from_code: str, to_code: str, date: str) -> dict | None:
    params = {
        "from": from_code,
        "to": to_code,
        "departureDate": date,
        "h": PARAM_H,
        "reSearch": "true",
        #"di": "1",
        #"dss": "1000:69d0d244ecf3575cfaefe8d9ed22b825779ab4a2a188ca10:f737d64317237ff6bf0f75d6e402de84de2ba59eeca41407",
        "adults": "1",
        "channel": "site",
        #"adtCount": 1,
        "language": "pt_BR",
        "initialCurrencyCode": "BRL",
        "clientType": "WEB",
        "children": "0",
        "chdCount": "0",
        "limit": "10",
        "routeType": "DOMESTIC",
        "flow": "SEARCH",
        #"disambiguationType": "NO_DISAMBIGUATION",
        #"infants": "0",
        #"searchType": "ONE_WAY",
        #"refererEvent": "SB",
        #"refererFront": f"https://www.decolar.com/shop/flights/results/oneway/{from_code}/{to_code}/{date}/1/0/0?from=SB&di=1&reSearch=true",
        "site": "BR",
        #"refererBusquets": f"http://www.decolar.com/shop/flights/results/oneway/{from_code}/{to_code}/{date}/1/0/0?from=SB&di=1&reSearch=true",
        "chdDistribution": "0",
        "user": "123a2907-afa9-483a-a3fb-507a7d885d38",
        "socialId": str(uuid.uuid4()),
        "pageViewId": f"shopping-flights-{uuid.uuid4()}"
    }

    headers = {
        "Accept": "*/*",
        "x-request-id": X_REQUEST_ID,
        "x-requestid": X_REQUESTID,
        "traceparent": TRACEPARENT,
        "x-trackingcode": X_TRACKING_CODE,
        "x-uow": X_UOW,
        "Cookie": COOKIE,
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "priority": "u=1, i",
        #"referer": f"https://www.decolar.com/shop/flights/results/oneway/{from_code}/{to_code}/{date}/1/0/0?from=SB&di=1&reSearch=true",
        "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "x-gui-version": "30.109.5",
        #"x-referrer": f"https://www.decolar.com/shop/flights/results/oneway/{from_code}/{to_code}/{date}/1/0/0?from=SB&di=1&reSearch=true",
        #"x-requested-with": "XMLHttpRequest"
    }

    try:
        response = requests.get(URL, params=params, headers=headers, timeout=60)

        if not response.ok:
            print("❌ Erro HTTP")
            print(response.text)
            return None

        data = response.json()
        airline_summary = data.get("airlinesMatrix", {}).get("airlineSummaries", [])

        if not airline_summary:
            print("⚠️ airlineSummaries vazio ou inexistente")
            return None

        return airline_summary[0]

    except requests.exceptions.Timeout:
        print("⏱️ Timeout ao chamar a API")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de rede: {e}")
        return None
    except ValueError:
        print("❌ Erro ao converter response para JSON")
        return None

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


if __name__ == "__main__":
    # Teste
    sys.argv = ["main.py", "SAO", "BEL", "2026-01-24"]

    # Verifica argumentos
    if len(sys.argv) < 4:
        print("Uso: python main.py FROM TO DATE [PRICE_ALERT]")
        print("Exemplo: SAO BEL 2026-01-24 300")
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
    price = result.get("bestPrice")

    if airline is None or price is None:
        print(f"⚠️ {from_code} -> {to_code} | dados incompletos")
        sys.exit(0)

    print(f"✈️ {from_code} -> {to_code} | Data: {date} | Companhia: {airline} | Melhor preço: R$ {price}")

    if price_alert is not None:
        price_alert_check(price, price_alert, from_code, to_code, date, airline, "+5511993130420")
        price_alert_check(price, price_alert, from_code, to_code, date, airline, "+5511993461788")        
