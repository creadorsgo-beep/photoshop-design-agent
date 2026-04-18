"""
Persists and retrieves client style guides as JSON files in the clients/ directory.
Each client gets one file: clients/{slug}.json
"""

import json
import os
import re
from datetime import datetime


CLIENTS_DIR = "clients"


def _slug(name: str) -> str:
    """Convert a client name to a safe filename slug."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower().strip()).strip("_")


def _client_path(client_name: str) -> str:
    os.makedirs(CLIENTS_DIR, exist_ok=True)
    return os.path.join(CLIENTS_DIR, f"{_slug(client_name)}.json")


def save_client_style(client_name: str, style_guide: dict) -> dict:
    """
    Persist a style guide dict under the given client name.
    Overwrites any previously saved guide for this client.
    """
    path = _client_path(client_name)
    payload = {
        "client_name": client_name,
        "saved_at": datetime.now().isoformat(),
        "style_guide": style_guide,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return {"status": "saved", "client": client_name, "path": path}


def load_client_style(client_name: str) -> dict:
    """
    Load a previously saved style guide for a client.
    Raises FileNotFoundError if the client doesn't exist.
    """
    path = _client_path(client_name)
    if not os.path.exists(path):
        available = list_clients()
        raise FileNotFoundError(
            f"No style guide found for '{client_name}'. "
            f"Available clients: {[c['client_name'] for c in available]}"
        )
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    return payload


def list_clients() -> list[dict]:
    """Return a list of all saved clients with their save dates."""
    os.makedirs(CLIENTS_DIR, exist_ok=True)
    clients = []
    for fname in sorted(os.listdir(CLIENTS_DIR)):
        if fname.endswith(".json"):
            fpath = os.path.join(CLIENTS_DIR, fname)
            try:
                with open(fpath, encoding="utf-8") as f:
                    data = json.load(f)
                clients.append({
                    "client_name": data.get("client_name", fname),
                    "saved_at": data.get("saved_at", ""),
                    "file": fpath,
                })
            except Exception:
                pass
    return clients
