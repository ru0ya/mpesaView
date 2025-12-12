import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App Configuration
APP_NAME = "M-Pesa Analyzer Pro"
APP_VERSION = "1.0.0"
PAGE_CONFIG = {
    "page_title": APP_NAME,
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Transaction Categories
CATEGORIES = [
    "Sent to M-Pesa",
    "Received M-Pesa",
    "Pay Bill",
    "Buy Goods",
    "Airtime",
    "Withdraw Cash",
    "Deposit",
    "Bank Transfer",
    "Loan",
    "Other"
]

# Chart Themes
THEME_COLORS = [
    "#00C49F", # Green (Income)
    "#FF8042", # Orange (Expense)
    "#0088FE", # Blue
    "#FFBB28", # Yellow
    "#FF6B6B", # Red
    "#8884d8", # Purple
]
