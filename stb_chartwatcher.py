<<<<<<< HEAD
# utils/chart_utils.py
import matplotlib.pyplot as plt
import os
import tempfile
from typing import Optional

# Where to save charts:
# 1) If CHART_OUTPUT_PATH is set in .env, use it
# 2) Otherwise, fall back to the OS temp directory
OUTPUT_DIR = os.getenv("CHART_OUTPUT_PATH") or tempfile.gettempdir()


def plot_holder_distribution(token_code: Optional[str] = None) -> str:
    """
    Create a placeholder holder-distribution pie chart
    for the specified token_code (argument is optional).

    Currently returns a static chart; replace with real data as needed.
    """
    # Dummy data (replace with real distribution later)
    holders = ["Top 1", "Top 2", "Others"]
    shares = [25, 15, 60]

    fig, ax = plt.subplots()
    ax.pie(shares, labels=holders, autopct="%1.1f%%")
    ax.set_title(f"{token_code or 'STB'} Holder Distribution")

    path = os.path.join(OUTPUT_DIR, f"{(token_code or 'STB').lower()}_holders_chart.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path
=======
# stb_chartwatcher.py
import asyncio
import logging
import os
from typing import Optional, Tuple

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
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

# ─────────────────────────────────────────────────────────
#  Setup
# ─────────────────────────────────────────────────────────
load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=os.getenv("TG_BOT_TOKEN"),
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)
dp = Dispatcher()


# ─────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────
def _resolve_token(chat_id: int, token_arg: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (token_code, issuer) or (None, error_msg)
    """
    watchlist = list_tokens(chat_id)
    if token_arg:
        token = token_arg.upper()
        if token not in watchlist:
            return None, f"❌ Token **{token}** is not in this chat’s watch-list."
        return token, watchlist[token]
    if watchlist:
        token, issuer = next(iter(watchlist.items()))
        return token, issuer
    return None, "⚠️ No tokens watched yet. Use `addtoken <CODE> <ISSUER>`."


# ─────────────────────────────────────────────────────────
#  Core / help
# ─────────────────────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "📊 *STB ChartWatcher Activated!*\n"
        "Track holders, whales, trades, and sentiment.\n"
        "Type `help` to view commands."
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        """
*🛰️ STB ChartWatcher — Commands*

holderschart [TOKEN] – Holder distribution chart  
whales [TOKEN]       – Top whale wallets  
bubbles [TOKEN]      – Bubble-map cluster summary  
buysells [TOKEN]     – Large buy/sell tracker  
sentiment [TOKEN]    – AI wallet sentiment  
price [TOKEN]        – Current token price  

addtoken <CODE> <ISSUER> – Add token to watch-list  
listtokens                – Show watched tokens  
removetoken <CODE>        – Remove token from list  

status – Bot status
""".strip()
    )


# ─────────────────────────────────────────────────────────
#  Token-management
# ─────────────────────────────────────────────────────────
@dp.message(Command("addtoken"))
async def cmd_addtoken(message: Message):
    parts = message.text.split()
    if len(parts) != 3:
        return await message.answer("Usage:  addtoken `<CODE>` `<ISSUER_ADDRESS>`")
    code, issuer = parts[1].upper(), parts[2]
    add_token(message.chat.id, code, issuer)
    await message.answer(f"✅ Added **{code}** to this chat’s watch-list.")


@dp.message(Command("listtokens"))
async def cmd_listtokens(message: Message):
    tokens = list_tokens(message.chat.id)
    if not tokens:
        return await message.answer("🗒️ No tokens are being watched yet.")
    lines = [f"• **{c}** → `{i}`" for c, i in tokens.items()]
    await message.answer("*Watched tokens:*\n" + "\n".join(lines))


@dp.message(Command("removetoken"))
async def cmd_removetoken(message: Message):
    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer("Usage:  removetoken `<CODE>`")
    code = parts[1].upper()
    remove_token(message.chat.id, code)
    await message.answer(f"🗑️ Removed **{code}** from the watch-list (if it existed).")


# ─────────────────────────────────────────────────────────
#  Analytics commands
# ─────────────────────────────────────────────────────────
@dp.message(Command("holderschart"))
async def cmd_holderschart(message: Message):
    token_arg = message.text.split()[1] if len(message.text.split()) > 1 else None
    code, err = _resolve_token(message.chat.id, token_arg)
    if code is None:
        return await message.answer(err)

    path = plot_holder_distribution(code)
    await message.answer_photo(types.FSInputFile(path), caption=f"📊 Holder chart for *{code}*")


@dp.message(Command("whales"))
async def cmd_whales(message: Message):
    token_arg = message.text.split()[1] if len(message.text.split()) > 1 else None
    code, err = _resolve_token(message.chat.id, token_arg)
    if code is None:
        return await message.answer(err)

    data = await get_whale_data(code)
    await message.answer(f"🐳 *{code} Whales:*\n{data}")


@dp.message(Command("bubbles"))
async def cmd_bubbles(message: Message):
    token_arg = message.text.split()[1] if len(message.text.split()) > 1 else None
    code, err = _resolve_token(message.chat.id, token_arg)
    if code is None:
        return await message.answer(err)

    data = await get_bubble_map(code)
    await message.answer(f"🧠 *{code} Bubble Map:*\n{data}")


@dp.message(Command("buysells"))
async def cmd_buysells(message: Message):
    token_arg = message.text.split()[1] if len(message.text.split()) > 1 else None
    code, err = _resolve_token(message.chat.id, token_arg)
    if code is None:
        return await message.answer(err)

    data = await get_big_txns(code)
    await message.answer(f"💸 *{code} Large Trades:*\n{data}")


@dp.message(Command("sentiment"))
async def cmd_sentiment(message: Message):
    token_arg = message.text.split()[1] if len(message.text.split()) > 1 else None
    code, err = _resolve_token(message.chat.id, token_arg)
    if code is None:
        return await message.answer(err)

    data = await get_sentiment(code)
    await message.answer(data)


@dp.message(Command("price"))
async def cmd_price(message: Message):
    token_arg = message.text.split()[1] if len(message.text.split()) > 1 else None
    code, err = _resolve_token(message.chat.id, token_arg)
    if code is None:
        return await message.answer(err)

    price = await fetch_price(code)
    await message.answer(f"💰 *{code} Price:* `{price}`")


@dp.message(Command("status"))
async def cmd_status(message: Message):
    await message.answer("✅ STB ChartWatcher is online and operational.")


# ─────────────────────────────────────────────────────────
#  Entrypoint
# ─────────────────────────────────────────────────────────
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
>>>>>>> ec10f73 (Clean up bytecode and cache)

