# utils/xrpl_utils.py
"""
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
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o")
GPT_ENABLED = os.getenv("ENABLE_GPT_WALLET_INSIGHTS", "false").lower() == "true"

async def gpt_wallet_summary(wallet_data: str):
    if not GPT_ENABLED:
        return "🧠 GPT Wallet Insights are disabled."

    prompt = (
        "You are an expert blockchain analyst. Analyze the following XRPL wallet activity. "
        "Summarize the wallet’s behavior, risk profile, trading habits, and potential classification "
        "(e.g., holder, sniper, whale, bot, LP provider).\n\n"
        f"{wallet_data}"
    )
    try:
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a blockchain wallet analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.6,
        )
        return "🧠 GPT Insight:\n" + response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ GPT error: {str(e)}"

async def gpt_token_holders_analysis(holder_data: str):
    if not GPT_ENABLED:
        return "🧠 GPT Token Holder Analysis is disabled."

    prompt = (
        "You are an expert XRPL token analyst. Analyze this list of token holders and their holdings. "
        "Identify possible whales, influencers, suspicious patterns, and concentration risk:\n\n"
        f"{holder_data}"
    )
    try:
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You analyze token holder distribution."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=350,
            temperature=0.5,
        )
        return "📊 Holder Analysis:\n" + response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ GPT error: {str(e)}"

async def gpt_sentiment_from_trades(trade_logs: str):
    if not GPT_ENABLED:
        return "🧠 GPT Sentiment Scan is disabled."

    prompt = (
        "You are a sentiment AI. Given this recent trading log from the XRPL, determine whether the market "
        "is trending bullish, bearish, or uncertain. Provide a brief justification:\n\n"
        f"{trade_logs}"
    )
    try:
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You analyze crypto trading sentiment."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.4,
        )
        return "📈 Sentiment Analysis:\n" + response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ GPT error: {str(e)}"

