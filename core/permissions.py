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

_ContextType = Literal[
    "DMs",
    "Guild",
    "Guild + DMs",
    "Main Guild",
    "Main Guild + DMs",
]

def access_control[F : Callable[..., object]](
    context       : _ContextType | None = "Guild + DMs",
    *,
    allowed_users : list[int]    | None = None,
    allowed_roles : list[int]    | None = None,
) -> Callable[[F], F]:
    users = allowed_users or []
    roles = allowed_roles or []

    if roles and context != "Main Guild":
        error = "allowed_roles can only be used when context is 'Main Guild'"
        raise ValueError(error)

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

        # ⸻ You're not in the main guild or DMs!

        if context == "Main Guild + DMs" and guild_id is not None and guild_id != MAIN_GUILD_ID:
            raise BadEnvironmentMainGuildOrDMs

        # ⸻ No restrictions provided..?

        if not users and not roles:
            error = "access_control must have a restriction of one or more users and/or one or more roles"
            raise ValueError(error)

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

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Raw Checks
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def is_director(user : Member) -> bool:
    return any(role.id == DIRECTORS_ROLE_ID for role in user.roles)

def is_staff(user : Member) -> bool:
    return any(role.id == STAFF_ROLE_ID for role in user.roles)
