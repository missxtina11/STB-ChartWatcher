# utils/token_store.py
import json
import os
from pathlib import Path

_STORE_PATH = Path("data/token_watchlists.json")

def _load() -> dict:
    if _STORE_PATH.exists():
        return json.loads(_STORE_PATH.read_text())
    return {}

def _save(data: dict):
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STORE_PATH.write_text(json.dumps(data, indent=2))

def add_token(chat_id: int, code: str, issuer: str):
    db = _load()
    db.setdefault(str(chat_id), {})[code.upper()] = issuer
    _save(db)

def remove_token(chat_id: int, code: str):
    db = _load()
    db.get(str(chat_id), {}).pop(code.upper(), None)
    _save(db)

def list_tokens(chat_id: int) -> dict:
    return _load().get(str(chat_id), {})

