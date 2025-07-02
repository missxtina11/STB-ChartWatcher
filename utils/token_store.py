# utils/token_store.py
"""
Simple per-chat token watch-list stored in data/token_watchlists.json

Functions
---------
add_token(chat_id: int, code: str, issuer: str)          -> None
remove_token(chat_id: int, code: str)                    -> None
list_tokens(chat_id: int)                                -> dict[code, issuer]
"""

import json
import os
from pathlib import Path
from threading import Lock

_LOCK = Lock()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

STORE_PATH = DATA_DIR / "token_watchlists.json"


def _load() -> dict:
    if STORE_PATH.exists():
        with STORE_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save(data: dict) -> None:
    with STORE_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ────────────────────────────────────────────────
def add_token(chat_id: int, code: str, issuer: str) -> None:
    """Add/update token for a Telegram chat."""
    with _LOCK:
        store = _load()
        chat_key = str(chat_id)
        store.setdefault(chat_key, {})[code.upper()] = issuer
        _save(store)


def remove_token(chat_id: int, code: str) -> None:
    """Remove token from a chat’s watch-list (no error if absent)."""
    with _LOCK:
        store = _load()
        chat_key = str(chat_id)
        if chat_key in store and code.upper() in store[chat_key]:
            store[chat_key].pop(code.upper())
            if not store[chat_key]:  # delete chat entry if empty
                store.pop(chat_key)
            _save(store)


def list_tokens(chat_id: int) -> dict:
    """Return {CODE: issuer} for selected chat or {}."""
    with _LOCK:
        store = _load()
        return store.get(str(chat_id), {}).copy()

