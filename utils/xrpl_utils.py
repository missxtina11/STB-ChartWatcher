"""
<<<<<<< HEAD
<<<<<<< HEAD
XRPL + GPT helper layer for STB-ChartWatcher.

Real XRPL queries are TODO-marked; for now we return simple stubs
so the bot responds without crashing. Replace each TODO with
real client logic when you’re ready.
"""

import os
import openai
from typing import List, Optional

# -------------------------------------------------------------------
#  OpenAI setup
# -------------------------------------------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")  # use any available model


# -------------------------------------------------------------------
#  XRPL quick-stubs  (replace with live data later)
# -------------------------------------------------------------------
async def get_wallet_balances(wallet: str) -> str:
    return f"📦 Balances for `{wallet}`\n- XRP: 500\n- STB: 10 000"


async def get_latest_transactions(wallet: str) -> str:
    return f"📜 Latest TX for `{wallet}`\n- Sent 100 STB\n- Received 50 STB"


async def get_amm_info() -> str:
    return "📊 STB AMM Info\n- Pool: STB/XRP\n- Volume: 123 456"


async def get_liquidity() -> str:
    return "1 000 000 STB"


async def get_holder_distribution() -> str:
    return "📈 Top Holders\n1. rXXXX… — 20 %\n2. rYYYY… — 15 %"


async def get_wallet_analysis(wallet: str) -> str:
    return f"🧠 Wallet {wallet} is a diamond-hand degen."


# -------------------------------------------------------------------
#  Bot analytics helpers (stubs)
# -------------------------------------------------------------------
async def get_whale_data(token: Optional[str] = None) -> str:
    return "WalletA — 25 %\nWalletB — 18 %\nOthers — 57 %"


async def get_bubble_map(token: Optional[str] = None) -> str:
    return "Cluster A (42 %)\nCluster B (30 %)\nLong tail"


async def get_big_txns(token: Optional[str] = None) -> str:
    return "BUY 120 k @ 0.000065\nSELL 80 k @ 0.000067"


async def get_sentiment(token: Optional[str] = None) -> str:
    return "🧠 Sentiment: Neutral → Slight Bullish"


# -------------------------------------------------------------------
#  Tiny data-fetch stubs for GPT (replace later)
# -------------------------------------------------------------------
async def get_wallet_tx_history(wallet: str) -> str:
    return "- BUY 5 000 STB\n- SELL 1 000 STB\n- LP add 2 000 STB"


async def get_holder_list_summary(token: str) -> str:
    return "Top 10 hold 65 %, CEX wallets hold 12 %."


async def get_recent_trade_logs(token: str) -> str:
    return "BUY 120 k @ 0.000065\nSELL 80 k @ 0.000067"


# -------------------------------------------------------------------
#  GPT wrappers
# -------------------------------------------------------------------
async def gpt_wallet_summary(tx_history: str) -> str:
    prompt = (
        "You are an XRPL trading analyst.\n\n"
        "Here is a wallet's recent transaction log:\n"
        f"{tx_history}\n\n"
        "Give me a concise summary (max 6 bullet points) of this wallet’s behaviour."
    )
    resp = await openai.ChatCompletion.acreate(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
    )
    return resp.choices[0].message.content.strip()


async def gpt_token_holders_analysis(holder_stats: str) -> str:
    prompt = (
        "You are an XRPL token-holder analyst.\n\n"
        f"Holder distribution:\n{holder_stats}\n\n"
        "Provide key insights and risks in 4-5 bullet points."
    )
    resp = await openai.ChatCompletion.acreate(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
    )
    return resp.choices[0].message.content.strip()


async def gpt_sentiment_from_trades(trade_log: str) -> str:
    prompt = (
        "You are an XRPL market-sentiment model.\n\n"
        f"Recent large trades:\n{trade_log}\n\n"
        "Classify overall sentiment (Bullish / Bearish / Neutral) and explain why."
    )
    resp = await openai.ChatCompletion.acreate(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
    )
    return resp.choices[0].message.content.strip()
=======
Placeholder helpers for Echo Protocol Watcher.

⚠️  These currently return static strings.
Swap in real XRPL calls (or a DB) later.
"""

# ───────────────────────────────────────────────────────────
#  Core analytics
# ───────────────────────────────────────────────────────────
async def get_whale_data() -> str:
    return (
        "🐋 *Top STB Whale Wallets*\n"
        "1. rXXXX...   · 25 %\n"
        "2. rYYYY...   · 18 %\n"
        "3. rZZZZ...   · 10 %\n"
    )


async def get_bubble_map() -> str:
    return (
        "🧩 *Bubble Map Clusters*\n"
        "• Cluster A – 12 wallets (42 % share)\n"
        "• Cluster B –  8 wallets (30 %)\n"
        "• Cluster C –  6 wallets (18 %)\n"
        "• Long tail  – others\n"
    )


async def get_big_txns() -> str:
    return (
        "💸 *Large Buys / Sells*\n"
        "• Buy 120 k STB @ 0.000065\n"
        "• Sell  80 k STB @ 0.000067\n"
        "• Buy  70 k STB @ 0.000066\n"
    )


async def get_sentiment() -> str:
    return (
        "🧠 *AI Wallet Sentiment*\n"
        "• Trend: **Bullish**  \n"
        "• Confidence: 72 %  \n"
        "• Note: Top wallets accumulating on dips."
    )
>>>>>>> 1b17b63 (Initial upload of Echo Protocol Watcher code)

import openai
=======
XRPL helper stubs for STB ChartWatcher.
Replace the placeholder logic with real XRPL queries when ready.
"""

from typing import List, Optional
>>>>>>> f20f4e2 (Remove conflict markers; clean xrpl_utils)
import os
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.models.requests import AccountCurrencies

# ─────────────────────────────────────────────────────────
#  XRPL RPC
# ─────────────────────────────────────────────────────────
XRPL_RPC = os.getenv("XRPL_RPC", "https://xrplcluster.com")


# ─────────────────────────────────────────────────────────
#  Issuer → currency list
# ─────────────────────────────────────────────────────────
async def currencies_for_issuer(issuer: str) -> List[str]:
    """
    Return a list of currency codes issued by `issuer`.
    """
    client = AsyncJsonRpcClient(XRPL_RPC)
    req = AccountCurrencies(account=issuer)
    resp = await client.request(req)
    return resp.result.get("send_currencies", [])


# ─────────────────────────────────────────────────────────
#  Analytics stubs (replace with live data later)
# ─────────────────────────────────────────────────────────
async def get_whale_data(token_code: Optional[str] = None) -> str:
    return "WalletA – 25%\nWalletB – 18%\nOthers – 57%"

async def get_bubble_map(token_code: Optional[str] = None) -> str:
    return "Cluster A (42 %)\nCluster B (30 %)\nLong tail"

async def get_big_txns(token_code: Optional[str] = None) -> str:
    return "BUY 120 k @ 0.000065\nSELL 80 k @ 0.000067"

async def get_sentiment(token_code: Optional[str] = None) -> str:
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

