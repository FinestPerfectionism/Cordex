from collections.abc import Callable

from discord import Member
from discord.app_commands import CheckFailure, check

from bot import Interaction

from constants import ADMINISTRATORS_ROLE_ID, BOT_OWNER_ID, DIRECTORS_ROLE_ID, MODERATORS_ROLE_ID, SENIOR_ADMINISTRATORS_ROLE_ID, SENIOR_MODERATORS_ROLE_ID, STAFF_ROLE_ID

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Permissions Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class BadPermissions(CheckFailure):
    pass

def access_control(*, allowed_users : list[int] | None = None, allowed_roles : list[int] | None = None):
    users = allowed_users or []
    roles = allowed_roles or []

    async def predicate(target : Interaction) -> bool:
        user = target.user

        if user.id in users:
            return True

        if isinstance(user, Member):
            for role in user.roles:
                if role.id in roles:
                    return True

        raise BadPermissions

    def decorator[F : Callable[..., object]](func : F) -> F:
        check(predicate)(func)
        return func

    return decorator

def bot_owner_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(allowed_users = [BOT_OWNER_ID])

def director_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(allowed_roles = [DIRECTORS_ROLE_ID])

def senior_administrator_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(allowed_roles = [SENIOR_ADMINISTRATORS_ROLE_ID])

def administrator_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(allowed_roles = [ADMINISTRATORS_ROLE_ID])

def senior_moderator_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(allowed_roles = [SENIOR_MODERATORS_ROLE_ID])

def moderator_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(allowed_roles = [MODERATORS_ROLE_ID])

def staff_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    return access_control(allowed_roles = [STAFF_ROLE_ID])