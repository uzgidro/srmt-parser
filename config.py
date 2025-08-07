import os
from dotenv import load_dotenv

load_dotenv()

STOCK_FORWARD_URL = os.getenv("STOCK_FORWARD_URL", "http://localhost:9010/sc/stock")
MODSNOW_FORWARD_URL = os.getenv("MODSNOW_FORWARD_URL", "http://localhost:9010/sc/modsnow")

API_KEY = os.getenv("API_KEY", "default-key-if-not-set")