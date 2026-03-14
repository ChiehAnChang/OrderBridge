from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = f"sqlite:///{BASE_DIR}/orderbridge.db"

APP_NAME = "OrderBridge"
APP_VERSION = "0.1.0"
