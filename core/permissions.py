from collections.abc import Callable

from discord import Member, User
from discord.app_commands import check

from bot import Interaction
from constants import DEVELOPER_IDS

from .exceptions import BadPermissionsCommand

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Permissions Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Command Decorator
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def bot_owner_cmd[F]() -> Callable[[F], F]:
    def predicate(interaction : Interaction) -> bool:
        if is_bot_owner(interaction.user):
            return True

        raise BadPermissionsCommand

    def decorator(func : F) -> F:
        check(predicate)(func)
        return func

    return decorator

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Permission Checks
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def is_bot_owner(target : User | Member, /) -> bool:
    return target.id in DEVELOPER_IDS
