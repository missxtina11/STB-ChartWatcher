<<<<<<< HEAD
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
=======
>>>>>>> 8f969e0 (Push full STB ChartWatcher bot)
# utils/token_store.py
"""
Simple JSON-backed token watch-list.
Each Telegram chat (ID) → {TOKEN_CODE: ISSUER}.
"""

import json
<<<<<<< HEAD
import os
>>>>>>> 517b8b9 (Remove mis-named _init_.py file)
>>>>>>> b24d42e (Remove mis-named _init_.py file)
=======
>>>>>>> 8f969e0 (Push full STB ChartWatcher bot)
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
<<<<<<< HEAD
=======
# Public helpers -----------------------------------------------------

>>>>>>> 9ebc290 (Add token_store for per-chat watch-lists)
=======
# Public helpers -----------------------------------------------------

=======
>>>>>>> 517b8b9 (Remove mis-named _init_.py file)
>>>>>>> b24d42e (Remove mis-named _init_.py file)
=======

# public helpers -----------------------------------------------------

>>>>>>> 8f969e0 (Push full STB ChartWatcher bot)
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
<<<<<<< HEAD
=======
    """Return {TOKEN: issuer} for this chat, or {} if none."""
>>>>>>> 9ebc290 (Add token_store for per-chat watch-lists)
=======
    """Return {TOKEN: issuer} for this chat, or {} if none."""
=======
>>>>>>> 517b8b9 (Remove mis-named _init_.py file)
>>>>>>> b24d42e (Remove mis-named _init_.py file)
=======
    """Return {TOKEN: issuer} or {} if none."""
>>>>>>> 8f969e0 (Push full STB ChartWatcher bot)
    return _load().get(str(chat_id), {})

