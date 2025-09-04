import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "AI Finance Tracker")
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "finance.db")

YELLOW_COLORS = ["#f59e0b", "#fbbf24", "#facc15", "#fde047", "#fef08a", "#fffbeb"]
