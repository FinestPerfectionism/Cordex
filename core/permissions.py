from collections.abc import Callable
from typing import Literal

from discord import Member
from discord.app_commands import check

from bot import Interaction
from constants import (
    ADMINISTRATORS_ROLE_ID,
    BOT_OWNER_ID,
    DIRECTORS_ROLE_ID,
    MAIN_GUILD_ID,
    MODERATORS_ROLE_ID,
    SENIOR_ADMINISTRATORS_ROLE_ID,
    SENIOR_MODERATORS_ROLE_ID,
    STAFF_ROLE_ID,
)

from .exceptions import (
    BadEnvironmentDMs,
    BadEnvironmentGuild,
    BadEnvironmentMainGuild,
    BadEnvironmentMainGuildOrDMs,
    BadPermissionsCommand,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Permissions Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @access_control
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

ContextType = Literal[
    "DMs",
    "Guild",
    "Guild + DMs",
    "Main Guild",
    "Main Guild + DMs",
]

def access_control[F : Callable[..., object]](
    context       : ContextType | None = "Guild + DMs",
    *,
    allowed_users : list[int]   | None = None,
    allowed_roles : list[int]   | None = None,
) -> Callable[[F], F]:
    users = allowed_users or []
    roles = allowed_roles or []

    if roles and context != "Main Guild":
        warning = f"allowed_roles can only be used when context is 'Main Guild' (got context = {context!r})"
        raise ValueError(warning)

    def predicate(target : Interaction) -> bool:
        guild_id = target.guild_id

        # ⸻ You're not in DMs!

        if context == "DMs" and guild_id is not None:
            raise BadEnvironmentDMs

        # ⸻ You're not in a guild!

        if context == "Guild" and guild_id is None:
            raise BadEnvironmentGuild

        # ⸻ You're not in the main guild!

        if context == "Main Guild" and guild_id != MAIN_GUILD_ID:
            raise BadEnvironmentMainGuild

        # ⸻ You're not in the main guild or DMs

        if context == "Main Guild + DMs" and guild_id is not None and guild_id != MAIN_GUILD_ID:
            raise BadEnvironmentMainGuildOrDMs

        if not users and not roles:
            return True

        user = target.user

        if user.id in users:
            return True

        if isinstance(user, Member):
            for role in user.roles:
                if role.id in roles:
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

def director_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(
        context       = "Main Guild",
        allowed_roles = [DIRECTORS_ROLE_ID],
    )

def senior_administrator_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(
        context       = "Main Guild",
        allowed_roles = [SENIOR_ADMINISTRATORS_ROLE_ID],
    )

def administrator_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(
        context       = "Main Guild",
        allowed_roles = [ADMINISTRATORS_ROLE_ID],
    )

def senior_moderator_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(
        context       = "Main Guild",
        allowed_roles = [SENIOR_MODERATORS_ROLE_ID],
    )

def moderator_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(
        context       = "Main Guild",
        allowed_roles = [MODERATORS_ROLE_ID],
    )

def staff_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(
        context       = "Main Guild",
        allowed_roles = [STAFF_ROLE_ID],
    )
