# stb_chartwatcher.py
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

# ───────────────────  simple wallet store  ─────────────────
# Just for demo until a real DB is wired:
_WALLET_WATCH: Dict[int, Set[str]] = {}  # chat_id → {wallet, …}


def _add_wallet(chat_id: int, wallet: str):
    _WALLET_WATCH.setdefault(chat_id, set()).add(wallet)


def _list_wallets(chat_id: int) -> Set[str]:
    return _WALLET_WATCH.get(chat_id, set())


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
    await bot.set_my_commands(
        [
            BotCommand("help", "Show help"),
            BotCommand("addtoken", "Add a token"),
            BotCommand("listtokens", "List watched tokens"),
            BotCommand("removetoken", "Remove a token"),
            BotCommand("holderschart", "Holder chart"),
            BotCommand("whales", "Whale wallets"),
            BotCommand("bubbles", "Bubble map"),
            BotCommand("buysells", "Large trades"),
            BotCommand("sentiment", "AI sentiment"),
            BotCommand("price", "Token price"),
            BotCommand("addwallet", "Watch a wallet"),
            BotCommand("gptwallet", "GPT wallet insight"),
            BotCommand("gptsentiment", "GPT sentiment scan"),
            BotCommand("gpt_holders", "GPT holder analysis"),
            BotCommand("status", "Bot status"),
        ]
    )
    await msg.answer(
        "📊 *STB ChartWatcher Activated!*\n"
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

addtoken <CODE> <ISSUER> – Add token  
listtokens                – List tokens  
removetoken <CODE>        – Remove token  

addwallet <ADDRESS>       – Watch XRPL wallet  
gptwallet [ADDRESS]       – GPT wallet summary  
gptsentiment              – GPT sentiment on watched wallets  
gpt_holders               – GPT analysis of token holders  

status – Bot status
""".strip()
    )

# ───────────── Token list management ─────────────
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

# ───────────── Wallet watch management ─────────────
@dp.message(Command("addwallet"))
async def cmd_addwallet(msg: Message):
    p = msg.text.split()
    if len(p) != 2:
        return await msg.answer("Usage: `addwallet <XRPL_WALLET_ADDRESS>`")
    _add_wallet(msg.chat.id, p[1])
    await msg.answer("👀 Wallet added to watch-list.")


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


# ───────────── GPT-powered stubs ─────────────
@dp.message(Command("gptwallet"))
async def cmd_gptwallet(msg: Message):
    target = msg.text.split()[1] if len(msg.text.split()) > 1 else None
    if not target:
        wallets = _list_wallets(msg.chat.id)
        if not wallets:
            return await msg.answer("No wallet given and none watched yet. Use `addwallet`.")
        target = next(iter(wallets))
    await msg.answer(f"🧠 GPT wallet insight for `{target}` (stub).")


@dp.message(Command("gptsentiment"))
async def cmd_gptsentiment(msg: Message):
    await msg.answer("🤖 GPT sentiment scan across watched wallets (stub).")


@dp.message(Command("gpt_holders"))
async def cmd_gptholders(msg: Message):
    tok, err = _resolve_token(msg.chat.id, None)
    if tok is None:
        return await msg.answer(err)
    await msg.answer(f"📈 GPT holder analysis for *{tok}* (stub).")


# ───────────── Misc  ─────────────
@dp.message(Command("status"))
async def cmd_status(msg: Message):
    await msg.answer("✅ STB ChartWatcher is online.")


@dp.message()
async def fallback(msg: Message):
    await msg.answer("🤖 I didn’t understand that. Try /help to see available commands.")


# ─────────────────── Entrypoint ───────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

