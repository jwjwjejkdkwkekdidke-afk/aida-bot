import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"

BOT_TOKEN = os.getenv("BOT_TOKEN", "8225960486:AAF9OJrUbK_L5oGnbX1tb5sreX5-D3PP9nQ")
PRICE_RUB = int(os.getenv("PRICE_RUB", "499"))
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "8052913358").split(",") if x.strip()}

# Реквизиты для оплаты (можно переопределить через переменную окружения CARD_NUMBER)
CARD_NUMBER = os.getenv("CARD_NUMBER", "2204120123651537")

SEASON_TITLE = "Айда! 1 Сезон"
