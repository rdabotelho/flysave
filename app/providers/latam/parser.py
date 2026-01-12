from app.utils.currency import parse_brl_price

def extract_lowest_price(prices: list[str]) -> float:
    values = [parse_brl_price(p) for p in prices]
    return min(values)
