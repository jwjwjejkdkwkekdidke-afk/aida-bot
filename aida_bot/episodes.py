import json
from config import BASE_DIR

def load_episodes() -> list[dict]:
    with open(BASE_DIR / "episodes.json", encoding="utf-8") as f:
        return json.load(f)

def get_episode(number: int) -> dict | None:
    for ep in load_episodes():
        if ep["number"] == number:
            return ep
    return None
