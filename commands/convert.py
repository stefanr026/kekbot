from config import COMMAND_PREFIX
from utils.users import find_user, load_users, reply_if_not_registered, set_user
from utils.amounts import parse_positive_amount
from utils.xp import XP_PER_KEK, record_level_change

async def cmd_convert(username, reply, args=None):
    print(f"@{username} requested convert command with args: {args}")

    args = args or []

    if len(args) < 1:
        await reply(
            f"@{username} Usage: "
            f"{COMMAND_PREFIX}convert <xp amount|all> "
            f"({XP_PER_KEK} XP -> 1 🍪)"
        )
        return

    users = load_users()
    user = find_user(users, username)

    if await reply_if_not_registered(reply, username, user):
        return

    xp = user.get("xp", 0)

    xp_amount = await parse_positive_amount(
        reply, username, args[0],
        allow_all=True,
        all_amount=xp,
        cap=xp,
        zero_message=f"@{username} You don't have any XP to convert KEKP",
    )
    if xp_amount is None:
        return

    reward = xp_amount // XP_PER_KEK

    if reward <= 0:
        await reply(
            f"@{username} You need at least {XP_PER_KEK} xp to convert into 🍪 KEKP"
        )
        return

    # Only spend the xp that actually converted, keep the leftover remainder
    spent_xp = reward * XP_PER_KEK

    user["xp"] = xp - spent_xp
    record_level_change(user, xp)
    user["balance"] += reward

    set_user(user["username"], user)

    await reply(
        f"@{username} Converted {spent_xp} xp into +{reward} 🍪 | "
        f"Balance: {user['balance']} 🍪 | Remaining xp: {user['xp']}"
    )
