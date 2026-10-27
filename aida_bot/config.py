import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Не задана переменная окружения {name}")
    return value


BOT_TOKEN = require_env("BOT_TOKEN")
PRICE_RUB = int(os.getenv("PRICE_RUB", "499"))
ADMIN_IDS = {int(x) for x in require_env("ADMIN_IDS").split(",") if x.strip()}

# Реквизиты для оплаты
CARD_NUMBER = require_env("CARD_NUMBER")

SEASON_TITLE = "Айда! 1 Сезон"
