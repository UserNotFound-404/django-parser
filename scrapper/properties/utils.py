import re


def parse_price(price_str):
    price_cleaned = re.sub(r"[^\d.]", "", price_str)
    return float(price_cleaned) if price_cleaned else None