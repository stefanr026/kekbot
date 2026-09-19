import json
import os

STOCKS_FILE = "data/stocks.json"


def _ensure_stocks_file():
    os.makedirs(os.path.dirname(STOCKS_FILE), exist_ok=True)
    if not os.path.exists(STOCKS_FILE):
        with open(STOCKS_FILE, "w") as f:
            json.dump([], f)


def load_stocks():
    _ensure_stocks_file()
    with open(STOCKS_FILE, "r") as f:
        return json.load(f)
    
def save_stocks(stocks):
    _ensure_stocks_file()
    tmp_path = f"{STOCKS_FILE}.tmp"
    with open(tmp_path, "w") as f:
        json.dump(stocks, f, indent=4)
    os.replace(tmp_path, STOCKS_FILE)