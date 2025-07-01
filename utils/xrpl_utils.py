"""
Stub XRPL helpers.
Each function accepts token_code (str | None) but returns placeholder data.
Replace with real XRPL queries when ready.
"""

async def get_whale_data(token_code: str | None = None):
    return "WalletA – 25%\nWalletB – 18%\nOthers – 57%"

async def get_bubble_map(token_code: str | None = None):
    return "Cluster A (42 %)\nCluster B (30 %)\nLong tail"

async def get_big_txns(token_code: str | None = None):
    return "BUY 120 k @ 0.000065\nSELL 80 k @ 0.000067"

async def get_sentiment(token_code: str | None = None):
    return "🧠 Sentiment: Neutral ➡️ Slight Bullish"

# utils/xrpl_utils.py (append at bottom)

from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.models.requests import AccountCurrencies
import os

XRPL_RPC = os.getenv("XRPL_RPC", "https://xrplcluster.com")

async def currencies_for_issuer(issuer: str) -> list[str]:
    """
    Return a list of currency codes issued by `issuer`.
    """
    client = AsyncJsonRpcClient(XRPL_RPC)
    req = AccountCurrencies(account=issuer)
    resp = await client.request(req)
    return resp.result.get("send_currencies", [])

