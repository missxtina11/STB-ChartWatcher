# stb_chartwatcher.py
"""
STB-ChartWatcher – Telegram bot for XRPL token analytics
────────────────────────────────────────────────────────
* aiogram v3
* openai >= 1.0   (for GPT features)

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

# ───────────────────────── Setup ──────────────────────────
load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=os.getenv("TG_BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)
dp = Dispatcher()

# ────────── in-memory wallet watch list (demo) ───────────
_WALLET_WATCH: Dict[int, Set[str]] = {}  # chat_id → {wallet…}


def _add_wallet(chat_id: int, addr: str):
    _WALLET_WATCH.setdefault(chat_id, set()).add(addr)


def _list_wallets(chat_id: int) -> Set[str]:
    return _WALLET_WATCH.get(chat_id, set())


# ───────────── Markdown helper (escape dynamic text) ─────
def md_escape(text: str) -> str:
    """Escape _ and * so classic Markdown stays valid."""
    return text.replace("_", "\\_").replace("*", "\\*")


# ───────────── Resolve token helper ─────────────
def _resolve_token(chat_id: int, arg: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    wl = list_tokens(chat_id)
    if arg:
        t = arg.upper()
        if t not in wl:
            return None, f"❌ Token `{md_escape(t)}` is not in this chat’s watch-list."
        return t, wl[t]
    if wl:
        t, iss = next(iter(wl.items()))
        return t, iss
    return None, "⚠️ No tokens watched yet. Use `addtoken <CODE> <ISSUER>`."


# ─────────────── Help text (all commands back-ticked) ───────────────
HELP_TEXT = """
*🛰️ STB ChartWatcher — Commands*

`holderschart` [&lt;TOKEN&gt;] – Holder pie-chart  
`whales` [&lt;TOKEN&gt;]       – Top wallets  
`bubbles` [&lt;TOKEN&gt;]      – Wallet clusters  
`buysells` [&lt;TOKEN&gt;]     – Large trades  
`sentiment` [&lt;TOKEN&gt;]    – AI sentiment  
`price` [&lt;TOKEN&gt;]        – Current price  

`addtoken` &lt;CODE&gt; &lt;ISSUER&gt; – Add token  
`listtokens`                  – List tokens  
`removetoken` &lt;CODE&gt;        – Remove token  

`addwallet` &lt;ADDRESS&gt;       – Watch wallet  
`gptwallet` [&lt;ADDRESS&gt;]     – GPT wallet summary  
`gptsentiment` [&lt;TOKEN&gt;]   – GPT sentiment  
`gpt_holders` [&lt;TOKEN&gt;]    – GPT holder analysis  

