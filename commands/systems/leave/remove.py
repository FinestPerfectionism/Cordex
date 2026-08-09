from discord import Member

from bot import Interaction
from core.exceptions import send_bad_permissions_argument
from core.permissions import is_director

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /leave remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_leave_remove(interaction : Interaction, target : Member | None = None) -> None:

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if not isinstance(interaction.user, Member):
        return

    if target and not is_director(interaction.user):
        await send_bad_permissions_argument(interaction, ["target"])
