from discord import Member

from bot import Interaction
from core.exceptions import send_bad_argument, send_bad_permissions_argument
from core.permissions import is_director, is_staff

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /leave remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def _validate_target(interaction : Interaction, target : Member) -> bool:
    is_self = (target.id == interaction.user.id)

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if not isinstance(interaction.user, Member):
        return False

    if not is_self and not is_director(interaction.user):
        await send_bad_permissions_argument(interaction, ["target"])
        return False

    if is_director(target) and not is_self:
        await send_bad_argument(
            interaction,
            subtitle = {"target" : "You cannot un-vacate other directors."},
        )
        return False

    if not is_staff(target):
        msg = "You are not staff." if is_self else "You cannot un-vacate those who are not staff."

        await send_bad_argument(
            interaction,
            subtitle = {"target" : msg},
        )
        return False

    return True


async def run_leave_remove(interaction : Interaction, target : Member | None = None) -> None:

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if not isinstance(interaction.user, Member):
        return

    effective_target = target or interaction.user

    if not await _validate_target(interaction, effective_target):
        return
