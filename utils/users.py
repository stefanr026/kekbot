import asyncio
import json
import os
from time import time

from config import COMMAND_PREFIX, USER_RESPAWN_TIME
from utils.duration import format_duration
from utils.lookup import find_by_name

USERS_FILE = "data/users.json"

# Serializes read-modify-write access to USERS_FILE so concurrent commands
# (or the respawn runner) can't clobber each other's changes with stale data.
users_lock = asyncio.Lock()


def _ensure_users_file():
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)


def load_users():
    _ensure_users_file()
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    _ensure_users_file()
    # Write to a temp file then atomically replace, so a concurrent load_users()
    # can never observe a half-written/truncated file.
    tmp_path = f"{USERS_FILE}.tmp"
    with open(tmp_path, "w") as f:
        json.dump(users, f, indent=4)
    os.replace(tmp_path, USERS_FILE)


def add_user(username):
    users = load_users()

    if not any(user["username"] == username for user in users):
        users.append({
            "username": username,
            "twitch_channel": "https://twitch.com/" + username,
            "last_seen": time(),
            "hp": 100,
            "death_time": 0,
            "armor": 0,
            "energy": 100,
            "duel_wins": 0,
            "duel_losses": 0,
            "balance": 0,
            "coinflip_wins": 0,
            "coinflip_losses": 0,
            "coinflip_biggest_win": 0,
            "coinflip_biggest_loss": 0,
            "bonus_timer": 0,
            "total_claimed": 0,
            "steal_timer": 0,
            "portfolio": [],
            "xp": 0,
            "level_reached_at": int(time())
        })

        save_users(users)


def get_user(username):
    users = load_users()

    for user in users:
        if user["username"] == username:
            return user
        
    add_user(username)

    return get_user(username)


def set_user(username, user_data):
    users = load_users()

    for i, user in enumerate(users):
        if user["username"] == username:
            users[i] = user_data
            break

    save_users(users)
    
def update_last_seen(username, timestamp):
    users = load_users()

    for user in users:
        if user["username"] == username:
            user["last_seen"] = timestamp
            break

    save_users(users)


def find_user(users, username):
    return find_by_name(users, username, key="username")


def get_user_by_name(username, users=None):
    return find_user(users if users is not None else load_users(), username)


def respawn_remaining(user):
    return max(0, user["death_time"] + USER_RESPAWN_TIME - time())


async def reply_if_dead(reply, viewer, user, *, is_self=False):
    if user["hp"] > 0:
        return False

    duration = format_duration(respawn_remaining(user))

    if is_self:
        await reply(
            f"@{viewer} You are dead KEKP | You will respawn in {duration}"
        )
    else:
        await reply(
            f"@{viewer} User '{user['username']}' is dead KEKP | "
            f"Will respawn in {duration}"
        )

    return True


async def reply_if_not_registered(reply, viewer, user, *, target=None, message=None):
    if user is not None:
        return False

    if message:
        await reply(message)
    elif target is None or target.lower() == viewer.lower():
        await reply(
            f"@{viewer} You are not registered. "
            f"Use {COMMAND_PREFIX}kek to register KEKP"
        )
    else:
        await reply(
            f"@{viewer} User '{target}' is not registered. "
            f"Use {COMMAND_PREFIX}kek to register KEKP"
        )

    return True


def hp_bar(hp, max_hp=100, width=10):
    step = max_hp // width
    offset = step // 2 - 1
    filled = max(0, min(width, (hp + offset) // step))

    return "█" * filled + "░" * (width - filled)


def xp_bar(xp, width=10):
    from utils.xp import get_xp_progress
    progress, needed = get_xp_progress(xp)
    
    if needed == 0:  # Maxed out at MAX_LEVEL
        return "█" * width
    
    step = needed // width
    offset = step // 2 - 1
    filled = max(0, min(width, (progress + offset) // step))
    
    return "█" * filled + "░" * (width - filled)