`status` – Bot status
""".strip()


# ────────────────── /start & /help ──────────────────
@dp.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer(
        "📊 *STB ChartWatcher Activated!*  \n"
        "Track holders, whales, trades and sentiment.\n"
        "Type `/help` for the full list of commands."
    )

    # Register command menu (done once per /start)
    await bot.set_my_commands(
        [
            BotCommand("help", "Show help"),
            BotCommand("addtoken", "Add token"),
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


@dp.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(HELP_TEXT)


# ───────────── Token-list management ─────────────
@dp.message(Command("addtoken"))
async def cmd_addtoken(msg: Message):
    p = msg.text.split()
    if len(p) != 3:
        return await msg.answer("Usage: `addtoken <CODE> <ISSUER>`")
    code, issuer = p[1].upper(), p[2]
    add_token(msg.chat.id, code, issuer)
    await msg.answer(f"✅ Added `{md_escape(code)}` to watch-list.")


@dp.message(Command("listtokens"))
async def cmd_listtokens(msg: Message):
    wl = list_tokens(msg.chat.id)
    if not wl:
        return await msg.answer("🗒️ No tokens watched yet.")
    await msg.answer(
        "*Watched tokens:*\n" +
        "\n".join(f"• `{md_escape(c)}` → `{iss}`" for c, iss in wl.items())
    )


@dp.message(Command("removetoken"))
async def cmd_removetoken(msg: Message):
    p = msg.text.split()
    if len(p) != 2:
        return await msg.answer("Usage: `removetoken <CODE>`")
    remove_token(msg.chat.id, p[1].upper())
    await msg.answer("🗑️ Removed (if it existed).")


# ───────────── Wallet-watch commands ─────────────
@dp.message(Command("addwallet"))
async def cmd_addwallet(msg: Message):
    p = msg.text.split()
    if len(p) != 2:
        return await msg.answer("Usage: `addwallet <XRPL_ADDRESS>`")
    _add_wallet(msg.chat.id, p[1])
    await msg.answer("👀 Wallet added to watch-list.")


# ───────────── Analytics commands ─────────────
@dp.message(Command("holderschart"))
async def cmd_holderschart(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1] if len(msg.text.split()) > 1 else None)
    if tok is None:
        return await msg.answer(err)
    path = plot_holder_distribution(tok)
    await msg.answer_photo(
        types.FSInputFile(path),
        caption=f"📊 Holder chart for `{md_escape(tok)}`"
    )


@dp.message(Command("whales"))
async def cmd_whales(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1] if len(msg.text.split()) > 1 else None)
    if tok is None:
        return await msg.answer(err)
    await msg.answer(f"🐳 `{md_escape(tok)}` whales:\n" + await get_whale_data(tok))


@dp.message(Command("bubbles"))
async def cmd_bubbles(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1] if len(msg.text.split()) > 1 else None)
    if tok is None:
        return await msg.answer(err)
    await msg.answer(f"🧠 `{md_escape(tok)}` bubble map:\n" + await get_bubble_map(tok))


@dp.message(Command("buysells"))
async def cmd_buysells(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1] if len(msg.text.split()) > 1 else None)
    if tok is None:
        return await msg.answer(err)
    await msg.answer(f"💸 Large trades for `{md_escape(tok)}`:\n" + await get_big_txns(tok))


@dp.message(Command("sentiment"))
async def cmd_sentiment(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1] if len(msg.text.split()) > 1 else None)
    if tok is None:
        return await msg.answer(err)
    await msg.answer(await get_sentiment(tok))


@dp.message(Command("price"))
async def cmd_price(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1] if len(msg.text.split()) > 1 else None)
    if tok is None:
        return await msg.answer(err)
    await msg.answer(f"💰 `{md_escape(tok)}` price: `{await fetch_price(tok)}`")


# ───────────── GPT-powered commands ─────────────
@dp.message(Command("gptwallet"))
async def cmd_gptwallet(msg: Message):
    target = msg.text.split()[1] if len(msg.text.split()) > 1 else None
    if not target:
        wallets = _list_wallets(msg.chat.id)
        if not wallets:
            return await msg.answer("No wallet given and none watched. Use `addwallet`.")
        target = next(iter(wallets))
    tx = await get_wallet_tx_history(target)
    summary = await gpt_wallet_summary(tx)
    await msg.answer(f"*GPT Wallet Insight for `{md_escape(target)}`*\n\n{summary}")


@dp.message(Command("gptsentiment"))
async def cmd_gptsentiment(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1] if len(msg.text.split()) > 1 else None)
    if tok is None:
        return await msg.answer(err)
    logs = await get_recent_trade_logs(tok)
    out = await gpt_sentiment_from_trades(logs)
    await msg.answer(f"*GPT Sentiment for `{md_escape(tok)}`*\n\n{out}")


@dp.message(Command("gpt_holders"))
async def cmd_gpt_holders(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1] if len(msg.text.split()) > 1 else None)
    if tok is None:
        return await msg.answer(err)
    stats = await get_holder_list_summary(tok)
    out = await gpt_token_holders_analysis(stats)
    await msg.answer(f"*GPT Holder Analysis for `{md_escape(tok)}`*\n\n{out}")


# ───────────── Misc ─────────────
@dp.message(Command("status"))
async def cmd_status(msg: Message):
    await msg.answer("✅ STB ChartWatcher is online.")


@dp.message()
async def fallback(msg: Message):
    await msg.answer("🤖 I didn’t understand that. Try `/help`.")


# ───────────── Entrypoint ─────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

