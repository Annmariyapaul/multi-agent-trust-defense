import json
from pathlib import Path

STORE = Path("data/trust_store.json")
STORE.parent.mkdir(parents=True, exist_ok=True)


def load_history():
    if STORE.exists():
        return json.loads(STORE.read_text())
    return {}


def save_history(history):
    STORE.write_text(json.dumps(history, indent=2))


def append_round(agent_name, positive, negative):
    history = load_history()
    rounds = history.get(agent_name, [])
    rounds.insert(0, {"positive": positive, "negative": negative})
    history[agent_name] = rounds[:20]   # keep last 20
    save_history(history)
    return history[agent_name]