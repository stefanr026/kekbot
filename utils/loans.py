import json
import os

LOANS_FILE = "data/loans.json"


def _ensure_loans_file():
    os.makedirs(os.path.dirname(LOANS_FILE), exist_ok=True)
    if not os.path.exists(LOANS_FILE):
        with open(LOANS_FILE, "w") as f:
            json.dump([], f)


def load_loans():
    _ensure_loans_file()
    with open(LOANS_FILE, "r") as f:
        return json.load(f)

def save_loans(loans):
    _ensure_loans_file()
    tmp_path = f"{LOANS_FILE}.tmp"
    with open(tmp_path, "w") as f:
        json.dump(loans, f, indent=4)
    os.replace(tmp_path, LOANS_FILE)
