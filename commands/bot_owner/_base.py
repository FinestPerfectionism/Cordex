from bot import Interaction
from core.cog_loader import discover_cogs
from core.exceptions import send_bad_permissions_command
from core.permissions import is_bot_owner

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Commands Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# get_cogs
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def get_cogs() -> list[str]:
    return discover_cogs("commands", "systems", "core")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Raw Bot-Owner Check
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def check_if_bo(interaction : Interaction) -> bool:
    if is_bot_owner(interaction.user):
        return True

    await send_bad_permissions_command(interaction)
    return False
