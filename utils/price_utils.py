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
# utils/price_utils.py
async def fetch_price():
    return "0.000067 XRP/STB"
=======
async def fetch_price(token_code: str | None = None) -> str:
    """Return a placeholder price for now."""
    return "0.000065"

>>>>>>> 7d74048 (Push full STB ChartWatcher bot)
>>>>>>> ec10f73 (Clean up bytecode and cache)
