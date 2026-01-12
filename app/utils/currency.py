def parse_brl_price(price_text: str) -> float:
    """
    Ex: 'R$ 1.234,56' -> 1234.56
    """
    return float(
        price_text
        .replace("R$", "")
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )
