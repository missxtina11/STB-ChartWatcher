# utils/price_utils.py
"""
Price helpers for STB-ChartWatcher.

• fetch_price(token)  → “0.000065 XRP”
   - Attempts Coingecko simple/price
   - Fallback: random stub so the bot never crashes
"""

import aiohttp
import random

_COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"


async def _coingecko_price(token: str) -> float | None:
    """
    Return price in XRP from Coingecko or None if unavailable.
    Coingecko expects the token 'id' (e.g. 'xrp', 'bitcoin').
    """
    params = {"ids": token.lower(), "vs_currencies": "xrp"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(_COINGECKO_API, params=params, timeout=10) as resp:
                data = await resp.json()
                return data.get(token.lower(), {}).get("xrp")
    except Exception:
        return None


# ──────────────────────────────────────────────────────────────
async def fetch_price(token: str) -> str:
    """
    Return the token’s price string (e.g. '0.000065 XRP').

    • First try Coingecko
    • If not listed, fall back to a pseudo-random stub
    """
    price = await _coingecko_price(token)
    if price is None:
        # fallback stub range; adjust as desired
        price = round(random.uniform(0.00005, 0.00007), 6)

    return f"{price:.6f} XRP"

