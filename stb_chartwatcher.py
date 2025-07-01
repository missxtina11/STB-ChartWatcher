# stb_chartwatcher.py
import asyncio
import logging
import os
from typing import Optional, Tuple

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

from utils.chart_utils import plot_holder_distribution
from utils.price_utils import fetch_price
from utils.xrpl_utils import (
    get_whale_data,
    get_bubble_map,
    get_big_txns,
    get_sentiment,
)
from utils.token_store import add_token, remove_token, list_tokens

# ────────────────────────── Setup ──────────────────────────
load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=os.getenv("TG_BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)
dp = Dispatcher()


# ─────────────────── Helper: resolve token ─────────────────
def _resolve_token(chat_id: int, token_arg: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    watchlist = list_tokens(chat_id)
    if token_arg:
        tok = token_arg.upper()
        if tok not in watchlist:
            return None, f"❌ Token **{tok}** is not in this chat’s watch-list."
        return tok, watchlist[tok]
    if watchlist:
        tok, issuer = next(iter(watchlist.items()))
        return tok, issuer
    return None, "⚠️ No tokens watched yet. Use `addtoken <CODE> <ISSUER>`."


# ────────────────────── Core commands ──────────────────────
@dp.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer(
        "📊 *STB ChartWatcher Activated!*  \n"
        "Track holders, whales, trades, and sentiment.\n"
        "Type `help` for commands."
    )


@dp.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(
        """
*🛰️ STB ChartWatcher — Commands*

holderschart [TOKEN] – Holder distribution  
whales [TOKEN]       – Top wallets  
bubbles [TOKEN]      – Wallet clusters  
buysells [TOKEN]     – Large trades  
sentiment [TOKEN]    – AI sentiment  
price [TOKEN]        – Current price  

addtoken <CODE> <ISSUER> – Add to watch-list  
listtokens                – Show watched tokens  
removetoken <CODE>        – Remove token  
status                    – Bot status
""".strip()
    )


# ───────────── Token-list management ─────────────
@dp.message(Command("addtoken"))
async def cmd_addtoken(msg: Message):
    p = msg.text.split()
    if len(p) != 3:
        return await msg.answer("Usage: `addtoken <CODE> <ISSUER_ADDRESS>`")
    code, issuer = p[1].upper(), p[2]
    add_token(msg.chat.id, code, issuer)
    await msg.answer(f"✅ Added **{code}** to this chat’s watch-list.")


@dp.message(Command("listtokens"))
async def cmd_listtokens(msg: Message):
    t = list_tokens(msg.chat.id)
    if not t:
        return await msg.answer("🗒️ No tokens watched yet.")
    lines = [f"• **{c}** → `{i}`" for c, i in t.items()]
    await msg.answer("*Watched tokens:*\n" + "\n".join(lines))


@dp.message(Command("removetoken"))
async def cmd_removetoken(msg: Message):
    p = msg.text.split()
    if len(p) != 2:
        return await msg.answer("Usage: `removetoken <CODE>`")
    remove_token(msg.chat.id, p[1].upper())
    await msg.answer("🗑️ Removed from watch-list (if it existed).")


# ───────────── Analytics commands ─────────────
@dp.message(Command("holderschart"))
async def cmd_holderschart(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1:] and msg.text.split()[1])
    if tok is None:
        return await msg.answer(err)
    path = plot_holder_distribution(tok)
    await msg.answer_photo(types.FSInputFile(path), caption=f"📊 Holder chart for *{tok}*")


@dp.message(Command("whales"))
async def cmd_whales(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1:] and msg.text.split()[1])
    if tok is None:
        return await msg.answer(err)
    await msg.answer(f"🐳 *{tok} Whales:*\n" + await get_whale_data(tok))


@dp.message(Command("bubbles"))
async def cmd_bubbles(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1:] and msg.text.split()[1])
    if tok is None:
        return await msg.answer(err)
    await msg.answer(f"🧠 *{tok} Bubble Map:*\n" + await get_bubble_map(tok))


@dp.message(Command("buysells"))
async def cmd_buysells(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1:] and msg.text.split()[1])
    if tok is None:
        return await msg.answer(err)
    await msg.answer(f"💸 *{tok} Trades:*\n" + await get_big_txns(tok))


@dp.message(Command("sentiment"))
async def cmd_sentiment(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1:] and msg.text.split()[1])
    if tok is None:
        return await msg.answer(err)
    await msg.answer(await get_sentiment(tok))


@dp.message(Command("price"))
async def cmd_price(msg: Message):
    tok, err = _resolve_token(msg.chat.id, msg.text.split()[1:] and msg.text.split()[1])
    if tok is None:
        return await msg.answer(err)
    await msg.answer(f"💰 *{tok} Price:* `{await fetch_price(tok)}`")


@dp.message(Command("status"))
async def cmd_status(msg: Message):
    await msg.answer("✅ STB ChartWatcher is online.")


# ─────────────────── Entrypoint ───────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

