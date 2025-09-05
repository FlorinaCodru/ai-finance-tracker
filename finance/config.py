import os
from dotenv import load_dotenv

load_dotenv()
APP_NAME = os.getenv("APP_NAME", "AI Finance Tracker")
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "finance.db")
YELLOW_COLORS = ["#fbbf24", "#facc15", "#f59e0b", "#fde047", "#fffbeb",  "#fef08a"]
