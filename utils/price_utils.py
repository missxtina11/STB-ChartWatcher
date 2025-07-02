import random

async def fetch_price(token: str) -> str:
    """
    Dummy price-feed stub.
    Replace with a real API/DEX lookup for `token`.
    """
    price = round(random.uniform(0.00005, 0.00007), 6)
    return f"{price} XRP"

