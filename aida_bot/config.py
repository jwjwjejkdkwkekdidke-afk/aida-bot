import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
PRICE_RUB = int(os.getenv("PRICE_RUB", "499"))
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}

# Реквизиты для оплаты (можно переопределить через переменную окружения CARD_NUMBER)
CARD_NUMBER = os.getenv("CARD_NUMBER", "2204120123651537")

SEASON_TITLE = "Айда! 1 Сезон"
