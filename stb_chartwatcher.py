# stb_chartwatcher.py
"""
STB-ChartWatcher – Telegram bot for XRPL token analytics
Requires:
  • python-telegram-bot aiogram v3
  • openai  >=1.0   (for GPT features)
  • utils/… helper modules shipped with this repo

Set TG_BOT_TOKEN and OPENAI_API_KEY in your .env
"""

import asyncio
import logging
import os
from typing import Optional, Tuple, Dict, Set

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, BotCommand
from dotenv import load_dotenv

# Local helpers
from utils.chart_utils import plot_holder_distribution
from utils.price_utils import fetch_price
from utils.xrpl_utils import (
    get_whale_data,
    get_bubble_map,
    get_big_txns,
    get_sentiment,
    get_wallet_tx_history,
    get_holder_list_summary,
    get_recent_trade_logs,
    gpt_wallet_summary,
    gpt_token_holders_analysis,
    gpt_sentiment_from_trades,
)
from utils.token_store import add_token, remove_token, list_tokens

# ─────────────────────────── Setup ────────────────────────────
load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=os.getenv("TG_BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)
dp = Dispatcher()

# ─────────── Simple in-memory wallet watch (demo) ────────────
_WALLET_WATCH: Dict[int, Set[str]] = {}  # chat_id → {wallet,…}


def _add_wallet(chat_id: int, addr: str):
    _WALLET_WATCH.setdefault(chat_id, set()).add(addr)


def _list_wallets(chat_id: int) -> Set[str]:
    return _WALLET_WATCH.get(chat_id, set())


# ────────────────── helper: resolve token ────────────────────
def _resolve_token(chat_id: int, arg: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (token_code, issuer) or (None, error_msg)
    """
    wl = list_tokens(chat_id)
    if arg:
        t = arg.upper()
        if t not in wl:
            return None, f"❌ Token **{t}** is not in this chat’s watch-list."
        return t, wl[t]
    if wl:
        t, iss = next(iter(wl.items()))
        return t, iss
    return None, "⚠️ No tokens watched yet. Use `addtoken <CODE> <ISSUER>`."


# ─────────────────────── /start & /help ───────────────────────
@dp.message(Command("start"))
async def cmd_start(m: Message):

from aiogram.types import BotCommand

# …

@dp.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer(
        "📊 *STB ChartWatcher Activated!*  \n"
        "Track holders, whales, trades, and sentiment.\n"
        "Type `help` for commands."
    )

    # Register the main commands with Telegram (done once every /start)
    await bot.set_my_commands(
        [
            BotCommand(command="help", description="Show help"),
            BotCommand(command="addtoken", description="Add token to watch-list"),
            BotCommand(command="listtokens", description="List watched tokens"),
            BotCommand(command="removetoken", description="Remove token"),
            BotCommand(command="holderschart", description="Holder pie chart"),
            BotCommand(command="whales", description="Top wallets"),
            BotCommand(command="bubbles", description="Wallet clusters"),
            BotCommand(command="buysells", description="Large trades"),
            BotCommand(command="sentiment", description="AI sentiment"),
            BotCommand(command="price", description="Token price"),
            BotCommand(command="status", description="Bot status"),
        ]
    )

    await bot.set_my_commands(
        [
            BotCommand("help", "Show help"),
            BotCommand("addtoken", "Add a token"),
            BotCommand("listtokens", "List tokens"),
            BotCommand("removetoken", "Remove token"),
            BotCommand("addwallet", "Watch a wallet"),
            BotCommand("holderschart", "Holder chart"),
            BotCommand("whales", "Whale wallets"),
            BotCommand("bubbles", "Bubble map"),
            BotCommand("buysells", "Large trades"),
            BotCommand("sentiment", "AI sentiment"),
            BotCommand("price", "Token price"),
            BotCommand("gptwallet", "GPT wallet summary"),
            BotCommand("gptsentiment", "GPT sentiment"),
            BotCommand("gpt_holders", "GPT holder analysis"),
            BotCommand("status", "Bot status"),
        ]
    )
    await m.answer(
        "📊 *STB ChartWatcher Activated!*\n"
        "Track holders, whales, trades, and sentiment.\n"
        "Type `help` for commands."
    )


@dp.message(Command("help"))
async def cmd_help(m: Message):
    await m.answer(
        """
*🛰️ STB ChartWatcher — Commands*

holderschart [TOKEN] – Holder pie-chart  
whales [TOKEN]       – Top wallets  
bubbles [TOKEN]      – Wallet clusters  
buysells [TOKEN]     – Large trades  
sentiment [TOKEN]    – AI sentiment  
price [TOKEN]        – Current price  

addtoken <CODE> <ISSUER> – Add token  
listtokens                – List tokens  
removetoken <CODE>        – Remove token  

addwallet <ADDRESS>       – Watch wallet  
gptwallet [ADDRESS]       – GPT wallet summary  
gptsentiment [TOKEN]      – GPT sentiment  
gpt_holders [TOKEN]       – GPT holder analysis  

status – Bot status
""".strip()
    )

# ─────────────── Token-watch commands ───────────────
@dp.message(Command("addtoken"))
async def cmd_addtoken(m: Message):
    p = m.text.split()
    if len(p) != 3:
        return await m.answer("Usage: `addtoken <CODE> <ISSUER>`")
    code, issuer = p[1].upper(), p[2]
    add_token(m.chat.id, code, issuer)
    await m.answer(f"✅ Added **{code}** to watch-list.")


@dp.message(Command("listtokens"))
async def cmd_listtokens(m: Message):
    wl = list_tokens(m.chat.id)
    if not wl:
        return await m.answer("🗒️ No tokens watched.")
    await m.answer(
        "*Watched tokens:*\n" + "\n".join(f"• **{c}** → `{i}`" for c, i in wl.items())
    )


@dp.message(Command("removetoken"))
async def cmd_removetoken(m: Message):
    p = m.text.split()
    if len(p) != 2:
        return await m.answer("Usage: `removetoken <CODE>`")
    remove_token(m.chat.id, p[1].upper())
    await m.answer("🗑️ Removed (if it existed).")

# ─────────────── Wallet-watch commands ───────────────
@dp.message(Command("addwallet"))
async def cmd_addwallet(m: Message):
    p = m.text.split()
    if len(p) != 2:
        return await m.answer("Usage: `addwallet <XRPL_ADDRESS>`")
    _add_wallet(m.chat.id, p[1])
    await m.answer("👀 Wallet added to watch-list.")

# ─────────────── Analytics commands ───────────────
@dp.message(Command("holderschart"))
async def cmd_holderschart(m: Message):
    tok, err = _resolve_token(m.chat.id, m.text.split()[1] if len(m.text.split()) > 1 else None)
    if tok is None:
        return await m.answer(err)
    path = plot_holder_distribution(tok)
    await m.answer_photo(types.FSInputFile(path), caption=f"📊 Holder chart for *{tok}*")


@dp.message(Command("whales"))
async def cmd_whales(m: Message):
    tok, err = _resolve_token(m.chat.id, m.text.split()[1] if len(m.text.split()) > 1 else None)
    if tok is None:
        return await m.answer(err)
    await m.answer(f"🐳 *{tok} Whales:*\n" + await get_whale_data(tok))


@dp.message(Command("bubbles"))
async def cmd_bubbles(m: Message):
    tok, err = _resolve_token(m.chat.id, m.text.split()[1] if len(m.text.split()) > 1 else None)
    if tok is None:
        return await m.answer(err)
    await m.answer(f"🧠 *{tok} Bubble Map:*\n" + await get_bubble_map(tok))


@dp.message(Command("buysells"))
async def cmd_buysells(m: Message):
    tok, err = _resolve_token(m.chat.id, m.text.split()[1] if len(m.text.split()) > 1 else None)
    if tok is None:
        return await m.answer(err)
    await m.answer(f"💸 *{tok} Trades:*\n" + await get_big_txns(tok))


@dp.message(Command("sentiment"))
async def cmd_sentiment(m: Message):
    tok, err = _resolve_token(m.chat.id, m.text.split()[1] if len(m.text.split()) > 1 else None)
    if tok is None:
        return await m.answer(err)
    await m.answer(await get_sentiment(tok))


@dp.message(Command("price"))
async def cmd_price(m: Message):
    tok, err = _resolve_token(m.chat.id, m.text.split()[1] if len(m.text.split()) > 1 else None)
    if tok is None:
        return await m.answer(err)
    await m.answer(f"💰 *{tok} Price:* `{await fetch_price(tok)}`")

# ─────────────── GPT-powered commands ───────────────
@dp.message(Command("gptwallet"))
async def cmd_gptwallet(m: Message):
    target = m.text.split()[1] if len(m.text.split()) > 1 else None
    if not target:
        wallets = _list_wallets(m.chat.id)
        if not wallets:
            return await m.answer("No wallet given and none watched. Use `addwallet`.")
        target = next(iter(wallets))
    tx = await get_wallet_tx_history(target)
    summary = await gpt_wallet_summary(tx)
    await m.answer(f"*GPT Wallet Insight for `{target}`*\n\n{summary}")


@dp.message(Command("gptsentiment"))
async def cmd_gptsentiment(m: Message):
    tok, err = _resolve_token(m.chat.id, m.text.split()[1] if len(m.text.split()) > 1 else None)
    if tok is None:
        return await m.answer(err)
    logs = await get_recent_trade_logs(tok)
    out = await gpt_sentiment_from_trades(logs)
    await m.answer(f"*GPT Sentiment for {tok}*\n\n{out}")


@dp.message(Command("gpt_holders"))
async def cmd_gpt_holders(m: Message):
    tok, err = _resolve_token(m.chat.id, m.text.split()[1] if len(m.text.split()) > 1 else None)
    if tok is None:
        return await m.answer(err)
    stats = await get_holder_list_summary(tok)
    out = await gpt_token_holders_analysis(stats)
    await m.answer(f"*GPT Holder Analysis for {tok}*\n\n{out}")

# ─────────────── Misc ───────────────
@dp.message(Command("status"))
async def cmd_status(m: Message):
    await m.answer("✅ STB ChartWatcher is online.")


@dp.message()
async def fallback(m: Message):
    await m.answer("🤖 I didn’t understand that. Try /help.")


# ───────────────── Entrypoint ─────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



