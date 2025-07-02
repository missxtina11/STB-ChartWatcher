# utils/xrpl_utils.py
"""
XRPL + GPT helper layer for STB-ChartWatcher.

Real XRPL queries are TODO-marked; current functions return stub
data so the bot always responds.
"""

import os
import random
import openai
from typing import Optional

# ─────────────────── OpenAI setup ───────────────────
openai.api_key = os.getenv("OPENAI_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")  # change if needed


# ─────────────── XRPL stub helpers ────────────────
async def get_wallet_balances(wallet: str) -> str:
    return f"📦 Balances for `{wallet}`\n• XRP  500\n• STB  10 000"


async def get_latest_transactions(wallet: str) -> str:
    return f"📜 Latest TX for `{wallet}`\n• Sent 100 STB\n• Received 50 STB"


async def get_amm_info() -> str:  # TODO real AMM stats
    return "📊 AMM Pool STB/XRP — Vol 123 456"


async def get_liquidity() -> str:
    return "1 000 000 STB"


async def get_holder_distribution() -> str:
    return "📈 Top holders:\n1. rXXXX… 20 %\n2. rYYYY… 15 %"


async def get_wallet_analysis(wallet: str) -> str:
    return f"🧠 Wallet {wallet} is a diamond-hand degen."


# ─────────────── Bot analytics stubs ────────────────
async def get_whale_data(token: Optional[str] = None) -> str:
    return "WalletA 25 %\nWalletB 18 %\nOthers 57 %"


async def get_bubble_map(token: Optional[str] = None) -> str:
    return "Cluster A 42 %\nCluster B 30 %\nLong tail"


async def get_big_txns(token: Optional[str] = None) -> str:
    return "BUY 120 k @ 0.000065\nSELL 80 k @ 0.000067"


async def get_sentiment(token: Optional[str] = None) -> str:
    return "🧠 Sentiment: Neutral → Slight Bullish"


# ─────────────── Tiny data stubs for GPT ────────────────
async def get_wallet_tx_history(wallet: str) -> str:
    return "- BUY 5 000 STB\n- SELL 1 000 STB\n- LP add 2 000 STB"


async def get_holder_list_summary(token: str) -> str:
    return "Top 10 hold 65 %, CEX wallets hold 12 %."


async def get_recent_trade_logs(token: str) -> str:
    return "BUY 120 k @ 0.000065\nSELL 80 k @ 0.000067"


# ─────────────── GPT wrappers ────────────────
async def gpt_wallet_summary(tx_history: str) -> str:
    prompt = (
        "You are an XRPL trading analyst.\n\n"
        f"Wallet transactions:\n{tx_history}\n\n"
        "Summarize behaviour in ≤6 bullet points."
    )
    res = await openai.ChatCompletion.acreate(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
    )
    return res.choices[0].message.content.strip()


async def gpt_token_holders_analysis(holder_stats: str) -> str:
    prompt = (
        "You analyse token holder distributions.\n\n"
        f"Data:\n{holder_stats}\n\n"
        "Give key insights & risks (4-5 bullets)."
    )
    res = await openai.ChatCompletion.acreate(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
    )
    return res.choices[0].message.content.strip()


async def gpt_sentiment_from_trades(trade_log: str) -> str:
    prompt = (
        "You are a market-sentiment model.\n\n"
        f"Recent large trades:\n{trade_log}\n\n"
        "Classify sentiment (Bullish / Bearish / Neutral) and explain."
    )
    res = await openai.ChatCompletion.acreate(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
    )
    return res.choices[0].message.content.strip()

