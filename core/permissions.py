from collections.abc import Callable
from typing import TYPE_CHECKING

from discord.app_commands import check

from constants import DEVELOPER_IDS

from .exceptions import BadEnvironmentGuild, BadPermissionsCommand

if TYPE_CHECKING:
    from discord import Member, User

    from bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Permissions Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @access_control
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def access_control[F : Callable[..., object]](allowed_users : list[int] | None = None) -> Callable[[F], F]:
    users = allowed_users or []

    def predicate(interaction : Interaction) -> bool:
        user = interaction.user

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
    return access_control(allowed_users = list(DEVELOPER_IDS))

def guild_owner_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    def predicate(interaction : Interaction) -> bool:
        if not interaction.guild:
            raise BadEnvironmentGuild

        if interaction.user == interaction.guild.owner:
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
