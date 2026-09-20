from bot import Interaction
from core.exceptions import send_bad_permissions_command
from core.permissions import is_bot_owner

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Commands Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Raw Bot-Owner Check
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def check_if_bo(interaction : Interaction) -> bool:
    if is_bot_owner(interaction.user):
        return True

    await send_bad_permissions_command(interaction)
    return False
