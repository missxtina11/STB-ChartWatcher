<<<<<<< HEAD
<<<<<<< HEAD
import random

async def fetch_price(token: str) -> str:
    """
    Dummy price-feed stub.
    Replace with a real API/DEX lookup for `token`.
    """
    price = round(random.uniform(0.00005, 0.00007), 6)
    return f"{price} XRP"

=======
<<<<<<< HEAD
=======
>>>>>>> 720f448 (Clean conflict markers from price_utils.py)
# utils/price_utils.py
from typing import Optional

async def fetch_price(token_code: Optional[str] = None) -> str:
    """
    Placeholder price fetcher.
    Replace with a real API/XRPL DEX lookup later.
    """
    # Dummy static price
    return "0.000065"

<<<<<<< HEAD
>>>>>>> 7d74048 (Push full STB ChartWatcher bot)
>>>>>>> ec10f73 (Clean up bytecode and cache)
=======
>>>>>>> 720f448 (Clean conflict markers from price_utils.py)
