from time import time


XP_PER_LEVEL = 1000
MAX_LEVEL = 30
MAX_XP = XP_PER_LEVEL * (MAX_LEVEL - 1)
XP_PER_KEK = 1  # $convert rate: 10 xp -> 1 kek, one-way only


def get_level(xp):
    return min(xp, MAX_XP) // XP_PER_LEVEL + 1


def get_kek_bonus(level):
    return level


def record_level_change(user, previous_xp, timestamp=None):
    previous_level = get_level(previous_xp)
    current_level = get_level(user.get("xp", 0))

    if current_level != previous_level:
        user["level_reached_at"] = int(time() if timestamp is None else timestamp)


def add_xp(user, amount):
    before = user.get("xp", 0)
    user["xp"] = min(before + amount, MAX_XP)
    record_level_change(user, before)
    return user["xp"] - before


def apply_kek_multiplier(user, amount):
    level = get_level(user.get("xp", 0))
    return amount + get_kek_bonus(level)


def get_xp_progress(xp):
    level = get_level(xp)
    if level >= MAX_LEVEL:
        return 0, 0

    return xp - (level - 1) * XP_PER_LEVEL, XP_PER_LEVEL

