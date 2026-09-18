import time

from utils.stocks import load_stocks
from utils.users import find_user, hp_bar, load_users, reply_if_not_registered, respawn_remaining
from utils.duration import format_duration
from utils.xp import get_kek_bonus, get_level, get_xp_progress
from commands.bonus import COOLDOWN_TIME
from config import COMMAND_PREFIX       

#TODO: Players can spend keks to upgrade their stats (hp, armor, strength) and these upgrades will be permanent. Players can also spend keks to reset their stats back to the default values. Players can also spend keks to reset their duel wins and losses back to 0. Players can also spend keks to reset their coinflip wins and losses back to 0. Players can also spend keks to reset their stock portfolio back to the default values. Players can also spend keks to reset their bonus timer back to 0. Players can also spend keks to reset their total claimed back to 0.

async def cmd_stats(username, reply, args=None):
    print(f"@{username} requested stats command with args: {args}")
    
    #! If second argument is provided, use it as the username to fetch stats for
    if args and len(args) > 0:
        username = args[0]

    users = load_users()
    user = find_user(users, username)

    if await reply_if_not_registered(
        reply, username, user,
        message=f"@{username} User not found. Use {COMMAND_PREFIX}kek to register KEKP"
    ):
        return

    biggest_win = (
    f"Biggest coinflip win: {user['coinflip_biggest_win']} 🍪 | "
    if user['coinflip_biggest_win'] != 0 else ""
    )

    biggest_loss = (
        f"Biggest coinflip loss: {user['coinflip_biggest_loss']} 🍪 | "
        if user['coinflip_biggest_loss'] != 0 else ""
    )
    
    remaining = user["bonus_timer"] + COOLDOWN_TIME - time.time()
    if remaining > 0:
        bonus_timer = f"Bonus cooldown: {format_duration(remaining)}"
    else:
        bonus_timer = f"Bonus not claimed ({COMMAND_PREFIX}kek)"
        
    steal_remaining = user["steal_timer"] + COOLDOWN_TIME - time.time()
    if steal_remaining > 0:
        steal_timer = f"Steal cooldown: {format_duration(steal_remaining)}"
    else:
        steal_timer = f"Steal not used ({COMMAND_PREFIX}steal)"
        
    if user["hp"] <= 0:
        respawn_hours, rem = divmod(int(respawn_remaining(user)), 3600)
        respawn_minutes, respawn_seconds = divmod(rem, 60)

        respawn_text = (
            f"Respawn in {respawn_hours}h "
            f"{respawn_minutes}m "
            f"{respawn_seconds}s | "
        )
    else:
        respawn_text = ""
        
        
    blocks_display = hp_bar(user["hp"])

    level = get_level(user.get("xp", 0))
    bonus = get_kek_bonus(level)
    xp_progress, xp_needed = get_xp_progress(user.get("xp", 0))
    xp_bar_display = hp_bar(xp_progress, max_hp=xp_needed, width=10) if xp_needed else "█" * 10
    xp_text = f"{xp_progress}/{xp_needed} XP" if xp_needed else f"{user.get('xp', 0)} XP"
    
    stocks = load_stocks()
    stats_message = (
        f"@{username} [ "
        f"HP: {blocks_display} [{user['hp']}/100] | "
        f"{respawn_text}"
        f"XP: {xp_bar_display} [{xp_text}] | "
        f"Level: {level} / 30 | "
        f"Duel wins: {user['duel_wins']} | "
        f"Duel losses: {user['duel_losses']} | "
        f"Duel winrate: {user['duel_wins'] / (user['duel_wins'] + user['duel_losses']) * 100 if (user['duel_wins'] + user['duel_losses']) > 0 else 0:.2f}% | "
        f"Balance: {user['balance']} 🍪 | "
        f"{bonus_timer} | "
        f"{steal_timer} | "
        f"Total claimed: {user['total_claimed']} 🍪 | "
        f"Coinflip winrate: {user['coinflip_wins'] / (user['coinflip_wins'] + user['coinflip_losses']) * 100 if (user['coinflip_wins'] + user['coinflip_losses']) > 0 else 0:.2f}%"
    )
    
    await reply(stats_message)