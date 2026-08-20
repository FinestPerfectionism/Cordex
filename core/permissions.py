from collections.abc import Callable
from typing import Literal

from discord.app_commands import check

from bot import Interaction
from constants import BOT_OWNER_ID

from .exceptions import BadPermissionsCommand

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Permissions Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @access_control
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

_ContextType = Literal[
    "DMs",
    "Guild",
    "Guild + DMs",
]

def access_control[F : Callable[..., object]](allowed_users : list[int] | None = None) -> Callable[[F], F]:
    users = allowed_users or []

    def predicate(target : Interaction) -> bool:
        user = target.user

        if user.id in users:
            return True

        raise BadPermissionsCommand

    def decorator(func : F) -> F:
        check(predicate)(func)
        return func

    return decorator

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Specific Decorators
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def bot_owner_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(allowed_users = [BOT_OWNER_ID])
