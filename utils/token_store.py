<<<<<<< HEAD
<<<<<<< HEAD
# utils/token_store.py
import json
import os
=======
=======
>>>>>>> b24d42e (Remove mis-named _init_.py file)
"""
Simple JSON-backed token watch-list store.
Each Telegram chat gets its own dict of {TOKEN_CODE: ISSUER}.
"""
import json
<<<<<<< HEAD
>>>>>>> 9ebc290 (Add token_store for per-chat watch-lists)
=======
=======
# utils/token_store.py
import json
import os
>>>>>>> 517b8b9 (Remove mis-named _init_.py file)
>>>>>>> b24d42e (Remove mis-named _init_.py file)
from pathlib import Path

_STORE_PATH = Path("data/token_watchlists.json")

def _load() -> dict:
    if _STORE_PATH.exists():
        return json.loads(_STORE_PATH.read_text())
    return {}

def _save(data: dict):
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STORE_PATH.write_text(json.dumps(data, indent=2))

<<<<<<< HEAD
<<<<<<< HEAD
=======
# Public helpers -----------------------------------------------------

>>>>>>> 9ebc290 (Add token_store for per-chat watch-lists)
=======
# Public helpers -----------------------------------------------------

=======
>>>>>>> 517b8b9 (Remove mis-named _init_.py file)
>>>>>>> b24d42e (Remove mis-named _init_.py file)
def add_token(chat_id: int, code: str, issuer: str):
    db = _load()
    db.setdefault(str(chat_id), {})[code.upper()] = issuer
    _save(db)

def remove_token(chat_id: int, code: str):
    db = _load()
    db.get(str(chat_id), {}).pop(code.upper(), None)
    _save(db)

def list_tokens(chat_id: int) -> dict:
<<<<<<< HEAD
<<<<<<< HEAD
=======
    """Return {TOKEN: issuer} for this chat, or {} if none."""
>>>>>>> 9ebc290 (Add token_store for per-chat watch-lists)
=======
    """Return {TOKEN: issuer} for this chat, or {} if none."""
=======
>>>>>>> 517b8b9 (Remove mis-named _init_.py file)
>>>>>>> b24d42e (Remove mis-named _init_.py file)
    return _load().get(str(chat_id), {})

