import os
from dotenv import load_dotenv

load_dotenv()

STOCK_FORWARD_URL = os.getenv("STOCK_FORWARD_URL")
MODSNOW_FORWARD_URL = os.getenv("MODSNOW_FORWARD_URL")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

API_KEY = os.getenv("API_KEY")